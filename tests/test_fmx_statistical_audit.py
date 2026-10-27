"""Disposable host fixtures; no acquisition or target execution."""
from copy import deepcopy
from fractions import Fraction
from itertools import product
import json
import numpy as np
import pytest
from scipy.special import ndtr,ndtri
from orchestration.autoresearch import fmx_statistical_audit as bf


def rows():
    result=[]
    for i in range(16):
        for step,t in enumerate(('A','B')if i%2==0 else('B','A')):
            v=10+i+3*(t=='B')+2*step
            result.append(dict(round_id='R76',block_index=i,crossover_step=step,treatment_id=t,
                observation=dict(p95_rtt_ms=v),mac_tx_packets_delta=100+i,mac_tx_retries_delta=2+(t=='B'),counter_interface='phy0-ap0.sta1'))
    return result


@pytest.mark.parametrize('damage',['missing','duplicate','mixed','future','bool_index','step','missing_metric'])
def test_pairing_never_relabels_drops_or_pairs_crossround(damage):
    r=rows()
    if damage=='missing':r.pop()
    elif damage=='duplicate':r.append(deepcopy(r[0]))
    elif damage=='mixed':r[0]['round_id']='R77'
    elif damage=='future':r[0]['round_id']='R81'
    elif damage=='bool_index':r[0]['block_index']=True
    elif damage=='step':r[0]['crossover_step']=2
    else:r[0]['observation'].pop('p95_rtt_ms')
    with pytest.raises(ValueError):bf.pair_rows(r,'A','B','p95_rtt_ms')


@pytest.mark.parametrize('key,value',[('mac_tx_packets_delta',0),('mac_tx_packets_delta',None),('mac_tx_packets_delta',True),
    ('mac_tx_packets_delta',100.),('mac_tx_retries_delta',-1),('mac_tx_retries_delta',None),('mac_tx_retries_delta',False),
    ('counter_interface','phy0-ap0'),('counter_interface',None)])
def test_retry_needs_station_identity_positive_denominator_not_reported_rate(key,value):
    r=rows()[0];r[key]=value;r['mac_retry_rate']=0
    with pytest.raises(ValueError):bf.retry_fraction(r)


def test_retry_pairs_use_rates_not_aggregate_or_count_difference():
    r=rows();r[0]['mac_tx_packets_delta']=100;r[0]['mac_tx_retries_delta']=10
    r[1]['mac_tx_packets_delta']=1000;r[1]['mac_tx_retries_delta']=20
    p=bf.pair_rows(r,'A','B','wds_mac_retry_rate')[0]
    assert p['difference']==pytest.approx(-.08)
    assert bf.retry_fraction(r[0])==Fraction(1,10)
    assert bf.retry_fraction(r[1])==Fraction(1,50)


@pytest.mark.parametrize('values',[[],[1,2],[1,2,True],[1,2,float('nan')],[1,2,float('inf')],['1',2,3],[[1],2,3]])
def test_bootstrap_rejects_bad_numeric_values(values):
    with pytest.raises((ValueError,TypeError)):bf.paired_bca_hl(values)


@pytest.mark.parametrize('confidence',[0,1,-.1,float('nan'),True])
def test_bootstrap_rejects_invalid_confidence(confidence):
    with pytest.raises(ValueError):bf.paired_bca_hl([1,2,3,4],confidence=confidence)


@pytest.mark.parametrize('damage',['float','negative','bound','shape','bool'])
def test_resample_index_identity_is_not_silently_cast(damage):
    index=bf.bootstrap_indices(4,50)
    if damage=='float':index=index.astype(float)
    elif damage=='negative':index[0,0]=-1
    elif damage=='bound':index[0,0]=4
    elif damage=='shape':index=index[:,:3]
    else:index=index.astype(bool)
    with pytest.raises(ValueError):bf.paired_bca_hl([1,2,3,4],resamples=50,resample_indices=index)


def reference(values,indices):
    def hl(x):return float(np.median([(a+b)/2 for i,a in enumerate(x)for b in x[i:]]))
    theta=hl(values);boots=np.array([hl([values[i]for i in ix])for ix in indices])
    jack=np.array([hl(values[:i]+values[i+1:])for i in range(len(values))]);v=jack.mean()-jack
    a=np.sum(v**3)/(6*np.sum(v**2)**1.5)
    z0=ndtri((np.sum(boots<theta)+np.sum(boots==theta)/2)/len(boots))
    probs=ndtr(z0+(z0+ndtri([.025,.975]))/(1-a*(z0+ndtri([.025,.975]))))
    return np.quantile(boots,probs),probs,theta


@pytest.mark.parametrize('values',[[0,1,1,2,4,10],[1,2,3,5,8,13],[-3,-3,0,1,1,7]])
def test_bca_matches_independent_scalar_walsh_jackknife_midtie_oracle(values):
    indices=bf.bootstrap_indices(len(values),1000)
    result=bf.paired_bca_hl(values,resample_indices=indices,resamples=1000)
    interval,probabilities,theta=reference(values,indices)
    assert result['status']=='APPROXIMATE_PAIRED_BCA_SENSITIVITY'
    assert result['observed_HL']==theta
    assert result['interval']==pytest.approx(interval,rel=1e-12,abs=1e-12)
    assert result['adjusted_probabilities']==pytest.approx(probabilities)
    assert result['bias_equal']>0
    assert not result['exact_interval'] and not result['promotion_input']


def test_constant_degenerate_has_no_fabricated_interval():
    result=bf.paired_bca_hl([4]*16)
    assert result['status']=='UNAVAILABLE'and result['interval']is None
    assert result['reason']=='CONSTANT_BOOTSTRAP_DISTRIBUTION'


