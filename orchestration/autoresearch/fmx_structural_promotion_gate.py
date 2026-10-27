"""Source-pinned offline canary eligibility; never permission or an actuator.

The caller supplies an independently accepted statistics receipt SHA256. A
matching status string alone is insufficient. Paths are explicit local files;
paths advertised by source metadata are not opened. No tolerance replaces the
literal decimal block-mean contract. No cross-regime significance transfer.
"""
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re
from statistics import median
from types import SimpleNamespace

from controller.adaptive_aql_regime_controller import policy_metadata


REGIMES = {'bidir_6flow': (6, True), 'bidir_2flow': (2, True),
           'unidir_dl_2flow': (2, False), 'unidir_ul_2flow': (2, False),
           'bidir_8flow': (8, True), 'covclass6_3km': (6, True),
           'covclass13_6km': (6, True)}
COVERAGE_CONTEXTS = {'covclass6_3km': (3000, 6), 'covclass13_6km': (6000, 13)}
HOOKS = {'short_retry_limit': (0, 255), 'long_retry_limit': (0, 255),
         'force_tx_status': (0, 1), 'ani_enable': (0, 1),
         'airtime_flags': (0, 3), 'fq_limit': (1, 2**32-1)}
REQUIRED_METRICS = {'bidir_6flow': ('p50_rtt_ms', 'p95_rtt_ms', 'p99_rtt_ms', 'ul_goodput_mbps', 'jain_fairness'),
                    'bidir_2flow': ('p50_rtt_ms', 'p95_rtt_ms', 'p99_rtt_ms', 'ul_goodput_mbps', 'jain_fairness'),
                    'unidir_dl_2flow': ('p50_rtt_ms', 'p95_rtt_ms', 'p99_rtt_ms', 'dl_goodput_mbps'),
                    'unidir_ul_2flow': ('p50_rtt_ms', 'p95_rtt_ms', 'p99_rtt_ms', 'ul_goodput_mbps')}
for _name in ('bidir_8flow', 'covclass6_3km', 'covclass13_6km'):
    REQUIRED_METRICS[_name] = REQUIRED_METRICS['bidir_6flow']
OPERATOR_UNIDIRECTIONAL_REGIMES = ('unidir_dl_2flow', 'unidir_ul_2flow', 'unidir_ul_8flow_hammer')
OPERATOR_REQUIRED_METRICS = {**REQUIRED_METRICS,
    'unidir_ul_8flow_hammer': REQUIRED_METRICS['unidir_ul_2flow']}


def audit_operator_promotion(evidence, *, regime, round_id, policy_id,
                              control_policy_id, distance_meters=None, coverage_class=None):
    """Strict literal <2% and applicable paired outcomes through requested R134.

    The legacy structural gate and its retry veto retain their original
    contract. This new explicit utility reports retry cost diagnostically.
    Eligibility is offline only, never permission to change a device.
    A positive GP change cannot override a single p50 reversal such as R63.
    """
    from orchestration.autoresearch.fmx_multi_regime_dyadic_selector import evaluate_operator_policy
    result=evaluate_operator_policy(evidence,regime=regime,round_id=round_id,
        policy_id=policy_id,control_policy_id=control_policy_id,
        mode='strict_goodput_preservation',distance_meters=distance_meters,coverage_class=coverage_class)
    utility=result.get('utility',{})
    loss=utility.get('observed_total_goodput_loss_fraction')
    strict_less_than_two=loss is not None and Fraction(loss)<2
    reasons=list(result.get('reasons',[]))
    if not strict_less_than_two: reasons.append('STRICT_LITERAL_GOODPUT_DROP_NOT_BELOW_2PCT')
    out={**result,'status':'ELIGIBLE_OFFLINE_STRICT_OPERATOR_PROMOTION' if not reasons else 'BLOCKED',
         'reasons':sorted(set(reasons)),'strict_literal_goodput_drop_below_2pct':strict_less_than_two}
    if regime in OPERATOR_UNIDIRECTIONAL_REGIMES:
        inactive='ul_goodput_mbps' if regime=='unidir_dl_2flow' else 'dl_goodput_mbps'
        out['profile_contrast_scope']=dict(required_unanimous_metrics=list(OPERATOR_REQUIRED_METRICS[regime]),
            excluded_inapplicable_metrics=['jain_fairness',inactive],complete_five_outcome_qualification=False,
            description='Three latency outcomes and the source-verified active-direction GP alias; no directional Jain qualification.')
    return out


