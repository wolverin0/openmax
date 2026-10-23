"""Offline contract regressions; never import acquisition code or contact radios."""
import ast
import os
from pathlib import Path
import shlex
import shutil
import subprocess
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'artifacts/canary_panel1_guarida/preprod1_trial_20261022.py'
BASELINE = ROOT / 'artifacts/canary_panel1_guarida/fmx0017_trial_20261022.py'


def extract(path, name):
    return next(n for n in ast.walk(ast.parse(path.read_text()))
                if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name)


def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)


@pytest.mark.parametrize('command', [
    'wpa_cli -i ath0 scan',
    'wpa_cli -i ath0 bss_flush 0',
    'wpa_cli -i ath0 enable_network 0',
    'cat /etc/version',
])
def test_no_xc_exec_can_cross_the_admission_boundary(command):
    namespace = dict(rec={'XC_command_audit': []}, control_window=False,
                     time=SimpleNamespace(monotonic=lambda: 10), require=require)
    node = extract(SOURCE, 'AuditedXC')
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(SOURCE), 'exec'), namespace)
    delegated = []
    client = SimpleNamespace(exec_command=lambda c: delegated.append(c))
    proxy = namespace['AuditedXC'](client)
    proxy.exec_command(command)  # Explicit pre-window preparation is permitted.
    namespace['control_window'] = True
    with pytest.raises(RuntimeError, match='FORBIDDEN_XC_EXEC_DURING_ZERO_TOUCH_WINDOW'):
        proxy.exec_command(command)
    assert delegated == [command]
    assert namespace['rec']['XC_command_audit'][-1]['window'] is True


def test_bounded_rpc_cannot_bypass_the_real_xc_window_audit():
    import threading, time
    opened=[]
    client=SimpleNamespace(get_transport=lambda:SimpleNamespace(
        open_session=lambda **kwargs:opened.append('OPENED')))
    namespace=dict(rec={'XC_command_audit':[]},control_window=True,
                   time=time,threading=threading,require=require)
    nodes=[extract(SOURCE,'AuditedXC'),extract(SOURCE,'remote')]
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(SOURCE),'exec'),namespace)
    with pytest.raises(RuntimeError,match='FORBIDDEN_XC_EXEC_DURING_ZERO_TOUCH_WINDOW'):
        namespace['remote'](namespace['AuditedXC'](client),'read-only-fixture',timeout=.1)
    assert opened==[] and len(namespace['rec']['XC_command_audit'])==1
    assert namespace['rec']['XC_command_audit'][0]['window'] is True


@pytest.mark.parametrize('device', ['SXT', 'LBM5'])
def test_legacy_restore_is_identical_to_accepted_run5(device):
    programs = []
    for path in [BASELINE, SOURCE]:
        namespace = dict(shlex=shlex)
        exec(compile(ast.Module(body=[extract(path, 'legacy_program')],
                                type_ignores=[]), str(path), 'exec'), namespace)
        programs.append(namespace['legacy_program'](device, '/tmp/owned', 'a' * 64))
    assert programs[1].replace('+900))', '+240))') == programs[0]


def test_xc_enable_cannot_observe_open_ap_setup():
    """Enforce the actual setup's protocol order without importing radio access."""
    main = extract(SOURCE, 'main')
    setup = next(n for n in main.body if isinstance(n, ast.Try))
    events = []
    for node in sorted(ast.walk(setup), key=lambda n: getattr(n, 'lineno', 0)):
        if isinstance(node, ast.Call):
            call = ast.unparse(node)
            if call == 'helper.arm(ap)':
                events.append('OPEN')
            elif call == 'mode(True)':
                events.append('SECURE')
            elif (isinstance(node.func, ast.Name) and node.func.id == 'remote'
                  and len(node.args) > 1 and isinstance(node.args[0], ast.Name)
                  and node.args[0].id == 'rocket' and isinstance(node.args[1], ast.Constant)):
                event = {'wpa_cli -i ath0 bss_flush 0': 'FLUSH',
                         'wpa_cli -i ath0 scan': 'SCAN',
                         'wpa_cli -i ath0 enable_network 0': 'ENABLE',
                         'wpa_cli -i ath0 reassociate': 'REASSOCIATE'}.get(node.args[1].value)
                if event:
                    events.append(event)
        elif isinstance(node, ast.Assign) and ast.unparse(node.targets[0]) == "rec['AP_discovery_seed_before_XC_preparation']":
            events.append('SEED')
        elif isinstance(node, ast.Assign) and ast.unparse(node.targets[0]) == "rec['AP_discovery_clear_before_XC_enable']":
            events.append('CLEAR')
        elif isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == 'control_window' for t in node.targets):
            if isinstance(node.value, ast.Constant) and node.value.value is True:
                events.append('WINDOW')
    assert events == ['OPEN', 'SECURE', 'SEED', 'FLUSH', 'SCAN', 'CLEAR', 'ENABLE', 'REASSOCIATE', 'WINDOW']


def shell_decision_block():
    source = (ROOT / 'tools/bench/preprod1_admitter.sh').read_text(encoding='utf8')
    start = source.index(' if test "$ie_on" = 1; then', source.index(' collect\n t=$(now)'))
    end = source.index(' printf \'%s phase=', start)
    block = source[start:end]
    assert not any(word in block for word in ['ubus ', 'ssh ', 'curl '])
    return block


def run_shell_fixture(body):
    native_git_bash = Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Git/bin/bash.exe'
    bash = str(native_git_bash) if native_git_bash.is_file() else shutil.which('bash')
    if bash:
        command = [bash, '-s']
    elif shutil.which('wsl.exe'):
        command = ['wsl.exe', '--exec', '/bin/sh', '-s']
    else:
        pytest.skip('POSIX shell unavailable for offline admission fixture')
    result = subprocess.run(command, input=body.encode(), stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=15)
    assert result.returncode == 0, result.stderr.decode(errors='replace')


@pytest.mark.parametrize('first,second', [('XC', 'WA'), ('WA', 'XC')])
def test_both_missing_airos_clients_must_see_the_same_ie_pulse(first, second):
    block = shell_decision_block()
    header = shell_header()
    script = header + 'probe_address=$' + first + '\n' + block
    script += '\ntest "$clears" = 0\n'
    script += 'probe_address=$' + second + '\n' + block
    script += '\ntest "$clears" = 1\ntest "$seen_xc" = 1\ntest "$seen_wa" = 1\n'
    run_shell_fixture(script)


def shell_header():
    return '''set -eu
WA=fc:ec:da:c2:54:0a; XC=b4:fb:e4:5c:d5:d2
GOOD=; phase=ADMIT; target=; pulses=1; ie_on=1
seen_wa=0; seen_xc=0; clears=0; IE=syntheticIE
t=100; wa_clear_not_before=0; xc_clear_not_before=0
good() { case " $GOOD " in *" $1 "*) return 0;; *) return 1;; esac; }
old_wds_retired() { return 0; }
log() { :; }
ucode() { :; }
clear_window() { ie_on=0; clears=$((clears+1)); }
probe_target=ff:ff:ff:ff:ff:ff
'''


@pytest.mark.parametrize('authorized,missing', [('XC', 'WA'), ('WA', 'XC')])
def test_authorized_peer_does_not_need_to_probe_again(authorized, missing):
    script = shell_header() + 'GOOD=$' + authorized + '\nprobe_address=$' + missing + '\n'
    script += shell_decision_block() + '\ntest "$clears" = 1\n'
    run_shell_fixture(script)


@pytest.mark.parametrize('probe', [
    'probe_address=$WA; probe_target=18:e8:29:74:55:a2',
    'probe_address=$XC; probe_target=00:11:22:33:44:55',
])
def test_directed_wa_or_foreign_target_does_not_satisfy_discovery(probe):
    script = shell_header() + probe + '\n' + shell_decision_block()
    script += '\ntest "$clears" = 0\ntest "$seen_wa" = 0\ntest "$seen_xc" = 0\n'
    run_shell_fixture(script)


def test_recovery_only_consumes_the_exact_missing_target_probe():
    block = shell_decision_block()
    script = shell_header() + 'phase=RECOVER; target=64:d1:54:1b:96:97; probe_address=$WA\n' + block
    script += '\ntest "$clears" = 0\nprobe_address=$target\n' + block
    script += '\ntest "$clears" = 1\n'
    run_shell_fixture(script)


def test_old_pulse_observations_cannot_satisfy_a_new_pulse():
    source = (ROOT / 'tools/bench/preprod1_admitter.sh').read_text(encoding='utf8')
    pulse = source.split('pulse_missing() {', 1)[1].split('\nstart=$(now);', 1)[0]
    script = shell_header() + 'pulse_missing() {' + pulse
    script += '\nnow() { echo 100; }\nset_ie() { :; }\n'
    script += 'ie_on=0; next_pulse=0; seen_xc=1; seen_wa=1\npulse_missing\n'
    script += 'test "$ie_on" = 1\ntest "$seen_xc" = 0\ntest "$seen_wa" = 0\n'
    run_shell_fixture(script)


@pytest.mark.parametrize('status,accepted', [
    ('wpa_state=SCANNING\n', True),
    ('wpa_state=ASSOCIATING\n', True),
    ('wpa_state=COMPLETED\n', False),
    ('FAIL\nnetwork id / ssid\n', False),
    ('address=b4:fb:e4:5c:d5:d2\n', False),
    ('wpa_state=SCANNING\nwpa_state=SCANNING\n', False),
    ('wpa_state=UNSUPPORTED\n', False),
    ('FAIL\nwpa_state=SCANNING\n', False),
])
def test_actual_pre_window_guard_requires_positive_native_waiting_state(status, accepted):
    main = extract(SOURCE, 'main')
    assignment = next(n for n in ast.walk(main) if isinstance(n, ast.Assign)
                      and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'pre_window_states')
    guard = next(n for n in ast.walk(main) if isinstance(n, ast.Expr)
                 and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name)
                 and n.value.func.id == 'require' and isinstance(n.value.args[-1], ast.Constant)
                 and n.value.args[-1].value == 'XC_PRE_WINDOW_STATUS_NOT_WAITING')
    program = compile(ast.Module(body=[assignment, guard], type_ignores=[]), str(SOURCE), 'exec')
    import re
    environment = dict(re=re, require=require, rec={'XC_pre_window_status': {'stdout': status}})
    if accepted:
        exec(program, environment)
    else:
        with pytest.raises(RuntimeError, match='XC_PRE_WINDOW_STATUS_NOT_WAITING'):
            exec(program, environment)


