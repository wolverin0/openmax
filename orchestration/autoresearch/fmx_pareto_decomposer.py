"""Observed-only six-regime/twelve-context Pareto decomposition with strict <2%.

The inclusive historical operator projection remains visible. Every candidate
must independently pass the unchanged structural gate before it can be chosen.
This module neither acquires evidence nor creates policies or device commands.
"""
from copy import deepcopy
from fractions import Fraction

from orchestration.autoresearch.fmx_multi_regime_dyadic_selector import (
    DISTANCE_CLASSES as _DISTANCE_CLASSES,
    COVERAGE_POLICY, COVERAGE_POLICY_MAX,
    EXTENDED_DISTANCE_CLASSES, _requested_coverage,
    _scope_identity,
    _operator_cost_vector,
    select_operator_policy,
)
from orchestration.autoresearch.fmx_structural_promotion_gate import audit_operator_promotion

DISTANCE_CLASSES = dict(_DISTANCE_CLASSES)
WORKLOAD_REGIMES = ('bidir_2flow','bidir_4flow','bidir_6flow','bidir_8flow',
                    'unidir_dl_2flow','unidir_ul_2flow')
EXTENDED_WORKLOAD_REGIMES = (*WORKLOAD_REGIMES, 'unidir_ul_8flow_hammer')
EXTENDED_DECLARED_CONTEXTS = tuple(sorted((*EXTENDED_DISTANCE_CLASSES.items(), (12000, 26))))


def _empty(regime,distance):
    return dict(status='BLOCKED',regime=regime if type(regime) is str else None,
        distance_meters=distance if type(distance) is int else None,selected=None,
        observed_points=[],structural_profiles=[],strict_frontier=[],eligible_contexts=[],
        automatic_execution_allowed=False,physical_acceptance=False,
        distance_interpretation='DECLARED_TIMING_CONTEXT_ONLY',
        evidence_freshness='IMMUTABLE_LOADED_SNAPSHOT_RELOAD_TO_CHECK_CURRENT_FILES',
        frontier_interpretation='DESCRIPTIVE_OBSERVED_PACKAGES_WITHIN_CONTEXT_NOT_CAUSAL',
        total_goodput_noninferiority_claim=False,coverage_policy=dict(COVERAGE_POLICY))


def _strict_negative(result):
    """Retain already blocked operator evidence and disclose the literal budget."""
    loss=result.get('utility',{}).get('observed_total_goodput_loss_fraction')
    strict=loss is not None and Fraction(loss)<2
    reasons=list(result.get('reasons',[]))
    if not strict:reasons.append('STRICT_LITERAL_GOODPUT_DROP_NOT_BELOW_2PCT')
    return {**result,'status':'BLOCKED','reasons':sorted(set(reasons)),
            'strict_literal_goodput_drop_below_2pct':strict}


def decompose_context(evidence,*,regime,distance_meters,round_ids=None,coverage_class=None):
    """Select an observed, source-bound package with regime-applicable outcomes.

    Explicit context encoding is not measured physical range. Missing flow by
    distance cells abstain. Neither Pareto membership nor a faster inclusive
    candidate can replace the structural <2% and all-five-unanimity conjunction.
    """
    out=_empty(regime,distance_meters)
    if (type(regime) is not str or regime not in EXTENDED_WORKLOAD_REGIMES
            or type(distance_meters) is not int or distance_meters not in EXTENDED_DISTANCE_CLASSES):
        return {**out,'reason':'UNSUPPORTED_DECLARED_CONTEXT'}
    try:
        requested_class = _requested_coverage(distance_meters, coverage_class)
    except (ValueError, TypeError):
        return {**out,'reason':'UNSUPPORTED_DECLARED_CONTEXT'}
    if coverage_class is not None:
        out['requested_coverage_class'] = requested_class
    if requested_class > COVERAGE_POLICY_MAX:
        return {**out,'reason':'COVERAGE_CLASS_EXCEEDS_SUPPORTED_POLICY_MAX31'}
    if regime in ('unidir_dl_2flow','unidir_ul_2flow','unidir_ul_8flow_hammer'):
        out['pareto_metric_scope']=['goodput_rx_mbps','p95_rtt_ms','p99_rtt_ms','wds_mac_retry_rate']
    try:
        parent=select_operator_policy(evidence,regime=regime,distance_meters=distance_meters,
            mode='strict_goodput_preservation',round_ids=round_ids,coverage_class=coverage_class)
        out['operator_projection']=parent
        out['observed_points']=deepcopy(parent.get('observed_points',[]))
        if parent.get('reason') not in (None,'AMBIGUOUS_ELIGIBLE_CONTEXTS'):
            return {**out,'reason':parent['reason']}
        for comparison in parent.get('evaluations',[]):
            if comparison['status'].startswith('ELIGIBLE_OFFLINE_'):
                result=audit_operator_promotion(evidence,regime=regime,
                    round_id=comparison['round_id'],policy_id=comparison['policy_id'],
                    control_policy_id=comparison['control_policy_id'],distance_meters=distance_meters,coverage_class=coverage_class)
            else:
                result=_strict_negative(comparison)
            out['structural_profiles'].append(result)
        eligible=[r for r in out['structural_profiles'] if r['status']=='ELIGIBLE_OFFLINE_STRICT_OPERATOR_PROMOTION']
        if not eligible:
            if not out['observed_points']:
                return {**out,'status':'ABSTAIN','reason':'NO_OBSERVED_CONTEXT'}
            return {**out,'reason':'NO_STRICT_ELIGIBLE_POLICY'}
        # Re-parse externally pinned immutable bytes; this is not a live-file check.
        rows=evidence.parse()[evidence.current_view]['records']['records']
        candidates=[]
        for result in eligible:
            own=[r for r in rows if r['round_id']==result['round_id'] and r['policy_key']==result['policy_id']]
            if len(own)!=1:raise ValueError('Unique source target required')
            row=own[0];context=_scope_identity(row,regime,operator=True)
            vector=_operator_cost_vector(row,regime)
            candidates.append((context,vector,row,result))
        frontier=[]
        for context,vector,row,result in candidates:
            if any(c==context and all(x>=y for x,y in zip(v,vector)) and any(x>y for x,y in zip(v,vector))
                   for c,v,_,_ in candidates):continue
            frontier.append((context,vector,row,result))
        out['strict_frontier']=[dict(round_id=r['round_id'],policy_id=r['policy_key'],
            control_policy_id=g['control_policy_id'],goodput_mbps=r['goodput_mbps'],p95_ms=r['p95_ms'])
            for _,_,r,g in frontier]
        contexts={c for c,_,_,_ in candidates}
        out['eligible_contexts']=[dict(distance_meters=c[0],encryption_mode=c[1],associated_cpes=list(c[2]),coverage_class=c[3])
                                  for c in sorted(contexts,key=repr)]
        if len(contexts)!=1:
            return {**out,'reason':'AMBIGUOUS_ELIGIBLE_CONTEXTS'}
        chosen=min(frontier,key=lambda t:(t[2]['p95_ms'],-t[2]['goodput_mbps'],t[2]['policy_key'],t[2]['round_id'],t[3]['control_policy_id']))
        return {**out,'status':'ELIGIBLE_OFFLINE_STRICT_CONTEXT','selected':chosen[3]}
    except (ValueError,TypeError,KeyError,AttributeError,IndexError,OverflowError,ZeroDivisionError) as error:
        return {**out,'status':'BLOCKED','selected':None,'reason':'MALFORMED_OR_UNBOUND_EVIDENCE','error_type':type(error).__name__}


