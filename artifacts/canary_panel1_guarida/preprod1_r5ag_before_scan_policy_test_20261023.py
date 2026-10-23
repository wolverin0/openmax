"""Pre-window scan policy is acknowledged, observed and restored independently."""
import ast
from pathlib import Path

import pytest


SOURCE = Path(__file__).resolve().parents[1] / 'artifacts/canary_panel1_guarida/preprod1_trial_20261022.py'


def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def functions(replies):
    tree = ast.parse(SOURCE.read_text(encoding='utf8'))
    names = {'prepare_xc_directed_scan', 'verify_xc_scan_policy_restore'}
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    calls = []

    def remote(_client, command, **_kwargs):
        calls.append(command)
        return dict(stdout=replies.pop(0), stderr='', exit_code=0)

    namespace = dict(require=require, remote=remote)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), 'exec'), namespace)
    return namespace, calls


def test_directed_scan_is_observed_before_use_and_original_saved_before_mutation():
    namespace, calls = functions(['0', 'OK\n', '1'])
    record = {}
    checkpoints = []
    namespace['prepare_xc_directed_scan'](object(), record,
        lambda: checkpoints.append((len(calls), record['XC_scan_policy'].copy())))
    assert record['XC_scan_policy']['applied']
    assert record['XC_scan_policy']['before'] == 0
    assert checkpoints[0] == (1, dict(before=0, requested=1, applied=False, scope='pre-window RAM only'))
    assert calls.count('wpa_cli -i ath0 set_network 0 scan_ssid 1') == 1
    assert all('enable' not in c and 'save_config' not in c for c in calls)


@pytest.mark.parametrize('replies', [['1'], ['FAIL\n'], ['0', 'FAIL\n'], ['0', 'OK\n', '0'],
                                     ['0', 'OK\n', '1\n1\n']])
def test_unconfirmed_original_setter_or_readback_never_marks_policy_applied(replies):
    namespace, calls = functions(replies)
    record = {}
    with pytest.raises(RuntimeError):
        namespace['prepare_xc_directed_scan'](object(), record, lambda: None)
    assert not record.get('XC_scan_policy', {}).get('applied')


def test_policy_cannot_be_applied_after_window_start():
    namespace, calls = functions([])
    with pytest.raises(RuntimeError, match='XC_SCAN_POLICY_AFTER_WINDOW_START'):
        namespace['prepare_xc_directed_scan'](object(), {'control_window_start': {}}, lambda: None)
    assert calls == []


@pytest.mark.parametrize('observed,accepted', [('0', True), ('1', False), ('FAIL\n', False)])
def test_restoration_requires_actual_original_policy_readback(observed, accepted):
    namespace, calls = functions([observed])
    record = dict(XC_scan_policy=dict(before=0, requested=1, applied=True), control_window_end={})
    if accepted:
        namespace['verify_xc_scan_policy_restore'](object(), record)
    else:
        with pytest.raises(RuntimeError, match='XC_SCAN_POLICY_NOT_RESTORED'):
            namespace['verify_xc_scan_policy_restore'](object(), record)
    assert record['XC_scan_policy']['restored'] is accepted
    assert calls == ['wpa_cli -i ath0 get_network 0 scan_ssid']


def test_actual_preparation_stays_after_secure_ap_and_before_scan_and_window():
    tree = ast.parse(SOURCE.read_text(encoding='utf8'))
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    calls = list(n for n in ast.walk(main) if isinstance(n, ast.Call))
    policy = next(n.lineno for n in calls if isinstance(n.func, ast.Name) and n.func.id == 'prepare_xc_directed_scan')
    secure = next(n.lineno for n in calls if ast.unparse(n) == 'mode(True)')
    flush = next(n.lineno for n in calls if any(isinstance(a, ast.Constant) and a.value == 'wpa_cli -i ath0 bss_flush 0' for a in n.args))
    window = next(n.lineno for n in ast.walk(main) if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == 'control_window' for t in n.targets)
                  and isinstance(n.value, ast.Constant) and n.value.value is True)
    assert secure < policy < flush < window
