"""Pinned, nonactuating six-regime selector for saved R27..R47 comparisons.

STRICT adds target observed total-GP >= 98% of control to the common gates.
DIRECTIONAL keeps the same source/health/HL/Holm500 conjunction without that
floor. It does NOT establish total-GP noninferiority. Both are within-link,
conditional offline eligibility, never an actuator or physical certification.

Each current/prior view needs an externally accepted statistics-receipt hash.
The caller owns that trust decision. All manifests are explicitly verified;
documentary original-source pointers are never opened. No recipe is imported.
"""
from dataclasses import dataclass
from fractions import Fraction
import math
from pathlib import Path
import re
import struct

import numpy as np

from orchestration.autoresearch.fmx_structural_promotion_gate import (
    BoundEvidence, REGIMES, COVERAGE_CONTEXTS, _context, _holm, _in_regime,
    _integer, _matched_hl, _number, _policy, _rows_for_block, _workload,
    load_bound_evidence,
    OPERATOR_UNIDIRECTIONAL_REGIMES,
)


SUPPORTED_REGIMES = tuple(k for k in REGIMES if k != 'bidir_2flow')
MODES = ('STRICT', 'DIRECTIONAL')
LATENCY_METRICS = ('p50_rtt_ms', 'p95_rtt_ms', 'p99_rtt_ms')
MEAN_FIELDS = ('goodput_mbps', 'dl_goodput_mbps', 'ul_goodput_mbps', 'jain_fairness')
OPERATOR_MODES = ('strict_goodput_preservation', 'directional_latency_ul_dominance',
                  'strict_goodput_AND_lower_retry')
RETRY_PRESERVING_MODE = OPERATOR_MODES[2]
OPERATOR_REGIMES = (*SUPPORTED_REGIMES, 'bidir_2flow', 'bidir_4flow', 'unidir_ul_8flow_hammer')
COVERAGE_POLICY_MAX = 31
COVERAGE_POLICY = dict(minimum_class=0, maximum_class=COVERAGE_POLICY_MAX,
    basis='CONSERVATIVE_OFFLINE_ADVICE_POLICY_HELD_CATALOG_NOT_INSTALLED_DRIVER_PROOF',
    hardware_ceiling_verified=False, effective_timing_independently_verified=False)
DISTANCE_CLASSES = {100: 0, 1500: 3, 3000: 6, 4500: 10, 6000: 13, 7500: 16, 9000: 20, 10500: 23, 12000: 27, 13500: 30, 14000: 31, 15000: 33}
# Preserve the twelve-label historical grid. New declarations are an additive
# interface: class26 and class27 at12km must never be silently substituted.
EXTENDED_DISTANCE_CLASSES = {**DISTANCE_CLASSES, 1000: 2}
OPERATOR_COVERAGE_DISTANCES = {c:d for d,c in EXTENDED_DISTANCE_CLASSES.items()}
OPERATOR_COVERAGE_DISTANCES[26] = 12000
OPERATOR_TIMINGS = {0:(9,18),2:(15,30),3:(18,36),6:(27,54),10:(39,78),13:(48,96),
    16:(57,114),20:(69,138),23:(78,156),26:(87,174),27:(90,180),30:(99,198),31:(102,204),33:(108,216)}


@dataclass(frozen=True)
class EvidenceViewPaths:
    name: str
    records_path: Path
    blocks_path: Path
    stats_path: Path
    manifest_path: Path
    receipt_path: Path
    expected_receipt_sha256: str


@dataclass(frozen=True)
class MultiRegimeEvidence:
    current_view: str
    views: tuple

    def parse(self):
        parsed = {name: evidence.parse() for name, evidence in self.views}
        if len(parsed) != len(self.views) or self.current_view not in parsed:
            raise ValueError('Unique explicitly named current/prior views required')
        return parsed


def _identity(row):
    return row['round_id'], row['iteration']


def _round(value):
    if not isinstance(value, str) or not re.fullmatch(r'R(?:[1-9]|[1-3][0-9]|4[0-7])', value):
        raise ValueError('Only recorded R1..R47 identities are in scope')
    return value


def load_multi_regime_evidence(*, current, prior_views=()):
    """Verify explicit immutable views; no recursive metadata-path loading."""
    return _load_views(current=current, prior_views=prior_views, operator=False)


def load_operator_evidence(*, current, prior_views=()):
    """Recorded R1..R134 scope; absent rounds never acquire evidence by identity."""
    return _load_views(current=current, prior_views=prior_views, operator=True)


def _operator_round(value):
    if not isinstance(value, str) or not re.fullmatch(r'R(?:[1-9]|[1-9][0-9]|1[0-2][0-9]|13[0-4])', value):
        raise ValueError('Only requested R1..R134 identities are in scope')
    return value


def _requested_coverage(distance_meters, coverage_class=None):
    if distance_meters is None:
        if coverage_class is not None:
            raise ValueError('Explicit coverage query requires its declared distance')
        return None
    _integer(distance_meters, 'requested distance class', 1)
    if distance_meters not in EXTENDED_DISTANCE_CLASSES:
        raise ValueError('Unsupported requested distance class')
    result = EXTENDED_DISTANCE_CLASSES[distance_meters] if coverage_class is None else coverage_class
    _integer(result, 'requested coverage class', 0, 33)
    if OPERATOR_COVERAGE_DISTANCES.get(result) != distance_meters:
        raise ValueError('Requested coverage class and timing distance conflict')
    return result


def _load_views(*, current, prior_views, operator):
    configs = (current, *prior_views)
    loaded = []
    for config in configs:
        if not isinstance(config, EvidenceViewPaths) or not isinstance(config.name, str) or not config.name.strip():
            raise ValueError('Explicit evidence view contract required')
        loaded.append((config.name, load_bound_evidence(**{
            k: getattr(config, k) for k in EvidenceViewPaths.__dataclass_fields__ if k != 'name'})))
    evidence = MultiRegimeEvidence(current.name, tuple(loaded))
    data = evidence.parse()
    current_data = data[current.name]
    rows = current_data['records']['records']
    current_rows = {_identity(r): r for r in rows}
    if len(current_rows) != len(rows):
        raise ValueError('Duplicate current window identity')
    for row in rows:
        (_operator_round if operator else _round)(row['round_id'])
    def blocks_by_id(items):
        result = {(b['round_id'], b['block_index'], b['crossover_step']): b for b in items}
        if len(result) != len(items):
            raise ValueError('Duplicate crossed source identity')
        return result
    current_blocks = blocks_by_id(current_data['blocks']['crossed'])
    for name, saved in data.items():
        for row in saved['records']['records']:
            if current_rows.get(_identity(row)) != row:
                raise ValueError('Current view changed an accepted prior record')
        for key, block in blocks_by_id(saved['blocks']['crossed']).items():
            if current_blocks.get(key) != block:
                raise ValueError('Current view changed an accepted prior block')
        if operator:
            current_sequential = current_data['blocks'].get('sequential', [])
            if any(block not in current_sequential for block in saved['blocks'].get('sequential', [])):
                raise ValueError('Current view changed an accepted prior sequential block')
        projection = saved['stats'].get('promotion_evidence')
        pins = dict(dict(evidence.views)[name].digests)
        if (not isinstance(projection, dict) or projection.get('source_inputs') !=
                {k + '_sha256': pins[k] for k in ('records', 'blocks', 'manifest')}):
            raise ValueError('Statistics projection source scope mismatch')
    return evidence


def _required_metrics(regime, *, mode=None):
    if mode == RETRY_PRESERVING_MODE:
        return LATENCY_METRICS[:2] + ('ul_goodput_mbps', 'jain_fairness')
    if regime == 'unidir_dl_2flow':
        return LATENCY_METRICS + ('dl_goodput_mbps',)
    if regime in ('unidir_ul_2flow','unidir_ul_8flow_hammer'):
        return LATENCY_METRICS + ('ul_goodput_mbps',)
    return LATENCY_METRICS + ('ul_goodput_mbps', 'jain_fairness')


