"""Pure offline finite-pool regime selector. No actuator or physical optimum.

Rows follow the RegimeMeasurement/EndpointPolicy loader contract; importing this
module neither loads artifacts nor imports a bench, surrogate or device helper.
"""

from collections import defaultdict
from copy import deepcopy
import json
import math


POLICY_FIELDS = (
    "aql_by_ac", "aql_threshold_us", "fq_quantum_bytes", "rc_per_thresh",
    "rts_threshold", "ct_baseband_rifs", "ct_pshack", "htt_max_amsdu",
    "htt_max_ampdu", "dscp_micro_vo_steering",
)
CROSS_LAYER_FIELDS = (
    "fq_target_us", "fq_interval_us", "tcp_limit_output_bytes",
    "tcp_notsent_lowat", "distance_meters", "encryption_mode",
)
ACK_FIELDS = ("ack_pps", "tcp_ack_vi", "ack_burst")
# Representable parser domains only. Selection never fabricates a policy at a
# boundary or treats an encoding limit as a physically safe hardware range.
LOWER_MAC_DOMAINS = {
    "short_retry_limit": (0, 255), "long_retry_limit": (0, 255),
    "force_tx_status": (0, 1), "ani_enable": (0, 1),
    "airtime_flags": (0, 3), "fq_limit": (1, 2**32-1),
}
_UNSPECIFIED = object()
LIMITS = (
    "OFFLINE_ONLY: no actuation or physically qualified policy",
    "Reported restoration is not independently verified restoration",
    "Observed sequential single-link outcomes are not causal predictions",
    "Queue/RC/ratio costs are ASSUMED_POLICY_COST, not learned effects",
    "EF46 to VO mapping is UNKNOWN; DSCP output is numeric metadata only",
    "Timing-distance is a programmed coverage setting, not physical range",
    "CoDel/TSQ and BE scaling select observed packages; no interpolation or causal gain",
    "Declared/inferred cipher and topology are not effective per-window readbacks",
)


def _number(value, name, low=0, high=None):
    try:
        valid = type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        valid = False
    if not valid or value < low or (high is not None and value > high):
        raise ValueError(f"Invalid {name}")
    return value


def _integer(value, name, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"Invalid {name}")
    return value


def policy_metadata(policy):
    """Validate representable input domains, never a physical safe RAM range."""
    if policy is None:
        return None
    result = {name: getattr(policy, name) for name in POLICY_FIELDS}
    acs = result["aql_by_ac"]
    if not isinstance(acs, tuple) or len(acs) != 4:
        raise ValueError("AQL requires VO/VI/BE/BK tuples")
    for pair in acs:
        if not isinstance(pair, tuple) or len(pair) != 2:
            raise ValueError("AQL requires low/high pairs")
        lo = _integer(pair[0], "AQL low", 1, 1_000_000)
        _integer(pair[1], "AQL high", lo, 1_000_000)
    for name, low, high in (
        ("aql_threshold_us", 1, 2_000_000), ("fq_quantum_bytes", 1, 65536),
        ("rc_per_thresh", 0, 256), ("ct_baseband_rifs", 0, 1),
        ("ct_pshack", 0, 255), ("htt_max_amsdu", 1, 31),
        ("htt_max_ampdu", 1, 64),
    ):
        if result[name] is None and name in {
            "ct_baseband_rifs", "ct_pshack", "htt_max_amsdu", "htt_max_ampdu"
        }:
            continue
        _integer(result[name], name, low, high)
    if result["rts_threshold"] is not None:
        _integer(result["rts_threshold"], "RTS threshold", 0, 65535)
    if type(result["dscp_micro_vo_steering"]) is not bool:
        raise ValueError("DSCP steering must be boolean")
    result["aql_by_ac"] = [list(pair) for pair in acs]
    # Preserve the legacy endpoint schema; the new loader explicitly supplies
    # these fields, including None for unrecorded cross-layer coordinates.
    if any(hasattr(policy, name) for name in CROSS_LAYER_FIELDS):
        result.update({name: getattr(policy, name, None) for name in CROSS_LAYER_FIELDS})
        for name in CROSS_LAYER_FIELDS[:-1]:
            if result[name] is not None:
                _integer(result[name], name, 0 if name in {
                    "distance_meters", "tcp_notsent_lowat"
                } else 1, 2**32-1)
        if (result["fq_target_us"] is not None and result["fq_interval_us"] is not None
                and result["fq_target_us"] > result["fq_interval_us"]):
            raise ValueError("CoDel target exceeds interval")
        if result["encryption_mode"] not in (None, "psk2", "none"):
            raise ValueError("Unsupported encryption mode")
    return result


