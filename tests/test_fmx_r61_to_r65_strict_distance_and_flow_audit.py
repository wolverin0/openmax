"""Pure-host exact-oracle, context and frozen R61-R65 regressions only."""
from copy import deepcopy
from fractions import Fraction
from itertools import product
import json
import pytest
from analysis.statistics import fmx_r61_to_r65_strict_distance_and_flow_audit as at


def declaration(number=61):
    distance,coverage,slot,ack=at.TIMING[number]
    common=dict(distance_m=distance,coverage_class=coverage,slot_time_us=slot,ack_timeout_us=ack)
    payload=deepcopy(common);knobs=deepcopy(common)|dict(ap_state={},cpe_state={})
    return payload,deepcopy(common)|dict(candidate_knobs=knobs)


@pytest.mark.parametrize('number',[61,62,63,64,65])
def test_all_four_timing_fields_are_shared_declarations_not_effective_range(number):
    payload,arm=declaration(number)
    result=at.declared_context(number,payload,arm)
    assert tuple(result[k] for k in ('distance_m','coverage_class','slot_time_us','ack_timeout_us'))==at.TIMING[number]
    assert result['slot_ack_provenance']=='SHARED_PAYLOAD_TREATMENT_KNOBS'
    assert result['endpoint_states_originally_omit_timing']
    assert result['physical_distance_verified'] is result['effective_runtime_application_verified'] is False


@pytest.mark.parametrize('location',['payload','arm','knobs'])
@pytest.mark.parametrize('field',['distance_m','coverage_class','slot_time_us','ack_timeout_us'])
def test_missing_shared_timing_cannot_inherit_root_only_old_provenance(location,field):
    payload,arm=declaration()
    target=payload if location=='payload' else arm if location=='arm' else arm['candidate_knobs']
    target.pop(field)
    with pytest.raises(ValueError):at.declared_context(61,payload,arm)


@pytest.mark.parametrize('field,value',[('coverage_class',True),('distance_m',3000.0),('slot_time_us',28),('ack_timeout_us',None)])
def test_untyped_or_conflicting_timing_rejected(field,value):
    payload,arm=declaration();arm['candidate_knobs'][field]=value
    with pytest.raises(ValueError):at.declared_context(61,payload,arm)


def test_endpoint_conflict_and_legacy_root_only_normalizer_provenance_rejected():
    payload,arm=declaration()
    arm['candidate_knobs']['ap_state']['distance_meters']=6000
    with pytest.raises(ValueError):at.declared_context(61,payload,arm)
    payload,arm=declaration()
    saved=dict(distance_meters=3000,coverage_class=6,certified_wds_evidence=dict(slot_time_us=27,ack_timeout_us=54,slot_ack_source='ROOT_RECEIPT_ONLY'))
    with pytest.raises(ValueError):at.declared_context(61,payload,arm,saved)


def synthetic_profiles():
    contrasts=[];utilities=[]
    for number in at.ROUNDS:
        utilities.append(dict(round_id=f'R{number}',loss_percent_exact='1'))
        for metric in at.METRICS:
            lower=metric in at.METRICS[1:4]
            contrasts.append(dict(scope=f'R{number}',metric=metric,favorable_blocks=15 if number==63 and metric=='p50_rtt_ms' else 16,
                direction='lower' if lower else 'higher',HL_estimate=-1 if lower else 1,family_adjusted_p={at.RANK_FAMILY:.015}))
    return contrasts,utilities


def test_spec_R63_five_unanimous_conflict_is_not_rescued_by_positive_GP_or_Holm():
    contrasts,utility=synthetic_profiles();utility[2]['loss_percent_exact']='-1/20'
    results=at.profile_conditions(contrasts,utility)
    r=next(r for r in results if r['round_id']=='R63')
    assert r['strict_observed_GP_loss_below2'] and r['five_direct_rank_HL_Holm500']
    assert not r['all_five_16of16'] and not r['requested_strict_claim_necessary_conditions_met']
    assert r['failed_unanimity_metrics']==['p50_rtt_ms']
    assert r['spec_R63_qualification_conflict_confirmed']
    assert all(r['status']=='NECESSARY_OBSERVED_CONDITIONS_ONLY_NOT_AU_PROMOTION' for r in results)


