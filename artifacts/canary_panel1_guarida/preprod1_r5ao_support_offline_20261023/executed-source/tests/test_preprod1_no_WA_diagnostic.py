"""The causal diagnostic preserves measurement gates and cannot qualify PREPROD1."""
import ast
import copy
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'artifacts/canary_panel1_guarida/preprod1_trial_20261022.py'
NATIVE = ROOT / 'tools/bench/preprod1_admitter.sh'
XC = 'b4:fb:e4:5c:d5:d2'
WA = 'fc:ec:da:c2:54:0a'


def functions():
    def require(ok, reason):
        if not ok:
            raise RuntimeError(reason)

    names = {'traffic_qualification_complete', 'validate_no_WA_diagnostic'}
    nodes = [n for n in ast.parse(SOURCE.read_text(encoding='utf8')).body
             if isinstance(n, ast.FunctionDef) and n.name in names]
    ns = dict(require=require, re=re, XC=XC,
              LABELS={WA: 'WA', XC: 'XC', 'sxt': 'SXT', 'm5': 'LBM5'})
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), 'exec'), ns)
    return ns


def evidence():
    actions = '\n'.join([
        '100.00 FOUR_ADMITTED', '100.00 STABLE_START epoch=0',
        '216.00 STABLE_DONE epoch=0', '216.00 STABLE_START epoch=1',
        '277.00 STABLE_DONE epoch=1', f'278.00 DROP_REQUEST n=2 target={XC} reason=3',
        f'280.00 PULSE 2 phase=RECOVER target={XC} seconds=60',
        f'310.00 RECOVERED n=2 target={XC}', '310.00 STABLE_START epoch=2',
        '371.00 STABLE_DONE epoch=2', '371.00 DIAGNOSTIC_ONLY_COMPLETE',
    ])
    stream = dict(qualifying=True, failures=[], transmitted=32, received=32,
                  reply_timings=32, paired=32)
    epochs = {str(n): {label: copy.deepcopy(stream) for label in ['WA', 'XC', 'SXT', 'LBM5']}
              for n in range(3)}
    return actions, {'2'}, epochs


def test_valid_diagnostic_is_partial_and_rejected_by_default_full_traffic_contract():
    ns = functions()
    actions, resets, epochs = evidence()
    result = ns['validate_no_WA_diagnostic'](actions, resets, epochs)
    assert result['XC_age_seconds'] == 178
    assert result['full_PREPROD1_PASS'] is False
    assert ns['traffic_qualification_complete'](epochs) is False


@pytest.mark.parametrize('mutation', ['prior_wa_drop', 'prior_ie', 'young', 'old',
                                     'short_hold', 'wrong_reset', 'full_marker',
                                     'missing_pair', 'missing_epoch', 'extra_epoch'])
def test_diagnostic_rejects_confounded_or_incomplete_evidence(mutation):
    ns = functions()
    actions, resets, epochs = evidence()
    if mutation == 'prior_wa_drop':
        actions += f'\n160.00 DROP_REQUEST n=1 target={WA} reason=2'
    elif mutation == 'prior_ie':
        actions += '\n160.00 IE_SET_ACK'
    elif mutation in ['young', 'old']:
        actions = actions.replace('278.00 DROP_REQUEST',
                                  ('270.00' if mutation == 'young' else '290.00') + ' DROP_REQUEST')
    elif mutation == 'short_hold':
        actions = actions.replace('371.00 STABLE_DONE epoch=2', '350.00 STABLE_DONE epoch=2')
    elif mutation == 'wrong_reset':
        resets.add('1')
    elif mutation == 'full_marker':
        actions += '\n371.01 COMPLETE'
    elif mutation == 'missing_pair':
        epochs['2']['XC']['paired'] = 31
    elif mutation == 'missing_epoch':
        del epochs['1']
    elif mutation == 'extra_epoch':
        epochs['3'] = copy.deepcopy(epochs['2'])
    with pytest.raises(RuntimeError):
        ns['validate_no_WA_diagnostic'](actions, resets, epochs)


def quiet_evidence():
    actions, resets, epochs = evidence()
    actions = actions.replace(f'280.00 PULSE 2 phase=RECOVER target={XC} seconds=60',
                              f'280.00 XC_RECOVERY_IE_SUPPRESSED n=2 target={XC}')
    return actions, resets, epochs


def test_quiet_diagnostic_requires_suppression_and_never_qualifies_full_trial():
    ns = functions()
    result = ns['validate_no_WA_diagnostic'](*quiet_evidence(), quiet=True)
    assert result['quiet_recovery_ie'] is True
    assert result['full_PREPROD1_PASS'] is False


@pytest.mark.parametrize('mutation', ['missing_marker', 'wrong_target', 'pulse', 'set_ie'])
def test_quiet_diagnostic_rejects_missing_guard_marker_or_any_recovery_exposure(mutation):
    ns = functions()
    actions, resets, epochs = quiet_evidence()
    if mutation == 'missing_marker':
        actions = actions.replace(f'280.00 XC_RECOVERY_IE_SUPPRESSED n=2 target={XC}', '')
    elif mutation == 'wrong_target':
        actions = actions.replace('XC_RECOVERY_IE_SUPPRESSED n=2 target='+XC,
                                  'XC_RECOVERY_IE_SUPPRESSED n=2 target='+WA)
    elif mutation == 'pulse':
        actions += '\n281.00 PULSE 2 phase=RECOVER'
    else:
        actions += '\n281.00 IE_SET_ACK'
    with pytest.raises(RuntimeError):
        ns['validate_no_WA_diagnostic'](actions, resets, epochs, quiet=True)