def _ulp_distance(a, b):
    # All permitted metric values are finite and nonnegative; +/-0 coincide.
    if a == b:
        return 0
    return abs(struct.unpack('>Q', struct.pack('>d', a))[0] -
               struct.unpack('>Q', struct.pack('>d', b))[0])


def dyadic_mean_audit(row, blocks):
    """Literal decimal Fraction and float64 np.mean equality, never epsilon."""
    own = _rows_for_block(blocks, row)
    if not own:
        raise ValueError('Source blocks required')
    report = {}
    for name in MEAN_FIELDS:
        values = [_number(b[name] if name in ('dl_goodput_mbps', 'ul_goodput_mbps')
                          else b['observation']['goodput_rx_mbps' if name == 'goodput_mbps' else name],
                          'source block mean field') for b in own]
        reported = _number(row.get(name), name)
        delta = Fraction(str(reported)) - sum((Fraction(str(v)) for v in values), Fraction()) / len(values)
        with np.errstate(over='ignore', invalid='ignore'):
            mean = float(np.mean(np.asarray(values, dtype=np.float64)))
        _number(mean, 'finite float64 mean')
        ulp = _ulp_distance(float(reported), mean)
        report[name] = dict(fraction_delta=str(delta), numpy_mean=mean,
                            float_delta=float(reported) - mean, ulp_error=ulp,
                            exact=delta == 0 and ulp == 0)
    return report


def _scope_identity(row, regime, *, operator=False):
    _policy(row)
    if not _in_regime(row, regime):
        raise ValueError('Recorded workload/coverage differs from requested regime')
    expected_workload = ((4, True) if regime == 'bidir_4flow' else (8, False)
                         if regime == 'unidir_ul_8flow_hammer' else REGIMES[regime]) if operator else REGIMES[regime]
    if ((row.get('active_flow_count'), row.get('bidirectional')) != expected_workload
            or type(row.get('active_flow_count')) is not int or type(row.get('bidirectional')) is not bool):
        raise ValueError('Exact typed workload declaration required')
    context = _context(row)
    coverage = row.get('coverage_class')
    provenance = row.get('certified_wds_evidence', {})
    recorded_class = provenance.get('coverage_class') if isinstance(provenance, dict) else None
    if coverage is None:
        if recorded_class is not None:
            raise ValueError('Unknown coverage conflicts with a declared provenance class')
    else:
        _integer(coverage, 'declared coverage class', 0, 33 if operator else 31)
        expected_distance = (OPERATOR_COVERAGE_DISTANCES if operator else {6:3000,13:6000}).get(coverage)
        if expected_distance is None:
            raise ValueError('Unsupported declared coverage class')
        for point in (row.get('distance_meters'), row['ap_policy'].get('distance_meters'),
                      row['cpe_policy'].get('distance_meters')):
            if _integer(point, 'coverage timing meters', 0, 2**32-1) != expected_distance:
                raise ValueError('Declared coverage class and programmed timing conflict')
        if (type(recorded_class) is not int or recorded_class != coverage
                or provenance.get('physical_distance_verified') is not False):
            raise ValueError('Programmed coverage evidence required; physical distance not established')
        rid = str(row.get('round_id'))
        shared_new_context = operator and bool(re.fullmatch(r'R[1-9][0-9]*', rid)) and 61 <= int(rid[1:]) <= 134
        if operator and (coverage == 0 or shared_new_context):
            slot, ack = OPERATOR_TIMINGS[coverage]
            for field,expected in (('slot_time_us',slot),('ack_timeout_us',ack)):
                if _integer(provenance.get(field),'explicit timing '+field) != expected:
                    raise ValueError('Explicit coverage slot/ACK context required')
                if (field in row or shared_new_context) and _integer(row.get(field),'recorded '+field) != expected:
                    raise ValueError('Conflicting explicit slot/ACK context')
            if provenance.get('effective_timing_independently_verified') is not False:
                raise ValueError('Saved context does not prove effective timing')
            if shared_new_context and (provenance.get('slot_ack_source') != 'SHARED_PAYLOAD_TREATMENT_KNOBS'
                    or provenance.get('saved_context_credited') is not True):
                raise ValueError('New round shared saved slot/ACK provenance required')
    # Generic workload names must retain the same coverage boundary as aliases.
    # None is unknown, not an inferred class from a matching timing distance.
    return (*context, coverage)


def _window_checks(row, blocks, manifests):
    reasons = []
    own = _rows_for_block(blocks, row)
    if row.get('window_kind', 'primary') != 'primary': reasons.append('NOT_PRIMARY_WINDOW')
    if row.get('restoration_verified') is not True: reasons.append('RESTORATION_NOT_TRUE')
    if _number(row.get('packet_loss_pct'), 'packet loss', 0, 100) != 0: reasons.append('PACKET_LOSS')
    if _integer(row.get('station_drops'), 'station drops') != 0: reasons.append('STATION_DROP')
    failure = row.get('source_failure_metadata')
    if failure is not None:
        if not isinstance(failure, dict) or type(failure.get('crash')) is not bool:
            raise ValueError('Malformed source failure metadata')
        if failure.get('disqualified') is not None and type(failure['disqualified']) is not bool:
            raise ValueError('Malformed source disqualification')
        if failure['crash'] or failure.get('disqualified') is True: reasons.append('SOURCE_CRASH_OR_DISQUALIFICATION')
    previous = _number(row.get('p50_ms'), 'p50')
    previous = _number(row.get('p95_ms'), 'p95', previous)
    _number(row.get('p99_ms'), 'p99', previous)
    provenance = row.get('certified_wds_evidence')
    if not isinstance(provenance, dict) or provenance.get('counter_interface') != 'phy0-ap0.sta1':
        reasons.append('WDS_INTERFACE_PROVENANCE_MISSING')
        provenance = {}
    for field in ('source_receipt', 'source_recipe'):
        ref = provenance.get(field)
        if not isinstance(ref, dict) or not any(all(ref.get(k) == e.get(k) for k in ('path', 'bytes', 'sha256')) for e in manifests):
            reasons.append('PINNED_' + field.upper() + '_MISSING')
    if not own:
        raise ValueError('Source blocks required')
    flat = [v for b in own for v in b['rtts_ms']]
    for value in flat: _number(value, 'RTT')
    if not flat or flat != row.get('rtts_ms'): reasons.append('RTT_CHRONOLOGY_MISMATCH')
    seen = set()
    for b in own:
        identity = (_integer(b['block_index'], 'block index'), _integer(b['crossover_step'], 'step'))
        if identity in seen: raise ValueError('Duplicate source block')
        seen.add(identity)
        sent = _integer(b['pings_sent'], 'pings sent', 1)
        if _integer(b['pings_rcvd'], 'pings received', 0, sent) != sent or len(b['rtts_ms']) != sent:
            reasons.append('BLOCK_PACKET_LOSS_OR_COUNT_MISMATCH')
        obs = b['observation']
        if 'station_drops' in obs and _integer(obs['station_drops'], 'block station drops'):
            reasons.append('BLOCK_STATION_DROP')
        if 'restoration_verified' in obs:
            if type(obs['restoration_verified']) is not bool: raise ValueError('Block restoration must be bool')
            if not obs['restoration_verified']: reasons.append('BLOCK_RESTORATION_FAILED')
        if 'packet_loss_pct' in obs and _number(obs['packet_loss_pct'], 'block loss', 0, 100):
            reasons.append('BLOCK_PACKET_LOSS')
        _integer(b['mac_tx_packets_delta'], 'block MAC packets', 1)
        _integer(b['mac_tx_retries_delta'], 'block MAC retries')
        if b.get('counter_interface') != 'phy0-ap0.sta1': reasons.append('BLOCK_COUNTER_INTERFACE_MISSING')
    packets = _integer(row['mac_tx_packets'], 'MAC packets', 1)
    retries = _integer(row['mac_tx_retries'], 'MAC retries')
    if sum(b['mac_tx_packets_delta'] for b in own) != packets or sum(b['mac_tx_retries_delta'] for b in own) != retries:
        reasons.append('MAC_COUNTER_SUM_MISMATCH')
    if abs(_number(row['mac_retry_rate'], 'reported retry fraction') - retries / packets) > .0000051:
        reasons.append('REPORTED_RETRY_FRACTION_MISMATCH')
    audit = dyadic_mean_audit(row, blocks)
    if not all(v['exact'] for v in audit.values()): reasons.append('FRACTION_OR_NUMPY_MEAN_NOT_ZERO_ULP')
    return reasons, audit


