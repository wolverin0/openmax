"""Stage46B: pure saved Stage50B audit; successful export is not native proof."""
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
    _dict, _local_path, _need, _number, _uint, canonical_digest, read_json,
)
from controller.stage48b_ltu_ota_triple_play_and_loop_flee_verifier import audit_progress_receipt

ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "T-S46B-CODEX-STAGE50B-LTU-HYBRID-SWQ-AND-MAXBD-OTA-VERIFIER"
SOURCE = "artifacts/autoresearch/stage50b_ltu_hybrid_swq_and_mcs_ceiling_ota_bench_20261025.json"
REPORT = "docs/STAGE50B_LTU_HYBRID_SWQ_AND_MCS_CEILING_OTA_BENCHMARK.md"
OUTPUT = "artifacts/autoresearch/stage46b_ltu_hybrid_swq_and_maxbd_audit_20261025.json"
SOURCE_PIN = "bd8a356d2d7cf78ab02e1c3808dd75aad67c079306f8c4f9694f84f70ae03fca"
REPORT_SHA = "092161b50d2b50f1511bc34d41f58d3448d1474c924640480262ff609ee2e3cd"
PROFILES = ("S50B-R0-STAGE49B-BASELINE", "S50B-R1-HYBRID-AUTOMCS-19-256QAM-8X",
            "S50B-R2-HYBRID-AUTOMCS-15-64QAM-6X-SWQ2")
TRIAL_ORDER = tuple((PROFILES[(i + rep - 1) % 3], rep) for rep in range(1, 4) for i in range(3))
TRIAL_PINS = dict(zip(TRIAL_ORDER, (
    "457d1cf7791cb4be4cfbd5bb0a362c6017bce5ea13cc20cea5c8e0bed47bb3d0",
    "29d850bae8186c59b48fcd9820be215e1f5f781d2e6f0574cd62aa1bcdd32e64",
    "26982f79a96e42c00ecc0713434d9329c62e926a80da13de3f05b4589ef9d66c",
    "8fae3223f5e48d0b01ed6cac07db42227873826e78914e6a05e203165bb929aa",
    "61f482f7e501b3e6305580fa396533ebdcfa8e98d5986c0136edfc0cd0d39651",
    "de8652001fc14c10971bf87f546e1afafbd97ba251d325285fee54944cc6749d",
    "95a29760b66623359c6859cbd48934a7853aa89e1265cbfa11d5cbe5e3096d7b",
    "144524d23f60549405be5012357cc2e98ced1c046f4bd6765fc400908dbfd3d6",
    "3fbc1c62879f0ede8021baa82e6a346840fda0681365ddd79d90243dd177159a")))
MCS_LABELS = {7: "QPSKl", 11: "16Ql", 15: "64Ql", 19: "256Ql", 23: "1024Ql", 31: "4096l"}
CEILINGS = dict(zip(PROFILES, (23, 19, 15)))
MEANS = ("bulk_tcp_mbps", "iptv_udp_mbps", "iptv_jitter_ms", "iptv_loss_pct", "voip_jitter_ms",
         "voip_loss_pct", "loaded_ping_p50_ms", "loaded_ping_p95_ms", "loaded_ping_p99_ms")


def _value(value):
    value = _number(value)
    _need(value <= 1e12, "BOUNDED_MEASUREMENT_REQUIRED")
    return value


def _mean(values):
    return round(statistics.mean(values), 3)


def _delta(control, target):
    _need(control > 0, "POSITIVE_BASELINE_DENOMINATOR_REQUIRED")
    value = 100 * (target - control) / control
    _need(math.isfinite(value), "FINITE_DELTA_REQUIRED")
    return round(value, 4)


def _trials(document):
    items = _dict(document).get("trials")
    _need(type(items) is list and len(items) == 9, "ALL_NINE_TRIALS_REQUIRED")
    result = {}
    for item in items:
        item = _dict(item); profile, rep = item.get("profile_id"), _uint(item.get("rep"))
        _need(type(profile) is str and profile in PROFILES and 1 <= rep <= 3 and
              (profile, rep) not in result, "UNIQUE_EXPECTED_PROFILE_REP_REQUIRED")
        result[profile, rep] = item
    return result


