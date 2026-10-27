"""Stage41B: saved-evidence audit and pure, review-only LTU preflight.

No SSH, loader, subprocess, device path or native callback is implemented.
Supplied getters prove internal consistency only, never native authenticity.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import unicodedata

from controller.stage42a_netdev_txq_and_airos6_verifier import (
    AP_AQL, _dict, _local_path, _need, _number, _queue_map, _uint,
    canonical_digest, read_json,
)

ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "T-S41B-CODEX-STAGE44A-CHAMPION-V15-AND-STAGE43A-LTU-INTMODE1-VERIFIER"
STAGE44_SOURCE = "artifacts/autoresearch/stage44a_m26_m27_napi_and_r5ac_txq_bench_20261025.json"
STAGE43_SOURCE = "artifacts/autoresearch/stage43a_ltu_rocket_ram_module_injection_20261025.json"
PHASES = ("A1", "B1", "A2", "B2")
ROUND_PINS = {
    "S44A-R1": "df9d67092974d4ce5d2aeb6d1e7032c529c14820915a31a87665622ab672ade9",
    "S44A-R2": "6035781a56da19b1b46f5913e0a32d97ceecbdde51ce3869b33acfe47a345907",
    "S44A-R3": "2f1bdde2f7a124c19de2a645cd93696bf8b913bb33d86e1756c1ef1b0a1818f3",
    "S44A-R4": "41934234df98e04383c4eae221846c9540124bc0138020fff8c7a9a4e88ccbf8",
    "S44A-R5": "cd827aafa15f227a5fe30ae7dac5c468920408055bbf5df75efffbedb86a9606",
}
STAGE43_PIN = "c5443bb806b6d229fea5ddba22068951b414edcd121f98af11464521e59dc820"
STAGE44_PIN = "67c803852ee7a10b111a13b5536115eb8263249b944310afb22506b7dc475ee6"
SYSCTLS = {"netdev_max_backlog": 1000, "dev_weight": 64, "dev_weight_rx_bias": 1,
           "dev_weight_tx_bias": 1, "netdev_budget": 600, "netdev_budget_usecs": 20000,
           "tcp_early_retrans": 3, "tcp_limit_output_bytes": 98304,
           "tcp_notsent_lowat": 8192, "tcp_pacing_ca_ratio": 105, "tcp_pacing_ss_ratio": 140}
AP_INTERFACES = ("br-lan", "eth0", "lo", "phy0-ap0", "phy0-ap0.sta1", "phy0-ap0.sta2")
CPE_INTERFACES = ("br-lan", "br-wan", "eth0", "lo", "phy0-sta0")
_HASH = re.compile(r"[0-9a-f]{64}")


def _rounds(document):
    rows = _dict(document).get("rounds")
    _need(type(rows) is list and len(rows) == 5, "ALL_FIVE_STAGE44_ROUNDS_REQUIRED")
    result = {}
    for row in rows:
        row = _dict(row)
        ident = row.get("round_id")
        _need(type(ident) is str and ident in ROUND_PINS and ident not in result,
              "UNIQUE_EXPECTED_ROUND_REQUIRED")
        result[ident] = row
    return result


def source_contract(stage44, stage43):
    rows = _rounds(stage44)
    for ident, pin in ROUND_PINS.items():
        _need(canonical_digest(rows[ident]) == pin, "PINNED_ROUND_DRIFT:" + ident)
    _need(canonical_digest(stage44) == STAGE44_PIN, "PINNED_STAGE44_ENVELOPE_DRIFT")
    _need(canonical_digest(_dict(stage43)) == STAGE43_PIN, "PINNED_STAGE43_DRIFT")
    return {"source_authenticated": True, "round_bindings": dict(ROUND_PINS),
            "stage43_binding": STAGE43_PIN, "stage44_binding": STAGE44_PIN,
            "authentication_scope": "CANONICAL_SAVED_OBJECTS_NOT_NATIVE_ACQUISITION"}


def _exact_uint_fields(actual, expected, code):
    actual = _dict(actual)
    for key, value in expected.items():
        _need(_uint(actual.get(key)) == value, code + ":" + key)


def _netdev_profile(getter, prefix, inventory):
    _need(type(inventory) in (tuple, list) and inventory and
          all(type(n) is str for n in inventory) and len(set(inventory)) == len(inventory),
          "EXPLICIT_UNIQUE_INTERFACE_INVENTORY_REQUIRED")
    actual = _queue_map(getter.get(prefix + "_netdev_tx_queue_len"))
    _need(set(actual) == set(inventory), "COMPLETE_INTERFACE_INVENTORY_REQUIRED")
    base = {"br-lan": 256, "eth0": 1000, "lo": 1000}
    if prefix == "ap":
        base["phy0-ap0"] = 256
        for name in actual:
            if name.startswith("phy0-ap0.sta"):
                _need(re.fullmatch(r"phy0-ap0\.sta[1-9][0-9]*", name) is not None,
                      "LITERAL_AP_VLAN_NAME_REQUIRED")
                base[name] = 256
    else:
        base.update({"br-wan": 1000, "phy0-sta0": 256})
    _need(actual == base, "ASYMMETRIC_TXQ_PROFILE_MISMATCH:" + prefix)
    for suffix in ("_napi_defer_hard_irqs", "_gro_flush_timeout_ns"):
        observed = _queue_map(getter.get(prefix + suffix))
        _need(set(observed) == set(actual) and all(v == 0 for v in observed.values()),
              "BASELINE_NAPI_REQUIRED:" + prefix + suffix)
    _exact_uint_fields(getter.get(prefix + "_sysctl"), SYSCTLS, "BASELINE_SYSCTL_REQUIRED")
    _exact_uint_fields(getter.get(prefix + "_aqm"),
        {"fq_flows_cnt": 4096, "fq_memory_limit": 4194304,
         "fq_limit": 2048 if prefix == "ap" else 1024,
         "fq_quantum": 4542 if prefix == "ap" else 1514}, "BASELINE_FQ_REQUIRED")
    return actual


def verify_asymmetric_profile(getter, *, ap_interfaces, cpe_interfaces):
    """Validate supplied v15 fields; driver/BQL and complete champion stay unknown."""
    getter = _dict(getter)
    ap = _netdev_profile(getter, "ap", ap_interfaces)
    cpe = _netdev_profile(getter, "cpe", cpe_interfaces)
    aql = _dict(getter.get("ap_aql_txq_limit"))
    _need(set(aql) == set(AP_AQL), "COMPLETE_AP_AQL_REQUIRED")
    for ac, thresholds in AP_AQL.items():
        _exact_uint_fields(aql[ac], thresholds, "BASELINE_AP_AQL_REQUIRED")
    rocket = _dict(getter.get("r5ac_m26_state"))
    _exact_uint_fields(rocket, {"br0_txqueuelen": 256, "ath0_txqueuelen": 256,
        "eth0_txqueuelen": 256, "netdev_budget": 600, "dev_weight": 64}, "AIROS8_R5AC_REQUIRED")
    _need(rocket.get("ff_mcast_airtime_limit") == "5 " + " ".join(["0"] * 15),
          "R5AC_MULTICAST_BASELINE_REQUIRED")
    m5 = _dict(getter.get("lbm5_m24_state"))
    _exact_uint_fields(m5, {"br0_txqueuelen": 256, "ath0_txqueuelen": 256,
        "eth0_txqueuelen": 256, "ewma_delegate": 1, "no_auto_prio": 0}, "M5_BASELINE_REQUIRED")
    _need(m5.get("txop_params") == "0 0" and m5.get("no_ack_rate") == "0 -1",
          "M5_BASELINE_VECTOR_REQUIRED")
    return {"profile_matches": True, "ap_queues": ap, "cpe_queues": cpe,
            "driver_bql_status": "UNKNOWN", "cpe_aql_status": "UNKNOWN",
            "station_airtime_weights_status": "UNKNOWN", "native_authenticated": False,
            "complete_champion_qualified": False}


def validate_bql_evidence(evidence):
    """BQL is dynamic Linux byte accounting, not a fixed 54250/1780 target."""
    evidence = _dict(evidence)
    _need(evidence.get("driver") == "ag71xx" and evidence.get("interface") == "eth0",
          "EXACT_AG71XX_ETH0_EVIDENCE_REQUIRED")
    queues = _dict(evidence.get("queues"))
    _need(0 < len(queues) <= 64 and all(type(q) is str and re.fullmatch(r"tx-[0-9]+", q)
              for q in queues), "EXPLICIT_BQL_QUEUE_INVENTORY_REQUIRED")
    inventory = evidence.get("expected_queues")
    _need(type(inventory) is list and len(inventory) == len(queues) and
          all(type(q) is str for q in inventory) and set(inventory) == set(queues),
          "COMPLETE_DECLARED_BQL_QUEUE_INVENTORY_REQUIRED")
    for queue in queues.values():
        queue = _dict(queue)
        low, limit, high = (_uint(queue.get(k)) for k in ("limit_min", "limit", "limit_max"))
        _need(low <= limit <= high and high > 0, "DYNAMIC_BQL_LIMIT_BOUNDS_REQUIRED")
    return {"supplied_evidence_consistent": True, "native_authenticated": False,
            "hardware_offload_proven": False, "bql_causality": "UNKNOWN"}


def _udp_view(observation):
    observation = _dict(observation)
    lost, total = (_uint(observation.get(k), maximum=2**64 - 1)
                   for k in ("lost_datagrams", "total_datagrams"))
    _need(0 < total and lost <= total, "VALID_UDP_DENOMINATOR_REQUIRED")
    pct = _number(observation.get("packet_loss_pct"))
    _need(pct <= 100 and abs(pct - 100 * lost / total) <= 0.00011, "UDP_PERCENT_MISMATCH")
    raw = observation.get("raw_receiver_line")
    _need(type(raw) is str and len(raw) <= 2048, "RAW_UDP_RECEIVER_REQUIRED")
    matches = re.findall(r"\b([0-9]+)/([0-9]+)\s+\(([0-9]+(?:\.[0-9]+)?)%\)\s+receiver\s*$", raw)
    _need(len(matches) == 1 and tuple(map(int, matches[0][:2])) == (lost, total),
          "RAW_UDP_COUNTS_MISMATCH")
    _need(abs(float(matches[0][2]) - pct) <= 0.051, "RAW_UDP_PERCENT_MISMATCH")
    return {"lost": lost, "total": total, "reported_pct": pct,
            "jitter_ms": _number(observation.get("jitter_ms")), "raw_receiver_line": raw}


def audit_stage44a(document):
    rows, results = _rounds(document), []
    for ident in ROUND_PINS:
        row = rows[ident]
        phases = _dict(row.get("phases"))
        _need(set(phases) == set(PHASES), "ALL_FOUR_PHASES_REQUIRED")
        recomputed = {}
        for short, field in (("goodput", "aggregate_goodput_mbps"),
                             ("p95", "sector_p95_rtt_ms"), ("p99", "sector_p99_rtt_ms")):
            a, b = (round(sum(_number(_dict(phases[arm + str(n)]).get(field), positive=True)
                              for n in (1, 2)) / 2, 3) for arm in ("A", "B"))
            recomputed[short] = {"control": a, "target": b, "delta_pct": round(100 * (b - a) / a, 3)}
        udp = {phase: {"iptv": _udp_view(_dict(phases[phase]).get("iptv_dual_stream_ac_vi")),
                       "voip": _udp_view(_dict(phases[phase]).get("voip_stream_ac_vo"))}
               for phase in PHASES}
        _need(type(row.get("promoted")) is bool, "EXPLICIT_PROMOTION_BOOL_REQUIRED")
        for short, field in (("goodput", "goodput_delta_pct"), ("p95", "p95_rtt_delta_pct")):
            observed = row.get(field)
            _need(type(observed) in (int, float) and abs(observed - recomputed[short]["delta_pct"]) <= 0.0011,
                  "RECOMPUTED_METRIC_MISMATCH:" + ident + ":" + field)
        gp, p95 = recomputed["goodput"], recomputed["p95"]
        pareto = round(100 * (gp["target"] - gp["control"]) / gp["control"] -
                       0.35 * 100 * (p95["target"] - p95["control"]) / p95["control"], 4)
        _need(type(row.get("pareto_score_delta_pct")) in (int, float) and
              abs(row["pareto_score_delta_pct"] - pareto) <= 0.00011,
              "RECOMPUTED_PARETO_MISMATCH:" + ident)
        recomputed["pareto_score_delta_pct"] = pareto
        for stream, report_key in (("iptv", "iptv_jitter_delta_pct"), ("voip", "voip_jitter_delta_pct")):
            a, b = (round(sum(udp[arm + str(n)][stream]["jitter_ms"] for n in (1, 2)) / 2, 3)
                    for arm in ("A", "B"))
            _need(a > 0, "POSITIVE_CONTROL_JITTER_REQUIRED")
            jitter_delta = round(100 * (b - a) / a, 3)
            _need(type(row.get(report_key)) in (int, float) and
                  abs(row[report_key] - jitter_delta) <= 0.0011,
                  "RECOMPUTED_JITTER_MISMATCH:" + ident)
            recomputed[stream + "_jitter"] = {"control": a, "target": b, "delta_pct": jitter_delta}
        results.append({"round_id": ident, "reported_decision": row.get("decision"),
            "promoted": row["promoted"], "recomputed": recomputed, "udp_windows": udp,
            "reported_pareto_score_delta_pct": row.get("pareto_score_delta_pct"),
            "reported_iptv_jitter_delta_pct": row.get("iptv_jitter_delta_pct"),
            "reported_voip_jitter_delta_pct": row.get("voip_jitter_delta_pct")})
    r5 = rows["S44A-R5"]
    profiles = {phase: verify_asymmetric_profile(r5["phases"][phase]["getter_readback"],
        ap_interfaces=AP_INTERFACES, cpe_interfaces=CPE_INTERFACES) for phase in ("B1", "B2")}
    return {"rounds": results, "windows": 20,
            "champion": {"round_id": "S44A-R5", "reported_version": 15,
                "reported_promotion": r5["promoted"], "profiles": profiles,
                "bql_causal_explanation": "INFERRED_NOT_ISOLATED",
                "universal_txq_rule_proven": False, "new_hardware_measurement": False,
                "raw_latency_samples_available": False, "complete_champion_qualified": False}}


def validate_ssid(ssid):
    """Count C-string payload bytes, never characters, truncation or normalization."""
    _need(type(ssid) is str and 0 < len(ssid) <= 16, "SSID_1_TO_16_UTF8_BYTES_REQUIRED")
    _need(not any(unicodedata.category(char).startswith("C") or char in "\u2028\u2029"
                  for char in ssid), "SSID_CONTROL_OR_SURROGATE_NOT_ALLOWED")
    encoded = ssid.encode("utf-8", errors="strict")
    _need(1 <= len(encoded) <= 16, "SSID_1_TO_16_UTF8_BYTES_REQUIRED")
    return encoded


def _identity(evidence):
    evidence = _dict(evidence)
    for key in ("device_id", "boot_id"):
        value = evidence.get(key)
        _need(type(value) is str and 0 < len(value) <= 128 and
              all(32 <= ord(c) <= 126 for c in value), "STABLE_IDENTITY_REQUIRED:" + key)
    for key in ("module_sha256", "evidence_sha256"):
        value = evidence.get(key)
        _need(type(value) is str and _HASH.fullmatch(value), "EXPLICIT_SHA256_REQUIRED:" + key)
    return tuple(evidence[k] for k in ("device_id", "boot_id", "module_sha256"))


def verify_ltu_readback(evidence):
    evidence = _dict(evidence)
    _identity(evidence)
    _need(_uint(evidence.get("board_ssid")) == 0xAE08, "BOARD_SSID_AE08_REQUIRED")
    _need(_uint(evidence.get("intmode")) == 1, "INTMODE_ONE_REQUIRED")
    _need(evidence.get("irq_gpio") == "GPIO_8" and evidence.get("irq_registered") is True,
          "GPIO8_REGISTERED_IRQ_EVIDENCE_REQUIRED")
    return {"supplied_readback_consistent": True, "native_authenticated": False,
            "board_ssid": 0xAE08, "intmode": 1, "irq_gpio": "GPIO_8"}


def verify_alternating_dcxo(samples, *, declared_frequencies, expected_identity):
    """Check an explicitly supplied ABAB recipe; this does not run calibration."""
    _need(type(declared_frequencies) in (tuple, list) and len(declared_frequencies) == 2,
          "TWO_PREDECLARED_FREQUENCIES_REQUIRED")
    frequencies = tuple(_uint(f, maximum=10000) for f in declared_frequencies)
    _need(all(f > 0 for f in frequencies) and frequencies[0] != frequencies[1],
          "TWO_DISTINCT_POSITIVE_FREQUENCIES_REQUIRED")
    _need(type(samples) is list and 4 <= len(samples) <= 64 and len(samples) % 2 == 0,
          "BOUNDED_COMPLETE_ABAB_CALIBRATION_REQUIRED")
    identity, previous = _identity(expected_identity), -1
    for index, sample in enumerate(samples):
        sample = _dict(sample)
        _need(_identity(sample) == identity, "SAME_DEVICE_BOOT_MODULE_REQUIRED")
        _need(_uint(sample.get("sequence")) == index, "ORDERED_CALIBRATION_SEQUENCE_REQUIRED")
        stamp = _uint(sample.get("monotonic_ns"), maximum=2**64 - 1)
        _need(stamp > previous, "STRICT_CALIBRATION_TIMESTAMPS_REQUIRED")
        previous = stamp
        frequency = frequencies[index % 2]
        _need(_uint(sample.get("frequency_mhz")) == frequency, "ALTERNATING_FREQUENCY_REQUIRED")
        freq_list = sample.get("freq_list")
        _need(type(freq_list) is list and len(freq_list) == 4 and
              all(_uint(f) == frequency for f in freq_list), "COMPLETE_FREQ_LIST_READBACK_REQUIRED")
        _need(sample.get("crystal_locked") is True and sample.get("calibration_complete") is True,
              "CRYSTAL_LOCK_AND_DCXO_COMPLETION_REQUIRED")
        # A locked/calibrated oscillator need not change its numeric control code.
        for key in ("dcxo_before", "dcxo_after"):
            _number(sample.get(key))
    return {"calibration_samples": len(samples), "last_frequency_mhz": frequencies[-1],
            "supplied_evidence_consistent": True, "native_authenticated": False}


def prepare_ini_candidate(ssid, *, readback, calibration_samples, declared_frequencies):
    """Validate first, then return a sealed fragment for offline review only.

    This is not a complete ame.ini nor a native loader. No existing runner is
    modified; 16 bytes do not prove the vendor buffer's terminator semantics.
    """
    encoded = validate_ssid(ssid)  # Must precede readback handling or payload creation.
    _need(not any(c in ssid for c in "=;#\"'\\[]"), "AMBIGUOUS_INI_SSID_NOT_ALLOWED")
    readback_result = verify_ltu_readback(readback)
    calibration = verify_alternating_dcxo(calibration_samples,
        declared_frequencies=declared_frequencies, expected_identity=readback)
    # Syntax is a conservative review fragment, not an assertion about ame.ini ABI.
    payload = b"ssid=" + encoded + b"\n"
    return {"payload_utf8": payload, "payload_sha256": hashlib.sha256(payload).hexdigest(),
            "ssid_bytes": len(encoded), "readback": readback_result, "calibration": calibration,
            "evidence_binding": canonical_digest({"readback": readback,
                "samples": calibration_samples, "frequencies": list(declared_frequencies)}),
            "native_dispatch_allowed": False, "complete_native_ini": False,
            "native_buffer_termination_qualified": False}


def audit_stage43a(document):
    document = _dict(document)
    tests = {}
    for key in ("test1_rocket_ame_core_intmode1", "test2_ltu_ame_core_intmode1"):
        item = _dict(document.get(key))
        common, dmesg = item.get("common_info"), item.get("dmesg_excerpt")
        _need(type(common) is str and type(dmesg) is str, "SAVED_COMMON_AND_DMESG_REQUIRED")
        ssids = re.findall(r"^SSID:(.*?) Security:", common, flags=re.M)
        counts = re.findall(r"^Stations count: ([0-9]+)$", common, flags=re.M)
        _need(len(ssids) == len(counts) == 1, "UNAMBIGUOUS_SAVED_SSID_AND_STATIONS_REQUIRED")
        tests[key] = {"reported_ssid": ssids[0], "reported_ssid_bytes": len(validate_ssid(ssids[0])),
            "stations": int(counts[0]), "board_ae08_in_excerpt": "Board SSID(0xae08)" in dmesg,
            "crystal_5500_in_excerpt": "Crystal Locked at Freq[5500]" in dmesg,
            "intmode_getter": "UNKNOWN", "gpio8_irq": "UNKNOWN",
            "alternating_freq_list_dcxo": "UNKNOWN", "native_module_identity": "UNKNOWN"}
    final = _dict(document.get("final_active_state_on_ltu1"))
    return {"tests": tests, "final_remote_info": final.get("remote_info"),
            "final_ping": final.get("ping_192_168_100_111"), "ota_link_qualified": False,
            "native_ini_admitted": False, "original_input_ssid_available": False,
            "producer_0x007008_consumer_0x045e20_instruction_proof": "UNKNOWN",
            "ssid_policy_bytes": 16, "native_buffer_termination_qualified": False,
            "abi_compatibility_from_vermagic_proven": False,
            "test2_fallback_and_stale_log_ambiguity": True,
            "patched_success_return_proves_hardware_success": False}


def audit_saved_sources(root=ROOT):
    root = _local_path(root)
    stage44, stage43 = read_json(root / STAGE44_SOURCE), read_json(root / STAGE43_SOURCE)
    contract = source_contract(stage44, stage43)
    audit44 = audit_stage44a(stage44)
    return {"task_id": TASK_ID, "source_contract": contract,
            "windows": audit44["windows"], "rounds": audit44["rounds"],
            "champion": audit44["champion"], "ltu": audit_stage43a(stage43),
            "boundaries": {"offline_only": True, "ssh": False, "hardware_access": False,
                "native_dispatch_allowed": False, "physical_acceptance": "UNKNOWN",
                "e2": "NOT_ACCEPTED"}}
