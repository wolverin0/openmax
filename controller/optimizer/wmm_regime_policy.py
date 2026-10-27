"""Offline selector of exact observed packages passing structural certification.

The filename retains the requested WMM label, not a claim that AQL is EDCA.
No actuator, synthesized knob package, retry-profile enrollment or significance
transfer is present. PROMOTED_CERTIFIED_CANARY describes offline eligibility.
"""
from copy import deepcopy

from orchestration.autoresearch.fmx_structural_promotion_gate import (
    REGIMES, _policy, _in_regime, _round_scope, evaluate_promotion,
)


def _target_kind(row, regime):
    """Classify declared fields only. Names/KEEP flags never define a package."""
    ap, cpe = _policy(row)
    if regime in ('bidir_8flow','covclass6_3km','covclass13_6km'):
        return (ap != cpe and row.get('airtime_flags') in (1,3)
                and row.get('fq_limit') in (2048,8192) and row.get('force_tx_status') in (0,1)
                and row.get('short_retry_limit')==7 and row.get('long_retry_limit')==4)
    if regime in ('bidir_6flow','bidir_2flow'):
        return (ap != cpe and row.get('airtime_flags')==1 and row.get('fq_limit')==2048
                and row.get('force_tx_status')==1 and row.get('short_retry_limit')==7
                and row.get('long_retry_limit')==4)
    # The recorded hybrid fields are AQL low/high and FQ bytes, not the spec's
    # unsupported TXOP1800/quantum3600 reinterpretation of these numbers.
    return (ap == cpe and ap['aql_by_ac'][2]==[1800,3600]
            and ap['fq_quantum_bytes']==256)


def select_regime_policy(evidence, *, regime, policy_id=None, requested_alias=None,
                         requested_wmm=None, round_ids=None):
    """Evaluate complete observed packages; optional retry5/3 needs explicit ID.

    No transfer rule is implemented. Direct n4 evidence cannot inherit broad
    multiplicity certification from a different workload regime. If several
    exact packages independently qualify, choose observed mean p95, then ID.
    That ranking is an explicit advisory heuristic, not an effect prediction.
    """
    result = dict(status='ABSTAIN', regime=regime, policy_id=None,
                  ap_policy=None,cpe_policy=None, candidates=[],
                  automatic_execution_allowed=False,physical_safety_qualified=False,
                  ranking='OBSERVED_MEAN_P95_THEN_EXACT_POLICY_ID',
                  requested_alias=requested_alias,
                  alias_diagnostic='REQUESTED_LABEL_NOT_EVIDENCE_OF_WMM_EDCA_CONTROLS' if requested_alias is not None else None,
                  limits=['OFFLINE_ONLY: structural canary eligibility is not execution authority or production acceptance',
                          'No cross-regime statistical transfer; optional retry5/3 is never enrolled by name',
                          'AQL thresholds are not WMM TXOP/CW/AIFS; observed field units stay unchanged'])
    if regime not in REGIMES: return {**result,'reason':'UNSUPPORTED_REGIME'}
    try:
        scope=_round_scope(round_ids)
        result['requested_round_ids']=sorted(scope) if scope is not None else None
        data=evidence.parse();rows=data['records']['records']
        relevant=[r for r in rows if _in_regime(r,regime) and
                  (scope is None or r.get('round_id') in scope) and
                  (policy_id is not None or 'certified_wds_evidence' in r) and
                  (r.get('policy_key')==policy_id if policy_id is not None else _target_kind(r,regime))]
        ids=sorted({r['policy_key'] for r in relevant})
        accepted=[]
        for key in ids:
            gate=evaluate_promotion(evidence,policy_id=key,regime=regime,requested_wmm=requested_wmm,round_ids=round_ids)
            result['candidates'].append(gate)
            if gate['status']=='PROMOTED_CERTIFIED_CANARY':
                own=[r for r in relevant if r['policy_key']==key]
                accepted.append((sum(r['p95_ms'] for r in own)/len(own),key,own[0]))
        if not accepted:
            return {**result,'status':'BLOCKED' if ids else 'ABSTAIN',
                    'reason':'NO_FULLY_CERTIFIED_PACKAGE' if ids else 'NO_EXACT_OBSERVED_TARGET_PACKAGE'}
        _,key,row=min(accepted,key=lambda item:(item[0],item[1]))
        ap,cpe=_policy(row)
        return {**result,'status':'PROMOTED_CERTIFIED_CANARY','policy_id':key,
                'ap_policy':deepcopy(ap),'cpe_policy':deepcopy(cpe),
                'source_receipt_sha256':evidence.receipt_sha256}
    except (KeyError,ValueError,TypeError,AttributeError,OverflowError) as error:
        return {**result,'status':'BLOCKED','reason':'MALFORMED_OR_UNBOUND_EVIDENCE',
                'error_type':type(error).__name__}