def audit_retry_preserving_promotion(evidence, *, regime, round_id, policy_id,
                                      control_policy_id, distance_meters=None, coverage_class=None):
    """Four-outcome profile with lower retry; never relabels all-five strict.

    p99 and total-GP block wins remain reported observations. Exact observed
    <2% is a budget predicate, not statistical noninferiority or actuation.
    """
    from orchestration.autoresearch.fmx_multi_regime_dyadic_selector import evaluate_operator_policy
    result=evaluate_operator_policy(evidence,regime=regime,round_id=round_id,
        policy_id=policy_id,control_policy_id=control_policy_id,
        mode='strict_goodput_AND_lower_retry',distance_meters=distance_meters,coverage_class=coverage_class)
    loss=result.get('utility',{}).get('observed_total_goodput_loss_fraction')
    strict_less_than_two=loss is not None and Fraction(loss)<2
    reasons=list(result.get('reasons',[]))
    if not strict_less_than_two:reasons.append('STRICT_LITERAL_GOODPUT_DROP_NOT_BELOW_2PCT')
    return {**result,'status':'ELIGIBLE_OFFLINE_RETRY_PRESERVING_FOUR_OUTCOME_PROFILE' if not reasons else 'BLOCKED',
        'reasons':sorted(set(reasons)),'strict_literal_goodput_drop_below_2pct':strict_less_than_two,
        'complete_five_outcome_qualification':False}


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _number(value, name, lo=0, hi=math.inf):
    if type(value) not in (int, float) or not math.isfinite(value) or not lo <= value <= hi:
        raise ValueError('Invalid '+name)
    return value


def _integer(value, name, lo=0, hi=2**53):
    if type(value) is not int or not lo <= value <= hi:
        raise ValueError('Invalid '+name)
    return value


def _json(raw):
    def constant(value):
        raise ValueError('Nonfinite JSON '+value)
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key')
            result[key] = value
        return result
    return json.loads(raw, parse_constant=constant, object_pairs_hook=pairs)


def _local(path):
    value = str(path)
    if '://' in value or value.startswith(('\\\\', '//')):
        raise ValueError('Explicit offline local paths only')
    path = Path(path).resolve()
    if str(path).startswith(('\\\\', '//')) or not path.is_file() or path.stat().st_size > 64_000_000:
        raise ValueError('Missing or unbounded local evidence')
    return path


@dataclass(frozen=True)
class BoundEvidence:
    """Immutable serialized data; every parse rechecks the externally pinned inputs."""
    payloads: tuple
    digests: tuple
    receipt_sha256: str

    def parse(self):
        pins = dict(self.digests)
        result = {}
        for name, raw in self.payloads:
            if _sha(raw) != pins[name]:
                raise ValueError('Bound evidence mutated')
            result[name] = _json(raw)
            if name == 'manifest' and isinstance(result[name], dict):
                result[name] = result[name].get('entries')
                if not isinstance(result[name], list):
                    raise ValueError('Frozen source manifest entries required')
            if name == 'manifest':
                result[name] = [_manifest_source_entry(entry) for entry in result[name]]
        return result


def _manifest_source_entry(entry):
    """Project an explicit frozen copy; keep the original pointer documentary."""
    if not isinstance(entry, dict) or not isinstance(entry.get('path'), str):
        raise ValueError('Malformed frozen source manifest')
    if 'copy' not in entry:
        return entry
    copy = entry['copy']
    if (not isinstance(copy, str) or not copy.strip() or '://' in copy
            or copy.startswith(('\\\\', '//'))):
        raise ValueError('Explicit local frozen copy path required')
    return {**entry, 'original_path': entry['path'], 'path': copy}


