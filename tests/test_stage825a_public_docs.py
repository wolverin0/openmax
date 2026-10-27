"""Public milestone claims, privacy guards and preserved setup qualifications."""
from pathlib import Path
import re

import pytest

from tools.observability import build_stage825a_public_milestones_through_824a as public


@pytest.mark.parametrize('label', public.PAGES)
def test_owned_public_pages_have_qualified_milestones(label):
    text = (public.ROOT / label).read_text(encoding='utf-8')
    assert public.audit_page(text, label) == []
    assert 'reported 78.51 Mbps' in text
    assert 'imported claims, not remeasured here' in text
    assert 'runtime compatibility remains UNKNOWN' in text
    assert 'stubs; zero-rogue-DHCP runtime UNKNOWN' in text
    assert 'Stage819A is an uncalibrated' in text


def page():
    return (public.ROOT / 'README.md').read_text(encoding='utf-8')


@pytest.mark.parametrize('addition,expected', [
    ('\nCustomer address: 198.51.100.7\n', 'private/nondefault address'),
    ('\nCustomer MAC: 00:11:22:33:44:55\n', 'MAC address'),
    ('\nCustomer: SampleSubscriber\n', 'customer identity'),
    ('\n[report](https://hackerone.com/reports/123)\n', 'disclosure destination'),
    ('\n[private rules](../AGENTS.md)\n', 'private operational/archive destination'),
    ('\n[raw archive](../artifacts/documentation/private.txt)\n', 'private operational/archive destination'),
    ('\n' + 'password' + '=' + 'sample_fixture_value' + '\n', 'possible embedded credential'),
    ('\nuniversal compatibility confirmed\n', 'unsupported universal compatibility'),
])
def test_privacy_and_claim_regressions_are_rejected(addition, expected):
    hashes = {public.fingerprint('SampleSubscriber')} if expected == 'customer identity' else set()
    assert any(expected in value for value in public.audit_page(page() + addition, 'fixture', hashes))


def test_runtime_and_model_qualifications_are_required():
    text = page().replace('UNKNOWN', 'ACCEPTED').replace('not measured', 'measured')
    failures = public.audit_page(text, 'fixture')
    assert 'missing milestone token: UNKNOWN' in failures
    assert 'Guarida v9/v10 evidence separation missing' in failures


def test_generic_factory_setup_is_not_customer_topology():
    failures = public.audit_page(page() + '\nFactory default:192.168.1.20/24; isolated tester PC192.168.1.10/24.\n', 'fixture')
    assert not any('address must' in item for item in failures)


def test_guides_preserve_legacy_recovery_and_source_limits():
    for label in public.PAGES[-2:]:
        text = (public.ROOT / label).read_text(encoding='utf-8')
        assert '815640' in text or 'kernel/DTB' in text
        assert 'SHA256SUMS' in text and 'WDS' in text
        assert '999' in text and 'samples=1' in text
        assert 'TFTP' in text and 'sysupgrade' in text
        assert 'watchdog' in text and 'Wi-Fi' in text


def test_current_state_keeps_all_original_continuation_routes():
    text = (public.ROOT / 'docs/CURRENT_STATE.md').read_text(encoding='utf-8')
    targets = re.findall(r'\]\((CURRENT_STATE_CONTINUATION_[^)]+)\)', text)
    assert len(targets) >= 20
    assert any(target.endswith('_001.md') for target in targets)
    assert any(target.endswith('_002.md') for target in targets)
    assert 'stage779a_784a_817a_822a_validation.json' in text
    assert 'stage792a_codex_787a_to_792a_gate_receipt.json' in text


def test_optional_local_identity_policy_is_hashed_and_case_normalized(tmp_path):
    policy = tmp_path / '.git/stage826a/private_terms.json'
    policy.parent.mkdir(parents=True)
    policy.write_text('["Example Subscriber"]')
    hashes = public.local_identity_hashes(tmp_path)
    assert hashes == {public.fingerprint('example subscriber')}
    assert public.has_private_identity('customer EXAMPLE Subscriber', hashes)
    assert not public.has_private_identity('customer different subscriber', hashes)
    assert public.local_identity_hashes(tmp_path / 'absent') == set()
