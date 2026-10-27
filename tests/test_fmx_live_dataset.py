"""Revision-fixed R56 replay and latest source-bound R1-R60 corpus contracts."""
from copy import deepcopy
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path

import pytest

from orchestration.autoresearch import fmx_live_dataset as live
from orchestration.autoresearch import fmx_offline_data as old


@pytest.fixture(scope='module')
def corpus():
    return live.load_live_dataset(through_round=56), live.load_crossed_dataset(through_round=56)


@pytest.fixture(scope='module')
def typed():
    return live.load_all56_measurements()[0]


def test_all_rounds_and_actual_block_identities(corpus):
    data, blocks = corpus
    assert data['schema_version'] == 10
    assert len(data['records']) == data['observed_record_count'] == 212
    assert (data['primary_window_count'], data['auxiliary_window_count']) == (210, 2)
    assert set(data['round_counts']) == {f'R{i}' for i in range(1, 57)}
    assert all(v > 0 for v in data['round_counts'].values())
    assert len(blocks['crossed']) == 988
    assert len({(r['round_id'], r['block_index']) for r in blocks['crossed']}) == 406
    assert len(blocks['sequential']) == 16
    new = [r for r in blocks['crossed'] if int(r['round_id'][1:]) >= 48]
    assert len(new) == 288
    assert len({(r['round_id'], r['block_index']) for r in new}) == 144
    assert len({(r['round_id'], r['block_index'], r['crossover_step']) for r in new}) == 288


def test_previous_sealed_record_dictionaries_and_blocks_are_identical(corpus):
    data, blocks = corpus
    assert data['records'][:194] == old.local_json(live.R47_RECORDS)['records']
    prior = old.local_json(live.R47_BLOCKS)
    assert blocks['crossed'][:700] == prior['crossed']
    assert blocks['sequential'] == prior['sequential']
    assert data['automatic_execution_allowed'] is data['physical_acceptance_claim'] is False


def test_old_normalizer_apis_remain_revision_fixed(typed):
    assert len(old.load_all47_measurements()[0]) == 194
    assert len(typed) == 212
    assert len(live.load_all56_measurements(include_auxiliary=False)[0]) == 210
    assert all(r.window_kind == 'primary' for r in live.load_all56_measurements(include_auxiliary=False)[0])


@pytest.mark.parametrize('number', range(48, 57))
def test_all_eighteen_new_arms_have_exact_means_health_and_chronology(typed, number):
    records = [r for r in typed if r.round_id == f'R{number}']
    assert len(records) == 2
    for r in records:
        a = r.dyadic_mean_audit
        assert a['status'] == 'DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP'
        assert list(a['fraction_deltas'].values()) == ['0'] * 4
        assert list(a['numpy_float_deltas'].values()) == [0.0] * 4
        assert list(a['ulp_errors'].values()) == [0] * 4
        assert a['all_binary_rational_means_equal'] and a['all_recorded_decimal_inputs_dyadic']
        assert len(r.rtts_ms) == 160 and r.packet_loss_pct == 0
        assert r.restoration_verified is True and r.station_drops == 0
        assert r.raw_rtts_matches_blocks is True
        assert r.mac_tx_packets > 0 and r.mac_tx_retries > 0
        assert r.certified_wds_evidence['mac_block_sums_match_window'] is True
        assert r.certified_wds_evidence['counter_interface'] == 'phy0-ap0.sta1'


@pytest.mark.parametrize('number,distance,coverage', [(48,3000,6),(49,6000,13),(52,3000,6),(53,6000,13)])
def test_coverage_is_shared_declared_timing_without_physical_range(typed, number, distance, coverage):
    for r in (r for r in typed if r.round_id == f'R{number}'):
        assert (r.distance_meters, r.coverage_class) == (distance, coverage)
        assert r.ap_policy.distance_meters == r.cpe_policy.distance_meters == distance
        assert r.workload_regime == 'bidir_6flow'
        assert r.certified_wds_evidence['physical_distance_verified'] is False
        assert r.certified_wds_evidence['programmed_distance_source_field'] == 'distance_m'
        assert r.certified_wds_evidence['original_endpoint_states_omit_distance'] is True


@pytest.mark.parametrize('number', [50,51,54,55,56])
def test_absent_default_distance_and_coverage_stay_unknown(typed, number):
    for r in (r for r in typed if r.round_id == f'R{number}'):
        assert r.distance_meters is r.coverage_class is None
        assert r.ap_policy.distance_meters is r.cpe_policy.distance_meters is None
        assert r.certified_wds_evidence['timing_provenance'] == 'UNKNOWN_NO_DEFAULT_TIMING_IMPUTED'


def test_manifest_verifies_all_twenty_seven_files():
    manifest = live._inputs()
    assert len(manifest['entries']) == 27
    assert set(e['round'] for e in manifest['entries']) == set(range(48,57))
    for e in manifest['entries']:
        raw = Path(e['path']).read_bytes()
        assert len(raw) == e['bytes'] and hashlib.sha256(raw).hexdigest() == e['sha256']


def test_r57_receipt_is_rejected_before_any_content_read(tmp_path):
    forbidden = tmp_path/'lap120_loco195_r57_forbidden.json'
    with pytest.raises(ValueError, match='not an authenticated'):
        list(live._campaign([forbidden]))
    assert not forbidden.exists()


@pytest.mark.parametrize('selector', [0,1,None,'false'])
def test_auxiliary_flag_requires_an_actual_boolean(selector):
    with pytest.raises(ValueError, match='must be boolean'):
        live.load_all56_measurements(include_auxiliary=selector)


def test_recipe_paths_are_provenance_never_imported(monkeypatch):
    import builtins
    original = builtins.__import__
    def bounded(name, *args, **kwargs):
        if name.startswith(('tools.bench', 'paramiko')):
            raise AssertionError('Recipe or device module import forbidden')
        return original(name, *args, **kwargs)
    monkeypatch.setattr(builtins, '__import__', bounded)
    assert len(live.load_live_dataset(through_round=56)['records']) == 212


def test_context_rejects_conflicting_typed_declarations():
    payload = old.local_json(live.R48_TO_R56_RECEIPTS[0])
    source = payload['iterations'][0]
    for key, value in [('active_flow_count', True), ('bidirectional', 1), ('distance_m',6000), ('coverage_class',13)]:
        changed = deepcopy(source)
        changed[key] = value
        with pytest.raises(ValueError):
            live._context(48, payload, changed)


def test_json_rejects_duplicate_keys_and_nonfinite_values(tmp_path):
    p = tmp_path/'bad.json'
    for text in ['{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}', '{"x":1e999}']:
        p.write_text(text)
        with pytest.raises(ValueError):
            live._json(p)


def test_prior_corpus_pin_rejects_changed_or_untrusted_evidence(tmp_path):
    p = tmp_path/'altered.json'; p.write_text('{}')
    with pytest.raises(ValueError, match='checksum or size'):
        live._prior(p, live.R47_RECORDS.name)
    with pytest.raises(ValueError, match='external pin'):
        live._prior(live.R47_RECORDS, live.R47_RECORDS.name, p)


def test_pair_output_preflight_never_creates_a_partial_pair(tmp_path, monkeypatch):
    records, blocks = tmp_path/'records.json', tmp_path/'blocks.json'
    blocks.write_bytes(b'original')
    monkeypatch.setattr(live, 'RECORDS_OUTPUT', records)
    monkeypatch.setattr(live, 'BLOCKS_OUTPUT', blocks)
    with pytest.raises(FileExistsError):
        live.build_dataset_outputs()
    assert blocks.read_bytes() == b'original' and not records.exists()


@pytest.fixture(scope='module')
def corpus60():
    return live.load_live_dataset(through_round=60),live.load_crossed_dataset(through_round=60)


@pytest.fixture(scope='module')
def typed60():
    return live.load_all60_measurements()[0]


def test_latest_canonical_corpus_has_all_sixty_rounds_and_preserves_r56_exactly(corpus60):
    data,blocks=corpus60
    assert data['schema_version']==11
    assert len(data['records'])==data['observed_record_count']==220
    assert (data['primary_window_count'],data['auxiliary_window_count'])==(218,2)
    assert set(data['round_counts'])=={f'R{i}' for i in range(1,61)}
    assert len(blocks['crossed'])==1116
    assert len({(b['round_id'],b['block_index']) for b in blocks['crossed']})==470
    assert len(blocks['sequential'])==16
    assert data['records'][:212]==live._sealed56(live.R56_RECORDS_OUTPUT)['records']
    saved=live._sealed56(live.R56_BLOCKS_OUTPUT)
    assert blocks['crossed'][:988]==saved['crossed'] and blocks['sequential']==saved['sequential']
    assert data['automatic_execution_allowed'] is data['physical_acceptance_claim'] is False
    assert len([r for r in data['records'] if r['round_id']=='R57'])==2


def test_explicit_historical_r56_canonical_interfaces_replay_identical_serialized_bytes():
    encode=lambda value:(json.dumps(value,indent=2,allow_nan=False)+'\n').encode()
    assert encode(live.load_live_dataset(through_round=56))==live.R56_RECORDS_OUTPUT.read_bytes()
    assert encode(live.load_crossed_dataset(through_round=56))==live.R56_BLOCKS_OUTPUT.read_bytes()