def load_bound_evidence(*, records_path, blocks_path, stats_path, manifest_path,
                        receipt_path, expected_receipt_sha256):
    """Verify four artifact bindings against an externally accepted receipt pin.

    Supplying an arbitrary new hash is not independent acceptance. The caller
    owns that trust decision; the gate cannot authenticate its own reviewer.
    Custom local fixtures exercise software contracts, not physical evidence.
    """
    if not isinstance(expected_receipt_sha256, str) or not re.fullmatch('[0-9a-f]{64}', expected_receipt_sha256):
        raise ValueError('Exact externally accepted receipt SHA256 required')
    raw = _local(receipt_path).read_bytes()
    if _sha(raw) != expected_receipt_sha256:
        raise ValueError('Statistics receipt pin mismatch')
    receipt_digest = _sha(raw)
    receipt = _json(raw)
    if not isinstance(receipt, dict) or not isinstance(receipt.get('bindings'), list):
        raise ValueError('Receipt artifact bindings required')
    payloads, digests = [], []
    for name, path in (('records', records_path), ('blocks', blocks_path),
                       ('stats', stats_path), ('manifest', manifest_path)):
        path = _local(path)
        matches = [b for b in receipt['bindings'] if isinstance(b, dict)
                   and isinstance(b.get('path'), str) and
                   # Compare names, not a filesystem probe of untrusted metadata.
                   (b['path'].replace('\\', '/') == path.as_posix()
                    or path.as_posix().endswith('/'+b['path'].replace('\\', '/')))]
        data = path.read_bytes()
        if len(matches) != 1 or matches[0].get('sha256') != _sha(data) or matches[0].get('bytes') != len(data):
            raise ValueError('Artifact hash/size binding mismatch: '+name)
        payloads.append((name, data)); digests.append((name, _sha(data)))
    manifest = _json(dict(payloads)['manifest'])
    if isinstance(manifest, dict):
        manifest = manifest.get('entries')
    if not isinstance(manifest, list):
        raise ValueError('Frozen source manifest required')
    base = _local(manifest_path).parent / 'inputs'
    for entry in manifest:
        # Only the explicit frozen path is read. The original source pointer is
        # documentary and never used for filesystem access.
        source = _manifest_source_entry(entry)
        value = source['path']
        if '://' in value or value.startswith(('\\\\', '//')):
            raise ValueError('Explicit offline frozen source paths only')
        path = Path(value).resolve()
        if not path.is_relative_to(base.resolve()):
            raise ValueError('Manifest entry escapes frozen inputs')
        path = _local(path)
        raw = path.read_bytes()
        if entry.get('sha256') != _sha(raw) or entry.get('bytes') != len(raw):
            raise ValueError('Frozen source hash/size mismatch')
    return BoundEvidence(tuple(payloads), tuple(digests), receipt_digest)


def _regime(row):
    # Existing loader's bulk label denotes the same specified two-flow DL mode.
    value = row.get('workload_regime')
    return 'unidir_dl_2flow' if value == 'bulk_unidirectional' else value


def _workload(regime):
    return 'bidir_6flow' if regime in COVERAGE_CONTEXTS else regime


def _in_regime(row, regime):
    if _regime(row) != _workload(regime):
        return False
    if regime in COVERAGE_CONTEXTS:
        distance, coverage = COVERAGE_CONTEXTS[regime]
        return (type(row.get('coverage_class')) is int and row['coverage_class'] == coverage
                and type(row.get('distance_meters')) is int and row['distance_meters'] == distance)
    return True


def _round_scope(round_ids):
    if round_ids is None:
        return None
    if (not isinstance(round_ids, (list, tuple)) or not round_ids
            or any(not isinstance(r, str) or not re.fullmatch(r'R[1-9][0-9]*', r) for r in round_ids)
            or len(set(round_ids)) != len(round_ids)):
        raise ValueError('Nonempty unique exact round scope required')
    return set(round_ids)


def _directional_identity(row):
    regime = _regime(row)
    if regime == 'unidir_ul_2flow':
        return row.get('dl_goodput_mbps') == 0 and row.get('ul_goodput_mbps') == row.get('goodput_mbps')
    return row.get('ul_goodput_mbps') == 0 and row.get('dl_goodput_mbps') == row.get('goodput_mbps')


