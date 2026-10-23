"""Stock global selection mode stays outside the zero-command window."""
import ast
from pathlib import Path

import pytest


SOURCE = Path(__file__).resolve().parents[1] / 'artifacts/canary_panel1_guarida/preprod1_trial_20261022.py'


def functions(replies):
    tree = ast.parse(SOURCE.read_text(encoding='utf8'))
    names = {'prepare_xc_ap_scan_mode', 'verify_xc_ap_scan_mode_restore'}
    calls = []

    def require(ok, reason):
        if not ok:
            raise RuntimeError(reason)

    def remote(_client, command, **_kwargs):
        calls.append(command)
        return dict(stdout=replies.pop(0), stderr='', exit_code=0)

    namespace = dict(require=require, remote=remote)
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), 'exec'), namespace)
    return namespace, calls


def test_mode2_requires_original_scan0_and_both_acks_with_checkpoint_before_set():
    ns, calls = functions(['0', 'OK', 'OK'])
    record, saved = {}, []
    ns['prepare_xc_ap_scan_mode'](object(), record,
        lambda: saved.append((len(calls), record['XC_ap_scan_policy'].copy())))
    assert saved[0][0] == 1
    assert saved[0][1]['applied'] is False
    assert record['XC_ap_scan_policy']['applied'] is True
    assert calls == ['wpa_cli -i ath0 get_network 0 scan_ssid',
                     'wpa_cli -i ath0 ap_scan 1', 'wpa_cli -i ath0 ap_scan 2']


@pytest.mark.parametrize('replies', [['1'], ['FAIL'], ['0', 'FAIL'],
                                     ['0', 'OK', 'FAIL'], ['0', 'OK', 'OK\nOK']])
def test_missing_baseline_or_treatment_ack_never_accepts_mode2(replies):
    ns, calls = functions(replies)
    record = {}
    with pytest.raises(RuntimeError):
        ns['prepare_xc_ap_scan_mode'](object(), record, lambda: None)
    assert not record.get('XC_ap_scan_policy', {}).get('applied')


def test_mode_cannot_change_after_window_start():
    ns, calls = functions([])
    with pytest.raises(RuntimeError, match='XC_AP_SCAN_AFTER_WINDOW_START'):
        ns['prepare_xc_ap_scan_mode'](object(), {'control_window_start': {}}, lambda: None)
    assert calls == []


def test_original_mode1_baseline_does_not_apply_rejected_mode2():
    ns, calls = functions(['0', 'OK'])
    record = {}
    ns['prepare_xc_ap_scan_mode'](object(), record, lambda: None, requested=1)
    assert record['XC_ap_scan_policy']['baseline_only'] is True
    assert record['XC_ap_scan_policy']['applied'] is False
    assert calls == ['wpa_cli -i ath0 get_network 0 scan_ssid', 'wpa_cli -i ath0 ap_scan 1']


@pytest.mark.parametrize('replies,accepted', [(['OK', '0'], True), (['FAIL'], False),
                                            (['OK', '1'], False), (['OK', 'FAIL'], False)])
def test_restore_requires_mode1_ack_and_actual_scan0_without_invented_mode_getter(replies, accepted):
    ns, calls = functions(replies)
    record = dict(XC_ap_scan_policy=dict(original=1, requested=2), control_window_end={})
    if accepted:
        ns['verify_xc_ap_scan_mode_restore'](object(), record)
    else:
        with pytest.raises(RuntimeError):
            ns['verify_xc_ap_scan_mode_restore'](object(), record)
    assert bool(record['XC_ap_scan_policy'].get('restored')) is accepted
    assert calls[0] == 'wpa_cli -i ath0 ap_scan 1'
    assert not any('get ap_scan' in c for c in calls)


def test_restore_refuses_any_command_with_window_open():
    ns, calls = functions([])
    with pytest.raises(RuntimeError, match='XC_AP_SCAN_RESTORE_WITH_WINDOW_OPEN'):
        ns['verify_xc_ap_scan_mode_restore'](object(), dict(XC_ap_scan_policy={}))
    assert calls == []


def test_active_setter_follows_fresh_secure_bss_and_ie_clear_before_enable_and_window():
    tree = ast.parse(SOURCE.read_text(encoding='utf8'))
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    calls = [n for n in ast.walk(main) if isinstance(n, ast.Call)]
    policy = next(n.lineno for n in calls if isinstance(n.func, ast.Name) and n.func.id == 'prepare_xc_ap_scan_mode')
    secure = next(n.lineno for n in calls if ast.unparse(n) == 'mode(True)')
    clear = next(n.lineno for n in ast.walk(main) if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Subscript) and isinstance(t.slice, ast.Constant)
                         and t.slice.value == 'AP_discovery_clear_before_XC_enable' for t in n.targets))
    enabled = next(n.lineno for n in calls if any(isinstance(a, ast.Constant)
                   and a.value == 'wpa_cli -i ath0 enable_network 0' for a in n.args))
    window = next(n.lineno for n in ast.walk(main) if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == 'control_window' for t in n.targets)
                  and isinstance(n.value, ast.Constant) and n.value.value is True)
    assert secure < clear < policy < enabled < window
    restore = next(n.lineno for n in calls if isinstance(n.func, ast.Name) and n.func.id == 'verify_xc_ap_scan_mode_restore')
    guard_ok = next(n.lineno for n in calls if any(isinstance(a, ast.Constant)
                    and a.value == 'ROCKET_GUARD_RESTORE_FAILED' for a in n.args))
    assert guard_ok < restore
