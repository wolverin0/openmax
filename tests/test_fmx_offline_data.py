"""Frozen R1-R9 normalization contracts, including unsafe and lossy source cases."""
from dataclasses import replace
from hashlib import sha256
import json

import pytest

from orchestration.autoresearch.fmx_offline_data import (
    AC_ORDER, ALL_ROUND_RECEIPTS, EFGH_INPUTS, ROOT, EndpointPolicy,
    load_all_measurements, load_measurements, local_json, normalized_regime_dataset, write_json,
)


def receipt_fixture(tmp_path,round_number=9):
    raw=local_json(ALL_ROUND_RECEIPTS[round_number-1])
    raw['iterations']=raw['iterations'][:1]
    path=tmp_path/'round.json'
    return raw,path


def parse_fixture(raw,path):
    path.write_text(json.dumps(raw),encoding='utf-8')
    return load_all_measurements([path])


def test_complete_frozen_corpus_counts_and_round_identity():
    records,refs=load_all_measurements()
    assert len(records)==58 and len(refs)==9
    assert [sum(r.round_id==f'R{i}' for r in records) for i in range(1,10)]==[8,5,7,7,6,7,6,6,6]
    assert len(load_measurements()[0])==13  # existing A-D API remains stable
    reverse,_=load_all_measurements(reversed(ALL_ROUND_RECEIPTS))
    assert reverse==records
    for ref,path in zip(refs,ALL_ROUND_RECEIPTS):
        assert ref['sha256']==sha256(path.read_bytes()).hexdigest()


def test_endpoints_regimes_and_raw_repetitions_are_not_invented():
    rows,_=load_all_measurements()
    assert [sum(r.workload_regime==name for r in rows) for name in
            ('bulk_unidirectional','bidir_2flow','bidir_6flow')]==[27,13,18]
    assert all(r.cpe_policy is None and len(r.goodputs_mbps)==2 for r in rows[:27])
    assert all(r.cpe_policy is not None and r.goodputs_mbps==() and r.repetitions_reported==2 for r in rows[27:])
    asymmetric=next(r for r in rows if r.iteration=='r5_iter4_asymmetric_ap2200_cpe1500_fq200')
    assert asymmetric.ap_policy.aql_by_ac[0]==(2200,4400)
    assert asymmetric.cpe_policy.aql_by_ac[0]==(1500,3000)
    assert all(r.mac_retry_rate is None for r in rows if r.round_id in {'R1','R2'})
    assert all(r.mac_retry_rate is not None for r in rows if r.round_id not in {'R1','R2'})


def test_per_ac_order_and_ef_treatment_preserved_without_mapping_claim():
    rows,_=load_all_measurements()
    row=next(r for r in rows if r.iteration=='r9_iter3_per_ac_vo800_be1800_fq256_rc28_dscp1')
    assert AC_ORDER==('VO','VI','BE','BK')
    assert row.ap_policy.aql_by_ac==((800,1600),(800,1600),(1800,3600),(800,1600))
    assert row.ap_policy.dscp_micro_vo_steering is True
    assert 'DSCP_EF_to_AC_VO_mapping_not_independently_verified' in row.flags
    assert row.ap_policy.htt_max_ampdu is None


def test_quantization_loss_and_reported_restoration_are_retained():
    rows,_=load_all_measurements()
    stock=next(r for r in rows if r.iteration=='r6_iter0_stock_both')
    assert stock.goodput_mbps==105.825
    assert 'aggregate_goodput_serialization_rounding_retained' in stock.flags
    lossful=[r for r in rows if r.packet_loss_pct]
    assert len(lossful)==5 and all(r.packet_loss_pct==5 for r in lossful)
    assert all('not_eligible_for_controller_promotion' in r.flags for r in lossful)
    assert all('reported_restoration_not_independent_acceptance' in r.flags for r in rows)


@pytest.mark.parametrize('mutation',[
    'duplicate_round','duplicate_window','missing_policy','boolean_aql','negative_aql','bad_ac_order',
    'bad_steering','nan_goodput','bad_total','bad_quantiles','bad_rtt_count',
    'bad_mac_fraction','fake_restoration','missing_rtts','missing_observation',
])
def test_malformed_or_misleading_records_fail_closed(tmp_path,mutation):
    raw,path=receipt_fixture(tmp_path)
    row=raw['iterations'][0]; p=row['candidate_knobs']; obs=row['observation']
    if mutation=='duplicate_round':
        path.write_text(json.dumps(raw),encoding='utf-8')
        with pytest.raises(ValueError):load_all_measurements([path,path])
        return
    if mutation=='duplicate_window':raw['iterations'].append(row.copy())
    if mutation=='missing_policy':p.pop('vo_low_us')
    if mutation=='boolean_aql':p['vo_low_us']=True
    if mutation=='negative_aql':p['vo_low_us']=-1
    if mutation=='bad_ac_order':p['vo_low_us']=p['vo_high_us']+1
    if mutation=='bad_steering':p['dscp_micro_vo_steering']=2
    if mutation=='nan_goodput':obs['goodput_rx_mbps']=float('nan')
    if mutation=='bad_total':row['total_bidir_goodput_mbps']+=10
    if mutation=='bad_quantiles':obs['p99_rtt_ms']=obs['p50_rtt_ms']-1
    if mutation=='bad_rtt_count':row['rtt_sample_count']+=1
    if mutation=='bad_mac_fraction':row['mac_retry_rate']=.9
    if mutation=='fake_restoration':obs['restoration_verified']='true'
    if mutation=='missing_rtts':row['rtts_ms']=None
    if mutation=='missing_observation':row.pop('observation')
    with pytest.raises(ValueError):parse_fixture(raw,path)


