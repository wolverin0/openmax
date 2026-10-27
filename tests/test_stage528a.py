"""Offline JSON, ELF-slice and source-literal contracts; no producer execution."""
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import pytest
from tools.autoresearch import build_stage528a_ltu_dcxo_gps_tcxo_and_144window_reconciler as m


def saved(stage):return json.loads((m.ROOT/'artifacts/autoresearch'/m.SOURCES[stage]).read_text('utf-8'))


def test_available_windows_and_reported_loopback_means_do_not_validate_cumulative_144():
    r=m.audit_windows467(saved(467),saved(470))
    assert r['available_named_rounds']==3 and r['available_direct_windows']==12
    assert r['claimed_campaigns']==12 and r['claimed_ab_rounds']==36
    assert r['claimed_cumulative_windows']==144 and r['unlinked_claimed_windows']==132
    assert r['claim_arithmetic_consistent'] and r['summary_conflicts']==[]
    assert r['reported_rtt_means_ms']==pytest.approx({'A':0.236,'B':0.198})
    assert r['reported_rtt_delta_pct']==pytest.approx(100*(0.198/0.236-1))
    assert r['accepted_ota_windows']==0 and not r['historical_window_chain_complete']
    assert r['probe_scope']=='LOOPBACK_127_0_0_1_NOT_OTA'
    assert r['reported_live_ssh_connected'] and not r['flag_excludes_partial_error_fallback']
    assert r['provenance_status']=='AMBIGUOUS_NATIVE_PROVENANCE_WITH_SYNTHETIC_FALLBACK'
    assert r['fallback_branch_actually_taken']=='UNKNOWN_NO_NATIVE_TRANSCRIPT_OR_EXIT'
    assert not r['counter_deltas_epoch_qualified']


@pytest.mark.parametrize('change',['duplicate_round','missing_window','extra_window','boolean_rtt','negative_rtt','nan_rtt','boolean_irq','negative_irq','boolean_round'])
def test_invalid_window_structure_and_measurement_domains(change):
    a=saved(467);w=a['counterbalanced_rounds'][0]['windows']['A1']
    if change=='duplicate_round':a['counterbalanced_rounds'][1]['round']=1
    elif change=='missing_window':a['counterbalanced_rounds'][0]['windows'].pop('B2')
    elif change=='extra_window':a['counterbalanced_rounds'][0]['windows']['C1']=deepcopy(w)
    elif change=='boolean_rtt':w['rtt_avg_ms']=True
    elif change=='negative_rtt':w['rtt_avg_ms']=-1
    elif change=='nan_rtt':w['rtt_avg_ms']=float('nan')
    elif change=='boolean_irq':w['irq52_cpu0_count']=False
    elif change=='negative_irq':w['irq52_cpu0_count']=-1
    else:a['counterbalanced_rounds'][0]['round']=True
    with pytest.raises(ValueError):m.audit_windows467(a,saved(470))


def test_wrong_summary_is_retained_as_conflict_not_extra_windows():
    a=saved(467);a['summary_metrics']['total_windows']=144
    r=m.audit_windows467(a,saved(470))
    assert r['available_direct_windows']==12 and r['unlinked_claimed_windows']==132
    assert 'total_windows'in r['summary_conflicts'] and r['accepted_ota_windows']==0


def test_monitor_silence_and_fallbacks_never_become_cfo_or_gps_evidence():
    source=saved(502)['monitor_script']['path'];text=(m.ROOT/source).read_text('utf-8');r=m.audit_monitor(text)
    assert r['status']=='UNSAFE_EVIDENCE_DEFAULTS_PRESENT'
    assert r['missing_log_assumes_good_sync']and r['missing_log_assumes_low_cfo']
    assert r['temperature_fallback_present']and r['uptime_fallback_present']and r['irq_fallback_present']
    assert r['gps_lock_evidence']==r['cfo_evidence']=='UNKNOWN'
    assert not r['script_executed']and not r['monitor_remediated']
    changed=m.audit_monitor(text.replace('TCXO_DISCIPLINED_OR_GPS_LOCKED','UNKNOWN').replace('LOW_WITHIN_0_25_PPM','UNKNOWN'))
    assert changed['gps_lock_evidence']==changed['cfo_evidence']=='UNKNOWN'


@pytest.mark.parametrize('text',['X="computed"','X=helper()','X="a"\nX="b"','X="a"\nX+="b"','other="a"'])
def test_old_template_extraction_requires_unique_ast_literal(text):
    if text=='X="computed"':assert m.extract_literal(text,'X')==b'computed'
    else:
        with pytest.raises(ValueError):m.extract_literal(text,'X')


