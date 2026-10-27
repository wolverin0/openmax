"""Local exact-oracle/disposable fixtures and authorized frozen R71-R75 only."""
from copy import deepcopy
from fractions import Fraction
from itertools import product
import json
import pytest
from analysis.statistics import fmx_r71_to_r75_seven_distance_and_flow_audit as bb


def declaration(number=71):
    distance,coverage,slot,ack=bb.TIMING[number]
    common=dict(distance_m=distance,coverage_class=coverage,slot_time_us=slot,ack_timeout_us=ack)
    return deepcopy(common),deepcopy(common)|dict(candidate_knobs=deepcopy(common)|dict(ap_state={},cpe_state={}))


@pytest.mark.parametrize('number',[71,72,73,74,75])
def test_declared_new_timing_is_not_physical_or_runtime_proof(number):
    root,arm=declaration(number);r=bb.declared_context(number,root,arm)
    assert tuple(r[k]for k in ('distance_m','coverage_class','slot_time_us','ack_timeout_us'))==bb.TIMING[number]
    assert r['physical_distance_verified'] is r['effective_runtime_application_verified'] is False
    assert r['slot_ack_provenance']=='SHARED_PAYLOAD_TREATMENT_KNOBS'
    assert r['endpoint_states_originally_omit_timing']


@pytest.mark.parametrize('where',['root','arm','knobs'])
@pytest.mark.parametrize('key',['distance_m','coverage_class','slot_time_us','ack_timeout_us'])
def test_missing_shared_field_cannot_inherit_from_class(where,key):
    root,arm=declaration();target=root if where=='root' else arm if where=='arm' else arm['candidate_knobs'];target.pop(key)
    with pytest.raises(ValueError):bb.declared_context(71,root,arm)


@pytest.mark.parametrize('key,value',[('coverage_class',True),('distance_m',100.),('slot_time_us',10),('ack_timeout_us',None)])
def test_wrong_timing_type_or_value_fails_closed(key,value):
    root,arm=declaration();arm['candidate_knobs'][key]=value
    with pytest.raises(ValueError):bb.declared_context(71,root,arm)


def test_endpoint_conflicts_and_unsupported_old_provenance_rejected():
    root,arm=declaration(73);arm['candidate_knobs']['ap_state']['distance_meters']=100
    with pytest.raises(ValueError):bb.declared_context(73,root,arm)
    root,arm=declaration(73)
    saved=dict(coverage_class=27,distance_meters=12000,certified_wds_evidence=dict(slot_time_us=90,ack_timeout_us=180,slot_ack_source='ROOT_RECEIPT_ONLY'))
    with pytest.raises(ValueError):bb.declared_context(73,root,arm,saved)


def test_presence_first_context_fallback_keeps_unknown_and_never_imputes():
    r=dict(distance_meters=4500,coverage_class=10,certified_wds_evidence=dict(slot_time_us=39,ack_timeout_us=78))
    assert bb.recorded_context(r)['slot_time_us']==39
    r['slot_time_us']=None;r['ack_timeout_us']=80
    assert bb.recorded_context(r)['slot_time_us'] is None and bb.recorded_context(r)['ack_timeout_us']==80
    assert bb.recorded_context(dict(distance_meters=3000,coverage_class=6))['slot_time_us'] is None


def profiles():
    contrasts=[];utilities=[]
    for n in bb.ROUNDS:
        utilities.append(dict(round_id=f'R{n}',loss_percent_exact='1',target_retry_lower=True))
        for m in bb.METRICS:
            lower=m in bb.METRICS[1:4]
            contrasts.append(dict(scope=f'R{n}',metric=m,favorable_blocks=15 if n==72 and lower else 16,
                direction='lower'if lower else'higher',HL_estimate=-1 if lower else 1,
                family_adjusted_p={bb.RANK_FAMILY:.01},equal_blocks=0,
                exact_rank={'p_value':.00003},exact_sign={'p_value':.00003},exact_sign_flips={'mean':{'p_value':.00003}}))
    return contrasts,utilities


def test_R72_and_R73_cannot_be_rescued_by_KEEP_good_QoE_or_lower_retry():
    c,u=profiles();u[1]['loss_percent_exact']='12/5';u[2]['loss_percent_exact']='21/10'
    r=bb.profile_conditions(c,u)
    assert not r[1]['strict_observed_GP_loss_below2'] and not r[1]['all_five_16of16']
    assert r[2]['all_five_16of16'] and r[2]['five_direct_rank_HL_Holm500'] and not r[2]['requested_strict_claim_necessary_conditions_met']
    assert r[2]['target_retry_lower']
    assert all(x['status']=='NECESSARY_OBSERVED_CONDITIONS_ONLY_NOT_BC_PROMOTION' for x in r)