def test_unidirectional_receiver_aggregate_cannot_be_silently_changed(tmp_path):
    raw,path=receipt_fixture(tmp_path,3)
    raw['iterations'][0]['goodputs_per_rep'][0]+=20
    with pytest.raises(ValueError,match='mean disagrees'):parse_fixture(raw,path)


def test_joint_policy_key_excludes_workload_for_leakage_groups():
    rows,_=load_all_measurements()
    row=rows[0]
    assert replace(row,workload_regime='bidir_6flow',round_id='R9').policy_key==row.policy_key
    assert replace(row,ap_policy=replace(row.ap_policy,fq_quantum_bytes=1514)).policy_key!=row.policy_key


def test_dataset_records_missing_history_as_a_completed_unknown_check():
    data=normalized_regime_dataset()
    assert data['historical_checks'][0]['status']=='UNKNOWN_LOCAL_ARTIFACT_ABSENT'
    assert data['historical_checks'][0]['check_complete'] is True
    assert data['automatic_execution_allowed'] is False
    assert data['physical_acceptance_claim'] is False
    assert len(data['recipe_refs'])==9


@pytest.mark.parametrize('path',[EFGH_INPUTS/'bad.json',EFGH_INPUTS/'recipes/bad.json',
                                  ROOT/'artifacts/autoresearch/lap120_loco195_r9_per_ac_dscp_20261024.json',
                                  ROOT/'artifacts/autoresearch/waves_efgh_20261024/NUL',
                                  ROOT/'artifacts/autoresearch/waves_efgh_20261024/file.json:stream'])
def test_extended_output_scope_still_rejects_frozen_live_and_device_paths(path):
    with pytest.raises(ValueError):write_json(path,{'unsafe':True})


# Wave I is an additive API: historical R1-R9 serialization and callers stay fixed.
from orchestration.autoresearch.fmx_offline_data import (
    ALL14_ROUND_RECEIPTS, IJKL_INPUTS, CrossLayerEndpointPolicy,
    load_all14_measurements, normalized_cross_layer_dataset,
)


def test_all14_primary_and_auxiliary_counts_and_provenance():
    rows,refs=load_all14_measurements()
    assert len(rows)==85 and len(refs)==14
    assert sum(row.window_kind=='primary' for row in rows)==83
    assert [sum(row.round_id==f'R{i}' for row in rows) for i in range(1,15)]==[8,5,7,7,6,7,6,6,6,6,7,4,6,4]
    assert len(load_all14_measurements(include_auxiliary=False)[0])==83
    assert load_all14_measurements(reversed(ALL14_ROUND_RECEIPTS))[0]==rows
    for ref,path in zip(refs,ALL14_ROUND_RECEIPTS):
        assert ref['sha256']==sha256(path.read_bytes()).hexdigest()
    assert all(row.source_position.startswith(('/iterations/','/cross_regime_validation/')) for row in rows)


def test_all14_cross_layer_knobs_preserve_unknowns_and_uint32_sentinel():
    rows,_=load_all14_measurements()
    old=next(row for row in rows if row.round_id=='R1')
    assert old.ap_policy.fq_target_us is None
    assert old.ap_policy.tcp_limit_output_bytes is None
    assert old.cpe_policy is None
    r11=next(row for row in rows if row.iteration=='r11_iter0_stock_6flows')
    assert r11.ap_policy.fq_target_us==20000 and r11.ap_policy.fq_interval_us==100000
    assert r11.cpe_policy.tcp_limit_output_bytes==1048576
    assert r11.cpe_policy.tcp_notsent_lowat==4294967295
    r13=next(row for row in rows if row.iteration=='r13_iter4_dist3000m_scaled_be1900_3800')
    assert r13.ap_policy.distance_meters==r13.distance_meters==3000
    assert r13.ap_policy.aql_by_ac[2]==(1900,3800)
    assert 'distance_is_declared_coverage_timing_not_physical_range' in r13.flags


def test_all14_encryption_context_and_actual_topology_are_explicit():
    rows,_=load_all14_measurements()
    closed=[row for row in rows if row.round_id!='R14']
    opened=[row for row in rows if row.round_id=='R14']
    assert all(row.encryption_mode=='psk2' and row.encryption_evidence.startswith('INFERRED_') for row in closed)
    assert all(row.encryption_mode=='none' and row.ap_policy.encryption_mode=='none' for row in opened)
    assert all(row.associated_cpes==('Loco195',) for row in opened)
    assert all(row.topology_evidence=='RECEIPT_ASSOCIATED_PEERS_NOT_TITLE' for row in opened)
    assert all(row.rtts_ms==() and row.raw_rtt_sample_count_reported==20 for row in opened)
    assert all('raw_RTT_samples_absent_summary_quantiles_only' in row.flags for row in opened)
    assert all(row.encryption_evidence.endswith('NOT_EFFECTIVE_READBACK') for row in opened)


def test_all14_r12_missing_received_ping_and_replication_membership_not_fabricated():
    rows,_=load_all14_measurements()
    r12=[row for row in rows if row.round_id=='R12']
    assert [len(row.rtts_ms) for row in r12]==[40,40,39,40]
    assert all(row.goodputs_mbps==() and row.repetitions_reported==4 for row in r12)
    assert r12[2].packet_loss_pct==2.5
    assert 'not_eligible_for_controller_promotion' in r12[2].flags
    assert all('RTT_repetition_membership_and_pairing_not_retained' in row.flags for row in r12)