def test_capture_helper_survives_the_legacy_baseline_snapshot():
    """Exercise the actual assignments that failed at R5c's first traffic epoch."""
    main = extract(SOURCE, 'main')
    load = next(n for n in ast.walk(main) if isinstance(n, ast.Assign)
                and isinstance(n.value, ast.Call)
                and ast.unparse(n.value) == "access.load('fmx0017_trial_20261022.py')")
    snapshot = next(n for n in ast.walk(main) if isinstance(n, ast.Assign)
                    and isinstance(n.value, ast.Call)
                    and ast.unparse(n.value) == 'legacy_snapshot(name, c)')
    capture = next(n for n in ast.walk(main) if isinstance(n, ast.Assign)
                   and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'capguard')
    wrapper = SimpleNamespace(adaptive_ping_wrapper=lambda cmd: 'now-start>=60 ' + cmd)
    namespace = dict(access=SimpleNamespace(load=lambda name: wrapper),
                     legacy_snapshot=lambda name, client: 'preserved snapshot text',
                     name='SXT', c=object(), capcmd='owned capture')
    exec(compile(ast.Module(body=[load, snapshot, capture], type_ignores=[]),
                 str(SOURCE), 'exec'), namespace)
    assert namespace['capguard'] == 'now-start>=45 owned capture'


@pytest.mark.parametrize('ping_done,capture_done,now,accepted', [
    (True, False, 35, False),
    (True, True, 44, True),
    (False, True, 30, False),
])
def test_actual_capture_readiness_keeps_station_observation_running(ping_done,capture_done,now,accepted):
    namespace=dict(require=require,time=SimpleNamespace(monotonic=lambda: now))
    node=extract(SOURCE,'traffic_ready')
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(SOURCE),'exec'),namespace)
    def stream(done):
        return (None,SimpleNamespace(channel=SimpleNamespace(exit_status_ready=lambda: done)))
    assert namespace['traffic_ready']([('mac','interface',stream(ping_done),stream(capture_done))],48) is accepted


def test_actual_capture_readiness_fails_closed_at_existing_guard_deadline():
    namespace=dict(require=require,time=SimpleNamespace(monotonic=lambda: 48))
    node=extract(SOURCE,'traffic_ready')
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(SOURCE),'exec'),namespace)
    stream=(None,SimpleNamespace(channel=SimpleNamespace(exit_status_ready=lambda: False)))
    with pytest.raises(RuntimeError,match='QUALIFY_CAPTURE_TIMEOUT'):
        namespace['traffic_ready']([('mac','interface',stream,stream)],48)


def test_traffic_output_is_archived_before_echo_or_radio_validation():
    main=extract(SOURCE,'main')
    flow_loop=next(n for n in ast.walk(main) if isinstance(n,ast.For)
                   and ast.unparse(n.target)=='(mac, device, ping, cap)'
                   and ast.unparse(n.iter)=='flows'
                   and any(isinstance(k,ast.Assign) and ast.unparse(k.targets[0])=='artifact' for k in n.body))
    archive=next(i for i,n in enumerate(flow_loop.body) if isinstance(n,ast.Assign)
                 and ast.unparse(n.targets[0])=='artifact')
    checks=[i for i,n in enumerate(flow_loop.body) if any(
        isinstance(call,ast.Call) and isinstance(call.func,ast.Name)
        and call.func.id in ['require','stream_quality'] for call in ast.walk(n))]
    assert checks and archive<min(checks)


def test_wa_recovery_does_not_consume_ie_on_a_directed_probe():
    block=shell_decision_block()
    script=shell_header()+'phase=RECOVER; target=$WA; probe_address=$WA; probe_target=18:e8:29:74:55:a2\n'+block
    script+='\ntest "$clears" = 0\nprobe_target=ff:ff:ff:ff:ff:ff\n'+block
    script+='\ntest "$clears" = 1\n'
    run_shell_fixture(script)


def test_stock_recovery_pulses_cover_broadcast_scan_and_legacy_stays_two_seconds():
    source=(ROOT/'tools/bench/preprod1_admitter.sh').read_text(encoding='utf8')
    pulse=source.split('pulse_missing() {',1)[1].split('\nstart=$(now);',1)[0]
    script=shell_header()+'pulse_missing() {'+pulse
    script+='\nnow() { echo 100; }\nset_ie() { :; }\nphase=RECOVER; target=$WA; ie_on=0; next_pulse=0\npulse_missing\ntest "$clear_at" = 160\n'
    script+='target=64:d1:54:1b:96:97; ie_on=0; next_pulse=0\npulse_missing\ntest "$clear_at" = 102\n'
    run_shell_fixture(script)


@pytest.mark.parametrize('chunks,ended,eof,now,expected', [
    ([b'tcpdump: verbose output suppressed\n'], False, False, 1, False),
    ([b'listening on phy0-ap0.sta2, link-type EN10MB\n'], False, False, 1, True),
    ([b'listening on eth0, link-type EN10MB\n'], False, False, 1, False),
    ([], True, False, 1, 'CAPTURE_EXITED_BEFORE_QUALIFIED_TRAFFIC'),
    ([], False, True, 1, 'CAPTURE_EXITED_BEFORE_QUALIFIED_TRAFFIC'),
    ([], False, False, 5, 'CAPTURE_LISTENING_TIMEOUT'),
    ([b'x' * 8193], False, False, 1, 'CAPTURE_START_STDERR_BOUND'),
])
def test_actual_capture_listening_barrier(chunks, ended, eof, now, expected):
    import re
    queue = list(chunks)
    channel = SimpleNamespace(recv_stderr_ready=lambda: bool(queue),
                              recv_stderr=lambda size: queue.pop(0),
                              exit_status_ready=lambda: ended,
                              closed=False, eof_received=eof)
    namespace = dict(require=require, re=re,
                     time=SimpleNamespace(monotonic=lambda: now))
    exec(compile(ast.Module(body=[extract(SOURCE, 'capture_listening')], type_ignores=[]),
                 str(SOURCE), 'exec'), namespace)
    header = bytearray()
    if isinstance(expected, str):
        with pytest.raises(RuntimeError, match=expected):
            namespace['capture_listening']((None, SimpleNamespace(channel=channel)),
                                           'phy0-ap0.sta2', header, 5)
    else:
        assert namespace['capture_listening']((None, SimpleNamespace(channel=channel)),
                                              'phy0-ap0.sta2', header, 5) is expected
        assert header == b''.join(chunks)


@pytest.mark.parametrize('present,owner,list_rc,expected', [
    (True, 'a' * 32, 0, 0),
    (False, '', 0, 0),
    (True, 'b' * 32, 0, 1),
    (True, 'a' * 32, 9, 9),
])
def test_actual_bridge_cleanup_deletes_only_its_owned_table(tmp_path, present, owner, list_rc, expected):
    import re
    namespace = dict(require=require, re=re)
    exec(compile(ast.Module(body=[extract(SOURCE, 'bridge_isolation')], type_ignores=[]),
                 str(SOURCE), 'exec'), namespace)
    table = 'fmx_preprod_' + 'a' * 32
    rules, cleanup = namespace['bridge_isolation'](table, 'a' * 32)
    assert 'hook forward' in rules and 'hook input' not in rules and 'hook output' not in rules
    assert 'iifname "eth0" oifname "phy0-ap0*" counter drop' in rules
    assert 'iifname "phy0-ap0*" oifname "eth0" counter drop' in rules
    directory = str(tmp_path).replace('\\', '/')
    script = 'D=' + shlex.quote(directory) + '\n'
    script += 'nft() {\n if test "$1 $2" = "list tables"; then\n'
    if list_rc:
        script += ' return ' + str(list_rc) + '\n'
    elif present:
        script += ' echo "table bridge ' + table + '"\n'
    if not list_rc and not present:
        script += ' :\n'
    script += ' elif test "$1" = delete; then printf "%s\\n" "$*" > "$D/deleted"; else echo syntheticJSON; fi\n}\n'
    script += 'jsonfilter() { echo ' + shlex.quote(owner) + '; }\n'
    script += '( set -e\n' + cleanup + '\n)\nresult=$?\ntest "$result" = ' + str(expected) + '\n'
    if present and owner == 'a' * 32 and not list_rc:
        script += 'test "$(cat "$D/deleted")" = "delete table bridge ' + table + '"\n'
    else:
        script += 'test ! -e "$D/deleted"\n'
    run_shell_fixture(script)


@pytest.mark.parametrize('table,owner', [
    ('fw4', 'a' * 32), ('fmx_preprod_' + 'a' * 32, 'b' * 32),
    ('fmx_preprod_' + 'a' * 31, 'a' * 31),
])
def test_bridge_isolation_rejects_unowned_names(table, owner):
    import re
    namespace = dict(require=require, re=re)
    exec(compile(ast.Module(body=[extract(SOURCE, 'bridge_isolation')], type_ignores=[]),
                 str(SOURCE), 'exec'), namespace)
    with pytest.raises(RuntimeError, match='ISOLATION_OWNER_FORMAT'):
        namespace['bridge_isolation'](table, owner)


def test_isolation_teardown_follows_final_reload_off_and_off_verification():
    namespace = dict(require=require, CONFIG_SHA='config', NETWORK_SHA='network', header=lambda: '')
    helper = ROOT / 'artifacts/canary_panel1_guarida/root_four_cpe_ap_window_20261022.py'
    exec(compile(ast.Module(body=[extract(helper, 'restore_body')], type_ignores=[]),
                 str(helper), 'exec'), namespace)
    original = namespace['restore_body']()
    exec(compile(ast.Module(body=[extract(SOURCE, 'restore_with_bridge_isolation')], type_ignores=[]),
                 str(SOURCE), 'exec'), namespace)
    wrapped = namespace['restore_with_bridge_isolation'](original, 'nft delete OWNED_TABLE\n')
    assert wrapped.count('wifi down radio0\n') == 2
    assert wrapped.index('ubus call network reload') < wrapped.rindex('wifi down radio0\n')
    assert wrapped.index('test "$(jsonfilter -s "$fmx_wireless"') > wrapped.rindex('wifi down radio0\n')
    assert wrapped.index('nft delete OWNED_TABLE') > wrapped.index('fmx_devs=$(iw dev)')
    assert wrapped.index('nft delete OWNED_TABLE') > wrapped.index('trap \'rmdir "$D/restoring"\' EXIT')