def _policy(row):
    key = row.get('policy_key')
    if not isinstance(key, str):
        raise ValueError('Missing complete policy identity')
    pair = _json(key)
    if not isinstance(pair, list) or len(pair) != 2 or any(not isinstance(p, dict) for p in pair):
        raise ValueError('Both complete endpoint policies required')
    # Endpoint dataclass fields plus separately retained ACK and lower-MAC fields.
    for end, policy in zip(('ap', 'cpe'), pair):
        declared = row.get(end+'_policy')
        if not isinstance(declared, dict):
            raise ValueError('Unknown endpoint')
        typed = dict(declared)
        typed['aql_by_ac'] = tuple(tuple(v) for v in declared['aql_by_ac'])
        if policy_metadata(SimpleNamespace(**typed)) != declared:
            raise ValueError('Incomplete or extra endpoint policy fields')
        expected = dict(declared)
        expected.update({name: row.get(end+'_'+name) for name in ('ack_pps', 'tcp_ack_vi', 'ack_burst')})
        expected.update({name: row.get(name) for name in HOOKS})
        controls = row.get('new_source_controls', {})
        if not isinstance(controls, dict) or set(controls) - {'rts_threshold', 'ap_ack_clocking'}:
            raise ValueError('Unknown source-bound package control')
        if controls:
            rid = row.get('round_id')
            if not isinstance(rid, str) or not re.fullmatch(r'R(?:9[3-9]|1[0-2][0-9]|13[0-4])', rid):
                raise ValueError('New package controls require an explicit R93-R134 source')
            if 'rts_threshold' in controls:
                literal = controls['rts_threshold']
                if (not isinstance(literal, str) or (literal != 'off' and
                        (not re.fullmatch(r'[1-9][0-9]*', literal) or int(literal) > 65535))):
                    raise ValueError('Literal declared RTS threshold required')
                if declared.get('rts_threshold') != (None if literal == 'off' else int(literal)):
                    raise ValueError('RTS control and normalized endpoint policy conflict')
            if 'ap_ack_clocking' in controls and type(controls['ap_ack_clocking']) is not bool:
                raise ValueError('Explicit boolean AP ACK clocking declaration required')
            endpoint_controls = controls if end == 'ap' else {k:v for k,v in controls.items() if k == 'rts_threshold'}
            if endpoint_controls:
                expected['new_source_controls'] = endpoint_controls
        if policy != expected:
            raise ValueError('Policy identity does not match endpoint declarations')
    for name, (lo, hi) in HOOKS.items():
        value = row.get(name)
        # ANI is not declared by every recipe: unknown stays unknown. Controls
        # that define the requested package cannot be guessed as stock values.
        if value is not None:
            _integer(value, name, lo, hi)
        elif name != 'ani_enable':
            raise ValueError('Requested package control is unknown: '+name)
    return pair


def _context(row):
    peers = row.get('associated_cpes')
    if not isinstance(peers, list) or not peers or len(set(peers))!=len(peers) or any(not isinstance(p, str) or not p or p.strip()!=p for p in peers):
        raise ValueError('Recorded topology required')
    if row.get('encryption_mode') != 'psk2':
        raise ValueError('WPA2 context required')
    distance = row.get('distance_meters')
    if distance is not None: _integer(distance, 'timing distance', 0, 2**32-1)
    for end in ('ap','cpe'):
        endpoint = row.get(end+'_policy')
        if not isinstance(endpoint,dict) or endpoint.get('distance_meters')!=distance or endpoint.get('encryption_mode')!=row['encryption_mode']:
            raise ValueError('Endpoint and ranking context differ')
    return (distance, row['encryption_mode'], tuple(peers))


def _rows_for_block(blocks, row):
    return [b for b in blocks if b.get('round_id') == row.get('round_id')
            and b.get('treatment_id') == row.get('iteration')]


def _holm(family, hypothesis_id, expected_size):
    """Recheck a fixed, explicitly padded family; unknown members have p=1."""
    if not isinstance(family,dict) or family.get('declared_size') != expected_size or type(family.get('declared_size')) is not int:
        raise ValueError('Wrong multiplicity family size')
    known=family.get('known_hypotheses')
    if not isinstance(known,dict) or not known or len(known)>expected_size or hypothesis_id not in known:
        raise ValueError('Missing source hypothesis in family')
    padding=_integer(family.get('unknown_padding_count'),'family unknown count',0,expected_size)
    if len(known)+padding!=expected_size:raise ValueError('Family padding mismatch')
    values=sorted(((_number(p,'family p',0,1),key) for key,p in known.items()))
    running=0.
    for rank,(p,key) in enumerate(values):
        running=max(running,min(1.,(expected_size-rank)*p))
        if key==hypothesis_id:return running
    raise ValueError('Hypothesis not ranked')


def _matched_hl(blocks, target, control, units, metric):
    """Verify the claimed HL on the same source pairs, not another outcome."""
    def values(rows):
        entries=[b for r in rows for b in _rows_for_block(blocks,r)]
        result={}
        for b in entries:
            key=(b['round_id'],b['block_index'])
            if key in result:raise ValueError('Multiple values for one source arm/unit')
            value=b[metric] if metric in ('dl_goodput_mbps','ul_goodput_mbps') else b['observation'][metric]
            result[key]=_number(value,'paired source metric')
        return result
    t,c=values(target),values(control)
    diffs=[t[tuple(u)]-c[tuple(u)] for u in units]
    if len(diffs)>256:raise ValueError('Bounded within-link statistical scope required')
    return median([(a+b)/2 for i,a in enumerate(diffs) for b in diffs[i:]])