def test_all14_auxiliary_summaries_never_inherit_primary_quality_or_samples():
    rows,_=load_all14_measurements()
    aux=[row for row in rows if row.window_kind=='summary_validation']
    assert len(aux)==2
    assert {row.workload_regime for row in aux}=={'bidir_2flow','bulk_unidirectional'}
    for row in aux:
        assert row.goodputs_mbps==row.rtts_ms==()
        assert row.restoration_verified is row.station_drops is row.packet_loss_pct is None
        assert row.raw_rtt_sample_count_reported is None and row.repetitions_reported==2
        assert 'not_eligible_for_controller_promotion' in row.flags


@pytest.mark.parametrize('field,bad',[
    ('fq_target_us',True),('fq_target_us',0),('fq_interval_us',-1),
    ('fq_interval_us',5000),('tcp_limit_output_bytes',0),
    ('tcp_notsent_lowat',2**32),('tcp_notsent_lowat',1.5),
    ('distance_meters',True),('distance_meters',-1),('encryption_mode','ccmp'),
])
def test_all14_invalid_cross_layer_declarations_fail_closed(tmp_path,field,bad):
    raw=local_json(ALL14_ROUND_RECEIPTS[12]);raw['iterations']=raw['iterations'][:1]
    raw['iterations'][0]['candidate_knobs'][field]=bad
    path=tmp_path/'fixture.json';path.write_text(json.dumps(raw),encoding='utf-8')
    with pytest.raises(ValueError):load_all14_measurements([path])


def test_all14_policy_identity_keeps_each_new_axis_without_changing_legacy_type():
    rows,_=load_all14_measurements()
    row=next(row for row in rows if row.round_id=='R13')
    assert isinstance(row.ap_policy,CrossLayerEndpointPolicy)
    for field,value in [('fq_target_us',11000),('fq_interval_us',110000),
                        ('tcp_limit_output_bytes',12345),('tcp_notsent_lowat',12345),
                        ('distance_meters',1500),('encryption_mode','none')]:
        assert replace(row,ap_policy=replace(row.ap_policy,**{field:value})).policy_key!=row.policy_key
    legacy,_=load_all_measurements()
    assert 'fq_target_us' not in legacy[0].ap_policy.as_dict()


def test_missing_historical_receipt_finishes_unknown_check_without_stall(tmp_path):
    missing=tmp_path/ALL14_ROUND_RECEIPTS[0].name
    rows,refs=load_all14_measurements([missing,ALL14_ROUND_RECEIPTS[13]])
    assert len(rows)==4 and refs[0]['status']=='UNKNOWN_LOCAL_ARTIFACT_ABSENT'
    assert refs[0]['check_complete'] is True
    assert load_all14_measurements([missing])[0]==[]


def test_all14_dataset_counts_context_and_14_frozen_recipes():
    data=normalized_cross_layer_dataset()
    assert data['primary_window_count']==83 and data['auxiliary_window_count']==2
    assert len(data['recipe_refs'])==14 and len(data['records'])==85
    assert data['historical_checks'][0]['check_complete'] is True
    assert data['historical_checks'][0]['status']=='UNKNOWN_LOCAL_ARTIFACT_ABSENT'
    assert data['automatic_execution_allowed'] is data['physical_acceptance_claim'] is False


@pytest.mark.parametrize('path',[IJKL_INPUTS/'output.json',IJKL_INPUTS/'recipes/output.json'])
def test_all14_frozen_inputs_remain_output_protected(path):
    with pytest.raises(ValueError):write_json(path,{})


# Y adds independent contracts without changing any of the earlier cases above.
def test_certified_frozen_actual_counts_preserve_prior131():
    from dataclasses import asdict
    from orchestration.autoresearch import fmx_offline_data as offline

    records, refs = offline.load_all32_measurements()
    prior = local_json(offline.R26_NORMALIZED_OUTPUT)
    actual_prior = [{**asdict(row), 'policy_key': row.policy_key}
                    for row in records if int(row.round_id[1:]) <= 26]
    assert json.loads(json.dumps(actual_prior)) == prior['records']
    assert len(records) == 150 and len(refs) == 32
    assert len(offline.load_all32_measurements(include_auxiliary=False)[0]) == 148
    blocks = offline.load_all32_block_observations()
    previous = local_json(offline.R26_BLOCK_OUTPUT)
    assert [b for b in blocks['crossed'] if int(b['round_id'][1:]) <= 26] == previous['crossed']
    assert blocks['sequential'] == previous['sequential']
    assert len(blocks['crossed']) == 332 and len(blocks['sequential']) == 16
    assert len({(b['round_id'], b['block_index']) for b in blocks['crossed']}) == 106


@pytest.mark.parametrize('round_number,arms,matched,regime,flows,bidir', [
    (27, 4, 4, 'bidir_6flow', 6, True),
    (28, 3, 12, 'bidir_6flow', 6, True),
    (29, 2, 14, 'bidir_6flow', 6, True),
    (30, 4, 4, 'bidir_2flow', 2, True),
    (31, 4, 4, 'unidir_dl_2flow', 2, False),
    (32, 2, 16, 'bidir_6flow', 6, True),
])
def test_certified_actual_round_units_and_workload(round_number, arms, matched, regime, flows, bidir):
    from orchestration.autoresearch import fmx_offline_data as offline

    records, _ = offline.load_all32_measurements()
    selected = [r for r in records if r.round_id == f'R{round_number}']
    assert len(selected) == arms
    assert all((r.workload_regime, r.active_flow_count, r.bidirectional) == (regime, flows, bidir)
               for r in selected)
    assert all(len(r.repetition_blocks) == matched for r in selected)
    assert all(r.block_mean_consistent is (round_number == 31) for r in selected)


