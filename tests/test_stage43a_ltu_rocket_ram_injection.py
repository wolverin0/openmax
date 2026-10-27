#!/usr/bin/env python3
"""
Unit tests for Stage 43A (LTU-Lite #1 board_ssid=0xae08 intmode=1 + LTU-Rocket RAM Module Injection).
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.bench.run_stage43a_intmode1_ota_test import (
    OUT_JSON_PATH,
    build_ltu_ame_core,
    build_patched_ame_dev,
    build_rocket_ame_core,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage43a_binary_builders_and_symtab_resolution() -> None:
    """Verify rocket_ame_core.ko, ltu_ame_core.ko, and ame_dev.ko binary builders."""
    rocket_bytes, meta_r = build_rocket_ame_core()
    assert len(rocket_bytes) == 3318764
    assert len(meta_r["movw_ae05_to_ae08_text_rvas"]) == 5
    assert sorted(meta_r["symtab_resolved_to_text_0x98_ret1"]) == [
        "send_map",
        "send_wr_fpga_reg_command",
    ]

    ltu_bytes, meta_l = build_ltu_ame_core()
    assert len(ltu_bytes) == 3282052
    assert len(meta_l["movw_ae05_to_ae08_text_rvas"]) == 5

    dev_bytes, meta_d = build_patched_ame_dev()
    assert len(dev_bytes) == 298760
    assert len(meta_d["movw_ae05_to_ae08_text_rvas"]) == 1


def test_stage43a_artifact_and_report_completeness() -> None:
    """Verify the Stage 43A JSON artifact and markdown report exist and contain valid hardware verification data."""
    assert OUT_JSON_PATH.exists(), f"Missing Stage 43A artifact: {OUT_JSON_PATH}"
    data = json.loads(OUT_JSON_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 43A"
    assert (
        data["task_id"]
        == "T-S43A-LTU-ROCKET-RAM-MODULE-INJECTION-AND-OTA-LINK-QUALIFICATION"
    )
    final = data["final_active_state_on_ltu1"]
    assert "ame_core" in final["lsmod_ame"]
    assert "5120273" in final["lsmod_ame"]
    assert any("ame_hal_submit_dlmap" in s for s in final["rocket_ap_symbols_in_kallsyms"])
    assert "AP-PTMP(Run)" in final["common_info"]
    assert "Txpower: 20,20" in final["common_info"]
    assert "AutoLink: 1" in final["common_info"]

    report_path = (
        REPO_ROOT
        / "docs"
        / "STAGE43A_LTU_ROCKET_RAM_MODULE_INJECTION_AND_INTMODE1_OTA.md"
    )
    assert report_path.exists()
    text = report_path.read_text(encoding="utf-8")
    assert "ame_hal_submit_dlmap" in text
    assert "0xae08" in text