def test_isolation_teardown_refuses_a_changed_restore_template():
    namespace = dict(require=require)
    exec(compile(ast.Module(body=[extract(SOURCE, 'restore_with_bridge_isolation')], type_ignores=[]),
                 str(SOURCE), 'exec'), namespace)
    with pytest.raises(RuntimeError, match='AP_RESTORE_ISOLATION_ANCHOR_CHANGED'):
        namespace['restore_with_bridge_isolation']('wifi down radio0\n', 'nft delete OWNED_TABLE\n')


def test_recovery_ie_waits_for_exact_old_wds_ifindex_retirement():
    source = (ROOT / 'tools/bench/preprod1_admitter.sh').read_text(encoding='utf8')
    pulse = source.split('pulse_missing() {', 1)[1].split('\nstart=$(now);', 1)[0]
    helper = source.split('old_wds_retired() {', 1)[1].split('\npulse_missing()', 1)[0] if 'old_wds_retired() {' in source else ' return 0; }\n'
    script = shell_header() + 'old_wds_retired() {' + helper + '\npulse_missing() {' + pulse
    script += '\nnow() { echo 100; }; set_ie() { :; }; log() { :; }\n'
    script += 'old_child=phy0-ap0.sta4; old_ifindex=21; old_wait_logged=0; drop_n=1; phase=RECOVER; target=$WA; ie_on=0; next_pulse=0\n'
    script += 'cat() { echo 21; }; pulse_missing\ntest "$ie_on" = 0\ntest "$pulses" = 1\n'
    script += 'cat() { echo 22; }; pulse_missing\ntest "$ie_on" = 1\ntest "$old_child" = ""\n'
    script += 'old_child=phy0-ap0.sta4; old_ifindex=21; ie_on=0; next_pulse=0\ncat() { return 1; }; pulse_missing\ntest "$ie_on" = 1\ntest "$old_child" = ""\n'
    run_shell_fixture(script)


def test_recovery_cannot_accept_reauthentication_before_old_wds_retirement():
    source = (ROOT / 'tools/bench/preprod1_admitter.sh').read_text(encoding='utf8')
    block = source.split('\n RECOVER)\n', 1)[1].split('\n ;;\n STABLE)', 1)[0]
    script = shell_header() + 'phase=RECOVER; t=100; phase_end=160; drop_n=1; target=$WA; recovered=0\n'
    script += 'now() { echo 100; }; protect_peers() { :; }; good() { return 0; }; old_wds_retired() { return 1; }\n'
    script += 'log() { case "$*" in RECOVERED*) recovered=$((recovered+1));; esac; }\n'
    script += block + '\ntest "$phase" = RECOVER\ntest "$recovered" = 0\n'
    script += 'old_wds_retired() { return 0; }\n' + block
    script += '\ntest "$phase" = STABLE\ntest "$recovered" = 1\n'
    run_shell_fixture(script)


@pytest.mark.parametrize('output,code', [('', 1), ('bad-index', 0), ('', 0), ('0', 0)])
def test_existing_wds_read_failure_or_invalid_index_never_counts_as_retired(output, code):
    source = (ROOT / 'tools/bench/preprod1_admitter.sh').read_text(encoding='utf8')
    helper = source.split('old_wds_retired() {', 1)[1].split('\npulse_missing()', 1)[0]
    script = shell_header() + 'old_wds_retired() {' + helper
    script += '\nold_child=phy0-ap0.sta4; old_ifindex=21; old_wait_logged=0; drop_n=1\n'
    script += 'cat() { printf "%s" ' + shlex.quote(output) + '; return ' + str(code) + '; }\n'
    script += 'test() { if [ "$1" = -e ]; then return 0; fi; builtin test "$@"; }\n'
    script += 'log() { case "$*" in OLD_WDS_RETIRED*|RECOVERED*|PULSE*) exit 94;; esac; }\n'
    script += 'set +e\n( old_wds_retired )\nstatus=$?\nset -e\ntest "$status" = ' + ('1' if code else '88') + '\n'
    script += 'test "$old_child" = phy0-ap0.sta4\n'
    run_shell_fixture(script)


def upload_namespace():
    import re
    import hashlib
    namespace = dict(require=require, re=re, shlex=shlex,
                     sha=lambda b: hashlib.sha256(b).hexdigest())
    exec(compile(ast.Module(body=[extract(SOURCE, 'daemon_upload_commands')], type_ignores=[]),
                 str(SOURCE), 'exec'), namespace)
    return namespace


def test_long_daemon_is_staged_byte_exact_with_bounded_exec_strings():
    import secrets
    namespace = upload_namespace()
    directory = '/tmp/fmx-admitter-' + secrets.token_hex(12)
    payload = ("#!/bin/sh\n#'\"$()\\ quoted-" + chr(233) + '\n' * 2).encode('utf8') + b"# ' " * 3500
    commands = namespace['daemon_upload_commands'](directory, payload)
    assert max(len(c.encode('utf8')) for c in commands) <= 4096
    assert len(payload) > 8192 and len(commands) > 2
    script = 'set -eu\n' + commands[0]
    script += 'trap ' + shlex.quote('rm -f ' + directory + '/admitter.sh; rmdir ' + directory) + ' EXIT\n'
    script += '\n'.join(commands[1:])
    script += '\ntest "$(wc -c < ' + directory + '/admitter.sh)" = ' + str(len(payload)) + '\n'
    run_shell_fixture(script)  # The generator's final SHA assertion checks actual shell reassembly.


@pytest.mark.parametrize('directory', ['/tmp/fmx-admitter-', '/tmp/other-' + 'a' * 24, '../outside'])
def test_daemon_staging_rejects_unowned_paths(directory):
    with pytest.raises(RuntimeError, match='DAEMON_UPLOAD_PATH'):
        upload_namespace()['daemon_upload_commands'](directory, b'#!/bin/sh\n')


def test_daemon_staging_enforces_its_bounded_transfer_size():
    with pytest.raises(RuntimeError, match='DAEMON_UPLOAD_SOURCE_BOUND'):
        upload_namespace()['daemon_upload_commands']('/tmp/fmx-admitter-' + 'a' * 24,
                                                      b'#!/bin/sh\n' + b'x' * 16384)


@pytest.mark.parametrize('failure', ['offset', 'checksum'])
def test_daemon_staging_refuses_incomplete_or_changed_bytes(failure):
    import secrets
    namespace = upload_namespace()
    directory = '/tmp/fmx-admitter-' + secrets.token_hex(12)
    commands = namespace['daemon_upload_commands'](directory, b'#!/bin/sh\n' + b'#test\n' * 300)
    script = 'set -eu\n' + commands[0]
    script += 'trap ' + shlex.quote('rm -f ' + directory + '/admitter.sh; rmdir ' + directory) + ' EXIT\n'
    if failure == 'offset':
        failing = commands[2]  # Skip the first chunk; the byte offset must reject this append.
    else:
        script += '\n'.join(commands[1:-1])
        script += '\nprintf x >> ' + directory + '/admitter.sh\n'
        failing = commands[-1]
    script += '\nset +e\n(\n' + failing + '\n)\nstatus=$?\nset -e\ntest "$status" -ne 0\n'
    run_shell_fixture(script)


@pytest.mark.parametrize('observed,poll_now,error,expected', [
    (4.9, 9, None, True),
    (5.0, 9, None, 'CAPTURE_LISTENING_TIMEOUT'),
    (None, 4, None, False),
    (None, 5, None, 'CAPTURE_LISTENING_TIMEOUT'),
    (None, 4, 'CAPTURE_EXITED_BEFORE_QUALIFIED_TRAFFIC', 'CAPTURE_EXITED_BEFORE_QUALIFIED_TRAFFIC'),
])
def test_startup_timestamp_survives_late_station_poll_without_extending_deadline(observed, poll_now, error, expected):
    namespace=dict(require=require,time=SimpleNamespace(monotonic=lambda:poll_now))
    exec(compile(ast.Module(body=[extract(SOURCE,'capture_startup_ready')],type_ignores=[]),
                 str(SOURCE),'exec'),namespace)
    state=dict(deadline=5,ready_mono=observed,error=error)
    if isinstance(expected,str):
        with pytest.raises(RuntimeError,match=expected):namespace['capture_startup_ready'](state)
    else:assert namespace['capture_startup_ready'](state) is expected


def test_startup_worker_records_header_observation_before_station_poll_returns():
    checks=iter([False,False,True]);sleeps=[]
    namespace=dict(capture_listening=lambda *args:next(checks),
                   time=SimpleNamespace(sleep=lambda seconds:sleeps.append(seconds),monotonic=lambda:4.9))
    exec(compile(ast.Module(body=[extract(SOURCE,'capture_startup_worker')],type_ignores=[]),
                 str(SOURCE),'exec'),namespace)
    state=dict(deadline=5,ready_mono=None,error=None)
    namespace['capture_startup_worker'](object(),'radio',bytearray(),state)
    assert state==dict(deadline=5,ready_mono=4.9,error=None) and sleeps==[.02,.02]


def test_startup_worker_preserves_native_startup_failure():
    def reject(*args):raise RuntimeError('CAPTURE_LISTENING_TIMEOUT')
    namespace=dict(capture_listening=reject,time=SimpleNamespace())
    exec(compile(ast.Module(body=[extract(SOURCE,'capture_startup_worker')],type_ignores=[]),
                 str(SOURCE),'exec'),namespace)
    state=dict(deadline=5,ready_mono=None,error=None)
    namespace['capture_startup_worker'](object(),'radio',bytearray(),state)
    assert state==dict(deadline=5,ready_mono=None,error='CAPTURE_LISTENING_TIMEOUT')


@pytest.mark.parametrize('stock', ['WA', 'XC'])
def test_stock_recovery_requires_current_broadcast_after_twenty_second_live_dwell(stock):
    block=shell_decision_block()
    prefix=stock.lower()
    script=shell_header()+'phase=RECOVER; target=$'+stock+'; '+prefix+'_clear_not_before=121; t=101; probe_address=$'+stock+'\n'+block
    script+='\ntest "$clears" = 0\ntest "$seen_'+prefix+'" = 1\nprobe_address=; probe_target=; t=120\n'+block
    script+='\ntest "$clears" = 0\nt=121\n'+block+'\ntest "$clears" = 0\nprobe_address=$'+stock+'; probe_target=ff:ff:ff:ff:ff:ff\n'+block+'\ntest "$clears" = 1\n'
    run_shell_fixture(script)