@pytest.mark.parametrize('position', range(19))
def test_certified_each_actual_arm_retains_exact_source_quality(position):
    from fractions import Fraction
    from orchestration.autoresearch import fmx_offline_data as offline

    records, _ = offline.load_all32_measurements()
    row = [r for r in records if int(r.round_id[1:]) >= 27][position]
    blocks = row.repetition_blocks
    assert row.raw_rtts_matches_blocks is True
    assert list(row.rtts_ms) == [v for b in blocks for v in b['rtts_ms']]
    assert type(row.mac_tx_packets) is int and row.mac_tx_packets > 0
    assert all(type(b['mac_tx_packets_delta']) is int and b['mac_tx_packets_delta'] > 0 for b in blocks)
    assert sum(b['mac_tx_packets_delta'] for b in blocks) == row.mac_tx_packets
    assert sum(b['mac_tx_retries_delta'] for b in blocks) == row.mac_tx_retries
    assert not any('zero_MAC_denominator' in flag for flag in row.flags)
    assert row.certified_wds_evidence['counter_interface'] == 'phy0-ap0.sta1'
    assert row.certified_wds_evidence['mac_block_sums_match_window'] is True
    assert row.certified_wds_evidence['recipe_execution_allowed'] is False
    assert row.certified_wds_evidence['rounded_summary_compatible'] is True
    comparisons = [('goodput_mbps', [b['observation']['goodput_rx_mbps'] for b in blocks]),
                   ('dl_goodput_mbps', [b['dl_goodput_mbps'] for b in blocks]),
                   ('ul_goodput_mbps', [b['ul_goodput_mbps'] for b in blocks]),
                   ('jain_fairness', [b['observation']['jain_fairness'] for b in blocks])]
    exact = all(Fraction(str(getattr(row, key))) * len(values) == sum(map(lambda x: Fraction(str(x)), values))
                for key, values in comparisons)
    assert row.block_mean_consistent is exact


def test_certified_literal_equality_and_float_noise_are_distinct():
    from orchestration.autoresearch import fmx_offline_data as offline

    records, _ = offline.load_all32_measurements()
    r27 = next(r for r in records if r.round_id == 'R27')
    evidence = r27.certified_wds_evidence
    assert evidence['block_mean_exact_delta_fractions']['goodput_mbps'] == '0'
    assert evidence['block_mean_exact_delta_fractions']['jain_fairness'] != '0'
    assert r27.block_mean_consistent is False
    assert abs(evidence['block_mean_deltas']['jain_fairness']) > 0
    assert sum(r.block_mean_consistent for r in records if isinstance(r, offline.CertifiedWDSMeasurement)) == 4


@pytest.mark.parametrize('mutation', [
    'duplicate_block', 'boolean_counter', 'chronology', 'bad_regime',
    'flow_conflict', 'bad_rtt_count', 'nonfinite', 'conflicting_hook',
])
def test_certified_malformed_source_fails_closed(tmp_path, mutation):
    from copy import deepcopy
    from orchestration.autoresearch import fmx_offline_data as offline

    payload = deepcopy(local_json(offline.R27_TO_R32_RECEIPTS[0]))
    first = payload['iterations'][0]
    if mutation == 'duplicate_block':
        first['repetition_blocks'][1] = deepcopy(first['repetition_blocks'][0])
    elif mutation == 'boolean_counter':
        first['repetition_blocks'][0]['mac_tx_packets_delta'] = True
    elif mutation == 'chronology':
        first['raw_rtts_ms'][0] += 0.00001
    elif mutation == 'bad_regime':
        payload['workload_regime'] = 'invented'
    elif mutation == 'flow_conflict':
        first['active_flow_count'] = 2
    elif mutation == 'bad_rtt_count':
        first['rtt_sample_count'] += 1
    elif mutation == 'nonfinite':
        first['observation']['goodput_rx_mbps'] = float('inf')
    else:
        first['candidate_knobs']['force_tx_status'] = 1 - first['force_tx_status']
    path = tmp_path / 'fixture.json'
    path.write_text(json.dumps(payload), encoding='utf-8')
    with pytest.raises(ValueError):
        offline.load_all32_measurements([path])


def test_certified_counter_mismatch_is_retained_and_ineligible(tmp_path):
    from orchestration.autoresearch import fmx_offline_data as offline

    payload = local_json(offline.R27_TO_R32_RECEIPTS[0])
    payload['iterations'][0]['mac_tx_packets_delta'] += 100
    payload['iterations'][0]['mac_retry_rate'] = (
        payload['iterations'][0]['mac_tx_retries_delta'] / payload['iterations'][0]['mac_tx_packets_delta'])
    path = tmp_path / 'fixture.json'
    path.write_text(json.dumps(payload), encoding='utf-8')
    records, _ = offline.load_all32_measurements([path])
    row = next(r for r in records if r.round_id == 'R27')
    assert row.certified_wds_evidence['mac_block_sums_match_window'] is False
    assert 'window_MAC_counters_disagree_with_block_sums' in row.flags