def test_deterministic_common_resamples_and_translation_positive_scale():
    x=[i*i/8 for i in range(16)];indices=bf.bootstrap_indices(16)
    a=bf.paired_bca_hl(x,resample_indices=indices);b=bf.paired_bca_hl([2*v+3 for v in x],resample_indices=indices)
    assert np.array_equal(indices,bf.bootstrap_indices(16))
    assert a['resample_indices_sha256']==b['resample_indices_sha256']
    assert b['interval']==pytest.approx([2*v+3 for v in a['interval']])
    assert bf.paired_bca_hl(x,resample_indices=indices)==a


def test_exact_rank_sign_mean_have_independent_exhaustive_oracle_and_zeros():
    x=[-5,0,1,1,2,8]
    result=bf.exact_sign_flips(x)
    observed=abs(sum(x));sums=[abs(sum(a*b for a,b in zip(x,s)))for s in product((-1,1),repeat=len(x))]
    assert result['mean']['p_value']==sum(v>=observed for v in sums)/len(sums)
    effect=bf.exact_effect(x)
    assert result['rank']['p_value']==effect['exact_rank']['p_value']
    assert result['sign']['p_value']==effect['exact_sign']['p_value']
    assert result['mean']['p_value']!=result['sign']['p_value']


def test_period_model_preserves_alias_assumptions_not_causal_p():
    r=bf.period_adjusted_estimation(rows(),'A','B','p95_rtt_ms')
    assert r['rank']==r['columns']==18 and r['AB_blocks']==r['BA_blocks']==8
    assert r['direct_estimate']==pytest.approx(3)and r['period_estimate']==pytest.approx(2)
    assert r['status']=='IDENTIFIED_RESTRICTED_MODEL_NOT_CAUSAL_CERTIFICATION'


@pytest.mark.parametrize('n',[76,77,78,79,80])
def test_context_is_saved_shared_declaration_not_physical_or_effective(n):
    d,c,s,a=bf.TIMING[n];common=dict(distance_m=d,coverage_class=c,slot_time_us=s,ack_timeout_us=a)
    arm=deepcopy(common)|dict(candidate_knobs=deepcopy(common)|dict(ap_state={},cpe_state={}))
    result=bf.declared_context(n,common,arm)
    assert not result['physical_distance_verified']and not result['effective_runtime_application_verified']
    arm['candidate_knobs']['slot_time_us']=None
    with pytest.raises(ValueError):bf.declared_context(n,common,arm)


def test_context_none_does_not_fall_back_and_unknown_never_inherits_class():
    x=dict(coverage_class=16,distance_meters=7500,slot_time_us=None,certified_wds_evidence=dict(slot_time_us=57,ack_timeout_us=114))
    assert bf.recorded_context(x)['slot_time_us']is None
    assert bf.recorded_context(x)['ack_timeout_us']==114
    assert bf.recorded_context({'coverage_class':16})['slot_time_us']is None


def test_frozen_recipe_preserves_35_metrics_and_separate_980_scope():
    plan=json.loads((bf.BASE/'wave_bf_family_and_bootstrap_recipe.json').read_text(encoding='utf-8'))
    assert len(plan['hypotheses'])==35
    assert plan['complete_known_rank']['known']==980
    assert plan['primary_rank_family']['padding_p1']==465
    assert 'wds_mac_retry_rate'in plan['metrics']


@pytest.mark.parametrize('number',[76,77,78,79,80])
def test_owned_frozen_source_all16_station_pairs_retained(number):
    receipts,_,_,_=bf.frozen_inputs();payload=receipts[number];group=[]
    for arm in payload['iterations']:
        bf.declared_context(number,payload,arm)
        for row in arm['repetition_blocks']:
            group.append(deepcopy(row)|dict(round_id=f'R{number}',treatment_id=arm['commit'],counter_interface='phy0-ap0.sta1'))
    a,b=[a['commit']for a in payload['iterations']]
    pairs=bf.pair_rows(group,a,b,'wds_mac_retry_rate')
    assert len(pairs)==16 and len({p['block_index']for p in pairs})==16
    assert {p['sequence']for p in pairs}=={'AB','BA'}
    assert len(group)==32 and all(bf.retry_fraction(row)>=0 for row in group)


def test_rank_confidence_sets_keep_components_and_alpha_monotonicity():
    effect=bf.exact_effect([float(i)for i in range(1,17)])
    assert effect['exact_rank']['p_value']==2/65536
    assert effect['exact_sign']['p_value']==2/65536
    # The engine exposes inversion sets, not a percentile-bootstrap substitute.
    assert len(effect['confidence_sets'])==2
    assert effect['HL_estimate']==8.5


def test_retry_is_not_accidentally_added_to_five_QoE_unanimity():
    contrasts=[];utilities=[]
    for n in bf.ROUNDS:
        utilities.append(dict(round_id=f'R{n}',loss_percent_exact='1',target_retry_lower=False))
        for metric in bf.METRICS:
            contrasts.append(dict(scope=f'R{n}',metric=metric,favorable_blocks=0 if metric=='wds_mac_retry_rate' else 16,
                direction='lower'if metric in bf.LOWER else'higher',HL_estimate=-1 if metric in bf.LOWER else 1,
                family_adjusted_p={bf.RANK_FAMILY:.01}))
    result=bf.profile_conditions(contrasts,utilities)
    assert all(r['all_five_16of16']and r['requested_strict_necessary_conditions_met']for r in result)
    assert all(not r['target_retry_lower']for r in result)