def test_wa_recovery_dwell_alone_never_replaces_broadcast_evidence():
    block=shell_decision_block()
    script=shell_header()+'phase=RECOVER; target=$WA; wa_clear_not_before=120; t=121; probe_address=$WA; probe_target=18:e8:29:74:55:a2\n'+block
    script+='\ntest "$clears" = 0\nprobe_target=ff:ff:ff:ff:ff:ff\n'+block+'\ntest "$clears" = 1\n'
    run_shell_fixture(script)


@pytest.mark.parametrize('stock', ['WA', 'XC'])
def test_each_stock_recovery_pulse_binds_its_own_dwell_start_and_probe(stock):
    source=(ROOT/'tools/bench/preprod1_admitter.sh').read_text(encoding='utf8')
    pulse=source.split('pulse_missing() {',1)[1].split('\nstart=$(now);',1)[0]
    prefix=stock.lower()
    script=shell_header()+'pulse_missing() {'+pulse
    script+='\nnow() { echo 100; }\nset_ie() { :; }\nphase=RECOVER; target=$'+stock+'; ie_on=0; next_pulse=0; seen_'+prefix+'=1; '+prefix+'_clear_not_before=1\npulse_missing\ntest "$'+prefix+'_clear_not_before" = 121\ntest "$seen_'+prefix+'" = 0\n'
    run_shell_fixture(script)


@pytest.mark.parametrize('blocked_stage', ['ack', 'status', None])
def test_readonly_diagnostic_query_closes_only_owned_channel_at_wall_deadline(blocked_stage):
    import io
    import threading
    import time
    diagnostic=ROOT/'artifacts/canary_panel1_guarida/preprod1_r5m_WA_readonly_20261022.py'
    closed=threading.Event()
    class Channel:
        def settimeout(self, value): pass
        def exec_command(self, command):
            if blocked_stage=='ack': closed.wait(1)
        def shutdown_write(self): pass
        def makefile(self, *args): return io.BytesIO(b'ok')
        def makefile_stderr(self, *args): return io.BytesIO(b'')
        def recv_exit_status(self):
            if blocked_stage=='status': closed.wait(1)
            return 0
        def close(self): closed.set()
    channel=Channel()
    client=SimpleNamespace(get_transport=lambda: SimpleNamespace(open_session=lambda **kwargs: channel))
    namespace=dict(threading=threading,a=SimpleNamespace(require=require))
    exec(compile(ast.Module(body=[extract(diagnostic,'readonly_command')],type_ignores=[]),str(diagnostic),'exec'),namespace)
    before=time.monotonic()
    if blocked_stage:
        with pytest.raises(RuntimeError,match='READONLY_QUERY_EXEC_DEADLINE'):
            namespace['readonly_command'](client,'cat /proc/uptime',timeout=.03)
    else:
        assert namespace['readonly_command'](client,'cat /proc/uptime',timeout=.1)['stdout']=='ok'
    assert closed.is_set() and time.monotonic()-before<2


def readonly_diagnostic_namespace():
    import hashlib
    import json
    import re
    diagnostic=ROOT/'artifacts/canary_panel1_guarida/preprod1_r5m_WA_readonly_20261022.py'
    namespace=dict(hashlib=hashlib,json=json,re=re,a=SimpleNamespace(require=require))
    exec(compile(ast.Module(body=[extract(diagnostic,'public_WA_diagnostic')],type_ignores=[]),str(diagnostic),'exec'),namespace)
    data=dict(identity={'stdout':'syntheticidentity'},queries={name:dict(exit_code=0,stderr='',stdout=value) for name,value in {'status':'wpa_state=SCANNING\n','log':'CTRL-EVENT-DISCONNECTED reason=3\n','kernel':'retainedkernel','radio':'Encryption key: PRIVATE_TEST_KEY','bss':'FAIL'}.items()})
    return namespace['public_WA_diagnostic'],data


@pytest.mark.parametrize('failed_query',['status','log','kernel'])
def test_readonly_diagnostic_cannot_pass_when_an_essential_query_failed(failed_query):
    public,data=readonly_diagnostic_namespace()
    data['queries'][failed_query]['exit_code']=127
    with pytest.raises(RuntimeError,match='WA_ESSENTIAL_READ_FAILED'): public(data)


def test_readonly_diagnostic_requires_a_positive_native_state():
    public,data=readonly_diagnostic_namespace();data['queries']['status']['stdout']='FAIL\n'
    with pytest.raises(RuntimeError,match='WA_STATUS_PROTOCOL_INVALID'): public(data)


def test_readonly_diagnostic_never_publishes_raw_radio_key_material():
    import json
    public,data=readonly_diagnostic_namespace();result=public(data)
    assert 'PRIVATE_TEST_KEY' not in json.dumps(result)
    assert 'radio' not in result['WA_readonly'] and len(result['private_radio_query_sha256'])==64


@pytest.mark.parametrize('frequency',[5180,5200])
def test_secure_readonly_acquisition_requires_exact_probe_context_and_ends_listener(frequency):
    import json
    import re
    diagnostic=ROOT/'artifacts/canary_panel1_guarida/preprod1_r5m_WA_readonly_20261022.py'
    event=json.dumps({'probe':{'address':'fc:ec:da:c2:54:0a','target':'ff:ff:ff:ff:ff:ff','freq':frequency,'ifname':'phy0-ap0'}}).encode()
    class Listener:
        closed=False
        pending=True
        def recv_ready(self): return self.pending
        def recv_stderr_ready(self): return False
        def recv(self, count): self.pending=False; return event
        def close(self): self.closed=True
    listener=Listener();commands=[];rec={};data={}
    def remote(client,command,*args,**kwargs):
        commands.append(command)
        if 'network.wireless status' in command: value={'radio0':{'up':True}}
        elif 'get_clients' in command: value={'clients':{'fc:ec:da:c2:54:0a':dict(auth=True,assoc=True,authorized=True,wds=True)}}
        else: value={}
        return dict(exit_code=0,stdout=json.dumps(value),stderr='')
    namespace=dict(json=json,re=re,shlex=shlex,a=SimpleNamespace(require=require),HERE=diagnostic.parent,
                   time=SimpleNamespace(monotonic=lambda:0,sleep=lambda _:None),
                   readonly_command=remote,before_deadline=remote,subscribe_WA=lambda _:(listener,'12','34'))
    exec(compile(ast.Module(body=[extract(diagnostic,'acquire_secure_WA')],type_ignores=[]),str(diagnostic),'exec'),namespace)
    helper=SimpleNamespace(readiness=lambda *args:dict(synthetic=True))
    if frequency==5180:
        namespace['acquire_secure_WA'](object(),helper,rec,data,lambda:None)
        assert rec['WA_secure_authorized'] is True
    else:
        with pytest.raises(RuntimeError,match='WA_PROBE_CONTEXT_CHANGED'):
            namespace['acquire_secure_WA'](object(),helper,rec,data,lambda:None)
        assert 'WA_secure_authorized' not in rec
    assert listener.closed and rec['discovery_listener_id']==dict(pid='12',ticks='34')
    assert 'discovery_listener_ended' not in rec  # Verification must follow the useful CPE reads.
    assert not any('kill -TERM "$p"' in command for command in commands)
    assert ('WA_discovery_clear' in rec)==(frequency==5180)



def test_readonly_rejected_query_keeps_its_result_for_private_diagnostics():
    import io
    import threading
    diagnostic=ROOT/'artifacts/canary_panel1_guarida/preprod1_r5m_WA_readonly_20261022.py'
    class Channel:
        def settimeout(self,value): pass
        def exec_command(self,command): pass
        def shutdown_write(self): pass
        def makefile(self,*args): return io.BytesIO(b'LISTENER_ENDED\n')
        def makefile_stderr(self,*args): return io.BytesIO(b'synthetic unexpected stderr')
        def recv_exit_status(self): return 0
        def close(self): pass
    client=SimpleNamespace(get_transport=lambda:SimpleNamespace(open_session=lambda **kwargs:Channel()))
    namespace=dict(threading=threading,a=SimpleNamespace(require=require))
    exec(compile(ast.Module(body=[extract(diagnostic,'readonly_command')],type_ignores=[]),str(diagnostic),'exec'),namespace)
    with pytest.raises(RuntimeError,match='READONLY_QUERY_EXIT_0') as error:
        namespace['readonly_command'](client,'synthetic readonly query',timeout=.1)
    assert error.value.query_result==dict(exit_code=0,stdout='LISTENER_ENDED\n',stderr='synthetic unexpected stderr')


@pytest.mark.parametrize('target', ['fc:ec:da:c2:54:0a', 'b4:fb:e4:5c:d5:d2',
                                   '64:d1:54:1b:96:97', 'f0:9f:c2:b2:b6:ba'])
def test_actual_drop_is_exact_target_reason3_only_for_xc_without_ban(tmp_path, target):
    import json
    source = (ROOT / 'tools/bench/preprod1_admitter.sh').read_text(encoding='utf8')
    block = 'drop_reason=2' + source.split('    drop_reason=2', 1)[1].split('\n    phase=WAIT_LOSS', 1)[0]
    directory = str(tmp_path).replace('\\', '/')
    script = 'set -e\nD=' + shlex.quote(directory) + '\n'
    script += 'target=' + shlex.quote(target) + '; drop_n=1; OBJ=hostapd.phy0-ap0; XC=b4:fb:e4:5c:d5:d2\n'
    script += 'log() { :; }\nubus() { test "$1 $2 $3 $4 $5" = "-t 4 call hostapd.phy0-ap0 del_client"; printf "%s" "$6" > "$D/request.json"; }\n'
    run_shell_fixture(script + block)
    request = json.loads((tmp_path / 'request.json').read_text())
    assert request == dict(addr=target, reason=3 if target=='b4:fb:e4:5c:d5:d2' else 2, deauth=True, ban_time=0)