@pytest.mark.parametrize('number',range(57,61))
def test_eight_new_arms_have_exact_means_complete_rtt_and_declared_context(typed60,number):
    own=[r for r in typed60 if r.round_id==f'R{number}']
    assert len(own)==2
    for row in own:
        assert (row.distance_meters,row.coverage_class)==(100,0)
        assert row.ap_policy.distance_meters==row.cpe_policy.distance_meters==100
        assert (row.active_flow_count,row.bidirectional)==((8,True) if number==57 else (6,True))
        assert row.workload_regime==('bidir_8flow' if number==57 else 'bidir_6flow')
        assert len(row.rtts_ms)==160 and row.packet_loss_pct==row.station_drops==0
        assert row.restoration_verified is True and row.raw_rtts_matches_blocks is True
        assert row.dyadic_mean_audit['status']=='DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP'
        assert list(row.dyadic_mean_audit['fraction_deltas'].values())==['0']*4
        assert list(row.dyadic_mean_audit['ulp_errors'].values())==[0]*4
        evidence=row.certified_wds_evidence
        assert (evidence['slot_time_us'],evidence['ack_timeout_us'])==(9,18)
        assert evidence['slot_ack_source']=='ROOT_RECEIPT_ONLY'
        assert evidence['saved_context_credited'] is True
        assert evidence['physical_distance_verified'] is evidence['effective_timing_independently_verified'] is False
        assert evidence['original_endpoint_states_omit_distance'] is True
        assert evidence['mac_block_sums_match_window'] is True


@pytest.mark.parametrize('number,be,codel,tsq',[(59,(1550,3100),(10000,50000),(262144,131072)),
                                            (60,(1520,3040),(8000,40000),(245760,122880))])
def test_retry64_rc24_and_asymmetric_endpoint_profiles_are_literal_source_fields(typed60,number,be,codel,tsq):
    row=next(r for r in typed60 if r.round_id==f'R{number}' and '_iter1_' in r.iteration)
    assert (row.short_retry_limit,row.long_retry_limit)==(6,4)
    assert row.ap_policy.aql_by_ac[2]==be
    assert row.cpe_policy.aql_by_ac[2]==(2100,4200)
    assert row.ap_policy.rc_per_thresh==row.cpe_policy.rc_per_thresh==24
    assert (row.ap_policy.fq_target_us,row.ap_policy.fq_interval_us)==codel
    assert (row.ap_policy.tcp_limit_output_bytes,row.ap_policy.tcp_notsent_lowat)==tsq
    assert (row.cpe_policy.fq_target_us,row.cpe_policy.fq_interval_us)==((12000,60000) if number==59 else (10000,50000))


def test_new_explicit_context_does_not_retroactively_fill_unknown_old_context(corpus60):
    rows=corpus60[0]['records']
    assert all(r['distance_meters'] is r['coverage_class'] is None for r in rows if r['round_id']=='R50')
    assert len(live.load_all60_measurements(include_auxiliary=False)[0])==218
    assert len(live.load_all56_measurements(include_auxiliary=False)[0])==210


def test_new_manifest_has_exactly_twelve_inputs_and_future_round_is_never_read(tmp_path):
    manifest=live._inputs60()
    assert len(manifest['entries'])==12 and {e['round'] for e in manifest['entries']}==set(range(57,61))
    future=tmp_path/'lap120_loco195_r61_forbidden.json'
    with pytest.raises(ValueError,match='not an authenticated'):list(live._campaign60([future]))
    assert not future.exists()


@pytest.mark.parametrize('scope',[55,57,61,True,60.0,'60'])
def test_latest_dataset_scope_cannot_widen_to_future_or_accept_untyped_scope(scope):
    with pytest.raises(ValueError):live.load_live_dataset(through_round=scope)
    with pytest.raises(ValueError):live.load_crossed_dataset(through_round=scope)


@pytest.mark.parametrize('field,value',[('coverage_class',1),('distance_m',3000),('slot_time_us',10),
                                        ('ack_timeout_us',19),('slot_time_us',True)])
def test_class_zero_context_rejects_contradictory_or_untyped_declarations(field,value):
    payload=old.local_json(live.R57_TO_R60_RECEIPTS[0]);item=payload['iterations'][0]
    changed=deepcopy(payload);changed[field]=value
    with pytest.raises(ValueError):live._context(57,changed,item,catalog=live.ROUND60_SPECS)


def test_latest_source_recipes_are_never_imported(monkeypatch):
    import builtins
    original=builtins.__import__
    def bounded(name,*args,**kwargs):
        if name.startswith(('tools.bench','paramiko')):raise AssertionError('Recipe/device import forbidden')
        return original(name,*args,**kwargs)
    monkeypatch.setattr(builtins,'__import__',bounded)
    assert len(live.load_live_dataset(through_round=60)['records'])==220


@pytest.fixture(scope='module')
def corpus65():
    return live.load_live_dataset(through_round=65), live.load_crossed_dataset(through_round=65)


@pytest.fixture(scope='module')
def typed65():
    return live.load_all65_measurements()[0]


def test_as_default_corpus_includes_65_rounds_with_unchanged_r60_prefix(corpus65):
    data, blocks = corpus65
    prior = live._sealed60(live.R60_RECORDS_OUTPUT)
    old_blocks = live._sealed60(live.R60_BLOCKS_OUTPUT)
    assert data['schema_version'] == 12
    assert len(data['records']) == data['observed_record_count'] == 230
    assert (data['primary_window_count'], data['auxiliary_window_count']) == (228, 2)
    assert set(data['round_counts']) == {f'R{i}' for i in range(1, 66)}
    assert len(blocks['crossed']) == 1276
    assert len({(b['round_id'], b['block_index']) for b in blocks['crossed']}) == 550
    assert len(blocks['sequential']) == 16
    assert data['records'][:220] == prior['records']
    assert blocks['crossed'][:1116] == old_blocks['crossed']
    assert blocks['sequential'] == old_blocks['sequential']
    assert data['automatic_execution_allowed'] is data['physical_acceptance_claim'] is False


def test_as_both_historical_corpus_interfaces_replay_byteidentically():
    encode = lambda value: (json.dumps(value, indent=2, allow_nan=False)+'\n').encode()
    for revision in (56, 60):
        records = getattr(live, f'R{revision}_RECORDS_OUTPUT')
        blocks = getattr(live, f'R{revision}_BLOCKS_OUTPUT')
        assert encode(live.load_live_dataset(through_round=revision)) == records.read_bytes()
        assert encode(live.load_crossed_dataset(through_round=revision)) == blocks.read_bytes()
    assert encode(live.load_r1_to_r60_dataset()) == live.R60_RECORDS_OUTPUT.read_bytes()


@pytest.mark.parametrize('number,distance,coverage,slot,ack,flows', [
    (61,3000,6,27,54,6), (62,6000,13,48,96,6), (63,100,0,9,18,8),
    (64,100,0,9,18,4), (65,100,0,9,18,6)])
def test_as_ten_new_arms_exact_means_shared_timing_flow_and_saved_health(typed65, number, distance, coverage, slot, ack, flows):
    rows = [r for r in typed65 if r.round_id == f'R{number}']
    assert len(rows) == 2
    for row in rows:
        assert (row.distance_meters, row.coverage_class, row.active_flow_count, row.bidirectional) == (distance, coverage, flows, True)
        assert row.workload_regime == f'bidir_{flows}flow'
        assert row.ap_policy.distance_meters == row.cpe_policy.distance_meters == distance
        assert len(row.rtts_ms) == 160
        assert row.packet_loss_pct == row.station_drops == 0
        assert row.restoration_verified is row.raw_rtts_matches_blocks is True
        assert list(row.dyadic_mean_audit['fraction_deltas'].values()) == ['0']*4
        assert list(row.dyadic_mean_audit['ulp_errors'].values()) == [0]*4
        e = row.certified_wds_evidence
        assert (e['slot_time_us'], e['ack_timeout_us']) == (slot, ack)
        assert e['slot_ack_source'] == 'SHARED_PAYLOAD_TREATMENT_KNOBS'
        assert e['effective_timing_independently_verified'] is e['physical_distance_verified'] is False
        assert e['mac_block_sums_match_window'] is True
        assert e['original_endpoint_states_omit_distance'] is True


@pytest.mark.parametrize('number', [61,62,63,64,65])
def test_as_joint_package_literal_retry_rc_and_asymmetric_codel(typed65, number):
    row = next(r for r in typed65 if r.round_id == f'R{number}' and '_iter1_' in r.iteration)
    assert (row.short_retry_limit, row.long_retry_limit) == ((5,4) if number == 65 else (6,4))
    assert row.ap_policy.rc_per_thresh == row.cpe_policy.rc_per_thresh == (22 if number == 65 else 24)
    assert row.ap_policy.aql_by_ac[2] == (1520,3040)
    assert row.cpe_policy.aql_by_ac[2] == (2100,4200)
    assert (row.ap_policy.fq_target_us, row.ap_policy.fq_interval_us) == (8000,40000)
    assert (row.cpe_policy.fq_target_us, row.cpe_policy.fq_interval_us) == (10000,50000)