def test_strict_boundary_and_direct_test_failure_are_distinct_from_unanimity():
    contrasts,utility=synthetic_profiles();utility[0]['loss_percent_exact']='2'
    c=next(c for c in contrasts if c['scope']=='R65' and c['metric']=='p99_rtt_ms')
    c['family_adjusted_p'][at.RANK_FAMILY]=.2
    rows=at.profile_conditions(contrasts,utility)
    assert not rows[0]['strict_observed_GP_loss_below2']
    assert rows[-1]['all_five_16of16'] and not rows[-1]['five_direct_rank_HL_Holm500']


def test_recipe_AST_records_literals_and_unknown_without_executing():
    text='raise RuntimeError("never execute")\napply_r33_state_with_distance(ap,distance_m=3000)\nobj.apply_r33_state_with_distance(distance_m=unknown)'
    calls=at.recipe_distance_calls(text)
    assert [c['declared_distance_m_literal'] for c in calls]==[3000,None]
    assert all(c['source_text_only_not_execution_or_readback'] for c in calls)


def test_exact_CI_acceptance_membership_matches_independent_small_sign_enumeration():
    values=[1.,2.,2.,3.,4.,8.]
    result=at.exact_effect(values)
    def member(confidence_set,theta):
        return any((c['lower'] is None or theta>c['lower'] or theta==c['lower'] and c['lower_closed']) and
                   (c['upper'] is None or theta<c['upper'] or theta==c['upper'] and c['upper_closed']) for c in confidence_set['components'])
    for theta in [-20.,0.,1.,1.5,2.,2.5,3.,4.,8.,20.]:
        shifted=[Fraction.from_float(v-theta) for v in values]
        rank_p=literal_oracle(shifted)[0]/64
        assert member(result['confidence_sets']['95'],theta)==(rank_p>.05)
        assert member(result['confidence_sets']['99.9'],theta)==(rank_p>.001)
        assert not member(result['confidence_sets']['95'],theta) or member(result['confidence_sets']['99.9'],theta)


def test_exact_percent_displays_do_not_replace_fraction_or_noninferiority():
    utility=at.observed_utility('104.9736328125','105.02734375')
    assert Fraction(utility['loss_percent_exact'])<0
    assert not utility['noninferiority_test']
    assert -Fraction(utility['loss_percent_exact'])!=Fraction('0.051166')


def test_all15_frozen_input_hashes_and_current_round_identity_only():
    receipts,literals,refs,recipes=at.frozen_inputs()
    assert len(refs)==15 and set(receipts)==set(literals)==set(recipes)==set(at.ROUNDS)
    assert all(len(a['repetition_blocks'])==16 for r in receipts.values() for a in r['iterations'])


@pytest.fixture(scope='module')
def actual():return at.build_analysis()


def test_actual_counts_and_complete_exact_contrast_units(actual):
    assert actual['counts']==dict(records=230,new_arms=10,crossed_rows=1276,new_crossed_rows=160,matched_ids=550,new_matched_ids=80,sequential_R17=16)
    assert len(actual['contrasts'])==30 and len(actual['source_claim_audits'])==10
    assert sum(len(r['pairs']) for r in actual['contrasts'])==480
    assert sum(len(r['confidence_sets']) for r in actual['contrasts'])==60
    for r in actual['contrasts']:
        assert len(r['pairs'])==len(r['paired_unit_ids'])==16
        assert r['exact_sign_flips']['assignments']==65536
        assert r['exact_sign_flips']['rank']['p_value']==r['exact_rank']['p_value']
        assert r['exact_sign_flips']['sign']['p_value']==r['exact_sign']['p_value']


def test_actual_all40_means1600_pings_context_chronology_and_health(actual):
    assert sum(r['received_pings'] for r in actual['source_claim_audits'])==1600
    for r in actual['source_claim_audits']:
        assert r['dyadic_audit']['status']=='DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP'
        assert r['complete_160_pings'] and r['saved_loss_pct']==r['saved_station_drops']==0
        assert r['saved_restoration_verified'] is True and r['mac_sums_match'] and r['chronology_matches']
        assert not r['declared_timing_context']['physical_distance_verified']
        assert r['declared_timing_context']['slot_ack_provenance']=='SHARED_PAYLOAD_TREATMENT_KNOBS'
    assert all(d['design']['rank']==18 and len(d['design']['columns'])==19 for d in actual['design_diagnostics'])