@pytest.mark.parametrize('stock', ['WA', 'XC'])
@pytest.mark.parametrize('probe,accepted', [
    ('probe_address=; probe_target=', False),
    ('probe_address=02:00:00:00:00:01; probe_target=ff:ff:ff:ff:ff:ff', False),
    ('probe_address=$WA; probe_target=18:e8:29:74:55:a2', False),
    ('probe_address=$WA; probe_target=ff:ff:ff:ff:ff:ff', True),
])
def test_recovery_old_broadcast_cannot_clear_on_an_unrelated_current_event(probe, accepted, stock):
    prefix=stock.lower()
    script = shell_header() + 'phase=RECOVER; target=$'+stock+'; seen_'+prefix+'=1; '+prefix+'_clear_not_before=120; t=121\n'
    script += probe.replace('$WA', '$'+stock) + '\n' + shell_decision_block()
    script += '\ntest "$clears" = ' + ('1' if accepted else '0') + '\n'
    run_shell_fixture(script)


def parser_poll_block():
    source = (ROOT / 'tools/bench/preprod1_admitter.sh').read_text()
    start = source.index(' probe_address=; probe_target=')
    end = source.index(' if test "$probe_address" = "$WA"; then', start)
    return source[start:end]


@pytest.mark.parametrize('clock_values,expected', [('0 0 0 0', 1), ('0 0 1 1', 2)])
def test_partial_json_does_not_repeat_expensive_station_poll(clock_values, expected):
    script = '''set -eu
D=$(mktemp -d); trap 'rm -rf "$D"' EXIT
printf '%s\\n' '{' '  "probe": {' '  "address": "synthetic"' '}}' > "$D/input"
exec 3< "$D/input"
phase=ADMIT; phase_end=100; end=1000; buf=; polls=0; next_state_poll=1
event_complete=0; read_lines=0; decoded_events=0; partial_skips=0; state_polls=0
collect() { polls=$((polls+1)); }
now() { echo "$fixture_clock"; }
jsonfilter() {
 case "$4" in
  @) case "$2" in *'}}') return 0;; *) return 1;; esac;;
  *) :;;
 esac
}
'''
    script += 'for fixture_clock in ' + clock_values + '; do\n' + parser_poll_block() + '\ndone\n'
    script += 'test "$polls" = ' + str(expected) + '\n'
    run_shell_fixture(script)


@pytest.mark.parametrize('phase,code', [('ADMIT', 76), ('WAIT_LOSS', 77), ('RECOVER', 78)])
def test_partial_event_cannot_bypass_original_phase_deadline(phase, code):
    block = parser_poll_block()
    script = '''set -eu
D=$(mktemp -d); trap 'rm -rf "$D"' EXIT
printf '%s\\n' '{' > "$D/input"; exec 3< "$D/input"
buf=; phase_end=100; end=1000; next_state_poll=101
read_lines=0; decoded_events=0; partial_skips=0; state_polls=0
now() { echo 100; }
collect() { :; }
jsonfilter() { return 1; }
set +e
(
'''
    script += 'phase=' + phase + '\n' + block + '\n)\nrc=$?\n'
    script += 'test "$rc" = ' + str(code) + '\n'
    run_shell_fixture(script)


@pytest.mark.parametrize('phase,code', [('ADMIT', 76), ('WAIT_LOSS', 77), ('RECOVER', 78), ('STABLE', 83)])
def test_station_poll_crossing_deadline_stops_before_any_ie_decision(phase, code):
    script = '''set -eu
D=$(mktemp -d); trap 'rm -rf "$D"' EXIT
printf '%s\\n' '{' > "$D/input"; exec 3< "$D/input"
buf=; fixture_clock=99; phase_end=100; end=100; next_state_poll=0
read_lines=0; decoded_events=0; partial_skips=0; state_polls=0
now() { echo "$fixture_clock"; }
collect() { fixture_clock=100; }
jsonfilter() { return 1; }
log() { :; }
set +e
(
'''
    script += 'phase=' + phase + '\n' + parser_poll_block() + '\n)\nrc=$?\n'
    script += 'test "$rc" = ' + str(code) + '\n'
    run_shell_fixture(script)


def trace_namespace():
    path = ROOT / 'artifacts/canary_panel1_guarida/preprod1_AP_debug_20261022.py'
    import re
    namespace = dict(re=re, access=SimpleNamespace(require=require, sha=lambda b: __import__('hashlib').sha256(b).hexdigest()))
    nodes = [extract(path, name) for name in ['public_context', 'APTrace']]
    namespace['XC'] = 'b4:fb:e4:5c:d5:d2'
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace


@pytest.mark.parametrize('failed', ['capture', 'logging_restore', 'RAM_cleanup', 'guard_end'])
def test_debug_failure_never_skips_remaining_restoration(tmp_path, failed):
    calls = []
    ns = trace_namespace()
    trace = ns['APTrace'].__new__(ns['APTrace'])
    record = dict(errors=[], guard_ended_verified=True, logger_restore_acknowledged=True,
                  level_restored_verified=True, ram_cleanup_verified=True)
    def action(label):
        calls.append(label)
        if label == failed:
            raise RuntimeError('FIXTURE_' + label)
    def save():
        (tmp_path / 'receipt.json').write_text(__import__('json').dumps(record))
    trace.proxy = SimpleNamespace(record=record, out=tmp_path,
                                  restore_level=lambda ap: action('logging_restore'),
                                  cleanup=lambda ap: action('RAM_cleanup'), save=save)
    trace.sample = lambda ap, force=False: action('capture')
    trace.verify_guard_ended = lambda ap: action('guard_end')
    trace.started=True; trace.finished=False; trace.guard=['12','34']
    trace.capture_count=1; trace.new_lines=[]
    result = trace.finish(None)
    assert calls == ['capture', 'logging_restore', 'RAM_cleanup', 'guard_end']
    assert result['status'] == 'TRACE_INCOMPLETE'
    assert len(result['errors']) == 1 and failed in result['errors'][0]
    assert trace.finish(None) is result
    assert len(calls) == 4


def test_public_ap_context_omits_keys_and_other_stations():
    ns = trace_namespace()
    lines = ['hostapd: unrelated old station'] * 3 + [
        'hostapd: phy0-ap0: STA aa:bb:cc:dd:ee:ff connected',
        'hostapd: phy0-ap0: STA ' + ns['XC'] + ' authenticated',
        'hostapd: phy0-ap0: STA ' + ns['XC'] + ' peer aa:bb:cc:dd:ee:ff rejected',
        'hostapd: PSK - hexdump: synthetic_secret',
        'hostapd: passphrase=synthetic_secret',
        'hostapd: phy0-ap0: association rejected: invalid rates',
    ]
    result = ns['public_context'](lines)
    assert any('invalid rates' in line for line in result)
    assert not any('synthetic_secret' in line for line in result)
    assert not any('aa:bb:cc:dd:ee:ff' in line for line in result)


def test_debug_is_staged_before_radio_and_restored_before_profile_reload():
    main = extract(SOURCE, 'main')
    acquisition = next(n for n in main.body if isinstance(n, ast.Try))
    calls = [(ast.unparse(n), n.lineno) for n in ast.walk(acquisition) if isinstance(n, ast.Call)]
    staged = next(line for call,line in calls if call == 'ap_trace.stage(ap)')
    armed = next(line for call,line in calls if call == 'helper.arm(ap)')
    assert staged < armed
    final_calls = [(ast.unparse(n),n.lineno) for statement in acquisition.finalbody
                   for n in ast.walk(statement) if isinstance(n,ast.Call)]
    finish = next(line for call,line in final_calls if call == 'ap_trace.finish(ap)')
    assert finish < min(line for call,line in final_calls if call in ['mode(False)', 'helper.restore(ap)'])


@pytest.mark.parametrize('force,expected', [(False, 13), (True, 14)])
def test_ap_trace_reserves_last_snapshot_for_final_capture(force, expected):
    ns=trace_namespace();ns['time']=SimpleNamespace(monotonic=lambda:100)
    trace=ns['APTrace'].__new__(ns['APTrace'])
    trace.started=True;trace.finished=False;trace.capture_count=13;trace.next_capture=0
    trace.seen_lines=set();trace.new_lines=[]
    writes=[]
    trace.proxy=SimpleNamespace(checked=lambda *a:b'hostapd: synthetic\n',
                                private=lambda name,raw:writes.append(name),record={},save=lambda:None)
    trace.sample(None,force=force)
    assert trace.capture_count==expected
    assert len(writes)==expected-13








def path_namespace():
    import re
    ns=dict(require=require,re=re,shlex=shlex)
    nodes=[extract(SOURCE,name) for name in ['path_capture_command','path_capture_evidence','validate_path_capture']]
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(SOURCE),'exec'),ns)
    return ns


def test_path_capture_is_passive_exact_echo_only():
    ns=path_namespace()
    command=shlex.split(ns['path_capture_command']('fe80::b6fb:e4ff:fe5c:d5d2'))
    assert command[:-1]==['exec','tcpdump','-p','-n','-l','-tt','-e','-s','128','-c','256','-i','any']
    assert command[-1]=='icmp6 and host fe80::b6fb:e4ff:fe5c:d5d2 and (ip6[40] == 128 or ip6[40] == 129)'
    with pytest.raises(RuntimeError,match='PATH_CAPTURE_INVALID_ADDRESS'):
        ns['path_capture_command']('fe80::1; forbidden')


@pytest.mark.parametrize('ended,stdout,stderr,rc,reason',[
    (False,b'',b'',0,'PATH_CAPTURE_NOT_ENDED'),
    (True,b'a'*65537,b'',0,'PATH_CAPTURE_OUTPUT_BOUND'),
    (True,b'',b'a'*8193,0,'PATH_CAPTURE_OUTPUT_BOUND'),
    (True,b'',b'',1,'PATH_CAPTURE_EXIT_FAILED'),
    (True,b'a'*65536,b'b'*(8192-len(b'listening on any,\n')),0,None),
],ids=['unfinished','stdout-overflow','stderr-overflow','exit-failure','exact-bounds'])
def test_path_capture_boundaries_and_failure_preservation(ended,stdout,stderr,rc,reason):
    reads=[]
    def reader(data):
        def read(size):
            reads.append(size);return data[:size]
        return read
    channel=SimpleNamespace(exit_status_ready=lambda:ended,recv_exit_status=lambda:rc)
    stream=(None,SimpleNamespace(channel=channel,read=reader(stdout)),SimpleNamespace(read=reader(stderr)))
    ns=path_namespace();output=ns['path_capture_evidence'](stream,bytearray(b'listening on any,\n'))
    if reason:
        with pytest.raises(RuntimeError,match=reason):ns['validate_path_capture'](output)
    else:ns['validate_path_capture'](output)
    assert len(output.get('stdout',''))<=65536 and len(output.get('stderr',''))<=8192
    assert reads==([65537,8193] if ended else [])