def test_certified_dataset_reports_observed_vs_requested_counts():
    from orchestration.autoresearch import fmx_offline_data as offline

    data = offline.normalized_certified_wds_dataset()
    assert data['observed_record_count'] == 150 and data['requested_record_count'] == 151
    assert data['crossed_observation_count'] == 332 and data['requested_crossed_observation_count'] == 328
    assert data['matched_round_scoped_block_count'] == 106 and data['requested_matched_block_count'] == 108
    assert data['new_arm_count'] == 19 and data['requested_new_arm_count'] == 20
    assert data['literal_exact_block_mean_pass_count'] == 4
    assert data['raw_rtt_chronology_pass_count'] == data['positive_MAC_denominator_count'] == 19
    assert data['automatic_execution_allowed'] is data['physical_acceptance_claim'] is False


def test_certified_new_outputs_cannot_overwrite_frozen_inputs(tmp_path):
    from orchestration.autoresearch import fmx_offline_data as offline

    for path in (offline.YZAB_INPUTS / 'out.json', offline.YZAB_INPUTS / 'nested' / 'out.json'):
        with pytest.raises(ValueError):
            write_json(path, {})
    with pytest.raises(ValueError):
        offline.load_all32_measurements(include_auxiliary=1)


# AC preserves the fixed Y corpus API above; latest aliases now include R33-R42.
def test_exact_campaign_preserves_prior150_and_actual_units():
    from dataclasses import asdict
    from orchestration.autoresearch import fmx_offline_data as offline
    rows, refs = offline.load_all42_measurements()
    prior = local_json(offline.R32_NORMALIZED_OUTPUT)
    preserved = [{**asdict(r), 'policy_key': r.policy_key} for r in rows if int(r.round_id[1:]) <= 32]
    assert json.loads(json.dumps(preserved)) == prior['records']
    assert len(rows) == 184 and len(refs) == 42
    assert len(offline.load_all42_measurements(include_auxiliary=False)[0]) == 182
    blocks = offline.load_all42_block_observations()
    old = local_json(offline.R32_BLOCK_OUTPUT)
    assert [b for b in blocks['crossed'] if int(b['round_id'][1:]) <= 32] == old['crossed']
    assert blocks['sequential'] == old['sequential']
    assert len(blocks['crossed']) == 540 and len(blocks['sequential']) == 16
    assert len({(b['round_id'], b['block_index']) for b in blocks['crossed']}) == 182


@pytest.mark.parametrize('round_number,arms,matched,regime,flows,bidir,distance,coverage', [
    (33,4,4,'bidir_6flow',6,True,3000,6), (34,4,4,'bidir_6flow',6,True,3000,6),
    (35,4,4,'bidir_6flow',6,True,6000,13), (36,4,4,'bidir_12flow',12,True,None,None),
    (37,4,4,'bidir_8flow',8,True,None,None), (38,4,4,'bidir_8flow',8,True,None,None),
    (39,4,4,'unidir_ul_2flow',2,False,None,None), (40,2,16,'bidir_6flow',6,True,None,None),
    (41,2,16,'bidir_6flow',6,True,None,None), (42,2,16,'bidir_6flow',6,True,None,None),
])
def test_exact_campaign_each_round_context(round_number,arms,matched,regime,flows,bidir,distance,coverage):
    from orchestration.autoresearch import fmx_offline_data as offline
    rows, _ = offline.load_all42_measurements()
    chosen = [r for r in rows if r.round_id == f'R{round_number}']
    assert len(chosen) == arms
    for r in chosen:
        assert (r.workload_regime,r.active_flow_count,r.bidirectional) == (regime,flows,bidir)
        assert len(r.repetition_blocks) == matched
        assert r.distance_meters == r.ap_policy.distance_meters == r.cpe_policy.distance_meters == distance
        assert r.coverage_class == coverage
        assert r.certified_wds_evidence['physical_distance_verified'] is False


@pytest.mark.parametrize('position', range(34))
def test_exact_campaign_every_arm_preserves_chronology_counters_and_literal_results(position):
    from fractions import Fraction
    from orchestration.autoresearch import fmx_offline_data as offline
    rows, _ = offline.load_all42_measurements()
    r = [r for r in rows if isinstance(r, offline.ExactCampaignMeasurement)][position]
    blocks = r.repetition_blocks
    evidence = r.certified_wds_evidence
    assert r.raw_rtts_matches_blocks is True
    assert list(r.rtts_ms) == [v for b in blocks for v in b['rtts_ms']]
    assert r.mac_tx_packets > 0 and all(b['mac_tx_packets_delta'] > 0 for b in blocks)
    assert sum(b['mac_tx_packets_delta'] for b in blocks) == r.mac_tx_packets
    assert sum(b['mac_tx_retries_delta'] for b in blocks) == r.mac_tx_retries
    assert evidence['mac_block_sums_match_window'] is True
    assert evidence['source_receipt']['sha256'] and evidence['source_recipe']['sha256']
    assert evidence['recipe_execution_allowed'] is evidence['effective_hardware_control_accepted'] is False
    pairs = {'goodput_mbps': [b['observation']['goodput_rx_mbps'] for b in blocks],
        'dl_goodput_mbps': [b['dl_goodput_mbps'] for b in blocks],
        'ul_goodput_mbps': [b['ul_goodput_mbps'] for b in blocks],
        'jain_fairness': [b['observation']['jain_fairness'] for b in blocks]}
    rational = {k: Fraction(str(getattr(r,k))) - sum(Fraction(str(v)) for v in vs)/len(vs) for k,vs in pairs.items()}
    floating = {k: getattr(r,k) - sum(vs)/len(vs) for k,vs in pairs.items()}
    assert evidence['block_mean_exact_delta_fractions'] == {k: str(v) for k,v in rational.items()}
    assert evidence['block_mean_float_deltas'] == floating
    assert r.block_mean_consistent is all(v == 0 for v in rational.values())
    assert evidence['block_mean_float_consistent'] is all(v == 0 for v in floating.values())


