"""Unit tests for Stage 29C Multi-Radio Exhaustion & Headroom Matrix (`T-S29C-GEM2-MULTI-RADIO-ROADMAP-AND-CHAMPION-AUDITOR`)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from analysis.multi_radio_exhaustion_and_headroom_matrix import (
    OUTPUT_DOC_PATH,
    OUTPUT_JSON_PATH,
    REQUIRED_RADIO_MODES,
    generate_stage29c_matrix_and_docs,
    inspect_stage_receipts_and_ledger,
)


def test_stage_receipts_and_champion_ledger_inspection() -> None:
    """Verify champion_state_ledger.json and stage13..28 JSON receipts are loaded."""
    inspection = inspect_stage_receipts_and_ledger()
    assert inspection["ledger_profiles_count"] >= 8
    assert inspection["stage_receipts_inspected_count"] >= 15
    assert "openwrt_lap120_ptp_1cpe_champion" in inspection["raw_ledger_profiles"]
    assert "openwrt_lap120_ptmp_multicpe_champion" in inspection["raw_ledger_profiles"]
    assert "ltu_lite_amesoc" in inspection["raw_ledger_profiles"]
    assert "r2ac_prism_ap" in inspection["raw_ledger_profiles"]
    assert "r5ac_prism_sta" in inspection["raw_ledger_profiles"]
    assert "pbm5_xw_weak_ota" in inspection["raw_ledger_profiles"]
    assert "af4x_invictus" in inspection["raw_ledger_profiles"]


def test_all_9_required_radio_modes_present_and_consistent(tmp_path: Path) -> None:
    """Verify all 9 required radio & operating modes have exact parameter counts, Champion deltas, headroom, and 3 queued rounds."""
    out_json = tmp_path / "stage29c_headroom_matrix_20261025.json"
    out_doc = tmp_path / "STAGE29C_MULTI_RADIO_HEADROOM_AND_ROADMAP_MATRIX.md"
    report = generate_stage29c_matrix_and_docs(output_json_path=out_json, output_doc_path=out_doc)

    assert out_json.exists()
    assert out_doc.exists()
    assert OUTPUT_JSON_PATH.exists()
    assert OUTPUT_DOC_PATH.exists()

    modes = report["radio_modes"]
    assert tuple(modes.keys()) == REQUIRED_RADIO_MODES
    assert len(modes) == 9

    for mode_key, entry in modes.items():
        total_p = entry["total_discoverable_parameters"]
        tested_p = entry["tested_parameters_count"]
        untested_p = entry["untested_parameters_count"]
        assert total_p > 0, f"{mode_key} total_discoverable_parameters must be > 0"
        assert tested_p + untested_p == total_p, f"{mode_key} tested + untested != total"
        assert entry["parameter_exhaustion_pct"] == pytest.approx(round(tested_p / total_p * 100.0, 2))

        delta = entry["champion_delta_vs_stock"]
        assert delta["cumulative_goodput_delta_pct"] > 0.0, f"{mode_key} must have positive goodput delta vs Stock"
        assert delta["cumulative_p95_rtt_delta_pct"] < 0.0, f"{mode_key} must have negative p95 RTT delta vs Stock"

        headroom = entry["estimated_remaining_theoretical_headroom"]
        assert headroom["physical_shannon_mac_ceiling_20mhz_mbps"] > delta["champion_goodput_mbps"]
        assert len(headroom["primary_physical_bottleneck"]) > 15

        queued = entry["next_3_autonomous_rounds_queued"]
        assert len(queued) == 3, f"{mode_key} must have exactly 3 queued autonomous rounds"
        for r in queued:
            assert r["round_id"].startswith("S30-")
            assert len(r["target_knobs"]) >= 1


def test_global_exhaustion_totals_math() -> None:
    """Verify global totals across all 9 radio modes match the sum of individual entries."""
    loaded = json.loads(OUTPUT_JSON_PATH.read_text(encoding="utf-8"))
    totals = loaded["global_exhaustion_totals"]
    modes = loaded["radio_modes"].values()

    assert totals["radio_modes_count"] == 9
    assert totals["total_discoverable_parameters_across_modes"] == sum(
        m["total_discoverable_parameters"] for m in modes
    )
    assert totals["total_tested_parameters_across_modes"] == sum(
        m["tested_parameters_count"] for m in modes
    )
    assert totals["total_untested_parameters_across_modes"] == sum(
        m["untested_parameters_count"] for m in modes
    )
    assert totals["total_queued_next_autonomous_rounds"] == 27
