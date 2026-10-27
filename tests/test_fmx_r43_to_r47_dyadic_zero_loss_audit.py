"""Synthetic exact-oracle fixtures only, no device/live recipe imports."""
from fractions import Fraction
from itertools import product
import math
import numpy as np
import pytest
from scipy import stats
from analysis.statistics.fmx_r43_to_r47_dyadic_zero_loss_audit import enumerate_fraction_flips,exact_sign_flips,fraction_rank_weights,period_adjusted_estimation,pair_rows,frozen_inputs
from analysis.statistics.fmx_r33_to_r42_exact_holm500_audit import exact_rank
from analysis.statistics.fmx_r16_to_r21_real_crossover_audit import multilevel_design_diagnostics


def independent_oracle(values):
    nonzero=[abs(v) for v in values if v];ranks=stats.rankdata([float(abs(v)) for v in values],method='average') if all(values) else None
    # Independent literal definition; zeros removed before assigning ranks.
    abslist=sorted(nonzero);rank={v:Fraction(sum(i+1 for i,w in enumerate(abslist) if w==v),abslist.count(v)) for v in set(abslist)}
    scores=[rank[abs(v)]*(1 if v>0 else -1) if v else Fraction(0) for v in values]
    sign=[int(v>0)-int(v<0) for v in values]
    coefficients=[scores,sign,values];observed=[abs(sum(v)) for v in coefficients];counts=[0,0,0]
    for signs in product((-1,1),repeat=len(values)):
        for k,w in enumerate(coefficients):counts[k]+=abs(sum(a*b for a,b in zip(w,signs)))>=observed[k]
    return counts


@pytest.mark.parametrize('values',[[0,0,0],[1,-1,2,-2,0],[1,1,1,-10],[1,-3,2,2,-4,0],[Fraction(1,10),Fraction(2,10),Fraction(-3,10),Fraction(4,10)]])
def test_integer_gray_rank_sign_mean_equal_independent_exhaustive_products(values):
    values=[Fraction(v) for v in values];a=enumerate_fraction_flips(values);counts=independent_oracle(values)
    assert [a[k]['extreme_assignments'] for k in ('rank','sign','mean')]==counts
    assert all(a[k]['p_value']==n/2**len(values) for k,n in zip(('rank','sign','mean'),counts))


def test_actual16_assignment_space_and_distinct_rank_sign_mean_statistics():
    d=list(range(1,17));a=exact_sign_flips(d)
    assert a['assignments']==65536
    assert all(a[k]['extreme_assignments']==2 and a[k]['p_value']==2/65536 for k in ('rank','sign','mean'))
    d=[1.,2.,3.,4.,5.,6.,7.,8.,9.,10.,11.,12.,13.,14.,15.,-.25]
    a=exact_sign_flips(d)
    assert a['rank']['p_value']==exact_rank(d)['p_value']
    assert a['sign']['p_value']==34/65536
    assert a['rank']['p_value']!=a['sign']['p_value']
    assert a['mean']['p_value']!=a['sign']['p_value']


def test_binary_float_exact_tail_never_uses_epsilon_or_float_sum():
    d=[.1,.2,-.3,.4,-.125]
    a=exact_sign_flips(d);oracle=independent_oracle([Fraction.from_float(v) for v in d])
    assert [a[k]['extreme_assignments'] for k in ('rank','sign','mean')]==oracle
    assert Fraction(int(a['mean']['observed_exact_numerator']),int(a['mean']['observed_exact_denominator']))==sum((Fraction.from_float(v) for v in d),Fraction(0))/len(d)


@pytest.mark.parametrize('values',[[],[True],[float('inf')],[float('nan')],list(range(21))])
def test_invalid_or_unbounded_values_reject(values):
    with pytest.raises(ValueError):exact_sign_flips(values)


def synthetic_rows(blocks=16,direct=3,period=2,lag=0):
    rows=[]
    for b in range(blocks):
        seq=('A','B') if b%2==0 else ('B','A');previous=None
        for step,t in enumerate(seq):
            value=10+b+direct*(t=='B')+period*step+lag*(previous=='B')
            rows.append(dict(round_id='R43',block_index=b,crossover_step=step,treatment_id=t,observation={'p95_rtt_ms':value,'p99_rtt_ms':value,'goodput_rx_mbps':value},rtts_ms=[value]))
            previous=t
    return rows


def test_named_direct_period_only_model_exact_coefficients_and_full_alias():
    rows=synthetic_rows();a=period_adjusted_estimation(rows,'A','B','p95_rtt_ms')
    assert a['direct_estimate']==3 and a['period_estimate']==2 and a['rank']==a['columns']==18
    assert a['AB_blocks']==a['BA_blocks']==8
    full=multilevel_design_diagnostics(rows)['design']
    assert full['rank']==18 and len(full['columns'])==19 and not full['full_column_rank']
    assert not full['conditional_column_estimability']['current:B']
    assert not full['conditional_column_estimability']['lag:B']
    assert 'No differential carryover' in a['assumptions'][0]
    assert 'p_value' not in a


def test_real_carryover_counterexample_restricted_estimate_is_not_causal_truth():
    rows=synthetic_rows(direct=3,period=2,lag=4);a=period_adjusted_estimation(rows,'A','B','p95_rtt_ms')
    assert a['direct_estimate']==1 and a['period_estimate']==4
    assert a['direct_estimate']!=3
    assert a['status']=='IDENTIFIED_RESTRICTED_MODEL_NOT_CAUSAL_CERTIFICATION'