def source_contract(document, report_text):
    trials = _trials(document)
    for key, pin in TRIAL_PINS.items():
        _need(canonical_digest(trials[key]) == pin, "PINNED_TRIAL_DRIFT:" + str(key))
    _need(canonical_digest(document) == SOURCE_PIN, "PINNED_SOURCE_ENVELOPE_DRIFT")
    _need(type(report_text) is str and hashlib.sha256(report_text.encode()).hexdigest() == REPORT_SHA,
          "PINNED_REPORT_BYTES_REQUIRED")
    return {"saved_objects_authenticated": True, "source_canonical_sha256": SOURCE_PIN, "report_raw_sha256": REPORT_SHA,
            "trial_bindings": [{"profile_id": p, "rep": r, "canonical_sha256": h} for (p, r), h in TRIAL_PINS.items()],
            "native_acquisition_authenticated": False}


def verify_cpe_mcs_contract(*, cpe_id, mcs_level, opcode):
    """Stage50B's declared contract, intentionally distinct from Stage49B's claim."""
    peer, level, operation = (_uint(v) for v in (cpe_id, mcs_level, opcode))
    _need(peer == 0 and operation in (0, 2), "STAGE50B_PEER_ZERO_DL_UL_AUTO_OPCODE_REQUIRED")
    _need(level in MCS_LABELS, "STAGE50B_DISCRETE_CEILING_REQUIRED_32_REJECTED")
    return {"cpe_id": peer, "mcs_level": level, "opcode": operation, "reported_label": MCS_LABELS[level],
            "supplied_stage50b_contract_consistent": True, "native_abi_authenticated": False,
            "conflicts_with_stage49b_sentinel32_claim": True}


def audit_maxbd(text):
    _need(type(text) is str and re.fullmatch(r"0x[0-9a-fA-F]{1,8}", text) is not None, "BOUNDED_MAXBD_HEX_REQUIRED")
    value = _uint(int(text, 16))
    return {"raw": text, "value": value, "in_reported_5_to_10_range": 5 <= value <= 10,
            "native_eab_high_water_semantics_authenticated": False, "reset_epoch_and_success_proven": False,
            "hard_cap_or_instantaneous_occupancy_proven": False}


def audit_bler_snapshot(text):
    _need(type(text) is str and 0 < len(text) <= 8192, "BOUNDED_BLER_SNAPSHOT_REQUIRED")
    pattern = (r"frag size ([0-9]+) bytes\s*\n\s*%\s+Correct\s+Total\s*:\s*bps\s*\n\s*"
               r"([0-9]{1,3})\s+([0-9a-fA-F]{1,16})\s+([0-9a-fA-F]{1,16})\s*:\s*"
               r"([0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)\s*")
    match = re.fullmatch(pattern, text)
    _need(match is not None, "COMPLETE_SINGLE_ROW_BLER_SNAPSHOT_REQUIRED")
    size, displayed = _uint(int(match[1])), _uint(int(match[2]), maximum=100)
    correct, total = (_uint(int(match[i], 16), maximum=2**53 - 1) for i in (3, 4))
    _need(0 < size <= 65536 and 0 < total and correct <= total, "VALID_FRAGMENT_COUNTS_REQUIRED")
    bps = _value(float(match[5])); ratio = 100 * correct / total
    return {"raw": text, "fragment_bytes": size, "displayed_percent": displayed, "correct": correct, "total": total,
            "correct_over_total_pct": ratio, "reported_bps": bps,
            "display_matches_floor_correct_ratio": displayed == math.floor(ratio),
            "bps_matches_correct_times_fragment_bits": math.isclose(bps, correct * size * 8, rel_tol=1e-9, abs_tol=1e-6),
            "display_is_authenticated_bler_or_packet_loss": False, "counter_reset_interval_and_rf_cause_proven": False}


