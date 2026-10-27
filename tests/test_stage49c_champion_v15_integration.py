"""
Stage 49C Verification Suite (`tests/test_stage49c_champion_v15_integration.py`)
===============================================================================
Validates `T-S49C-GEM2-STAGE44A-CHAMPION-V15-AND-LTU-16BYTE-SSID-PACKAGER`:
1. `validate_stage44a_bql_eth0_and_ltu_16byte_ssid_guard` in both
   `controller.openwrt_ptmp_2cpe_aqm_profile` and `controller.airos_stock_champ_profile`
   enforcing:
   - `openwrt_eth0_txq == 1000` (hardware BQL `limit=54250/1780` on `ag71xx`; `S44A-R1` proved `256`
     regresses goodput `-1.99%` and p95 RTT `+7.82%`)
   - `openwrt_br_wds_txq == 256`
   - `r5ac_br0_txq == 256`
   - `r5ac_netdev_budget == 600`
   - `1 <= len(ltu_ssid.encode('utf-8')) <= 16` (`Stage 45B` `ame_core_beacon_update @ 0x007008`
     `[s_beacon, #0x0e..0x1d]` vs `slm_find_preferred_record @ 0x045e20` `strcmp`)
   - alternating adjacent frequencies in `ltu_freq_list` (preventing `cpeFsmStart @ 0x048000` Quick TCXO)
2. `export_openwisp_bql_eth0_r5ac_txq256_champion_v15_netjson_template` and
   `load_empirical_stage44a_and_stage45b_champion_v15_evidence` in both profile modules encoding
   `S44A-R5` (`M26b_PURE_R5AC_BR0_TXQ_256_OPENWRT_ETH0_1000`: `+7.14%` goodput `32.998 -> 35.354 Mbps`,
   `-3.62%` [`-3.618%`] p95 RTT `85.782 -> 82.678 ms`, `-12.86%` p99 RTT `97.689 -> 85.123 ms`,
   `0.00%` Dual IPTV loss, `0.00%` VoIP loss, Pareto `+8.4063%`) and `Stage 45B` (`FMX-LTU` 7-byte SSID
   + `5500 5520 5500 5520` full DCXO calibration + `board_ssid=0xae08` `intmode=1`).
3. `controller.futuramax_openwrt_imagebuilder_packager` & `firmware.openwrt.futuramax_openwrt_imagebuilder_packager`
   with `render_uci_defaults_98_futuramax_champion_v15_aqm()` explicitly preserving
   `/sys/class/net/eth0/tx_queue_len=1000` while setting `br-lan` and `phy0-ap0*` to `256`,
   and writing `artifacts/autoresearch/stage49c_imagebuilder_champion_v15_manifest_20261025.json`.
4. `controller.closed_loop_research_reactor` (`ingest_stage44a_and_stage45b_and_synthesize_m32_m33`)
   ingesting `S44A-R1..R5` and `S45B-LTU-SSID` and synthesizing `M32` and `M33` into
   `artifacts/autoresearch/stage49c_closed_loop_reactor_champion_v15_20261025.json`.
5. `/api/v1/controller/template/champion-v15-aqm/` and Card `a7)` in
   `tools.nms.serve_openwisp_dual_nms_live` and `OPENWISP_DUAL_NMS_PORTAL.html`.
"""
from __future__ import annotations

import io
import json

