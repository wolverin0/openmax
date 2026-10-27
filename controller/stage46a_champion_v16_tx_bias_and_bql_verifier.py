"""Stage43B: offline v16 audit; conflicting saved layers remain conflicting.

No native runner, network, deployment or target execution. Profile and CPU
checks concern supplied policy fields, never authenticated hardware behavior.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
import re

from controller.stage42a_netdev_txq_and_airos6_verifier import (
    AP_AQL, _dict, _local_path, _need, _number, _queue_map, _uint, canonical_digest, read_json,
)
from controller.stage44a_champion_v15_and_ltu_beacon_verifier import (
    AP_INTERFACES, CPE_INTERFACES, SYSCTLS, STAGE44_PIN, STAGE44_SOURCE, ROUND_PINS as STAGE44_ROUND_PINS,
)

ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "T-S43B-CODEX-STAGE46A-CHAMPION-V16-TX-BIAS-2-AND-BQL-TRADEOFF-VERIFIER"
SOURCE = "artifacts/autoresearch/stage46a_m28_m29_bql_and_tx_bias_bench_20261025.json"
REPORT = "docs/STAGE46A_M28_M29_AG71XX_BQL_AND_NAPI_TX_BIAS_BENCHMARK.md"
SOURCE_PIN = "33bf3b1b7be59abb2adf680d579c0cc51bec917eec83155143f0dc2d03c2e76d"
REPORT_SHA = "be3a52f8c5499c0bdc71a2d1cdea9cf2decc53e6f05b4a73a29e98bb05a2267c"
ROUND_PINS = {
    "S46A-R1": "fc56a525d7fd75d370e93852387a10627fed76a3ea9366cfdc2c6ff0f171f041",
    "S46A-R2": "b83be6dd1d69b0823d101c49d2d85557606cec9af622db1e59cb9bf80b92e2d1",
    "S46A-R3": "7624254769640759e29f928431526b2c78c4ab99db49c8e1f29a30ababe2a178",
    "S46A-R4": "3ff7b66e9e4777d0817c71fd644c246c153b447960ab9cc419f7cf2a1e90a64b",
    "S46A-R5": "f3aae92124fd36678eac9a39712de63a0384acf597c49bc0b41e7548bdc3a113",
    "S46A-R6": "574fd7fe754601c2248bacfcf8042471fa4cdf3236cc0b5dafba10ab8073e02e",
}
PHASES = ("A1", "B1", "A2", "B2")
STREAMS = {"iptv": "iptv_dual_stream_ac_vi", "voip": "voip_stream_ac_vo"}
DYNAMIC_POLICY = {"limit_min": 0, "limit_max": 1879048192, "hold_time": 1000}
CPU_POLICY = {"LAP-120": ("MIPS74Kc_560MHz", 600), "Loco5AC": ("MIPS74Kc_560MHz", 600),
              "R5AC-Prism": ("Scorpion", 600), "LiteBeamM5": ("AR934x_400MHz", 300)}


def _finite(value):
    _need(type(value) in (int, float), "FINITE_SCALAR_REQUIRED")
    try:
        ok = math.isfinite(value)
    except OverflowError:
        ok = False
    _need(ok, "FINITE_SCALAR_REQUIRED")
    return float(value)


def _rows(document):
    rows = _dict(document).get("rounds")
    _need(type(rows) is list and len(rows) == 6, "ALL_SIX_ROUNDS_REQUIRED")
    result = {}
    for row in rows:
        row = _dict(row); ident = row.get("round_id")
        _need(type(ident) is str and ident in ROUND_PINS and ident not in result, "UNIQUE_EXPECTED_ROUND_REQUIRED")
        result[ident] = row
    return result


def source_contract(document, report_text, stage44):
    rows = _rows(document)
    for ident, pin in ROUND_PINS.items():
        _need(canonical_digest(rows[ident]) == pin, "PINNED_ROUND_DRIFT:" + ident)
    _need(canonical_digest(document) == SOURCE_PIN, "PINNED_STAGE46_ENVELOPE_DRIFT")
    _need(type(report_text) is str and hashlib.sha256(report_text.encode()).hexdigest() == REPORT_SHA,
          "PINNED_REPORT_BYTES_REQUIRED")
    _need(canonical_digest(_dict(stage44)) == STAGE44_PIN, "PINNED_STAGE44_DRIFT")
    return {"saved_objects_authenticated": True, "round_bindings": dict(ROUND_PINS),
            "stage46_canonical_sha256": SOURCE_PIN, "stage44_canonical_sha256": STAGE44_PIN,
            "report_sha256": REPORT_SHA, "native_acquisition_authenticated": False}


def audit_bql_snapshot(snapshot):
    snapshot = _dict(snapshot)
    values = {k: _uint(snapshot.get(k)) for k in ("limit_min", "limit_max", "limit", "hold_time", "inflight")}
    _need(values["limit_min"] <= values["limit_max"] and values["limit_max"] > 0,
          "ORDERED_BQL_CONFIGURATION_REQUIRED")
    inside = values["limit_min"] <= values["limit"] <= values["limit_max"]
    return {**values, "current_within_configured_bounds": inside,
            "dynamic_default_configuration": all(values[k] == v for k, v in DYNAMIC_POLICY.items()),
            "converged_same_epoch_readback_qualified": False, "native_authenticated": False}


def verify_default_dynamic_bql(snapshot):
    result = audit_bql_snapshot(snapshot)
    _need(result["dynamic_default_configuration"], "DEFAULT_CHAMPION_STATIC_BQL_CLAMP_REJECTED")
    _need(result["current_within_configured_bounds"], "CURRENT_BQL_LIMIT_OUTSIDE_CONFIGURED_BOUNDS")
    return result


def tx_bias_effect(*, dev_weight, tx_bias, driver_napi_weight):
    weight, bias, napi = (_uint(v) for v in (dev_weight, tx_bias, driver_napi_weight))
    _need(1 <= weight <= 4096 and 1 <= bias <= 64 and 1 <= napi <= 4096, "BOUNDED_POSITIVE_WEIGHT_REQUIRED")
    return {"qdisc_packet_quota": weight * bias, "driver_napi_weight": napi,
            "driver_napi_weight_scaled": False, "direct_htt_completion_multiplier_proven": False,
            "scope": "PRIMARY_LINUX_6_6_110_MECHANICS_NOT_RUNNING_BUILD_AUTHENTICATION"}


def verify_cpu_budget_ceiling(inventory):
    _need(type(inventory) is list and len(inventory) == 4, "ALL_FOUR_POLICY_ENDPOINTS_REQUIRED")
    observed = {}
    for item in inventory:
        item = _dict(item); ident = item.get("id")
        _need(type(ident) is str and ident in CPU_POLICY and ident not in observed, "UNIQUE_POLICY_ENDPOINT_REQUIRED")
        cpu_class, ceiling = CPU_POLICY[ident]
        _need(item.get("cpu_class") == cpu_class, "EXPLICIT_EXPECTED_CPU_CLASS_REQUIRED")
        budget = _uint(item.get("netdev_budget"))
        _need(0 < budget <= ceiling, "BENCH_POLICY_BUDGET_CEILING_EXCEEDED:" + ident)
        observed[ident] = {"supplied_budget": budget, "policy_ceiling": ceiling, "cpu_class": cpu_class}
    return {"endpoints": observed, "supplied_policy_consistent": True,
            "native_cpu_identity_authenticated": False, "universal_cpu_frequency_limit_proven": False}


def _fields(actual, expected, code):
    actual = _dict(actual)
    for key, value in expected.items():
        _need(_uint(actual.get(key)) == value, code + ":" + key)


def _queues(getter, prefix, inventory):
    _need(type(inventory) in (tuple, list) and inventory and all(type(k) is str for k in inventory) and
          len(set(inventory)) == len(inventory), "EXPLICIT_UNIQUE_INTERFACE_INVENTORY_REQUIRED")
    actual = _queue_map(getter.get(prefix + "_netdev_tx_queue_len"))
    _need(set(actual) == set(inventory), "COMPLETE_INTERFACE_INVENTORY_REQUIRED")
    expected = {"eth0": 1000, "br-lan": 256, "lo": 1000}
    if prefix == "ap":
        expected["phy0-ap0"] = 256
        for name in actual:
            if name.startswith("phy0-ap0.sta"):
                _need(re.fullmatch(r"phy0-ap0\.sta[1-9][0-9]*", name), "LITERAL_AP_VLAN_NAME_REQUIRED")
                expected[name] = 256
    else:
        expected.update({"br-wan": 1000, "phy0-sta0": 256})
    _need(actual == expected, "ASYMMETRIC_QUEUE_POLICY_REQUIRED")
    return actual


def verify_champion_profile(getter, *, ap_interfaces, cpe_interfaces):
    getter = _dict(getter)
    queues = {p: _queues(getter, p, inventory) for p, inventory in
              (("ap", ap_interfaces), ("cpe", cpe_interfaces))}
    for prefix in ("ap", "cpe"):
        _fields(getter.get(prefix + "_sysctl"), {**SYSCTLS, "dev_weight_tx_bias": 2}, "V16_SYSCTL_REQUIRED")
        verify_default_dynamic_bql(getter.get(prefix + "_eth0_bql"))
        _fields(getter.get(prefix + "_aqm"), {"fq_flows_cnt": 4096, "fq_memory_limit": 4194304,
                "fq_limit": 2048 if prefix == "ap" else 1024,
                "fq_quantum": 4542 if prefix == "ap" else 1514}, "BASELINE_FQ_REQUIRED")
    aql = _dict(getter.get("ap_aql_txq_limit")); _need(set(aql) == set(AP_AQL), "COMPLETE_AP_AQL_REQUIRED")
    for ac, fields in AP_AQL.items():
        _fields(aql[ac], fields, "BASELINE_AP_AQL_REQUIRED")
    rocket = _dict(getter.get("r5ac_m26_state"))
    _fields(rocket, {"br0_txqueuelen": 256, "ath0_txqueuelen": 256, "eth0_txqueuelen": 256,
                     "netdev_budget": 600, "dev_weight": 64}, "ROCKET_POLICY_REQUIRED")
    _need(rocket.get("ff_mcast_airtime_limit") == "5 " + " ".join(["0"] * 15), "ROCKET_MCAST_VECTOR_REQUIRED")
    m5 = _dict(getter.get("lbm5_m29_state"))
    _fields(m5, {"br0_txqueuelen": 256, "ath0_txqueuelen": 256, "eth0_txqueuelen": 256,
                 "netdev_budget": 300, "ewma_delegate": 1, "no_auto_prio": 0}, "M5_POLICY_REQUIRED")
    _need(m5.get("txop_params") == "0 0" and m5.get("no_ack_rate") == "0 -1", "M5_VECTOR_REQUIRED")
    return {"supplied_profile_matches": True, "queues": queues, "native_authenticated": False,
            "napi_defer_gro_readback": "UNKNOWN", "cpe_aql_and_threshold": "UNKNOWN",
            "station_airtime_getter_qualified": False, "cpu_identity": "UNKNOWN",
            "m5_exception_fallback_excluded": False, "complete_champion_qualified": False}


def audit_udp_observation(observation):
    observation = _dict(observation)
    lost, total = (_uint(observation.get(k), maximum=2**64 - 1) for k in ("lost_datagrams", "total_datagrams"))
    _need(0 < total and lost <= total, "VALID_UDP_COUNTS_REQUIRED")
    pct, jitter = _number(observation.get("packet_loss_pct")), _number(observation.get("jitter_ms"))
    _need(pct <= 100, "UDP_PERCENT_RANGE")
    raw = observation.get("raw_receiver_line")
    _need(type(raw) is str and 0 < len(raw) <= 2048, "BOUNDED_RAW_RECEIVER_REQUIRED")
    match = re.search(r"\s([0-9]+(?:\.[0-9]+)?) ms\s+([0-9]+)/([0-9]+)\s+\(([0-9]+(?:\.[0-9]+)?)%\)\s+receiver\s*$", raw)
    _need(match is not None, "COMPLETE_RAW_UDP_RECEIVER_REQUIRED")
    raw_jitter, raw_pct = _number(float(match[1])), _number(float(match[4]))
    raw_lost, raw_total = (_uint(int(match[i]), maximum=2**64 - 1) for i in (2, 3))
    _need(0 < raw_total and raw_lost <= raw_total and raw_pct <= 100, "VALID_RAW_UDP_COUNTS_REQUIRED")
    precision = len(match[4].partition(".")[2])
    tolerance = 0.5 * 10 ** (-precision) + 1e-9
    calculated_pct = 100 * lost / total
    checks = {"typed_pct_vs_counts": abs(pct - calculated_pct) <= 0.00011,
              "typed_counts_vs_raw": (lost, total) == (raw_lost, raw_total),
              "raw_pct_vs_raw_counts": abs(raw_pct - 100 * raw_lost / raw_total) <= tolerance,
              "typed_jitter_vs_raw": abs(jitter - raw_jitter) <= 0.00051}
    return {"typed": {"lost": lost, "total": total, "pct": pct, "jitter_ms": jitter},
            "raw": {"lost": raw_lost, "total": raw_total, "pct": raw_pct, "jitter_ms": raw_jitter,
                    "receiver_line": raw}, "count_loss_pct": calculated_pct, "checks": checks,
            "consistent": all(checks.values())}


def _recipe(ident, phase):
    treatment = phase.startswith("B")
    bql = dict(DYNAMIC_POLICY)
    if treatment and ident in ("S46A-R1", "S46A-R4"):
        bql = {"limit_min": 3028, "limit_max": 24576, "hold_time": 500}
    elif treatment and ident == "S46A-R5":
        bql = {"limit_min": 4542, "limit_max": 65536, "hold_time": 1000}
    return {"bql": bql, "tx_bias": 2 if treatment and ident in ("S46A-R3", "S46A-R4") else 1,
            "m5_budget": 600 if treatment and ident in ("S46A-R2", "S46A-R4", "S46A-R6") else 300}


def audit_stage46a(document):
    rows, result, discrepancies = _rows(document), [], []
    for ident in ROUND_PINS:
        row = rows[ident]; phases = _dict(row.get("phases"))
        _need(set(phases) == set(PHASES), "ALL_FOUR_PHASES_REQUIRED")
        _need(type(row.get("promoted")) is bool, "EXPLICIT_PROMOTION_BOOL_REQUIRED")
        metrics, windows = {}, {}
        for short, phase_field, report_field in (("goodput", "aggregate_goodput_mbps", "goodput_mbps"),
                ("p95", "sector_p95_rtt_ms", "p95_rtt_ms"), ("p99", "sector_p99_rtt_ms", "p99_rtt_ms")):
            a, b = (round(sum(_number(_dict(phases[arm + str(n)]).get(phase_field), positive=True)
                              for n in (1, 2)) / 2, 3) for arm in ("A", "B"))
            metrics[short] = {"control": a, "target": b, "delta_pct": round(100 * (b - a) / a, 3)}
            for arm, value in (("a", a), ("b", b)):
                reported = _number(row.get("arm_" + arm + "_mean_" + report_field), positive=True)
                if abs(value - reported) > 0.0011:
                    discrepancies.append({"round": ident, "code": "SUMMARY_MEAN_DISAGREES", "field": short,
                                          "arm": arm, "reported": reported, "recomputed": value})
        gp, p95 = metrics["goodput"], metrics["p95"]
        metrics["pareto_score_delta_pct"] = round(100 * (gp["target"] - gp["control"]) / gp["control"] -
                                                  0.35 * 100 * (p95["target"] - p95["control"]) / p95["control"], 4)
        for field, value in (("goodput_delta_pct", gp["delta_pct"]), ("p95_rtt_delta_pct", p95["delta_pct"]),
                             ("pareto_score_delta_pct", metrics["pareto_score_delta_pct"])):
            reported = _finite(row.get(field))
            if abs(reported - value) > 0.0011:
                discrepancies.append({"round": ident, "code": "SUMMARY_DELTA_DISAGREES", "field": field,
                                      "reported": reported, "recomputed": value})
        for phase in PHASES:
            item = _dict(phases[phase]); getter = _dict(item.get("getter_readback")); recipe = _recipe(ident, phase)
            udp = {name: audit_udp_observation(item.get(field)) for name, field in STREAMS.items()}
            for name, value in udp.items():
                for check, ok in value["checks"].items():
                    if not ok:
                        discrepancies.append({"round": ident, "phase": phase, "stream": name,
                                              "code": "UDP_LAYER_DISAGREEMENT", "check": check})
            bql = {}
            for prefix in ("ap", "cpe"):
                bql[prefix] = audit_bql_snapshot(getter.get(prefix + "_eth0_bql"))
                _fields(getter[prefix + "_eth0_bql"], recipe["bql"], "DECLARED_ROUND_BQL_RECIPE_MISMATCH")
                _fields(getter.get(prefix + "_sysctl"), {"dev_weight_tx_bias": recipe["tx_bias"],
                        "netdev_budget": 600, "netdev_budget_usecs": 20000}, "DECLARED_ROUND_NAPI_RECIPE_MISMATCH")
                if not bql[prefix]["current_within_configured_bounds"]:
                    discrepancies.append({"round": ident, "phase": phase, "endpoint": prefix,
                                          "code": "BQL_CURRENT_OUTSIDE_CONFIGURED_BOUNDS"})
            _fields(getter.get("lbm5_m29_state"), {"netdev_budget": recipe["m5_budget"]}, "M5_ROUND_BUDGET_MISMATCH")
            windows[phase] = {"udp": udp, "bql": bql, "declared_recipe": recipe}
        for stream in STREAMS:
            layers = {}
            for arm in ("A", "B"):
                observations = [windows[arm + str(n)]["udp"][stream] for n in (1, 2)]
                typed_mean = round(sum(x["typed"]["jitter_ms"] for x in observations) / 2, 3)
                raw_mean = round(sum(x["raw"]["jitter_ms"] for x in observations) / 2, 3)
                total, lost = (sum(x["typed"][k] for x in observations) for k in ("total", "lost"))
                layers[arm] = {"typed_mean_jitter_ms": typed_mean, "raw_mean_jitter_ms": raw_mean,
                               "mean_typed_pct": round(sum(x["typed"]["pct"] for x in observations) / 2, 4),
                               "lost": lost, "total": total, "pooled_count_loss_pct": 100 * lost / total}
                for field, calculated in (("jitter_ms", typed_mean), ("loss_pct", layers[arm]["mean_typed_pct"])):
                    key = stream + "_arm_" + arm.lower() + "_mean_" + field
                    reported = _number(row.get(key))
                    if abs(reported - calculated) > (0.0011 if field == "jitter_ms" else 0.00011):
                        discrepancies.append({"round": ident, "code": "UDP_SUMMARY_MEAN_DISAGREES", "field": key,
                                              "reported": reported, "recomputed": calculated})
            a, b = layers["A"], layers["B"]
            _need(a["typed_mean_jitter_ms"] > 0 and a["raw_mean_jitter_ms"] > 0, "POSITIVE_CONTROL_JITTER_REQUIRED")
            layers["typed_jitter_delta_pct"] = round(100 * (b["typed_mean_jitter_ms"] - a["typed_mean_jitter_ms"]) / a["typed_mean_jitter_ms"], 3)
            layers["raw_jitter_delta_pct"] = round(100 * (b["raw_mean_jitter_ms"] - a["raw_mean_jitter_ms"]) / a["raw_mean_jitter_ms"], 3)
            layers["reported_jitter_delta_pct"] = _finite(row.get(stream + "_jitter_delta_pct"))
            if abs(layers["reported_jitter_delta_pct"] - layers["typed_jitter_delta_pct"]) > 0.0011:
                discrepancies.append({"round": ident, "code": "UDP_SUMMARY_DELTA_DISAGREES", "stream": stream})
            metrics[stream] = layers
        result.append({"round_id": ident, "reported_decision": row.get("decision"), "reported_promoted": row["promoted"],
                       "metrics": metrics, "windows": windows})
    profiles = {phase: verify_champion_profile(rows["S46A-R3"]["phases"][phase]["getter_readback"],
                ap_interfaces=AP_INTERFACES, cpe_interfaces=CPE_INTERFACES) for phase in ("B1", "B2")}
    return {"rounds": result, "windows": 24, "udp_observations": 48, "discrepancies": discrepancies,
            "research_evidence_status": "INCONSISTENT_SAVED_EVIDENCE" if discrepancies else "SAVED_FIELDS_CONSISTENT_NOT_NATIVE_AUTHENTICATED",
            "champion": {"reported_version": 16, "reported_promoted_round": "S46A-R3", "supplied_profiles": profiles,
                         "native_promotion_accepted": False, "raw_qoe_qualified": False}}


def compare_stage44a(stage46, stage44):
    _need(canonical_digest(_dict(stage44)) == STAGE44_PIN, "PINNED_STAGE44_DRIFT")
    rows46 = _rows(stage46); rows44 = {r["round_id"]: r for r in stage44["rounds"]}
    contrasts = {}
    for ident in ("S44A-R3", "S44A-R4"):
        row = rows44[ident]
        _need(canonical_digest(row) == STAGE44_ROUND_PINS[ident], "PINNED_STAGE44_ROUND_DRIFT")
        contrasts[ident] = {"reported_goodput_delta_pct": row["goodput_delta_pct"],
                           "reported_p95_delta_pct": row["p95_rtt_delta_pct"],
                           "declared_time_slice_us": 8000 if ident == "S44A-R3" else 12000,
                           "declared_time_slice_matches_getter": False,
                           "ap_treatment_sysctl": row["phases"]["B1"]["getter_readback"]["ap_sysctl"],
                           "ap_treatment_sysctl_B2": row["phases"]["B2"]["getter_readback"]["ap_sysctl"],
                           "ap_treatment_eth0_txq": row["phases"]["B1"]["getter_readback"]["ap_netdev_tx_queue_len"]["eth0"]}
    return {"prior_rounds": contrasts, "stage46_reported_promotion": rows46["S46A-R3"]["promoted"],
            "changed_budget_time_slice_or_eth0_are_confounders": True,
            "isolated_cross_round_causal_explanation_proven": False,
            "tx_bias_doubles_driver_htt_napi_weight": "REFUTED_FOR_PRIMARY_LINUX_6_6_110",
            "native_qdisc_or_aql_causal_benefit": "UNKNOWN"}


def audit_saved_sources(root=ROOT):
    root = _local_path(root)
    document, stage44 = read_json(root / SOURCE), read_json(root / STAGE44_SOURCE)
    path = _local_path(root / REPORT); _need(path.stat().st_size <= 250000, "BOUNDED_LOCAL_REPORT_REQUIRED")
    raw = path.read_bytes(); _need(len(raw) <= 250000, "BOUNDED_LOCAL_REPORT_REQUIRED")
    contract = source_contract(document, raw.decode("utf-8"), stage44)
    return {"task_id": TASK_ID, "source_contract": contract, "stage46a": audit_stage46a(document),
            "stage44_comparison": compare_stage44a(document, stage44),
            "boundaries": {"offline_only": True, "native_dispatch_allowed": False, "ssh": False,
                           "hardware_access": False, "physical_acceptance": "UNKNOWN", "e2": "NOT_ACCEPTED"}}