def _alias_valid(rows, blocks, metric):
    other = 'dl_goodput_mbps' if metric == 'ul_goodput_mbps' else 'ul_goodput_mbps'
    return (all(r[other] == 0 and r[metric] == r['goodput_mbps'] for r in rows)
            and all(b[other] == 0 and b[metric] == b['observation']['goodput_rx_mbps']
                    for r in rows for b in _rows_for_block(blocks, r)))


def _p99_diagnostic(contrasts, projection, blocks, target, control, source_units, wins):
    """Check an optional accepted projection without qualifying the primary profile."""
    out=dict(status='UNKNOWN',metric='p99_rtt_ms',wins=wins,paired_count=len(source_units),
        HL=None,p_exact_rank=None,holm500_adjusted_p=None,comparability_status=None,
        used_for_primary_profile_eligibility=False,complete_five_outcome_qualification=False)
    try:
        own=[c for c in contrasts if c.get('metric')=='p99_rtt_ms']
        if len(own)!=1:return {**out,'reason':'NO_UNIQUE_DIRECT_P99_STATISTICAL_PROJECTION'}
        contrast=own[0];units=contrast['paired_unit_ids']
        if not isinstance(units,list):raise ValueError('Paired units required')
        for unit in units:
            if not isinstance(unit,dict) or set(unit)!={'round_id','block_index'}:raise ValueError('Typed paired unit required')
            _integer(unit['block_index'],'diagnostic paired block index')
        normalized=[(u['round_id'],u['block_index']) for u in units]
        if sorted(normalized)!=source_units or len(set(normalized))!=len(normalized):
            raise ValueError('P99 diagnostic paired scope differs')
        hypothesis=contrast['source_hypothesis_id'];family=projection['families'][contrast['family500_key']]
        q=_holm(family,hypothesis,500);p=_number(contrast['p_exact_rank'],'diagnostic p',0,1)
        hl=_number(_matched_hl(blocks,[target],[control],normalized,'p99_rtt_ms'),'diagnostic HL',-math.inf)
        claimed=_number(contrast['holm500_adjusted_p'],'diagnostic Holm500',0,1)
        effect=_number(contrast['effect_hl'],'diagnostic source HL',-math.inf)
        comparable=contrast.get('comparability_status') in ('COMPARABLE','WITHIN_ROUND_DECLARED_PACKAGE_COMPARISON')
        if (family['known_hypotheses'][hypothesis]!=p or abs(q-claimed)>1e-12
                or abs(hl-effect)>max(1e-10,abs(hl)*1e-12) or p<2.0**(1-len(units))
                or contrast.get('direction')!='lower' or not comparable):
            raise ValueError('P99 diagnostic source statistics disagree')
        return {**out,'status':'SOURCE_CHECKED_DIAGNOSTIC','HL':hl,'p_exact_rank':p,
            'holm500_adjusted_p':q,'source_hypothesis_id':hypothesis,
            'comparability_status':contrast['comparability_status'],
            'favorable_HL_and_Holm500':hl<0 and q<=.05,'unanimous_favorable_blocks':wins==16}
    except (ValueError,TypeError,KeyError,IndexError,AttributeError,OverflowError,ZeroDivisionError) as error:
        return {**out,'reason':'INVALID_OR_UNBOUND_P99_DIAGNOSTIC','error_type':type(error).__name__}


def evaluate_policy(evidence, *, regime, round_id, policy_id, control_policy_id, mode='STRICT'):
    """One exact target/control/round; all source pairs, no outcome-wise controls."""
    return _evaluate_policy(evidence, regime=regime, round_id=round_id, policy_id=policy_id,
                            control_policy_id=control_policy_id, mode=mode)


def evaluate_operator_policy(evidence, *, regime, round_id, policy_id, control_policy_id,
                             mode='strict_goodput_preservation', distance_meters=None, coverage_class=None):
    """Explicit operator utilities; retry cost is reported, legacy veto unchanged.

    Directional UL gain >=40%; 40..80% is a descriptive expected band, not a
    veto against larger gains. The separate retry-preserving profile requires
    four unanimous outcomes and exposes p99 without all-five qualification.
    Unknown timing never satisfies a requested distance class.
    """
    return _evaluate_policy(evidence, regime=regime, round_id=round_id, policy_id=policy_id,
        control_policy_id=control_policy_id, mode=mode, operator=True, distance_meters=distance_meters, coverage_class=coverage_class)


