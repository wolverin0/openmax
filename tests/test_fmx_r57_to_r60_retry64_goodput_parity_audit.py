"""Offline exact-oracle and saved-input tests; no live helper imports."""
from copy import deepcopy
from fractions import Fraction
from itertools import product
import json

import pytest

from analysis.statistics import fmx_r57_to_r60_retry64_goodput_parity_audit as ap


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
    result=ap.enumerate_fraction_flips(values)
    assert [result[k]['extreme_assignments'] for k in ('rank','sign','mean')]==literal_oracle(values)


def test_actual16_sign_count_not_same_as_mean_or_rank_statistic():
    allwins=ap.exact_sign_flips(list(range(1,17)))
    assert allwins['assignments']==65536
    assert all(allwins[k]['extreme_assignments']==2 for k in ('rank','sign','mean'))
    mixed=ap.exact_sign_flips(list(range(1,16))+[-.125])
    assert mixed['sign']['extreme_assignments']==34
    assert mixed['rank']['p_value']!=mixed['sign']['p_value']!=mixed['mean']['p_value']


@pytest.mark.parametrize('bad',[[],[True],[float('nan')],[float('inf')],list(range(21))])
def test_nonfinite_bool_empty_or_exponential_unbounded_inputs_refused(bad):
    with pytest.raises(ValueError):ap.exact_sign_flips(bad)


def rows(lag=0):
    result=[]
    for index in range(16):
        previous=None
        for step,t in enumerate(('A','B') if index%2==0 else ('B','A')):
            value=10+index+3*(t=='B')+2*step+lag*(previous=='B')
            result.append(dict(round_id='R57',block_index=index,crossover_step=step,treatment_id=t,
                observation={'p95_rtt_ms':value},rtts_ms=[value]))
            previous=t
    return result


def test_campaign_specific_pairing_and_period_assumption_no_old_ID_relabel():
    result=ap.period_adjusted_estimation(rows(),'A','B','p95_rtt_ms')
    assert (result['direct_estimate'],result['period_estimate'],result['rank'])==(3,2,18)
    contaminated=ap.period_adjusted_estimation(rows(4),'A','B','p95_rtt_ms')
    assert (contaminated['direct_estimate'],contaminated['period_estimate'])==(1,4)
    assert contaminated['status']=='IDENTIFIED_RESTRICTED_MODEL_NOT_CAUSAL_CERTIFICATION'
    assert 'p_value' not in contaminated
    old=rows();old[0]['round_id']='R56'
    with pytest.raises(ValueError):ap.pair_rows(old,'A','B','p95_rtt_ms')


@pytest.mark.parametrize('damage',['missing','duplicate','mixed','bool_index','wrongstep'])
def test_actual_pair_identity_errors_cannot_be_silently_omitted(damage):
    source=rows()
    if damage=='missing':source.pop()
    elif damage=='duplicate':source.append(deepcopy(source[0]))
    elif damage=='mixed':source[0]['round_id']='R58'
    elif damage=='bool_index':source[0]['block_index']=True
    else:source[0]['crossover_step']=2
    with pytest.raises(ValueError):ap.pair_rows(source,'A','B','p95_rtt_ms')


def declaration():
    payload=dict(coverage_class=0,distance_m=100,slot_time_us=9,ack_timeout_us=18)
    arm=dict(coverage_class=0,distance_m=100,candidate_knobs=dict(coverage_class=0,distance_m=100,ap_state={},cpe_state={}))
    return payload,arm


def test_explicit_timing_declarations_are_not_recipe_application_or_physical_range():
    result=ap.declared_context(*declaration(),dict(coverage_class=0,distance_meters=100))
    assert result['coverage_class']==0 and result['distance_m']==100
    assert result['slot_time_us']==9 and result['ack_timeout_us']==18
    assert result['endpoint_states_originally_omit_distance']
    assert not result['physical_distance_verified'] and not result['effective_runtime_application_verified']


@pytest.mark.parametrize('where,key,value',[
    ('payload','coverage_class',False),('payload','distance_m',100.),('payload','slot_time_us',None),
    ('payload','ack_timeout_us',19),('arm','coverage_class',None),('knobs','distance_m',3000),
    ('knobs','slot_time_us',10),('arm','ack_timeout_us',True)])
def test_timing_unknown_bool_or_conflict_does_not_look_like_explicit_class0(where,key,value):
    payload,arm=declaration();target=payload if where=='payload' else arm if where=='arm' else arm['candidate_knobs']
    target[key]=value
    with pytest.raises(ValueError):ap.declared_context(payload,arm)


def test_decimal_display_goodput_and_true_near_parity_not_noninferiority():
    result=ap.observed_utility('104.8505859375','104.830078125')
    loss=Fraction(result['loss_percent_exact'])
    assert 0<loss<Fraction(1,50)
    assert loss!=Fraction('0.019559')
    assert not result['noninferiority_test']
    assert ap.observed_utility('100','100')['loss_percent_exact']=='0'