def _window_gates(row, blocks):
    reasons = []
    if row.get('window_kind', 'primary') != 'primary': reasons.append('NOT_PRIMARY_WINDOW')
    if row.get('block_mean_consistent') is not True: reasons.append('LITERAL_BLOCK_MEAN_NOT_CERTIFIED')
    if row.get('raw_rtts_matches_blocks') is not True: reasons.append('CHRONOLOGICAL_RTT_MEMBERSHIP_NOT_CERTIFIED')
    if row.get('restoration_verified') is not True: reasons.append('RESTORATION_NOT_REPORTED_TRUE')
    if _number(row.get('packet_loss_pct'), 'loss', 0, 100): reasons.append('OBSERVED_PACKET_LOSS')
    if _integer(row.get('station_drops'), 'station drops'): reasons.append('OBSERVED_STATION_DROP')
    p50=_number(row.get('p50_ms'),'p50')
    p95=_number(row.get('p95_ms'),'p95',p50)
    _number(row.get('p99_ms'),'p99',p95)
    _integer(row.get('mac_tx_packets'), 'MAC denominator', 1)
    _integer(row.get('mac_tx_retries'), 'MAC retries')
    rate=_number(row.get('mac_retry_rate'),'reported MAC retry fraction')
    if abs(rate-row['mac_tx_retries']/row['mac_tx_packets'])>.0000051:
        reasons.append('MAC_RETRY_FRACTION_MISMATCH')
    if row.get('bidirectional') is False and not _directional_identity(row):
        reasons.append('UNIDIRECTIONAL_METRIC_SCOPE_MISMATCH')
    provenance = row.get('certified_wds_evidence')
    if not isinstance(provenance, dict) or provenance.get('counter_interface') != 'phy0-ap0.sta1':
        reasons.append('EXACT_WDS_COUNTER_PROVENANCE_MISSING')
    elif provenance.get('mac_counters_valid') is not True or provenance.get('mac_block_sums_match_window') is not True:
        reasons.append('WDS_COUNTER_SUMS_NOT_CERTIFIED')
    failure = row.get('source_failure_metadata')
    if failure is not None:
        if (not isinstance(failure, dict) or type(failure.get('crash')) is not bool
                or failure.get('disqualified') is not None and type(failure.get('disqualified')) is not bool):
            raise ValueError('Malformed source crash metadata')
        if failure['crash'] or failure.get('disqualified') is True:
            reasons.append('SOURCE_CRASH_OR_DISQUALIFICATION')
    if row.get('coverage_class') is not None:
        coverage = _integer(row['coverage_class'], 'coverage class', 0, 31)
        expected = {6: 3000, 13: 6000}.get(coverage)
        if expected is None or row.get('distance_meters') != expected:
            reasons.append('UNSUPPORTED_COVERAGE_TIMING_CONTEXT')
        if (not isinstance(provenance, dict) or provenance.get('coverage_class') != coverage
                or provenance.get('physical_distance_verified') is not False):
            reasons.append('COVERAGE_TIMING_PROVENANCE_MISSING')
    own = _rows_for_block(blocks, row)
    if not own: return reasons+['NO_SOURCE_BLOCKS']
    flat = [v for b in own for v in b.get('rtts_ms', [])]
    if not flat or row.get('rtts_ms') != flat: reasons.append('RAW_RTT_BLOCK_ORDER_MISMATCH')
    for value in flat: _number(value, 'RTT')
    for name, getter in (
        ('goodput_mbps', lambda b: b['observation']['goodput_rx_mbps']),
        ('dl_goodput_mbps', lambda b: b['dl_goodput_mbps']),
        ('ul_goodput_mbps', lambda b: b['ul_goodput_mbps']),
        ('jain_fairness', lambda b: b['observation']['jain_fairness'])):
        reported = _number(row.get(name), name)
        values = [_number(getter(b), 'block '+name) for b in own]
        if Fraction(str(reported))*len(values) != sum((Fraction(str(v)) for v in values), Fraction(0)):
            reasons.append('LITERAL_MEAN_MISMATCH_'+name)
        if 'source_failure_metadata' in row and reported != sum(values)/len(values):
            reasons.append('LITERAL_PYTHON_FLOAT_MEAN_MISMATCH_'+name)
    seen=set()
    for b in own:
        block=_integer(b.get('block_index'), 'block ID'); step=_integer(b.get('crossover_step'), 'step ID')
        identity=(b.get('round_id'),block,step)
        if identity in seen: raise ValueError('Duplicate source block identity')
        seen.add(identity)
        sent = _integer(b.get('pings_sent'), 'attempted pings', 1)
        received = _integer(b.get('pings_rcvd'), 'received pings', 0, sent)
        if received != len(b.get('rtts_ms', [])) or received != sent:
            reasons.append('SOURCE_BLOCK_PACKET_LOSS_OR_COUNT_MISMATCH')
        observation=b['observation']
        if 'station_drops' in observation and _integer(observation['station_drops'],'block station drops'):
            reasons.append('SOURCE_BLOCK_STATION_DROP')
        if 'restoration_verified' in observation:
            if type(observation['restoration_verified']) is not bool:
                raise ValueError('Block restoration must be boolean')
            if not observation['restoration_verified']:
                reasons.append('SOURCE_BLOCK_RESTORATION_FAILED')
        _integer(b.get('mac_tx_packets_delta'), 'block MAC packets', 1)
        _integer(b.get('mac_tx_retries_delta'), 'block MAC retries')
        if b.get('counter_interface') != 'phy0-ap0.sta1':
            reasons.append('BLOCK_WDS_COUNTER_INTERFACE_UNKNOWN')
    if sum(b['mac_tx_packets_delta'] for b in own) != row['mac_tx_packets'] or sum(b['mac_tx_retries_delta'] for b in own) != row['mac_tx_retries']:
        reasons.append('MAC_BLOCK_SUMS_MISMATCH')
    return reasons


