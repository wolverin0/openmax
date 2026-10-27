"""Stage773A software packaging only; historical metrics are not runtime proof."""
from pathlib import Path
import pytest
from tools.firmware import build_stage773a_wa_champion_v13_344window_field_rollout_kit as builder


@pytest.fixture
def kit(tmp_path):
    helper=tmp_path/builder.HELPER_REL
    helper.parent.mkdir(parents=True)
    helper.write_bytes(builder.HELPER_PATH.read_bytes())
    return tmp_path,builder.build(tmp_path)


def test_stage773a_kit_and_receipt(kit):
    root,data=kit
    assert data['stage']=='773A' and data['status']=='CONFIRMED'
    assert data['execution_mode']=='OFFLINE_PACKAGING'
    assert data['runtime_acceptance']=='UNKNOWN'
    assert data['historical_reported_windows']==344
    assert data['historical_reported_metrics']['vht20_peak_tcp_mbps']==78.51
    assert data['dhcp_services_changed'] is False
    assert 'verified_metrics' not in data
    assert data['apply_contract']['default']=='PLANNED'


def test_stage773a_doc_limits(kit):
    root,_=kit
    text=(root/'docs'/f'{builder.STEM.upper()}.md').read_text(encoding='utf-8')
    assert len(text.splitlines())<180
    assert text.count('<!-- doc-head:')==1
    assert text.count('<!-- /doc-head -->')==1
    assert 'imported historical claims only' in text
