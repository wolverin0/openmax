"""Saved packages cannot silently become a fitted law or a traffic classifier."""
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path

import pytest

from orchestration.autoresearch.fmx_offline_data import recorded_uplink_package
from orchestration.autoresearch.fmx_multi_regime_dyadic_selector import (
    EvidenceViewPaths, audit_recorded_uplink_laws, load_operator_evidence,
)

ROOT = Path(__file__).resolve().parents[1]
SAVED = ROOT / 'artifacts/autoresearch/waves_bq_to_cf_20261024'


@pytest.fixture(scope='module')
def source_rows():
    return json.loads((SAVED / 'normalized_r1_to_r134_measurements_20261024.json').read_text())['records']


def target(rows, number):
    return deepcopy([r for r in rows if r['round_id'] == f'R{number}'][1])


@pytest.mark.parametrize('number,meters,low', [(116,1000,2650),(117,3000,3150),
    (118,6000,3550),(119,9000,3800),(120,12000,3950),(121,14000,4100)])
def test_ul2_preserves_observed_knots_without_fitting(source_rows,number,meters,low):
    result = recorded_uplink_package(target(source_rows, number))
    assert result['distance_meters'] == meters
    assert result['cpe_be_us'] == [low, 2*low]
    assert result['cpe_tcp_limit_output_bytes'] == 1048576
    assert result['logarithmic_formula'] is None
    assert result['interpolation_allowed'] is False
    assert result['physical_acceptance'] is False


@pytest.mark.parametrize('number,rts,clock', [(122,'256',True),(123,'256',True),
    (127,'256',True),(128,'off',True),(129,'off',False),(133,'off',False),(134,'off',False)])
def test_ul8_retains_rts_and_ack_clocking_as_distinct_coordinates(source_rows,number,rts,clock):
    result = recorded_uplink_package(target(source_rows,number))
    assert result['rts_declared'] == rts
    assert result['ap_ack_clocking_declared'] is clock
    assert result['pure_ac_vo_max_packet_bytes'] is None
    assert result['pure_ac_vo_160_verified'] is False
    assert result['adaptive_rts_control_law_verified'] is False


def test_r134_body_value_wins_over_filename_and_other_1km_packages(source_rows):
    assert recorded_uplink_package(target(source_rows,134))['cpe_be_us'] == [3150,6300]
    assert recorded_uplink_package(target(source_rows,116))['cpe_be_us'] == [2650,5300]
    assert recorded_uplink_package(target(source_rows,128))['cpe_fq_target_us'] == 11000
    assert recorded_uplink_package(target(source_rows,134))['cpe_fq_target_us'] == 16000


@pytest.mark.parametrize('mutation', [
    lambda r:r.update(round_id='R110'),
    lambda r:r.update(active_flow_count=True),
    lambda r:r.update(distance_meters=True),
    lambda r:r.update(coverage_class=True),
    lambda r:r.update(distance_meters=3000),
    lambda r:r.update(certified_wds_evidence=None),
    lambda r:r['certified_wds_evidence'].update(new_source_control_provenance=None),
    lambda r:r.update(ap_policy=None),
    lambda r:r['ap_policy'].update(distance_meters=True),
    lambda r:r.update(workload_regime='unidir_ul_2flow'),
    lambda r:r['new_source_controls'].update(ap_ack_clocking='false'),
    lambda r:r['ap_policy'].update(rts_threshold=256),
    lambda r:r['certified_wds_evidence']['new_source_control_provenance']['controls'].update(rts_threshold='256'),
    lambda r:(r['new_source_controls'].update(rts_threshold=None),
              r['certified_wds_evidence']['new_source_control_provenance']['controls'].update(rts_threshold=None)),
])
def test_mismatched_or_untyped_package_fails_closed(source_rows,mutation):
    row=target(source_rows,134);mutation(row)
    with pytest.raises(ValueError):recorded_uplink_package(row)


def test_summary_does_not_mutate_source(source_rows):
    row=target(source_rows,134);before=deepcopy(row)
    result=recorded_uplink_package(row);result['cpe_be_us'][0]=1
    assert row == before


def test_real_bound_law_audit_keeps_unchanged_strict_rejections():
    review=json.loads((SAVED/'review_statistics.json').read_text())
    config=EvidenceViewPaths('BQCF134',SAVED/'normalized_r1_to_r134_measurements_20261024.json',
        SAVED/'normalized_r16_to_r134_block_observations_20261024.json',
        SAVED/'stats_crossover_analysis.json',SAVED/'inputs_manifest.json',
        SAVED/'stats_validation.json',review['accepted_receipt_sha256'])
    evidence=load_operator_evidence(current=config)
    result=audit_recorded_uplink_laws(evidence)
    assert result['status']=='AUDITED_RECORDED_PACKAGES'
    assert len(result['packages'])==19 and result['missing_rounds']==[]
    assert all(p['strict_evaluation']['status']=='BLOCKED' for p in result['packages'])
    assert result['ul2_observed_discrete_concavity'] is False
    assert [Fraction(v) for v in result['ul2_segment_slopes_us_per_km']] == [250,Fraction(400,3),Fraction(250,3),50,75]
    assert result['automatic_execution_allowed'] is result['physical_acceptance'] is False


def test_invalid_requested_scope_rejects_before_evidence_read():
    class NoRead:
        def parse(self):raise AssertionError('Invalid request must not read evidence')
    result=audit_recorded_uplink_laws(NoRead(),round_ids=['R135'])
    assert result['status']=='BLOCKED' and result['reason']=='UNSUPPORTED_UL_LAW_ROUND_SCOPE'
