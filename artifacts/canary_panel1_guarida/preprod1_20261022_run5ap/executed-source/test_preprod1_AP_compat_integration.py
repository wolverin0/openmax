"""Reviewed source/binary bindings and per-trace daemon identity must stay strict."""
import ast
import importlib.util
import hashlib
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'artifacts/canary_panel1_guarida'
COMPAT_SHA = 'e86a3aafe2ac427e01ee402d1da0df5b7f37e1dbe113bd2d90109ff5ac72ea09'
STOCK_SHA = 'f48e4ffa30b382b1526c7d8b32889b19dbc498a362443f41142646db60fb3a12'
BINARY_FILE = 'preprod_guarida_20261022/history/preprod1_r5al_AP_compat/wpad.compat'


def require(value, reason):
    if not value:
        raise RuntimeError(reason)


def validator():
    path = HERE / 'preprod1_trial_20261022.py'
    tree = ast.parse(path.read_text())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                and n.name == 'validate_AP_compat_plan')
    scope = {'require': require, 're': re}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), scope)
    return scope['validate_AP_compat_plan']


def plan():
    prefix = 'artifacts/canary_panel1_guarida/'
    paths = [prefix + 'preprod1_AP_compat_20261023.py', prefix + BINARY_FILE,
             'tools/bench/hostapd_preprod1_xc_ssid.h',
             'tools/bench/hostapd_preprod1_xc_ssid.patch',
             'tools/bench/build_preprod1_xc_assocresp.py',
             'tools/bench/hostapd_preprod1_xc_assocresp.h',
             'tools/bench/hostapd_preprod1_xc_assocresp.patch',
             'tests/test_preprod1_xc_assocresp_compat.py',
             'tests/test_preprod1_xc_assocresp_integration.py',
             'tests/test_preprod1_xc_ssid_compat.py',
             'tests/test_preprod1_AP_compat.py',
             'tests/test_preprod1_AP_compat_integration.py']
    return {'AP_mgmt': True, 'AP_XC_SSID_compat': {
        'enabled': True, 'binary_sha256': COMPAT_SHA, 'binary_file': BINARY_FILE,
        'response_compat': 'XC_ASSOCRESP3'},
        'preconditions': {'AL_response_fields': {
            'file': 'preprod1_r5al_response_field_gate_independent_review_20261023.json',
            'sha256': 'ab17327cc465dc0e2f50b59f17f94cd38d1bbccaa1c0229faa46837541f3c598'}},
        'source_bindings': {path: COMPAT_SHA for path in paths}}


def test_original_stack_default_has_no_compat_requirement():
    assert validator()({}) is None


def test_explicit_compat_requires_every_support_and_binary_binding():
    original = plan()
    assert validator()(original) is original['AP_XC_SSID_compat']
    for path in original['source_bindings']:
        missing = plan()
        del missing['source_bindings'][path]
        with pytest.raises(RuntimeError, match='AP_COMPAT_SUPPORT_NOT_FROZEN'):
            validator()(missing)


@pytest.mark.parametrize('change, reason', [
    ({'enabled': False}, 'INVALID_EXPLICIT_AP_COMPAT_TREATMENT'),
    ({'response_compat': False}, 'AP_COMPAT_RESPONSE_PROFILE_REQUIRED'),
    ({'response_compat': 'SSID_ONLY'}, 'AP_COMPAT_RESPONSE_PROFILE_REQUIRED'),
    ({'binary_file': '../outside/wpad'}, 'AP_COMPAT_BINARY_PRIVATE_SCOPE'),
    ({'binary_sha256': STOCK_SHA}, 'AP_COMPAT_BINARY_PLAN_MISMATCH'),
    ({'binary_sha256': 'not-a-digest'}, 'AP_COMPAT_BINARY_PLAN_MISMATCH'),
])
def test_compat_plan_rejects_unbound_or_out_of_scope_inputs(change, reason):
    value = plan()
    value['AP_XC_SSID_compat'].update(change)
    with pytest.raises(RuntimeError, match=reason):
        validator()(value)


def test_response_field_review_cannot_be_omitted_or_substituted():
    for row in [None, {}, {'file': '../unreviewed', 'sha256': COMPAT_SHA}]:
        value = plan()
        value['preconditions']['AL_response_fields'] = row
        with pytest.raises(RuntimeError, match='AP_COMPAT_RESPONSE_FIELD_REVIEW_NOT_BOUND'):
            validator()(value)


def test_unapproved_binary_stays_rejected_even_if_its_binding_matches():
    value = plan()
    value['AP_XC_SSID_compat']['binary_sha256'] = STOCK_SHA
    value['source_bindings']['artifacts/canary_panel1_guarida/' + BINARY_FILE] = STOCK_SHA
    with pytest.raises(RuntimeError, match='AP_COMPAT_BINARY_PLAN_MISMATCH'):
        validator()(value)