from controller.airos_stock_champ_profile import (
    CHAMPION_V15_MECHANISM_ID as AIROS_V15_MECH,
    CHAMPION_V15_PROFILE_ID as AIROS_V15_PROF,
    CHAMPION_V15_ROUND_ID as AIROS_V15_ROUND,
    export_openwisp_bql_eth0_r5ac_txq256_champion_v15_netjson_template as export_v15_airos,
    load_empirical_stage44a_and_stage45b_champion_v15_evidence as load_v15_airos,
    validate_stage44a_bql_eth0_and_ltu_16byte_ssid_guard as validate_v15_guard_airos,
)
from controller.closed_loop_research_reactor import (
    STAGE49C_REACTOR_V15_RECEIPT_JSON,
    ingest_stage44a_and_stage45b_and_synthesize_m32_m33,
)
from controller.futuramax_openwrt_imagebuilder_packager import (
    STAGE49C_OUTPUT_JSON,
    generate_stage49c_imagebuilder_champion_v15_manifest,
    render_hotplug_99_futuramax_wds_dms,
    render_uci_defaults_98_futuramax_champion_v15_aqm,
)
from controller.openwrt_ptmp_2cpe_aqm_profile import (
    CHAMPION_V15_MECHANISM_ID as OWRT_V15_MECH,
    CHAMPION_V15_PROFILE_ID as OWRT_V15_PROF,
    CHAMPION_V15_ROUND_ID as OWRT_V15_ROUND,
    export_openwisp_bql_eth0_r5ac_txq256_champion_v15_netjson_template as export_v15_openwrt,
    load_empirical_stage44a_and_stage45b_champion_v15_evidence as load_v15_openwrt,
    render_openwrt_bql_eth0_r5ac_txq256_champion_v15_script,
    validate_stage44a_bql_eth0_and_ltu_16byte_ssid_guard as validate_v15_guard_openwrt,
)
from tools.nms.serve_openwisp_dual_nms_live import (
    PORTAL_HTML_OUT,
    OpenWispDualNmsHandler,
    build_iptv_and_capacity_ceiling_api_payload,
    build_openwisp_portal_html,
    export_openwisp_bql_eth0_r5ac_txq256_champion_v15_netjson_template as export_v15_nms,
)


def test_stage44a_bql_eth0_and_ltu_16byte_ssid_guard_accepts_champion_v15_and_fmx_ltu() -> None:
    assert OWRT_V15_PROF == AIROS_V15_PROF == "openwrt_bql_eth0_1000_r5ac_txq256_champion_v15"
    assert OWRT_V15_ROUND == AIROS_V15_ROUND == "S44A-R5"
    assert OWRT_V15_MECH == AIROS_V15_MECH == "M26b_PURE_R5AC_BR0_TXQ_256_OPENWRT_ETH0_1000"

    res = validate_v15_guard_openwrt(
        openwrt_eth0_txq=1000,
        openwrt_br_wds_txq=256,
        r5ac_br0_txq=256,
        r5ac_netdev_budget=600,
        ltu_ssid="FMX-LTU",
        ltu_freq_list="5500 5520 5500 5520",
    )
    assert res == validate_v15_guard_airos(
        openwrt_eth0_txq=1000,
        openwrt_br_wds_txq=256,
        r5ac_br0_txq=256,
        r5ac_netdev_budget=600,
        ltu_ssid="FMX-LTU",
        ltu_freq_list=[5500, 5520, 5500, 5520],
    )
    assert res["valid"] is True
    assert res["violation_count"] == 0
    assert res["openwrt_eth0_txq"] == 1000
    assert res["openwrt_br_wds_txq"] == 256
    assert res["r5ac_br0_txq"] == 256
    assert res["r5ac_netdev_budget"] == 600
    assert res["ltu_ssid"] == "FMX-LTU"
    assert res["ltu_ssid_utf8_len"] == 7
    assert res["ltu_freq_list"] == [5500, 5520, 5500, 5520]


def test_stage44a_guard_rejects_eth0_256_bad_r5ac_or_19byte_ltu_ssid_or_consecutive_freqs() -> None:
    # 1. Shrinking OpenWrt eth0 tx_queue_len to 256 (S44A-R1 BQL conflict)
    res_eth0 = validate_v15_guard_openwrt(
        openwrt_eth0_txq=256,
        openwrt_br_wds_txq=256,
        r5ac_br0_txq=256,
        r5ac_netdev_budget=600,
        ltu_ssid="FMX-LTU",
        ltu_freq_list="5500 5520 5500 5520",
    )
    assert res_eth0["valid"] is False
    assert any("OPENWRT_ETH0_BQL_TXQ_MISMATCH" in v for v in res_eth0["violations"])

    # 2. Wrong br-lan/WDS txq or R5AC br0 txq or R5AC netdev_budget
    res_r5ac = validate_v15_guard_airos(
        openwrt_eth0_txq=1000,
        openwrt_br_wds_txq=1000,
        r5ac_br0_txq=1000,
        r5ac_netdev_budget=300,
        ltu_ssid="FMX-LTU",
        ltu_freq_list="5500 5520 5500 5520",
    )
    assert res_r5ac["valid"] is False
    assert any("OPENWRT_BR_WDS_TXQ_MISMATCH" in v for v in res_r5ac["violations"])
    assert any("R5AC_BR0_TXQ_MISMATCH" in v for v in res_r5ac["violations"])
    assert any("R5AC_NETDEV_BUDGET_MISMATCH" in v for v in res_r5ac["violations"])

    # 3. 19-byte SSID 'FuturaMAX-LTU-Bench' (> 16 bytes truncated by ame_core_beacon_update @ 0x007008) or empty SSID
    for bad_ssid in ("FuturaMAX-LTU-Bench", ""):
        res_ssid = validate_v15_guard_openwrt(
            openwrt_eth0_txq=1000,
            openwrt_br_wds_txq=256,
            r5ac_br0_txq=256,
            r5ac_netdev_budget=600,
            ltu_ssid=bad_ssid,
            ltu_freq_list="5500 5520 5500 5520",
        )
        assert res_ssid["valid"] is False
        assert any("LTU_BEACON_16BYTE_SSID_TRUNCATION" in v for v in res_ssid["violations"])

    # 4. Consecutive identical frequencies '5500 5500 5500 5500' (triggers Quick TCXO in cpeFsmStart @ 0x048000)
    res_freq = validate_v15_guard_airos(
        openwrt_eth0_txq=1000,
        openwrt_br_wds_txq=256,
        r5ac_br0_txq=256,
        r5ac_netdev_budget=600,
        ltu_ssid="FMX-LTU",
        ltu_freq_list="5500 5500 5500 5500",
    )
    assert res_freq["valid"] is False
    assert any("LTU_QUICK_TCXO_CONSECUTIVE_FREQ_TRAP" in v for v in res_freq["violations"])