def test_actual_complete_families_and_exact_projection_no_transfer(actual):
    families=actual['families']
    assert families[at.RANK_FAMILY]['known_count']==families[at.MEAN_FAMILY]['known_count']==30
    assert families[at.RANK_FAMILY]['unknown_padding_count']==families[at.MEAN_FAMILY]['unknown_padding_count']==470
    assert families['complete_known_rank885_bound885']['known_count']==885
    assert at.MEAN_FAMILY not in actual['promotion_evidence']['families']
    by_id={r['source_hypothesis_id']:r for r in actual['contrasts']}
    for row in actual['promotion_evidence']['contrasts']:
        source=by_id[row['source_hypothesis_id']]
        assert row['p_exact_rank']==source['exact_rank']['p_value']
        assert row['paired_unit_ids']==source['paired_unit_ids']
        assert row['round_ids']==[source['scope']]
        assert row['holm500_adjusted_p']==source['family_adjusted_p'][at.RANK_FAMILY]
    assert not actual['automatic_execution_allowed'] and not actual['physical_or_causal_acceptance']


def test_actual_win_claims_and_spec_conflict_preserved(actual):
    assert len(actual['requested_win_claims'])==30
    for claim in actual['requested_win_claims']:
        source=next(c for c in actual['contrasts'] if (c['scope'],c['metric'])==(claim['round_id'],claim['metric']))
        assert claim['actual_favorable']==source['favorable_blocks']
        if claim['claimed_favorable'] is not None:assert claim['matches']==(claim['claimed_favorable']==claim['actual_favorable'])
    r=next(x for x in actual['strict_source_profile_conditions'] if x['round_id']=='R63')
    assert r['failed_unanimity_metrics']==['p50_rtt_ms']
    assert not r['requested_strict_claim_necessary_conditions_met']
    assert r['spec_R63_qualification_conflict_confirmed']
    assert all(x['paired_crossround_p_value'] is None and not x['causal_acceptance'] for x in actual['historical_descriptive_comparisons'])


def test_actual_claim_metrics_use_source_literals_and_report_display_differences(actual):
    means=[c for c in actual['numerical_source_claims'] if c['metric']=='goodput_mbps']
    assert len(means)==10
    assert all(c['matches']==(Fraction(str(c['actual']))==Fraction(c['claimed_literal'])) for c in means)
    assert len(actual['stated_latency_display_claims'])==30
    for c in actual['stated_latency_display_claims']:
        assert c['canonical_python_4f']==format(c['actual'],'.4f')
        assert c['rounded_matches']==(format(c['actual'],'.4f')==c['claimed_display'])


def test_historical_context_retains_declared_nested_timing_without_class_defaults():
    """Typed-asdict lacks extra top-level keys, but nested provenance survives."""
    records=[]
    timing={57:(9,18),60:(9,18),61:(27,54),62:(48,96),63:(9,18),64:(9,18),65:(9,18)}
    for number in (52,53,55,57,60,61,62,63,64,65):
        distance,coverage=(3000,6) if number in (52,61) else (6000,13) if number in (53,62) else (None,None) if number==55 else (100,0)
        nested=dict(zip(('slot_time_us','ack_timeout_us'),timing[number])) if number in timing else {}
        records.append(dict(round_id=f'R{number}',iteration=f'r{number}_iter1_fixture',policy_key='[]',
            workload_regime='bidir_6flow',active_flow_count=6,distance_meters=distance,coverage_class=coverage,
            certified_wds_evidence=nested,goodput_mbps=100.,ul_goodput_mbps=20.,p95_ms=30.,p99_ms=40.,jain_fairness=.8))
    result=at.historical_comparisons(records)
    observed={}
    for row in result:
        for rid,context in zip((row['control_round'],row['target_round']),row['recorded_contexts']):
            observed[rid]=(context['slot_time_us'],context['ack_timeout_us'])
    assert {rid:observed[f'R{rid}'] for rid in timing}==timing
    assert all(observed[f'R{number}']==(None,None) for number in (52,53,55))
    # An explicit top-level unknown must not be replaced by nested or class data.
    row=next(r for r in records if r['round_id']=='R61')
    row['slot_time_us']=None;row['ack_timeout_us']=55
    result=at.historical_comparisons(records)
    context=next(r for r in result if r['target_round']=='R61')['recorded_contexts'][1]
    assert context['slot_time_us'] is None and context['ack_timeout_us']==55


