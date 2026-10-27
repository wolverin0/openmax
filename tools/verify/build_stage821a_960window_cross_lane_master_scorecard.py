#!/usr/bin/env python3
"""Stage821A: source-qualified scorecard; 960 is a target, not a preset result."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.sim.run_stage819a_guarida_tower_v10_triple_patch_and_xw_mixed_tdma_pareto import (
    BOUNDARY, emit, pillars, source,
)

SLUG = "stage821a_960window_cross_lane_master_scorecard"
# Only exact known receipts; never run the producers, scan arbitrary credentials,
# or add cross-lane summary totals to the same underlying lane a second time.
INPUTS = {
    "wa": (
        ("stage773a_wa_champion_v13_344window_field_rollout_kit.json", ("cumulative_wa_windows",)),
        ("stage801a_live_wa_mk1_251_e2e_v14_400window_milestone.json", ("cumulative_windows_all_10_e2e_rounds",)),
    ),
    "ltu": (
        ("stage774a_ltu_champion_v20_264window_zero_dhcp_kit.json", ("cumulative_ltu_windows",)),
        ("stage793a_live_ltu110_round23_276window_autoresearch.json", ("summary_metrics", "cumulative_ltu110_live_windows")),
    ),
    "multi_radio": (
        ("stage721a_multi_radio_240w_milestone_campaign.json", ("cumulative_multi_radio_windows",)),
        ("stage779a_multi_radio_264w_milestone_campaign.json", ("milestone_summary", "cumulative_multi_radio_windows")),
    ),
    "ptp": (
        ("stage741a_pbe5ac_lbe5ac_vht40_pb050_production_bundle_v5.json", ("cumulative_ptp_windows",)),
        ("stage777a_900window_cross_lane_master_scorecard.json", ("live_window_breakdown", "pbe5ac_lbe5ac_v5_ptp_windows")),
    ),
}


def nested_count(obj: dict, keys: tuple[str, ...]) -> int | None:
    value = obj
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    if type(value) is not int or value < 0:
        raise ValueError("invalid_cumulative_window_count")
    return value


def summarize(root: Path = ROOT) -> dict:
    lanes = []
    all_sources = []
    for lane, inputs in INPUTS.items():
        records = []
        counts = []
        unique_ids = set()
        duplicate_ids = 0
        for filename, count_keys in inputs:
            pin, obj = source(root, f"artifacts/autoresearch/{filename}")
            all_sources.append(pin)
            row = {"source": pin, "count_path": list(count_keys)}
            if obj is None:
                row.update(classification="MISSING", reported_windows=None)
                records.append(row)
                continue
            mode = str(obj.get("execution_mode", "")).upper()
            explicit_fallback = (any(token in mode for token in ("FALLBACK", "SYNTH", "SIMULATION"))
                                 or obj.get("live_ssh_connected") is False)
            reported = nested_count(obj, count_keys)
            row.update(classification="SYNTHETIC_EXCLUDED" if explicit_fallback else "REPORTED_UNVERIFIED",
                       reported_windows=reported, source_execution_mode=mode or "UNSPECIFIED")
            if not explicit_fallback and reported is not None:
                counts.append(reported)
            windows = obj.get("windows", obj.get("counterbalanced_windows", []))
            if not isinstance(windows, list):
                windows = []
            for window in windows:
                if not isinstance(window, dict):
                    continue
                wid = window.get("window_id")
                if not explicit_fallback and isinstance(wid, str) and wid:
                    # A repeated ID within a lane is one reported window, never two.
                    if wid in unique_ids:
                        duplicate_ids += 1
                    unique_ids.add(wid)
            records.append(row)
        lanes.append({"lane": lane, "reported_cumulative_max": max(counts) if counts else None,
                      "reported_distinct_window_ids": sorted(unique_ids),
                      "duplicate_window_ids_removed": duplicate_ids,
                      "accepted_live_windows": None, "physical_evidence_status": "UNKNOWN",
                      "sources": records})
    values = [lane["reported_cumulative_max"] for lane in lanes]
    complete = all(value is not None for value in values)
    subtotal = sum(value for value in values if value is not None)
    return {"lanes": lanes, "sources": all_sources, "target_windows": 960,
            "reported_windows_subtotal": subtotal,
            "reported_windows_total": subtotal if complete else None,
            "report_complete": complete,
            "reported_target_reached": subtotal >= 960 if complete else None,
            "accepted_live_windows": None, "live_target_accepted": False,
            "deduplication": "maximum cumulative count per lane; IDs unique within lane; no cross-lane summary addition"}


def build(root: Path = ROOT) -> dict:
    summary = summarize(root)
    pins = [source(root, path)[0] for path in (
        "tools/verify/build_stage821a_960window_cross_lane_master_scorecard.py",
        "tools/sim/run_stage819a_guarida_tower_v10_triple_patch_and_xw_mixed_tdma_pareto.py")]
    receipt = {"stage": "821A", "status": "CONFIRMED", "execution_mode": "OFFLINE_SCORECARD",
               "claim_scope": "local reconciliation only; imported claims are not independently accepted",
               "attribution": ["external controller"], "boundary": dict(BOUNDARY),
               **summary, "code_sources": pins,
               "five_pillar_compliance": pillars("821A", "max-per-lane cumulative reconciliation and ID deduplication")}
    rows = "\n".join(f"| {item['lane']} | {item['reported_cumulative_max']} | UNKNOWN |" for item in summary["lanes"])
    return emit(root, SLUG, receipt, "# Stage821A cross-lane 960-window target\n\n"
                "CONFIRMED local reconciliation; physical acceptance UNKNOWN.\n\n"
                "| Lane | Imported cumulative maximum | Accepted live windows |\n| --- | ---: | --- |\n" + rows + "\n\n"
                f"Reported subtotal: {summary['reported_windows_subtotal']}. Complete report: {summary['report_complete']}.\n"
                f"960 target reported reached: {summary['reported_target_reached']}; live target accepted: false.\n\n"
                "Missing lanes stay unknown. Cumulative receipts use a maximum per lane, never a sum.\n"
                "Fallback/synthetic receipts are excluded; repeated window IDs are deduplicated per lane.\n"
                "Source status CONFIRMED and claimed SSH success do not authenticate native measurement provenance.\n"
                "No new radio trials, SSH, flash or MemoryMaster ingestion were performed.\n")


def main() -> int:
    receipt = build()
    print(f"821A reported subtotal={receipt['reported_windows_subtotal']} complete={receipt['report_complete']} accepted=UNKNOWN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