def decompose_distance_grid(evidence,*,round_ids=None):
    """Enumerate 72 declared cells: 66 in policy and 6 historical class33 blocks."""
    cells=[decompose_context(evidence,regime=r,distance_meters=d,round_ids=round_ids)
           for r in WORKLOAD_REGIMES for d in DISTANCE_CLASSES]
    return dict(status='OFFLINE_OBSERVED_CONTEXT_GRID',cells=cells,
        declared_distance_classes=dict(DISTANCE_CLASSES),workload_regimes=list(WORKLOAD_REGIMES),
        context_count=len(cells),
        supported_policy_context_count=sum(DISTANCE_CLASSES[c['distance_meters']] <= COVERAGE_POLICY_MAX for c in cells),
        historical_unsupported_context_count=sum(DISTANCE_CLASSES[c['distance_meters']] > COVERAGE_POLICY_MAX for c in cells),
        all72_cells_qualified=all(c['selected'] is not None for c in cells),
        all66_cells_qualified=all(c['selected'] is not None for c in cells if c['distance_meters'] != 14000),
        all44_cells_qualified=all(c['selected'] is not None for c in cells if c['regime'] in WORKLOAD_REGIMES[:4] and c['distance_meters'] != 14000),
        coverage_policy=dict(COVERAGE_POLICY),
        automatic_execution_allowed=False,physical_acceptance=False,
        distance_interpretation='DECLARED_TIMING_CONTEXT_ONLY')


def decompose_extended_distance_grid(evidence,*,round_ids=None):
    """Enumerate98 literal declarations, including both12km timing classes.

    This additive interface preserves the historical72-cell API. UL8 hammer is
    separate from UL2. Unsupported class33 remains visible and always blocked.
    """
    cells=[decompose_context(evidence,regime=r,distance_meters=d,coverage_class=c,round_ids=round_ids)
           for r in EXTENDED_WORKLOAD_REGIMES for d,c in EXTENDED_DECLARED_CONTEXTS]
    supported=[cell for cell in cells if cell['requested_coverage_class'] <= COVERAGE_POLICY_MAX]
    return dict(status='OFFLINE_EXTENDED_OBSERVED_CONTEXT_GRID',cells=cells,
        declared_contexts=[dict(distance_meters=d,coverage_class=c) for d,c in EXTENDED_DECLARED_CONTEXTS],
        workload_regimes=list(EXTENDED_WORKLOAD_REGIMES),context_count=len(cells),
        supported_policy_context_count=len(supported),historical_unsupported_context_count=len(cells)-len(supported),
        all_declared_cells_qualified=all(c['selected'] is not None for c in cells),
        all_supported_cells_qualified=all(c['selected'] is not None for c in supported),
        coverage_policy=dict(COVERAGE_POLICY),automatic_execution_allowed=False,physical_acceptance=False,
        distance_interpretation='DECLARED_TIMING_CONTEXT_ONLY')
