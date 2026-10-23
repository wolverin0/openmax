"""Reviewed source/binary bindings and per-trace daemon identity must stay strict."""
import ast
import importlib.util
import re
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'artifacts/canary_panel1_guarida'
COMPAT_SHA = '99122e15246efc0006c82fc23a8667f7ccdcdf9d15bd2f46edc7e95c0f7b6923'
STOCK_SHA = 'f48e4ffa30b382b1526c7d8b32889b19dbc498a362443f41142646db60fb3a12'
BINARY_FILE = 'preprod_guarida_20261022/history/preprod1_r5ak_AP_compat/wpad.compat'


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
             'tools/bench/build_preprod1_xc_ssid.py',
             'tests/test_preprod1_xc_ssid_compat.py',
             'tests/test_preprod1_AP_compat.py',
             'tests/test_preprod1_AP_compat_integration.py']
    return {'AP_mgmt': True, 'AP_XC_SSID_compat': {
        'enabled': True, 'binary_sha256': COMPAT_SHA, 'binary_file': BINARY_FILE},
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
    ({'binary_file': '../outside/wpad'}, 'AP_COMPAT_BINARY_PRIVATE_SCOPE'),
    ({'binary_sha256': STOCK_SHA}, 'AP_COMPAT_BINARY_PLAN_MISMATCH'),
    ({'binary_sha256': 'not-a-digest'}, 'AP_COMPAT_BINARY_PLAN_MISMATCH'),
])
def test_compat_plan_rejects_unbound_or_out_of_scope_inputs(change, reason):
    value = plan()
    value['AP_XC_SSID_compat'].update(change)
    with pytest.raises(RuntimeError, match=reason):
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
