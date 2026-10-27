"""Tests for Stages 241A to 246A (IRQ 33 Spectral Filter Dissection, Stage 0 Mode B Kits, Live CPE Map, 1.85B SimPy Model & Stage 59A Update)."""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage241a_wa_irq33_spectral_filter_storm_dissection() -> None:
    p = REPO_ROOT / "artifacts" / "autoresearch" / "stage241a_wa_irq33_spectral_filter_storm_dissection.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "241A"
    assert data["production_safety_audit"]["writes_performed"] == 0
    fn = data["binary_dissection_ath_dev_ko"]["text_functions"]
    assert fn["ath_spectral_filter_init"]["offset"] == "0x027c00"
    assert fn["ath_spectral_filter_start"]["offset"] == "0x027cac"
    assert fn["ath_spectral_filter_stop"]["offset"] == "0x027cb4"
    corr = data["live_irq33_and_xmit_filtered_correlation"]
    assert corr["total_irq33_interrupts_across_4_radios"] == 4532402525
    assert corr["total_xmit_filtered_events_across_4_radios"] == 1852520403
    assert audit_stage_receipt_5pillars(data)["compliant"]


def test_stage242a_guarida_stage0_mode_b_kits() -> None:
    p = REPO_ROOT / "artifacts" / "autoresearch" / "stage242a_guarida_stage0_mode_b_kits.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "242A"
    assert len(data["kits"]) == 4
    for kit in data["kits"]:
        script_path = REPO_ROOT / kit["script_path"]
        assert script_path.exists()
        txt = script_path.read_text(encoding="utf-8")
        assert "vm.min_free_kbytes=4096" in txt
        assert "airview.status=disabled" in txt
        assert "system.cfg.orig" in txt
    assert audit_stage_receipt_5pillars(data)["compliant"]


def test_stage243a_panel2_panel3_live_cpe_arp_and_airtime_map() -> None:
    p = REPO_ROOT / "artifacts" / "autoresearch" / "stage243a_panel2_panel3_live_cpe_arp_and_airtime_map.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "243A"
    assert data["active_online_cpes_count"] == 10
    franco = [c for c in data["active_online_cpes"] if "FRANCO" in c["hostname"]][0]
    assert franco["airmax_tx_usage"] == 298
    assert franco["sector_dl_airtime_share_pct"] == 59.36
    assert audit_stage_receipt_5pillars(data)["compliant"]


def test_stage244a_guarida_185billion_txbuf_drop_simpy_model() -> None:
    p = REPO_ROOT / "artifacts" / "autoresearch" / "stage244a_guarida_185billion_txbuf_drop_simpy_model.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "244A"
    reg = data["simpy_regimes"]
    assert (
        reg["R1_STAGE0_MODE_B_RC_POSTSTART_AND_CFG_FIX"]["no_tx_buf_ratio_pct"]
        < reg["R0_LIVE_STOCK_BASELINE"]["no_tx_buf_ratio_pct"]
    )
    assert (
        reg["R2_STAGE1_2_OPENWRT_24_10_4_WA_CHAMPION_V3"]["p99_queue_delay_ms"]
        < reg["R0_LIVE_STOCK_BASELINE"]["p99_queue_delay_ms"]
    )
    assert audit_stage_receipt_5pillars(data)["compliant"]


def test_stage245a_stage59a_guarida_master_plan_update() -> None:
    p = REPO_ROOT / "artifacts" / "autoresearch" / "stage245a_stage59a_guarida_master_plan_update.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "245A"
    assert data["line_count"] < 220
    assert data["doc_head_count"] == 1
    doc = REPO_ROOT / "docs" / "STAGE59A_ZERO_FALSE_POSITIVE_WISP_RF_OBSERVABILITY_AND_GUARIDA_PLAN.md"
    assert doc.exists()
    lines = doc.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1
    assert audit_stage_receipt_5pillars(data)["compliant"]