def _apply_readback(meta, expected_label):
    meta = _dict(meta); text = meta.get("ap_apply_out")
    _need(type(text) is str and 0 < len(text) <= 8192, "BOUNDED_APPLY_READBACK_REQUIRED")
    match = re.fullmatch(r"(OTA_OK|OTA_FAIL)\n1 \(0:OFF, 1:ON, 2:AUTO\) gain:0x([0-9a-fA-F]+)\n"
                         r"(1024qam \(10x\)|256qam \(8x\)|64qam \(6x\))", text)
    _need(match is not None and match[3] == expected_label, "EXPECTED_PB_AND_CEILING_READBACK_REQUIRED")
    _need(type(meta.get("ota_verified")) is bool and type(meta.get("cpe_watchdog_disarmed_after_verify")) is bool,
          "EXPLICIT_OTA_AND_WATCHDOG_FLAGS_REQUIRED")
    _need(meta["ota_verified"] == (match[1] == "OTA_OK"), "OTA_FLAG_AND_MARKER_MUST_AGREE")
    return {"raw": text, "pb_boost": 1, "gain_raw_hex": match[2], "ceiling_label": match[3],
            "reported_ota_verified": meta["ota_verified"], "reported_watchdog_disarmed": meta["cpe_watchdog_disarmed_after_verify"],
            "numeric_cpe_mcs_readback_proven": False, "per_trial_watchdog_disarm_proven": False}


