#!/usr/bin/env python3
"""
Tests for Stage 46C (`T-S46C-GEM2-CHAMPION-V13-DUAL-NETDEV-WEIGHTS-AND-AQL-INVERSION-GUARD`):
  1. Hardware-verified AQL Priority Inversion & Quantum/Budget Mismatch Guard (`validate_aql_and_aqm_priority_inversion_guard`).
  2. Empirical Stage 41A Champion v13 loader & OpenWISP 26.09 NetJSON Template (`export_openwisp_dual_netdev_champion_v13_netjson_template`).
  3. OpenWrt 24.10.4 ImageBuilder First-Boot UCI-defaults (`98-futuramax-champion-v13-aqm`) & WDS Hotplug (`99-futuramax-wds-dms`) Dual-Netdev `768:512:128` airtime weight persistence.
  4. Closed-Loop Research Reactor (`ingest_stage41a_champion_v13_and_synthesize_m26_m27`) synthesizing `M26` & `M27`.
  5. OpenWISP Dual-NMS Portal (`OPENWISP_DUAL_NMS_PORTAL.html` & `/api/v1/iptv/capacity/`) exposing Champion v13.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from controller.wisp_iptv_ptmp_sector_optimizer import (
    export_openwisp_dual_netdev_champion_v13_netjson_template,
    load_empirical_stage41a_champion_v13_evidence,
    render_openwrt_dual_netdev_champion_v13_script,
    validate_aql_and_aqm_priority_inversion_guard,
)
from firmware.openwrt.futuramax_openwrt_imagebuilder_packager import (
    STAGE46C_OUTPUT_JSON,
    generate_stage46c_imagebuilder_champion_v13_manifest,
    render_hotplug_99_futuramax_wds_dms,
    render_uci_defaults_98_futuramax_champion_v13_aqm,
)
from tools.research.closed_loop_research_reactor import (
    STAGE46C_REACTOR_V13_RECEIPT_JSON,
    ingest_stage41a_champion_v13_and_synthesize_m26_m27,
)
from tools.serve_openwisp_dual_nms_live import (
    PORTAL_HTML_OUT,
    build_iptv_and_capacity_ceiling_api_payload,
    build_openwisp_portal_html,
)


def test_aql_priority_inversion_and_quantum_guard_rules() -> None:
    # 1. Valid Stage 41A Champion v13 configuration must pass
    valid_res = validate_aql_and_aqm_priority_inversion_guard(
        fq_quantum_bytes=4542,
        ac_vo_low_us=300,
        ac_vi_low_us=1200,
        ac_be_low_us=1500,
        aql_threshold_us=5000,
    )
    assert valid_res["valid"] is True
    assert valid_res["violations"] == []

    # 2. S41A-R3 AQL Priority Inversion (AC_VI_low=1000 < AC_BE_low=1500) must be rejected
    r3_res = validate_aql_and_aqm_priority_inversion_guard(
        fq_quantum_bytes=4542,
        ac_vo_low_us=300,
        ac_vi_low_us=1000,
        ac_be_low_us=1500,
        aql_threshold_us=5000,
    )
    assert r3_res["valid"] is False
    assert any("AQL_PRIORITY_INVERSION" in v for v in r3_res["violations"])

    # 3. S41A-R1 AQM-to-AQL 4xMTU Quantum/Budget mismatch (fq_quantum=6056, BE=1400, thr=4000) must be rejected
    r1_res = validate_aql_and_aqm_priority_inversion_guard(
        fq_quantum_bytes=6056,
        ac_vo_low_us=250,
        ac_vi_low_us=1000,
        ac_be_low_us=1400,
        aql_threshold_us=4000,
    )
    assert r1_res["valid"] is False
    assert any("AQM_AQL_QUANTUM_BUDGET_MISMATCH" in v for v in r1_res["violations"])

    # 4. S41A-R4 sub-300 us AC_VO wakeup churn (VO=250) must be rejected
    r4_res = validate_aql_and_aqm_priority_inversion_guard(
        fq_quantum_bytes=4542,
        ac_vo_low_us=250,
        ac_vi_low_us=1200,
        ac_be_low_us=1500,
        aql_threshold_us=5000,
    )
    assert r4_res["valid"] is False
    assert any("VOIP_AQL_WAKEUP_CHURN" in v for v in r4_res["violations"])


def test_stage41a_champion_v13_evidence_and_netjson_template() -> None:
    ev = load_empirical_stage41a_champion_v13_evidence()
    r2 = ev["s41a_r2_champion_v13_promoted"]
    assert r2["round_id"] == "S41A-R2"
    assert abs(float(r2["goodput_delta_pct"]) - 1.462) < 1e-3
    assert float(r2["iptv_arm_b_loss_pct"]) == 0.0
    assert float(r2["voip_loss_pct"]) == 0.0
    assert r2["tcp_notsent_lowat"] == 8192
    assert r2["tcp_limit_output_bytes"] == 98304

    script = render_openwrt_dual_netdev_champion_v13_script()
    assert "airtime_weight 768" in script
    assert "airtime_weight 512" in script
    assert "airtime_weight 128" in script
    assert "tcp_notsent_lowat=8192" in script
    assert "tcp_limit_output_bytes=98304" in script
    assert "echo fq_quantum 4542" in script
    assert "echo \"1 1200 2400\"" in script

    tpl = export_openwisp_dual_netdev_champion_v13_netjson_template()
    assert tpl["name"] == "FMX openwrt_dual_netdev_768_512_128_tcp_lowat_8k_champion_v13"
    assert len(tpl["profile_sha256"]) == 64
    assert tpl["aql_priority_inversion_guard"]["valid"] is True


def test_imagebuilder_champion_v13_and_hotplug_wds_weights() -> None:
    hotplug = render_hotplug_99_futuramax_wds_dms("ubnt_lap-120")
    assert "multicast_to_unicast" in hotplug
    assert "multicast_fast_leave" in hotplug
    assert "airtime_weight 768" in hotplug
    assert "airtime_weight 512" in hotplug
    assert "airtime_weight 128" in hotplug

    ap_uci = render_uci_defaults_98_futuramax_champion_v13_aqm("ubnt_lap-120")
    assert 'echo "fq_quantum 4542"' in ap_uci
    assert "tcp_notsent_lowat=8192" in ap_uci
    assert "airtime_weight 768" in ap_uci

    cpe_uci = render_uci_defaults_98_futuramax_champion_v13_aqm("ubnt_nanostation-ac-loco")
    assert 'echo "fq_quantum 1514"' in cpe_uci
    assert "tcp_pacing_ca_ratio=140" in cpe_uci

    manifest = generate_stage46c_imagebuilder_champion_v13_manifest()
    assert STAGE46C_OUTPUT_JSON.exists()
    assert manifest["stage"] == "46C"
    assert manifest["targets_count"] == 4
    for target_data in manifest["targets"].values():
        assert "files/etc/uci-defaults/98-futuramax-champion-v13-aqm" in target_data["overlay_files"]
        assert "files/etc/hotplug.d/net/99-futuramax-wds-dms" in target_data["overlay_files"]


def test_closed_loop_reactor_v13_ingestion_and_m26_m27_synthesis() -> None:
    receipt = ingest_stage41a_champion_v13_and_synthesize_m26_m27()
    assert STAGE46C_REACTOR_V13_RECEIPT_JSON.exists()
    assert receipt["stage"] == "46C"
    assert set(receipt["ingested_rounds_summary"].keys()) == {"S41A-R1", "S41A-R2", "S41A-R3", "S41A-R4"}
    mechs = {m["mechanism_id"]: m for m in receipt["next_wave_mechanisms_m26_to_m27"]}
    assert "M26" in mechs
    assert "M27" in mechs
    assert "768:512:128" in mechs["M26"]["title"]
    assert "AQL Priority Inversion" in mechs["M27"]["title"]


def test_openwisp_dual_nms_portal_champion_v13_integration() -> None:
    api_payload = build_iptv_and_capacity_ceiling_api_payload()
    assert "openwisp_dual_netdev_champion_v13_template" in api_payload
    assert "stage41a_champion_v13_evidence" in api_payload

    out_html = build_openwisp_portal_html()
    assert out_html == PORTAL_HTML_OUT
    html_text = out_html.read_text(encoding="utf-8")
    assert "a4) 1-Click OpenWISP Dual-Netdev Airtime Weight (768:512:128)" in html_text
    assert "FMX openwrt_dual_netdev_768_512_128_tcp_lowat_8k_champion_v13" in html_text
    assert 'id="wisp-iptv-capacity-ceiling-tab"' in html_text