def test_telemetry_field_presence_and_package_diff_do_not_make_mechanism_proof():
    assert ap.telemetry_paths({'retransmits':12,'x':{'cwnd':[10,8]}})==['$.x.cwnd']
    a=[{'long_retry_limit':4,'short_retry_limit':7,'aql_by_ac':[[1,2]]}]
    b=[{'long_retry_limit':3,'short_retry_limit':5,'aql_by_ac':[[1,3]]}]
    assert set(ap.changed_coordinates(a,b))=={'[0].long_retry_limit','[0].short_retry_limit','[0].aql_by_ac[0][1]'}


def test_exclusive_output_guard_before_calculation(tmp_path,monkeypatch):
    path=tmp_path/'wave_ap_already.json';path.write_text('preserve')
    monkeypatch.setattr(ap,'BASE',tmp_path)
    monkeypatch.setattr('sys.argv',['audit','--output',str(path)])
    monkeypatch.setattr(ap,'build_analysis',lambda:(_ for _ in ()).throw(AssertionError('must not compute')))
    with pytest.raises(FileExistsError):ap.main()
    assert path.read_text()=='preserve'


def test_all12_frozen_input_hashes_and_rounds_verified():
    receipts,literals,refs,recipes=ap.frozen_inputs()
    assert len(refs)==12 and set(receipts)==set(literals)==set(recipes)=={57,58,59,60}
    assert all(len(a['repetition_blocks'])==16 for r in receipts.values() for a in r['iterations'])


@pytest.fixture(scope='module')
def actual():return ap.build_analysis()


def test_actual220_1116_470_and24_contrasts_no_measurement_pseudoreplication(actual):
    assert actual['counts']==dict(records=220,new_arms=8,crossed_rows=1116,new_crossed_rows=128,matched_ids=470,new_matched_ids=64,sequential_R17=16)
    assert len(actual['contrasts'])==24 and len(actual['source_claim_audits'])==8
    for row in actual['contrasts']:
        assert len(row['pairs'])==len(row['paired_unit_ids'])==16
        assert row['exact_sign_flips']['assignments']==65536
        assert row['exact_sign_flips']['rank']['p_value']==row['exact_rank']['p_value']
        assert row['exact_sign_flips']['sign']['p_value']==row['exact_sign']['p_value']
        assert all(not row['confidence_sets'][k]['whole_real_line'] for k in ('95','99.9'))


def test_actual_four_mean_metrics_pings_health_counter_and_timing_claims(actual):
    assert sum(r['received_pings'] for r in actual['source_claim_audits'])==1280
    for row in actual['source_claim_audits']:
        assert row['dyadic_audit']['status']=='DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP'
        assert row['complete_160_pings'] and row['saved_loss_pct']==row['saved_station_drops']==0
        assert row['saved_restoration_verified'] is True and row['mac_sums_match'] and row['chronology_matches']
        assert row['declared_timing_context']['coverage_class']==0 and row['declared_timing_context']['distance_m']==100
        assert not row['declared_timing_context']['physical_distance_verified']
    assert all(d['design']['rank']==18 and len(d['design']['columns'])==19 for d in actual['design_diagnostics'])


def test_actual_primary_and_secondary_families_and_projection(actual):
    f=actual['families']
    assert f[ap.RANK_FAMILY]['known_count']==f[ap.MEAN_FAMILY]['known_count']==24
    assert f[ap.RANK_FAMILY]['unknown_padding_count']==f[ap.MEAN_FAMILY]['unknown_padding_count']==476
    assert f['complete_known_rank855_bound855']['known_count']==855
    assert actual['catalog_scope']['complete_primary_Holm500'].startswith('INAPPLICABLE')
    assert ap.MEAN_FAMILY not in actual['promotion_evidence']['families']
    by_id={r['source_hypothesis_id']:r for r in actual['contrasts']}
    for projected in actual['promotion_evidence']['contrasts']:
        r=by_id[projected['source_hypothesis_id']]
        assert projected['paired_unit_ids']==r['paired_unit_ids']
        assert projected['p_exact_rank']==r['exact_rank']['p_value']
        assert projected['holm500_adjusted_p']==r['family_adjusted_p'][ap.RANK_FAMILY]
    assert not actual['automatic_execution_allowed'] and not actual['physical_or_causal_acceptance']


def test_actual_claims_are_recomputed_and_mechanism_not_declared_proven(actual):
    for row in actual['requested_win_claims']:
        r=next(r for r in actual['contrasts'] if (r['scope'],r['metric'])==(row['round_id'],row['metric']))
        assert row['actual_favorable']==r['favorable_blocks']
        if row['claimed_favorable'] is not None:assert row['matches']==(row['actual_favorable']==row['claimed_favorable'])
    assert sum(r['claimed_favorable'] is not None for r in actual['requested_win_claims'])==22
    m=actual['R58_mechanism_assessment'];assert m['status']=='HYPOTHESIS_NOT_DEMONSTRATED'
    assert not m['mechanism_causal_acceptance']
    assert all(c['paired_crossround_p_value'] is None and not c['isolated_long_retry_control'] for c in m['crossround_comparisons'])