# BJ additions; all prior BF test bodies above remain unchanged.
def bj_payload(number=81):
    d,c,s,a=bf.BJ_TIMING[number];regime,flows,bidir=bf.BJ_REGIMES[number]
    common=dict(distance_m=d,coverage_class=c,slot_time_us=s,ack_timeout_us=a,traffic_regime=regime,active_flow_count=flows,bidirectional=bidir)
    active='dl_goodput_mbps'if number==81 else'ul_goodput_mbps';inactive='ul_goodput_mbps'if number==81 else'dl_goodput_mbps'
    arms=[]
    for treatment in('A','B'):
        blocks=[]
        for i in range(16):
            v=100+i+(treatment=='B')
            blocks.append(dict(block_index=i,crossover_step=(i%2)if treatment=='A' else 1-i%2,total_goodput_mbps=v,
                **{active:v,inactive:0},bidir_jain_fairness=.5,observation=dict(goodput_rx_mbps=v,jain_fairness=.5)))
        v=sum(b['total_goodput_mbps']for b in blocks)/16
        arms.append(deepcopy(common)|dict(commit=treatment,candidate_knobs=deepcopy(common)|dict(ap_state={},cpe_state={}),
            total_bidir_goodput_mbps=v,**{active:v,inactive:0},bidir_jain_fairness=.5,observation=dict(goodput_rx_mbps=v),repetition_blocks=blocks))
    return deepcopy(common)|dict(iterations=arms)


@pytest.mark.parametrize('n',[81,82])
def test_bj_alias_is_exact_both_arms_all_blocks_and_one_hypothesis(n):
    p=bj_payload(n);a=bf.unidirectional_alias_audit(n,p)
    assert a['status']=='EXACT_ACTIVE_DIRECTION_TOTAL_GP_ALIAS_VERIFIED'
    assert a['arms_checked']==2 and a['blocks_checked']==32 and a['same_hypothesis_not_duplicate']
    assert a['active_metric']==('dl_goodput_mbps'if n==81 else'ul_goodput_mbps')
    assert all(x['raw_directional_Jain']==.5 for x in a['source_units'])
    assert len(bf.metrics_bj(n))==5 and'jain_fairness'not in bf.metrics_bj(n)


@pytest.mark.parametrize('n',[81,82])
@pytest.mark.parametrize('where',['arm','block'])
@pytest.mark.parametrize('defect',['inactive_nonzero','inactive_missing','active_mismatch','observation_mismatch','boolean'])
def test_bj_alias_cannot_impute_inactive_zero_or_ignore_one_bad_source_unit(n,where,defect):
    p=bj_payload(n);a=p['iterations'][1];obj=a if where=='arm'else a['repetition_blocks'][5]
    active='dl_goodput_mbps'if n==81 else'ul_goodput_mbps';inactive='ul_goodput_mbps'if n==81 else'dl_goodput_mbps'
    if defect=='inactive_nonzero':obj[inactive]=.001
    elif defect=='inactive_missing':obj.pop(inactive)
    elif defect=='active_mismatch':obj[active]+=.001
    elif defect=='observation_mismatch':obj['observation']['goodput_rx_mbps']+=.001
    else:obj[inactive]=False
    with pytest.raises(ValueError):bf.unidirectional_alias_audit(n,p)


@pytest.mark.parametrize('n',[81,82,83,84,85,86])
@pytest.mark.parametrize('defect',['wrong_direction','wrong_flow','wrong_regime','float_timing','missing_timing'])
def test_bj_context_never_relabels_new4flow_or_unidirectional_as_legacy6flow(n,defect):
    d,c,s,a=bf.BJ_TIMING[n];regime,flows,bidir=bf.BJ_REGIMES[n]
    common=dict(distance_m=d,coverage_class=c,slot_time_us=s,ack_timeout_us=a,traffic_regime=regime,active_flow_count=flows,bidirectional=bidir)
    arm=deepcopy(common)|dict(candidate_knobs=deepcopy(common)|dict(ap_state={},cpe_state={}))
    target=arm['candidate_knobs']
    if defect=='wrong_direction':target['bidirectional']=not bidir
    elif defect=='wrong_flow':target['active_flow_count']=6 if flows!=6 else 4
    elif defect=='wrong_regime':target['traffic_regime']='bidir_6flow'if regime!='bidir_6flow'else'bidir_4flow'
    elif defect=='float_timing':target['slot_time_us']=float(s)
    else:target.pop('ack_timeout_us')
    with pytest.raises(ValueError):bf.declared_context_bj(n,common,arm)


@pytest.mark.parametrize('n',[81,82])
def test_bj_real_frozen_direction_recipe_and_alias_are_source_bound(n):
    receipts,_,_,recipes=bf.frozen_inputs_bj()
    result=bf.direction_recipe_audit_bj(n,recipes[n])
    assert result['direct_window_command_flags'][0]['parallel2']
    assert result['direct_window_command_flags'][0]['reverse']==(n==82)
    assert not result['executed_or_effectively_read_back']
    assert bf.unidirectional_alias_audit(n,receipts[n])['blocks_checked']==32


@pytest.mark.parametrize('n',[81,82])
def test_bj_inapplicable_jain_never_enters_paired_inference(n):
    p=bj_payload(n);r=[]
    for a in p['iterations']:
        for row in a['repetition_blocks']:r.append(deepcopy(row)|dict(round_id=f'R{n}',treatment_id=a['commit']))
    with pytest.raises(ValueError):bf.pair_rows_bj(r,'A','B','jain_fairness')


def test_bj_future87_rejected_before_content_and_contract38_not42(monkeypatch):
    native=bf.Path.read_text
    def deny_future(path,*args,**kwargs):
        if 'r87'in path.name.lower():raise AssertionError('future content read')
        return native(path,*args,**kwargs)
    monkeypatch.setattr(bf.Path,'read_text',deny_future)
    with pytest.raises(ValueError):bf.metrics_bj(87)
    plan=json.loads((bf.BJ_BASE/'wave_bj_family_and_bootstrap_recipe.json').read_text(encoding='utf-8'))
    assert len(plan['hypotheses'])==38
    assert plan['complete_known']['total']==1018 and plan['primary']['unknown_p1_padding']==462
    assert sum(h['metric']=='jain_fairness'for h in plan['hypotheses'])==4