@pytest.mark.parametrize('number', [61,62,63,64,65])
@pytest.mark.parametrize('where', ['root','iteration','knobs'])
def test_as_missing_or_changed_shared_slot_declaration_rejected(number, where):
    p = old.local_json(live.R61_TO_R65_RECEIPTS[number-61])
    item = p['iterations'][0]
    declared = p if where == 'root' else item if where == 'iteration' else item['candidate_knobs']
    declared.pop('slot_time_us')
    with pytest.raises(ValueError):
        live._context(number, p, item, catalog=live.ROUND65_SPECS)


def test_as_frozen_manifest_and_future66_fail_before_content_reads(tmp_path, monkeypatch):
    m = live._inputs65()
    assert len(m['entries']) == 15 and {e['round'] for e in m['entries']} == set(range(61,66))
    future = tmp_path/'lap120_loco195_r66_forbidden.json'
    native = Path.read_bytes
    def bounded(path):
        if path == future: raise AssertionError('future content read')
        return native(path)
    monkeypatch.setattr(Path, 'read_bytes', bounded)
    with pytest.raises(ValueError, match='not an authenticated'):
        list(live._campaign65([future]))
    assert not future.exists()


@pytest.mark.parametrize('revision', [61,64,66,True,65.0,'65'])
def test_as_only_explicit_56_60_65_revisions_are_permitted(revision):
    with pytest.raises(ValueError): live.load_live_dataset(through_round=revision)
    with pytest.raises(ValueError): live.load_crossed_dataset(through_round=revision)


def test_as_typed_revision_counts_and_old_unknown_context_stays_unknown(typed65):
    assert len(typed65) == 230
    assert len(live.load_all65_measurements(include_auxiliary=False)[0]) == 228
    assert len(live.load_all60_measurements()[0]) == 220
    assert len(live.load_all56_measurements()[0]) == 212
    assert all(r.coverage_class is r.distance_meters is None for r in typed65 if r.round_id == 'R50')


@pytest.fixture(scope='module')
def corpus70():
    return live.load_live_dataset(through_round=70), live.load_crossed_dataset(through_round=70)


@pytest.fixture(scope='module')
def typed70():
    return live.load_all70_measurements()[0]


def test_aw_default_corpus_has_70_rounds_and_preserves_all_230_prior_records(corpus70):
    data, blocks = corpus70
    prior = live._sealed65(live.R65_RECORDS_OUTPUT)
    old_blocks = live._sealed65(live.R65_BLOCKS_OUTPUT)
    assert data['schema_version'] == 13
    assert len(data['records']) == data['observed_record_count'] == 240
    assert (data['primary_window_count'], data['auxiliary_window_count']) == (238,2)
    assert set(data['round_counts']) == {f'R{i}' for i in range(1,71)}
    assert (len(blocks['crossed']),len(blocks['sequential'])) == (1436,16)
    assert len({(b['round_id'],b['block_index']) for b in blocks['crossed']}) == 630
    assert data['records'][:230] == prior['records']
    assert blocks['crossed'][:1276] == old_blocks['crossed']
    assert blocks['sequential'] == old_blocks['sequential']
    assert data['automatic_execution_allowed'] is data['physical_acceptance_claim'] is False


def test_aw_three_historical_serialized_interfaces_are_byteidentical():
    encode=lambda value:(json.dumps(value,indent=2,allow_nan=False)+'\n').encode()
    for revision in (56,60,65):
        assert encode(live.load_live_dataset(through_round=revision)) == getattr(live,f'R{revision}_RECORDS_OUTPUT').read_bytes()
        assert encode(live.load_crossed_dataset(through_round=revision)) == getattr(live,f'R{revision}_BLOCKS_OUTPUT').read_bytes()
    assert encode(live.load_r1_to_r65_dataset()) == live.R65_RECORDS_OUTPUT.read_bytes()


@pytest.mark.parametrize('number,distance,coverage,slot,ack,flows',[
    (66,100,0,9,18,2),(67,100,0,9,18,8),(68,4500,10,39,78,6),
    (69,9000,20,69,138,6),(70,4500,10,39,78,6)])
def test_aw_ten_new_arms_have_literal_shared_context_exact_means_and_zero_loss(typed70,number,distance,coverage,slot,ack,flows):
    rows=[r for r in typed70 if r.round_id==f'R{number}']
    assert len(rows)==2
    for row in rows:
        assert (row.distance_meters,row.coverage_class,row.active_flow_count,row.bidirectional)==(distance,coverage,flows,True)
        assert row.workload_regime==f'bidir_{flows}flow'
        assert row.ap_policy.distance_meters==row.cpe_policy.distance_meters==distance
        assert len(row.rtts_ms)==160 and row.packet_loss_pct==row.station_drops==0
        assert row.restoration_verified is row.raw_rtts_matches_blocks is True
        assert list(row.dyadic_mean_audit['fraction_deltas'].values())==['0']*4
        assert list(row.dyadic_mean_audit['ulp_errors'].values())==[0]*4
        e=row.certified_wds_evidence
        assert (e['slot_time_us'],e['ack_timeout_us'])==(slot,ack)
        assert e['slot_ack_source']=='SHARED_PAYLOAD_TREATMENT_KNOBS'
        assert e['mac_block_sums_match_window'] is True
        assert e['physical_distance_verified'] is e['effective_timing_independently_verified'] is False
        assert e['frozen_recipe_distance_application_declared'] is False
        assert e['frozen_recipe_coverage_command_declared'] is True
        assert e['coverage_command_execution_or_readback_independently_verified'] is False


@pytest.mark.parametrize('number,be,codel,cpe_codel',[(66,1520,8000,10000),(67,1480,7000,9000),(68,1520,8000,10000),(69,1520,8000,10000),(70,1560,8000,10000)])
def test_aw_package_preserves_cochanged_aql_codel_airtime_and_retry(typed70,number,be,codel,cpe_codel):
    row=next(r for r in typed70 if r.round_id==f'R{number}' and '_iter1_' in r.iteration)
    assert (row.short_retry_limit,row.long_retry_limit)==(6,4)
    assert row.ap_policy.rc_per_thresh==row.cpe_policy.rc_per_thresh==24
    assert row.ap_policy.aql_by_ac[2]==(be,2*be)
    assert row.cpe_policy.aql_by_ac[2]==(2100,4200)
    assert (row.ap_policy.fq_target_us,row.ap_policy.fq_interval_us)==(codel,5*codel)
    assert (row.cpe_policy.fq_target_us,row.cpe_policy.fq_interval_us)==(cpe_codel,5*cpe_codel)


@pytest.mark.parametrize('number',[66,67,68,69,70])
@pytest.mark.parametrize('where',['root','iteration','knobs'])
def test_aw_missing_slot_at_any_shared_declaration_is_rejected(number,where):
    p=old.local_json(live.R66_TO_R70_RECEIPTS[number-66])
    item=p['iterations'][0]
    declared=p if where=='root' else item if where=='iteration' else item['candidate_knobs']
    declared.pop('slot_time_us')
    with pytest.raises(ValueError):
        live._context(number,p,item,catalog=live.ROUND70_SPECS)


@pytest.mark.parametrize('field,value',[('coverage_class',True),('coverage_class',10.0),('distance_m','4500'),('distance_m',None),('slot_time_us',39.0),('slot_time_us',True),('ack_timeout_us',78.0),('ack_timeout_us',79)])
def test_aw_new_coverage_class_context_requires_exact_typed_values(field,value):
    p=old.local_json(live.R66_TO_R70_RECEIPTS[2])
    p[field]=value
    with pytest.raises(ValueError):
        live._context(68,p,p['iterations'][0],catalog=live.ROUND70_SPECS)


def test_aw_frozen_manifest_and_future71_reject_before_any_content_read(tmp_path,monkeypatch):
    manifest=live._inputs70()
    assert len(manifest['entries'])==15 and {e['round'] for e in manifest['entries']}==set(range(66,71))
    future=tmp_path/'lap120_loco195_r71_forbidden.json'
    native=Path.read_bytes
    def bounded(path):
        if path==future:raise AssertionError('future content read')
        return native(path)
    monkeypatch.setattr(Path,'read_bytes',bounded)
    with pytest.raises(ValueError,match='not an authenticated'):
        list(live._campaign70([future]))
    assert not future.exists()


@pytest.mark.parametrize('revision',[66,69,71,True,70.0,'70'])
def test_aw_untyped_or_unlisted_latest_revisions_are_rejected(revision):
    with pytest.raises(ValueError):live.load_live_dataset(through_round=revision)
    with pytest.raises(ValueError):live.load_crossed_dataset(through_round=revision)


def test_aw_typed_counts_and_historical_unknown_timing_remain_unchanged(typed70):
    assert len(typed70)==240
    assert len(live.load_all70_measurements(include_auxiliary=False)[0])==238
    assert len(live.load_all65_measurements()[0])==230
    assert all(r.distance_meters is r.coverage_class is None for r in typed70 if r.round_id=='R50')