@pytest.mark.parametrize('mode,epoch,drop,expected_epoch,expected_drop,tag', [
    ('diagnostic_no_WA', 0, 0, 1, 0, 'STABLE_START epoch=1'),
    ('diagnostic_no_WA', 1, 0, 1, 2, f'DROP_REQUEST n=2 target={XC}'),
    ('diagnostic_no_WA', 2, 2, 2, 2, 'DIAGNOSTIC_ONLY_COMPLETE'),
    ('diagnostic_no_WA_quiet_XC', 1, 0, 1, 2, f'DROP_REQUEST n=2 target={XC}'),
    ('diagnostic_no_WA_quiet_XC', 2, 2, 2, 2, 'DIAGNOSTIC_ONLY_COMPLETE'),
    ('qualify', 0, 0, 0, 1, f'DROP_REQUEST n=1 target={WA}'),
    ('qualify', 4, 4, 4, 4, 'COMPLETE'),
])
def test_actual_native_stable_transitions_keep_qualifier_order_and_separate_diagnostic(
        tmp_path, mode, epoch, drop, expected_epoch, expected_drop, tag):
    native = NATIVE.read_text(encoding='utf8')
    block = re.split(r'(?m)^\s*STABLE\)\n', native, maxsplit=1)[1]
    block = re.split(r'(?m)^\s*COMPLETE\)', block, maxsplit=1)[0]
    git_bash = Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Git/bin/bash.exe'
    bash = str(git_bash) if git_bash.is_file() else shutil.which('bash')
    if not bash:
        pytest.skip('POSIX fixture shell unavailable')
    body = f'''set -eu
D={shlex.quote(tmp_path.as_posix())}
mode={mode}; epoch={epoch}; drop_n={drop}; phase=STABLE; stable_end=0; t=500
WA={WA}; XC={XC}; rows=synthetic; OBJ=hostapd.phy0-ap0
all_good() {{ return 0; }}
good() {{ return 0; }}
now() {{ echo 500; }}
log() {{ echo "$*"; }}
jsonfilter() {{ echo 4; }}
iw() {{ printf 'Station %s (on %s)' "$5" "$2"; }}
cat() {{ echo 21; }}
ubus() {{ :; }}
collect() {{ :; }}
protect_peers() {{ :; }}
for step in 1; do
case STABLE in
STABLE)
{block}
esac
done
printf 'FINAL epoch=%s drop=%s\\n' "$epoch" "$drop_n"
'''
    result = subprocess.run([bash, '-s'], input=body.encode(), stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=10)
    assert result.returncode == 0, result.stderr.decode(errors='replace')
    output = result.stdout.decode()
    assert tag in output
    assert f'FINAL epoch={expected_epoch} drop={expected_drop}' in output
    if mode.startswith('diagnostic_no_WA'):
        assert not re.search(r'(?m)^COMPLETE$', output)


@pytest.mark.parametrize('ie_on,expected_code', [(0, 0), (1, 89)])
def test_actual_quiet_native_branch_suppresses_once_and_fails_if_ie_already_on(ie_on, expected_code):
    source = NATIVE.read_text(encoding='utf8')
    start = source.index('pulse_missing() {')
    block = source[start:source.index('\n}\n', start)+3]
    git_bash = Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Git/bin/bash.exe'
    bash = str(git_bash) if git_bash.is_file() else shutil.which('bash')
    if not bash:
        pytest.skip('POSIX fixture shell unavailable')
    body = f'''set -eu
mode=diagnostic_no_WA_quiet_XC; phase=RECOVER; target={XC}; XC={XC}
ie_on={ie_on}; xc_quiet_logged=0; drop_n=2
log() {{ echo "$*"; }}
set_ie() {{ echo FORBIDDEN_IE_SET; exit 97; }}
{block}
pulse_missing
pulse_missing
'''
    result = subprocess.run([bash, '-s'], input=body.encode(), stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=10)
    assert result.returncode == expected_code
    output = result.stdout.decode()
    assert 'FORBIDDEN_IE_SET' not in output
    assert output.count('XC_RECOVERY_IE_SUPPRESSED') == (1 if ie_on == 0 else 0)


def test_diagnostic_cannot_set_full_pass_or_use_extended_native_deadlines():
    tree = ast.parse(SOURCE.read_text(encoding='utf8'))
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    passed = next(n for n in ast.walk(main) if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == 'passed' for t in n.targets))
    assert 'not diagnostic' in ast.unparse(passed.value)
    source = NATIVE.read_text(encoding='utf8')
    assert 'end=$((start+780))' in source
    assert 'phase_end=$((start+120))' in source
    assert 'phase=RECOVER; phase_end=$(($(now)+60))' in source