def test_bj_extension_preserves_all_legacy_BF_function_and_test_ASTs():
    import ast
    before=bf.BJ_BASE/'wave_bj_before_source_extension'
    old=ast.parse((before/'fmx_statistical_audit.py').read_text(encoding='utf-8'))
    current=ast.parse((bf.ROOT/'orchestration/autoresearch/fmx_statistical_audit.py').read_text(encoding='utf-8'))
    functions=lambda t:{n.name:ast.dump(n,include_attributes=False)for n in t.body if isinstance(n,ast.FunctionDef)}
    a,b=functions(old),functions(current)
    assert all(b[name]==body for name,body in a.items())
    oldtests=functions(ast.parse((before/'test_fmx_statistical_audit.py').read_text(encoding='utf-8')))
    nowtests=functions(ast.parse((bf.ROOT/'tests/test_fmx_statistical_audit.py').read_text(encoding='utf-8')))
    assert all(nowtests[name]==body for name,body in oldtests.items())


@pytest.mark.parametrize('n',[81,82])
def test_bj_source_step1_2_roundtrip_preserves_original_block_id(n):
    p=bj_payload(n);arm=p['iterations'][0];normalized=[]
    for b in arm['repetition_blocks']:
        step=b.pop('crossover_step');b['step_in_block']=step+1
        normalized.append(dict(round_id=f'R{n}',treatment_id=arm['commit'],block_index=b['block_index'],crossover_step=step,
            source_step_in_block=step+1,source_step_field='step_in_block',crossover_step_mapping='EXPLICIT_ONE_BASED_SOURCE_MINUS_ONE'))
    audit=bf.raw_step_roundtrip_bj(n,arm,normalized)
    assert len(audit['units'])==16 and all(u['exact_roundtrip']for u in audit['units'])
    assert [u['block_index']for u in audit['units']]==list(range(16))


@pytest.mark.parametrize('damage',['bool','zero','three','dual','missing','canonical_wrong','source_provenance_missing','provenance_bool','wrong_mapping'])
def test_bj_step_mapping_never_guesses_or_accepts_conflicting_periods(damage):
    p=bj_payload();arm=p['iterations'][0];normalized=[]
    for b in arm['repetition_blocks']:
        step=b.pop('crossover_step');b['step_in_block']=step+1
        normalized.append(dict(round_id='R81',treatment_id=arm['commit'],block_index=b['block_index'],crossover_step=step,
            source_step_in_block=step+1,source_step_field='step_in_block',crossover_step_mapping='EXPLICIT_ONE_BASED_SOURCE_MINUS_ONE'))
    b=arm['repetition_blocks'][0]
    if damage=='bool':b['step_in_block']=True
    elif damage=='zero':b['step_in_block']=0
    elif damage=='three':b['step_in_block']=3
    elif damage=='dual':b['crossover_step']=0
    elif damage=='missing':b.pop('step_in_block')
    elif damage=='canonical_wrong':normalized[0]['crossover_step']=1
    elif damage=='source_provenance_missing':normalized[0].pop('source_step_in_block')
    elif damage=='provenance_bool':normalized[0]['source_step_in_block']=True
    else:normalized[0]['crossover_step_mapping']='GUESSED_FROM_ORDER'
    with pytest.raises(ValueError):bf.raw_step_roundtrip_bj(81,arm,normalized)


def test_bj_reads_only_manifest_copies_never_originals(monkeypatch):
    manifest=json.loads((bf.BJ_BASE/'inputs_manifest.json').read_text(encoding='utf-8'))
    original={(bf.ROOT/e['path']).resolve()for e in manifest['entries']}
    native=bf.Path.read_bytes;native_text=bf.Path.read_text
    def bytes_guard(p):
        if p.resolve()in original:raise AssertionError('Original/live source read')
        return native(p)
    def text_guard(p,*args,**kwargs):
        if p.resolve()in original:raise AssertionError('Original/live source read')
        return native_text(p,*args,**kwargs)
    monkeypatch.setattr(bf.Path,'read_bytes',bytes_guard);monkeypatch.setattr(bf.Path,'read_text',text_guard)
    receipts,_,refs,_=bf.frozen_inputs_bj()
    assert set(receipts)==set(range(81,87))and len(refs)==18
    assert all((bf.ROOT/e['path']).is_relative_to(bf.BJ_BASE/'inputs')for e in refs)


@pytest.mark.parametrize('missing',[False,True])
def test_bj_context_points_are_descriptive_and_never_pool_other_round_units(missing):
    records=[]
    for n in(64,83,84,86,77,80,85):
        for i in(0,1):
            records.append(dict(round_id=f'R{n}',iteration=f'r{n}_iter{i}_fixture',policy_key=json.dumps([{'fixture_coordinate':n+i}]),
                workload_regime='bidir_4flow'if n in(64,83,84,86)else'bidir_6flow',active_flow_count=4 if n in(64,83,84,86)else 6,
                distance_meters=100 if n==64 else 7500,coverage_class=None,goodput_mbps=100-i,dl_goodput_mbps=70,ul_goodput_mbps=30-i,
                p50_ms=1,p95_ms=2,p99_ms=3,jain_fairness=.8))
    if missing:
        records.pop()
        with pytest.raises(ValueError):bf.contextual_descriptions_bj(records)
    else:
        groups=bf.contextual_descriptions_bj(records)
        assert len(groups)==2 and all(g['no_crossround_pairing']and g['no_physical_distance_or_interpolation_proof']for g in groups)
        assert all(not p['crossround_paired_units']for g in groups for p in g['points'])


@pytest.mark.parametrize('values,expected',[
    ([-.59375,-2.296875,-1.59375,4.203125,-2.6875,-2.703125,-1,0,.90625,-.609375,1.796875,2.796875,-3.5,.796875,1.390625,-1.09375],Fraction(9949,16384)),
    ([0,-.390625,-1,-2.78125,-3.703125,-3.90625,-1,-1.78125,-2.59375,.390625,-2.5,.203125,-2.109375,-8.203125,5.90625,.609375],Fraction(1941,16384))])