def test_exact_campaign_requested18_literal_claim_is_audited_without_rounding_rescue():
    from orchestration.autoresearch import fmx_offline_data as offline
    rows, _ = offline.load_all42_measurements()
    selected = [r for r in rows if r.round_id in {'R37','R38','R39','R40','R41','R42'}]
    assert len(selected) == 18
    failed = {(r.round_id, int(r.iteration.split('_iter')[1].split('_')[0])) for r in selected if not r.block_mean_consistent}
    assert failed == {('R37',1),('R37',2),('R37',3),('R38',0),('R38',2),('R39',3)}
    assert sum(r.block_mean_consistent for r in selected) == 12
    assert sum(r.certified_wds_evidence['block_mean_float_consistent'] for r in selected) == 13
    assert sum(r.certified_wds_evidence['block_mean_numpy_consistent'] for r in selected) == 14


@pytest.mark.parametrize('arm', [0,1])
def test_exact_campaign_r41_both_arms_zero_loss_rational_float_quantiles_and_frames(arm):
    import numpy as np
    from orchestration.autoresearch import fmx_offline_data as offline
    rows, _ = offline.load_all42_measurements()
    r = [r for r in rows if r.round_id == 'R41'][arm]
    e = r.certified_wds_evidence
    assert r.packet_loss_pct == 0.0
    assert sum(b['pings_sent'] for b in r.repetition_blocks) == 160
    assert sum(b['pings_rcvd'] for b in r.repetition_blocks) == 160
    assert len(r.rtts_ms) == 160 and r.mac_tx_packets > 579000
    assert r.block_mean_consistent is e['block_mean_float_consistent'] is True
    assert e['exact_numpy_quantiles'] is True
    assert [r.p50_ms,r.p95_ms,r.p99_ms] == list(np.percentile(r.rtts_ms,[50,95,99]))
    assert all('recorded_block_observation' in b for b in r.repetition_blocks)


@pytest.mark.parametrize('arm', range(4))
def test_exact_campaign_r36_all_four_crashes_retained_without_claiming_oom_proof(arm):
    from orchestration.autoresearch import fmx_offline_data as offline
    rows, _ = offline.load_all42_measurements()
    r = [r for r in rows if r.round_id == 'R36'][arm]
    assert r.goodput_mbps == 0.0 and r.station_drops == 1
    assert r.packet_loss_pct == 0.0 and len(r.rtts_ms) == 40
    assert r.source_failure_metadata['crash'] is r.source_failure_metadata['disqualified'] is True
    assert r.source_failure_metadata['reason'] == 'Station dropped during treatment (1 drops)'
    assert r.source_failure_metadata['fmx_loss']['nonfinite_source_token'] == 'Infinity'
    assert 'NOT_ESTABLISHED' in r.source_failure_metadata['oom_cause']
    assert 'not_eligible_for_controller_promotion' in r.flags
    assert all(b['source_failure_metadata']['crash'] for b in r.repetition_blocks)
    json.dumps(r.certified_wds_evidence, allow_nan=False)


@pytest.mark.parametrize('mutation', ['nonfinite_measurement','unqualified_infinity','nan_loss','duplicate',
    'bad_regime','bad_distance','bad_coverage','chronology','boolean_counter','nested_quality_conflict'])
def test_exact_campaign_malformed_source_fails_closed(tmp_path,mutation):
    from orchestration.autoresearch import fmx_offline_data as offline
    raw = json.loads(offline.R33_TO_R42_RECEIPTS[8].read_text())
    a = raw['iterations'][0]
    if mutation == 'nonfinite_measurement': a['observation']['goodput_rx_mbps'] = float('inf')
    elif mutation == 'unqualified_infinity': a['evaluation']['fmx_loss'] = float('inf')
    elif mutation == 'nan_loss': a['evaluation'].update(fmx_loss=float('nan'), decision='crash', disqualified=True)
    elif mutation == 'duplicate': raw['iterations'].append(a)
    elif mutation == 'bad_regime': raw['traffic_regime'] = 'bidir_8flow'
    elif mutation == 'bad_distance': a['candidate_knobs']['distance_m'] = 3000
    elif mutation == 'bad_coverage': a['coverage_class'] = 6
    elif mutation == 'chronology': a['raw_rtts_ms'].reverse()
    elif mutation == 'boolean_counter': a['repetition_blocks'][0]['mac_tx_packets_delta'] = True
    else: a['repetition_blocks'][0]['observation']['goodput_rx_mbps'] += 1
    path = tmp_path/'fixture.json'; path.write_text(json.dumps(raw))
    with pytest.raises(ValueError): offline.load_all42_measurements([path])


def test_exact_campaign_dataset_reports_counts_and_protects_frozen_outputs():
    from orchestration.autoresearch import fmx_offline_data as offline
    d = offline.normalized_exact_campaign_dataset()
    assert (d['observed_record_count'],d['requested_record_count']) == (184,182)
    assert (d['matched_round_scoped_block_count'],d['requested_matched_block_count']) == (182,186)
    assert d['crossed_observation_count'] == d['requested_crossed_observation_count'] == 540
    assert d['crash_arm_count'] == 4 and d['new_arm_count'] == 34
    assert d['automatic_execution_allowed'] is d['physical_acceptance_claim'] is False
    for p in (offline.ACAF_INPUTS/'out.json',offline.ACAF_INPUTS/'nested/out.json'):
        with pytest.raises(ValueError): offline.write_json(p,{})
    with pytest.raises(ValueError): offline.load_all42_measurements(include_auxiliary=1)