@pytest.mark.parametrize('damage',['duplicate','missing','wrongstep','mixed','bool_id'])
def test_period_model_never_fabricates_pairs_or_ids(damage):
    rows=synthetic_rows()
    if damage=='duplicate':rows.append(dict(rows[0]))
    elif damage=='missing':rows.pop()
    elif damage=='wrongstep':rows[0]['crossover_step']=2
    elif damage=='mixed':rows[0]['round_id']='R44'
    else:rows[0]['block_index']=True
    with pytest.raises(ValueError):pair_rows(rows,'A','B','p95_rtt_ms')


def test_all_frozen15_inputs_verified_without_following_original_pointers():
    receipts,literal,refs=frozen_inputs()
    assert len(refs)==15 and len(receipts)==5
    assert all(len(x['iterations'])==2 for x in receipts.values())
    assert all(len(a['repetition_blocks'])==16 for x in receipts.values() for a in x['iterations'])


from decimal import Decimal
from analysis.statistics.fmx_r43_to_r47_dyadic_zero_loss_audit import dyadic_mean_audit,build_analysis


def mean_arm(values,reported):
    arm={'observation':{'goodput_rx_mbps':float(reported)},'dl_goodput_mbps':float(reported),'ul_goodput_mbps':0.,'bidir_jain_fairness':1.,'repetition_blocks':[{'total_goodput_mbps':float(v),'dl_goodput_mbps':float(v),'ul_goodput_mbps':0.,'bidir_jain_fairness':1.} for v in values]}
    literal={'observation':{'goodput_rx_mbps':Decimal(reported)},'dl_goodput_mbps':Decimal(reported),'ul_goodput_mbps':0,'bidir_jain_fairness':1,'repetition_blocks':[{'total_goodput_mbps':Decimal(v),'dl_goodput_mbps':Decimal(v),'ul_goodput_mbps':0,'bidir_jain_fairness':1} for v in values]}
    return arm,literal


def test_dyadic_zeroULP_distinct_from_non_dyadic_equal_or_real_summary_error():
    a,l=mean_arm(['.125','.375'],'.25');r=dyadic_mean_audit(a,l)
    assert r['status']=='DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP'
    assert all(v['fraction_delta']=='0' and v['ulp_error']==0 and v['binary_rational_delta']=='0' for v in r['fields'].values())
    a,l=mean_arm(['.1','.1'],'.1');r=dyadic_mean_audit(a,l)
    assert r['status']=='FLOAT_AND_RATIONAL_EXACT_ZERO_ULP_NON_DYADIC_INPUTS'
    a,l=mean_arm(['.125','.375'],'.250000000001');r=dyadic_mean_audit(a,l)
    assert not r['all_fraction_zero'] and not r['all_zero_ulp']
    assert r['status']=='NOT_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP'


@pytest.fixture(scope='module')
def actual():return build_analysis()


def test_actual_corpus_counts_and30_complete16pair_contrasts(actual):
    assert actual['counts']==dict(records=194,new_arms=10,crossed_rows=700,new_crossed_rows=160,matched_ids=262,new_matched_ids=80,sequential_R17=16)
    assert len(actual['contrasts'])==30 and len(actual['requested_win_claims'])==17
    for r in actual['contrasts']:
        assert len(r['pairs'])==16 and len({(u['round_id'],u['block_index']) for u in r['paired_unit_ids']})==16
        assert r['exact_sign_flips']['assignments']==65536
        assert r['exact_sign_flips']['rank']['p_value']==r['exact_rank']['p_value']
        assert r['exact_sign_flips']['sign']['p_value']==r['exact_sign']['p_value']
        assert r['period_adjusted']['AB_blocks']==r['period_adjusted']['BA_blocks']==8


def test_actual_all10source_means_exact_and_period_alias_not_disguised(actual):
    assert len(actual['source_claim_audits'])==10
    for row in actual['source_claim_audits']:
        assert row['dyadic_audit']['status']==row['AG_dyadic_audit']['status']=='DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP'
        assert row['attempted_pings']==row['received_pings']==160 and row['saved_loss_pct']==0
        assert row['chronology_matches'] and row['mac_sums_match'] and row['mac_tx_packets']>0
    for d in actual['design_diagnostics']:
        assert d['design']['rank']==18 and len(d['design']['columns'])==19
        assert not d['design']['full_column_rank'] and d['schedule_agreement']['matches']
    assert actual['R46_vs_R39_tradeoff']['paired_p_value'] is None
    assert actual['R46_vs_R39_tradeoff']['objective_is_not_packet_loss']
    assert actual['R46_vs_R39_tradeoff']['packet_loss_change_pct_points']==0


def test_actual_primary_rank_and_mean_families_never_interchanged(actual):
    f=actual['families']
    assert f['new_rank30_bound500']['known_count']==30 and f['new_rank30_bound500']['unknown_padding_count']==470
    assert f['new_meanflip30_bound500']['known_count']==30 and f['new_meanflip30_bound500']['unknown_padding_count']==470
    assert f['complete_known_rank777_bound777']['known_count']==777
    assert actual['catalog_scope']['complete_primary_Holm500'].startswith('INAPPLICABLE')
    assert 'new_meanflip30_bound500' not in actual['promotion_evidence']['families']
    ids={r['source_hypothesis_id']:r for r in actual['contrasts']}
    for c in actual['promotion_evidence']['contrasts']:
        r=ids[c['source_hypothesis_id']]
        assert c['p_exact_rank']==r['exact_rank']['p_value']
        assert c['holm500_adjusted_p']==f['new_rank30_bound500']['adjusted_p'][r['source_hypothesis_id']]
        assert c['paired_unit_ids']==r['paired_unit_ids']
    assert not actual['automatic_execution_allowed'] and not actual['physical_or_causal_acceptance']