def test_bj_exact_sign_uses_integer_tail_for_observed_zero_pair_counterexamples(values,expected):
    effect=bf.exact_effect_bj(values)
    assert effect['exact_sign']['p_value']==float(expected)
    assert bf.exact_sign_flips(values)['sign']['p_value']==float(expected)


@pytest.mark.parametrize('values',[[0]*4,[0,1,1,-1,-1,2],[1,1,1,1]])
def test_bj_integer_sign_tail_preserves_zero_tie_and_unanimous_cases(values):
    effect=bf.exact_effect_bj(values);enumerated=bf.exact_sign_flips(values)
    assert effect['exact_sign']['p_value']==enumerated['sign']['p_value']
    assert float(Fraction(effect['exact_sign']['exact_binomial_fraction']))==effect['exact_sign']['p_value']
    assert effect['exact_rank']==bf.exact_effect(values)['exact_rank']


@pytest.mark.parametrize('number', [87, 88, 89, 90, 91, 92])
def test_bn_prescribed_distinct_applicable_metrics(number):
    expected = bf.METRICS[:4] + bf.METRICS[-1:] if number == 87 else bf.METRICS
    assert bf.metrics_bn(number) == expected


# BN uses frozen source only; synthetic mutations are never physical observations.
def bn_payload(number=87):
    receipts, _, _, _ = bf.frozen_inputs_bn()
    return deepcopy(receipts[number])


@pytest.mark.parametrize('number', [86, 93, True, 87.0, '87'])
def test_bn_rejects_unowned_round_before_inspecting_payload(number):
    with pytest.raises(ValueError): bf.metrics_bn(number)
    with pytest.raises(ValueError): bf.declared_context_bn(number, None, None)


@pytest.mark.parametrize('damage', ['active', 'inactive', 'missing', 'bool', 'duplicate_observation'])
def test_bn_pureDL_alias_requires_all_both_arm_and_block_identities(damage):
    payload = bn_payload(); row = payload['iterations'][1]['repetition_blocks'][7]
    if damage == 'active': row['dl_goodput_mbps'] += 1
    elif damage == 'inactive': row['ul_goodput_mbps'] = .1
    elif damage == 'missing': row.pop('ul_goodput_mbps')
    elif damage == 'bool': row['dl_goodput_mbps'] = True
    else: row['observation'] = {'goodput_rx_mbps': row['total_goodput_mbps'] + 1}
    with pytest.raises(ValueError): bf.unidirectional_alias_audit_bn(87, payload)


@pytest.mark.parametrize('where,field,value', [
    ('payload','coverage_class',31.0),('arm','coverage_class',True),
    ('knobs','coverage_class',33),('knobs','slot_time_us',108),
    ('payload','distance_m',15000),('arm','active_flow_count',4.0),
    ('payload','bidirectional',1),('knobs','traffic_regime','unidir_dl_2flow'),
    ('endpoint','distance_meters',None),('arm','ack_timeout_us',None)])
def test_bn_exact_class31_context_rejects_substitution_not_clamped(where,field,value):
    payload = bn_payload(89); arm = payload['iterations'][0]
    obj = {'payload':payload,'arm':arm,'knobs':arm['candidate_knobs'],
           'endpoint':arm['candidate_knobs']['ap_state']}[where]
    obj[field] = value
    with pytest.raises(ValueError): bf.declared_context_bn(89,payload,arm)


@pytest.mark.parametrize('damage', ['class_bool','class_float','class33','physical_claim','readback_claim'])
def test_bn_policy_ceiling_does_not_coerce_or_claim_hardware(damage):
    payload = bn_payload(89); context = bf.declared_context_bn(89,payload,payload['iterations'][0])
    if damage == 'class_bool': context['coverage_class'] = True
    elif damage == 'class_float': context['coverage_class'] = 31.0
    elif damage == 'class33': context['coverage_class'] = 33
    elif damage == 'physical_claim': context['physical_distance_verified'] = True
    else: context['effective_timing_independently_verified'] = True
    with pytest.raises(ValueError): bf.coverage_policy_audit_bn(89,context)


def test_bn_real_recipe_filename_is_not_context_authority():
    receipts, _, refs, recipes = bf.frozen_inputs_bn()
    ref = next(x for x in refs if x['round']==89 and x['path'].endswith('.py'))
    assert 'class33_15km' in ref['path']
    context = bf.declared_context_bn(89,receipts[89],receipts[89]['iterations'][0])
    commands = bf.recipe_coverage_commands(recipes[89])
    assert context['coverage_class']==31 and context['distance_m']==14000
    assert 31 in [x['class_value'] for x in commands if 'class_value' in x] or 'set coverage 31' in recipes[89]
    assert not bf.coverage_policy_audit_bn(89,context)['silicon_or_installed_build_ceiling_verified']


def bn_crossed(payload, number):
    result=[]
    for arm in payload['iterations']:
        for block in arm['repetition_blocks']:
            row=deepcopy(block)
            if number==87:
                row['source_step_in_block']=row.pop('step_in_block')
                row['crossover_step']=row['source_step_in_block']-1
                row['source_step_field']='step_in_block';row['crossover_step_mapping']='EXPLICIT_ONE_BASED_SOURCE_MINUS_ONE'
                row['observation']={k:row[k]for k in ('p50_rtt_ms','p95_rtt_ms','p99_rtt_ms')}
                row['observation'].update(goodput_rx_mbps=row['total_goodput_mbps'],jain_fairness=row['bidir_jain_fairness'])
            row.update(round_id=f'R{number}',treatment_id=arm['commit'],counter_interface='phy0-ap0.sta1')
            result.append(row)
    return result


