import json
from pathlib import Path
import pytest
from tools.bench import export_cumulative_autoresearch_leaderboard as m


def windows():
    return [{'window':lab,'goodput_mbps':gp,'under_load_rtt':{'p50_ms':1,'p95_ms':p95,'p99_ms':p95+1,'samples':10}}
            for lab,gp,p95 in [('A1',10,5),('B1',12,4),('A2',20,7),('B2',24,6)]]


def test_recomputed_means_not_source_claims():
    ws,basis=m.normalize(windows());a,b,d=m.summarize(ws)
    assert a['goodput_mbps']==15 and b['goodput_mbps']==18
    assert d['goodput_mbps']==20 and basis=='goodput_mbps'


@pytest.mark.parametrize('kind',['order','sentinel','nan','samples','quantile'])
def test_bad_windows_rejected(kind):
    ws=windows()
    if kind=='order':ws[1]['window']='A2'
    if kind=='sentinel':ws[0]['under_load_rtt']['p95_ms']=999
    if kind=='nan':ws[0]['goodput_mbps']=float('nan')
    if kind=='samples':ws[0]['under_load_rtt']['samples']=1
    if kind=='quantile':ws[0]['under_load_rtt']['p50_ms']=9
    with pytest.raises(ValueError):m.normalize(ws)


def test_cutoff_simulation_dedup_and_missing_panel1(tmp_path):
    path=tmp_path/'artifacts/autoresearch';path.mkdir(parents=True)
    for name in ('stage123a_live_wa_test.json','stage124a_live_wa_duplicate.json','stage169a_cumulative_wa_test.json','stage269a_live_wa_test.json','stage124a_wa_sim.json'):
        (path/name).write_text(json.dumps({'rounds':[{'round_id':'R1','windows':windows()}]}))
    (path/'stage168a_live_panel1_test.json').write_text(json.dumps({'protocol':'A1 -> B1 -> A2 -> B2'}))
    result=m.export(tmp_path)
    assert result['summary']['unique_comparisons']==1
    assert result['summary']['duplicate_comparisons']==1
    assert result['coverage']['Panel1']['status']=='NO_QUALIFYING_SAVED_ABAB'
    assert all('269' not in r['path'] for r in result['static_sources'])
    assert any(r.get('classification')=='simulation_or_plan' for r in result['static_sources'])
    assert any(r.get('classification')=='derived_or_observational_not_primary_counterbalanced_acquisition' for r in result['static_sources'])


def test_joint_families_do_not_become_single_radio_replications():
    assert m.family_for('stage151a_live_xc_2xc_test.json')=='XC+2XC'
    assert m.family_for('stage103a_wa_xc_test.json')=='WA+XC'
    assert m.family_for('stage103f_ltu_dual_and_2xc_test.json')=='LTU+2XC'


def test_ltu_phases_and_xm_basis():
    phases={w['window']:{'goodput_mbps':w['goodput_mbps'],'rtt_p95_ms':w['under_load_rtt']['p95_ms']} for w in windows()}
    ptr,rows,ctx=next(m.arrays({'phases':phases}))
    assert ctx['named_phase_keys'] is True
    assert len(m.normalize(rows)[0])==4
    ws=[{'window':w['window'],'bridge_goodput_mbps':w['goodput_mbps'],'boca2_xm_1_20_rtt':w['under_load_rtt']} for w in windows()]
    assert m.normalize(ws)[1]=='bridge_goodput_mbps'


def test_duplicate_window_ids_and_conflicting_arms_rejected():
    ws=windows();ws[2]['window']='A1'
    with pytest.raises(ValueError,match='duplicate'):m.normalize(ws)
    ws=windows();ws[0]['arm']='B'
    with pytest.raises(ValueError,match='conflict'):m.normalize(ws)
    ws=windows();ws[2]['window']='A1';ws[3]['window']='B'
    with pytest.raises(ValueError,match='duplicate'):m.normalize(ws)
    ws=windows();ws[0]['phase']='A2'
    with pytest.raises(ValueError,match='conflict'):m.normalize(ws)


def test_huge_json_numbers_and_derived_overflow_are_rejected():
    assert not m.finite(10**400)
    ws=windows()
    for w in ws:w['goodput_mbps']=1e-308 if w['window'].startswith('A') else 1e308
    normalized,_=m.normalize(ws)
    with pytest.raises(ValueError,match='nonfinite_derived'):m.summarize(normalized)


def test_reconstructed_arrays_use_real_json_pointers():
    ws=windows();obj={'rounds':[{'arm_a_windows':ws[::2],'arm_b_windows':ws[1::2]}]}
    pointer,rows,context=next(m.arrays(obj))
    assert pointer=='/rounds/0'
    assert context['source_array_pointers']==['/rounds/0/arm_a_windows','/rounds/0/arm_b_windows']
    assert m.normalize(rows)[0][1]['arm']=='B'


def test_named_phase_keys_cannot_hide_conflicting_saved_labels():
    phases={w['window']:{'phase':w['window'],'goodput_mbps':w['goodput_mbps'],'rtt_p95_ms':5} for w in windows()}
    phases['A1']['phase']='B1'
    _,rows,_=next(m.arrays({'phases':phases}))
    with pytest.raises(ValueError):m.normalize(rows)


def test_saved_export_has_provenance_no_physical_acceptance():
    root=Path(__file__).resolve().parents[1]
    r=json.loads((root/m.OUT).read_text())
    assert r['summary']['unique_comparisons']>10
    assert not r['boundary']['live_acquisition_executed'] and not r['boundary']['global_champion']
    assert all(x['source']['json_pointer'] and len(x['source']['sha256'])==64 for x in r['rounds'])