def evaluate_promotion(evidence, *, policy_id, regime, requested_wmm=None, round_ids=None):
    """All gates are conjunctive; never transfer a p-value between regimes."""
    result = dict(status='BLOCKED', policy_id=policy_id, regime=regime, reasons=[],
                  automatic_execution_allowed=False, physical_safety_qualified=False,
                  independent_physical_acceptance=False, scope='OFFLINE_OBSERVED_PACKAGE_CANARY_ELIGIBILITY_ONLY')
    if regime not in REGIMES:
        return {**result, 'reasons':['UNSUPPORTED_REGIME']}
    try:
        if requested_wmm is not None and (not isinstance(requested_wmm,dict) or set(requested_wmm)!= {'AP','CPE'} or not all(isinstance(v,dict) and v for v in requested_wmm.values())):
            raise ValueError('Explicit nonempty AP/CPE WMM control values required')
        scope = _round_scope(round_ids)
        result['requested_round_ids'] = sorted(scope) if scope is not None else None
        result['eligibility_limits'] = ['within_link_repetitions_not_independent_sector_trials',
            'programmed_coverage_timing_not_verified_physical_range', 'NO_AUTOMATIC_EXECUTION_OR_PRODUCTION_ACCEPTANCE']
        data = evidence.parse()
        records, blocks = data['records']['records'], data['blocks']['crossed']
        matching = [r for r in records if r.get('policy_key') == policy_id and _in_regime(r, regime)]
        certified = [r for r in matching if 'block_mean_consistent' in r]
        own = [r for r in certified if scope is None or r.get('round_id') in scope]
        if scope is not None and {r.get('round_id') for r in own} != scope:
            return {**result, 'reasons':['REQUESTED_ROUND_SCOPE_NOT_OBSERVED_FOR_EXACT_PACKAGE']}
        result['older_source_certifications_outside_requested_scope'] = [
            dict(round_id=r.get('round_id'),iteration=r.get('iteration'),
                 block_mean_consistent=r.get('block_mean_consistent'))
            for r in certified if scope is not None and r.get('round_id') not in scope]
        if not own: return {**result, 'reasons':['NO_EXACT_OBSERVED_PACKAGE_IN_REGIME']}
        contexts = {_context(r) for r in own}
        if len(contexts) != 1: result['reasons'].append('AMBIGUOUS_RANK_CONTEXT')
        historical = [r for r in matching if 'block_mean_consistent' not in r]
        result['prior_uncertified_observations_not_used_for_certification'] = [
            dict(round_id=r.get('round_id'),iteration=r.get('iteration')) for r in historical]
        # True negative outcomes quarantine the same whole policy/context,
        # regardless of whether an older acquisition had certification fields.
        for row in matching:
            if _context(row) not in contexts: continue
            loss=row.get('packet_loss_pct');drops=row.get('station_drops')
            if ((loss is not None and _number(loss,'prior loss',0,100)>0)
                    or (drops is not None and _integer(drops,'prior station drops')>0)
                    or row.get('restoration_verified') is False
                    or isinstance(row.get('source_failure_metadata'),dict) and
                    (row['source_failure_metadata'].get('crash') is True or row['source_failure_metadata'].get('disqualified') is True)):
                result['reasons'].append('KNOWN_NEGATIVE_WHOLE_PACKAGE_IN_CONTEXT')
        for row in own:
            _policy(row)
            if (row.get('active_flow_count'), row.get('bidirectional')) != REGIMES[regime] or type(row.get('active_flow_count')) is not int or type(row.get('bidirectional')) is not bool:
                result['reasons'].append('REGIME_METADATA_MISMATCH')
            result['reasons'].extend(_window_gates(row, blocks))
            provenance = row.get('certified_wds_evidence', {})
            for name in ('source_receipt', 'source_recipe'):
                ref = provenance.get(name)
                if not isinstance(ref, dict) or not any(
                        all(ref.get(k)==entry.get(k) for k in ('path','bytes','sha256')) for entry in data['manifest']):
                    result['reasons'].append('FROZEN_'+name.upper()+'_PROVENANCE_MISSING')
            if requested_wmm is not None:
                recorded = row['certified_wds_evidence'].get('wmm_edca_values')
                if recorded != requested_wmm or recorded is None:
                    result['reasons'].append('REQUESTED_WMM_CONTROLS_NOT_RECORDED')
        projection = data['stats'].get('promotion_evidence')
        if not isinstance(projection, dict):
            result['reasons'].append('STATISTICAL_PROMOTION_EVIDENCE_MISSING')
        else:
            pins = dict(evidence.digests)
            if projection.get('source_inputs') != {k+'_sha256':pins[k] for k in ('records','blocks','manifest')}:
                result['reasons'].append('STATISTICAL_SOURCE_SCOPE_MISMATCH')
            contrasts = projection.get('contrasts', [])
            result['statistical_support']=[]
            for metric in REQUIRED_METRICS[regime]:
                eligible = [c for c in contrasts if c.get('regime') == _workload(regime) and c.get('target_policy_id') == policy_id and
                            (c.get('metric') == metric or (regime in ('unidir_dl_2flow','unidir_ul_2flow') and metric in ('dl_goodput_mbps','ul_goodput_mbps') and c.get('metric')=='goodput_rx_mbps'))]
                accepted = False
                for c in eligible:
                    rounds = c.get('round_ids')
                    units = c.get('paired_unit_ids')
                    if not isinstance(rounds,list) or not rounds or not isinstance(units,list) or not units:
                        continue
                    if len(set(rounds))!=len(rounds) or any(not isinstance(r,str) for r in rounds):
                        continue
                    for unit in units:
                        if not isinstance(unit,dict) or set(unit)!={'round_id','block_index'} or not isinstance(unit['round_id'],str):
                            raise ValueError('Invalid statistical paired unit')
                        _integer(unit['block_index'],'statistical paired block ID')
                    if scope is not None and set(rounds) != scope:
                        continue
                    target = [r for r in own if r['round_id'] in rounds]
                    control = [r for r in records if r.get('policy_key') == c.get('control_policy_id') and r.get('round_id') in rounds and _in_regime(r,regime)]
                    if not target or not control or {_context(r) for r in target+control} != contexts:
                        continue
                    if any((r.get('active_flow_count'),r.get('bidirectional'))!=REGIMES[regime] or type(r.get('active_flow_count')) is not int or type(r.get('bidirectional')) is not bool for r in control):
                        continue
                    if set(rounds)!={r['round_id'] for r in target} or set(rounds)!={r['round_id'] for r in control}:
                        continue
                    t = {(b['round_id'],b['block_index']) for r in target for b in _rows_for_block(blocks,r)}
                    ctrl = {(b['round_id'],b['block_index']) for r in control for b in _rows_for_block(blocks,r)}
                    if t!=ctrl:continue
                    source_units = sorted([list(x) for x in t & ctrl])
                    normalized_units=[[u['round_id'],u['block_index']] for u in units]
                    if sorted(normalized_units) != source_units or len({tuple(x) for x in normalized_units}) != len(units):
                        continue
                    p = _number(c.get('p_exact_rank'), 'exact p', 0, 1)
                    h324 = _number(c.get('holm324_adjusted_p'), 'Holm324', 0, 1)
                    h500 = _number(c.get('holm500_adjusted_p'), 'Holm500', 0, 1)
                    hypothesis=c.get('source_hypothesis_id')
                    families=projection.get('families',{})
                    f324=families.get(c.get('family324_key'))
                    f500=families.get(c.get('family500_key'))
                    check324=_holm(f324,hypothesis,324);check500=_holm(f500,hypothesis,500)
                    if f324['known_hypotheses'][hypothesis]!=p or f500['known_hypotheses'][hypothesis]!=p or abs(check324-h324)>1e-12 or abs(check500-h500)>1e-12:
                        continue
                    effect = _number(c.get('effect_hl'), 'effect', -math.inf)
                    algebraic_alias=c.get('metric')!=metric
                    if algebraic_alias:
                        # One already-computed GP test is a DL test only under
                        # this exact algebraic identity, not a new hypothesis.
                        bs=[b for r in target+control for b in _rows_for_block(blocks,r)]
                        other = 'dl_goodput_mbps' if regime=='unidir_ul_2flow' else 'ul_goodput_mbps'
                        if any(not _directional_identity(r) for r in target+control) or any(b.get(other)!=0 or b.get(metric)!=b['observation']['goodput_rx_mbps'] for b in bs):
                            continue
                    source_hl=_matched_hl(blocks,target,control,normalized_units,metric)
                    if abs(source_hl-effect)>max(1e-10,abs(source_hl)*1e-12):
                        continue
                    sign = -1 if metric in ('p50_rtt_ms','p95_rtt_ms','p99_rtt_ms') else 1
                    # Even an externally bound receipt must not claim an
                    # impossible two-sided exact floor for a four-pair arm.
                    comparable = (c.get('comparability_status') == 'COMPARABLE' or
                                  (len(rounds)==1 and c.get('comparability_status')=='WITHIN_ROUND_DECLARED_PACKAGE_COMPARISON'))
                    if (comparable and c.get('direction') == ('lower' if sign<0 else 'higher')
                            and effect*sign>0 and p>=2.0**(1-len(units)) and h324>=p and h500>=p
                            and h324<=.05 and h500<=.05):
                        accepted=True
                        result['statistical_support'].append(dict(required_metric=metric,source_metric=c['metric'],
                            source_hypothesis_id=hypothesis,round_ids=rounds,paired_count=len(units),
                            DL_equals_total_GP_verified=algebraic_alias and regime=='unidir_dl_2flow',
                            UL_equals_total_GP_verified=algebraic_alias and regime=='unidir_ul_2flow',holm324_adjusted_p=h324,holm500_adjusted_p=h500))
                if not accepted: result['reasons'].append('NO_DIRECT_HOLM324_500_SUPPORT_'+metric)
        result['reasons'] = sorted(set(result['reasons']))
        result['source_receipt_sha256'] = evidence.receipt_sha256
        result['observed_windows'] = [dict(round_id=r['round_id'],iteration=r['iteration']) for r in own]
        result['source_campaign_checks'] = [dict(round_id=r['round_id'],iteration=r['iteration'],
            literal_fraction_consistent=r.get('block_mean_consistent'),
            Python_float_consistent=r.get('certified_wds_evidence',{}).get('block_mean_float_consistent'),
            NumPy_mean_consistent_report_only=r.get('certified_wds_evidence',{}).get('block_mean_numpy_consistent'),
            NumPy_quantiles_exact_audited_report_only=r.get('certified_wds_evidence',{}).get('exact_numpy_quantiles'),
            coverage_class=r.get('coverage_class'),programmed_timing_meters=r.get('distance_meters'),
            physical_distance_verified=False,source_failure_metadata=r.get('source_failure_metadata'))
            for r in own if 'source_failure_metadata' in r]
        if not result['reasons']: result['status']='PROMOTED_CERTIFIED_CANARY'
        return result
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError, IndexError) as error:
        return {**result, 'status':'BLOCKED', 'reasons':sorted(set(result['reasons']+['MALFORMED_OR_UNBOUND_EVIDENCE'])),
                'error_type':type(error).__name__}


def audit_available_hmac_promotion(*, round_id, **source_options):
    """Expose the saved hMAC/VoIP boundary without changing any legacy gate."""
    from orchestration.autoresearch.fmx_multi_regime_dyadic_selector import audit_available_hmac_packages
    if type(round_id) is not str or not re.fullmatch(r'R(?:13[5-9]|14[0-6])',round_id):
        raise ValueError('Explicit requested R135-R146 identity required')
    report=audit_available_hmac_packages(**source_options)
    own=[row for row in report['packages'] if row['round_id']==round_id]
    return dict(status='BLOCKED',round_id=round_id,regime='bidir_8flow_voip_hmac',
        package=own[0] if len(own)==1 else None,
        reasons=own[0]['reasons'] if len(own)==1 else report.get('reasons',['REQUESTED_HMAC_RECEIPT_NOT_AVAILABLE_AT_CUTOFF']),
        independently_accepted_same_regime_statistics=False,
        historical_gate_contracts_changed=False,automatic_execution_allowed=False,physical_acceptance=False)