@pytest.mark.parametrize('number,coverage',[(68,10),(69,20),(70,10)])
def test_aw_new_coverage_command_must_be_in_frozen_recipe(number,coverage):
    campaign=list(live._campaign70([live.R66_TO_R70_RECEIPTS[number-66]]))
    entry=list(campaign[0])
    entry[-1]=entry[-1].replace(f'iw phy phy0 set coverage {coverage}', 'REMOVED_COVERAGE_COMMAND')
    with pytest.raises(ValueError,match='frozen recipe command'):
        live._convert_campaign([tuple(entry)],catalog=live.ROUND70_SPECS,max_round=70)


@pytest.mark.parametrize('number',[66,67])
def test_aw_class_zero_recipe_command_flag_is_derived_from_literal_source(number):
    campaign=list(live._campaign70([live.R66_TO_R70_RECEIPTS[number-66]]))
    values,_,_=live._convert_campaign(campaign,catalog=live.ROUND70_SPECS,max_round=70)
    assert all(r.certified_wds_evidence['frozen_recipe_coverage_command_declared'] is True for r in values)
    entry=list(campaign[0])
    entry[-1]=entry[-1].replace('iw phy phy0 set coverage 0 2>/dev/null || true','REMOVED_COVERAGE_ZERO_LITERAL')
    values,_,_=live._convert_campaign([tuple(entry)],catalog=live.ROUND70_SPECS,max_round=70)
    assert all(r.certified_wds_evidence['frozen_recipe_coverage_command_declared'] is False for r in values)


@pytest.fixture(scope='module')
def corpus75():
    return live.load_live_dataset(through_round=75), live.load_crossed_dataset(through_round=75)


@pytest.fixture(scope='module')
def typed75():
    return live.load_all75_measurements()[0]


def test_ba_default_corpus_has_75_rounds_and_preserves_all_240_prior_records(corpus75):
    data,blocks=corpus75
    prior=live._sealed70(live.R70_RECORDS_OUTPUT)
    old_blocks=live._sealed70(live.R70_BLOCKS_OUTPUT)
    assert data['schema_version']==14
    assert len(data['records'])==data['observed_record_count']==250
    assert (data['primary_window_count'],data['auxiliary_window_count'])==(248,2)
    assert set(data['round_counts'])=={f'R{i}' for i in range(1,76)}
    assert (len(blocks['crossed']),len(blocks['sequential']))==(1596,16)
    assert len({(b['round_id'],b['block_index']) for b in blocks['crossed']})==710
    assert data['records'][:240]==prior['records']
    assert blocks['crossed'][:1436]==old_blocks['crossed']
    assert blocks['sequential']==old_blocks['sequential']
    assert data['automatic_execution_allowed'] is data['physical_acceptance_claim'] is False


@pytest.mark.parametrize('revision',[56,60,65,70])
def test_ba_four_historical_serialized_interfaces_are_byteidentical(revision):
    encode=lambda value:(json.dumps(value,indent=2,allow_nan=False)+'\n').encode()
    assert encode(live.load_live_dataset(through_round=revision))==getattr(live,f'R{revision}_RECORDS_OUTPUT').read_bytes()
    assert encode(live.load_crossed_dataset(through_round=revision))==getattr(live,f'R{revision}_BLOCKS_OUTPUT').read_bytes()
    if revision==70:
        assert encode(live.load_r1_to_r70_dataset())==live.R70_RECORDS_OUTPUT.read_bytes()


@pytest.mark.parametrize('number,distance,coverage,slot,ack,flows',[
    (71,100,0,9,18,2),(72,100,0,9,18,8),(73,12000,27,90,180,6),
    (74,100,0,9,18,8),(75,15000,33,108,216,6)])
def test_ba_all_new_arms_keep_exact_means_raw_pings_and_declared_context(typed75,number,distance,coverage,slot,ack,flows):
    rows=[r for r in typed75 if r.round_id==f'R{number}']
    assert len(rows)==2
    for r in rows:
        assert (r.distance_meters,r.coverage_class,r.active_flow_count,r.bidirectional)==(distance,coverage,flows,True)
        assert r.workload_regime==f'bidir_{flows}flow'
        assert r.ap_policy.distance_meters==r.cpe_policy.distance_meters==distance
        assert len(r.rtts_ms)==160 and r.packet_loss_pct==r.station_drops==0
        assert r.restoration_verified is r.raw_rtts_matches_blocks is True
        assert list(r.dyadic_mean_audit['fraction_deltas'].values())==['0']*4
        assert list(r.dyadic_mean_audit['ulp_errors'].values())==[0]*4
        e=r.certified_wds_evidence
        assert (e['slot_time_us'],e['ack_timeout_us'])==(slot,ack)
        assert e['slot_ack_source']=='SHARED_PAYLOAD_TREATMENT_KNOBS'
        assert e['mac_block_sums_match_window'] is True
        assert e['physical_distance_verified'] is e['effective_timing_independently_verified'] is False
        assert e['frozen_recipe_coverage_command_declared'] is True
        assert e['coverage_command_execution_or_readback_independently_verified'] is False


@pytest.mark.parametrize('number,ap_be,cpe_be,ap_codel,cpe_codel,vo,vo_high,airtime',[
    (71,1350,2200,6000,10000,500,1100,1),(72,1520,2100,7000,9000,500,1100,1),
    (73,1520,2100,8000,10000,500,1100,1),(74,1510,2150,5000,7000,900,1800,3),
    (75,1520,2100,8000,10000,500,1100,1)])
def test_ba_complete_endpoint_packages_include_vo_and_cpe_codel(typed75,number,ap_be,cpe_be,ap_codel,cpe_codel,vo,vo_high,airtime):
    r=next(r for r in typed75 if r.round_id==f'R{number}' and '_iter1_' in r.iteration)
    assert (r.short_retry_limit,r.long_retry_limit,r.airtime_flags)==(6,4,airtime)
    assert r.ap_policy.rc_per_thresh==r.cpe_policy.rc_per_thresh==24
    assert r.ap_policy.aql_by_ac[0]==r.cpe_policy.aql_by_ac[0]==(vo,vo_high)
    assert r.ap_policy.aql_by_ac[2]==(ap_be,2*ap_be)
    assert r.cpe_policy.aql_by_ac[2]==(cpe_be,2*cpe_be)
    assert (r.ap_policy.fq_target_us,r.ap_policy.fq_interval_us)==(ap_codel,5*ap_codel)
    assert (r.cpe_policy.fq_target_us,r.cpe_policy.fq_interval_us)==(cpe_codel,5*cpe_codel)


@pytest.mark.parametrize('number',[71,72,73,74,75])
@pytest.mark.parametrize('where',['root','iteration','knobs'])
@pytest.mark.parametrize('field',['distance_m','coverage_class','slot_time_us','ack_timeout_us'])
def test_ba_every_shared_context_field_is_required(number,where,field):
    p=old.local_json(live.R71_TO_R75_RECEIPTS[number-71]);item=p['iterations'][0]
    d=p if where=='root' else item if where=='iteration' else item['candidate_knobs']
    d.pop(field)
    with pytest.raises(ValueError):live._context(number,p,item,catalog=live.ROUND75_SPECS)


@pytest.mark.parametrize('number',[73,75])
@pytest.mark.parametrize('field,value',[('coverage_class',True),('coverage_class',27.0),('distance_m','12000'),
    ('distance_m',None),('slot_time_us',90.0),('slot_time_us',True),('ack_timeout_us',180.0),('ack_timeout_us',179)])
def test_ba_new_distance_classes_require_exact_typed_shared_values(number,field,value):
    p=old.local_json(live.R71_TO_R75_RECEIPTS[number-71]);p[field]=value
    with pytest.raises(ValueError):live._context(number,p,p['iterations'][0],catalog=live.ROUND75_SPECS)


def test_ba_future76_is_rejected_before_any_content_read(tmp_path,monkeypatch):
    manifest=live._inputs75()
    assert len(manifest['entries'])==15 and {e['round'] for e in manifest['entries']}==set(range(71,76))
    future=tmp_path/'lap120_loco195_r76_forbidden.json';native=Path.read_bytes
    def bounded(path):
        if path==future:raise AssertionError('future content read')
        return native(path)
    monkeypatch.setattr(Path,'read_bytes',bounded)
    with pytest.raises(ValueError,match='not an authenticated'):list(live._campaign75([future]))
    assert not future.exists()


@pytest.mark.parametrize('revision',[74,76,True,75.0,'75'])
def test_ba_untyped_or_unlisted_latest_revisions_stay_rejected(revision):
    with pytest.raises(ValueError):live.load_live_dataset(through_round=revision)
    with pytest.raises(ValueError):live.load_crossed_dataset(through_round=revision)


def test_ba_typed_counts_and_legacy_unknown_context_are_unchanged(typed75):
    assert len(typed75)==250
    assert len(live.load_all75_measurements(include_auxiliary=False)[0])==248
    assert len(live.load_all70_measurements()[0])==240
    assert all(r.distance_meters is r.coverage_class is None for r in typed75 if r.round_id=='R50')


@pytest.mark.parametrize('number,coverage',[(73,27),(75,33)])
def test_ba_new_coverage_command_must_exist_in_frozen_recipe(number,coverage):
    campaign=list(live._campaign75([live.R71_TO_R75_RECEIPTS[number-71]]));entry=list(campaign[0])
    entry[-1]=entry[-1].replace(f'iw phy phy0 set coverage {coverage}','REMOVED_COVERAGE_COMMAND')
    with pytest.raises(ValueError,match='frozen recipe command'):
        live._convert_campaign([tuple(entry)],catalog=live.ROUND75_SPECS,max_round=75)


