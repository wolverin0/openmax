"""
Stage 50C Verification Suite (`tests/test_stage50c_champion_v16_integration.py`)
===============================================================================
Validates `T-S50C-GEM2-STAGE46A-CHAMPION-V16-TX-BIAS-2-AND-STAGE47B-LTU-OTA-PACKAGER`:
1. `validate_stage46a_tx_bias_2_dynamic_bql_and_lbm5_budget_guard` in both
   `controller.openwrt_ptmp_2cpe_aqm_profile` and `controller.airos_stock_champ_profile`
   enforcing:
   - `dev_weight_tx_bias == 2` at full `netdev_budget == 600` on OpenWrt (`S46A-R3` Champion v16)
   - dynamic kernel `dql` BQL on `ag71xx` `eth0` (rejecting static `limit_max` overrides per `S46A-R1/R5`)
   - `lbm5_netdev_budget == 300` on 400 MHz AR934x `airOS 6` (`S46A-R6` proved `600` inflates p95 RTT `+8.84%`)
2. `export_openwisp_tx_bias_2_dynamic_bql_champion_v16_netjson_template` and
   `load_empirical_stage46a_and_stage47b_champion_v16_evidence` in both profile modules encoding
   `S46A-R3` (`M29b_PURE_DEV_WEIGHT_TX_BIAS_2_AT_FULL_BUDGET_600`: `+3.489%` goodput `39.642 -> 41.025 Mbps`,
   `-6.291%` p95 RTT `90.986 -> 85.262 ms`, `-6.113%` p99 RTT `95.257 -> 89.434 ms`, `-17.703%` Dual IPTV
   jitter `2.412 -> 1.985 ms`, `-5.206%` VoIP jitter `2.689 -> 2.549 ms`, Pareto `+5.6906%`) and `Stage 47B`
   (`FMX-LTU` 7-byte SSID + `5500 5520` DCXO + `+15 dBm`: `5.1s` OTA association `AP-PTMP(Run)` <-> `CPE-PTMP(Run)`,
   `TA=235`, `SpectrumEfficient=1535/1319` 1024-QAM MIMO, `61.4/79.1 Mbps` DL & `41.9 Mbps` UL).
3. `controller.futuramax_openwrt_imagebuilder_packager` & `firmware.openwrt.futuramax_openwrt_imagebuilder_packager`
   with `render_uci_defaults_98_futuramax_champion_v16_aqm()` and writing
   `artifacts/autoresearch/stage50c_imagebuilder_champion_v16_manifest_20261025.json`.
4. `controller.closed_loop_research_reactor` (`ingest_stage46a_and_stage47b_and_synthesize_m34_m35`)
   ingesting `S46A-R1..R6` and `S47B-LTU-OTA` and synthesizing `M34` and `M35` into
   `artifacts/autoresearch/stage50c_closed_loop_reactor_champion_v16_20261025.json`.
5. `/api/v1/controller/template/champion-v16-aqm/` and Card `a8)` in
   `tools.nms.serve_openwisp_dual_nms_live` and `OPENWISP_DUAL_NMS_PORTAL.html`.
"""
from __future__ import annotations

import io
import json