def test_unstated_GP_wins_never_invented_and_twoflow_retry_not_extended():
    c,u=profiles();claims=bb.profile_claims(c)
    assert [x['claimed_favorable']for x in claims if x['metric']==bb.METRICS[0]]==[None,7,6,None,5]
    assert all(x['retry_mode_scope']=='EXISTING_SIX_FLOW_ONLY_NOT_EXTENDED_BY_THIS_AUDIT' for x in bb.profile_conditions(c,u))
    u[0]['loss_percent_exact']='2'
    assert not bb.profile_conditions(c,u)[0]['strict_observed_GP_loss_below2']


def rows(lag=0):
    out=[]
    for i in range(16):
        previous=None
        for step,t in enumerate(('A','B')if i%2==0 else('B','A')):
            value=10+i+3*(t=='B')+2*step+lag*(previous=='B')
            out.append(dict(round_id='R71',block_index=i,crossover_step=step,treatment_id=t,observation={'p95_rtt_ms':value},rtts_ms=[value]))
            previous=t
    return out


@pytest.mark.parametrize('damage',['missing','duplicate','old','mixed','bool_index','wrong_step'])
def test_pairing_does_not_drop_or_relabel_bad_units(damage):
    r=rows()
    if damage=='missing':r.pop()
    elif damage=='duplicate':r.append(deepcopy(r[0]))
    elif damage=='old':r[0]['round_id']='R65'
    elif damage=='mixed':r[0]['round_id']='R72'
    elif damage=='bool_index':r[0]['block_index']=True
    else:r[0]['crossover_step']=2
    with pytest.raises(ValueError):bb.pair_rows(r,'A','B','p95_rtt_ms')


def test_restricted_period_model_does_not_resolve_full_carryover_alias():
    ordinary=bb.period_adjusted_estimation(rows(),'A','B','p95_rtt_ms')
    lagged=bb.period_adjusted_estimation(rows(4),'A','B','p95_rtt_ms')
    assert (ordinary['direct_estimate'],ordinary['period_estimate'],ordinary['rank'])==(3,2,18)
    assert (lagged['direct_estimate'],lagged['period_estimate'])==(1,4)
    assert lagged['status']=='IDENTIFIED_RESTRICTED_MODEL_NOT_CAUSAL_CERTIFICATION'
    assert 'p_value' not in lagged


def literal_oracle(values):
    absolute=sorted(abs(v)for v in values if v)
    ranks={v:sum((Fraction(i+1)for i,w in enumerate(absolute)if w==v),Fraction())/absolute.count(v)for v in set(absolute)}
    weights=[[ranks[abs(v)]*(1 if v>0 else-1)if v else 0 for v in values],[int(v>0)-int(v<0)for v in values],values]
    return [sum(abs(sum(a*s for a,s in zip(w,signs)))>=abs(sum(w))for signs in product((-1,1),repeat=len(values)))for w in weights]


@pytest.mark.parametrize('values',[[0,0,0],[1,1,-1,2,-2,0],[.1,.2,-.3,.4],[1,2,3,4,-.125]])
def test_integer_rank_sign_mean_tails_match_independent_literal_sign_products(values):
    exact=[Fraction.from_float(float(v))for v in values];r=bb.enumerate_fraction_flips(exact)
    assert [r[k]['extreme_assignments']for k in ('rank','sign','mean')]==literal_oracle(exact)


def test_CI_components_and_alpha_monotonicity_match_literal_oracle():
    data=[1.,2.,2.,3.,4.,8.];result=bb.exact_effect(data)
    def member(ci,x):return any((c['lower']is None or x>c['lower']or x==c['lower']and c['lower_closed'])and(c['upper']is None or x<c['upper']or x==c['upper']and c['upper_closed'])for c in ci['components'])
    for theta in [-20.,0.,1.,1.5,2.,2.5,3.,4.,8.,20.]:
        p=literal_oracle([Fraction.from_float(v-theta)for v in data])[0]/64
        assert member(result['confidence_sets']['95'],theta)==(p>.05)
        assert member(result['confidence_sets']['99.9'],theta)==(p>.001)