@pytest.mark.parametrize('number',[71,72,74])
def test_ba_class_zero_command_flag_does_not_invent_execution(number):
    campaign=list(live._campaign75([live.R71_TO_R75_RECEIPTS[number-71]]))
    values,_,_=live._convert_campaign(campaign,catalog=live.ROUND75_SPECS,max_round=75)
    assert all(r.certified_wds_evidence['frozen_recipe_coverage_command_declared'] for r in values)
    entry=list(campaign[0]);entry[-1]=entry[-1].replace('iw phy phy0 set coverage 0 2>/dev/null || true','REMOVED_COVERAGE_ZERO_LITERAL')
    values,_,_=live._convert_campaign([tuple(entry)],catalog=live.ROUND75_SPECS,max_round=75)
    assert all(r.certified_wds_evidence['frozen_recipe_coverage_command_declared'] is False for r in values)
    assert all(r.certified_wds_evidence['effective_timing_independently_verified'] is False for r in values)


@pytest.mark.parametrize('field,value',[
    ('round_id','R74'),('distance_meters',14999),('active_flow_count',8),
    ('distance_meters',15000.0),('active_flow_count',6.0),('bidirectional',False),
    ('workload_regime','bidir_8flow'),('coverage_class',32),('coverage_class',34),('coverage_class',33.0)])
def test_ba_declared_class33_has_no_legacy_or_other_context_escape(typed75,field,value):
    row=next(r for r in typed75 if r.round_id=='R75')
    with pytest.raises(ValueError):replace(row,**{field:value})


@pytest.mark.parametrize('field,value',[
    ('coverage_class',27),('slot_time_us',None),('ack_timeout_us',215),('slot_ack_source','UNKNOWN'),
    ('coverage_class',33.0),('slot_time_us',108.0),('ack_timeout_us',216.0),
    ('physical_distance_verified',True),('effective_timing_independently_verified',True),
    ('coverage_command_execution_or_readback_independently_verified',True),
    ('frozen_recipe_coverage_command_declared',False)])
def test_ba_declared_class33_requires_shared_unknown_runtime_provenance(typed75,field,value):
    row=next(r for r in typed75 if r.round_id=='R75')
    evidence=deepcopy(row.certified_wds_evidence);evidence[field]=value
    with pytest.raises(ValueError):replace(row,certified_wds_evidence=evidence)


def test_ba_legacy_dataclass_does_not_admit_above31_coverage(typed75):
    row=next(r for r in typed75 if r.round_id=='R70')
    for coverage in (32,33,34,255):
        with pytest.raises(ValueError):replace(row,coverage_class=coverage)


def test_be_default_corpus_has_80_rounds_without_relabeling_saved_history():
    data,blocks=live.load_live_dataset(through_round=80),live.load_crossed_dataset(through_round=80)
    assert len(data['records'])==260
    assert data['observed_record_count']==260
    assert len(blocks['crossed'])==1756
    assert len({(b['round_id'],b['block_index'])for b in blocks['crossed']})==790
    assert len(blocks['sequential'])==16
    assert data['records'][:250]==live._sealed75(live.R75_RECORDS_OUTPUT)['records']
    assert data['records'][:250]==json.loads(json.dumps(live.load_live_dataset(through_round=75)))['records']
    assert blocks['crossed'][:1596]==live.load_crossed_dataset(through_round=75)['crossed']
    assert set(data['round_counts'])=={f'R{i}'for i in range(1,81)}


def test_be_explicit75_interface_and_typed80_api_are_additive():
    assert callable(getattr(live,'load_r1_to_r75_dataset',None))
    assert callable(getattr(live,'load_all80_measurements',None))
    assert callable(getattr(live,'load_all80_block_observations',None))
    encode=lambda value:(json.dumps(value,indent=2,allow_nan=False)+'\n').encode()
    assert encode(live.load_r1_to_r75_dataset())==live.R75_RECORDS_OUTPUT.read_bytes()
    rows,refs=live.load_all80_measurements()
    assert len(rows)==260 and len(refs)==80
    assert len(live.load_all80_measurements(include_auxiliary=False)[0])==258


@pytest.fixture(scope='module')
def corpus80():
    return live.load_live_dataset(through_round=80),live.load_crossed_dataset(through_round=80)


@pytest.fixture(scope='module')
def typed80():
    return live.load_all80_measurements()[0]


@pytest.mark.parametrize('revision',[56,60,65,70,75])
def test_be_all_five_historical_serialized_interfaces_are_byteidentical(revision):
    encode=lambda v:(json.dumps(v,indent=2,allow_nan=False)+'\n').encode()
    assert encode(live.load_live_dataset(through_round=revision))==getattr(live,f'R{revision}_RECORDS_OUTPUT').read_bytes()
    assert encode(live.load_crossed_dataset(through_round=revision))==getattr(live,f'R{revision}_BLOCKS_OUTPUT').read_bytes()


@pytest.mark.parametrize('number,distance,coverage,slot,ack',[
    (76,1500,3,18,36),(77,7500,16,57,114),(78,10500,23,78,156),
    (79,13500,30,99,198),(80,7500,16,57,114)])
def test_be_new_source_contexts_exact_means_chronology_and_MACs_are_retained(typed80,number,distance,coverage,slot,ack):
    own=[r for r in typed80 if r.round_id==f'R{number}']
    assert len(own)==2
    for row in own:
        assert (row.distance_meters,row.coverage_class,row.active_flow_count,row.bidirectional)==(distance,coverage,6,True)
        assert row.ap_policy.distance_meters==row.cpe_policy.distance_meters==distance
        assert len(row.rtts_ms)==160 and row.raw_rtts_matches_blocks is True
        assert row.packet_loss_pct==row.station_drops==0 and row.restoration_verified is True
        assert row.dyadic_mean_audit['all_fraction_zero'] is True
        assert row.dyadic_mean_audit['all_zero_ulp'] is True
        e=row.certified_wds_evidence
        assert (e['slot_time_us'],e['ack_timeout_us'])==(slot,ack)
        assert e['mac_block_sums_match_window'] is True
        assert e['counter_interface']=='phy0-ap0.sta1'
        assert e['frozen_recipe_coverage_command_declared'] is e['frozen_recipe_coverage_reset0_declared'] is True
        for field in ('physical_distance_verified','effective_timing_independently_verified',
                      'coverage_command_execution_or_readback_independently_verified','coverage_reset_execution_or_readback_independently_verified'):
            assert e[field]is False


def test_be_R76_is_recorded_1500m_not_narrative_4500m_and_R77_R80_are_not_identical_packages(typed80):
    targets={r.round_id:r for r in typed80 if r.round_id in {'R76','R77','R80'} and '_iter1_' in r.iteration}
    assert (targets['R76'].distance_meters,targets['R76'].coverage_class)==(1500,3)
    assert targets['R77'].distance_meters==targets['R80'].distance_meters==7500
    assert targets['R77'].policy_key!=targets['R80'].policy_key
    assert targets['R77'].ap_policy.aql_by_ac[2]==(1520,3040)
    assert targets['R80'].ap_policy.aql_by_ac[2]==(1540,3080)
    assert (targets['R77'].airtime_flags,targets['R80'].airtime_flags)==(1,3)


@pytest.mark.parametrize('number',[76,77,78,79,80])
@pytest.mark.parametrize('where',['root','iteration','knobs'])
@pytest.mark.parametrize('field',['distance_m','coverage_class','slot_time_us','ack_timeout_us'])
@pytest.mark.parametrize('defect',['missing','boolean','fractional','conflict'])
def test_be_all_shared_context_fields_reject_missing_and_coercion(number,where,field,defect):
    payload=old.local_json(live.R76_TO_R80_RECEIPTS[number-76]);item=payload['iterations'][0]
    target=payload if where=='root' else item if where=='iteration' else item['candidate_knobs']
    if defect=='missing':target.pop(field)
    elif defect=='boolean':target[field]=True
    elif defect=='fractional':target[field]=float(target[field])
    else:target[field]+=1
    with pytest.raises(ValueError):live._context(number,payload,item,catalog=live.ROUND80_SPECS)


@pytest.mark.parametrize('number,coverage',[(76,3),(77,16),(78,23),(79,30),(80,16)])
@pytest.mark.parametrize('kind',['set','reset'])
def test_be_new_coverage_and_reset_literals_are_required_but_never_execution_proof(number,coverage,kind):
    campaign=list(live._campaign80([live.R76_TO_R80_RECEIPTS[number-76]]));entry=list(campaign[0])
    literal=f'iw phy phy0 set coverage {coverage if kind=="set" else 0} 2>/dev/null || true'
    assert literal in entry[-1]
    entry[-1]=entry[-1].replace(literal,'REMOVED_REQUIRED_DECLARATION')
    with pytest.raises(ValueError,match='frozen'):
        live._convert_campaign([tuple(entry)],catalog=live.ROUND80_SPECS,max_round=80)


