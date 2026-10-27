"""
Tests for Stage 43C (`T-S43C-GEM2-CHAMPION-V11-TRIPLE-PLAY-AQM-4542-AND-VOIP-AQL-INTEGRATION`):
Verifies:
  1. `load_empirical_stage37a_champion_v11_evidence()` loads `S37A-R1` (`REFUTED`, `-3.628%` GP) vs
     `S37A-R2` (`CONFIRMED` Champion v11: `+2.648%` GP, `-3.778%` p95 RTT, `-22.452%` p50 RTT,
     `0/5684` Dual IPTV loss, `0/1198` VoIP loss).
  2. `export_openwisp_triple_play_champion_v11_netjson_template()` generates a valid OpenWISP
     NetJSON DeviceConfiguration template with `fq_quantum 4542`, `fq_limit 2048`,
     `fq_memory_limit 4194304`, `AC_VO=300/600`, `AC_VI=1200/2400`, `AC_BE=1500/3000`,
     and zero `FORBIDDEN_TOKENS`.
  3. `tools/serve_openwisp_dual_nms_live.py` exposes Champion v11 in `build_iptv_and_capacity_ceiling_api_payload()`
     and renders it in `OPENWISP_DUAL_NMS_PORTAL.html`.
"""

from __future__ import annotations

from controller.multiradio_golden_profile_applicator import FORBIDDEN_TOKENS
from controller.wisp_iptv_ptmp_sector_optimizer import (
    export_openwisp_triple_play_champion_v11_netjson_template,
    load_empirical_stage37a_champion_v11_evidence,
    render_openwrt_triple_play_champion_v11_script,
)
from tools.serve_openwisp_dual_nms_live import (
    PORTAL_HTML_OUT,
    build_iptv_and_capacity_ceiling_api_payload,
    build_openwisp_portal_html,
)


def test_stage43c_empirical_stage37a_champion_v11_evidence() -> None:
    ev = load_empirical_stage37a_champion_v11_evidence()
    r1 = ev["s37a_r1_quantum_3028_vo_600_1200_refuted"]
    r2 = ev["s37a_r2_champion_v11_promoted"]

    assert r1["round_id"] == "S37A-R1"
    assert r1["claim_status"] == "REFUTED"
    assert r1["goodput_delta_pct"] == -3.628

    assert r2["round_id"] == "S37A-R2"
    assert r2["claim_status"] == "CONFIRMED"
    assert r2["goodput_delta_pct"] == 2.648
    assert r2["p95_rtt_delta_pct"] == -3.778
    assert r2["p50_rtt_delta_pct"] == -22.452
    assert r2["iptv_lost_datagrams"] == 0
    assert r2["iptv_total_datagrams"] == 5684
    assert r2["voip_lost_datagrams"] == 0
    assert r2["voip_total_datagrams"] == 1198
    assert r2["ap_fq_quantum_bytes"] == 4542
    assert r2["ap_fq_limit_pkts"] == 2048
    assert r2["cpe_fq_limit_pkts"] == 1024


def test_stage43c_triple_play_champion_v11_netjson_and_portal() -> None:
    script = render_openwrt_triple_play_champion_v11_script()
    assert "echo fq_quantum 4542" in script
    assert "echo fq_limit 2048" in script
    assert "echo fq_memory_limit 4194304" in script
    assert 'echo "0 300 600"' in script
    assert 'echo "1 1200 2400"' in script
    assert 'echo "2 1500 3000"' in script
    assert "udp dport 5202 ip dscp set cs4" in script
    assert "udp dport 5203 ip dscp set ef" in script

    for tok in FORBIDDEN_TOKENS:
        assert tok not in script.lower()

    tpl = export_openwisp_triple_play_champion_v11_netjson_template()
    assert tpl["name"] == "FMX openwrt_triple_play_aqm_4542_voip_iptv_champion_v11"
    assert len(tpl["profile_sha256"]) == 64

    api_payload = build_iptv_and_capacity_ceiling_api_payload()
    assert "openwisp_triple_play_champion_v11_template" in api_payload
    assert "stage37a_champion_v11_evidence" in api_payload

    out_html = build_openwisp_portal_html(PORTAL_HTML_OUT)
    html_text = out_html.read_text(encoding="utf-8")
    assert "FMX openwrt_triple_play_aqm_4542_voip_iptv_champion_v11" in html_text
    assert "fq_quantum=4542" in html_text
    assert "0/5684" in html_text
    assert "0/1198" in html_text