def test_path_capture_requires_actual_listening_header():
    with pytest.raises(RuntimeError,match='PATH_CAPTURE_NOT_LISTENING'):
        path_namespace()['validate_path_capture'](dict(ended=True,truncated=False,exit_code=0,startup_stderr='tcpdump: any\n'))


def test_path_capture_shares_barrier_and_cleanup_without_extra_ping():
    main=extract(SOURCE,'main')
    acquisition=next(n for n in main.body if isinstance(n,ast.Try))
    branch=next(n for n in ast.walk(acquisition) if isinstance(n,ast.If) and ast.unparse(n.test)=="epoch == 0 and plan.get('AP_path_capture') is True")
    text=ast.unparse(branch)
    assert "deadline=setup['listening_deadline']" in text
    assert "'now-start>=60', 'now-start>=45'" in text and 'timeout=48' in text
    assert text.count('ap.exec_command(')==1 and 'ping=' not in text
    assert 'owned_captures.append(cap)' in text and 'startup_threads.append(watcher)' in text
    assert "setup['captures'].append" not in text
    whole=ast.unparse(main)
    assert 'listening.append(capture_startup_ready(state))' in whole
    final=ast.unparse(ast.Module(body=acquisition.finalbody,type_ignores=[]))
    assert final.index("'CAPTURE_NATIVE_GUARD_NOT_ENDED'")<final.index('path_capture_evidence(cap, header)')
    assert final.index("private('epoch0-XC-any-path.json', output)")<final.index('validate_path_capture(output)')<final.index('mode(False)')
    assert "plan.get('AP_path_capture') is not True or rec.get('AP_path_capture_verified')" in final


def test_original_radio_capture_requests_immediate_small_buffer_delivery():
    main=extract(SOURCE,'main')
    assignment=next(n for n in ast.walk(main) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='capcmd' for t in n.targets))
    command=eval(compile(ast.Expression(body=assignment.value),str(SOURCE),'eval'),dict(shlex=shlex,device='phy0-ap0.sta2',filt='icmp6 and host fe80::1'))
    assert shlex.split(command)==['exec','tcpdump','--immediate-mode','-B','64','-p','-n','-l','-tt','-s','128','-c','64','-i','phy0-ap0.sta2','icmp6 and host fe80::1']


def test_failure_context_is_bounded_and_does_not_serialize_locals_or_source():
    import traceback
    ns=dict(Path=Path,traceback=traceback)
    exec(compile(ast.Module(body=[extract(SOURCE,'failure_record')],type_ignores=[]),str(SOURCE),'exec'),ns)
    def nested(depth):
        secret_local='PRIVATE_FIXTURE_LOCAL_ONLY'
        if depth:return nested(depth-1)
        raise TimeoutError('x'*300)
    try:nested(12)
    except TimeoutError as error:record=ns['failure_record'](error)
    assert record['type']=='TimeoutError' and len(record['gate'])==180 and len(record['frames'])==8
    assert 'PRIVATE_FIXTURE_LOCAL_ONLY' not in repr(record)
    assert all(set(frame)=={'file','line','function'} and '/' not in frame['file'] and '\\' not in frame['file'] for frame in record['frames'])


@pytest.mark.parametrize('ended', [True,False])
def test_failed_ie_clear_remains_fatal_but_ended_owned_ram_cleanup_proceeds(ended):
    import hashlib
    main=extract(SOURCE,'main');acquisition=next(n for n in main.body if isinstance(n,ast.Try))
    block=next(n for n in acquisition.finalbody if isinstance(n,ast.If) and ast.unparse(n.test)=='ap is not None and daemon_dir is not None')
    commands=[]
    data={'restore.rc':'249\n','exit.rc':'249\n','stop.reason':'error\n','actions.log':'ENDED\n','stderr':'clear failed','listener.stderr':'','events.jsonl':'','state.log':''}
    def remote(client,command,**kwargs):
        commands.append(command)
        if command.startswith('cat '):return dict(stdout=data[command.rsplit('/',1)[1]],stderr='',exit_code=0)
        if 'kill -USR1 ' in command and not ended:raise RuntimeError('OWN_DAEMON_STILL_LIVE_FIXTURE')
        return dict(stdout='ENDED\n',stderr='',exit_code=0)
    rec=dict(cleanup_errors=[])
    ns=dict(ap=object(),daemon_dir='/tmp/fmx-admitter-'+'a'*24,daemon_id=['12','34'],remote=remote,rec=rec,diagnostic=False,re=__import__('re'),
            private=lambda *args:dict(file='fixture.json'),daemon_source=b'synthetic source',sha=lambda raw:hashlib.sha256(raw).hexdigest(),require=require)
    exec(compile(ast.Module(body=[block],type_ignores=[]),str(SOURCE),'exec'),ns)
    assert rec['cleanup_errors'] and not rec.get('daemon_acceptance')
    removed=any('rmdir "$D"' in command for command in commands)
    assert removed is ended and bool(rec.get('daemon_RAM_files_removed')) is ended
    if ended:assert rec['daemon_restore_rc']=='249' and 'DAEMON_CLEAR_FAILED_249' in rec['cleanup_errors'][0]


def quality_namespace():
    import math,re
    ns=dict(require=require,math=math,re=re,LABELS=dict(wa='WA',xc='XC',sxt='SXT',m5='LBM5'))
    nodes=[extract(SOURCE,name) for name in ['stream_quality','traffic_qualification_complete']]
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(SOURCE),'exec'),ns)
    return ns


def quality_fixture(received=32,pairs=32):
    ping=(''.join('64 bytes: seq='+str(n)+' time=1.000 ms\n' for n in range(received))+
          '32 packets transmitted, '+str(received)+' packets received\n').encode()
    capture=''.join('ICMP6, echo '+kind+', id 7, seq '+str(n)+'\n' for n in range(pairs) for kind in ['request','reply']).encode()
    return [ping,b'',0,capture,b'',0,'XC']


@pytest.mark.parametrize('received,pairs',[(32,32),(31,32),(32,31),(30,30),(0,0)])
def test_packet_deficits_are_returned_unrescored_without_aborting_recovery_observation(received,pairs):
    quality=quality_namespace()['stream_quality'](*quality_fixture(received,pairs))
    assert (quality['received'],quality['paired'],quality['reply_timings'])==(received,pairs,received)
    assert quality['qualifying'] is (received==32 and pairs==32)
    assert bool(quality['failures']) is not quality['qualifying']


@pytest.mark.parametrize('index,value,reason',[
    (0,b'x'*16385,'QUALIFY_PING_OUTPUT_BOUND'),
    (3,b'x'*32769,'QUALIFY_CAPTURE_OUTPUT_BOUND'),
    (1,b'error','QUALIFY_PING_EXIT_FAILED'),
    (2,1,'QUALIFY_PING_EXIT_FAILED'),
    (5,1,'QUALIFY_CAPTURE_EXIT_FAILED'),
    (0,b'malformed','QUALIFY_PING_FORMAT_FAILED'),
],ids=['ping-bound','capture-bound','stderr','ping-exit','capture-exit','malformed'])
def test_invalid_acquisition_still_stops_immediately(index,value,reason):
    args=quality_fixture();args[index]=value
    with pytest.raises(RuntimeError,match=reason):quality_namespace()['stream_quality'](*args)


def test_final_traffic_gate_rechecks_all_twenty_original_streams():
    ns=quality_namespace();valid=ns['stream_quality'](*quality_fixture())
    epochs={str(n):{name:dict(valid) for name in ns['LABELS'].values()} for n in range(5)}
    assert ns['traffic_qualification_complete'](epochs)
    for epoch,rows in epochs.items():
        for name,row in rows.items():
            row['received']=31
            assert not ns['traffic_qualification_complete'](epochs)
            row['received']=32
    epochs['4'].pop('LBM5')
    assert not ns['traffic_qualification_complete'](epochs)


def test_pending_epoch_records_deficit_and_finishes_all_four_streams():
    import io
    ns=quality_namespace();flows=[];headers={}
    def stream(raw):
        channel=SimpleNamespace(recv_exit_status=lambda:0)
        return (None,SimpleNamespace(read=io.BytesIO(raw).read,channel=channel),SimpleNamespace(read=lambda n:b''))
    for mac in ns['LABELS']:
        args=quality_fixture(received=30 if mac=='xc' else 32,pairs=30 if mac=='xc' else 32)
        ping=stream(args[0]);cap=stream(args[3]);headers[id(cap)]=bytearray()
        flows.append((mac,'radiochild',ping,cap))
    pending=[(0,flows)];rec=dict(epoch_pending={'0':dict(capture_deadline=100)},failures=[])
    ns.update(pending_epochs=pending,rec=rec,traffic_ready=lambda *args:True,capture_headers=headers,
              private=lambda name,value:dict(file=name),save=lambda:None)
    main=extract(SOURCE,'main')
    block=next(n for n in ast.walk(main) if isinstance(n,ast.For) and ast.unparse(n.iter)=='pending_epochs[:]')
    exec(compile(ast.Module(body=[block],type_ignores=[]),str(SOURCE),'exec'),ns)
    assert pending==[] and len(rec['epoch_stream_artifacts'])==4
    assert set(rec['epoch_traffic']['0'])==set(ns['LABELS'].values())
    assert rec['epoch_traffic']['0']['XC']['received']==30
    assert {row['gate'] for row in rec['failures']}=={'QUALIFY_ECHO_FAILED_XC','QUALIFY_RADIO_PAIRS_FAILED_XC'}
    assert not ns['traffic_qualification_complete'](rec['epoch_traffic'])
    text=ast.unparse(main)
    assert text.index("require(rec['traffic_qualification_complete'], 'TRAFFIC_QUALIFICATION_FAILED')")<text.index("rec['multicycle_pass'] = not diagnostic")