def test_be_block_retry_denominators_remain_typed_positive_and_per_block_not_window_imputed(corpus80):
    _,blocks=corpus80
    new=[b for b in blocks['crossed']if int(b['round_id'][1:])>=76]
    assert len(new)==160
    for block in new:
        assert block['counter_interface']=='phy0-ap0.sta1'
        assert type(block['mac_tx_packets_delta'])is int and block['mac_tx_packets_delta']>0
        assert type(block['mac_tx_retries_delta'])is int and block['mac_tx_retries_delta']>=0
        assert block['mac_retry_rate']==block['mac_tx_retries_delta']/block['mac_tx_packets_delta']
    entry=list(next(live._campaign80([live.R76_TO_R80_RECEIPTS[0]])))
    entry[1]=deepcopy(entry[1]);entry[1]['iterations'][0]['repetition_blocks'][0]['mac_tx_packets_delta']=0
    rows,retained,_=live._convert_campaign([tuple(entry)],catalog=live.ROUND80_SPECS,max_round=80)
    assert retained[0]['mac_tx_packets_delta']==0
    assert retained[0]['mac_retry_rate_from_counters'] is None
    assert rows[0].certified_wds_evidence['mac_counters_valid'] is False
    assert rows[0].certified_wds_evidence['mac_block_sums_match_window'] is False
    for field,value in [('mac_tx_packets_delta',True),('mac_tx_retries_delta',False)]:
        entry=list(next(live._campaign80([live.R76_TO_R80_RECEIPTS[0]])))
        entry[1]=deepcopy(entry[1]);entry[1]['iterations'][0]['repetition_blocks'][0][field]=value
        with pytest.raises(ValueError):live._convert_campaign([tuple(entry)],catalog=live.ROUND80_SPECS,max_round=80)


def test_be_future81_and_old75_campaign_boundaries_reject_before_content(tmp_path,monkeypatch):
    future=tmp_path/'lap120_loco195_r81_forbidden.json'
    newpath=live.R76_TO_R80_RECEIPTS[0];native=Path.read_bytes
    def bounded(path):
        if path in (future,newpath):raise AssertionError('Out-of-selected-campaign content read')
        return native(path)
    monkeypatch.setattr(Path,'read_bytes',bounded)
    with pytest.raises(ValueError,match='not an authenticated'):list(live._campaign75([newpath]))
    monkeypatch.setattr(Path,'read_bytes',lambda path:(_ for _ in ()).throw(AssertionError('future content read')) if path==future else native(path))
    with pytest.raises(ValueError,match='not an authenticated'):list(live._campaign80([future]))
    assert not future.exists()


@pytest.mark.parametrize('revision',[76,79,81,True,80.0,'80'])
def test_be_revision_selectors_are_explicit_and_typed(revision):
    with pytest.raises(ValueError):live.load_live_dataset(through_round=revision)
    with pytest.raises(ValueError):live.load_crossed_dataset(through_round=revision)


def test_be_manifest_and_legacy_unknown_timing_remain_explicit(typed80):
    manifest=live._inputs80()
    assert len(manifest['entries'])==15
    assert {e['round']for e in manifest['entries']}==set(range(76,81))
    assert all(r.distance_meters is r.coverage_class is None for r in typed80 if r.round_id=='R50')
    assert len(live.load_all75_measurements()[0])==250


def test_bi_latest86_adds_12_arms_without_changing260_saved_records():
    data,blocks=live.load_live_dataset(through_round=86),live.load_crossed_dataset(through_round=86)
    assert len(data['records'])==272
    assert len(blocks['crossed'])==1948
    assert len({(b['round_id'],b['block_index'])for b in blocks['crossed']})==886


def test_bi_explicit80_and_typed86_apis_exist():
    assert callable(getattr(live,'load_r1_to_r80_dataset',None))
    assert callable(getattr(live,'load_all86_measurements',None))
    assert callable(getattr(live,'load_all86_block_observations',None))


@pytest.fixture(scope='module')
def corpus86():
    return live.load_live_dataset(through_round=86),live.load_crossed_dataset(through_round=86)


@pytest.fixture(scope='module')
def typed86():
    return live.load_all86_measurements()[0]


@pytest.mark.parametrize('revision',[56,60,65,70,75,80])
def test_bi_six_historical_record_and_block_serializations_remain_exact(revision):
    encode=lambda v:(json.dumps(v,indent=2,allow_nan=False)+'\n').encode()
    assert encode(live.load_live_dataset(through_round=revision))==getattr(live,f'R{revision}_RECORDS_OUTPUT').read_bytes()
    assert encode(live.load_crossed_dataset(through_round=revision))==getattr(live,f'R{revision}_BLOCKS_OUTPUT').read_bytes()


def test_bi_all260_records1756_rows_and16_sequential_are_unmodified(corpus86):
    data,blocks=corpus86
    prior=live._sealed80(live.R80_RECORDS_OUTPUT);prior_blocks=live._sealed80(live.R80_BLOCKS_OUTPUT)
    assert data['records'][:260]==prior['records']
    assert blocks['crossed'][:1756]==prior_blocks['crossed']
    assert blocks['sequential']==prior_blocks['sequential']
    assert (data['primary_window_count'],data['auxiliary_window_count'])==(270,2)
    assert len(data['source_refs'])==86
    assert len(live.load_all86_measurements(include_auxiliary=False)[0])==270


@pytest.mark.parametrize('number,regime,flows,bidir,distance,coverage,slot,ack',[
    (81,'unidir_dl_2flow',2,False,100,0,9,18),(82,'unidir_ul_2flow',2,False,100,0,9,18),
    (83,'bidir_4flow',4,True,3000,6,27,54),(84,'bidir_4flow',4,True,6000,13,48,96),
    (85,'bidir_6flow',6,True,7500,16,57,114),(86,'bidir_4flow',4,True,9000,20,69,138)])
def test_bi_source_direction_context_exact_means_and_chronology(typed86,number,regime,flows,bidir,distance,coverage,slot,ack):
    rows=[r for r in typed86 if r.round_id==f'R{number}'];assert len(rows)==2
    for r in rows:
        assert (r.workload_regime,r.active_flow_count,r.bidirectional)==(regime,flows,bidir)
        assert (r.distance_meters,r.coverage_class)==(distance,coverage)
        assert r.ap_policy.distance_meters==r.cpe_policy.distance_meters==distance
        assert type(r.active_flow_count)is int and type(r.bidirectional)is bool
        assert len(r.rtts_ms)==160 and r.raw_rtts_matches_blocks is True
        assert r.packet_loss_pct==r.station_drops==0 and r.restoration_verified is True
        assert r.dyadic_mean_audit['all_fraction_zero'] is r.dyadic_mean_audit['all_zero_ulp'] is True
        e=r.certified_wds_evidence
        assert e['exact_numpy_quantiles']is e['mac_counters_valid']is e['mac_block_sums_match_window']is True
        assert (e['slot_time_us'],e['ack_timeout_us'])==(slot,ack)
        assert e['frozen_recipe_distance_application_declared']is False
        assert e['frozen_recipe_coverage_command_declared']is e['frozen_recipe_coverage_reset0_declared']is True
        assert e['physical_distance_verified']is e['effective_timing_independently_verified']is False
        a=e['directional_applicability']
        assert a['regime']==regime and a['jain_applicable_for_QoE_inference']is bidir
        if not bidir:
            assert r.jain_fairness==.5
            assert a['active_direction_equals_total_every_arm_and_block']is True
            assert a['inactive_direction_zero_every_arm_and_block']is True


@pytest.mark.parametrize('number',[81,82,83,84,85,86])
@pytest.mark.parametrize('where',['root','iteration','knobs'])
@pytest.mark.parametrize('field',['distance_m','coverage_class','slot_time_us','ack_timeout_us'])
@pytest.mark.parametrize('defect',['missing','boolean','float','conflict'])
def test_bi_shared_timing_is_typed_and_complete(number,where,field,defect):
    payload=old.local_json(live.R81_TO_R86_RECEIPTS[number-81]);item=payload['iterations'][0]
    source=payload if where=='root' else item if where=='iteration' else item['candidate_knobs']
    if defect=='missing':source.pop(field)
    elif defect=='boolean':source[field]=True
    elif defect=='float':source[field]=float(source[field])
    else:source[field]+=1
    with pytest.raises(ValueError):live._context(number,payload,item,catalog=live.ROUND86_SPECS)


@pytest.mark.parametrize('number',[81,83,85])
@pytest.mark.parametrize('where',['root','iteration','knobs'])
@pytest.mark.parametrize('field',['traffic_regime','active_flow_count','bidirectional'])
@pytest.mark.parametrize('defect',['missing','wrong','coercion'])
def test_bi_shared_workload_flow_direction_never_defaults(number,where,field,defect):
    payload=old.local_json(live.R81_TO_R86_RECEIPTS[number-81]);item=payload['iterations'][0]
    source=payload if where=='root' else item if where=='iteration' else item['candidate_knobs']
    if defect=='missing':source.pop(field)
    elif defect=='wrong':source[field]='bidir_8flow' if field=='traffic_regime' else 8 if field=='active_flow_count' else not source[field]
    else:source[field]=[] if field=='traffic_regime' else float(source[field]) if field=='active_flow_count' else int(source[field])
    with pytest.raises(ValueError):live._context(number,payload,item,catalog=live.ROUND86_SPECS)