def _evaluate_policy(evidence, *, regime, round_id, policy_id, control_policy_id, mode,
                      operator=False, distance_meters=None, coverage_class=None):
    out = dict(status='BLOCKED', mode=mode, regime=regime, round_id=round_id,
               policy_id=policy_id, control_policy_id=control_policy_id, reasons=[],
               automatic_execution_allowed=False, physical_acceptance=False,
               total_goodput_noninferiority_claim=False,
               limitations=['Within-link conditional evidence, not independent sector trials.',
                   'Declared coverage is timing, not verified physical range.',
                   'Pinned statistics acceptance is an external caller trust boundary.'])
    if regime not in (OPERATOR_REGIMES if operator else SUPPORTED_REGIMES): return {**out, 'reasons':['UNSUPPORTED_REGIME']}
    if mode not in (OPERATOR_MODES if operator else MODES): return {**out, 'reasons':['UNSUPPORTED_UTILITY_MODE']}
    if mode == RETRY_PRESERVING_MODE and regime not in ('bidir_6flow','covclass6_3km','covclass13_6km'):
        return {**out,'reasons':['RETRY_PRESERVING_PROFILE_REQUIRES_BIDIR_6FLOW']}
    try:
        (_operator_round if operator else _round)(round_id)
        requested_class = _requested_coverage(distance_meters, coverage_class) if operator else None
        data = evidence.parse()
        primary = data[evidence.current_view]
        rows, blocks = primary['records']['records'], primary['blocks']['crossed']
        targets = [r for r in rows if r['round_id'] == round_id and r['policy_key'] == policy_id and _in_regime(r, regime)]
        controls = [r for r in rows if r['round_id'] == round_id and r['policy_key'] == control_policy_id and _in_regime(r, regime)]
        if len(targets) != 1 or len(controls) != 1 or policy_id == control_policy_id:
            return {**out, 'reasons':['UNIQUE_RECORDED_TARGET_AND_CONTROL_REQUIRED']}
        target, control = targets[0], controls[0]
        required_metrics=_required_metrics(regime,mode=mode if operator else None)
        if mode == RETRY_PRESERVING_MODE:
            out['profile_contrast_scope']=dict(required_unanimous_metrics=list(required_metrics),
                diagnostic_metrics=['p99_rtt_ms'],complete_five_outcome_qualification=False,
                description='Four-outcome retry-preserving profile; p99 remains visible and is not certified unanimous.')
        context = _scope_identity(target, regime, operator=operator)
        if _scope_identity(control, regime, operator=operator) != context:
            raise ValueError('Target/control context mismatch')
        if operator:
            out['coverage_policy'] = dict(COVERAGE_POLICY)
            if target.get('coverage_class') is not None and target['coverage_class'] > COVERAGE_POLICY_MAX:
                out['reasons'].append('COVERAGE_CLASS_EXCEEDS_SUPPORTED_POLICY_MAX31')
            out['recorded_context'] = dict(distance_meters=target.get('distance_meters'),
                coverage_class=target.get('coverage_class'), physical_distance_verified=False)
            if distance_meters is not None and (target.get('distance_meters') != distance_meters
                    or target.get('coverage_class') != requested_class):
                out['reasons'].append('REQUESTED_DISTANCE_CONTEXT_NOT_RECORDED')
        manifests = [e for view in data.values() for e in view['manifest']]
        out['source_views'] = [{'name':name, 'receipt_sha256':view.receipt_sha256} for name, view in evidence.views]
        out['source_checks'] = {}
        for label, row in (('target', target), ('control', control)):
            reasons, audit = _window_checks(row, blocks, manifests)
            out['reasons'].extend(label.upper() + '_' + r for r in reasons)
            out['source_checks'][label] = dict(dyadic_means=audit, window_id=_identity(row),
                MAC_packets=row['mac_tx_packets'], MAC_retries=row['mac_tx_retries'],
                recorded_block_health_fields=sum('restoration_verified' in b['observation'] for b in _rows_for_block(blocks,row)),
                independent_device_health_verified=False)
        history = []
        history_unknown = []
        for row in rows:
            if row['round_id'] == round_id or row['policy_key'] != policy_id or not _in_regime(row, regime): continue
            if _scope_identity(row, regime, operator=operator) != context: continue
            restoration = row.get('restoration_verified')
            if restoration is not None and type(restoration) is not bool:
                raise ValueError('Historical restoration must be bool or legacy unknown')
            failure = row.get('source_failure_metadata')
            if failure is not None:
                if not isinstance(failure, dict) or type(failure.get('crash')) is not bool:
                    raise ValueError('Historical crash metadata must be typed')
                if failure.get('disqualified') is not None and type(failure['disqualified']) is not bool:
                    raise ValueError('Historical disqualification must be bool or unknown')
            unknown_fields = []
            if restoration is None: unknown_fields.append('restoration_verified')
            if failure is None: unknown_fields.append('source_failure_metadata')
            if unknown_fields:
                history_unknown.append(dict(round_id=row['round_id'], iteration=row['iteration'],
                                            unknown_fields=unknown_fields))
            negative_block = False
            for block in _rows_for_block(blocks, row):
                obs = block['observation']
                sent = _integer(block['pings_sent'], 'historical pings sent', 1)
                received = _integer(block['pings_rcvd'], 'historical pings received', 0, sent)
                if received < sent: negative_block = True
                if 'packet_loss_pct' in obs and _number(obs['packet_loss_pct'], 'historical block loss', 0, 100):
                    negative_block = True
                if 'station_drops' in obs and _integer(obs['station_drops'], 'historical block drops'):
                    negative_block = True
                if 'restoration_verified' in obs:
                    if obs['restoration_verified'] is not None and type(obs['restoration_verified']) is not bool:
                        raise ValueError('Historical block restoration must be bool or legacy unknown')
                    if obs['restoration_verified'] is False: negative_block = True
            if (negative_block or (_number(row['packet_loss_pct'], 'historical target loss', 0, 100) > 0)
                    or _integer(row['station_drops'], 'historical drops') > 0 or restoration is False
                    or failure is not None and (failure['crash'] or failure.get('disqualified') is True)):
                history.append(dict(round_id=row['round_id'],iteration=row['iteration']))
        out['historical_target_negatives'] = history
        out['historical_target_unknown_metadata'] = history_unknown
        if history: out['reasons'].append('KNOWN_NEGATIVE_TARGET_PACKAGE_CONTEXT')
        tr = Fraction(target['mac_tx_retries'], target['mac_tx_packets'])
        cr = Fraction(control['mac_tx_retries'], control['mac_tx_packets'])
        out['retry_fraction'] = dict(target=float(tr), control=float(cr), target_strictly_lower=tr < cr)
        if (not operator or mode == RETRY_PRESERVING_MODE) and not tr < cr:
            out['reasons'].append('TARGET_MAC_RETRY_FRACTION_NOT_LOWER')
        gp, baseline = Fraction(str(target['goodput_mbps'])), Fraction(str(control['goodput_mbps']))
        if baseline <= 0: raise ValueError('Positive control total goodput required')
        floor = gp * 100 >= baseline * 98
        out['utility'] = dict(target_total_goodput_mbps=float(gp), control_total_goodput_mbps=float(baseline),
            observed_total_goodput_loss_pct=float((baseline-gp)*100/baseline), passes_observed_2pct_floor=floor,
            permits_total_goodput_cost=mode=='DIRECTIONAL', independent_noninferiority_test=False)
        if mode == 'STRICT' and not floor: out['reasons'].append('OBSERVED_TOTAL_GOODPUT_LOSS_EXCEEDS_2PCT')
        if operator:
            loss = (baseline-gp)*100/baseline
            ul_control = Fraction(str(_number(control.get('ul_goodput_mbps'), 'control UL')))
            ul_target = Fraction(str(_number(target.get('ul_goodput_mbps'), 'target UL')))
            ul_gain = (ul_target-ul_control)*100/ul_control if ul_control else None
            maximum = 15 if mode == OPERATOR_MODES[1] else 2
            out['utility'].update(observed_total_goodput_loss_fraction=str(loss),
                max_total_goodput_drop_pct=maximum, passes_operator_goodput_floor=loss <= maximum,
                ul_gain_pct=float(ul_gain) if ul_gain is not None else None,
                ul_gain_fraction=str(ul_gain) if ul_gain is not None else None,
                expected_ul_gain_band_pct=[40,80], retry_cost_is_diagnostic=mode != RETRY_PRESERVING_MODE,
                permits_total_goodput_cost=True)
            if loss > maximum: out['reasons'].append('OPERATOR_GOODPUT_DROP_LIMIT_EXCEEDED')
            if mode == OPERATOR_MODES[1] and (ul_gain is None or ul_gain < 40):
                out['reasons'].append('DIRECTIONAL_UL_GAIN_BELOW_40PCT')
        unit_t = {(b['round_id'],b['block_index']) for b in _rows_for_block(blocks,target)}
        unit_c = {(b['round_id'],b['block_index']) for b in _rows_for_block(blocks,control)}
        if unit_t != unit_c: raise ValueError('Different complete source paired sets')
        source_units = sorted(unit_t)
        if operator:
            if len(source_units) != 16: out['reasons'].append('EXACTLY_16_MATCHED_BLOCKS_REQUIRED')
            ordered_pairs=[]
            for rid,bid in source_units:
                steps=[]
                for row in (target,control):
                    own=[b for b in _rows_for_block(blocks,row) if b['block_index']==bid]
                    if len(own)!=1: raise ValueError('Unique per-arm matched block required')
                    steps.append(_integer(own[0]['crossover_step'],'AB/BA step',0,1))
                ordered_pairs.append(tuple(steps))
            if ordered_pairs.count((0,1))!=8 or ordered_pairs.count((1,0))!=8:
                out['reasons'].append('BALANCED_8AB_8BA_DESIGN_REQUIRED')
            for row in (target, control):
                if sum(b['pings_sent'] for b in _rows_for_block(blocks,row)) != 160:
                    out['reasons'].append('EXACTLY_160_RTT_PER_ARM_REQUIRED')
            out['paired_block_wins'] = {}
            for metric in _required_metrics(regime):
                direction = -1 if metric in LATENCY_METRICS else 1
                values = []
                for rid, bid in source_units:
                    pair = []
                    for row in (target,control):
                        own = [b for b in _rows_for_block(blocks,row) if b['block_index']==bid]
                        if len(own) != 1: raise ValueError('Unique per-arm matched block required')
                        block=own[0]
                        pair.append(_number(block.get(metric, block['observation'].get(metric)), 'paired metric'))
                    values.append((Fraction(str(pair[0]))-Fraction(str(pair[1])))*direction)
                wins=sum(v>0 for v in values)
                out['paired_block_wins'][metric] = dict(wins=wins, pairs=len(values))
                if metric in required_metrics and (wins != 16 or len(values) != 16):
                    out['reasons'].append('NOT_16_OF_16_FAVORABLE_'+metric)
            if int(round_id[1:]) >= 57 or mode == RETRY_PRESERVING_MODE:
                gp_differences=[]
                for rid,bid in source_units:
                    pair=[]
                    for row in (target,control):
                        block=next(b for b in _rows_for_block(blocks,row) if b['block_index']==bid)
                        pair.append(Fraction(str(_number(block['observation']['goodput_rx_mbps'],'paired total GP'))))
                    gp_differences.append(pair[0]-pair[1])
                out['total_goodput_block_wins']=dict(wins=sum(v>0 for v in gp_differences),
                    losses=sum(v<0 for v in gp_differences),ties=sum(v==0 for v in gp_differences),
                    pairs=len(gp_differences),independent_noninferiority_claim=False)
        sources = []
        for name, view in data.items():
            projection = view['stats']['promotion_evidence']
            matching = [c for c in projection['contrasts'] if c.get('regime') == _workload(regime)
                and c.get('round_ids') == [round_id] and c.get('target_policy_id') == policy_id
                and c.get('control_policy_id') == control_policy_id]
            if matching: sources.append((name, projection, matching))
        if len(sources) != 1: return {**out, 'reasons':sorted(set(out['reasons']+['UNIQUE_PINNED_DIRECT_STATISTICAL_VIEW_REQUIRED']))}
        name, projection, contrasts = sources[0]
        out['statistical_view'] = name
        out['statistical_support'] = []
        for metric in required_metrics:
            eligible = [c for c in contrasts if c.get('metric') == metric or
                        (regime in OPERATOR_UNIDIRECTIONAL_REGIMES and metric in ('dl_goodput_mbps','ul_goodput_mbps') and c.get('metric')=='goodput_rx_mbps')]
            accepted = False
            for contrast in eligible:
                units = contrast.get('paired_unit_ids')
                if not isinstance(units,list): raise ValueError('Exact paired units required')
                for u in units:
                    if not isinstance(u,dict) or set(u)!={'round_id','block_index'}: raise ValueError('Typed paired unit required')
                    _integer(u['block_index'],'paired block index')
                normalized = [(u['round_id'],u['block_index']) for u in units]
                if sorted(normalized) != source_units or len(set(normalized)) != len(normalized): continue
                alias = contrast['metric'] != metric
                if alias and not _alias_valid((target,control),blocks,metric): continue
                if regime in OPERATOR_UNIDIRECTIONAL_REGIMES and not _alias_valid((target,control),blocks,_required_metrics(regime)[-1]):
                    out['reasons'].append('UNIDIRECTIONAL_SOURCE_IDENTITY_MISMATCH')
                    continue
                hypothesis = contrast['source_hypothesis_id']
                family = projection['families'][contrast['family500_key']]
                q = _holm(family,hypothesis,500)
                p = _number(contrast['p_exact_rank'],'rank p',0,1)
                claimed = _number(contrast['holm500_adjusted_p'],'Holm500',0,1)
                hl = _number(_matched_hl(blocks,targets,controls,normalized,metric), 'finite source HL', -math.inf)
                source_effect = _number(contrast['effect_hl'],'HL',-math.inf)
                sign = -1 if metric in LATENCY_METRICS else 1
                if (family['known_hypotheses'][hypothesis] != p or abs(q-claimed)>1e-12
                        or abs(hl-source_effect)>max(1e-10,abs(hl)*1e-12)):
                    continue
                comparable = contrast.get('comparability_status') in ('COMPARABLE','WITHIN_ROUND_DECLARED_PACKAGE_COMPARISON')
                if (comparable and contrast.get('direction') == ('lower' if sign<0 else 'higher')
                        and hl*sign>0 and p>=2.0**(1-len(units)) and q<=.05):
                    accepted = True
                    out['statistical_support'].append(dict(metric=metric,source_metric=contrast['metric'],
                        source_hypothesis_id=hypothesis,paired_count=len(units),HL=hl,p_exact_rank=p,
                        holm500_adjusted_p=q,directional_GP_identity_verified=alias))
            if not accepted: out['reasons'].append('NO_DIRECT_FAVORABLE_HOLM500_'+metric)
        if mode == RETRY_PRESERVING_MODE:
            out['diagnostic_statistics']={'p99_rtt_ms':_p99_diagnostic(contrasts,projection,blocks,target,control,
                source_units,out['paired_block_wins']['p99_rtt_ms']['wins'])}
        out['reasons'] = sorted(set(out['reasons']))
        if not out['reasons']: out['status'] = 'ELIGIBLE_OFFLINE_' + mode
        return out
    except (ValueError,TypeError,KeyError,IndexError,AttributeError,OverflowError,ZeroDivisionError) as error:
        return {**out,'status':'BLOCKED','reasons':sorted(set(out['reasons']+['MALFORMED_OR_UNBOUND_EVIDENCE'])),
                'error_type':type(error).__name__}


