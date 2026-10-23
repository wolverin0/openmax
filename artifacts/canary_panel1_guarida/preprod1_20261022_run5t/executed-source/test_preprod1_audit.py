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
    script = shell_header() + 'phase=RECOVER; target=$XC; probe_address=$WA\n' + block
    script += '\ntest "$clears" = 0\nprobe_address=$XC\n' + block
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
    checks=[i for i,n in enumerate(flow_loop.body) if isinstance(n,ast.Expr)
            and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name)
            and n.value.func.id=='require']
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
    script+='target=$XC; ie_on=0; next_pulse=0\npulse_missing\ntest "$clear_at" = 160\n'
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
    script += 'set +e\n( old_wds_retired )\nstatus=$?\nset -e\ntest "$status" = 88\n'
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
def test_actual_drop_is_exact_target_reason2_without_ban(tmp_path, target):
    import json
    source = (ROOT / 'tools/bench/preprod1_admitter.sh').read_text(encoding='utf8')
    block = 'log "DROP_REQUEST' + source.split('log "DROP_REQUEST', 1)[1].split('\n    phase=WAIT_LOSS', 1)[0]
    directory = str(tmp_path).replace('\\', '/')
    script = 'set -e\nD=' + shlex.quote(directory) + '\n'
    script += 'target=' + shlex.quote(target) + '; drop_n=1; OBJ=hostapd.phy0-ap0\n'
    script += 'log() { :; }\nubus() { test "$1 $2 $3 $4 $5" = "-t 4 call hostapd.phy0-ap0 del_client"; printf "%s" "$6" > "$D/request.json"; }\n'
    run_shell_fixture(script + block)
    request = json.loads((tmp_path / 'request.json').read_text())
    assert request == dict(addr=target, reason=2, deauth=True, ban_time=0)


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