def _topology(value):
    if value is None:
        return None
    if (not isinstance(value, tuple) or not value or any(
            not isinstance(x, str) or not x or x.strip() != x for x in value)
            or len(set(value)) != len(value)):
        raise ValueError("Invalid associated CPE identities")
    return tuple(sorted(value))


def _context(row, ap, cpe):
    distance = getattr(row, "distance_meters", None)
    if distance is not None:
        _integer(distance, "timing-distance meters", 0, 2**32-1)
    encryption = getattr(row, "encryption_mode", None)
    if encryption not in (None, "psk2", "none"):
        raise ValueError("Unsupported recorded encryption mode")
    for p in (ap, cpe):
        if p is not None:
            for name, value in (("distance_meters", distance), ("encryption_mode", encryption)):
                if p.get(name) != value:
                    raise ValueError("Endpoint and window context disagree")
    return distance, encryption, _topology(getattr(row, "associated_cpes", None))


def _context_metadata(context):
    distance, encryption, topology = context
    return dict(distance_meters=distance, encryption_mode=encryption,
                associated_cpes=list(topology) if topology else None,
                distance_kind="PROGRAMMED_COVERAGE_TIMING_NOT_PHYSICAL_RANGE")


def _evidence(row):
    return dict(round_id=row.round_id, iteration=row.iteration,
                window_kind=getattr(row, "window_kind", "primary"),
                source_position=getattr(row, "source_position", None),
                encryption_evidence=getattr(row, "encryption_evidence", "UNKNOWN"),
                topology_evidence=getattr(row, "topology_evidence", "UNKNOWN"))


def _policy_id(ap, cpe):
    return json.dumps([ap, cpe], sort_keys=True, separators=(",", ":"), allow_nan=False)


def _dscp_metadata(ap, cpe):
    return {
        "rules": [dict(endpoint=name, enabled=p["dscp_micro_vo_steering"],
                       protocols=["UDP", "ICMP"], packet_length_lt_bytes=256,
                       dscp=46) for name, p in (("AP", ap), ("CPE", cpe)) if p is not None],
        "ef_to_vo_mapping": "UNKNOWN", "executable": False,
    }