def select_policy(evidence, *, regime, mode='STRICT', round_ids=None):
    """Rank eligible exact observed comparisons; never synthesize or actuate."""
    out = dict(status='ABSTAIN',regime=regime,mode=mode,selected=None,evaluations=[],
               automatic_execution_allowed=False,physical_acceptance=False,
               ranking='OBSERVED_TARGET_P95_ASC_GP_DESC_EXACT_ID_ROUND',
               total_goodput_noninferiority_claim=False)
    if regime not in SUPPORTED_REGIMES or mode not in MODES:
        return {**out,'reason':'UNSUPPORTED_REGIME_OR_MODE'}
    try:
        if round_ids is not None:
            if not isinstance(round_ids,(list,tuple)) or not round_ids or len(set(round_ids))!=len(round_ids):
                raise ValueError('Nonempty unique round scope required')
            for r in round_ids:_round(r)
        data=evidence.parse();rows=data[evidence.current_view]['records']['records']
        comparisons=set()
        for saved in data.values():
            for c in saved['stats']['promotion_evidence']['contrasts']:
                rounds=c.get('round_ids')
                if c.get('regime')!=_workload(regime) or not isinstance(rounds,list) or len(rounds)!=1:continue
                rid=_round(rounds[0])
                if round_ids is not None and rid not in round_ids:continue
                if not any(r['round_id']==rid and r['policy_key']==c.get('target_policy_id') and _in_regime(r,regime) for r in rows):continue
                comparisons.add((rid,c['target_policy_id'],c['control_policy_id']))
        eligible=[]
        for rid,target,control in sorted(comparisons):
            result=evaluate_policy(evidence,regime=regime,round_id=rid,policy_id=target,control_policy_id=control,mode=mode)
            out['evaluations'].append(result)
            if result['status'].startswith('ELIGIBLE_OFFLINE_'):
                row=next(r for r in rows if r['round_id']==rid and r['policy_key']==target)
                eligible.append((row['p95_ms'],-row['goodput_mbps'],target,rid,result))
        if eligible:
            out['selected']=min(eligible,key=lambda item:item[:4])[-1]
            out['status']='ELIGIBLE_OFFLINE_'+mode
        elif comparisons:out['status']='BLOCKED'
        return out
    except (ValueError,TypeError,KeyError,AttributeError,OverflowError) as error:
        return {**out,'status':'BLOCKED','reason':'MALFORMED_OR_UNBOUND_EVIDENCE','error_type':type(error).__name__}