def postwindow_namespace(tmp_path):
    import hashlib,json,re
    ns=dict(HERE=tmp_path,require=require,re=re,json=json,Path=Path,
            sha=lambda raw:hashlib.sha256(raw).hexdigest(),time=SimpleNamespace(monotonic=lambda:100))
    ns['failure_record']=lambda error:dict(type=type(error).__name__,gate=str(error))
    exec(compile(ast.Module(body=[extract(SOURCE,'postwindow_xc_evidence')],type_ignores=[]),str(SOURCE),'exec'),ns)
    parent=tmp_path/'preprod_guarida_20261022'/'history';parent.mkdir(parents=True)
    return ns,parent/'preprod1_fixture_XC_postwindow'


@pytest.mark.parametrize('window,ended,wrong_path',[(True,True,False),(False,False,False),(False,True,True)])
def test_postwindow_reads_require_native_end_closed_window_and_private_scope(tmp_path,window,ended,wrong_path):
    ns,directory=postwindow_namespace(tmp_path);calls=[]
    if wrong_path:directory=tmp_path/'outside'
    with pytest.raises(RuntimeError,match='XC_DIAGNOSTIC_'):
        ns['postwindow_xc_evidence'](None,directory,lambda *a,**kw:calls.append(a),[],window,ended)
    assert calls==[] and not directory.exists()


@pytest.mark.parametrize('failed',[None,'tail','dmesg'])
def test_postwindow_diagnostics_retain_private_raw_and_continue_after_read_failure(tmp_path,failed):
    import json
    ns,directory=postwindow_namespace(tmp_path);calls=[];audit=[]
    def read(client,command,**kwargs):
        calls.append(command)
        assert kwargs==dict(timeout=5,limit=32768,check=False)
        if failed and command.startswith(failed):raise RuntimeError('PRIVATE_FIXTURE_SECRET')
        return dict(exit_code=0,stderr='',stdout='wpa_state=SCANNING\nPRIVATE_FIXTURE_SECRET\n')
    record=ns['postwindow_xc_evidence'](None,directory,read,audit,False,True)
    assert len(calls)==4 and len(audit)==4 and all(row['window'] is False and row['postwindow_readonly'] for row in audit)
    assert record['wpa_state']=='SCANNING' and record['private_raw']
    assert record['status']==('INCOMPLETE_POSTWINDOW_READONLY' if failed else 'CAPTURED_POSTWINDOW_READONLY')
    assert 'PRIVATE_FIXTURE_SECRET' not in json.dumps(record)
    assert len(list(directory.glob('*.json')))==4
    assert 'PRIVATE_FIXTURE_SECRET' in (directory/'status.json').read_text()


def test_postwindow_diagnostic_is_guarded_after_native_end_before_profile_restoration():
    main=extract(SOURCE,'main');acquisition=next(n for n in main.body if isinstance(n,ast.Try))
    final=ast.unparse(ast.Module(body=acquisition.finalbody,type_ignores=[]))
    start=final.index('control_window = False')
    proof=final.index("rec['daemon_ended_verified'] = remote(")
    diagnostic=final.index('postwindow_xc_evidence(rocket, directory, reader.readonly_command,')
    assert start<proof<diagnostic<final.index('mode(False)')<final.index('restore_AP_resources(helper, ap_compat, ap, armed)')
    assert "get('stdout', '').strip() == 'ENDED'" in final
    assert 'time.monotonic() + 45 < min(whole_end, legacy_end or whole_end)' in final


MGMT_SOURCE = ROOT / 'artifacts/canary_panel1_guarida/preprod1_AP_mgmt_20261022.py'


def mgmt_namespace():
    import hashlib, re, threading
    ns = dict(Path=Path, re=re, shlex=shlex, threading=threading,
              access=SimpleNamespace(require=require, sha=lambda b: hashlib.sha256(b).hexdigest()),
              XC=bytes.fromhex('b4fbe45cd5d2'), AP=bytes.fromhex('18e8297455a2'),
              RAW_LIMIT=262144, FRAME_LIMIT=2000)
    nodes = [extract(MGMT_SOURCE, name) for name in ['frame_summary', 'APTrace']]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(MGMT_SOURCE), 'exec'), ns)
    return ns


def mgmt_frame(ies=b'\x00\x0dFuturaMAX-LAB\x01\x02\x8c\x12', foreign=False):
    # AssocReq header and fixed fields, no RF or acquisition code execution.
    return (b'\x00\x00\x00\x00' + bytes.fromhex('18e8297455a2')
            + bytes.fromhex('001122334455' if foreign else 'b4fbe45cd5d2')
            + bytes.fromhex('18e8297455a2') + b'\x10\x00\x31\x04\x0a\x00' + ies)


def mgmt_event(frame):
    return b'IFNAME=phy0-ap0 <3>AP-MGMT-FRAME-RECEIVED buf=' + frame.hex().encode() + b'\n'


def test_mgmt_summary_keeps_exact_received_ie_failure_without_exporting_payload():
    import json
    ns = mgmt_namespace()
    raw = mgmt_event(mgmt_frame(b'\x00\x0dPRIVATE_SSID!\x30\x02\x01\x00\xdd\x0fshort'))
    result = ns['frame_summary'](raw)
    assert len(result) == 1 and result[0]['subtype'] == 0
    assert result[0]['SSID_exact_one_lab_match'] is False
    assert result[0]['association_parse_error'] == 'received_IE_length_exceeds_body'
    assert result[0]['invalid_IE'] == dict(id=221, declared_bytes=15, remaining_bytes=5)
    assert 'PRIVATE_SSID' not in json.dumps(result) and 'short' not in json.dumps(result)


def test_mgmt_summary_omits_foreign_frames_and_parses_real_structure():
    ns = mgmt_namespace()
    result = ns['frame_summary'](mgmt_event(mgmt_frame(foreign=True)) + mgmt_event(mgmt_frame()))
    assert len(result) == 1
    assert result[0]['SSID_exact_one_lab_match'] is True
    assert result[0]['capability'] == 0x431 and result[0]['listen_interval'] == 10
    assert result[0]['sequence_control'] == 16 and result[0]['sequence'] == 1
    assert result[0]['ies'][1]['rates_hex'] == '8c12'


@pytest.mark.parametrize('value', [b'0', b'zz', b'00' * 23, b'00' * 2024],
                         ids=['odd-hex', 'non-hex', 'short-header', 'cli-cap'])
def test_mgmt_summary_never_accepts_incomplete_or_capped_control_hex(value):
    with pytest.raises(RuntimeError, match='AP_MGMT_FRAME_TRUNCATED_OR_INVALID'):
        mgmt_namespace()['frame_summary'](b'AP-MGMT-FRAME-RECEIVED buf=' + value + b'\n')


def mgmt_fixture(tmp_path, pong=True):
    import json
    tmp_path.mkdir(exist_ok=True)
    ns = mgmt_namespace()
    clock = [0.0]
    ns['time'] = SimpleNamespace(monotonic=lambda: clock[0], sleep=lambda n: clock.__setitem__(0, clock[0] + n))
    actions, commands, files, chunks = [], [], {}, [b'Interactive mode\n> PONG\n' if pong else b'Interactive mode\n> ']
    channel = SimpleNamespace(recv_ready=lambda: bool(chunks), recv=lambda n: chunks.pop(0),
        recv_stderr_ready=lambda: False, exit_status_ready=lambda: channel.ended,
        settimeout=lambda n: None, close=lambda: None, ended=False)
    def write(value):
        if value == 'quit\n':
            channel.ended = True
    stdin = SimpleNamespace(write=write, flush=lambda: None, close=lambda: None)
    stdout = SimpleNamespace(channel=channel, readline=lambda n: 'MGMT_LISTENER 100 200 300 400\n', close=lambda: None)
    stderr = SimpleNamespace(close=lambda: None)
    channel.makefile_stdin = lambda *a: stdin
    channel.makefile = lambda *a: stdout
    channel.makefile_stderr = lambda *a: stderr
    channel.exec_command = lambda command: commands.append(command)
    def checked(ap, command, **kwargs):
        commands.append(command)
        if '/var/run/hostapd-phy0.conf' in command:
            return b'interface=phy0-ap0\n'
        if command.startswith('CTRL:'):
            return b'OK\n'
        if 'echo MGMT_GUARD_LIVE_SOURCE_BOUND' in command:
            return b'MGMT_GUARD_LIVE_SOURCE_BOUND\n'
        if 'echo ENDED' in command:
            return b'ENDED\n'
        return b''
    record = dict(binary_sha256='b' * 64)
    def private(name, raw):
        (tmp_path / name).write_bytes(raw)
        record[name] = dict(bytes=len(raw), sha256=ns['access'].sha(raw))
    proxy = SimpleNamespace(created=True, directory='/tmp/fmx-assoc-debug-fixture', out=tmp_path,
        record=record, daemon=b'123 456\n', guard_started=False,
        identity=lambda ap: actions.append('identity'), checked=checked,
        control=lambda command: 'CTRL:' + command,
        put=lambda ap, name, raw, mode: files.__setitem__(name, raw), private=private,
        save=lambda: (tmp_path / 'receipt.json').write_text(json.dumps(record), encoding='utf-8'))
    def cleanup(ap):
        actions.append('cleanup')
        record['ram_cleanup_verified'] = True
    proxy.cleanup = cleanup
    trace = ns['APTrace'].__new__(ns['APTrace'])
    trace.proxy, trace.wpad_sha = proxy, 'f' * 64
    trace.guard_seconds = 90
    trace.stream = trace.listener = trace.guard = trace.result = None
    trace.raw, trace.error = bytearray(), bytearray()
    trace.started = trace.finished = trace.changed = False
    ap = SimpleNamespace(exec_command=lambda command, **kwargs: (commands.append(command) or (stdin, stdout, stderr)),
                         get_transport=lambda: SimpleNamespace(open_session=lambda **kwargs: channel))
    return trace, ap, commands, actions, files, chunks


