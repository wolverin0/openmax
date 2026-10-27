"""Observed-only timing-distance surfaces over the unchanged strict gate.

No interpolation, acquisition, physical-range claim or policy generation.
An absent or blocked knot stays absent or blocked, including the proposed
seven-point pureDL curve. Distinct saved coverage classes remain distinct.
"""
from orchestration.autoresearch.fmx_pareto_decomposer import decompose_context

PRIMARY_KNOTS = ((100,0),(1000,2),(3000,6),(6000,13),(9000,20),(12000,27),(14000,31))


def build_distance_surface(evidence, *, regime, knots=PRIMARY_KNOTS, round_ids=None):
    """Evaluate each explicit saved distance/class pair without filling gaps."""
    out=dict(status='BLOCKED',regime=regime,points=[],complete_curve_qualified=False,
             automatic_execution_allowed=False,physical_acceptance=False,
             distance_interpretation='DECLARED_TIMING_CONTEXT_ONLY',interpolated=False)
    if (not isinstance(knots,(list,tuple)) or not knots or
            any(not isinstance(k,(list,tuple)) or len(k)!=2 or any(type(v) is not int for v in k) for k in knots)):
        return {**out,'reason':'EXPLICIT_UNIQUE_DISTANCE_COVERAGE_PAIRS_REQUIRED'}
    pairs=[tuple(k) for k in knots]
    if len(set(pairs)) != len(pairs):
        return {**out,'reason':'EXPLICIT_UNIQUE_DISTANCE_COVERAGE_PAIRS_REQUIRED'}
    points=[decompose_context(evidence,regime=regime,distance_meters=d,coverage_class=c,round_ids=round_ids)
            for d,c in pairs]
    qualified=all(p['status']=='ELIGIBLE_OFFLINE_STRICT_CONTEXT' and p['selected'] is not None for p in points)
    return {**out,'status':'OFFLINE_OBSERVED_DISTANCE_SURFACE','points':points,
            'complete_curve_qualified':qualified,'all_seven_primary_points_qualified':qualified and tuple(pairs)==PRIMARY_KNOTS,
            'qualified_knots':sum(p['selected'] is not None for p in points),
            'missing_or_blocked_knots':[dict(distance_meters=d,coverage_class=c,status=p['status'],reason=p.get('reason'))
                                        for (d,c),p in zip(pairs,points) if p['selected'] is None]}