def test_dyadic_campaign_latest194_preserves_all184_prior_records_and700_blocks():
    from dataclasses import asdict
    from orchestration.autoresearch import fmx_offline_data as offline
    rows, refs=offline.load_normalized_records()
    prior=local_json(offline.R42_NORMALIZED_OUTPUT)
    old=[{**asdict(r),'policy_key':r.policy_key} for r in rows if int(r.round_id[1:])<=42]
    assert json.loads(json.dumps(old))==prior['records']
    assert len(rows)==194 and len(refs)==47
    assert len(offline.load_all47_measurements(include_auxiliary=False)[0])==192
    blocks=offline.load_crossed_block_records();previous=local_json(offline.R42_BLOCK_OUTPUT)
    assert len(blocks['crossed'])==700 and len(blocks['sequential'])==16
    assert len({(b['round_id'],b['block_index']) for b in blocks['crossed']})==262
    assert [b for b in blocks['crossed'] if int(b['round_id'][1:])<=42]==previous['crossed']
    assert blocks['sequential']==previous['sequential']
    assert len(offline.load_all42_measurements()[0])==184


@pytest.mark.parametrize('round_number,regime,flows,bidir',[
    (43,'unidir_dl_2flow',2,False),(44,'unidir_dl_2flow',2,False),
    (45,'bidir_6flow',6,True),(46,'unidir_ul_2flow',2,False),(47,'bidir_8flow',8,True),
])
def test_dyadic_campaign_each_declared_context_and16_matched_blocks(round_number,regime,flows,bidir):
    from orchestration.autoresearch import fmx_offline_data as offline
    rows,_=offline.load_all47_measurements();own=[r for r in rows if r.round_id==f'R{round_number}']
    assert len(own)==2
    for r in own:
        assert (r.workload_regime,r.active_flow_count,r.bidirectional)==(regime,flows,bidir)
        assert len(r.repetition_blocks)==16 and len(r.rtts_ms)==160
        assert r.packet_loss_pct==0 and r.station_drops==0 and r.restoration_verified is True
        assert sum(b['pings_sent'] for b in r.repetition_blocks)==160
        assert sum(b['pings_rcvd'] for b in r.repetition_blocks)==160
        assert r.distance_meters is None and r.coverage_class is None


@pytest.mark.parametrize('position',range(10))
def test_dyadic_campaign_all_ten_arms_zero_ulp_exact_means_and_original_chronology(position):
    from fractions import Fraction
    import numpy as np
    from orchestration.autoresearch import fmx_offline_data as offline
    rows,_=offline.load_all47_measurements()
    r=[r for r in rows if isinstance(r,offline.DyadicCampaignMeasurement)][position]
    audit=offline.audit_dyadic_block_means(r)
    assert audit==r.dyadic_mean_audit==r.certified_wds_evidence['dyadic_mean_audit']
    assert audit['status']=='DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP'
    assert list(audit['fraction_deltas'].values())==['0']*4
    assert list(audit['numpy_float_deltas'].values())==[0.0]*4
    assert list(audit['ulp_errors'].values())==[0]*4
    assert audit['all_recorded_decimal_inputs_dyadic'] is audit['all_binary_rational_means_equal'] is True
    assert list(r.rtts_ms)==[v for b in r.repetition_blocks for v in b['rtts_ms']]
    assert r.mac_tx_packets>0 and all(b['mac_tx_packets_delta']>0 for b in r.repetition_blocks)
    assert sum(b['mac_tx_packets_delta'] for b in r.repetition_blocks)==r.mac_tx_packets
    assert sum(b['mac_tx_retries_delta'] for b in r.repetition_blocks)==r.mac_tx_retries
    for name,getter in [('goodput_mbps',lambda b:b['observation']['goodput_rx_mbps']),
        ('dl_goodput_mbps',lambda b:b['dl_goodput_mbps']),('ul_goodput_mbps',lambda b:b['ul_goodput_mbps']),
        ('jain_fairness',lambda b:b['observation']['jain_fairness'])]:
        values=[getter(b) for b in r.repetition_blocks]
        assert Fraction(str(getattr(r,name)))*16==sum(Fraction(str(v)) for v in values)
        assert getattr(r,name)==float(np.mean(values))


@pytest.mark.parametrize('metric',['goodput_mbps','dl_goodput_mbps','ul_goodput_mbps','jain_fairness'])
def test_dyadic_mean_helper_rejects_one_ulp_perturbation_without_tolerance(metric):
    from dataclasses import asdict
    import numpy as np
    from orchestration.autoresearch import fmx_offline_data as offline
    r=asdict(next(r for r in offline.load_all47_measurements()[0] if r.round_id=='R45'))
    r[metric]=float(np.nextafter(r[metric],np.inf))
    audit=offline.audit_dyadic_block_means(r)
    assert audit['ulp_errors'][metric]==1
    assert audit['fraction_deltas'][metric]!='0'
    assert audit['all_fraction_zero'] is audit['all_float_zero'] is audit['all_zero_ulp'] is False
    assert audit['status']=='NOT_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP'


def test_dyadic_mean_helper_does_not_recertify_old_r41_numpy_roundoff():
    from orchestration.autoresearch import fmx_offline_data as offline
    rows,_=offline.load_all42_measurements()
    r=next(r for r in rows if r.round_id=='R41' and '_iter1_' in r.iteration)
    audit=offline.audit_dyadic_block_means(r)
    assert audit['all_fraction_zero'] is True
    assert audit['all_float_zero'] is audit['all_zero_ulp'] is False
    assert audit['status']=='NOT_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP'


