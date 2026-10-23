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
            elif isinstance(node.func, ast.Name) and node.func.id == 'remote' and call.startswith('remote(rocket,'):
                if 'bss_flush 0' in call:
                    events.append('FLUSH')
                elif 'enable_network 0' in call:
                    events.append('ENABLE')
        elif isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == 'control_window' for t in node.targets):
            if isinstance(node.value, ast.Constant) and node.value.value is True:
                events.append('WINDOW')
    assert events == ['OPEN', 'SECURE', 'FLUSH', 'ENABLE', 'WINDOW']


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
good() { case " $GOOD " in *" $1 "*) return 0;; *) return 1;; esac; }
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