from controller.airos_stock_champ_profile import (
    CHAMPION_V16_MECHANISM_ID as AIROS_V16_MECH,
    CHAMPION_V16_PROFILE_ID as AIROS_V16_PROF,
    CHAMPION_V16_ROUND_ID as AIROS_V16_ROUND,
    export_openwisp_tx_bias_2_dynamic_bql_champion_v16_netjson_template as export_v16_airos,
    load_empirical_stage46a_and_stage47b_champion_v16_evidence as load_v16_airos,
    validate_stage46a_tx_bias_2_dynamic_bql_and_lbm5_budget_guard as validate_v16_guard_airos,
)
from controller.closed_loop_research_reactor import (
    STAGE50C_REACTOR_V16_RECEIPT_JSON,
    ingest_stage46a_and_stage47b_and_synthesize_m34_m35,
)
from controller.futuramax_openwrt_imagebuilder_packager import (
    STAGE50C_OUTPUT_JSON,
    generate_stage50c_imagebuilder_champion_v16_manifest,
    render_uci_defaults_98_futuramax_champion_v16_aqm,
)
from controller.openwrt_ptmp_2cpe_aqm_profile import (
    CHAMPION_V16_MECHANISM_ID as OWRT_V16_MECH,
    CHAMPION_V16_PROFILE_ID as OWRT_V16_PROF,
    CHAMPION_V16_ROUND_ID as OWRT_V16_ROUND,
    export_openwisp_tx_bias_2_dynamic_bql_champion_v16_netjson_template as export_v16_openwrt,
    load_empirical_stage46a_and_stage47b_champion_v16_evidence as load_v16_openwrt,
    render_openwrt_tx_bias_2_dynamic_bql_champion_v16_script,
    validate_stage46a_tx_bias_2_dynamic_bql_and_lbm5_budget_guard as validate_v16_guard_openwrt,
)
from tools.nms.serve_openwisp_dual_nms_live import (
    PORTAL_HTML_OUT,
    OpenWispDualNmsHandler,
    build_iptv_and_capacity_ceiling_api_payload,
    build_openwisp_portal_html,
    export_openwisp_tx_bias_2_dynamic_bql_champion_v16_netjson_template as export_v16_nms,
)


def test_stage46a_tx_bias_2_dynamic_bql_and_lbm5_budget_guard_accepts_champion_v16() -> None:
    assert OWRT_V16_PROF == AIROS_V16_PROF == "openwrt_tx_bias_2_dynamic_bql_champion_v16"
    assert OWRT_V16_ROUND == AIROS_V16_ROUND == "S46A-R3"
    assert OWRT_V16_MECH == AIROS_V16_MECH == "M29b_PURE_DEV_WEIGHT_TX_BIAS_2_AT_FULL_BUDGET_600"

    res = validate_v16_guard_openwrt(
        dev_weight_tx_bias=2,
        netdev_budget=600,
        ag71xx_bql_mode="dynamic_dql",
        lbm5_netdev_budget=300,
    )
    assert res == validate_v16_guard_airos(
        dev_weight_tx_bias=2,
        netdev_budget=600,
        ag71xx_bql_mode={"limit_min": 0, "limit_max": 1879048192, "hold_time": 1000},
        lbm5_netdev_budget=300,
    )
    assert res["valid"] is True
    assert res["violation_count"] == 0
    assert res["dev_weight_tx_bias"] == 2
    assert res["netdev_budget"] == 600
    assert res["ag71xx_bql_mode"] == "dynamic_dql"
    assert res["lbm5_netdev_budget"] == 300


def test_stage46a_guard_rejects_tx_bias_1_budget_300_static_bql_or_lbm5_budget_600() -> None:
    # 1. Wrong dev_weight_tx_bias (1 instead of 2) or halved OpenWrt netdev_budget (300 from S44A-R3)
    res_bias = validate_v16_guard_openwrt(
        dev_weight_tx_bias=1,
        netdev_budget=300,
        ag71xx_bql_mode="dynamic_dql",
        lbm5_netdev_budget=300,
    )
    assert res_bias["valid"] is False
    assert any("OPENWRT_DEV_WEIGHT_TX_BIAS_MISMATCH" in v for v in res_bias["violations"])
    assert any("OPENWRT_NETDEV_BUDGET_MISMATCH" in v for v in res_bias["violations"])

    # 2. Static ag71xx BQL limit_max overrides (S46A-R1 24576 or S46A-R5 65536)
    for bad_bql in (
        "static_limit_max_24576",
        "M28b_65536",
        {"limit_min": 3028, "limit_max": 24576, "hold_time": 500},
        {"limit_min": 4542, "limit_max": 65536, "hold_time": 1000},
    ):
        res_bql = validate_v16_guard_airos(
            dev_weight_tx_bias=2,
            netdev_budget=600,
            ag71xx_bql_mode=bad_bql,
            lbm5_netdev_budget=300,
        )
        assert res_bql["valid"] is False
        assert any("AG71XX_STATIC_BQL_OVERRIDE_REJECTED" in v for v in res_bql["violations"])

    # 3. LiteBeam M5 400 MHz AR934x netdev_budget=600 (S46A-R6 proved +8.84% p95 RTT inflation)
    res_lbm5 = validate_v16_guard_openwrt(
        dev_weight_tx_bias=2,
        netdev_budget=600,
        ag71xx_bql_mode="dynamic_dql",
        lbm5_netdev_budget=600,
    )
    assert res_lbm5["valid"] is False
    assert any("LBM5_AR934X_400MHZ_NETDEV_BUDGET_MISMATCH" in v for v in res_lbm5["violations"])


