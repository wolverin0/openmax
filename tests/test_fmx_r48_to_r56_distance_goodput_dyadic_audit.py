"""Pure local statistical/oracle fixtures and frozen saved-input checks only."""
from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from itertools import product
import json

import pytest

from analysis.statistics.fmx_r48_to_r56_distance_goodput_dyadic_audit import (
    METRICS, RANK_FAMILY, MEAN_FAMILY, build_analysis, claimed_win_profiles,
    descriptive_pareto, dyadic_mean_audit, enumerate_fraction_flips, exact_sign_flips,
    frozen_inputs, numeric_spec_claims, observed_utility, pair_rows,
    period_adjusted_estimation, record_dict, source_arm_audit)


def independent_counts(values):
    absolute=sorted(abs(v) for v in values if v)
    rank={v:sum((Fraction(i+1) for i,w in enumerate(absolute) if w==v),Fraction())/absolute.count(v) for v in set(absolute)}
    weights=[[rank[abs(v)]*(1 if v>0 else -1) if v else 0 for v in values],
             [int(v>0)-int(v<0) for v in values],values]
    return [sum(abs(sum(w*s for w,s in zip(ws,signs)))>=abs(sum(ws))
                for signs in product((-1,1),repeat=len(values))) for ws in weights]


@pytest.mark.parametrize('values',[[0,0,0],[1,-1,2,-2,0],[1,2,3,-.125],[.1,.2,-.3,.4],[1,1,-1,2,-2,3]])
def test_reused_exact_engine_matches_independent_literal_products(values):
    fractions=[Fraction.from_float(float(v)) for v in values]
    actual=enumerate_fraction_flips(fractions)
    assert [actual[k]['extreme_assignments'] for k in ('rank','sign','mean')]==independent_counts(fractions)


def test_65536_assignment_space_and_sign_is_not_rank_or_mean():
    allpositive=exact_sign_flips(list(range(1,17)))
    assert allpositive['assignments']==65536
    assert all(allpositive[k]['extreme_assignments']==2 for k in ('rank','sign','mean'))
    almost=exact_sign_flips(list(range(1,16))+[-.25])
    assert almost['sign']['extreme_assignments']==34
    assert almost['rank']['p_value']!=almost['sign']['p_value']!=almost['mean']['p_value']


@pytest.mark.parametrize('bad',[[],[True],[float('nan')],[float('inf')],list(range(21))])
def test_nonfinite_bool_and_unbounded_inference_rejects(bad):
    with pytest.raises(ValueError):exact_sign_flips(bad)


@pytest.mark.parametrize('target,lt,le',[('98',False,True),('98.000000000001',True,True),('97.999999999999',False,False)])
def test_strict_and_nonstrict_observed_floor_are_fraction_distinct(target,lt,le):
    result=observed_utility('100',target)
    assert result['passes_strict_less_than_2_percent'] is lt
    assert result['passes_observed_at_most_2_percent'] is le
    assert not result['noninferiority_test']


def test_r50_literal_gp_floor_does_not_entail_lower_retry_or_policy_acceptance():
    result=observed_utility('109.046875','107.6826171875')
    assert result['passes_strict_less_than_2_percent']
    assert Fraction(result['loss_percent_exact'])==Fraction(34925,27916)
    assert 'eligible' not in result and 'retry' not in result


def synthetic_rows(lag=0):
    rows=[]
    for b in range(16):
        previous=None
        for step,t in enumerate(('A','B') if b%2==0 else ('B','A')):
            value=10+b+3*(t=='B')+2*step+lag*(previous=='B')
            rows.append(dict(round_id='R48',block_index=b,crossover_step=step,treatment_id=t,
                observation={'p95_rtt_ms':value},rtts_ms=[value]))
            previous=t
    return rows