def test_sixteen_sign_count_is_not_rank_or_mean():
    r=bb.exact_sign_flips(list(range(1,16))+[-.125])
    assert r['assignments']==65536 and r['sign']['extreme_assignments']==34
    assert r['rank']['p_value']!=r['sign']['p_value']!=r['mean']['p_value']


@pytest.mark.parametrize('bad',[[],[True],[float('nan')],[float('inf')],list(range(21))])
def test_bad_or_unbounded_exact_engine_inputs_rejected(bad):
    with pytest.raises(ValueError):bb.exact_sign_flips(bad)


def test_recipe_AST_never_executes_and_retains_unknown_call_value():
    text='raise RuntimeError("never run")\napply_r33_state_with_distance(distance_m=4500)\nx.apply_r33_state_with_distance(distance_m=unknown)'
    r=bb.recipe_distance_calls(text)
    assert [x['declared_distance_m_literal']for x in r]==[4500,None]


def test_literal_coverage_shell_fragment_is_not_a_successful_helper_or_readback():
    text='raise RuntimeError("never run")\ncommand="iw phy phy0 set coverage 10 2>/dev/null || true\\niw phy phy0 set coverage 0"'
    r=bb.recipe_coverage_commands(text)
    assert [x['coverage_class_literal']for x in r]==[10,0]
    assert r[0]['ignored_error_declared']and not r[1]['ignored_error_declared']
    assert all(x['source_text_only_not_execution_or_readback']for x in r)
    assert bb.recipe_distance_calls(text)==[]


def test_exclusive_output_guard_precedes_computation(tmp_path,monkeypatch):
    p=tmp_path/'wave_bb_existing.json';p.write_text('keep')
    monkeypatch.setattr(bb,'BASE',tmp_path);monkeypatch.setattr('sys.argv',['audit','--output',str(p)])
    monkeypatch.setattr(bb,'build_analysis',lambda:(_ for _ in()).throw(AssertionError('must not compute')))
    with pytest.raises(FileExistsError):bb.main()
    assert p.read_text()=='keep'


def test_all15_frozen_hashes_are_owned_current_rounds_only():
    r,l,refs,recipes=bb.frozen_inputs()
    assert len(refs)==15 and set(r)==set(l)==set(recipes)==set(bb.ROUNDS)
    assert all(len(a['repetition_blocks'])==16 for p in r.values()for a in p['iterations'])


@pytest.fixture(scope='module')
def actual():return bb.build_analysis()


def test_actual_counts_and_exact_independent_units(actual):
    assert actual['counts']==dict(records=250,new_arms=10,crossed_rows=1596,new_crossed_rows=160,matched_ids=710,new_matched_ids=80,sequential_R17=16)
    assert len(actual['contrasts'])==30 and sum(len(c['pairs'])for c in actual['contrasts'])==480
    assert sum(len(c['confidence_sets'])for c in actual['contrasts'])==60
    for c in actual['contrasts']:
        assert len(c['pairs'])==len(c['paired_unit_ids'])==16 and c['exact_sign_flips']['assignments']==65536
        assert c['exact_sign_flips']['rank']['p_value']==c['exact_rank']['p_value']
        assert c['exact_sign_flips']['sign']['p_value']==c['exact_sign']['p_value']


def test_actual_all40_means1600_pings_health_chronology_and_design(actual):
    assert sum(r['received_pings']for r in actual['source_claim_audits'])==1600
    for r in actual['source_claim_audits']:
        assert r['dyadic_audit']['status']=='DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP'
        assert r['complete_160_pings']and r['saved_loss_pct']==r['saved_station_drops']==0
        assert r['saved_restoration_verified']is True and r['mac_sums_match']and r['chronology_matches']
        assert r['declared_timing_context']['physical_distance_verified']is False
    assert all(d['design']['rank']==18 and len(d['design']['columns'])==19 for d in actual['design_diagnostics'])


