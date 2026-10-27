from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts/autoresearch/stage473a_openwrt_ct_vs_stock_xtensa_rc_globals_map.json"
DOC = ROOT / "docs/STAGE473A_OPENWRT_CT_VS_STOCK_XTENSA_RC_GLOBALS_MAP.md"


def test_stage473a_rc_globals_map_artifact_and_doc() -> None:
    assert ARTIFACT.exists(), f"Missing {ARTIFACT}"
    assert DOC.exists(), f"Missing {DOC}"
    doc_lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220, f"Doc exceeds 220 lines ({len(doc_lines)})"

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["stage"] == "473A"
    assert data["status"] == "CONFIRMED"
    assert data["live_devices_touched"] is False
    assert data["firmware_count_analyzed"] == 10

    by_id = {fm["firmware_id"]: fm for fm in data["firmware_maps"]}
    owrt = by_id["OpenWrt_10.1.467-ct_IE3"]
    assert owrt["g_rc_probe_period_ms"]["ram_va"] == "0x0040c24c"
    assert owrt["g_rc_probe_period_ms"]["data_init_value_ms"] == 256
    assert owrt["g_rc_probe_period_ms"]["peer_assoc_override_lit_va"] == "0x009805ec"
    assert owrt["g_rc_probe_pkt_threshold"]["ram_va"] == "0x0040c250"
    assert owrt["g_rc_probe_pkt_threshold"]["data_init_value_pkts"] == 64
    assert owrt["g_rc_probe_pkt_threshold"]["peer_assoc_movi_insn_va"] == "0x0098a3e7"
    assert owrt["g_rc_probe_enable"]["ram_va"] == "0x0040c254"

    wa_ptp = by_id["WA.v8.7.25_ptp"]
    assert wa_ptp["g_rc_probe_period_ms"]["ram_va"] == "0x0040d4e0"
    assert wa_ptp["g_rc_probe_pkt_threshold"]["ram_va"] == "0x0040d4e4"
    assert wa_ptp["rc_ctx_and_thresholds"]["g_default_xretry_per_penalty"]["ram_va"] == "0x0040da78"
    assert wa_ptp["rc_ctx_and_thresholds"]["g_default_xretry_per_penalty"]["data_init_value_pct"] == 30
    assert wa_ptp["rc_ctx_and_thresholds"]["g_rc_rate_max_per_thr"]["ram_va"] == "0x0040da7c"
    assert wa_ptp["rc_ctx_and_thresholds"]["g_rc_rate_max_per_thr"]["data_init_value_pct"] == 65
    assert wa_ptp["rc_ctx_and_thresholds"]["g_default_no_ack_wifi_thr"]["ram_va"] == "0x0040da14"
    assert wa_ptp["g_dbg_max_sw_retry"]["ram_va"] == "0x0040d364"
    assert wa_ptp["g_dbg_max_sw_retry"]["data_init_value"] == 41

    gate = audit_stage_receipt_5pillars(data)
    assert gate["compliant"] is True, f"5-pillar gate failed: {gate}"