@pytest.mark.parametrize('left,right,distance',[(0.0,-0.0,0),(1.0,1.0,0),(-2.0,-2.0,0)])
def test_float_ulp_distance_exact_and_signed_zero(left,right,distance):
    from orchestration.autoresearch import fmx_offline_data as offline
    assert offline.float_ulp_distance(left,right)==distance


@pytest.mark.parametrize('mutation',['duplicate','wrong_regime','wrong_flows','boolean_direction',
    'nonfinite','boolean_counter','bad_chronology','bad_ping_count','nested_mismatch'])
def test_dyadic_campaign_malformed_source_fails_closed(tmp_path,mutation):
    from orchestration.autoresearch import fmx_offline_data as offline
    raw=local_json(offline.R43_TO_R47_RECEIPTS[2]);a=raw['iterations'][0]
    if mutation=='duplicate':raw['iterations'].append(a)
    elif mutation=='wrong_regime':raw['traffic_regime']='bidir_8flow'
    elif mutation=='wrong_flows':a['active_flow_count']=8
    elif mutation=='boolean_direction':a['bidirectional']=1
    elif mutation=='nonfinite':a['observation']['goodput_rx_mbps']=float('inf')
    elif mutation=='boolean_counter':a['repetition_blocks'][0]['mac_tx_packets_delta']=True
    elif mutation=='bad_chronology':a['raw_rtts_ms'].reverse()
    elif mutation=='bad_ping_count':a['repetition_blocks'][0]['pings_rcvd']=9
    else:a['repetition_blocks'][0]['observation']['goodput_rx_mbps']+=1
    path=tmp_path/'fixture.json';path.write_text(json.dumps(raw))
    with pytest.raises(ValueError):offline.load_all47_measurements([path])


def test_dyadic_campaign_provenance_output_protection_and_aggregate_counts():
    from orchestration.autoresearch import fmx_offline_data as offline
    data=offline.normalized_dyadic_campaign_dataset()
    assert data['schema_version']==9
    assert (data['observed_record_count'],data['crossed_observation_count'],data['matched_round_scoped_block_count'])==(194,700,262)
    assert data['dyadic_exact_arm_count']==data['new_arm_count']==10
    assert data['raw_rtt_chronology_pass_count']==data['positive_MAC_denominator_count']==10
    assert data['automatic_execution_allowed'] is data['physical_acceptance_claim'] is False
    for path in (offline.AGAJ_INPUTS/'output.json',offline.AGAJ_INPUTS/'nested/output.json'):
        with pytest.raises(ValueError):offline.write_json(path,{})
    with pytest.raises(ValueError):offline.load_all47_measurements(include_auxiliary=1)


def test_bi_directional_alias_audit_preserves_inapplicable_literal_values():
    from orchestration.autoresearch import fmx_offline_data as offline
    assert callable(getattr(offline,'audit_directional_throughput',None))
    result=offline.audit_directional_throughput('unidir_dl_2flow',total=10,dl=10,ul=0,jain=.5,
        blocks=[dict(observation=dict(goodput_rx_mbps=10,jain_fairness=.5),dl_goodput_mbps=10,ul_goodput_mbps=0)])
    assert result['active_direction']=='DL'
    assert result['active_direction_equals_total_every_arm_and_block'] is True
    assert result['jain_applicable_for_QoE_inference'] is False


@pytest.mark.parametrize('regime,dl,ul,active',[('unidir_dl_2flow',10,0,'DL'),('unidir_ul_2flow',0,10,'UL')])
def test_bi_directional_alias_has_one_active_hypothesis_not_constant_Jain_evidence(regime,dl,ul,active):
    from orchestration.autoresearch import fmx_offline_data as offline
    b=dict(observation=dict(goodput_rx_mbps=10,jain_fairness=.5),dl_goodput_mbps=dl,ul_goodput_mbps=ul)
    r=offline.audit_directional_throughput(regime,total=10,dl=dl,ul=ul,jain=.5,blocks=[b])
    assert r['active_direction']==active and r['literal_recorded_jain']==.5
    assert r['jain_applicable_for_QoE_inference']is False
    assert r['required_QoE_metrics']==['p50_rtt_ms','p95_rtt_ms','p99_rtt_ms','goodput_rx_mbps']
    assert r['duplicate_active_throughput_hypothesis']is False


@pytest.mark.parametrize('bad',[None,True,10.000001,float('nan')])
def test_bi_directional_auditor_rejects_missing_or_approximate_active_alias(bad):
    from orchestration.autoresearch import fmx_offline_data as offline
    b=dict(observation=dict(goodput_rx_mbps=10,jain_fairness=.5),dl_goodput_mbps=bad,ul_goodput_mbps=0)
    with pytest.raises(ValueError):offline.audit_directional_throughput('unidir_dl_2flow',total=10,dl=10,ul=0,jain=.5,blocks=[b])


def test_bm_R87_saved_one_based_step_has_explicit_roundtrip_only_adapter():
    from orchestration.autoresearch import fmx_offline_data as offline
    manifest=local_json(ROOT/'artifacts/autoresearch/waves_bm_to_bp_20261024/inputs_manifest.json')
    entry=next(e for e in manifest['entries']if e['round']==87 and e['path'].endswith('.json'))
    payload=local_json(ROOT/entry['copy'])
    rows=offline._exact_campaign_block_rows(payload,max_round=92)
    assert len(rows)==32
    assert all(b['crossover_step']==b['source_step_in_block']-1 for b in rows)
    assert all(b['source_step_field']=='step_in_block'for b in rows)
