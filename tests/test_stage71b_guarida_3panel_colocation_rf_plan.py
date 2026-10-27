"""Unit tests for Stage 71B (`T-S71B-XC-AIRPRISM-FILTER-AND-CO-LOCATION-INTERFERENCE-BENCHMARK`)
Guarida 3-Panel Co-Location Channel, Guard-Band & `airPrism` / `ANI` / `AQL` Optimizer.
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.deploy.build_stage71b_guarida_3panel_colocation_rf_plan import (
    DEFAULT_OUTPUT_RECEIPT_PATH,
    PROTECTED_BACKBONE_INTERFACE,
    REPO_ROOT,
    REQUIRED_CATALOG_KNOB_IDS,
    audit_catalog_colocation_knobs,
    build_stage71b_guarida_3panel_colocation_plan,
    compute_pairwise_colocation_isolation,
    evaluate_3panel_channel_plan,
    select_airprism_filter_state,
    verify_command_safety,
    write_stage71b_receipt,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars


def test_airprism_filter_selector_matches_native_umac_and_tuner_sh() -> None:
    """Verify `select_airprism_filter_state` matches the 6-entry `ubnt_prism_filters` table
    and discovers the >50 MHz Stage 1 bypass behavior in UNII-2C/UNII-3.
    """
    # Panel 1: 5240 MHz / 20 MHz (UNII-1) -> Stage 1 Entry 0 (GPIO15=1,16=1) + Stage 2 Entry 2 (GPIO13=1,14=0)
    st_5240_20 = select_airprism_filter_state(5240, 20)
    assert st_5240_20["stage1_entry_index"] == 0
    assert st_5240_20["stage2_entry_index"] == 2
    assert st_5240_20["gpio_pins"] == {"gpio15": 1, "gpio16": 1, "gpio13": 1, "gpio14": 0}
    assert st_5240_20["bits_gpio16_to_13"] == 13
    assert st_5240_20["both_stages_selective"] is True

    # Panel 2: 5540 MHz / 20 MHz (UNII-2C) -> Stage 1 Entry 1 (GPIO15=1,16=0) + Stage 2 Entry 5 (GPIO13=1,14=1)
    st_5540_20 = select_airprism_filter_state(5540, 20)
    assert st_5540_20["stage1_entry_index"] == 1
    assert st_5540_20["stage2_entry_index"] == 5
    assert st_5540_20["gpio_pins"] == {"gpio15": 1, "gpio16": 0, "gpio13": 1, "gpio14": 1}
    assert st_5540_20["bits_gpio16_to_13"] == 7
    assert st_5540_20["stage1_selective"] is True

    # Panel 3: 5785 MHz / 20 MHz (UNII-3) -> Stage 1 Entry 1 (GPIO15=1,16=0) + Stage 2 Entry 3 (GPIO13=0,14=1)
    st_5785_20 = select_airprism_filter_state(5785, 20)
    assert st_5785_20["stage1_entry_index"] == 1
    assert st_5785_20["stage2_entry_index"] == 3
    assert st_5785_20["gpio_pins"] == {"gpio15": 1, "gpio16": 0, "gpio13": 0, "gpio14": 1}
    assert st_5785_20["bits_gpio16_to_13"] == 6
    assert st_5785_20["both_stages_selective"] is True

    # 80 MHz in UNII-3 (5775 MHz / 80 MHz) exceeds Entry 1 max_width=50 -> falls back to Stage 1 Entry 4 bypass!
    st_5775_80 = select_airprism_filter_state(5775, 80)
    assert st_5775_80["stage1_entry_index"] == 4
    assert st_5775_80["stage1_selective"] is False
    assert st_5775_80["stage2_entry_index"] == 3
    assert st_5775_80["both_stages_selective"] is False


def test_catalog_colocation_knobs_and_command_safety() -> None:
    """Verify all 18 required `XC`, `WA`, `ath10k`, and `mac80211` knobs exist in the 571-Knob Catalog
    and safety checks reject forbidden backbone or partition commands.
    """
    audit = audit_catalog_colocation_knobs()
    assert audit["total_catalog_knobs"] == 571
    assert audit["required_colocation_knobs_verified"] == len(REQUIRED_CATALOG_KNOB_IDS)
    assert audit["missing_knob_ids"] == []

    unsafe = verify_command_safety(
        [
            f"ip link set {PROTECTED_BACKBONE_INTERFACE} down",
            "dd if=/dev/zero of=/dev/mtd5",
        ]
    )
    assert unsafe["safe"] is False
    assert len(unsafe["violations"]) == 2


def test_stage71b_guarida_3panel_colocation_plan_and_5pillar_gate(tmp_path: Path) -> None:
    """Verify the full Stage 71B Guarida 3-Panel RF plan receipt, topology invariants (`3` panels, `32` CPEs),
    counterbalanced arm comparison (`B2` beats `A0` and `B1`), report line budget (`< 220` lines), and 5-pillar gate.
    """
    out_file = tmp_path / "stage71b_receipt.json"
    receipt = write_stage71b_receipt(out_file)
    assert out_file.exists()
    assert DEFAULT_OUTPUT_RECEIPT_PATH.exists()

    saved = json.loads(DEFAULT_OUTPUT_RECEIPT_PATH.read_text(encoding="utf-8"))
    assert saved["receipt_sha256"] == receipt["receipt_sha256"]
    assert saved["automatic_execution_allowed"] is False
    assert saved["live_devices_touched"] is False

    # Topology invariants: 3 panels, 32 CPEs (4 + 22 + 6)
    topo = saved["guarida_topology_bound"]
    assert topo["panel_count"] == 3
    assert topo["total_cpes"] == 32
    assert topo["panel1_cpes"] == 4
    assert topo["panel2_cpes"] == 22
    assert topo["panel3_cpes"] == 6

    # Counterbalanced comparison: B2 wins with >= 225 MHz guard band and lowest fmx_loss
    comp = saved["counterbalanced_channel_plan_comparison"]
    assert comp["winning_arm"] == "ARM_B2_OPTIMAL_3SUBBAND_AIRPRISM_SELECTIVE_20MHZ"
    loss_a0 = comp["arm_a0_congested_single_subband"]["fmx_loss"]
    loss_b1 = comp["arm_b1_wideband_80mhz_stage1_bypass"]["fmx_loss"]
    loss_b2 = comp["arm_b2_optimal_3subband_selective_20mhz"]["fmx_loss"]
    assert loss_b2 < loss_b1 < loss_a0
    assert comp["arm_b2_optimal_3subband_selective_20mhz"]["min_guard_band_mhz"] == 225
    assert comp["arm_b2_optimal_3subband_selective_20mhz"]["all_pairs_disjoint_airprism_subbands"] is True

    # Verify 5-Pillar Research Gate compliance
    pillar_res = audit_stage_receipt_5pillars(saved)
    assert pillar_res["compliant"] is True
    assert pillar_res["missing_pillars"] == []

    # Verify report exists and is strictly < 220 lines
    doc_path = REPO_ROOT / "docs" / "STAGE71B_GUARIDA_3PANEL_AIRPRISM_AND_COLOCATION_RF_PLAN.md"
    assert doc_path.exists()
    doc_lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220
    assert doc_lines[0].startswith("<!-- doc-head:")