@pytest.mark.parametrize('damage', ['duplicate','missing_target','same_period','bad_index','mixed_round','unrelated_target'])
def test_bn_pair_units_are_exact_source_not_enumerated_pings(damage):
    payload=bn_payload(88); rows=bn_crossed(payload,88); a,b=[x['commit']for x in payload['iterations']]
    if damage=='duplicate': rows.append(deepcopy(rows[0]))
    elif damage=='missing_target': rows.pop()
    elif damage=='same_period': rows[16]['crossover_step']=rows[0]['crossover_step']
    elif damage=='bad_index': rows[0]['block_index']=False
    elif damage=='mixed_round': rows[0]['round_id']='R89'
    else: rows[16]['treatment_id']='unrelated'
    with pytest.raises(ValueError): bf.pair_rows_bn(rows,a,b,'p95_rtt_ms')


@pytest.mark.parametrize('damage', ['zero','missing','bool','wrong_interface'])
def test_bn_retry_outcome_requires_positive_saved_station_denominator(damage):
    payload=bn_payload(88); rows=bn_crossed(payload,88); a,b=[x['commit']for x in payload['iterations']]
    if damage=='zero': rows[0]['mac_tx_packets_delta']=0
    elif damage=='missing': rows[0].pop('mac_tx_packets_delta')
    elif damage=='bool': rows[0]['mac_tx_retries_delta']=False
    else: rows[0]['counter_interface']='phy0-ap0'
    with pytest.raises(ValueError): bf.pair_rows_bn(rows,a,b,'wds_mac_retry_rate')


def test_bn_unidir_applicability_and_unknown_health_retained():
    payload=bn_payload(); rows=bn_crossed(payload,87); a,b=[x['commit']for x in payload['iterations']]
    assert len(bf.pair_rows_bn(rows,a,b,'goodput_rx_mbps'))==16
    assert 'station_drops' not in rows[0] and 'restoration_verified' not in rows[0]
    for metric in ('ul_goodput_mbps','jain_fairness','dl_goodput_mbps'):
        with pytest.raises(ValueError): bf.pair_rows_bn(rows,a,b,metric)
    alias=bf.unidirectional_alias_audit_bn(87,payload)
    assert alias['active_metric']=='dl_goodput_mbps' and alias['blocks_checked']==32
    assert alias['same_hypothesis_not_duplicate']


@pytest.mark.parametrize('damage',['dual','source_bool','wrong_canonical','missing_provenance'])
def test_bn_one_based_source_mapping_never_guesses(damage):
    payload=bn_payload();arm=payload['iterations'][0];rows=bn_crossed(payload,87)
    if damage=='dual':arm['repetition_blocks'][0]['crossover_step']=0
    elif damage=='source_bool':arm['repetition_blocks'][0]['step_in_block']=True
    elif damage=='wrong_canonical':rows[0]['crossover_step']=1-rows[0]['crossover_step']
    else:rows[0].pop('source_step_field')
    with pytest.raises(ValueError):bf.raw_step_roundtrip_bn(87,arm,rows)


def test_bn_additive_source_preserves_every_legacy_function_AST_and_test_body():
    import ast
    before=bf.BN_BASE/'wave_bn_before_extension'
    def functions(path):
        return {x.name:ast.dump(x,include_attributes=False)for x in ast.parse(path.read_text(encoding='utf-8')).body if isinstance(x,ast.FunctionDef)}
    old=functions(before/'fmx_statistical_audit.py'); now=functions(bf.ROOT/'orchestration/autoresearch/fmx_statistical_audit.py')
    assert len(old)==35 and all(now[k]==v for k,v in old.items())
    old=functions(before/'test_fmx_statistical_audit.py'); now=functions(bf.ROOT/'tests/test_fmx_statistical_audit.py')
    assert all(now[k]==v for k,v in old.items())


@pytest.mark.parametrize('damage', [None, 'wrong_helper', 'duration', 'wrong_module', 'missing_call'])
def test_bn_direction_binds_named_frozen_R81_window_without_executing_it(damage):
    _, _, _, recipes=bf.frozen_inputs_bn();text=recipes[87]
    if damage=='wrong_helper':text=text.replace('run_single_5s_unidir_dl_2flow_dyadic','run_single_5s_unidir_ul_2flow_dyadic')
    elif damage=='duration':text=text.replace('duration_sec=5','duration_sec=6')
    elif damage=='wrong_module':text=text.replace('from tools.bench.run_live_autoresearch_r81_', 'from tools.bench.run_live_autoresearch_r93_')
    elif damage=='missing_call':text=text.replace('blk = run_single_5s_unidir_dl_2flow_dyadic(', 'blk = other_window(')
    if damage is not None:
        with pytest.raises(ValueError):bf.direction_recipe_audit_bn(87,text)
    else:
        result=bf.direction_recipe_audit_bn(87,text)
        assert result['direction_evidence']=='EXACT_NAMED_CALL_TO_PRIOR_FROZEN_R81_WINDOW'
        assert result['frozen_helper_source']['sha256'] and not result['executed_or_effectively_read_back']



def test_bn_builder_global_numeric_bindings_resolve_before_inference():
    import ast, symtable, builtins
    text=(bf.ROOT/'orchestration/autoresearch/fmx_statistical_audit.py').read_text(encoding='utf-8')
    table=next(x for x in symtable.symtable(text,'fmx_statistical_audit.py','exec').get_children()if x.get_name()=='_build_analysis_bn')
    missing=[s.get_name()for s in table.get_symbols()if s.is_global()and s.is_referenced()and s.get_name()not in vars(bf)and s.get_name()not in vars(builtins)]
    assert missing==[]


def test_bqcf_family_is_one_union_not_four_restarts():
    assert len(bf.metrics_bqcf(93))==7
    assert len(bf.metrics_bqcf(103))==5
    assert sum(len(bf.metrics_bqcf(n))for n in bf.BQCF_ROUNDS)==210
    for n in (110,111,112,113,135,True):
        with pytest.raises(ValueError):bf.metrics_bqcf(n)