def test_restricted_period_estimate_preserves_explicit_carryover_counterexample():
    simple=period_adjusted_estimation(synthetic_rows(),'A','B','p95_rtt_ms')
    carry=period_adjusted_estimation(synthetic_rows(4),'A','B','p95_rtt_ms')
    assert (simple['direct_estimate'],simple['period_estimate'],simple['rank'])==(3,2,18)
    assert (carry['direct_estimate'],carry['period_estimate'])==(1,4)
    assert carry['status']=='IDENTIFIED_RESTRICTED_MODEL_NOT_CAUSAL_CERTIFICATION'
    assert not any(k=='p_value' for k in carry)


@pytest.mark.parametrize('damage',['missing','duplicate','mixed','bool_id'])
def test_pair_identifiers_never_invented_or_silently_dropped(damage):
    rows=synthetic_rows()
    if damage=='missing':rows.pop()
    elif damage=='duplicate':rows.append(deepcopy(rows[0]))
    elif damage=='mixed':rows[0]['round_id']='R49'
    else:rows[0]['block_index']=True
    with pytest.raises(ValueError):pair_rows(rows,'A','B','p95_rtt_ms')


def point(name,coverage=None,gp=100,p95=10):
    return dict(id=name,policy_id=name,context={'workload_regime':'bidir_6flow','coverage_class':coverage},
        summary=dict(goodput_mbps=gp,ul_goodput_mbps=20,jain_fairness=.75,p50_ms=5,p95_ms=p95,p99_ms=20))


def test_pareto_compares_only_same_context_and_keeps_gain_cost_tradeoffs():
    points=[point('old'),point('fast',gp=90,p95=5),point('dominated',gp=80,p95=12),point('other',coverage=6,gp=200,p95=1)]
    result=descriptive_pareto(points);groups=result['groups']
    assert len(groups)==2 and result['paired_p_value'] is None
    local=next(g for g in groups if g['context']['coverage_class'] is None)
    state={p['id']:p for p in local['points']}
    assert state['old']['nondominated'] and state['fast']['nondominated']
    assert not state['dominated']['nondominated']
    assert 'other' not in state['dominated']['dominated_by']


def test_dataclass_property_policy_identity_not_lost_by_asdict():
    @dataclass
    class Record:
        iteration:str='A'
        @property
        def policy_key(self):return 'FULL_EXACT_AP_CPE_COORDINATES'
    assert record_dict(Record())['policy_key']=='FULL_EXACT_AP_CPE_COORDINATES'


def test_all27_frozen_inputs_are_hash_checked_without_original_reference_reads():
    receipts,literals,refs=frozen_inputs()
    assert len(refs)==27 and len(receipts)==len(literals)==9
    assert all(len(a['repetition_blocks'])==16 for r in receipts.values() for a in r['iterations'])


@pytest.fixture(scope='module')
def actual():return build_analysis()


def test_actual212_988_406_and54_complete_contrasts(actual):
    assert actual['counts']==dict(records=212,new_arms=18,crossed_rows=988,new_crossed_rows=288,matched_ids=406,new_matched_ids=144,sequential_R17=16)
    assert len(actual['contrasts'])==54 and len(actual['source_claim_audits'])==18
    for row in actual['contrasts']:
        assert len(row['pairs'])==len(row['paired_unit_ids'])==16
        assert row['exact_sign_flips']['assignments']==65536
        assert row['exact_sign_flips']['rank']['p_value']==row['exact_rank']['p_value']
        assert row['exact_sign_flips']['sign']['p_value']==row['exact_sign']['p_value']


def test_actual_dyadic_counts_chronology_mac_and_health_reported_not_physical(actual):
    for row in actual['source_claim_audits']:
        assert row['dyadic_audit']['status']=='DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP'
        assert row['attempted_pings']==row['received_pings']==160 and row['complete_160_pings']
        assert row['saved_loss_pct']==row['saved_station_drops']==0 and row['saved_restoration_verified'] is True
        assert row['chronology_matches'] and row['mac_sums_match'] and row['mac_tx_packets']>0
        assert not row['independent_device_health_verified']
    assert sum(x['received_pings'] for x in actual['source_claim_audits'])==2880
    assert all(d['design']['rank']==18 and len(d['design']['columns'])==19 and not d['design']['full_column_rank'] for d in actual['design_diagnostics'])