def test_champion_v16_evidence_and_netjson_template_match_s46a_r3_and_s47b() -> None:
    ev = load_v16_openwrt()
    assert ev == load_v16_airos()

    r1 = ev["s46a_r1_static_bql_24576_refuted"]
    assert r1["round_id"] == "S46A-R1"
    assert r1["goodput_delta_pct"] == -0.977

    r5 = ev["s46a_r5_static_bql_65536_min_4542_refuted"]
    assert r5["round_id"] == "S46A-R5"
    assert r5["goodput_delta_pct"] == -10.267

    r6 = ev["s46a_r6_lbm5_400mhz_budget_600_refuted"]
    assert r6["round_id"] == "S46A-R6"
    assert r6["p95_rtt_delta_pct"] == 8.839

    r3 = ev["s46a_r3_champion_v16_promoted"]
    assert r3["round_id"] == "S46A-R3"
    assert r3["mechanism_id"] == "M29b_PURE_DEV_WEIGHT_TX_BIAS_2_AT_FULL_BUDGET_600"
    assert r3["arm_a_mean_goodput_mbps"] == 39.642
    assert r3["arm_b_mean_goodput_mbps"] == 41.025
    assert r3["goodput_delta_pct"] == 3.489
    assert r3["arm_a_mean_p95_rtt_ms"] == 90.986
    assert r3["arm_b_mean_p95_rtt_ms"] == 85.262
    assert r3["p95_rtt_delta_pct"] == -6.291
    assert r3["arm_a_mean_p99_rtt_ms"] == 95.257
    assert r3["arm_b_mean_p99_rtt_ms"] == 89.434
    assert r3["p99_rtt_delta_pct"] == -6.113
    assert r3["iptv_arm_a_mean_jitter_ms"] == 2.412
    assert r3["iptv_arm_b_mean_jitter_ms"] == 1.985
    assert r3["iptv_jitter_delta_pct"] == -17.703
    assert r3["voip_arm_a_mean_jitter_ms"] == 2.689
    assert r3["voip_arm_b_mean_jitter_ms"] == 2.549
    assert r3["voip_jitter_delta_pct"] == -5.206
    assert r3["pareto_score_delta_pct"] == 5.6906

    ota = ev["stage47b_ltu_ota_1024qam_verification"]
    assert ota["ssid"] == "FMX-LTU"
    assert ota["ota_lock_time_s"] == 5.1
    assert ota["ap_role"] == "AP-PTMP(Run)"
    assert ota["cpe_role"] == "CPE-PTMP(Run)"
    assert ota["timing_advance_ta"] == 235
    assert ota["ap_spectrum_efficient"] == 1535
    assert ota["cpe_spectrum_efficient"] == 1319
    assert ota["dl_mean_mbps"] == 61.4
    assert ota["dl_peak_mbps"] == 79.1
    assert ota["ul_mean_mbps"] == 41.9
    assert ota["aggregate_20mhz_goodput_mbps"] == 103.3

    tpl = export_v16_openwrt()
    assert tpl == export_v16_airos()
    assert tpl == export_v16_nms()
    assert tpl["stage"] == "50C"
    assert "v16" in tpl["champion_version"]
    assert len(tpl["profile_sha256"]) == 64
    assert tpl["stage46a_tx_bias_2_dynamic_bql_and_lbm5_budget_guard"]["valid"] is True

    script = render_openwrt_tx_bias_2_dynamic_bql_champion_v16_script()
    assert "net.core.dev_weight_tx_bias=2" in script
    assert "net.core.netdev_budget=600" in script
    assert "echo 1879048192 > /sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit_max" in script
    assert "sysctl -w net.core.netdev_budget=300" in script


