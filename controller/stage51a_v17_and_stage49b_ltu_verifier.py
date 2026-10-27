"""Stage45B saved-source audit. Pure contract checks never authorize devices.

Round summaries, receiver strings and recipe readbacks are separate evidence.
Successful local export is not physical or causal acceptance.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import statistics
import tempfile

from controller.stage42a_netdev_txq_and_airos6_verifier import (
    AP_AQL, CPE_AQL, PEERS, _dict, _local_path, _need, _number, _uint,
    canonical_digest, read_json,
)
from controller.stage44a_champion_v15_and_ltu_beacon_verifier import (
    AP_INTERFACES, CPE_INTERFACES, SYSCTLS,
)
from controller.stage46a_champion_v16_tx_bias_and_bql_verifier import (
    DYNAMIC_POLICY, audit_bql_snapshot, audit_udp_observation, tx_bias_effect,
)

ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "T-S45B-CODEX-STAGE51A-CHAMPION-V17-BQL-42392-AND-STAGE49B-LTU-VERIFIER"
SOURCE_51A = "artifacts/autoresearch/stage51a_m30_m31_bql_sweetspot_and_aql_bench_20261025.json"
SOURCE_49B = "artifacts/autoresearch/stage49b_ltu_pb_boost_and_frame_len_ota_bench_20261025.json"
REPORT_51A = "docs/STAGE51A_M30_M31_BQL_SWEETSPOT_AND_AQL_BENCHMARK.md"
REPORT_49B = "docs/STAGE49B_LTU_PB_BOOST_AND_FRAME_LEN_OTA_BENCHMARK.md"
OUTPUT = "artifacts/autoresearch/stage45b_v17_and_stage49b_audit_20261025.json"
SOURCE_PINS = ("d829e73995ab55dfe71d41aab6a00a873c0aff83f05df29c7507cb1542869386",
               "7346f3fb6a26ea5906465a874b8a462df5a3d68d39fc9070cd73461f69fb79a5")
REPORT_PINS = ("85988021fc99c8b2c3bfbc41fcb905332c303d08a20f0554621df11dc69ac2e8",
               "c6c9f7e19f0749839586c6034ea3923fa4cd7d23ed88c9a0410a2aa4eec11126")
ROUND_PINS = dict(zip((f"S51A-R{i}" for i in range(1, 7)), (
    "6c7b4f237fae0c031a47816e42c0f0b6dbc08e12c8fbf49d465cea9e6e658ee1",
    "bf6ce44b1342c8023eba14658171a78b41b373f2a0cfbae336efdc31003100fd",
    "fc7265ab10aeb6fdbbd2e9ee07056e6ed5260d18b98c5a5b023bb2966126f79f",
    "0761e91a45f79290813f6fc844af02c87e7e94bca830130d740f4510c95c4727",
    "58d0518b8140637dacaff8e7986c777e911308e6450ce6207ef7dda0d2636065",
    "879a617a25144a2641b77a892f3d927c6430725ad65078a71841ecc2f0dd1007")))
PROFILES = ("S49B-R0-STAGE48B-BASELINE", "S49B-R1-PB-BOOST-ON-2MS",
            "S49B-R2-PB-BOOST-AND-EVM-MCS-CEILING")
TRIAL_ORDER = tuple((PROFILES[(i + rep - 1) % 3], rep) for rep in range(1, 4) for i in range(3))
TRIAL_PINS = dict(zip(TRIAL_ORDER, (
    "ab51dd67becc2a326b5c716e91d348a4ea4a166a0fa0692ab48adf1f29a24f10",
    "ff4eef49020bc0ae7e4a5256bf64ed102584de08f1c58a98667020b7332e14e6",
    "3db85b6d85963cbf2b7935f39158e6629415eea3504076ee6d8a4af640d0e05e",
    "5a897e5f55f9e717a6ae93ea85b0f95225fddc6a386e9a0d2a8c5944b8c91584",
    "7645f0907c5d030aef53799ba005b43615a4932c23f0305d1b0dc3f4ee409150",
    "a8bad8d0ae44f3cfb6bed3ad64cc141669c1927867e899054025aadaa6672b26",
    "0df40d145dd6310e8c5011536de33c5852b3487a462344676491ae5dead24422",
    "5cd03c42cc1f163feb6e780c1d66818610f132e4082a26954ca3ff2c8588378d",
    "7613fee6ade3fdfe7bc4b03669ca0e874a76899d898e162606c126099e1f6a32")))
PHASES = ("A1", "B1", "A2", "B2")
V17_BQL = {"limit_min": 3028, "limit_max": 42392, "hold_time": 1000}
MCS_MAP = {"7": "qpsk (2x)", "11": "16qam (4x)", "15": "64qam (6x)",
           "19": "256qam (8x)", "23": "1024qam (10x)", "31": "4096qam (12x)", "32": "automatic (2x)"}
LTU_MEANS = ("bulk_tcp_mbps", "iptv_udp_mbps", "iptv_jitter_ms", "iptv_loss_pct",
             "voip_jitter_ms", "voip_loss_pct", "loaded_ping_p50_ms", "loaded_ping_p95_ms", "loaded_ping_p99_ms")


def _value(value, *, positive=False):
    value = _number(value, positive=positive)
    _need(value <= 1e12, "BOUNDED_MEASUREMENT_REQUIRED")
    return value


def _signed(value):
    _need(type(value) in (int, float), "FINITE_SIGNED_NUMBER_REQUIRED")
    try:
        valid = math.isfinite(value) and abs(value) <= 1e15
    except OverflowError:
        valid = False
    _need(valid, "BOUNDED_FINITE_SIGNED_NUMBER_REQUIRED")
    return float(value)


def _mean(values, digits=3):
    return round(statistics.mean(values), digits)


def _delta(control, target, digits=4):
    _need(control > 0, "POSITIVE_CONTROL_DENOMINATOR_REQUIRED")
    result = 100 * (target - control) / control
    _need(math.isfinite(result), "FINITE_DELTA_REQUIRED")
    return round(result, digits)


def _fields(actual, expected):
    actual = _dict(actual)
    for key, value in expected.items():
        _need(_uint(actual.get(key)) == value, "SUPPLIED_PROFILE_FIELD_MISMATCH:" + key)


def _rows(document):
    rows = _dict(document).get("rounds")
    _need(type(rows) is list and len(rows) == 6, "ALL_SIX_ROUNDS_REQUIRED")
    result = {}
    for row in rows:
        row = _dict(row); ident = row.get("round_id")
        _need(type(ident) is str and ident in ROUND_PINS and ident not in result, "UNIQUE_EXPECTED_ROUND_REQUIRED")
        result[ident] = row
    return result


def _trials(document):
    trials = _dict(document).get("trials")
    _need(type(trials) is list and len(trials) == 9, "ALL_NINE_TRIALS_REQUIRED")
    result = {}
    for item in trials:
        item = _dict(item); profile, rep = item.get("profile_id"), _uint(item.get("rep"))
        _need(type(profile) is str and profile in PROFILES and 1 <= rep <= 3 and
              (profile, rep) not in result, "UNIQUE_EXPECTED_PROFILE_REP_REQUIRED")
        result[profile, rep] = item
    return result


def source_contract(stage51a, stage49b, report51_text, report49_text):
    rows, trials = _rows(stage51a), _trials(stage49b)
    for ident, pin in ROUND_PINS.items():
        _need(canonical_digest(rows[ident]) == pin, "PINNED_ROUND_DRIFT:" + ident)
    for key, pin in TRIAL_PINS.items():
        _need(canonical_digest(trials[key]) == pin, "PINNED_TRIAL_DRIFT:" + str(key))
    for doc, pin in zip((stage51a, stage49b), SOURCE_PINS):
        _need(canonical_digest(doc) == pin, "PINNED_SOURCE_ENVELOPE_DRIFT")
    for text, pin in zip((report51_text, report49_text), REPORT_PINS):
        _need(type(text) is str and hashlib.sha256(text.encode()).hexdigest() == pin, "PINNED_REPORT_BYTES_REQUIRED")
    return {"saved_objects_authenticated": True, "source_canonical_sha256": list(SOURCE_PINS),
            "report_raw_sha256": list(REPORT_PINS), "round_bindings": ROUND_PINS,
            "trial_bindings": [{"profile_id": p, "rep": n, "canonical_sha256": h} for (p, n), h in TRIAL_PINS.items()],
            "native_acquisition_authenticated": False}


def verify_v17_profile(getter):
    """Supplied R6 policy, including asymmetric queues; never a native getter."""
    getter = _dict(getter)
    bql = {}
    for prefix, interfaces, aql in (("ap", AP_INTERFACES, AP_AQL), ("cpe", CPE_INTERFACES, CPE_AQL)):
        bql[prefix] = audit_bql_snapshot(getter.get(prefix + "_eth0_bql"))
        _fields(getter[prefix + "_eth0_bql"], V17_BQL)
        _need(bql[prefix]["current_within_configured_bounds"], "V17_CURRENT_BQL_OUTSIDE_BOUNDS")
        _fields(getter.get(prefix + "_sysctl"), {**SYSCTLS, "dev_weight_tx_bias": 2})
        queues = _dict(getter.get(prefix + "_netdev_tx_queue_len"))
        _need(set(queues) == set(interfaces), "COMPLETE_INTERFACE_SET_REQUIRED")
        _fields(queues, {name: 1000 if name in ("eth0", "lo", "br-wan") else 256 for name in interfaces})
        _fields(getter.get(prefix + "_aqm"), {"fq_flows_cnt": 4096, "fq_memory_limit": 4194304,
                "fq_limit": 2048 if prefix == "ap" else 1024, "fq_quantum": 4542 if prefix == "ap" else 1514})
        actual = _dict(getter.get(prefix + "_aql_txq_limit"))
        _need(set(actual) == set(aql), "COMPLETE_AQL_AC_SET_REQUIRED")
        for ac, expected in aql.items():
            _fields(actual[ac], expected)
    rocket, m5 = _dict(getter.get("r5ac_m26_state")), _dict(getter.get("lbm5_m29_state"))
    _fields(rocket, {"br0_txqueuelen": 256, "ath0_txqueuelen": 256, "eth0_txqueuelen": 256,
                     "netdev_budget": 600, "dev_weight": 64})
    _need(rocket.get("ff_mcast_airtime_limit") == "5 " + " ".join(["0"] * 15), "ROCKET_VECTOR_REQUIRED")
    _fields(m5, {"br0_txqueuelen": 256, "ath0_txqueuelen": 256, "eth0_txqueuelen": 256,
                "netdev_budget": 300, "ewma_delegate": 1, "no_auto_prio": 0})
    _need(m5.get("txop_params") == "0 0" and m5.get("no_ack_rate") == "0 -1", "M5_VECTORS_REQUIRED")
    return {"supplied_profile_matches": True, "bql": bql, "native_authenticated": False,
            "bql_is_adaptive_with_configured_bounds": True, "universal_optimum_proven": False,
            "build_cpu_identity_and_station_weight_getter_qualified": False}


def _recipe(ident, phase):
    candidate = phase.startswith("B")
    bql = dict(DYNAMIC_POLICY)
    if candidate and ident in ("S51A-R1", "S51A-R2", "S51A-R4", "S51A-R6"):
        bql = dict(V17_BQL)
        if ident == "S51A-R1":
            bql.update(limit_max=36336, hold_time=750)
    return {"bql": bql, "dev_weight": 80 if candidate and ident == "S51A-R4" else 64,
            "vi": {"low_us": 2000, "high_us": 3500} if candidate and ident in
                   ("S51A-R3", "S51A-R4", "S51A-R5") else AP_AQL["VI"]}


def _udp(observation):
    result = audit_udp_observation(observation)
    bitrate = _value(observation.get("delivered_bitrate_mbps"))
    match = re.search(r"\s([0-9]+(?:\.[0-9]+)?) ([KMG]?)bits/sec\s", result["raw"]["receiver_line"])
    _need(match is not None, "RAW_UDP_BITRATE_REQUIRED")
    scale = {"": 1e-6, "K": 1e-3, "M": 1, "G": 1000}[match[2]]
    raw_rate = _value(float(match[1]) * scale)
    precision = len(match[1].partition(".")[2])
    result["typed"]["bitrate_mbps"] = bitrate
    result["raw"]["bitrate_mbps"] = raw_rate
    result["checks"]["typed_bitrate_vs_raw"] = abs(bitrate - raw_rate) <= 0.5 * 10 ** (-precision) * scale + 1e-9
    result["consistent"] = all(result["checks"].values())
    return result


def audit_stage51a(document):
    rows, result, findings, failed_windows = _rows(document), [], [], []
    metric_fields = {"goodput": ("aggregate_goodput_mbps", "goodput_mbps"),
                     "p50": ("sector_p50_rtt_ms", "p50_rtt_ms"),
                     "p95": ("sector_p95_rtt_ms", "p95_rtt_ms"), "p99": ("sector_p99_rtt_ms", "p99_rtt_ms")}
    for ident in ROUND_PINS:
        row, windows, metrics = rows[ident], {}, {}
        phases = _dict(row.get("phases")); _need(set(phases) == set(PHASES), "ALL_FOUR_PHASES_REQUIRED")
        _need(type(row.get("promoted")) is bool, "PROMOTION_BOOL_REQUIRED")
        for phase in PHASES:
            item = _dict(phases[phase]); getter = _dict(item.get("getter_readback")); recipe = _recipe(ident, phase)
            bql = {}
            for prefix in ("ap", "cpe"):
                bql[prefix] = audit_bql_snapshot(getter.get(prefix + "_eth0_bql"))
                _fields(getter[prefix + "_eth0_bql"], recipe["bql"])
                _fields(getter.get(prefix + "_sysctl"), {"dev_weight": recipe["dev_weight"],
                        "dev_weight_tx_bias": 2, "netdev_budget": 600, "netdev_budget_usecs": 20000})
                _fields(_dict(getter.get(prefix + "_aql_txq_limit")).get("VI"), recipe["vi"])
                if not bql[prefix]["current_within_configured_bounds"]:
                    findings.append({"code": "BQL_CURRENT_OUTSIDE_BOUNDS", "round": ident, "phase": phase, "endpoint": prefix})
            _fields(getter.get("lbm5_m29_state"), {"netdev_budget": 300})
            _fields(getter.get("r5ac_m26_state"), {"netdev_budget": 600})
            udp = {name: _udp(item.get(field)) for name, field in
                   (("iptv", "iptv_dual_stream_ac_vi"), ("voip", "voip_stream_ac_vo"))}
            for stream, value in udp.items():
                for check, ok in value["checks"].items():
                    if not ok:
                        findings.append({"code": "UDP_LAYER_DISAGREEMENT", "round": ident, "phase": phase,
                                         "stream": stream, "check": check})
            peers = _dict(item.get("per_cpe")); _need(set(peers) == set(PEERS), "ALL_THREE_CPES_REQUIRED")
            losses, counts, peer_goodput = {}, {}, {}
            for name, (mac, _) in PEERS.items():
                peer = _dict(peers[name]); latency = _dict(peer.get("latency"))
                _need(peer.get("mac") == mac, "EXACT_REPORTED_PEER_REQUIRED")
                losses[name] = _value(latency.get("loss_pct")); _need(losses[name] <= 100, "PING_PERCENT_RANGE")
                counts[name] = _uint(latency.get("count"))
                for field in ("p50_ms", "p95_ms", "p99_ms", "mean_ms", "jitter_ms"):
                    _value(latency.get(field))
                peer_goodput[name] = _value(peer.get("goodput_mbps"))
            if any(losses.values()):
                failed_windows.append({"round": ident, "phase": phase, "per_cpe_loss_pct": losses,
                                       "received_counts": counts})
            loss = _value(item.get("mean_loss_pct")); _need(loss <= 100, "PING_PERCENT_RANGE")
            if abs(loss - _mean(losses.values(), 2)) > 0.011:
                findings.append({"code": "SECTOR_LOSS_MEAN_DISAGREES", "round": ident, "phase": phase})
            for field, _ in metric_fields.values():
                _value(item.get(field), positive=True)
            ap_queues = _dict(getter.get("ap_netdev_tx_queue_len"))
            queue_shape_matches = set(ap_queues) == set(AP_INTERFACES) and all(
                _uint(ap_queues.get(name)) == (1000 if name in ("eth0", "lo") else 256)
                for name in AP_INTERFACES)
            if not queue_shape_matches:
                findings.append({"code": "AP_QUEUE_INVENTORY_DIFFERS_FROM_FULL_BASELINE", "round": ident, "phase": phase,
                                 "readback": ap_queues})
            windows[phase] = {"udp": udp, "bql": bql, "recipe": recipe, "per_cpe_loss_pct": losses,
                              "per_cpe_goodput_mbps": peer_goodput,
                              "received_counts": counts, "declared_sector_mean_loss_pct": loss,
                              "station_airtime_weights_readback": _dict(getter.get("ap_station_airtime_weights")),
                              "getter_arm_label": getter.get("arm_label")}
        for name, (field, summary_suffix) in metric_fields.items():
            a, b = (_mean([_value(phases[arm + str(n)][field], positive=True) for n in (1, 2)]) for arm in ("A", "B"))
            metrics[name] = {"control": a, "target": b, "delta_pct": _delta(a, b)}
            for arm, value in (("a", a), ("b", b)):
                reported = _value(row.get("arm_" + arm + "_mean_" + summary_suffix), positive=True)
                if abs(reported - value) > 0.0011:
                    findings.append({"code": "SUMMARY_MEAN_DISAGREES", "round": ident, "field": name,
                                     "arm": arm, "reported": reported, "recomputed": value})
        for stream in ("iptv", "voip"):
            layers = {}
            for arm in ("A", "B"):
                obs = [windows[arm + str(n)]["udp"][stream] for n in (1, 2)]
                lost, total = (sum(x["typed"][key] for x in obs) for key in ("lost", "total"))
                layers[arm] = {"typed_mean_jitter_ms": _mean([x["typed"]["jitter_ms"] for x in obs]),
                               "raw_mean_jitter_ms": _mean([x["raw"]["jitter_ms"] for x in obs]),
                               "typed_mean_bitrate_mbps": _mean([x["typed"]["bitrate_mbps"] for x in obs]),
                               "raw_mean_bitrate_mbps": _mean([x["raw"]["bitrate_mbps"] for x in obs]),
                               "mean_typed_loss_pct": _mean([x["typed"]["pct"] for x in obs], 4),
                               "lost": lost, "total": total, "pooled_count_loss_pct": 100 * lost / total}
                for suffix, value in (("jitter_ms", layers[arm]["typed_mean_jitter_ms"]),
                                      ("loss_pct", layers[arm]["mean_typed_loss_pct"])):
                    key = stream + "_arm_" + arm.lower() + "_mean_" + suffix
                    if abs(_value(row.get(key)) - value) > (0.0011 if suffix == "jitter_ms" else 0.00011):
                        findings.append({"code": "UDP_SUMMARY_DISAGREES", "round": ident, "field": key})
                if stream == "iptv":
                    key = "iptv_arm_" + arm.lower() + "_mean_bitrate_mbps"
                    if abs(_value(row.get(key)) - layers[arm]["typed_mean_bitrate_mbps"]) > 0.0011:
                        findings.append({"code": "UDP_SUMMARY_DISAGREES", "round": ident, "field": key})
            layers["typed_jitter_delta_pct"] = _delta(layers["A"]["typed_mean_jitter_ms"], layers["B"]["typed_mean_jitter_ms"])
            layers["raw_jitter_delta_pct"] = _delta(layers["A"]["raw_mean_jitter_ms"], layers["B"]["raw_mean_jitter_ms"])
            metrics[stream] = layers
        metrics["pareto_score_delta_pct"] = round(metrics["goodput"]["delta_pct"] - 0.35 * metrics["p95"]["delta_pct"], 4)
        for key, value in (("goodput_delta_pct", metrics["goodput"]["delta_pct"]),
                           ("p95_rtt_delta_pct", metrics["p95"]["delta_pct"]),
                           ("pareto_score_delta_pct", metrics["pareto_score_delta_pct"]),
                           ("iptv_jitter_delta_pct", metrics["iptv"]["typed_jitter_delta_pct"]),
                           ("voip_jitter_delta_pct", metrics["voip"]["typed_jitter_delta_pct"])):
            if abs(_signed(row.get(key)) - value) > 0.0011:
                findings.append({"code": "SUMMARY_DELTA_DISAGREES", "round": ident, "field": key,
                                 "reported": row[key], "recomputed": value})
        result.append({"round_id": ident, "reported_decision": row.get("decision"), "reported_promoted": row["promoted"],
                       "metrics": metrics, "windows": windows})
    summary = _dict(document.get("summary"))
    _fields(summary, {"rounds_executed": 6, "promoted_count": sum(r["promoted"] for r in rows.values())})
    _need(type(summary.get("all_radios_healthy")) is bool, "HEALTH_BOOL_REQUIRED")
    if summary["all_radios_healthy"] and failed_windows:
        findings.append({"code": "SUMMARY_HEALTH_DOES_NOT_QUALIFY_FAILED_WINDOWS", "failed_windows": len(failed_windows)})
    return {"rounds": result, "windows": 24, "udp_observations": 48, "findings": findings,
            "failed_ping_windows": failed_windows, "reported_active_champion": summary.get("active_champion_after_stage51a"),
            "champion": {"reported_version": 17, "reported_promoted_round": "S51A-R6",
                         "supplied_profiles": {phase: verify_v17_profile(rows["S51A-R6"]["phases"][phase]["getter_readback"])
                                               for phase in ("B1", "B2")}, "native_promotion_accepted": False},
            "design": {"listed_order": list(PHASES), "is_abba": False, "randomization_proven": False,
                       "sector_rtt_statistic": "Unweighted mean of per-CPE quantiles with count>0; then mean of2 windows per arm",
                       "goodput_statistic": "Mixed station byte deltas and max(application streams, OTA bytes) for Loco",
                       "application_workload": "Loco bidirectional TCP+IPTV+VoIP; Rocket/M5 large ICMP loops; not3 per-CPE TCP streams",
                       "representative_sector_capacity_or_fairness_proven": False,
                       "pooled_rtt_quantiles_reconstructable": False, "kernel_build_and_causal_mechanism_qualified": False,
                       "getter_epoch": "Before load; inflight0 is not an under-load DQL convergence trace",
                       "m5_state_fresh_per_arm": False, "station_weight_getter_nonempty_windows": sum(
                           bool(w["station_airtime_weights_readback"]) for r in result for w in r["windows"].values())},
            "tx_bias": tx_bias_effect(dev_weight=64, tx_bias=2, driver_napi_weight=64),
            "bql_policy": {"v16_default": DYNAMIC_POLICY, "v17_bounded_candidate": V17_BQL,
                           "v16_descriptor_alone_resets_bql": False,
                           "dynamic_restore_is_explicit_in_stage51a_runner": True,
                           "fixed_operating_limit_or_universal_optimum": False}, "native_acceptance": False}


def verify_ltu_rate_contract(*, auto_mcs_ceiling, cpe_id, mcs_level, opcode):
    """Safe supplied auto-rate contract; emits no device commands."""
    ceiling, peer, level, operation = (_uint(v) for v in (auto_mcs_ceiling, cpe_id, mcs_level, opcode))
    _need(str(ceiling) in MCS_MAP, "DECLARED_AUTOMCS_CEILING_INDEX_REQUIRED")
    _need(peer == 0 and operation in (0, 2), "STAGE49B_PEER_ZERO_AUTO_RATE_OPCODE_REQUIRED")
    _need(level == 32, "CPE_MCS_AUTO_REQUIRES_32_NOT_CEILING_INDEX")
    return {"auto_mcs_ceiling": ceiling, "reported_ceiling_label": MCS_MAP[str(ceiling)],
            "cpe_id": peer, "mcs_level": level, "opcode": operation,
            "supplied_contract_consistent": True, "native_abi_and_siso_recovery_authenticated": False}


def _bandwidth_config(text):
    _need(type(text) is str and 0 < len(text) <= 8192, "BOUNDED_BANDWIDTH_CONFIG_REQUIRED")
    _need(text.strip().startswith("{") and text.strip().endswith("}"), "BANDWIDTH_CONFIG_BRACES_REQUIRED")
    matches = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([0-9]+)", text)
    fields = {}
    for key, value in matches:
        _need(key not in fields, "DUPLICATE_BANDWIDTH_CONFIG_FIELD")
        fields[key] = _uint(int(value))
    remainder = re.sub(r"[A-Za-z_][A-Za-z0-9_]*\s*:\s*[0-9]+", "", text)
    _need(re.fullmatch(r"[\s{},]*", remainder) is not None, "NUMERIC_BANDWIDTH_CONFIG_FIELDS_REQUIRED")
    _need(set(fields) == {"bandwidth", "frame_period", "duty_cycle", "sample_rate", "cpsample",
                          "dl_symbols", "ul_symbols", "gap0", "gap1", "cz_len"}, "COMPLETE_BANDWIDTH_CONFIG_REQUIRED")
    return fields


def audit_frame_len_discovery(discovery):
    discovery = _dict(discovery)
    _need(type(discovery.get("ame_core_sysfs_frame_len_bug_confirmed")) is bool, "EXPLICIT_BUG_FLAG_REQUIRED")
    before = _bandwidth_config(discovery.get("bandwidthConfig_after_echo_5000_frame_len"))
    restored = _bandwidth_config(discovery.get("bandwidthConfig_after_restore_duty_cycle_750"))
    expected = {"frame_period": 2000, "bandwidth": 20, "dl_symbols": 60, "ul_symbols": 19}
    _fields(before, {**expected, "duty_cycle": 5000}); _fields(restored, {**expected, "duty_cycle": 750})
    mapping = _dict(discovery.get("verified_autoMcsCeiling_map"))
    _need(mapping == MCS_MAP, "COMPLETE_DECLARED_MCS_MAP_REQUIRED")
    return {"reported_bug_confirmed": discovery["ame_core_sysfs_frame_len_bug_confirmed"],
            "saved_values_match_reported_duty_cycle_overwrite": True, "after_frame_len_write": before,
            "after_duty_cycle_restore": restored, "cz_len_changed": before["cz_len"] != restored["cz_len"],
            "full_mcs_map": mapping, "full_map_probed_by_current_runner": False,
            "handler_root_cause_or_5ms_mode_proven": False, "running_module_hash": "MISSING"}


def audit_stage49b(document):
    trials, results, findings, profiles = _trials(document), [], [], {}
    for item in document["trials"]:
        profile, rep = item["profile_id"], item["rep"]; index = PROFILES.index(profile)
        vals = {key: _value(item.get(key)) for key in (*LTU_MEANS, "voip_udp_mbps")}
        _need(vals["iptv_loss_pct"] <= 100 and vals["voip_loss_pct"] <= 100, "UDP_PERCENT_RANGE")
        _need(vals["loaded_ping_p50_ms"] <= vals["loaded_ping_p95_ms"] <= vals["loaded_ping_p99_ms"], "ORDERED_QUANTILES_REQUIRED")
        samples = _uint(item.get("loaded_ping_samples")); _need(samples > 0, "POSITIVE_PING_SAMPLE_COUNT_REQUIRED")
        _uint(item.get("bulk_tcp_retransmits"))
        meta = _dict(item.get("apply_meta")); expected_pb, expected_label = (2 if index == 0 else 1), ("64qam (6x)" if index == 2 else "1024qam (10x)")
        observed = {}
        for endpoint in ("ap", "cpe"):
            text = meta.get(endpoint + "_apply_out")
            _need(type(text) is str and 0 < len(text) <= 8192, "BOUNDED_APPLY_READBACK_REQUIRED")
            match = re.fullmatch(r"(?:OTA_OK\n)?([012]) \(0:OFF, 1:ON, 2:AUTO\) gain:0x([0-9a-fA-F]+)\n(1024qam \(10x\)|64qam \(6x\))", text)
            _need(match is not None and int(match[1]) == expected_pb and match[3] == expected_label, "EXPECTED_PB_AND_CEILING_READBACK_REQUIRED")
            observed[endpoint] = {"pb_boost": int(match[1]), "gain_raw_hex": match[2], "ceiling_label": match[3], "raw": text}
        _need(type(meta.get("ota_verified")) is bool and type(meta.get("cpe_watchdog_disarmed_after_verify")) is bool,
              "EXPLICIT_OTA_AND_WATCHDOG_FLAGS_REQUIRED")
        _need(meta["ota_verified"] == ("OTA_OK" in meta["ap_apply_out"]), "OTA_FLAG_AND_MARKER_MUST_AGREE")
        bler = item.get("bler_snapshot"); _need(type(bler) is str and 0 < len(bler) <= 8192, "BOUNDED_BLER_TEXT_REQUIRED")
        results.append({"profile_id": profile, "rep": rep, "values": vals, "ping_samples": samples,
                        "apply_readback": observed, "reported_ota_verified": meta["ota_verified"],
                        "reported_watchdog_disarmed": meta["cpe_watchdog_disarmed_after_verify"],
                        "watchdog_execution_or_full_rollback_proven": False, "raw_bler_snapshot": bler})
    summaries = _dict(document.get("summary_by_profile")); _need(set(summaries) == set(PROFILES), "ALL_THREE_PROFILE_SUMMARIES_REQUIRED")
    for profile in PROFILES:
        obs = [t for t in results if t["profile_id"] == profile]
        means = {"mean_" + key: _mean([t["values"][key] for t in obs]) for key in LTU_MEANS}
        means["mean_aggregate_dl_mbps"] = _mean([t["values"]["bulk_tcp_mbps"] + t["values"]["iptv_udp_mbps"] for t in obs])
        for short in ("p50", "p95"):
            key = "loaded_ping_" + short + "_ms"
            means["median_" + key] = statistics.median([t["values"][key] for t in obs])
        summary = _dict(summaries[profile]); _need(_uint(summary.get("n_trials")) == 3, "THREE_TRIALS_PER_PROFILE_REQUIRED")
        comparisons = {}
        for key, value in means.items():
            reported = _value(summary.get(key)); comparisons[key] = abs(reported - value) <= 0.0011
            if not comparisons[key]:
                findings.append({"code": "PROFILE_SUMMARY_DISAGREES", "profile_id": profile, "field": key,
                                 "reported": reported, "recomputed": value})
        profiles[profile] = {"means": means, "summary_checks": comparisons,
                             "rate_contracts": [verify_ltu_rate_contract(auto_mcs_ceiling=15 if profile == PROFILES[2] else 23,
                                                    cpe_id=0, mcs_level=32, opcode=op) for op in (0, 2)]}
    baseline = profiles[PROFILES[0]]["means"]
    changes = {p: {key: _delta(baseline[key], value) for key, value in profiles[p]["means"].items() if baseline[key] > 0}
               for p in PROFILES[1:]}
    order = [(t["profile_id"], t["rep"]) for t in results]
    findings.append({"code": "R2_LATENCY_BENEFIT_HAS_IPTV_THROUGHPUT_AND_JITTER_TRADEOFF",
                     "rep3_iptv_jitter_ms": trials[PROFILES[2], 3]["iptv_jitter_ms"],
                     "rep3_p95_ms": trials[PROFILES[2], 3]["loaded_ping_p95_ms"]})
    return {"trials": results, "profiles": profiles, "changes_vs_baseline_pct": changes, "findings": findings,
            "frame_len_discovery": audit_frame_len_discovery(document.get("hardware_and_driver_discoveries")),
            "design": {"listed_order": [{"profile_id": p, "rep": n} for p, n in order],
                       "cyclic_latin_square_positions": tuple(order) == TRIAL_ORDER, "randomization_proven": False,
                       "carryover_balanced": False, "five_samples_per_trial": all(t["ping_samples"] == 5 for t in results),
                       "quantiles": "Runner linear interpolation at (N-1)*p; mean/median of trial quantiles, not pooled packet quantiles",
                       "raw_ping_receiver_counts_and_timestamp_epochs": "MISSING", "isolated_pb_or_ceiling_cause_proven": False},
            "recipe_qualifications": {"R1_also_changes": ["SWQ20to2", "DGAIN0to1", "AP_UL_strategy0to1", "AP_UL_PM65535to0", "stallBD2to0"],
                                      "R2_also_changes": ["HTB26to25Mbps", "BEceil26to24Mbps", "burst15kto12k", "FQtarget2to1.5ms", "FQinterval40to30ms"],
                                      "cpe_mcs_getter_and_before_after_siso_recovery": "MISSING",
                                      "full_mcs_map_and_bug_flag_hardcoded_in_runner": True,
                                      "af_set_framelength_executed_by_current_runner": False,
                                      "five_ms_or_40mhz_treatment_present": False,
                                      "watchdog_partial_restore": ["autoMcsCeiling23", "pb_boost2"], "native_effective_recipe_qualified": False},
            "post_bench_link_snapshot": _dict(document.get("ota_link_verification_post_bench")),
            "standalone_route_isolation_and_coldboot_proven": False, "native_acceptance": False}


def audit_saved_sources(root=ROOT):
    root = _local_path(root)
    docs = [read_json(root / p) for p in (SOURCE_51A, SOURCE_49B)]
    reports, raw_hashes = [], {}
    for p in (SOURCE_51A, SOURCE_49B, REPORT_51A, REPORT_49B):
        path = _local_path(root / p); _need(path.stat().st_size <= 1_000_000, "BOUNDED_SAVED_SOURCE_REQUIRED")
        raw = path.read_bytes(); _need(len(raw) <= 1_000_000, "BOUNDED_SAVED_SOURCE_REQUIRED")
        raw_hashes[p] = hashlib.sha256(raw).hexdigest()
        if p in (REPORT_51A, REPORT_49B):
            reports.append(raw.decode("utf-8"))
    contract = source_contract(*docs, *reports)
    s51, s49 = audit_stage51a(docs[0]), audit_stage49b(docs[1])
    # These report-only numbers belong to authenticated report bytes above.
    report_claims = {"S51A_R4_iptv_jitter_ms_A_B": [1.392, 1.976],
                     "S51A_R4_voip_jitter_ms_A_B": [2.838, 2.753],
                     "S51A_R5_claims_all_3_CPEs_verified": True}
    return {"audit_version": 1, "task_id": TASK_ID, "audit_status": "COMPLETE_WITH_QUALIFICATIONS",
            "source_contract": contract, "input_raw_sha256": raw_hashes,
            "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "stage51a": s51, "stage49b": s49,
            "static_recipe_context_sha256": {
                "tools/bench/run_stage51a_m30_m31_bql_sweetspot_and_aql_bench.py": "3a0e847df88027164c3ee7682d5e60ef7f3ddf0f9eb495cb60688299c61dd9dc",
                "tools/bench/run_stage49b_ltu_pb_boost_and_frame_len_ota_bench.py": "224369feb832b68d7de56422f05900f2b860621d8a064f6bf72761f8475eaf5e",
                "tools/bench/run_stage37a_triple_play_aqm_fq_limit_bench.py": "41b5e852d020e44d0d9f7497de49244d942e3c3b6604e1b2a584d9c6d35231c7"},
            "pinned_report_qualifications": {"claims": report_claims,
                "S51A_R4_exact_json_iptv_jitter_ms_A_B": [s51["rounds"][3]["metrics"]["iptv"][a]["typed_mean_jitter_ms"] for a in ("A", "B")],
                "S51A_R4_exact_json_voip_jitter_ms_A_B": [s51["rounds"][3]["metrics"]["voip"][a]["typed_mean_jitter_ms"] for a in ("A", "B")],
                "S51A_R5_failed_M5_windows": [w for w in s51["failed_ping_windows"] if w["round"] == "S51A-R5"],
                "S49B_full_MCS_map_is_literal_in_runner": True, "S49B_frame_len_root_cause_not_proven": True},
            "boundary": {"offline_only": True, "ssh": False, "hardware_access": False,
                         "native_dispatch_allowed": False, "physical_acceptance": "UNKNOWN", "e2": "NOT_ACCEPTED"}}


def write_audit(audit, output, *, protected_paths=()):
    """Atomic local managed JSON export with fail-closed path/ownership guards."""
    audit = _dict(audit)
    _need(audit.get("task_id") == TASK_ID and type(audit.get("audit_version")) is int and audit["audit_version"] == 1,
          "MANAGED_STAGE45B_AUDIT_REQUIRED")
    _need(isinstance(output, (str, Path)), "LOCAL_OUTPUT_PATH_REQUIRED")
    raw_path = str(output); normalized = raw_path.replace("\\", "/")
    _need(raw_path and "\x00" not in raw_path and not normalized.startswith("//") and
          (not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", normalized) or re.match(r"^[A-Za-z]:/", normalized)),
          "NETWORK_URI_OR_DEVICE_OUTPUT_NOT_ALLOWED")
    candidate = Path(output).absolute(); parent = _local_path(candidate.parent)
    _need(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,180}\.json", candidate.name, re.I) and
          candidate.stem.split(".")[0].upper() not in {"CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1, 10)], *[f"LPT{i}" for i in range(1, 10)]},
          "LITERAL_NONDEVICE_JSON_FILENAME_REQUIRED")
    target = parent / candidate.name
    for protected in protected_paths:
        _need(target != _local_path(protected), "SOURCE_OVERWRITE_REJECTED")
    if target.exists() or target.is_symlink():
        current = read_json(target)
        _need(current.get("task_id") == TASK_ID and type(current.get("audit_version")) is int and current["audit_version"] == 1,
              "UNOWNED_OUTPUT_OVERWRITE_REJECTED")
    try:
        payload = (json.dumps(audit, indent=2, ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")
    except (ValueError, TypeError, OverflowError) as error:
        raise ValueError("FINITE_JSON_AUDIT_REQUIRED") from error
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=parent, prefix=".stage45b-", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name); handle.write(payload); handle.flush(); os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return target
