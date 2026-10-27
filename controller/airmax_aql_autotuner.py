"""Offline advice over observed bidirectional and active-direction AQL packages.

Despite the historical target filename, no actuator, SSH client, optimizer,
background runner or nearest-distance policy fabrication is implemented here.
"""
import json
from orchestration.autoresearch.fmx_pareto_decomposer import decompose_context


def advise_airmax_aql(evidence,*,regime,distance_meters,round_ids=None,execute=False,coverage_class=None):
    """Return source-qualified AP+CPE advice within class 0..31; never actuate."""
    if execute is not False:
        return dict(status='BLOCKED',reason='OFFLINE_EXECUTION_DISABLED',selected=None,
            candidate_policy=None,advisory_only=True,automatic_execution_allowed=False,
            physical_acceptance=False,distance_interpretation='DECLARED_TIMING_CONTEXT_ONLY')
    result=decompose_context(evidence,regime=regime,distance_meters=distance_meters,round_ids=round_ids,coverage_class=coverage_class)
    selected=result.get('selected')
    package=json.loads(selected['policy_id']) if selected else None
    return {**result,'candidate_policy':package,'advisory_only':True,
            'automatic_execution_allowed':False,'physical_acceptance':False}