def literal_oracle(values):
    absolute=sorted(abs(v) for v in values if v)
    ranks={v:sum((Fraction(i+1) for i,w in enumerate(absolute) if w==v),Fraction())/absolute.count(v) for v in set(absolute)}
    coefficients=[[ranks[abs(v)]*(1 if v>0 else -1) if v else 0 for v in values],
        [int(v>0)-int(v<0) for v in values],values]
    return [sum(abs(sum(a*s for a,s in zip(weights,signs)))>=abs(sum(weights))
                for signs in product((-1,1),repeat=len(values))) for weights in coefficients]

@pytest.mark.parametrize('data',[[0,0,0],[1,1,-1,2,-2,0],[.1,.2,-.3,.4],[1,2,3,4,-.125]])
def test_generic_exact_engine_matches_independent_literal_products(data):
    values=[Fraction.from_float(float(v)) for v in data]
    result=at.enumerate_fraction_flips(values)
    assert [result[k]['extreme_assignments'] for k in ('rank','sign','mean')]==literal_oracle(values)

def test_sixteen_sign_count_not_same_as_mean_or_rank_statistic():
    allwins=at.exact_sign_flips(list(range(1,17)))
    assert allwins['assignments']==65536
    assert all(allwins[k]['extreme_assignments']==2 for k in ('rank','sign','mean'))
    mixed=at.exact_sign_flips(list(range(1,16))+[-.125])
    assert mixed['sign']['extreme_assignments']==34
    assert mixed['rank']['p_value']!=mixed['sign']['p_value']!=mixed['mean']['p_value']

@pytest.mark.parametrize('bad',[[],[True],[float('nan')],[float('inf')],list(range(21))])
def test_nonfinite_bool_empty_or_exponential_unbounded_inputs_refused(bad):
    with pytest.raises(ValueError):at.exact_sign_flips(bad)

def rows(lag=0):
    result=[]
    for index in range(16):
        previous=None
        for step,t in enumerate(('A','B') if index%2==0 else ('B','A')):
            value=10+index+3*(t=='B')+2*step+lag*(previous=='B')
            result.append(dict(round_id='R61',block_index=index,crossover_step=step,treatment_id=t,
                observation={'p95_rtt_ms':value},rtts_ms=[value]))
            previous=t
    return result

def test_campaign_specific_pairing_and_period_assumption_no_old_ID_relabel():
    result=at.period_adjusted_estimation(rows(),'A','B','p95_rtt_ms')
    assert (result['direct_estimate'],result['period_estimate'],result['rank'])==(3,2,18)
    contaminated=at.period_adjusted_estimation(rows(4),'A','B','p95_rtt_ms')
    assert (contaminated['direct_estimate'],contaminated['period_estimate'])==(1,4)
    assert contaminated['status']=='IDENTIFIED_RESTRICTED_MODEL_NOT_CAUSAL_CERTIFICATION'
    assert 'p_value' not in contaminated
    old=rows();old[0]['round_id']='R60'
    with pytest.raises(ValueError):at.pair_rows(old,'A','B','p95_rtt_ms')

@pytest.mark.parametrize('damage',['missing','duplicate','mixed','bool_index','wrongstep'])
def test_pair_identity_errors_cannot_be_silently_omitted(damage):
    source=rows()
    if damage=='missing':source.pop()
    elif damage=='duplicate':source.append(deepcopy(source[0]))
    elif damage=='mixed':source[0]['round_id']='R62'
    elif damage=='bool_index':source[0]['block_index']=True
    else:source[0]['crossover_step']=2
    with pytest.raises(ValueError):at.pair_rows(source,'A','B','p95_rtt_ms')

def test_exclusive_output_guard_before_calculation(tmp_path,monkeypatch):
    path=tmp_path/'wave_at_already.json';path.write_text('preserve')
    monkeypatch.setattr(at,'BASE',tmp_path)
    monkeypatch.setattr('sys.argv',['audit','--output',str(path)])
    monkeypatch.setattr(at,'build_analysis',lambda:(_ for _ in ()).throw(AssertionError('must not compute')))
    with pytest.raises(FileExistsError):at.main()
    assert path.read_text()=='preserve'