def test_actual_families_and_projection_remain_rank_not_mean_or_transfer(actual):
    f=actual['families']
    assert f[bb.RANK_FAMILY]['known_count']==f[bb.MEAN_FAMILY]['known_count']==30
    assert f[bb.RANK_FAMILY]['unknown_padding_count']==f[bb.MEAN_FAMILY]['unknown_padding_count']==470
    assert f['complete_known_rank945_bound945']['known_count']==945
    assert bb.MEAN_FAMILY not in actual['promotion_evidence']['families']
    by_id={c['source_hypothesis_id']:c for c in actual['contrasts']}
    for r in actual['promotion_evidence']['contrasts']:
        c=by_id[r['source_hypothesis_id']]
        assert r['round_ids']==[c['scope']]and r['paired_unit_ids']==c['paired_unit_ids']
        assert r['p_exact_rank']==c['exact_rank']['p_value']and r['holm500_adjusted_p']==c['family_adjusted_p'][bb.RANK_FAMILY]
    assert not actual['automatic_execution_allowed']and not actual['physical_or_causal_acceptance']


def test_actual_source_claims_report_false_or_unstated_without_forcing_acceptance(actual):
    for c in actual['numerical_source_claims']:
        if c['metric']=='goodput_mbps':assert c['matches']==(Fraction(str(c['actual']))==Fraction(c['claimed_literal']))
    for c in actual['stated_latency_display_claims']:
        assert c['canonical_python_4f']==format(c['actual'],'.4f')
        assert c['rounded_matches']==(None if c['claimed_display']is None else format(c['actual'],'.4f')==c['claimed_display'])
    profiles={r['round_id']:r for r in actual['strict_source_profile_conditions']}
    assert all(not profiles[f'R{n}']['all_five_16of16'] for n in (71,72,74))
    assert all(not profiles[f'R{n}']['requested_strict_claim_necessary_conditions_met'] for n in (71,72,74))
    assert profiles['R73']['requested_strict_claim_necessary_conditions_met'] and profiles['R75']['requested_strict_claim_necessary_conditions_met']


def test_actual_seven_points_are_heterogeneous_not_a_physical_or_Cartesian_curve(actual):
    r=actual['declared_context_curves']
    assert [p['round_id']for p in r['distance_points']]==['R60','R61','R70','R62','R69','R73','R75']
    assert [p['round_id']for p in r['flow_points']]==['R71','R64','R60','R63','R72','R74']
    assert not r['flow_observed_necessary_conditions_all_observed']
    assert not r['crossround_independence_or_physical_range_proven']and not r['interpolation_or_unobserved_Cartesian_cells_qualified']
    assert r['exact_lower_knee_claim']['status'].startswith('NOT_IDENTIFIED')
    assert all(c['paired_crossround_p_value']is None for c in actual['historical_descriptive_comparisons'])


def test_highest_eightflow_gain_search_includes_adverse_history_not_just_new_arms(actual):
    h=actual['highest_eight_flow_observed_gain']
    assert {'R37','R38','R47','R57','R63','R67','R72','R74'}==set(h['compared_rounds'])
    assert h['target_arms']==12 and h['no_healthy_only_selection']
    assert h['claim_supported_for_relative_gain']==(h['highest_relative_gain_rounds']==['R74'])
    assert all(x['historical_or_policy_controlled_comparison']is False for x in h['entries'])


def test_highest_gain_does_not_turn_into_unanimity_or_healthy_filter():
    def row(rid,iteration,gp,loss=0):return dict(round_id=rid,iteration=iteration,goodput_mbps=gp,window_kind='primary',active_flow_count=8,bidirectional=True,packet_loss_pct=loss,station_drops=0,policy_key='p')
    records=[row('R74','r74_iter0_stock',100),row('R74','r74_iter1_t',101),row('R37','r37_iter0_stock',100),row('R37','r37_iter1_bad',103,10)]
    h=bb.highest_eight_flow_gain(records)
    assert not h['claim_supported_for_relative_gain'] and h['highest_relative_gain_rounds']==['R37']
    assert h['no_unanimity_or_statistical_promotion_inferred']


def test_mutated_future_input_is_rejected_before_any_content_access(tmp_path,monkeypatch):
    m=tmp_path/'inputs_manifest.json';p=tmp_path/'inputs'/'R76_poison.json'
    m.write_text(json.dumps({'entries':[dict(path=str(p),round=76,sha256='0'*64,bytes=1)]*15}))
    monkeypatch.setattr(bb,'BASE',tmp_path)
    def checked(path):
        if path==p:raise AssertionError('Future content must not be read')
        return dict(sha256=bb.MANIFEST_SHA if path.name=='inputs_manifest.json'else bb.FAMILY_SHA)
    monkeypatch.setattr(bb,'binding',checked)
    with pytest.raises(ValueError,match='owned|Owned'):bb.frozen_inputs()
