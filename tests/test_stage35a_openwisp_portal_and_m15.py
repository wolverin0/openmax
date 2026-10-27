"""
Unit and receipt verification tests for Stage 35A
(`T-S35A-LIVE-OPENWISP-PORTAL-SERVER-AND-5GHZ-M15-CROSSBAND-BENCH`).
"""

from __future__ import annotations

import json
from pathlib import Path

from controller.openwisp_controller_api_bridge import (
    APPROVED_PROFILE_SET_SHA256,
    validate_device_monitoring,
)
from tools.serve_openwisp_dual_nms_live import (
    OPENWRT_TOH_LINKS,
    PORTAL_HTML_OUT,
    build_openwisp_dual_nms_registry,
    build_openwisp_portal_html,
)

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_JSON = ROOT / "artifacts" / "autoresearch" / "stage35a_openwisp_portal_and_m15_5ghz_bench_20261025.json"
REPORT_MD = ROOT / "docs" / "STAGE35A_LIVE_OPENWISP_PORTAL_AND_M15_5GHZ_BENCHMARK.md"


def test_stage35a_s35a_r1_crossband_benchmark_receipt() -> None:
    assert RECEIPT_JSON.exists(), f"Missing Stage 35A receipt: {RECEIPT_JSON}"
    data = json.loads(RECEIPT_JSON.read_text(encoding="utf-8"))
    assert data["task_id"] == "T-S35A-LIVE-OPENWISP-PORTAL-SERVER-AND-5GHZ-M15-CROSSBAND-BENCH"
    assert data["flash_writes"] == 0

    rounds = data["rounds"]
    assert len(rounds) == 1
    r1 = rounds[0]
    assert r1["round_id"] == "S35A-R1"
    assert r1["mechanism_id"] == "M15_5GHz"
    assert r1["decision"] == "PROMOTE_NEW_CHAMPION"
    assert r1["promoted"] is True
    assert r1["claim_status"] == "CONFIRMED"
    assert r1["goodput_delta_pct"] > 0.0
    assert r1["p95_rtt_delta_pct"] < -10.0
    assert set(r1["phases"].keys()) == {"A1", "B1", "A2", "B2"}
    assert "5\t0\t0" in r1["phases"]["B1"]["getter_readback"]["r198_ff_mcast_airtime_limit"]
    assert "5\t0\t0" in r1["phases"]["B2"]["getter_readback"]["r198_ff_mcast_airtime_limit"]


def test_openwisp_dual_nms_registry_all_8_devices() -> None:
    reg = build_openwisp_dual_nms_registry()
    assert reg["approved_profile_set_sha256"] == APPROVED_PROFILE_SET_SHA256
    assert reg["templates_count"] == 8
    assert reg["devices_count"] == 8
    assert len(reg["openwrt_toh_links"]) == 5

    expected_keys = {
        "lap120_ap_openwrt",
        "loco5ac_cpe_openwrt",
        "r5ac_prism_cpe_airos8",
        "lbm5_xw_cpe_airos6",
        "r2ac_prism_ap_airos8_24ghz",
        "nanoloco_m2_xm_cpe_24ghz",
        "ltu_lite_1_amesoc",
        "ltu_lite_2_amesoc",
    }
    actual_keys = {d["device_key"] for d in reg["devices"]}
    assert actual_keys == expected_keys

    for d in reg["devices"]:
        assert len(d["openwisp_controller"]["configuration_checksum"]) == 64
        assert validate_device_monitoring(d["openwisp_monitoring"]["netjson_monitoring"]) is True
        assert d["uisp_udapi_bridge"]["unms_status"] == 2
        assert d["uisp_udapi_bridge"]["envelope_version"] == "2.0"


def test_openwisp_portal_html_generation_and_toh_links() -> None:
    out_path = build_openwisp_portal_html()
    assert out_path == PORTAL_HTML_OUT
    assert out_path.exists()
    html = out_path.read_text(encoding="utf-8")
    assert len(html) > 50_000
    for toh in OPENWRT_TOH_LINKS:
        assert toh["url"] in html
    assert "fmx-openwisp-dual-nms-registry" in html


def test_stage35a_markdown_report_exists() -> None:
    assert REPORT_MD.exists(), f"Missing Stage 35A report: {REPORT_MD}"
    text = REPORT_MD.read_text(encoding="utf-8")
    for token in (
        "S35A-R1",
        "M15_5GHz",
        "PROMOTE_NEW_CHAMPION",
        "OPENWISP_DUAL_NMS_PORTAL.html",
        "multicast_to_unicast",
        "ff_mcast_airtime_limit",
    ):
        assert token in text, f"Missing token {token} in Stage 35A report"