def _operator_cost_vector(row, regime):
    """Observed costs; directional Jain and inactive throughput are not objectives."""
    gp=Fraction(str(_number(row['goodput_mbps'],'GP')))
    tail=(-Fraction(str(_number(row['p95_ms'],'p95'))),
          -Fraction(str(_number(row['p99_ms'],'p99'))),
          -Fraction(_integer(row['mac_tx_retries'],'retries'),_integer(row['mac_tx_packets'],'packets',1)))
    if regime in OPERATOR_UNIDIRECTIONAL_REGIMES:
        return (gp,*tail)
    return (gp,Fraction(str(_number(row['ul_goodput_mbps'],'UL'))),
            Fraction(str(_number(row['jain_fairness'],'Jain',0,1))),*tail)


def select_operator_policy(evidence, *, regime, mode='strict_goodput_preservation',
                           distance_meters=None, round_ids=None, coverage_class=None):
    """Select observed eligible comparisons and expose context-grouped Pareto cost.

    Frontier membership is descriptive and does not override any eligibility
    reason. Different saved rounds are not a randomized between-package trial.
    """
    out=dict(status='ABSTAIN',regime=regime,mode=mode,distance_meters=distance_meters,
        selected=None,evaluations=[],pareto_frontier=[],observed_points=[],
        automatic_execution_allowed=False,physical_acceptance=False,
        total_goodput_noninferiority_claim=False,
        frontier_interpretation='DESCRIPTIVE_OBSERVED_WITHIN_RECORDED_CONTEXT_NOT_CAUSAL',
        ranking='OBSERVED_TARGET_P95_ASC_GP_DESC_EXACT_ID_ROUND')
    if regime not in OPERATOR_REGIMES or mode not in OPERATOR_MODES:
        return {**out,'reason':'UNSUPPORTED_REGIME_OR_MODE'}
    try:
        if round_ids is not None:
            if not isinstance(round_ids,(list,tuple)) or not round_ids or len(set(round_ids))!=len(round_ids):
                raise ValueError('Nonempty unique round scope required')
            for rid in round_ids: _operator_round(rid)
        requested_class = _requested_coverage(distance_meters, coverage_class)
        data=evidence.parse();rows=data[evidence.current_view]['records']['records']
        comparisons=set()
        for saved in data.values():
            for contrast in saved['stats']['promotion_evidence']['contrasts']:
                rounds=contrast.get('round_ids')
                if contrast.get('regime') != _workload(regime) or not isinstance(rounds,list) or len(rounds)!=1: continue
                rid=_operator_round(rounds[0])
                if round_ids is not None and rid not in round_ids: continue
                if any(r['round_id']==rid and r['policy_key']==contrast.get('target_policy_id') and _in_regime(r,regime) for r in rows):
                    comparisons.add((rid,contrast['target_policy_id'],contrast['control_policy_id']))
        eligible=[];eligible_contexts=set();points={}
        for rid,target,control in sorted(comparisons):
            result=evaluate_operator_policy(evidence,regime=regime,round_id=rid,policy_id=target,
                control_policy_id=control,mode=mode,distance_meters=distance_meters,coverage_class=coverage_class)
            out['evaluations'].append(result)
            own=[r for r in rows if r['round_id']==rid and r['policy_key'] in (target,control)]
            for row in own:
                context=_scope_identity(row,regime,operator=True)
                # Unknown context remains an explicit group; it cannot match a distance request.
                if distance_meters is not None and (row.get('distance_meters') != distance_meters or
                        row.get('coverage_class') != requested_class): continue
                values=_operator_cost_vector(row,regime)
                key=(rid,row['iteration'])
                points[key]=(context,values,dict(round_id=rid,iteration=row['iteration'],policy_id=row['policy_key'],
                    role='target' if row['policy_key']==target else 'control',
                    distance_meters=row.get('distance_meters'),coverage_class=row.get('coverage_class'),
                    goodput_mbps=row['goodput_mbps'],ul_goodput_mbps=row['ul_goodput_mbps'],
                    jain_fairness=row['jain_fairness'],p95_ms=row['p95_ms'],p99_ms=row['p99_ms'],
                    retry_fraction=float(-values[-1]),eligibility_status=result['status'] if row['policy_key']==target else 'REFERENCE_CONTROL',
                    reasons=result['reasons'] if row['policy_key']==target else []))
            if result['status'].startswith('ELIGIBLE_OFFLINE_'):
                row=next(r for r in own if r['policy_key']==target)
                eligible.append((row['p95_ms'],-row['goodput_mbps'],target,rid,result))
                eligible_contexts.add(_scope_identity(row,regime,operator=True))
        for context,values,point in points.values():
            dominated=any(other_context==context and all(a>=b for a,b in zip(other,values))
                and any(a>b for a,b in zip(other,values)) for other_context,other,_ in points.values())
            point['pareto_nondominated']=not dominated
            out['observed_points'].append(point)
            if not dominated: out['pareto_frontier'].append(point)
        out['eligible_contexts']=[dict(distance_meters=c[0],encryption_mode=c[1],associated_cpes=list(c[2]),coverage_class=c[3])
                                  for c in sorted(eligible_contexts,key=repr)]
        if len(eligible_contexts)>1:
            out['status']='BLOCKED'
            out['reason']='AMBIGUOUS_ELIGIBLE_CONTEXTS'
        elif eligible:
            # Rank the nondominated eligible subset. A blocked observation may
            # be displayed on the frontier but cannot veto an eligible choice.
            def vector(item):
                return next(values for _,values,p in points.values()
                            if p['round_id']==item[3] and p['policy_id']==item[2])
            nondominated=[item for item in eligible if not any(
                all(a>=b for a,b in zip(vector(other),vector(item)))
                and any(a>b for a,b in zip(vector(other),vector(item))) for other in eligible)]
            out['selected']=min(nondominated,key=lambda item:item[:4])[-1]
            out['status']='ELIGIBLE_OFFLINE_'+mode
        elif comparisons: out['status']='BLOCKED'
        return out
    except (ValueError,TypeError,KeyError,IndexError,AttributeError,OverflowError,ZeroDivisionError) as error:
        return {**out,'status':'BLOCKED','selected':None,'reason':'MALFORMED_OR_UNBOUND_EVIDENCE',
                'error_type':type(error).__name__}