def test_actual_prespecified_families_and_projection_never_transfer_mean_test(actual):
    f=actual['families'];assert f[RANK_FAMILY]['known_count']==f[MEAN_FAMILY]['known_count']==54
    assert f[RANK_FAMILY]['unknown_padding_count']==f[MEAN_FAMILY]['unknown_padding_count']==446
    assert f['complete_known_rank831_bound831']['known_count']==831
    assert MEAN_FAMILY not in actual['promotion_evidence']['families']
    assert actual['catalog_scope']['complete_primary_Holm500'].startswith('INAPPLICABLE')
    indexed={r['source_hypothesis_id']:r for r in actual['contrasts']}
    for c in actual['promotion_evidence']['contrasts']:
        r=indexed[c['source_hypothesis_id']]
        assert c['p_exact_rank']==r['exact_rank']['p_value']
        assert c['holm500_adjusted_p']==f[RANK_FAMILY]['adjusted_p'][c['source_hypothesis_id']]
        assert c['paired_unit_ids']==r['paired_unit_ids']
    assert not actual['automatic_execution_allowed'] and not actual['physical_or_causal_acceptance']


def test_actual_spec_differences_and_r50_retry_adverse_do_not_erase_gp_floor(actual):
    claims=actual['numeric_spec_claims'];r48=next(c for c in claims if c['round_id']=='R48' and '_iter0_' in c['iteration'])
    assert r48['actual']==103.5068359375 and not r48['matches']
    r50=next(r for r in actual['observed_utility'] if r['round_id']=='R50')
    assert r50['passes_strict_less_than_2_percent'] and not r50['target_retry_lower']
    assert len(actual['requested_win_claims'])==45
    assert sum(c['claimed_favorable'] is not None for c in actual['requested_win_claims'])==42
    rows={c['source_hypothesis_id']:c for c in actual['contrasts']}
    for claim in actual['requested_win_claims']:
        match=next(r for r in rows.values() if r['scope']==claim['round_id'] and r['metric']==claim['metric'])
        assert claim['actual_favorable']==match['favorable_blocks']
        if claim['matches'] is not None:assert claim['matches']==(claim['claimed_favorable']==claim['actual_favorable'])


def test_actual108_marginal_confidence_sets_finite_and_nested_not_simultaneous(actual):
    for row in actual['contrasts']:
        narrow,wide=(row['confidence_sets'][k] for k in ('95','99.9'))
        assert narrow['confidence']==.95 and wide['confidence']==.999
        assert narrow['independent_blocks']==wide['independent_blocks']==16
        assert not narrow['whole_real_line'] and not wide['whole_real_line']
        for ci in (narrow,wide):
            assert ci['components'] and all(c['lower'] is not None and c['upper'] is not None for c in ci['components'])
            assert min(c['lower'] for c in ci['components'])<=row['HL_estimate']<=max(c['upper'] for c in ci['components'])
        assert min(c['lower'] for c in wide['components'])<=min(c['lower'] for c in narrow['components'])
        assert max(c['upper'] for c in wide['components'])>=max(c['upper'] for c in narrow['components'])


def test_source_arm_health_failure_retained_not_silently_excluded(actual):
    receipts,literals,_=frozen_inputs();arm=deepcopy(receipts[48]['iterations'][0]);literal=literals[48]['iterations'][0]
    arm['repetition_blocks'][0]['pings_rcvd']-=1
    arm['repetition_blocks'][0]['observation']['restoration_verified']=False
    arm['observation'].update(packet_loss_pct=.625,station_drops=1,restoration_verified=False)
    old=next(r for r in actual['source_claim_audits'] if r['round_id']=='R48' and '_iter0_' in r['iteration'])
    saved=old['summary']|dict(policy_key=old['policy_id'])|old['context']
    audit=source_arm_audit(48,arm,literal,saved)
    assert audit['attempted_pings']==160 and audit['received_pings']==159
    assert not audit['complete_160_pings'] and audit['saved_loss_pct']==.625
    assert audit['saved_station_drops']==1 and audit['saved_restoration_verified'] is False
    assert audit['block_health'][0]['restoration_verified'] is False