def test_current_v10_literal_and_current_script_are_compared_independently():
    claim=saved(470);manifest=json.loads((m.ROOT/m.MANIFEST).read_text('utf-8'))
    text=(m.ROOT/m.PRODUCERS[470]).read_text('utf-8');current=(m.ROOT/m.CHAMPION).read_bytes()
    r=m.audit_v10(claim,manifest,text,current)
    assert r['recorded_v10_sha256']=='28ba77b4d3841296e6a50696c034390094586f663ba089bbc92f552829b31ecb'
    assert r['recorded_claims_agree']
    assert r['current_script_matches_v10']==(hashlib.sha256(current).hexdigest()==r['recorded_v10_sha256'])
    literal_hash=hashlib.sha256(m.extract_literal(text,'CHAMPION_V10_SH_CONTENT')).hexdigest()
    assert r['literal_matches_recorded_v10']==r['old_v10_recovered']==(literal_hash==r['recorded_v10_sha256'])
    assert not r['script_written_or_executed']
    assert r['current_script_sha256']==hashlib.sha256(current).hexdigest()
    assert r['manifest_models']==6 and r['manifest_reported_live_models']==['LTU-Lite']
    assert not r['all_manifest_models_hardware_qualified']
    mismatch=m.audit_v10(claim,manifest,'CHAMPION_V10_SH_CONTENT="untrusted later content"',current)
    assert not mismatch['literal_matches_recorded_v10']and not mismatch['old_v10_recovered']


@pytest.mark.parametrize('change',['duplicate_board','boolean_liveflag','boolean_claim_count'])
def test_manifest_identity_flags_and_claim_types(change):
    claim=saved(470);manifest=json.loads((m.ROOT/m.MANIFEST).read_text('utf-8'))
    if change=='duplicate_board':manifest['boards'].append(deepcopy(manifest['boards'][0]))
    elif change=='boolean_liveflag':manifest['boards'][0]['live_bench_verified']=1
    else:manifest['cumulative_live_windows']=True
    with pytest.raises(ValueError):m.audit_v10(claim,manifest,(m.ROOT/m.PRODUCERS[470]).read_text('utf-8'),b'unexecuted')


@pytest.mark.parametrize('change',['source_pin','slice_hash','slice_bounds','duplicate_name','elf_attrs','truncated_census'])
def test_all_symbol_slices_and_arm_metadata_are_bound(change):
    proof=json.loads((m.ROOT/m.PROOF).read_text('utf-8'))
    if change=='source_pin':proof['source']['sha256']='0'*64
    elif change=='slice_hash':proof['defined_sized_symbols'][0]['sha256']='0'*64
    elif change=='slice_bounds':proof['defined_sized_symbols'][0]['file_offset']=proof['source']['bytes']
    elif change=='duplicate_name':proof['defined_sized_symbols'][1]['name']=proof['defined_sized_symbols'][0]['name']
    elif change=='elf_attrs':proof['elf']['machine']='MIPS'
    else:proof['defined_sized_symbols'].pop()
    with pytest.raises(ValueError):m.verify_symbols(m.ROOT,proof)


def test_515_saved_metrics_are_synthetic_not_measured_cfo_or_4096qam_limits():
    r=m.audit_model515(saved(515))
    assert r['reported_metrics']['baseline']['mean_goodput_mbps']==409.73
    assert r['reported_metrics']['champion']['mean_goodput_mbps']==618.
    assert r['recomputed_synthetic_goodput_gain_pct']==pytest.approx(100*(618/409.73-1))
    assert r['status']=='UNCALIBRATED_SYNTHETIC_MODEL_NOT_MEASURED'
    assert not r['measured_4096qam_or_cfo_threshold']and not r['model_reexecuted']


def test_saved_report_source_pins_census_correction_and_boundaries():
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((m.ROOT/m.OUT).read_text('utf-8'))
    assert r['static_symbols']['broad_defined_sized_count']==38 and r['static_symbols']['bbp_rf_dcxo_defined_sized_count']==11
    assert r['saved486']['reported_capped_dcxo_tcxo_count']==30 and not r['saved486']['census_is_complete']
    assert not r['named_source_correction']['stage485_is_ltu_dcxo_source']
    assert r['named_source_correction']['actual_ltu_source_stage']==486
    assert not r['causal_join_between_linux_loopback_and_dcxo_model_allowed'] and not any(r['boundary'].values())
    for key in('callable_abi_proven','gps_lock_proven','cfo_readback_proven','board_capability_proven'):assert not r['static_symbols'][key]
    for pin in r['static_sources']+r['analysis_dependencies']:assert sha(m.ROOT/pin['path'])==pin['sha256']
    assert r['implementation']['sha256']==sha(Path(m.__file__))
    text=(m.ROOT/m.DOC).read_text('utf-8')
    assert len(text.splitlines())<220 and text.startswith('<!-- doc-head:')
    assert text.count('<!-- doc-head:')==text.count('<!-- /doc-head -->')==1
    assert r['outputs'][m.DOC]['sha256']==sha(m.ROOT/m.DOC)
    tree=ast.parse(Path(m.__file__).read_text('utf-8'));imports=[n.module or ''for n in ast.walk(tree)if isinstance(n,ast.ImportFrom)]
    imports += [a.name for n in ast.walk(tree)if isinstance(n,ast.Import)for a in n.names]
    assert not any(n.startswith(('tools.bench','tools.sim','tools.firmware','subprocess','socket','paramiko'))for n in imports)