def audit_stage50b(document):
    trials, results, findings, profiles = _trials(document), [], [], {}
    for item in document["trials"]:
        profile, rep = item["profile_id"], item["rep"]
        vals = {key: _value(item.get(key)) for key in (*MEANS, "voip_udp_mbps")}
        _need(vals["iptv_loss_pct"] <= 100 and vals["voip_loss_pct"] <= 100, "UDP_PERCENT_RANGE")
        _need(vals["loaded_ping_p50_ms"] <= vals["loaded_ping_p95_ms"] <= vals["loaded_ping_p99_ms"], "ORDERED_QUANTILES_REQUIRED")
        samples = _uint(item.get("loaded_ping_samples")); _need(samples > 0, "POSITIVE_PING_SAMPLE_COUNT_REQUIRED")
        retransmits = _uint(item.get("bulk_tcp_retransmits"))
        label = dict(zip(PROFILES, ("1024qam (10x)", "256qam (8x)", "64qam (6x)")))[profile]
        maxbd, bler = audit_maxbd(item.get("maxBD_peak_hex")), audit_bler_snapshot(item.get("bler_snapshot"))
        if not maxbd["in_reported_5_to_10_range"]:
            findings.append({"code": "MAXBD_OUTSIDE_REPORTED_RANGE", "profile_id": profile, "rep": rep, "value": maxbd["value"]})
        for check in ("display_matches_floor_correct_ratio", "bps_matches_correct_times_fragment_bits"):
            if not bler[check]:
                findings.append({"code": "FRAGMENT_LABEL_ARITHMETIC_DISAGREES", "profile_id": profile, "rep": rep, "check": check})
        results.append({"profile_id": profile, "rep": rep, "values": vals, "ping_samples": samples,
                        "bulk_tcp_retransmits": retransmits, "apply_readback": _apply_readback(item.get("apply_meta"), label),
                        "maxbd": maxbd, "fragment_snapshot": bler})
    summaries = _dict(document.get("summary_by_profile")); _need(set(summaries) == set(PROFILES), "ALL_THREE_PROFILE_SUMMARIES_REQUIRED")
    for profile in PROFILES:
        obs = [t for t in results if t["profile_id"] == profile]
        means = {"mean_" + key: _mean([t["values"][key] for t in obs]) for key in MEANS}
        means["mean_aggregate_dl_mbps"] = _mean([t["values"]["bulk_tcp_mbps"] + t["values"]["iptv_udp_mbps"] for t in obs])
        for short in ("p50", "p95"):
            key = "loaded_ping_" + short + "_ms"
            means["median_" + key] = statistics.median([t["values"][key] for t in obs])
        summary = _dict(summaries[profile]); _need(_uint(summary.get("n_trials")) == 3, "THREE_TRIALS_PER_PROFILE_REQUIRED")
        checks = {key: abs(_value(summary.get(key)) - value) <= 0.0011 for key, value in means.items()}
        for key, ok in checks.items():
            if not ok:
                findings.append({"code": "PROFILE_SUMMARY_DISAGREES", "profile_id": profile, "field": key,
                                 "reported": summary[key], "recomputed": means[key]})
        peaks = [t["maxbd"]["value"] for t in obs]
        profiles[profile] = {"means": means, "summary_checks": checks,
            "median_iptv_loss_pct": statistics.median([t["values"]["iptv_loss_pct"] for t in obs]),
            "maxbd": {"values": peaks, "min": min(peaks), "max": max(peaks)},
            "reported_fragment_percent_values": [t["fragment_snapshot"]["displayed_percent"] for t in obs],
            "supplied_rate_contracts": [verify_cpe_mcs_contract(cpe_id=0, mcs_level=CEILINGS[profile], opcode=op) for op in (0, 2)]}
    baseline = profiles[PROFILES[0]]["means"]
    changes = {p: {key: _delta(baseline[key], value) for key, value in profiles[p]["means"].items() if baseline[key] > 0}
               for p in PROFILES[1:]}
    scores = {p: round(profiles[p]["means"]["median_loaded_ping_p95_ms"] + 10 * profiles[p]["means"]["mean_iptv_loss_pct"], 3)
              for p in PROFILES}
    winner = PROFILES[2] if scores[PROFILES[2]] <= scores[PROFILES[1]] else PROFILES[1]
    reported_winner = document.get("winning_profile")
    _need(type(reported_winner) is str and reported_winner in PROFILES, "KNOWN_REPORTED_WINNER_REQUIRED")
    if reported_winner != winner:
        findings.append({"code": "REPORTED_WINNER_DISAGREES_WITH_HYBRID_SCORE", "reported": reported_winner, "recomputed": winner})
    persistence = _dict(document.get("flash_persistence_receipt")); ceiling = _uint(persistence.get("winning_mcs_ceiling"))
    if ceiling != CEILINGS[reported_winner]:
        findings.append({"code": "WINNING_FLASH_CEILING_DISAGREES", "reported": ceiling, "expected": CEILINGS[reported_winner]})
    receipts = {"LTU1": audit_progress_receipt(persistence.get("ltu1_boca5_cfgmtd_out"), persistence.get("ltu1_boca5_cfgmtd_rc")),
                "LTU2": audit_progress_receipt(persistence.get("ltu2_ota_cfgmtd_out"), persistence.get("ltu2_ota_cfgmtd_rc"))}
    for endpoint, receipt in receipts.items():
        if not receipt["command_success_receipt"]:
            findings.append({"code": "CFGMTD_SUCCESS_RECEIPT_INCOMPLETE", "endpoint": endpoint})
    stage = _dict(document.get("remote_cpe_stage_meta"))
    _need(stage.get("cpe_stage_out") == "1 (0:OFF, 1:ON, 2:AUTO) gain:0x268d\n1024qam (10x)", "EXPECTED_INITIAL_CPE_STAGE_READBACK_REQUIRED")
    _need(type(stage.get("ota_verified")) is bool and type(stage.get("cpe_watchdog_disarmed_after_verify")) is bool,
          "EXPLICIT_REMOTE_STAGE_FLAGS_REQUIRED")
    findings.extend([
        {"code": "STAGE50_DISCRETE_CPE_MCS_CONFLICTS_WITH_STAGE49_SENTINEL32", "native_resolution": "MISSING_DMESG_AND_EXACT_BUILD"},
        {"code": "MAXBD_RANGE_MATCHES_BUT_EAB_ABI_RESET_AND_HARD_CAP_UNPROVEN"},
        {"code": "R2_REPORT_BLER_19_TO_21_NOT_IN_SAVED_FRAGMENT_PERCENT_FIELDS",
         "saved_displayed_percent": profiles[PROFILES[2]]["reported_fragment_percent_values"]},
        {"code": "HYBRID_SUBSET_SELECTION_EXCLUDES_LOWER_SCORING_BASELINE", "scores": scores},
        {"code": "R1_LATENCY_GAIN_HAS_THROUGHPUT_AND_IPTV_LOSS_TRADEOFF", "changes_pct": changes[PROFILES[1]]},
    ])
    order = [(t["profile_id"], t["rep"]) for t in results]
    return {"trials": results, "profiles": profiles, "changes_vs_baseline_pct": changes, "findings": findings,
            "selection": {"formula": "median_trial_p95_ms + 10*mean_trial_IPTV_loss_pct", "scores_all_profiles": scores,
                          "eligible_profiles": list(PROFILES[1:]), "recomputed_winner": winner, "reported_winner": reported_winner,
                          "global_optimum_or_pareto_improvement_proven": False},
            "persistence": {"receipts": receipts, "winning_mcs_ceiling": ceiling,
                            "persisted_content_and_deployed_script_hashes": "MISSING", "new_poststart_executed_by_runner": False,
                            "cpe_live_ceiling_staged": 23, "cpe_persisted_ceiling_reported": ceiling,
                            "live_and_postboot_profiles_equivalent_proven": False, "cold_boot_proven": False},
            "design": {"listed_order": [{"profile_id": p, "rep": n} for p, n in order],
                       "cyclic_latin_square_positions": tuple(order) == TRIAL_ORDER, "randomization_proven": False,
                       "carryover_balanced": False, "five_samples_per_trial": all(t["ping_samples"] == 5 for t in results),
                       "quantiles": "Linear interpolation at (N-1)*p; mean/median of trial quantiles, not pooled tails",
                       "aggregate_dl_excludes_voip": True, "raw_receiver_json_counts_and_ping_samples": "MISSING",
                       "isolated_mcs_swq_htb_or_maxbd_cause_proven": False},
            "recipe_qualifications": {"R0_HTB_root_mbps": 26, "hybrid_HTB_root_mbps": 21,
                "hybrids_also_change": ["SWQ20to2", "DGAIN0to1", "ULstrategy0to1", "UL_PM65535to0", "stallBD2to0", "2tierTo3tierHTB", "FQclassAndTiming"],
                "remote_cpe_stays_SWQ2_DGAIN1_during_R0": True, "trial_changes_AP_only": True,
                "ulautogain1_report_not_supported_by_saved_getter": True, "trial_ulautogain3_is_conditional_on_rxgain_prefix7": True,
                "watchdog_partial_restore": ["autoMcsCeiling23", "pb_boost1"], "watchdog_flag_is_AP_ota_ok_alias": True,
                "maxBD_write0_before_profile_ping_then_one_postload_read": True,
                "dmesg_ELF_relocation_module_hashes_and_complete_native_getters": "MISSING",
                "prior_Stage48_maxBD49_comparative_peak_capture": "NOT_ESTABLISHED"},
            "remote_cpe_stage_report": stage, "post_bench_link_snapshot": _dict(document.get("ota_link_verification_post_bench")),
            "standalone_route_isolation_and_coldboot_proven": False, "native_acceptance": False, "physical_status": "UNKNOWN"}