@pytest.mark.parametrize('number',[81,82])
def test_bi_source_steps_roundtrip_1based_to_0based_and_balance_8AB8BA(corpus86,number):
    _,blocks=corpus86;rows=[b for b in blocks['crossed']if b['round_id']==f'R{number}']
    assert len(rows)==32 and len({b['block_index']for b in rows})==16
    assert all(b['crossover_step']==b['source_step_in_block']-1 for b in rows)
    assert all(b['source_step_field']=='step_in_block' for b in rows)
    orders=[]
    for index in sorted({b['block_index']for b in rows}):
        own=sorted([b for b in rows if b['block_index']==index],key=lambda b:b['crossover_step'])
        assert [b['crossover_step']for b in own]==[0,1]
        assert [b['source_step_in_block']for b in own]==[1,2]
        orders.append(own[0]['treatment_id'])
    assert sorted(orders.count(t)for t in set(orders))==[8,8]


@pytest.mark.parametrize('defect',['bool','float','missing','conflict','mixed'])
def test_bi_step_alias_rejects_coercion_conflicts_and_mixed_schemas(defect):
    p=old.local_json(live.R81_TO_R86_RECEIPTS[0]);b=p['iterations'][0]['repetition_blocks'][0]
    if defect=='bool':b['step_in_block']=True
    elif defect=='float':b['step_in_block']=float(b['step_in_block'])
    elif defect=='missing':b.pop('step_in_block')
    elif defect=='conflict':
        for a in p['iterations']:
            for v in a['repetition_blocks']:v['crossover_step']=v['step_in_block']-1
        b['crossover_step']=1-(b['step_in_block']-1)
    else:b['crossover_step']=b['step_in_block']-1
    with pytest.raises(ValueError):old._exact_campaign_block_rows(p,max_round=86)


@pytest.mark.parametrize('number',[81,82])
@pytest.mark.parametrize('where',['window','block'])
@pytest.mark.parametrize('field',['dl_goodput_mbps','ul_goodput_mbps'])
def test_bi_directional_source_alias_is_not_a_label_only(number,where,field):
    entry=list(next(live._campaign86([live.R81_TO_R86_RECEIPTS[number-81]])))
    p=deepcopy(entry[1]);a=p['iterations'][0];target=a if where=='window' else a['repetition_blocks'][0]
    target[field]+=0.0000001;entry[1]=p
    with pytest.raises(ValueError):live._convert_campaign([tuple(entry)],catalog=live.ROUND86_SPECS,max_round=86)


@pytest.mark.parametrize('number',[81,82,83,84,85,86])
@pytest.mark.parametrize('kind',['set','reset'])
def test_bi_prep_and_reset_must_be_declared_for_both_endpoints(number,kind):
    entry=list(next(live._campaign86([live.R81_TO_R86_RECEIPTS[number-81]])))
    # Remove the corresponding RPC call target from the source text, not execute it.
    if kind=='set':
        import ast
        tree=ast.parse(entry[-1])
        users=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='rpc'and len(n.args)>=2
            and ast.unparse(n.args[0])=='b.client' and any(isinstance(x,ast.Name)and x.id=='prep_cmd'for x in ast.walk(n.args[1]))]
        assert len(users)==1
        users[0].args[0]=ast.Name(id='unknown_endpoint',ctx=ast.Load())
        text=ast.unparse(tree)
    else:text=entry[-1].replace('iw phy phy0 set coverage 0 2>/dev/null || true;','REMOVED_RESET;')
    assert text!=entry[-1]
    with pytest.raises(ValueError):live._recipe_context86(text,live.ROUND86_SPECS[number][-1])


def test_bi_future87_and_historical80_boundary_before_content(tmp_path,monkeypatch):
    future=tmp_path/'lap120_loco195_r87_out_of_scope.json';new=live.R81_TO_R86_RECEIPTS[0];native=Path.read_bytes
    def bounded(path):
        if path in (future,new):raise AssertionError('out-of-selected-scope input content read')
        return native(path)
    monkeypatch.setattr(Path,'read_bytes',bounded)
    with pytest.raises(ValueError,match='not an authenticated'):list(live._campaign80([new]))
    monkeypatch.setattr(Path,'read_bytes',lambda p:(_ for _ in ()).throw(AssertionError('future content read'))if p==future else native(p))
    with pytest.raises(ValueError,match='not an authenticated'):list(live._campaign86([future]))
    assert not future.exists()


@pytest.mark.parametrize('defect',['checksum','size','missing','path','future'])
def test_bi_frozen_copy_manifest_rejects_tamper_without_original_reads(monkeypatch,defect):
    native=live._json;m=deepcopy(native(live.BI_INPUT_MANIFEST));first=m['entries'][0]
    if defect=='checksum':first['sha256']='0'*64
    elif defect=='size':first['bytes']=True
    elif defect=='missing':m['entries'].pop()
    elif defect=='path':first['copy']=first['path']
    else:first['round']=87
    monkeypatch.setattr(live,'_json',lambda p:m if p==live.BI_INPUT_MANIFEST else native(p))
    with pytest.raises(ValueError):live._inputs86()


@pytest.mark.parametrize('number,field,value',[(81,'active_flow_count',2.0),(83,'bidirectional',False)])
def test_bi_typed_rows_cannot_spoof_declared_direction_context(typed86,number,field,value):
    row=next(r for r in typed86 if r.round_id==f'R{number}')
    with pytest.raises(ValueError):replace(row,**{field:value})


def test_bm_latest92_adds12_arms_to272_without_inventing_spec185():
    data,blocks=live.load_live_dataset(through_round=92),live.load_crossed_dataset(through_round=92)
    assert len(data['records'])==284
    assert len(blocks['crossed'])==2140
    assert len({(r['round_id'],r['block_index'])for r in blocks['crossed']})==982


def test_bm_explicit86_and_typed92_interfaces_are_additive():
    assert callable(getattr(live,'load_r1_to_r86_dataset',None))
    assert callable(getattr(live,'load_all92_measurements',None))
    assert callable(getattr(live,'load_all92_block_observations',None))


@pytest.fixture(scope='module')
def corpus92():
    return live.load_live_dataset(through_round=92),live.load_crossed_dataset(through_round=92)


@pytest.fixture(scope='module')
def typed92():
    return live.load_all92_measurements()[0]


@pytest.mark.parametrize('revision',[56,60,65,70,75,80,86])
def test_bm_all14_historical_serialized_interfaces_are_exact(revision):
    encode=lambda v:(json.dumps(v,indent=2,allow_nan=False)+'\n').encode()
    assert encode(live.load_live_dataset(through_round=revision))==getattr(live,f'R{revision}_RECORDS_OUTPUT').read_bytes()
    assert encode(live.load_crossed_dataset(through_round=revision))==getattr(live,f'R{revision}_BLOCKS_OUTPUT').read_bytes()


def test_bm_prior272_records1948_crossed16_sequential_are_literal_prefix(corpus92):
    data,blocks=corpus92;prior=live._sealed86(live.R86_RECORDS_OUTPUT);pb=live._sealed86(live.R86_BLOCKS_OUTPUT)
    assert data['records'][:272]==prior['records']
    assert blocks['crossed'][:1948]==pb['crossed']and blocks['sequential']==pb['sequential']
    assert (data['primary_window_count'],data['auxiliary_window_count'])==(282,2)
    assert len(data['source_refs'])==92
    assert len(live.load_all92_measurements(include_auxiliary=False)[0])==282


@pytest.mark.parametrize('number,regime,flows,bidir,distance,coverage,slot,ack',[
    (87,'unidir_dl_2flow',2,False,100,0,9,18),(88,'bidir_4flow',4,True,12000,27,90,180),
    (89,'bidir_4flow',4,True,14000,31,102,204),(90,'bidir_6flow',6,True,14000,31,102,204),
    (91,'bidir_2flow',2,True,3000,6,27,54),(92,'bidir_2flow',2,True,6000,13,48,96)])
def test_bm_sourcecontext_mean_RTT_and_WDS_saved_evidence(typed92,number,regime,flows,bidir,distance,coverage,slot,ack):
    rows=[r for r in typed92 if r.round_id==f'R{number}'];assert len(rows)==2
    for r in rows:
        assert (r.workload_regime,r.active_flow_count,r.bidirectional,r.distance_meters,r.coverage_class)==(regime,flows,bidir,distance,coverage)
        assert type(r.active_flow_count)is int and type(r.bidirectional)is bool
        assert r.ap_policy.distance_meters==r.cpe_policy.distance_meters==distance
        e=r.certified_wds_evidence
        assert (e['slot_time_us'],e['ack_timeout_us'])==(slot,ack)
        assert r.dyadic_mean_audit['all_fraction_zero']is r.dyadic_mean_audit['all_zero_ulp']is True
        assert len(r.rtts_ms)==160 and r.raw_rtts_matches_blocks is True
        assert e['exact_numpy_quantiles']is e['mac_counters_valid']is e['mac_block_sums_match_window']is True
        assert r.packet_loss_pct==r.station_drops==0 and r.restoration_verified is True
        assert e['frozen_recipe_distance_application_declared']is False
        assert e['frozen_recipe_coverage_command_declared']is e['frozen_recipe_coverage_reset0_declared']is True
        assert e['physical_distance_verified']is e['effective_timing_independently_verified']is False
        assert e['directional_applicability']['jain_applicable_for_QoE_inference']is bidir
        if number==87:
            assert r.jain_fairness==.5 and r.ul_goodput_mbps==0 and r.dl_goodput_mbps==r.goodput_mbps
            assert e['directional_applicability']['active_direction_equals_total_every_arm_and_block']is True
            assert r.ap_policy.aql_by_ac[2]in((5000,12000),(1900,3800))