@pytest.mark.parametrize('flags', [{'AP_mgmt': False}, {'AP_debug': True}])
def test_explicit_compat_requires_original_management_trace(flags):
    value = plan()
    value.update(flags)
    with pytest.raises(RuntimeError, match='AP_COMPAT_REQUIRES_BOUND_MGMT_TRACE'):
        validator()(value)


def trace_module(monkeypatch, tmp_path):
    monkeypatch.syspath_prepend(str(HERE))
    spec = importlib.util.spec_from_file_location('_compat_trace_test', HERE / 'preprod1_AP_mgmt_20261022.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, 'HERE', tmp_path)
    private = tmp_path / 'preprod_guarida_20261022/history'
    private.mkdir(parents=True)
    return module, private


def test_trace_binary_identity_override_is_private_and_default_stays_stock(monkeypatch, tmp_path):
    module, private = trace_module(monkeypatch, tmp_path)
    fake_helper = SimpleNamespace()  # No RPC exists: construction cannot touch a device.
    altered = module.APTrace(fake_helper, private / 'preprod1_compat_AP_mgmt',
                             expected_wpad_sha=COMPAT_SHA)
    original = module.APTrace(fake_helper, private / 'preprod1_original_AP_mgmt')
    assert altered.wpad_sha == COMPAT_SHA
    assert original.wpad_sha == STOCK_SHA
    assert altered.proxy.identity.__globals__['WPAD_SHA'] == COMPAT_SHA
    assert original.proxy.identity.__globals__['WPAD_SHA'] == STOCK_SHA
    assert altered.proxy.record['expected_wpad_sha256'] == COMPAT_SHA


@pytest.mark.parametrize('digest', ['', '0' * 63, 'X' * 64, False])
def test_trace_rejects_invalid_identity_before_creating_private_output(monkeypatch, tmp_path, digest):
    module, private = trace_module(monkeypatch, tmp_path)
    output = private / 'preprod1_invalid_AP_mgmt'
    with pytest.raises(RuntimeError, match='AP_MGMT_EXPECTED_WPAD_SHA'):
        module.APTrace(SimpleNamespace(), output, expected_wpad_sha=digest)
    assert not output.exists()


def lifecycle_fixture(monkeypatch, tmp_path, *, guard_restores=True, baseline_matches=True, close_fails=False):
    monkeypatch.syspath_prepend(str(HERE))
    source = HERE / 'preprod1_r5al_RAM_lifecycle_20261023.py'
    spec = importlib.util.spec_from_file_location('_rf_off_lifecycle_test', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.HERE = module.ROOT = tmp_path
    module.PLAN = tmp_path / 'plan.json'
    calls = []
    helper = SimpleNamespace(DIR='/tmp/fmx-owned-test',
                             guard_body=lambda: 'guard', restore_body=lambda: 'restore',
                             header=lambda: 'HEADER\n', file_guards=lambda: 'GUARDS\n',
                             off=lambda _ap: calls.append('off'),
                             arm=lambda _ap: pytest.fail('RF-off preflight must never arm the radio'))

    class Compat:
        cleanup_names = []
        record = {}

        def prepare_and_activate(self, _ap):
            calls.append('activate_under_existing_guard')
            self.record['status'] = 'COMPAT_ACTIVE_RADIO_OFF'

        def verify_restored(self, _ap):
            calls.append('verify_restored')
            return {'status': 'PASS_COMPAT_STOCK_RESTORED', 'stock': True, 'radio_off': True}

        def restore_if_needed(self, _ap):
            calls.append('failure_restore')
            return {'restored': True}

    compat = Compat()
    def close():
        calls.append('close')
        if close_fails:
            raise OSError('fixture close failed')

    ap = SimpleNamespace(close=close)
    baseline_calls = 0
    marker_calls = 0

    def remote(_ap, command, **_kwargs):
        nonlocal baseline_calls, marker_calls
        calls.append(command)
        output, code = '', 0
        if command.startswith('sha256sum /usr/sbin/wpad'):
            baseline_calls += 1
            output = 'original' if baseline_calls == 1 or baseline_matches else 'changed'
        elif command.startswith('test -f '):
            marker_calls += 1
            code = 0 if guard_restores and marker_calls > 1 else 1
        elif command.startswith('cat '):
            output = 'NATIVE_RESTORE_OK\n'
        elif command.startswith('set -eu\nHEADER\nGUARDS\n'):
            output = 'OWNED_RAM_REMOVED\n'
        else:
            pytest.fail('Unexpected lifecycle RPC: ' + command)
        return {'exit_code': code, 'stdout': output, 'stderr': ''}

    class Clock:
        value = 0

        def monotonic(self):
            return self.value

        def sleep(self, seconds):
            self.value += seconds

    module.time = Clock()
    monkeypatch.setattr(module, 'setup', lambda _plan: (helper, compat, remote))
    monkeypatch.setattr(module.access, 'load', lambda name: SimpleNamespace(ap_client=lambda: ap)
                        if name == 'root_goal_direct_link_connection_20261022.py'
                        else pytest.fail('Unexpected lifecycle module load'))
    value = {'frozen': True, 'production_access_permitted': False,
             'source_bindings': {}, 'preconditions': [], 'review_file': 'review.json',
             'rendered_guard_sha256': hashlib.sha256(b'guard').hexdigest(),
             'rendered_restore_sha256': hashlib.sha256(b'restore').hexdigest()}
    module.PLAN.write_text(json.dumps(value))
    plan_sha = hashlib.sha256(module.PLAN.read_bytes()).hexdigest()
    (tmp_path / 'review.json').write_text(json.dumps({
        'status': 'PASS_FIXTURE', 'plan_sha256': plan_sha, 'source_bindings': {}}))
    monkeypatch.setattr(sys, 'argv', ['lifecycle', '--execute', plan_sha])
    return module, calls


def test_rf_off_lifecycle_waits_for_native_guard_then_verifies_before_cleanup(monkeypatch, tmp_path):
    module, calls = lifecycle_fixture(monkeypatch, tmp_path)
    assert module.main() == 0
    record = json.loads((tmp_path / 'preprod1_r5al_RAM_lifecycle_20261023/receipt.json').read_text())
    assert record['status'] == 'PASS_RF_OFF_RAM_WPAD_NATIVE_GUARD_RESTORED'
    assert record['native_guard_restore_observed'] is True
    assert 'failure_restore' not in calls
    cleanup = next(c for c in calls if isinstance(c, str) and 'OWNED_RAM_REMOVED' in c)
    assert calls.index('verify_restored') < calls.index(cleanup)


@pytest.mark.parametrize('options', [{'guard_restores': False}, {'baseline_matches': False}])
def test_rf_off_failure_remains_unaccepted_and_restores_without_deleting_evidence(monkeypatch, tmp_path, options):
    module, calls = lifecycle_fixture(monkeypatch, tmp_path, **options)
    assert module.main() == 1
    record = json.loads((tmp_path / 'preprod1_r5al_RAM_lifecycle_20261023/receipt.json').read_text())
    assert record['status'] == 'NOT_ACCEPTED_RF_OFF_LIFECYCLE'
    assert 'failure_restore' in calls
    assert not any(isinstance(c, str) and 'OWNED_RAM_REMOVED' in c for c in calls)


def test_close_failure_keeps_final_receipt_and_nonzero_result(monkeypatch, tmp_path):
    module, _calls = lifecycle_fixture(monkeypatch, tmp_path, close_fails=True)
    assert module.main() == 1
    record = json.loads((tmp_path / 'preprod1_r5al_RAM_lifecycle_20261023/receipt.json').read_text())
    assert record['status'] == 'NOT_ACCEPTED_RF_OFF_LIFECYCLE'
    assert record['ended_utc']
    assert record['cleanup_errors'] == ['AP_close: fixture close failed']


@pytest.mark.parametrize('armed, status, owned, expected', [
    (False, 'PASS_NO_COMPAT_REMOTE_RESOURCES_CREATED', False, ['partial']),
    (False, 'PASS_COMPAT_STOCK_RESTORED', True, ['partial']),
    (True, 'PASS_COMPAT_STOCK_RESTORED', True, ['restore', 'verify']),
])
def test_partial_creation_uses_ownership_probe_before_any_cleanup(armed, status, owned, expected):
    path = HERE / 'preprod1_trial_20261022.py'
    node = next(n for n in ast.parse(path.read_text()).body
                if isinstance(n, ast.FunctionDef) and n.name == 'restore_AP_resources')
    scope = {'require': require}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), scope)
    calls = []
    def result(name):
        calls.append(name)
        return {'status': status, 'guard_ended_verified': owned}
    helper = SimpleNamespace(restore=lambda ap: result('restore'))
    compat = SimpleNamespace(restore_if_needed=lambda ap: result('partial'),
                             verify_restored=lambda ap: result('verify'))
    restored, checked, present = scope['restore_AP_resources'](helper, compat, object(), armed)
    assert calls == expected
    assert present is owned
    assert checked['status'] == status
    assert restored['guard_ended_verified'] is owned


def test_partial_restore_hold_cannot_reach_ram_cleanup():
    path = HERE / 'preprod1_trial_20261022.py'
    node = next(n for n in ast.parse(path.read_text()).body
                if isinstance(n, ast.FunctionDef) and n.name == 'restore_AP_resources')
    scope = {'require': require}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), scope)
    helper = SimpleNamespace(restore=lambda ap: pytest.fail('Unverified partial guard'))
    compat = SimpleNamespace(restore_if_needed=lambda ap: {'status': 'HOLD_OWNED_RAM'})
    with pytest.raises(RuntimeError, match='AP_COMPAT_PARTIAL_RESTORE_HOLD'):
        scope['restore_AP_resources'](helper, compat, object(), False)
