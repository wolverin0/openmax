"""Native tc-optional transactions in disposable command-stub fixtures only."""
import json
from pathlib import Path

import pytest

from tests.test_chatgpt_audit_wa_kit import fixture, device_view, HELPER

ROOT = Path(__file__).resolve().parents[1]
KITS = [HELPER, ROOT/'firmware/openwrt/common/fmx_wa_v14_356window_field_kit.sh',
        ROOT/'firmware/openwrt/common/fmx_wa_v15_368window_field_kit.sh']


@pytest.mark.parametrize('helper', KITS)
@pytest.mark.parametrize('tc_present', [True, False])
def test_all_profiles_apply_verify_rollback_on_both_backends(fixture, helper, tc_present):
    state=json.loads(fixture['device'].read_text())
    state['attrs']['/sys/class/net/eth0/tx_queue_len']='42'
    fixture['device'].write_text(json.dumps(state))
    result=fixture['run'](helper=helper,tc_present=tc_present)
    assert result.returncode==0,(result.stdout,result.stderr)
    current=json.loads(fixture['device'].read_text())
    assert current['attrs']['/sys/class/net/eth0/tx_queue_len']=='1000'
    expected=('1500','3000') if 'v15_' in helper.name else ('2000','4000')
    assert all(tuple(line.split()[1:])==expected for line in
               current['attrs']['/sys/kernel/debug/ieee80211/phy1/aql_txq_limit'].splitlines())
    checked=fixture['run']('--verify',helper=helper,tc_present=tc_present)
    assert checked.returncode==0,(checked.stdout,checked.stderr)
    assert json.loads(fixture['device'].read_text())['mutations']==current['mutations']
    restored=fixture['run']('--rollback',helper=helper,tc_present=tc_present)
    assert restored.returncode==0,(restored.stdout,restored.stderr)
    assert device_view(json.loads(fixture['device'].read_text()))==device_view(state)


def test_native_aql_labels_are_normalized_and_restored(fixture):
    state=json.loads(fixture['device'].read_text())
    label='/sys/kernel/debug/ieee80211/phy1/aql_txq_limit'
    state['attrs'][label]='AC low high\nVO 1000 3000\nVI 1001 3001\nBE 1002 3002\nBK 1003 3003'
    fixture['device'].write_text(json.dumps(state))
    result=fixture['run'](tc_present=False)
    assert result.returncode==0,(result.stdout,result.stderr)
    restored=fixture['run']('--rollback',tc_present=False)
    assert restored.returncode==0,(restored.stdout,restored.stderr)
    assert device_view(json.loads(fixture['device'].read_text()))==device_view(state)


@pytest.mark.parametrize('rows', [
    'AC low high\nVO 1000 3000\nVI 1001 3001\nVO 1002 3002\nBK 1003 3003',
    'AC low high\nVO 1000 3000\nVI 1001 3001\nBE 1002 3002',
    'AC low high\nVO 1000 3000\nVI 1001 3001\nBE 1002 3002\nBK 5000 3003'])
def test_invalid_native_aql_rows_rejected_before_writes(fixture, rows):
    state=json.loads(fixture['device'].read_text())
    state['attrs']['/sys/kernel/debug/ieee80211/phy1/aql_txq_limit']=rows
    fixture['device'].write_text(json.dumps(state))
    result=fixture['run'](tc_present=False)
    assert result.returncode!=0 and 'APPLIED_VERIFIED' not in result.stdout
    assert json.loads(fixture['device'].read_text())['mutations']==0


def test_tcless_verify_detects_real_tx_queue_len_drift(fixture):
    applied=fixture['run'](tc_present=False)
    assert applied.returncode==0,(applied.stdout,applied.stderr)
    state=json.loads(fixture['device'].read_text())
    state['attrs']['/sys/class/net/eth0/tx_queue_len']='42'
    fixture['device'].write_text(json.dumps(state))
    result=fixture['run']('--verify',tc_present=False)
    assert result.returncode!=0 and 'APPLIED_VERIFIED' not in result.stdout
    assert json.loads(fixture['device'].read_text())['mutations']==state['mutations']


def test_backend_cannot_be_silently_switched(fixture):
    applied=fixture['run'](qdisc_mode='sysfs-default')
    assert applied.returncode==0,(applied.stdout,applied.stderr)
    state=json.loads(fixture['device'].read_text())
    result=fixture['run']('--verify',qdisc_mode='tc')
    assert result.returncode!=0 and 'backend mismatch' in result.stderr
    assert json.loads(fixture['device'].read_text())['mutations']==state['mutations']


def test_tc_command_failure_does_not_fall_back_to_sysfs(fixture):
    result=fixture['run'](snapshot_error=1)
    assert result.returncode!=0 and 'APPLIED_VERIFIED' not in result.stdout
    assert json.loads(fixture['device'].read_text())['mutations']==0


@pytest.mark.parametrize('ordinal', range(1, 11))
def test_tcless_each_write_failure_restores_actual_snapshot(fixture, ordinal):
    failed=fixture['run'](tc_present=False,fail_mutation=ordinal)
    assert failed.returncode!=0 and 'FAILED_ROLLED_BACK' in failed.stdout,(failed.stdout,failed.stderr)
    assert device_view(json.loads(fixture['device'].read_text()))==device_view(fixture['original'])


def test_explicit_tc_requires_binary_even_if_default_is_fq_codel(fixture):
    result=fixture['run'](qdisc_mode='tc',tc_present=False)
    assert result.returncode!=0 and 'tc backend unavailable' in result.stderr
    assert json.loads(fixture['device'].read_text())['mutations']==0


def test_preexisting_phase_hardlink_cannot_overwrite_other_file(fixture):
    assert fixture['run'](tc_present=False).returncode==0
    victim=fixture['tmp']/'victim.txt'
    victim.write_text('UNCHANGED\n')
    (fixture['snapshot']/'phase.tmp').hardlink_to(victim)
    result=fixture['run']('--rollback',tc_present=False)
    assert result.returncode!=0 and 'FAILED_PRECONDITION' in result.stderr
    assert victim.read_text()=='UNCHANGED\n'


@pytest.mark.parametrize('setting', [{'state_owner':'1001'}, {'state_mode':'777'}])
def test_untrusted_state_metadata_is_rejected(fixture, setting):
    assert fixture['run'](tc_present=False).returncode==0
    result=fixture['run']('--verify',tc_present=False,**setting)
    assert result.returncode!=0 and 'FAILED_PRECONDITION' in result.stderr