def bqcf_rows(number=93):
    result=rows()
    for row in result:row['round_id']=f'R{number}'
    return result


@pytest.mark.parametrize('damage',['missing','duplicate','crossround','future','absent','bool_id','float_step','unknown_arm','same_arm','nan','inapplicable'])
def test_bqcf_pair_identity_and_missing_outcomes_fail_closed(damage):
    data=bqcf_rows(103 if damage=='inapplicable' else 93);control,target='A','B';metric='p95_rtt_ms'
    if damage=='missing':data.pop()
    elif damage=='duplicate':data.append(deepcopy(data[0]))
    elif damage=='crossround':data[0]['round_id']='R94'
    elif damage=='future':data[0]['round_id']='R135'
    elif damage=='absent':data[0]['round_id']='R110'
    elif damage=='bool_id':data[0]['block_index']=False
    elif damage=='float_step':data[0]['crossover_step']=0.0
    elif damage=='unknown_arm':data[0]['treatment_id']='unknown'
    elif damage=='same_arm':target=control
    elif damage=='nan':data[0]['observation'][metric]=float('nan')
    else:metric='jain_fairness'
    with pytest.raises(ValueError):bf.pair_rows_bqcf(data,control,target,metric)


def test_bqcf_restricted_period_model_recovers_named_submodel_not_carryover():
    result=bf.period_adjusted_bqcf(bqcf_rows(),'A','B','p95_rtt_ms')
    assert (result['AB_blocks'],result['BA_blocks'],result['rank'],result['columns'])==(8,8,18,18)
    assert result['direct_exact_fraction']=='3' and result['period_exact_fraction']=='2'
    assert result['status']=='IDENTIFIED_RESTRICTED_MODEL_NOT_CAUSAL_CERTIFICATION'


def bqcf_payload(number=103):
    ul=number>107;flows=8 if number>=122 else 2
    shared=dict(distance_m=1000,coverage_class=2,slot_time_us=15,ack_timeout_us=30,
                traffic_regime=f'unidir_{"ul" if ul else "dl"}_{flows}flow'+('_hammer' if flows==8 else ''),active_flow_count=flows,bidirectional=False)
    active='ul_goodput_mbps' if ul else 'dl_goodput_mbps';inactive='dl_goodput_mbps' if ul else 'ul_goodput_mbps'
    arms=[]
    for index,commit in enumerate(('A','B')):
        blocks=[]
        for i in range(16):
            step=index if i%2==0 else 1-index
            blocks.append(dict(block_index=i,step_in_block=step+1,**{active:10.+index,inactive:0.},
                               total_goodput_mbps=10.+index,bidir_jain_fairness=.5))
        arm=dict(shared,commit=commit,total_bidir_goodput_mbps=10.+index,**{active:10.+index,inactive:0.},
                 bidir_jain_fairness=.5,observation=dict(goodput_rx_mbps=10.+index),repetition_blocks=blocks)
        arm['candidate_knobs']=dict(shared,ap_state={},cpe_state={})
        arms.append(arm)
    return dict(shared,iterations=arms)


@pytest.mark.parametrize('number,active,flows',[(103,'dl_goodput_mbps',2),(108,'ul_goodput_mbps',2),(122,'ul_goodput_mbps',8),(134,'ul_goodput_mbps',8)])
def test_bqcf_directional_alias_keeps_literal_direction_and_eight_flow(number,active,flows):
    payload=bqcf_payload(number);alias=bf.unidirectional_alias_bqcf(number,payload)
    assert alias['active_metric']==active and alias['blocks_checked']==32
    assert alias['inapplicable_inference'][0]=='jain_fairness'
    assert bf.declared_context_bqcf(number,payload,payload['iterations'][0])['active_flow_count']==flows


@pytest.mark.parametrize('damage',['inactive','active','duplicate_observation','bool_active','missing_direction','flow_bool','class_float','endpoint_distance','knobs_slot'])
def test_bqcf_alias_cannot_hide_inactive_traffic_or_context_conflict(damage):
    payload=bqcf_payload();arm=payload['iterations'][0];block=arm['repetition_blocks'][0]
    if damage=='inactive':block['ul_goodput_mbps']=.001
    elif damage=='active':block['dl_goodput_mbps']+=1
    elif damage=='duplicate_observation':arm['observation']['goodput_rx_mbps']=99
    elif damage=='bool_active':block['dl_goodput_mbps']=True
    elif damage=='missing_direction':payload.pop('bidirectional')
    elif damage=='flow_bool':payload['active_flow_count']=True
    elif damage=='class_float':arm['coverage_class']=2.0
    elif damage=='endpoint_distance':arm['candidate_knobs']['cpe_state']['distance_meters']=3000
    else:arm['candidate_knobs']['slot_time_us']+=1
    with pytest.raises(ValueError):bf.unidirectional_alias_bqcf(103,payload)


@pytest.mark.parametrize('damage',[None,'two_schemas','bool_step','wrong_step','lost_provenance'])
def test_bqcf_source_step_roundtrip_is_explicit_not_enumerated(damage):
    payload=bqcf_payload();arm=payload['iterations'][0];canonical=[]
    for raw in arm['repetition_blocks']:
        canonical.append(dict(round_id='R103',treatment_id='A',block_index=raw['block_index'],crossover_step=raw['step_in_block']-1,
                              source_step_in_block=raw['step_in_block'],source_step_field='step_in_block',crossover_step_mapping='EXPLICIT_ONE_BASED_SOURCE_MINUS_ONE'))
    if damage=='two_schemas':arm['repetition_blocks'][0]['crossover_step']=0
    elif damage=='bool_step':arm['repetition_blocks'][0]['step_in_block']=True
    elif damage=='wrong_step':canonical[0]['crossover_step']=1
    elif damage=='lost_provenance':canonical[0].pop('source_step_in_block')
    if damage:
        with pytest.raises(ValueError):bf.raw_step_roundtrip_bqcf(103,arm,canonical)
    else:assert bf.raw_step_roundtrip_bqcf(103,arm,canonical)['units'][0]['source_step_literal']==1