def audit_recorded_uplink_laws(evidence, *, round_ids=None):
    """Expose the UL2/UL8 saved packages with unchanged strict eligibility.

    Six distance knots are an observed lookup, not an interpolating controller.
    Neither an RTS/ACK-clock package comparison nor a 'pureVO' label proves an
    adaptive decision rule or an AC_VO packet-size filter.
    """
    out = dict(status='ABSTAIN', packages=[], missing_rounds=[],
        ul2_segment_slopes_us_per_km=[], ul2_observed_discrete_concavity=None,
        logarithmic_formula=None, interpolation_allowed=False,
        pure_ac_vo_160_verified=False, adaptive_rts_control_law_verified=False,
        automatic_execution_allowed=False, physical_acceptance=False)
    requested = [f'R{n}' for n in range(116,135)] if round_ids is None else round_ids
    allowed = {f'R{n}' for n in range(116,135)}
    if (not isinstance(requested, (list,tuple)) or not requested or
            any(type(r) is not str or r not in allowed for r in requested) or
            len(set(requested)) != len(requested)):
        return {**out, 'status':'BLOCKED', 'reason':'UNSUPPORTED_UL_LAW_ROUND_SCOPE'}
    try:
        from orchestration.autoresearch.fmx_offline_data import recorded_uplink_package
        data = evidence.parse()
        rows = data[evidence.current_view]['records']['records']
        contrasts = data[evidence.current_view]['stats']['promotion_evidence']['contrasts']
        for rid in sorted(requested, key=lambda r:int(r[1:])):
            pairs = {(c['target_policy_id'], c['control_policy_id']) for c in contrasts if c.get('round_ids') == [rid]}
            if not pairs:
                out['missing_rounds'].append(rid)
                continue
            if len(pairs) != 1:
                raise ValueError('Ambiguous recorded law package contrast')
            target, control = next(iter(pairs))
            summaries = []
            for policy_id in (target,control):
                own = [r for r in rows if r['round_id']==rid and r['policy_key']==policy_id]
                if len(own) != 1:
                    raise ValueError('Unique source-bound law package arm required')
                row=own[0]
                _scope_identity(row, row['workload_regime'], operator=True)
                summaries.append(recorded_uplink_package(row))
            evaluation = evaluate_operator_policy(evidence, regime=summaries[0]['workload_regime'],
                round_id=rid, policy_id=target, control_policy_id=control,
                mode='strict_goodput_preservation', distance_meters=summaries[0]['distance_meters'],
                coverage_class=summaries[0]['coverage_class'])
            out['packages'].append(dict(round_id=rid, target=summaries[0], control=summaries[1],
                strict_evaluation=evaluation))
        knots = [p['target'] for p in out['packages'] if p['target']['workload_regime']=='unidir_ul_2flow']
        knots.sort(key=lambda p:p['distance_meters'])
        if len(knots)==6:
            slopes = [Fraction((b['cpe_be_us'][0]-a['cpe_be_us'][0])*1000,
                               b['distance_meters']-a['distance_meters']) for a,b in zip(knots,knots[1:])]
            out['ul2_segment_slopes_us_per_km']=[str(s) for s in slopes]
            out['ul2_observed_discrete_concavity']=all(a>=b for a,b in zip(slopes,slopes[1:]))
        out['status']='INCOMPLETE_RECORDED_PACKAGES' if out['missing_rounds'] else 'AUDITED_RECORDED_PACKAGES'
        return out
    except (ValueError,TypeError,KeyError,IndexError,AttributeError,OverflowError,ZeroDivisionError) as error:
        return {**out, 'status':'BLOCKED', 'packages':[], 'reason':'MALFORMED_OR_UNBOUND_EVIDENCE',
                'error_type':type(error).__name__}


def _hmac_observed_goodput(control, target):
    """Literal descriptive <2% predicate, never statistical noninferiority."""
    for value in (control,target):
        if type(value) not in (int,float) or value<=0:
            raise ValueError('Positive finite saved goodput required')
        try:
            valid=math.isfinite(value)
        except OverflowError as error:
            raise ValueError('Finite representable saved goodput required') from error
        if not valid:
            raise ValueError('Positive finite saved goodput required')
    loss=100*(Fraction(str(control))-Fraction(str(target)))/Fraction(str(control))
    return dict(observed_total_goodput_loss_percent=str(loss),
                observed_total_goodput_drop_strictly_below_2pct=loss<2,
                statistical_noninferiority_qualified=False)


def audit_available_hmac_packages(*, manifest_path, expected_manifest_sha256,
                                  silicon_path, expected_silicon_sha256):
    """Diagnose the frozen hMAC/VoIP regime without borrowing other regimes.

    These saved packages have no accepted same-regime statistical receipt or
    effective queue-gating qualification. Their observations are useful, but
    cannot become eligible by relabelling ordinary bidirectional results.
    """
    from orchestration.autoresearch.fmx_live_dataset import (
        load_available_hmac_dataset, load_available_hmac_blocks)
    from orchestration.autoresearch.fmx_silicon_receipt import (
        load_saved_silicon_receipt, audit_saved_silicon_receipt)
    result=dict(status='ABSTAIN_NO_QUALIFIED_HMAC_PACKAGE',packages=[],
        regime='bidir_8flow_voip_hmac',recommended_policy=None,
        independently_accepted_same_regime_statistics=False,
        automatic_execution_allowed=False,physical_acceptance=False,
        historical_selector_behavior_changed=False)
    try:
        options=dict(manifest_path=manifest_path,expected_manifest_sha256=expected_manifest_sha256)
        data=load_available_hmac_dataset(**options)
        blocks=load_available_hmac_blocks(**options)
        silicon=audit_saved_silicon_receipt(load_saved_silicon_receipt(
            silicon_path,expected_sha256=expected_silicon_sha256))
        # The explicit probe must belong to this input freeze, not merely have
        # an attractive experiment label from a different acquisition.
        import hashlib
        import json
        raw=Path(manifest_path).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=expected_manifest_sha256:
            raise ValueError('Input manifest changed during audit')
        manifest=json.loads(raw)
        probe_pins=[b['sha256'] for b in manifest['bindings'] if
            b['path'].endswith('/pb_021_031_050_live_lap120_silicon_qualification_20261024.json')]
        if probe_pins!=[expected_silicon_sha256]:
            raise ValueError('Probe does not belong to the caller-accepted freeze')
        timing={row['coverage_class']:row for row in silicon['timing_rows']}
        rows=[row for row in data['records'] if row.get('workload_regime')==result['regime']]
        expected_rounds=[row['round_id'] for row in manifest['available']]
        if set(row['round_id'] for row in rows)!=set(expected_rounds):
            raise ValueError('Frozen hMAC round identities changed')
        for round_id in expected_rounds:
            own=[row for row in rows if row['round_id']==round_id]
            if len(own)!=2 or any(row['active_flow_count']!=8 or row['bidirectional'] is not True for row in own):
                raise ValueError('Exact two-arm hMAC/VoIP context required')
            control,target=own
            if [row['source_position'] for row in own]!=['/iterations/0','/iterations/1']:
                raise ValueError('Explicit saved control/target source order required')
            utility=_hmac_observed_goodput(control['goodput_mbps'],target['goodput_mbps'])
            reasons=['NO_ACCEPTED_SAME_REGIME_STATISTICAL_RECEIPT',
                     'EFFECTIVE_HMAC_QUEUE_GATING_UNQUALIFIED',
                     'VOIP_SERVICE_METRICS_AND_EFFECTIVE_TID_ATTRIBUTION_UNQUALIFIED',
                     'SILICON_CONTROL_BOUNDARY_UNQUALIFIED']
            if not utility['observed_total_goodput_drop_strictly_below_2pct']:
                reasons.append('OBSERVED_TOTAL_GOODPUT_DROP_NOT_BELOW_2PCT')
            coverage=target['coverage_class']
            declared_ack=target['certified_wds_evidence']['ack_timeout_us']
            result['packages'].append(dict(round_id=round_id,status='BLOCKED',reasons=reasons,
                control_policy_id=control['iteration'],policy_id=target['iteration'],
                control_policy_key=control['policy_key'],policy_key=target['policy_key'],
                distance_meters=target['distance_meters'],coverage_class=coverage,
                declared_ack_timeout_us=declared_ack,
                saved_probe_reported_ack_timeout_us=timing[coverage]['reported_ack_timeout_us'],
                declaration_matches_saved_probe_ack=declared_ack==timing[coverage]['reported_ack_timeout_us'],
                effective_timing_verified=False,voip_evidence=target['voip_evidence'],
                hmac_source_controls=target['hmac_source_controls'],utility=utility,
                generic_rtt_is_not_automatically_voip_service_latency=True,
                physical_acceptance=False,automatic_execution_allowed=False))
        result.update(source_manifest_sha256=expected_manifest_sha256,
            silicon_receipt_sha256=expected_silicon_sha256,
            records=len(data['records']),crossed_windows=len(blocks['crossed']),
            sequential_windows=len(blocks['sequential']),missing_at_cutoff=manifest['missing_at_cutoff'],
            silicon_boundary=silicon)
        return result
    except (ValueError,TypeError,KeyError,IndexError,AttributeError,OverflowError,OSError) as error:
        return {**result,'status':'BLOCKED','packages':[],
                'reasons':['MALFORMED_OR_UNBOUND_HMAC_EVIDENCE'],'error_type':type(error).__name__}