def test_imagebuilder_champion_v16_sets_tx_bias_2_and_writes_stage50c_manifest() -> None:
    uci_v16 = render_uci_defaults_98_futuramax_champion_v16_aqm("ubnt_lap-120")
    assert "net.core.dev_weight_tx_bias=2" in uci_v16
    assert "net.core.netdev_budget=600" in uci_v16
    assert "echo 1000 > /sys/class/net/eth0/tx_queue_len" in uci_v16
    assert "echo 1879048192 > /sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit_max" in uci_v16
    assert "echo 256 > /sys/class/net/br-lan/tx_queue_len" in uci_v16

    manifest = generate_stage50c_imagebuilder_champion_v16_manifest()
    assert STAGE50C_OUTPUT_JSON.exists()
    assert manifest["stage"] == "50C"
    assert "v16" in manifest["champion_version"]
    assert len(manifest["targets"]) == 4
    assert manifest["stage46a_tx_bias_2_dynamic_bql_and_lbm5_budget_guard"]["valid"] is True
    assert manifest["stage46a_tx_bias_2_dynamic_bql_and_lbm5_budget_guard"]["dev_weight_tx_bias"] == 2
    for t in manifest["targets"].values():
        v16_contents = t["overlay_files"]["files/etc/uci-defaults/98-futuramax-champion-v16-aqm"]["contents"]
        assert "net.core.dev_weight_tx_bias=2" in v16_contents
        assert "echo 1000 > /sys/class/net/eth0/tx_queue_len" in v16_contents


def test_closed_loop_reactor_ingests_stage46a_and_stage47b_and_synthesizes_m34_m35() -> None:
    receipt = ingest_stage46a_and_stage47b_and_synthesize_m34_m35()
    assert STAGE50C_REACTOR_V16_RECEIPT_JSON.exists()
    loaded = json.loads(STAGE50C_REACTOR_V16_RECEIPT_JSON.read_text(encoding="utf-8"))
    assert loaded["stage"] == "50C"
    assert loaded["champion_version"] == "v16"
    assert loaded["champion_round_id"] == "S46A-R3"
    assert loaded["champion_mechanism_id"] == "M29b_PURE_DEV_WEIGHT_TX_BIAS_2_AT_FULL_BUDGET_600"
    round_ids = [e["round_id"] for e in loaded["ingested_reactor_events"]]
    assert round_ids == ["S46A-R1", "S46A-R2", "S46A-R3", "S46A-R4", "S46A-R5", "S46A-R6", "S47B-LTU-OTA"]
    mids = [m["mechanism_id"] for m in receipt["next_wave_mechanisms_m34_to_m35"]]
    assert mids == ["M34", "M35"]


def test_openwisp_portal_exposes_champion_v16_aqm_endpoint_and_card_a8() -> None:
    cap = build_iptv_and_capacity_ceiling_api_payload()
    assert "openwisp_tx_bias_2_dynamic_bql_champion_v16_template" in cap
    assert "stage46a_and_stage47b_champion_v16_evidence" in cap
    assert cap["stage50c_tx_bias_2_dynamic_bql_and_lbm5_budget_guard"]["valid"] is True

    out_html = build_openwisp_portal_html()
    assert out_html == PORTAL_HTML_OUT
    html_text = out_html.read_text(encoding="utf-8")
    assert "a8) Stage 50C" in html_text
    assert "FMX openwrt_tx_bias_2_dynamic_bql_champion_v16" in html_text
    assert "SpectrumEfficient=1535/1319" in html_text

    # Verify HTTP GET /api/v1/controller/template/champion-v16-aqm/ handler directly
    handler = OpenWispDualNmsHandler.__new__(OpenWispDualNmsHandler)
    handler.path = "/api/v1/controller/template/champion-v16-aqm/"
    handler.wfile = io.BytesIO()
    status_codes: list[int] = []
    handler.send_response = lambda code: status_codes.append(code)  # type: ignore[assignment]
    handler.send_header = lambda k, v: None  # type: ignore[assignment]
    handler.end_headers = lambda: None  # type: ignore[assignment]
    handler.do_GET()

    assert status_codes == [200]
    body = json.loads(handler.wfile.getvalue().decode("utf-8"))
    assert body["name"] == "FMX openwrt_tx_bias_2_dynamic_bql_champion_v16"
    assert body["stage"] == "50C"
    assert body["stage46a_tx_bias_2_dynamic_bql_and_lbm5_budget_guard"]["valid"] is True