def test_bm_R89_literal_recipe_name_is_not_timing_identity_authority(typed92):
    expected='run_live_autoresearch_r89_bidir_4flow_covclass33_15km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py'
    assert live.ROUND92_RECIPES[89]==expected
    manifest=live._inputs92()
    ref=next(e for e in manifest['entries']if e['round']==89 and e['path'].endswith('.py'))
    assert ref['path'].endswith(expected)and ref['original_path'].endswith(expected)
    text=(old.ROOT/ref['path']).read_text()
    assert live._recipe_context86(text,31)['prep_coverage']==31
    with pytest.raises(ValueError):live._recipe_context86(text,33)
    for row in (r for r in typed92 if r.round_id=='R89'):
        assert (row.distance_meters,row.coverage_class)==(14000,31)
        assert row.certified_wds_evidence['source_recipe']['path'].endswith(expected)


def test_bm_historical_R75_class33_remains_literal_not_repaired(typed92):
    row=next(r for r in typed92 if r.round_id=='R75')
    assert (row.distance_meters,row.coverage_class)==(15000,33)
    assert row.certified_wds_evidence['physical_distance_verified']is False
    assert row.certified_wds_evidence['effective_timing_independently_verified']is False


@pytest.mark.parametrize('number',[87,88,89,90,91,92])
@pytest.mark.parametrize('where',['root','iteration','knobs'])
@pytest.mark.parametrize('field',['distance_m','coverage_class','slot_time_us','ack_timeout_us'])
@pytest.mark.parametrize('fault',['missing','boolean','float','conflict'])
def test_bm_shared_timing_never_coerces_or_defaults(number,where,field,fault):
    p=old.local_json(live.R87_TO_R92_RECEIPTS[number-87]);item=p['iterations'][0]
    d=p if where=='root'else item if where=='iteration'else item['candidate_knobs']
    if fault=='missing':d.pop(field)
    elif fault=='boolean':d[field]=True
    elif fault=='float':d[field]=float(d[field])
    else:d[field]+=1
    with pytest.raises(ValueError):live._context(number,p,item,catalog=live.ROUND92_SPECS)


@pytest.mark.parametrize('number',[87,89,91,92])
@pytest.mark.parametrize('where',['root','iteration','knobs'])
@pytest.mark.parametrize('field',['traffic_regime','active_flow_count','bidirectional'])
@pytest.mark.parametrize('fault',['missing','wrong','coercion'])
def test_bm_new_directional_and_two_flow_declarations_are_explicit(number,where,field,fault):
    p=old.local_json(live.R87_TO_R92_RECEIPTS[number-87]);item=p['iterations'][0]
    d=p if where=='root'else item if where=='iteration'else item['candidate_knobs']
    if fault=='missing':d.pop(field)
    elif fault=='wrong':d[field]='bidir_8flow'if field=='traffic_regime'else 8 if field=='active_flow_count'else not d[field]
    else:d[field]=[]if field=='traffic_regime'else float(d[field])if field=='active_flow_count'else int(d[field])
    with pytest.raises(ValueError):live._context(number,p,item,catalog=live.ROUND92_SPECS)


@pytest.mark.parametrize('number,field,value',[(87,'active_flow_count',2.0),(87,'bidirectional',True),
    (89,'distance_meters',15000),(89,'coverage_class',33),(90,'coverage_class',31.0),
    (91,'active_flow_count',6),(92,'workload_regime','bidir_6flow')])
def test_bm_typed_context_cannot_relabel_new_saved_packages(typed92,number,field,value):
    row=next(r for r in typed92 if r.round_id==f'R{number}')
    with pytest.raises(ValueError):replace(row,**{field:value})


@pytest.mark.parametrize('fault',['missing','bool','float','conflict','mixed'])
def test_bm_R87_explicit_step_alias_rejects_ambiguous_coordinate_schema(fault):
    p=old.local_json(live.R87_TO_R92_RECEIPTS[0]);b=p['iterations'][0]['repetition_blocks'][0]
    if fault=='missing':b.pop('step_in_block')
    elif fault=='bool':b['step_in_block']=True
    elif fault=='float':b['step_in_block']=float(b['step_in_block'])
    elif fault=='mixed':b['crossover_step']=b['step_in_block']-1
    else:
        for a in p['iterations']:
            for block in a['repetition_blocks']:block['crossover_step']=block['step_in_block']-1
        b['crossover_step']=1-(b['step_in_block']-1)
    with pytest.raises(ValueError):old._exact_campaign_block_rows(p,max_round=92)


def test_bm_R87_roundtrip_preserves_indices_and8AB8BA_without_block_health_invention(corpus92):
    _,blocks=corpus92;own=[b for b in blocks['crossed']if b['round_id']=='R87']
    assert len(own)==32 and len({b['block_index']for b in own})==16
    assert all(b['source_step_in_block']in(1,2)and b['crossover_step']==b['source_step_in_block']-1 for b in own)
    first=[b['treatment_id']for b in own if b['crossover_step']==0]
    assert sorted(first.count(t)for t in set(first))==[8,8]
    assert all(b['source_step_field']=='step_in_block'for b in own)
    assert all('restoration_verified'not in b['observation']for b in own)
    assert all(b['quality_evidence']=='PING_COUNTS_RECORDED_OTHER_BLOCK_HEALTH_UNKNOWN_UNLESS_EXPLICIT'for b in own)


@pytest.mark.parametrize('leg',['dl_goodput_mbps','ul_goodput_mbps'])
@pytest.mark.parametrize('where',['arm','block'])
def test_bm_R87_active_alias_and_inactive_zero_are_exact_not_approximate(leg,where):
    e=list(next(live._campaign92([live.R87_TO_R92_RECEIPTS[0]])));p=deepcopy(e[1]);a=p['iterations'][0]
    target=a if where=='arm'else a['repetition_blocks'][0];target[leg]+=0.0000001;e[1]=p
    with pytest.raises(ValueError):live._convert_campaign([tuple(e)],catalog=live.ROUND92_SPECS,max_round=92)


def test_bm_only_frozen_copy_paths_are_read_never_documentary_originals(monkeypatch):
    manifest=old.local_json(live.BM_INPUT_MANIFEST);originals={(old.ROOT/e['path']).resolve()for e in manifest['entries']}
    native_file,native_read=Path.is_file,Path.read_bytes
    def nofile(p):
        if p.resolve()in originals:raise AssertionError('Original source was probed')
        return native_file(p)
    def noread(p):
        if p.resolve()in originals:raise AssertionError('Original source was opened')
        return native_read(p)
    monkeypatch.setattr(Path,'is_file',nofile);monkeypatch.setattr(Path,'read_bytes',noread)
    rows,_,refs=live._new_data92()
    assert len(rows)==12 and len(refs)==6


@pytest.mark.parametrize('fault',['sha256','size_bool','bad_copy','missing','future','inferred_recipe_name'])
def test_bm_manifest_exact_membership_and_digests_fail_closed(monkeypatch,fault):
    native=live._json;manifest=deepcopy(native(live.BM_INPUT_MANIFEST));e=manifest['entries'][0]
    if fault=='sha256':e['sha256']='0'*64
    elif fault=='size_bool':e['bytes']=True
    elif fault=='bad_copy':e['copy']=e['path']
    elif fault=='missing':manifest['entries'].pop()
    elif fault=='future':e['round']=93
    else:
        e=next(e for e in manifest['entries']if e['round']==89 and e['path'].endswith('.py'))
        e['path']=e['path'].replace('covclass33_15km','covclass31_14km')
    monkeypatch.setattr(live,'_json',lambda p:manifest if p==live.BM_INPUT_MANIFEST else native(p))
    with pytest.raises(ValueError):live._inputs92()


def test_bm_future93_and_revision86_reject_before_content_read(tmp_path,monkeypatch):
    future=tmp_path/'lap120_loco195_r93_forbidden.json';new=live.R87_TO_R92_RECEIPTS[0];native=Path.read_bytes
    def bounded(p):
        if p in(future,new):raise AssertionError('Out-of-selected-campaign content read')
        return native(p)
    monkeypatch.setattr(Path,'read_bytes',bounded)
    with pytest.raises(ValueError,match='not an authenticated'):list(live._campaign86([new]))
    monkeypatch.setattr(Path,'read_bytes',lambda p:(_ for _ in ()).throw(AssertionError('future content read'))if p==future else native(p))
    with pytest.raises(ValueError,match='not an authenticated'):list(live._campaign92([future]))
    assert not future.exists()