def test_champion_v15_evidence_and_netjson_template_match_s44a_r5_and_s45b() -> None:
    ev = load_v15_openwrt()
    assert ev == load_v15_airos()
    r1 = ev["s44a_r1_openwrt_eth0_txq256_bql_conflict_refuted"]
    assert r1["round_id"] == "S44A-R1"
    assert r1["goodput_delta_pct"] == -1.985
    assert r1["p95_rtt_delta_pct"] == 7.822
    assert r1["hardware_bql_limit"] == "54250/1780"

    r5 = ev["s44a_r5_champion_v15_promoted"]
    assert r5["round_id"] == "S44A-R5"
    assert r5["mechanism_id"] == "M26b_PURE_R5AC_BR0_TXQ_256_OPENWRT_ETH0_1000"
    assert r5["arm_a_mean_goodput_mbps"] == 32.998
    assert r5["arm_b_mean_goodput_mbps"] == 35.354
    assert r5["goodput_delta_pct"] == 7.14
    assert r5["arm_a_mean_p95_rtt_ms"] == 85.782
    assert r5["arm_b_mean_p95_rtt_ms"] == 82.678
    assert r5["p95_rtt_delta_pct"] == -3.618
    assert r5["arm_a_mean_p99_rtt_ms"] == 97.689
    assert r5["arm_b_mean_p99_rtt_ms"] == 85.123
    assert r5["p99_rtt_delta_pct"] == -12.86
    assert r5["iptv_loss_pct"] == 0.0
    assert r5["voip_loss_pct"] == 0.0
    assert r5["pareto_score_delta_pct"] == 8.4063

    ltu = ev["stage45b_ltu_16byte_ssid_and_dcxo_fix"]
    assert ltu["new_ssid"] == "FMX-LTU"
    assert ltu["new_ssid_len_bytes"] == 7
    assert ltu["new_freq_list"] == "5500 5520 5500 5520"
    assert ltu["board_ssid"] == "0xae08"
    assert ltu["intmode"] == 1
    assert ltu["ssid_exact_match"] is True

    tpl = export_v15_openwrt()
    assert tpl == export_v15_airos()
    assert tpl == export_v15_nms()
    assert tpl["stage"] == "49C"
    assert "v15" in tpl["champion_version"]
    assert len(tpl["profile_sha256"]) == 64
    assert tpl["stage44a_bql_eth0_and_ltu_16byte_ssid_guard"]["valid"] is True

    script = render_openwrt_bql_eth0_r5ac_txq256_champion_v15_script()
    assert "echo 1000 > /sys/class/net/eth0/tx_queue_len" in script
    assert "/sys/class/net/br-lan/tx_queue_len" in script
    assert "/sys/class/net/phy0-ap0*/tx_queue_len" in script
    assert "/sys/class/net/br0/tx_queue_len" in script
    assert "net.core.netdev_budget=600" in script