class AdaptiveAQLRegimeController:
    """Rank complete observed AP/CPE policy pairs within one measured regime.

    score = G/100 - p95/20 - .25*p99/20 - .25*directional_mismatch
            - (.05 + .5*retry)*directional_BE_high/12000
            - .25*retry*directional_raw_RC/256 - .01*directional_FQ/1514.

    Constants define a transparent heuristic objective, not fitted coefficients.
    Repeated windows are averaged within round first, then equally across rounds.
    Policy coordinates are never synthesized or mixed across endpoint pairs.
    """

    def __init__(self, records, *, min_switch_gain=0.05, allow_asymmetric=True,
                 include_three_tier=False, include_lower_mac=False):
        # Earlier R5-R7 already contained asymmetric policies. True preserves
        # their behavior; False explicitly filters known unequal endpoint pairs.
        if type(allow_asymmetric) is not bool:
            raise ValueError("allow_asymmetric must be boolean")
        if type(include_three_tier) is not bool:
            raise ValueError("include_three_tier must be boolean")
        if type(include_lower_mac) is not bool:
            raise ValueError("include_lower_mac must be boolean")
        include_three_tier = include_three_tier or include_lower_mac
        self.allow_asymmetric = allow_asymmetric
        self.include_three_tier = include_three_tier
        self.include_lower_mac = include_lower_mac
        self.min_switch_gain = _number(min_switch_gain, "hysteresis margin", 0, 10)
        self._groups = defaultdict(list)
        self.excluded = []
        self._unusable_three_tier_evidence = []
        negatives = defaultdict(list)
        eligible = defaultdict(list)
        seen = set()
        for row in records:
            identity = (row.round_id, row.iteration, getattr(row, "window_kind", "primary"))
            if identity in seen:
                raise ValueError("Duplicate measurement identity")
            seen.add(identity)
            try:
                if not include_lower_mac and any(hasattr(row, name) for name in LOWER_MAC_DOMAINS):
                    self.excluded.append(dict(round_id=row.round_id, iteration=row.iteration,
                                              reason="LOWER_MAC_OPT_IN_REQUIRED"))
                    continue
                if not include_three_tier and any(hasattr(row, end+"_"+name)
                        for end in ("ap", "cpe") for name in ACK_FIELDS):
                    self.excluded.append(dict(round_id=row.round_id, iteration=row.iteration,
                                              reason="THREE_TIER_OPT_IN_REQUIRED"))
                    continue
                reason = self._admit(row)
                if include_three_tier:
                    consistency = getattr(row, "summary_consistency", None)
                    flag = "reported_summary_disagrees_with_repetition_blocks" in getattr(row, "flags", ())
                    source_reason = None
                    if include_lower_mac and any(hasattr(row, name) for name in LOWER_MAC_DOMAINS) and consistency is None:
                        source_reason = "MISSING_LOWER_MAC_SUMMARY_CONSISTENCY"
                    elif consistency is not None and (not isinstance(consistency, dict)
                            or type(consistency.get("consistent")) is not bool):
                        source_reason = "MALFORMED_SUMMARY_CONSISTENCY"
                    elif flag or (consistency is not None and not consistency["consistent"]):
                        source_reason = "REPORTED_SUMMARY_DISAGREES_WITH_REPETITION_BLOCKS"
                    if source_reason:
                        ap, cpe = self._row_policies(row)
                        self._unusable_three_tier_evidence.append(dict(
                            **self._row_evidence(row), reason=source_reason,
                            ack_controls={end: {name: p.get(name) for name in ACK_FIELDS} if p else None
                                          for end, p in (("AP", ap), ("CPE", cpe))},
                            summary_consistency=deepcopy(consistency),
                            handling="PRESERVED_UNPROMOTED_NOT_WIRELESS_FAILURE_OR_REPAIRED_SCORE"))
                        # Real loss/drop/restoration negatives remain negatives
                        # even when measurement summaries also contradict blocks.
                        reason = reason or source_reason
                if reason:
                    self.excluded.append(dict(round_id=row.round_id, iteration=row.iteration, reason=reason))
                    if reason in {"OBSERVED_PACKET_LOSS", "RESTORATION_NOT_REPORTED_TRUE", "OBSERVED_STATION_DROP"}:
                        ap, cpe = self._row_policies(row)
                        if ap is None:
                            raise ValueError("Negative AP policy missing")
                        key = (row.workload_regime, _policy_id(ap, cpe), _context(row, ap, cpe))
                        negatives[key].append({**self._row_evidence(row), "reasons": self._quality_reasons(row)})
                    continue
                ap, cpe = self._row_policies(row)
                if ap is None:
                    raise ValueError("AP policy missing")
                key = (row.workload_regime, _policy_id(ap, cpe), _context(row, ap, cpe))
                eligible[key].append((row, ap, cpe))
            except (AttributeError, TypeError, ValueError, OverflowError):
                self.excluded.append(dict(round_id=row.round_id, iteration=row.iteration,
                                          reason="MALFORMED_OR_INCOMPLETE_MEASUREMENT"))
        # Admission happens only AFTER collecting all negative observations,
        # independent of receipt order or which duplicate happened to pass.
        self._excluded_policy_evidence = []
        for (regime, key, context), failed in sorted(negatives.items(), key=lambda x: repr(x[0])):
            failed = sorted(failed, key=lambda r: (r["round_id"], r["iteration"]))
            duplicates = eligible.get((regime, key, context), [])
            self._excluded_policy_evidence.append(dict(workload_regime=regime, policy_id=key,
                context=_context_metadata(context),
                negative_windows=failed,
                quarantined_windows=[self._row_evidence(r)
                                     for r, _, _ in sorted(duplicates, key=lambda x: (x[0].round_id, x[0].iteration))]))
            for row, _, _ in duplicates:
                self.excluded.append(dict(round_id=row.round_id, iteration=row.iteration,
                    reason="KNOWN_FAILED_JOINT_POLICY_IN_SAME_REGIME", negative_windows=failed))
        for key, samples in eligible.items():
            if key not in negatives:
                self._groups[key] = samples

    def _row_policies(self, row):
        ap, cpe = policy_metadata(row.ap_policy), policy_metadata(row.cpe_policy)
        if self.include_three_tier:
            for prefix, policy in (("ap", ap), ("cpe", cpe)):
                values = {name: getattr(row, prefix+"_"+name, None) for name in ACK_FIELDS}
                for name, value in values.items():
                    if value is not None:
                        if name == "tcp_ack_vi":
                            if type(value) is not bool:raise ValueError("ACK-to-VI must be boolean or unknown")
                        else:_integer(value, prefix+"_"+name, 0, 2**32-1)
                if policy is None:
                    if any(v is not None for v in values.values()):
                        raise ValueError("ACK controls require a recorded endpoint package")
                else:
                    # In this opt-in schema legacy absent fields remain UNKNOWN.
                    # Canonical None coordinates keep a legacy negative from
                    # re-entering as a new positive with unrecorded ACK fields.
                    policy.update(values)
        if self.include_lower_mac:
            values = {name: getattr(row, name, None) for name in LOWER_MAC_DOMAINS}
            for name, value in values.items():
                if value is not None:
                    _integer(value, name, *LOWER_MAC_DOMAINS[name])
            for policy in (ap, cpe):
                if policy is None:
                    if any(value is not None for value in values.values()):
                        raise ValueError("Lower MAC controls require both recorded endpoint packages")
                else:
                    # The shared declaration applies to both endpoints. None
                    # canonicalizes old unknown fields, including negatives.
                    policy.update(values)
        return ap, cpe

    def _row_evidence(self, row):
        evidence = _evidence(row)
        if self.include_three_tier:
            evidence.update(source_policy_id=getattr(row, "policy_key", None),
                ack_control_evidence=getattr(row, "ack_control_evidence", "UNKNOWN"),
                cpu_telemetry_available=getattr(row, "cpu_telemetry", None) is not None,
                cpu_telemetry_used_for_score=False)
        if self.include_lower_mac:
            evidence.update(lower_mac_evidence=getattr(row, "lower_mac_evidence", "UNKNOWN"),
                            lower_mac_controls={name: getattr(row, name, None) for name in LOWER_MAC_DOMAINS})
        return evidence

    @staticmethod
    def _quality_reasons(row):
        reasons = []
        if _number(row.packet_loss_pct, "loss percent", 0, 100) > 0:
            reasons.append("OBSERVED_PACKET_LOSS")
        if row.restoration_verified is not True:
            reasons.append("RESTORATION_NOT_REPORTED_TRUE")
        if _integer(row.station_drops, "station drops", 0, 1_000_000) != 0:
            reasons.append("OBSERVED_STATION_DROP")
        return reasons

    @staticmethod
    def _admit(row):
        if getattr(row, "window_kind", "primary") != "primary":
            return "SUMMARY_OR_UNSUPPORTED_WINDOW_NOT_POLICY_EVIDENCE"
        reasons = AdaptiveAQLRegimeController._quality_reasons(row)
        if reasons:
            return reasons[0]
        expected = {"bulk_unidirectional": (2, False), "bidir_2flow": (2, True),
                    "bidir_6flow": (6, True)}
        if (row.workload_regime not in expected or type(row.active_flow_count) is not int
                or type(row.bidirectional) is not bool
                or (row.active_flow_count, row.bidirectional) != expected[row.workload_regime]):
            return "UNSUPPORTED_RECORDED_REGIME"
        _number(row.goodput_mbps, "goodput", 0, 10000)
        p50 = _number(row.p50_ms, "p50", 0, 1_000_000)
        p95 = _number(row.p95_ms, "p95", p50, 1_000_000)
        _number(row.p99_ms, "p99", p95, 1_000_000)
        if row.bidirectional:
            _number(row.dl_goodput_mbps, "DL goodput", 0.000001, 10000)
            _number(row.ul_goodput_mbps, "UL goodput", 0.000001, 10000)
            if row.cpe_policy is None:
                return "BIDIRECTIONAL_CPE_POLICY_UNKNOWN"
        return None

    @staticmethod
    def _mean_by_round(samples):
        rounds = defaultdict(list)
        for round_id, value in samples:
            rounds[round_id].append(value)
        return math.fsum(math.fsum(v)/len(v) for v in rounds.values())/len(rounds)

    def select(self, active_flow_count, ul_dl_ratio, mac_retry_fraction, *, previous=None,
               distance_meters=_UNSPECIFIED, encryption_mode=_UNSPECIFIED,
               associated_cpes=_UNSPECIFIED, fq_target_us=_UNSPECIFIED,
               fq_interval_us=_UNSPECIFIED, tcp_limit_output_bytes=_UNSPECIFIED,
               tcp_notsent_lowat=_UNSPECIFIED, allow_asymmetric=None,
               ap_ack_pps=_UNSPECIFIED, cpe_ack_pps=_UNSPECIFIED,
               ap_tcp_ack_vi=_UNSPECIFIED, cpe_tcp_ack_vi=_UNSPECIFIED,
               short_retry_limit=_UNSPECIFIED, long_retry_limit=_UNSPECIFIED,
               force_tx_status=_UNSPECIFIED, ani_enable=_UNSPECIFIED,
               airtime_flags=_UNSPECIFIED, fq_limit=_UNSPECIFIED):
        """Return metadata only. UL/DL is a ratio; retry input is bounded [0,1].

        Retry events/tx-packets is not MAC PER and may exceed one in other
        telemetry contracts; such values must not be silently clipped here.
        Omitted context fields are unconstrained, explicit None matches only
        recorded unknown, and supplied values require exact equality. Multiple
        remaining contexts cause abstention; they are never averaged together.
        CoDel/TSQ constraints follow the same omitted/unknown/exact contract and
        must match AP and every recorded CPE endpoint before any ranking.
        allow_asymmetric=None inherits the constructor's compatible True
        default. False removes known unequal AP/CPE packages before support,
        ranking and hysteresis; AP-only bulk remains explicitly CPE-unknown.
        ACK constraints require include_three_tier=True. Missing ACK data stays
        None; observed zero/False are distinct. No controls are synthesized.
        Lower MAC constraints require include_lower_mac=True (which includes
        the ACK schema). Each exact integer/None constraint matches both
        recorded endpoints before ranking. Encoding domains are not safe ranges.
        """
        _integer(active_flow_count, "active flow count", 0, 1_000_000)
        ratio = _number(ul_dl_ratio, "UL/DL ratio")
        retry = _number(mac_retry_fraction, "MAC retry input", 0, 1)
        if allow_asymmetric is not None and type(allow_asymmetric) is not bool:
            raise ValueError("allow_asymmetric must be boolean or None")
        allow_asymmetric = self.allow_asymmetric if allow_asymmetric is None else allow_asymmetric
        constraints = tuple(value is not _UNSPECIFIED for value in
                            (distance_meters, encryption_mode, associated_cpes))
        distance_meters = None if distance_meters is _UNSPECIFIED else distance_meters
        encryption_mode = None if encryption_mode is _UNSPECIFIED else encryption_mode
        associated_cpes = None if associated_cpes is _UNSPECIFIED else associated_cpes
        if distance_meters is not None:
            _integer(distance_meters, "timing-distance meters", 0, 2**32-1)
        if encryption_mode not in (None, "psk2", "none"):
            raise ValueError("Unsupported encryption context")
        topology = _topology(associated_cpes)
        knob_constraints = {}
        for name, value in (("fq_target_us", fq_target_us), ("fq_interval_us", fq_interval_us),
                            ("tcp_limit_output_bytes", tcp_limit_output_bytes),
                            ("tcp_notsent_lowat", tcp_notsent_lowat)):
            specified = value is not _UNSPECIFIED
            if specified and value is not None:
                _integer(value, name, 0 if name == "tcp_notsent_lowat" else 1, 2**32-1)
            knob_constraints[name] = dict(specified=specified, value=value if specified else None,
                                          scope="AP_AND_EVERY_RECORDED_CPE")
        ack_constraints = {}
        for endpoint, name, value in (("AP", "ack_pps", ap_ack_pps), ("CPE", "ack_pps", cpe_ack_pps),
                                      ("AP", "tcp_ack_vi", ap_tcp_ack_vi), ("CPE", "tcp_ack_vi", cpe_tcp_ack_vi)):
            specified = value is not _UNSPECIFIED
            if specified and not self.include_three_tier:
                raise ValueError("ACK constraints require include_three_tier=True")
            if specified and value is not None:
                if name == "tcp_ack_vi":
                    if type(value) is not bool:raise ValueError("ACK-to-VI constraint must be boolean or unknown")
                else:_integer(value, endpoint+" ACK pps", 0, 2**32-1)
            ack_constraints[endpoint.lower()+"_"+name] = dict(endpoint=endpoint, field=name,
                specified=specified, value=value if specified else None)
        lower_mac_constraints = {}
        for name, value in (("short_retry_limit", short_retry_limit), ("long_retry_limit", long_retry_limit),
                            ("force_tx_status", force_tx_status), ("ani_enable", ani_enable),
                            ("airtime_flags", airtime_flags), ("fq_limit", fq_limit)):
            specified = value is not _UNSPECIFIED
            if specified and not self.include_lower_mac:
                raise ValueError("Lower MAC constraints require include_lower_mac=True")
            if specified and value is not None:
                _integer(value, name, *LOWER_MAC_DOMAINS[name])
            lower_mac_constraints[name] = dict(specified=specified, value=value if specified else None,
                                               scope="AP_AND_EVERY_RECORDED_CPE")
        result = dict(status="ABSTAIN", automatic_execution_allowed=False,
                      physical_safety_qualified=False, ap_policy=None, cpe_policy=None,
                      policy_id=None, score=None, dscp_metadata=None,
                      objective="FINITE_OBSERVED_POOL_HEURISTIC", cost_kind="ASSUMED_POLICY_COST",
                      retry_units="retry_events_per_tx_packet_bounded_input_not_PER",
                      excluded_policy_evidence=[],
                      inputs=dict(active_flow_count=active_flow_count, ul_dl_ratio=ratio,
                                  mac_retry_fraction=retry, distance_meters=distance_meters,
                                  encryption_mode=encryption_mode, associated_cpes=list(topology) if topology else None,
                                  allow_asymmetric=allow_asymmetric),
                      context_constraints=dict(zip(("distance_meters", "encryption_mode", "associated_cpes"), constraints)),
                      policy_constraints=knob_constraints,
                      limits=list(LIMITS), candidates=[])
        if self.include_three_tier:
            result.update(three_tier_policy_schema=True, ack_constraints=ack_constraints,
                          unusable_three_tier_evidence=deepcopy(self._unusable_three_tier_evidence),
                          ack_policy_limits=["Declared/recorded ACK policy is not effective pacing or WMM mapping proof",
                                             "No new ACK/VI/burst score coefficients or automatic enrollment"])
        if self.include_lower_mac:
            result.update(lower_mac_policy_schema=True, lower_mac_constraints=lower_mac_constraints,
                          lower_mac_policy_limits=["Shared declared fields are metadata, not verified firmware behavior",
                                                   "Parser encoding bounds are not physically safe RAM ranges",
                                                   "No new Lower MAC score coefficients or automatic enrollment"])
        if active_flow_count == 0:
            return {**result, "status": "IDLE", "reason": "NO_ACTIVE_FLOWS"}
        regime = ("bulk_unidirectional" if active_flow_count == 2 and ratio == 0 else
                  "bidir_2flow" if active_flow_count == 2 else
                  "bidir_6flow" if active_flow_count == 6 and ratio > 0 else None)
        result["workload_regime"] = regime
        result["excluded_policy_evidence"] = deepcopy(
            [e for e in self._excluded_policy_evidence if e["workload_regime"] == regime])
        pool = [(key, rows) for key, rows in self._groups.items() if key[0] == regime]
        pool = [(key, rows) for key, rows in pool if all(
            not req["specified"] or all(p is None or p.get(name) == req["value"] for p in rows[0][1:])
            for name, req in lower_mac_constraints.items())]
        pool = [(key, rows) for key, rows in pool if all(not req["specified"]
            or (rows[0][1 if req["endpoint"] == "AP" else 2] or {}).get(req["field"]) == req["value"]
            for req in ack_constraints.values())]
        if not allow_asymmetric:
            pool = [(key, rows) for key, rows in pool if rows[0][2] is None or rows[0][1] == rows[0][2]]
        requested = (distance_meters, encryption_mode, topology)
        pool = [(key, rows) for key, rows in pool if all(
            not constraints[i] or key[2][i] == value for i, value in enumerate(requested))]
        pool = [(key, rows) for key, rows in pool if all(
            not requirement["specified"] or all(p is None or p.get(name) == requirement["value"]
                for p in rows[0][1:]) for name, requirement in knob_constraints.items())]
        if not pool:
            return {**result, "reason": "UNSUPPORTED_REGIME_OR_NO_ELIGIBLE_POLICY"}
        contexts = {key[2] for key, _ in pool}
        result["available_contexts"] = [_context_metadata(c) for c in sorted(contexts, key=repr)]
        if len(contexts) != 1:
            return {**result, "reason": "AMBIGUOUS_CONTEXT_REQUIRE_EXPLICIT_CONSTRAINTS"}
        context = next(iter(contexts))
        result["context"] = _context_metadata(context)
        observed_ratios = [row.ul_goodput_mbps/row.dl_goodput_mbps if row.bidirectional else 0.0
                           for _, rows in pool for row, _, _ in rows]
        support = [min(observed_ratios), max(observed_ratios)]
        result["ratio_support"] = support
        if not support[0] <= ratio <= support[1]:
            return {**result, "reason": "UL_DL_RATIO_OUTSIDE_OBSERVED_ENVELOPE"}
        ul_share = ratio/(1+ratio)
        dl_share = 1-ul_share
        for (regime, key, context), rows in sorted(pool, key=lambda x: x[0][1]):
            ap, cpe = rows[0][1:]
            # Bulk has no recorded CPE policy: its zero UL share supplies no
            # invented endpoint values. No CPE setting is recommended for it.
            directional = lambda name: dl_share*ap[name] + (ul_share*cpe[name] if cpe else 0)
            q = dl_share*ap["aql_by_ac"][2][1] + (ul_share*cpe["aql_by_ac"][2][1] if cpe else 0)
            mean = lambda getter: self._mean_by_round([(r.round_id, getter(r)) for r, _, _ in rows])
            g, p95, p99 = (mean(lambda r: r.goodput_mbps), mean(lambda r: r.p95_ms), mean(lambda r: r.p99_ms))
            observed_ul_share = mean(lambda r: r.ul_goodput_mbps/(r.dl_goodput_mbps+r.ul_goodput_mbps)
                                     if r.bidirectional else 0.0)
            terms = dict(goodput=g/100, p95=-p95/20, p99=-0.25*p99/20,
                         directional_mismatch=-0.25*abs(ul_share-observed_ul_share),
                         queue=-(0.05+0.5*retry)*q/12000,
                         raw_rc=-0.25*retry*directional("rc_per_thresh")/256,
                         fq=-0.01*directional("fq_quantum_bytes")/1514)
            result["candidates"].append(dict(policy_id=key, ap_policy=ap, cpe_policy=cpe,
                asymmetric_package=ap!=cpe if cpe is not None else None,
                score=math.fsum(terms.values()), terms=terms,
                context=_context_metadata(context),
                evidence=[self._row_evidence(r) for r, _, _ in sorted(rows, key=lambda x: (x[0].round_id, x[0].iteration))],
                aggregation="equal_round_means_of_observed_windows_not_causal_predictions"))
        ranked = sorted(result["candidates"], key=lambda c: (-c["score"], c["policy_id"]))
        selected, hysteresis = ranked[0], False
        if previous is not None:
            # Trust no previous scores/settings: find its identity in the newly
            # admitted pool for this input/regime and recompute the score above.
            if not isinstance(previous, dict):
                raise ValueError("Previous selection must be metadata or None")
            prior = next((c for c in ranked if c["policy_id"] == previous.get("policy_id")), None)
            if (previous.get("status") == "SELECTED" and previous.get("workload_regime") == regime
                    and previous.get("context") == result["context"]
                    and prior is not None and selected["score"]-prior["score"] <= self.min_switch_gain):
                selected, hysteresis = prior, prior["policy_id"] != selected["policy_id"]
        return deepcopy({**result, **{k: selected[k] for k in ("policy_id", "ap_policy", "cpe_policy", "score")},
                "status": "SELECTED", "reason": "OBSERVED_POOL_RANKING",
                "hysteresis_held": hysteresis,
                "asymmetric_package": selected["asymmetric_package"],
                "distance_scaling": self._distance_scaling(selected, ranked, context),
                "dscp_metadata": _dscp_metadata(selected["ap_policy"], selected["cpe_policy"])})

    @staticmethod
    def _distance_scaling(selected, ranked, context):
        """Describe finite observed BE options, never compute a new AQL tuple.

        At a recorded timing point the unchanged outcome/cost objective selects
        a whole package (including CoDel/TSQ). Different packages confound BE;
        this is not a fitted distance formula or a recommendation for real km.
        """
        return dict(method="EXACT_TIMING_POINT_OBSERVED_PACKAGE_SELECTION",
                    timing_distance_meters=context[0], physical_distance_verified=False,
                    interpolation=False, extrapolation=False, synthesized_policy=False,
                    selected_be_us={endpoint: selected[name]["aql_by_ac"][2]
                        if selected[name] else None
                        for endpoint, name in (("AP", "ap_policy"), ("CPE", "cpe_policy"))},
                    observed_be_options=[dict(policy_id=c["policy_id"],
                        AP=c["ap_policy"]["aql_by_ac"][2],
                        CPE=c["cpe_policy"]["aql_by_ac"][2] if c["cpe_policy"] else None,
                        evidence=c["evidence"]) for c in ranked],
                    gain_claim="NONE; sequential package outcomes confound individual coordinates")