def test_mgmt_listener_is_natively_guarded_before_exec_and_needs_attached_ping(tmp_path):
    trace, ap, commands, actions, files, chunks = mgmt_fixture(tmp_path)
    trace.start(ap)
    launch = next(c for c in commands if 'MGMT_LISTENER' in c)
    assert launch.index('/guard.sh') < launch.index('exec /tmp/')
    assert ' -a ' not in launch and trace.proxy.record['interactive_attach_ping_ready']
    assert 'while test $n -lt 90' in files['guard.sh'].decode()
    assert 'SET notify_mgmt_frames 0' in files['guard.sh'].decode()
    assert 'NOTIFY_RESET_FAILED' in files['guard.sh'].decode()
    assert commands[-1] == 'CTRL:SET notify_mgmt_frames 1'
    chunks.append(mgmt_event(mgmt_frame()))
    result = trace.finish(ap)
    assert result['status'] == 'TRACE_COMPLETE' and result['listener_ended_verified']
    assert result['notify_restore_acknowledged'] and result['guard_ended_verified']
    assert commands.index('CTRL:SET notify_mgmt_frames 0') < commands.index('touch /tmp/fmx-assoc-debug-fixture/disarm')
    assert actions[-1] == 'cleanup' and len(result['XC_RX_frames']) == 1
    native_bash = Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Git/bin/bash.exe'
    bash = str(native_bash) if native_bash.is_file() else shutil.which('bash')
    if bash:
        for program in [files['guard.sh'], launch.encode()]:
            check = subprocess.run([bash, '-n'], input=program, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
            assert check.returncode == 0, check.stderr.decode(errors='replace')


def test_mgmt_readiness_failure_cannot_enable_notification_and_still_cleans(tmp_path):
    trace, ap, commands, actions, files, chunks = mgmt_fixture(tmp_path, pong=False)
    with pytest.raises(RuntimeError, match='AP_MGMT_ATTACH_PING_DEADLINE'):
        trace.start(ap)
    result = trace.finish(ap)
    assert 'CTRL:SET notify_mgmt_frames 1' not in commands
    assert result['status'] == 'TRACE_INCOMPLETE' and result['listener_ended_verified']
    assert result['guard_ended_verified'] and result['ram_cleanup_verified']


def test_mgmt_failed_host_reset_keeps_native_guard_but_stops_listener_and_archives(tmp_path):
    trace, ap, commands, actions, files, chunks = mgmt_fixture(tmp_path)
    trace.start(ap)
    chunks.append(mgmt_event(mgmt_frame()))
    original = trace.proxy.checked
    def failed(ap, command, **kwargs):
        if command == 'CTRL:SET notify_mgmt_frames 0':
            raise RuntimeError('CONTROL_UNAVAILABLE')
        return original(ap, command, **kwargs)
    trace.proxy.checked = failed
    result = trace.finish(ap)
    assert result['status'] == 'TRACE_INCOMPLETE' and result['listener_ended_verified']
    assert (tmp_path / 'mgmt-stream.txt').is_file()
    assert 'touch /tmp/fmx-assoc-debug-fixture/disarm' not in commands
    assert 'cleanup' not in actions  # Keep live/unverified guard source intact.


def test_mgmt_dead_or_unbound_guard_cannot_enable_notifications(tmp_path):
    trace, ap, commands, actions, files, chunks = mgmt_fixture(tmp_path)
    original = trace.proxy.checked
    def dead_guard(ap, command, **kwargs):
        if 'echo MGMT_GUARD_LIVE_SOURCE_BOUND' in command:
            return b'NOT_READY\n'
        return original(ap, command, **kwargs)
    trace.proxy.checked = dead_guard
    with pytest.raises(RuntimeError, match='AP_MGMT_GUARD_NOT_LIVE_SOURCE_BOUND'):
        trace.start(ap)
    assert 'CTRL:SET notify_mgmt_frames 1' not in commands
    result = trace.finish(ap)
    assert result['status'] == 'TRACE_INCOMPLETE' and result['listener_ended_verified']
    assert result['guard_ended_verified'] and result['ram_cleanup_verified']


def test_mgmt_stream_overflow_is_bounded_and_does_not_skip_listener_stop(tmp_path):
    trace, ap, commands, actions, files, chunks = mgmt_fixture(tmp_path)
    trace.start(ap)
    trace.raw.extend(b'x' * (262145 - len(trace.raw)))
    chunks.append(b'x')
    with pytest.raises(RuntimeError, match='AP_MGMT_STREAM_BOUND'):
        trace.sample(ap)
    result = trace.finish(ap)
    assert result['status'] == 'TRACE_INCOMPLETE' and result['listener_ended_verified']
    assert result['notify_restore_acknowledged'] and result['ram_cleanup_verified']
    assert (tmp_path / 'mgmt-stream.txt').stat().st_size == 262144
    assert result['raw_capture_truncated'] is True and result['raw_observed_bytes_at_least'] == 262145


def test_mgmt_exec_ack_wait_is_owned_and_absolute_deadline_bounded(tmp_path):
    import threading, time
    trace, ap, commands, actions, files, chunks = mgmt_fixture(tmp_path)
    event, delays = threading.Event(), []
    channel = ap.get_transport().open_session(timeout=5)
    def close():
        channel.ended = True
        event.set()
    channel.close = close
    def pending(command):
        commands.append(command)
        assert event.wait(.4), 'exec ACK was not bounded by owned-channel timer'
        raise EOFError('closed by timer')
    channel.exec_command = pending
    def unbounded(*args, **kwargs):
        event.wait(.25)
        raise AssertionError('High-level SSH exec waited without an owned timer')
    ap.exec_command = unbounded
    def timer(delay, callback):
        delays.append(delay)
        return threading.Timer(.02, callback)  # Scaled clock, real blocked exec-ACK.
    trace.start.__func__.__globals__['threading'] = SimpleNamespace(Event=threading.Event, Timer=timer)
    started = time.monotonic()
    with pytest.raises(RuntimeError, match='AP_MGMT_ATTACH_PING_DEADLINE'):
        trace.start(ap)
    assert time.monotonic() - started < .2 and delays == [5]
    assert trace.stream is not None and event.is_set()
    result = trace.finish(ap)
    assert result['status'] == 'TRACE_INCOMPLETE'
    assert 'CTRL:SET notify_mgmt_frames 1' not in commands and 'cleanup' not in actions


def test_mgmt_failure_has_independent_original_restoration_and_no_cpe_executor():
    final = ast.unparse(ast.Module(body=next(n for n in extract(SOURCE, 'main').body
        if isinstance(n, ast.Try)).finalbody, type_ignores=[]))
    assert final.index('mgmt_trace.finish(ap)') < final.index('restore_AP_resources(helper, ap_compat, ap, armed)')
    restore = ast.unparse(extract(SOURCE, 'restore_AP_resources'))
    assert restore.index('helper.restore(ap)') < restore.index('compat.verify_restored(ap)')
    assert "rec['cleanup_errors'].extend(('AP_mgmt:' + e for e in rec['AP_mgmt']['errors']))" in final
    module = ast.parse(MGMT_SOURCE.read_text(encoding='utf-8'))
    calls = [ast.unparse(n) for n in ast.walk(module) if isinstance(n, ast.Call)]
    assert not any('rocket' in call or 'wpa_cli' in call or 'GET_CONFIG' in call for call in calls)
    frozen = next(n for n in extract(SOURCE, 'main').body if isinstance(n, ast.If)
                  and ast.unparse(n.test) == "plan.get('AP_mgmt')")
    names = ast.literal_eval(frozen.body[0].iter)
    assert names == ['preprod1_AP_mgmt_20261022.py', 'root_goal_ap_assoc_debug_20261022.py',
                     'root_goal_hostapd_cli_20261022.bin']


def test_mgmt_initial_180s_then_recovery_90s_requires_exact_prior_reset(tmp_path):
    initial, ap, commands, actions, files, chunks = mgmt_fixture(tmp_path / 'initial')
    initial.guard_seconds = 180
    initial.start(ap)
    assert 'while test $n -lt 180' in files['guard.sh'].decode()
    chunks.append(mgmt_event(mgmt_frame()))
    first = initial.finish(ap)
    assert first['status'] == 'TRACE_COMPLETE' and first['guard_seconds'] == 180
    recovery, ap, commands, actions, files, chunks = mgmt_fixture(tmp_path / 'recovery')
    recovery.start(ap, previous_trace=initial)
    assert 'while test $n -lt 90' in files['guard.sh'].decode()
    chunks.append(mgmt_event(mgmt_frame()))
    second = recovery.finish(ap)
    assert second['status'] == 'TRACE_COMPLETE' and second['guard_seconds'] == 90
    assert second['previous_trace_private_receipt_sha256'] == first['private_receipt_sha256']
    assert 'prior trace reset0 ACK' in second['original_provenance']


@pytest.mark.parametrize('missing', ['finished', 'notify_restore_acknowledged', 'guard_ended_verified', 'ram_cleanup_verified'])
def test_mgmt_recovery_does_not_assume_zero_after_unproven_initial_reset(tmp_path, missing):
    trace, ap, commands, actions, files, chunks = mgmt_fixture(tmp_path)
    proof = dict(status='TRACE_COMPLETE', notify_restore_acknowledged=True, listener_ended_verified=True,
                 guard_ended_verified=True, ram_cleanup_verified=True, private_receipt_sha256='a' * 64)
    previous = SimpleNamespace(finished=missing != 'finished', result=proof)
    if missing != 'finished':
        proof[missing] = False
    with pytest.raises(RuntimeError, match='AP_MGMT_PREVIOUS_TRACE_RESET_NOT_PROVEN'):
        trace.start(ap, previous_trace=previous)
    assert 'CTRL:SET notify_mgmt_frames 1' not in commands
    assert not trace.proxy.guard_started and trace.stream is None
    result = trace.finish(ap)
    assert result['status'] == 'TRACE_INCOMPLETE' and result['ram_cleanup_verified']


def test_initial_trace_keeps_final_xc_waiting_check_adjacent_to_window_and_ends_before_load():
    text = ast.unparse(extract(SOURCE, 'main'))
    ready = text.index('initial_mgmt_trace.start(ap)')
    enable = text.index("remote(rocket, 'wpa_cli -i ath0 enable_network 0')")
    state = text.index("rec['XC_pre_window_waiting_state'] = pre_window_states[0]")
    window = text.index('control_window = True')
    assert ready < enable < state < window
    assert 'mgmt_trace.start(ap, previous_trace=initial_mgmt_trace)' in text
    finish = text.index("rec['AP_mgmt_initial'] = initial_mgmt_trace.finish(ap)")
    assert finish < text.index('if epoch >= 0 and epoch not in qualified')