def audit_saved_sources(root=ROOT):
    root = _local_path(root); document = read_json(root / SOURCE)
    report = _local_path(root / REPORT); _need(report.stat().st_size <= 250000, "BOUNDED_LOCAL_REPORT_REQUIRED")
    raw = report.read_bytes(); _need(len(raw) <= 250000, "BOUNDED_LOCAL_REPORT_REQUIRED")
    text = raw.decode("utf-8"); contract = source_contract(document, text)
    return {"audit_version": 1, "task_id": TASK_ID, "audit_status": "COMPLETE_WITH_QUALIFICATIONS",
            "source_contract": contract, "input_raw_sha256": {SOURCE: hashlib.sha256((root / SOURCE).read_bytes()).hexdigest(),
                                                             REPORT: hashlib.sha256(raw).hexdigest()},
            "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "static_recipe_context_sha256": {"tools/bench/run_stage50b_ltu_hybrid_swq_and_mcs_ceiling_ota_bench.py":
                                               "cd97f7afabae6f2ca53e2b327e878374c26fc3838ce3f97fecca9d661bbef7cf"},
            "stage50b": audit_stage50b(document),
            "boundary": {"offline_only": True, "ssh": False, "hardware_access": False,
                         "native_dispatch_allowed": False, "physical_acceptance": "UNKNOWN", "e2": "NOT_ACCEPTED"}}


def write_audit(audit, output, *, protected_paths=()):
    """Atomic local managed JSON export; reject links, devices and unowned files."""
    audit = _dict(audit)
    _need(audit.get("task_id") == TASK_ID and type(audit.get("audit_version")) is int and audit["audit_version"] == 1,
          "MANAGED_STAGE46B_AUDIT_REQUIRED")
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
        with tempfile.NamedTemporaryFile(dir=parent, prefix=".stage46b-", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name); handle.write(payload); handle.flush(); os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return target