def test_bqcf_one_union_holm_not_independent_group_restart_and_prior_not_recomputed():
    prior={f'old:{i}':.5 for i in range(1058)}
    def member(scope,p):return dict(scope=scope,metric='p95_rtt_ms',source_hypothesis_id=scope,exact_rank=dict(p_value=p),exact_sign_flips=dict(mean=dict(p_value=p)))
    a=member('R93',.00001);b=member('R108',.00005)
    joint=bf.joint_families_bqcf([a,b],prior)
    family=joint[bf.BQCF_RANK_FAMILY]
    assert family['unknown_padding_count']==498
    assert family['adjusted_p']['R108']==pytest.approx(.00005*499)
    assert family['adjusted_p']['R108']!=pytest.approx(bf.joint_families_bqcf([b],prior)[bf.BQCF_RANK_FAMILY]['adjusted_p']['R108'])
    assert joint['complete_known_rank1060_bound1060']['known_hypotheses']['old:0']==.5
    assert set(joint[bf.BQCF_MEAN_FAMILY]['known_hypotheses'])=={'MEANFLIP:R93','MEANFLIP:R108'}


@pytest.mark.parametrize('damage',['future','missing','traversal'])
def test_bqcf_manifest_identity_preflight_rejects_before_copy_content(tmp_path,monkeypatch,damage):
    monkeypatch.setattr(bf,'BQCF_BASE',tmp_path)
    entries=[]
    for n in bf.BQCF_ROUNDS:
        for suffix in ('.json','.tsv','.py'):
            logical=f'source_r{n}_fixture{suffix}'
            entries.append(dict(round=n,path=logical,copy=str(tmp_path/'inputs'/logical),sha256='0'*64,bytes=0))
    if damage=='future':entries[-1]['round']=135
    elif damage=='missing':entries[-1]['round']=110
    else:entries[-1]['path']='../escape.py'
    (tmp_path/'inputs_manifest.json').write_text(json.dumps(dict(entries=entries)))
    def bind_only_metadata(path):
        if path.name=='inputs_manifest.json':return dict(sha256=bf.BQCF_MANIFEST_SHA)
        if path.name=='stats_family_and_bootstrap_recipe.json':return dict(sha256=bf.BQCF_FAMILY_SHA)
        raise AssertionError('Source copy was touched before invalid identity rejection')
    monkeypatch.setattr(bf,'binding',bind_only_metadata)
    with pytest.raises(ValueError):bf.frozen_inputs_bqcf()


def test_bqcf_recipe_ul8_call_and_literal_warmup_cannot_be_ul2():
    context=bf.declared_context_bqcf(122,bqcf_payload(122),bqcf_payload(122)['iterations'][0])
    text="run_single_5s_unidir_ul_8flow_resilient(b,duration_sec=5)\nwarmup='iperf3 -c example -P 8 -R -t 1 >/dev/null'\n"
    result=bf.source_recipe_audit_bqcf(122,text,context)
    assert result['warmup_direction_checks'][0]['parallel_streams']==8 and not result['recipe_imported_or_executed']
    with pytest.raises(ValueError):bf.source_recipe_audit_bqcf(122,text.replace('-P 8','-P 2'),context)


def test_bqcf_unknown_block_health_is_retained_not_a_healthy_fixture():
    data=bqcf_rows()
    assert len(bf.pair_rows_bqcf(data,'A','B','p95_rtt_ms'))==16
    quality=bf._quality(data)
    assert quality['loss_unknown_rows']==32
    assert quality['restoration_verified_unknown_rows']==32
    assert quality['station_drops_unknown_rows']==32
    assert 'restoration_false_rows' not in quality


def test_bqcf_canonical_future_path_rejected_before_any_content_or_dependency_read(monkeypatch):
    def forbidden(*args,**kwargs):raise AssertionError('No source or freeze read permitted')
    monkeypatch.setattr(bf.Path,'read_text',forbidden)
    with pytest.raises(ValueError):
        bf.statistics_inputs_bqcf(bf.BQCF_BASE/'normalized_r1_to_r135_measurements_20261024.json',
            bf.BQCF_BASE/'normalized_r16_to_r134_block_observations_20261024.json',bf.BQCF_BASE/'inputs_manifest.json')


def test_bqcf_two_names_cannot_duplicate_a_planned_hypothesis():
    a=dict(scope='R93',metric='p95_rtt_ms',source_hypothesis_id='a',exact_rank=dict(p_value=.1),exact_sign_flips=dict(mean=dict(p_value=.2)))
    b=dict(a,source_hypothesis_id='b')
    with pytest.raises(ValueError):bf.joint_families_bqcf([a,b],{f'old:{i}':.5 for i in range(1058)})


@pytest.mark.parametrize('damage',[None,'bytes_drift','path_traversal'])
def test_bqcf_final_input_guard_rehashes_relative_binding_as_absolute(tmp_path,monkeypatch,damage):
    monkeypatch.setattr(bf,'ROOT',tmp_path)
    p=tmp_path/'records.json';p.write_text('{}')
    expected=dict(path='records.json',sha256='valid',bytes=2)
    def absolute_binding(path):
        assert path==p and path.is_absolute(), 'Historical binding helper requires absolute path'
        return dict(expected,bytes=path.stat().st_size)
    monkeypatch.setattr(bf,'binding',absolute_binding)
    pins={'records':dict(expected)}
    if damage=='bytes_drift':p.write_text('{"changed":true}')
    elif damage=='path_traversal':pins['records']['path']='../records.json'
    if damage:
        with pytest.raises(ValueError):bf.revalidate_input_pins_bqcf(pins)
    else:bf.revalidate_input_pins_bqcf(pins)