def test_imagebuilder_champion_v15_preserves_eth0_1000_and_writes_stage49c_manifest() -> None:
    uci_v15 = render_uci_defaults_98_futuramax_champion_v15_aqm("ubnt_lap-120")
    hotplug_wds = render_hotplug_99_futuramax_wds_dms()
    assert "echo 1000 > /sys/class/net/eth0/tx_queue_len" in uci_v15
    assert "echo 256 > /sys/class/net/br-lan/tx_queue_len" in uci_v15
    assert "/sys/class/net/phy0-ap0*/tx_queue_len" in uci_v15
    assert "echo 1000 > /sys/class/net/eth0/tx_queue_len" in hotplug_wds
    assert "echo 256 > /sys/class/net/br-lan/tx_queue_len" in hotplug_wds

    manifest = generate_stage49c_imagebuilder_champion_v15_manifest()
    assert STAGE49C_OUTPUT_JSON.exists()
    assert manifest["stage"] == "49C"
    assert "v15" in manifest["champion_version"]
    assert len(manifest["targets"]) == 4
    assert manifest["stage44a_bql_eth0_and_ltu_16byte_ssid_guard"]["valid"] is True
    assert manifest["stage44a_bql_eth0_and_ltu_16byte_ssid_guard"]["openwrt_eth0_txq"] == 1000
    for t in manifest["targets"].values():
        v15_contents = t["overlay_files"]["files/etc/uci-defaults/98-futuramax-champion-v15-aqm"]["contents"]
        assert "echo 1000 > /sys/class/net/eth0/tx_queue_len" in v15_contents
        assert "echo 256 > /sys/class/net/br-lan/tx_queue_len" in v15_contents


def test_closed_loop_reactor_ingests_stage44a_and_stage45b_and_synthesizes_m32_m33() -> None:
    receipt = ingest_stage44a_and_stage45b_and_synthesize_m32_m33()
    assert STAGE49C_REACTOR_V15_RECEIPT_JSON.exists()
    loaded = json.loads(STAGE49C_REACTOR_V15_RECEIPT_JSON.read_text(encoding="utf-8"))
    assert loaded["stage"] == "49C"
    assert loaded["champion_version"] == "v15"
    assert loaded["champion_round_id"] == "S44A-R5"
    assert loaded["champion_mechanism_id"] == "M26b_PURE_R5AC_BR0_TXQ_256_OPENWRT_ETH0_1000"
    round_ids = [e["round_id"] for e in loaded["ingested_reactor_events"]]
    assert round_ids == ["S44A-R1", "S44A-R2", "S44A-R3", "S44A-R4", "S44A-R5", "S45B-LTU-SSID"]
    mids = [m["mechanism_id"] for m in receipt["next_wave_mechanisms_m32_to_m33"]]
    assert mids == ["M32", "M33"]


def test_openwisp_portal_exposes_champion_v15_aqm_endpoint_and_card_a7() -> None:
    cap = build_iptv_and_capacity_ceiling_api_payload()
    assert "openwisp_bql_eth0_r5ac_txq256_champion_v15_template" in cap
    assert "stage44a_and_stage45b_champion_v15_evidence" in cap
    assert cap["stage49c_bql_eth0_and_ltu_16byte_ssid_guard"]["valid"] is True

    out_html = build_openwisp_portal_html()
    assert out_html == PORTAL_HTML_OUT
    html_text = out_html.read_text(encoding="utf-8")
    assert "a7) Stage 49C" in html_text
    assert "FMX openwrt_bql_eth0_1000_r5ac_txq256_champion_v15" in html_text
    assert "FMX-LTU" in html_text

    # Verify HTTP GET /api/v1/controller/template/champion-v15-aqm/ handler directly
    handler = OpenWispDualNmsHandler.__new__(OpenWispDualNmsHandler)
    handler.path = "/api/v1/controller/template/champion-v15-aqm/"
    handler.wfile = io.BytesIO()
    status_codes: list[int] = []
    handler.send_response = lambda code: status_codes.append(code)  # type: ignore[assignment]
    handler.send_header = lambda k, v: None  # type: ignore[assignment]
    handler.end_headers = lambda: None  # type: ignore[assignment]
    handler.do_GET()

    assert status_codes == [200]
    body = json.loads(handler.wfile.getvalue().decode("utf-8"))
    assert body["name"] == "FMX openwrt_bql_eth0_1000_r5ac_txq256_champion_v15"
    assert body["stage"] == "49C"
    assert body["stage44a_bql_eth0_and_ltu_16byte_ssid_guard"]["valid"] is True