def select_available_hmac_policy(*, distance_meters, coverage_class, **source_options):
    """Return an explicit abstention for this unqualified saved regime."""
    _integer(distance_meters,'hMAC requested distance',1)
    _integer(coverage_class,'hMAC requested coverage',0,33)
    if OPERATOR_COVERAGE_DISTANCES.get(coverage_class)!=distance_meters:
        raise ValueError('Exact declared distance and coverage context required')
    report=audit_available_hmac_packages(**source_options)
    packages=[row for row in report['packages'] if row['distance_meters']==distance_meters and
              row['coverage_class']==coverage_class]
    return dict(status='ABSTAIN',recommended_policy=None,regime='bidir_8flow_voip_hmac',
        distance_meters=distance_meters,coverage_class=coverage_class,recorded_packages=packages,
        reasons=report.get('reasons') or ['NO_QUALIFIED_PACKAGE_FOR_EXACT_HMAC_CONTEXT'],
        missing_at_cutoff=report.get('missing_at_cutoff'),
        automatic_execution_allowed=False,physical_acceptance=False)


def audit_full_hmac_packages(*,manifest_path,expected_manifest_sha256,
                             silicon_path=None,expected_silicon_sha256=None):
    """Diagnose twelve saved packages; no transfer from ordinary bidirectional data.

    A recipe-declared static HTT pair is retained in the new policy identities.
    It supplies neither feedback-adaptive aggregation nor voice-service proof.
    """
    from orchestration.autoresearch import fmx_full_hmac_dataset as full
    from orchestration.autoresearch.fmx_silicon_receipt import load_saved_silicon_receipt,audit_saved_silicon_receipt
    result=dict(status='ABSTAIN_NO_QUALIFIED_HMAC_PACKAGE',packages=[],regime=full.REGIME,
        recommended_policy=None,independently_accepted_same_regime_statistics=False,
        physical_acceptance=False,automatic_execution_allowed=False,historical_selector_behavior_changed=False)
    try:
        options=dict(manifest_path=manifest_path,expected_manifest_sha256=expected_manifest_sha256)
        data=full.load_full_hmac_dataset(**options);blocks=full.load_full_hmac_blocks(**options)
        pin=data['silicon_receipt_binding'];probe=full._safe_path(full.ROOT/pin['path'])
        if (silicon_path is None)!=(expected_silicon_sha256 is None):raise ValueError('Both explicit silicon path and pin required')
        if silicon_path is not None and(full._safe_path(silicon_path)!=probe or expected_silicon_sha256!=pin['sha256']):
            raise ValueError('Silicon evidence must be the exact authenticated frozen member')
        silicon=audit_saved_silicon_receipt(load_saved_silicon_receipt(probe,expected_sha256=pin['sha256']))
        timing={row['coverage_class']:row for row in silicon['timing_rows']}
        rows=[r for r in data['records']if r.get('workload_regime')==full.REGIME]
        if len(rows)!=24 or {r['round_id']for r in rows}!={f'R{n}'for n in full.CONTEXTS}:
            raise ValueError('Exact twelve two-arm saved hMAC packages required')
        for number,context in full.CONTEXTS.items():
            own=[r for r in rows if r['round_id']==f'R{number}']
            if len(own)!=2 or [r['source_position']for r in own]!=['/iterations/0','/iterations/1']:
                raise ValueError('Source control/target order is explicit, never inferred from KEEP')
            control,target=own;distance,coverage,slot,ack=context
            if any(r['active_flow_count']!=8 or r['bidirectional']is not True or r['distance_meters']!=distance
                   or r['coverage_class']!=coverage for r in own):raise ValueError('Exact saved hMAC context required')
            utility=_hmac_observed_goodput(control['goodput_mbps'],target['goodput_mbps'])
            reasons=['NO_ACCEPTED_SAME_REGIME_STATISTICAL_RECEIPT','EFFECTIVE_HMAC_QUEUE_GATING_UNQUALIFIED',
                'VOIP_SERVICE_METRICS_AND_EFFECTIVE_TID_ATTRIBUTION_UNQUALIFIED','SILICON_CONTROL_BOUNDARY_UNQUALIFIED']
            if not utility['observed_total_goodput_drop_strictly_below_2pct']:
                reasons.append('OBSERVED_TOTAL_GOODPUT_DROP_NOT_BELOW_2PCT')
            compound=target.get('compound_recipe_controls')
            if compound and compound.get('declared_endpoint_pairs')is not None:
                reasons.append('STATIC_COMPOUND_HTT_DECLARATION_IS_NOT_ADAPTIVE_OR_CAUSAL_QUALIFICATION')
            result['packages'].append(dict(round_id=f'R{number}',status='BLOCKED',reasons=reasons,
                control_policy_id=control['iteration'],policy_id=target['iteration'],
                control_policy_key=control['policy_key'],policy_key=target['policy_key'],
                distance_meters=distance,coverage_class=coverage,declared_slot_time_us=slot,declared_ack_timeout_us=ack,
                saved_probe_reported_ack_timeout_us=timing[coverage]['reported_ack_timeout_us'],
                declaration_matches_saved_probe_ack=ack==timing[coverage]['reported_ack_timeout_us'],
                effective_timing_verified=False,physical_distance_verified=False,
                control_saved_health=dict(packet_loss_pct=control['packet_loss_pct'],station_drops=control['station_drops'],
                    restoration_verified=control['restoration_verified'],source_failure_metadata=control['source_failure_metadata']),
                target_saved_health=dict(packet_loss_pct=target['packet_loss_pct'],station_drops=target['station_drops'],
                    restoration_verified=target['restoration_verified'],source_failure_metadata=target['source_failure_metadata']),
                voip_evidence=target['voip_evidence'],hmac_source_controls=target['hmac_source_controls'],
                compound_recipe_controls=compound,reported_batch=target.get('reported_batch'),
                source_reported_experiment_ref=target.get('source_reported_experiment_ref'),utility=utility,
                generic_rtt_is_not_automatically_voip_service_latency=True,
                physical_acceptance=False,automatic_execution_allowed=False))
        result.update(records=len(data['records']),crossed_windows=len(blocks['crossed']),
            sequential_windows=len(blocks['sequential']),missing_at_cutoff=[],historical_missing_rounds=[110,111,112,113],
            source_manifest_sha256=expected_manifest_sha256,silicon_receipt_sha256=pin['sha256'],silicon_boundary=silicon)
        return result
    except (ValueError,TypeError,KeyError,IndexError,AttributeError,OverflowError,OSError)as error:
        return {**result,'status':'BLOCKED','packages':[],
            'reasons':['MALFORMED_OR_UNBOUND_FULL_HMAC_EVIDENCE'],'error_type':type(error).__name__}


def select_full_hmac_policy(*,distance_meters,coverage_class,**source_options):
    """Context-exact, deterministic abstention for the unqualified full cohort."""
    _integer(distance_meters,'full hMAC requested distance',1)
    _integer(coverage_class,'full hMAC requested coverage',0,31)
    from orchestration.autoresearch.fmx_full_hmac_dataset import CONTEXTS
    if (distance_meters,coverage_class)not in {(v[0],v[1])for v in CONTEXTS.values()}:
        raise ValueError('Only an observed declared context, without interpolation')
    report=audit_full_hmac_packages(**source_options)
    return dict(status='ABSTAIN',recommended_policy=None,regime='bidir_8flow_voip_hmac',
        distance_meters=distance_meters,coverage_class=coverage_class,
        recorded_packages=[p for p in report['packages']if p['distance_meters']==distance_meters and p['coverage_class']==coverage_class],
        reasons=report.get('reasons')or['NO_QUALIFIED_PACKAGE_FOR_EXACT_HMAC_CONTEXT'],
        missing_at_cutoff=report.get('missing_at_cutoff'),physical_acceptance=False,automatic_execution_allowed=False)
