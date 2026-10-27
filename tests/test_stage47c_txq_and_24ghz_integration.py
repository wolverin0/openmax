"""
Stage 47C Verification Suite (`tests/test_stage47c_txq_and_24ghz_integration.py`)
=================================================================================
Validates `T-S47C-GEM2-STAGE40A-42A-NETDEV-TXQ-GUARD-AND-24GHZ-M18-PACKAGER`:
1. `validate_openwrt_netdev_txq_and_airos6_unpolled_guard` in both
   `controller.openwrt_ptmp_2cpe_aqm_profile` and `controller.airos_stock_champ_profile`
   enforcing Stage 42A physical laws (`tx_queue_len >= 512`, `netdev_max_backlog <= 1500`,
   and unpolled `airOS 6` `XW` `ubnt_poll` `txop_params == '0 0'` & `no_ack_rate == 0`).
2. `export_r2ac_24ghz_m18_iptv_netjson_template` in `controller.airos_stock_champ_profile`
   encoding Stage 40A `R2AC` 2.4 GHz `M18` (`ff_mcast_airtime_limit=5` written last,
   `IGMPv2=2`, `multicast_fast_leave=1`, `512 KB` `tcp_wmem`, `0.00%` IPTV/VoIP loss).
3. `controller.futuramax_openwrt_imagebuilder_packager` & `firmware.openwrt.futuramax_openwrt_imagebuilder_packager`
   preserving `/sys/class/net/br-lan/tx_queue_len=1000` and `/sys/class/net/phy0-ap0*/tx_queue_len=1000`
   in `98-futuramax-champion-v13-aqm` and `99-futuramax-wds-dms` with zero broken BusyBox
   `ip link set txqueuelen` calls, and generating `stage47c_imagebuilder_txq1000_manifest_20261025.json`.
4. `controller.closed_loop_research_reactor` (`ingest_stage40a_and_stage42a_and_synthesize_m28_m29`)
   ingesting `S40A-R1`, `S40A-R2`, `S42A-R1..R4` and synthesizing `M28` and `M29` into
   `stage47c_closed_loop_reactor_s40a_s42a_ingestion_20261025.json`.
5. `/api/v1/controller/template/stage47c-guards/` and Card `a5)` in
   `tools.nms.serve_openwisp_dual_nms_live` and `OPENWISP_DUAL_NMS_PORTAL.html`.
"""
from __future__ import annotations

import json
from pathlib import Path

from controller.airos_stock_champ_profile import (
    export_r2ac_24ghz_m18_iptv_netjson_template,
    load_empirical_stage40a_and_stage42a_evidence,
    validate_openwrt_netdev_txq_and_airos6_unpolled_guard as validate_guard_airos,
)
from controller.closed_loop_research_reactor import (
    STAGE47C_REACTOR_S40A_S42A_RECEIPT_JSON,
    ingest_stage40a_and_stage42a_and_synthesize_m28_m29,
)
from controller.futuramax_openwrt_imagebuilder_packager import (
    STAGE47C_OUTPUT_JSON,
    generate_stage47c_imagebuilder_txq1000_manifest,
    render_hotplug_99_futuramax_wds_dms,
    render_uci_defaults_98_futuramax_champion_v13_aqm,
)
from controller.openwrt_ptmp_2cpe_aqm_profile import (
    validate_openwrt_netdev_txq_and_airos6_unpolled_guard as validate_guard_openwrt,
)
from tools.nms.serve_openwisp_dual_nms_live import (
    PORTAL_HTML_OUT,
    build_iptv_and_capacity_ceiling_api_payload,
    build_openwisp_portal_html,
    build_stage47c_guards_and_24ghz_m18_api_payload,
)


def test_stage42a_netdev_txq_and_airos6_unpolled_guard_accepts_champion_v13_defaults() -> None:
    res = validate_guard_openwrt(
        tx_queue_len=1000,
        netdev_max_backlog=1000,
        airos6_unpolled_txop_params="0 0",
        airos6_unpolled_no_ack_rate=0,
    )
    assert res["valid"] is True
    assert res["violation_count"] == 0
    assert res["tx_queue_len"] == 1000
    assert res["netdev_max_backlog"] == 1000


def test_stage42a_guard_rejects_low_sysfs_tx_queue_len_64_128_256() -> None:
    for bad_txq in (64, 128):
        res = validate_guard_openwrt(
            tx_queue_len=bad_txq,
            netdev_max_backlog=1000,
            airos6_unpolled_txop_params="0 0",
            airos6_unpolled_no_ack_rate=0,
        )
        assert res["valid"] is False
        assert any("NETDEV_TXQ_STARVATION" in v for v in res["violations"])
    # S42A-R3 coupled tx_queue_len=256 with netdev_max_backlog=2000 -> rejected
    res_s42a_r3 = validate_guard_openwrt(
        tx_queue_len=256,
        netdev_max_backlog=2000,
        airos6_unpolled_txop_params="0 0",
        airos6_unpolled_no_ack_rate=0,
    )
    assert res_s42a_r3["valid"] is False
    assert any("NETDEV_MAX_BACKLOG_BLOAT" in v for v in res_s42a_r3["violations"])


def test_stage42a_guard_rejects_excessive_netdev_max_backlog_2000() -> None:
    res = validate_guard_openwrt(
        tx_queue_len=1000,
        netdev_max_backlog=2000,
        airos6_unpolled_txop_params="0 0",
        airos6_unpolled_no_ack_rate=0,
    )
    assert res["valid"] is False
    assert any("NETDEV_MAX_BACKLOG_BLOAT" in v for v in res["violations"])


def test_stage42a_guard_rejects_unpolled_airos6_xw_txop_or_no_ack() -> None:
    res_txop = validate_guard_airos(
        tx_queue_len=1000,
        netdev_max_backlog=1000,
        airos6_unpolled_txop_params="15 5",
        airos6_unpolled_no_ack_rate=0,
    )
    assert res_txop["valid"] is False
    assert any("AIROS6_UNPOLLED_UBNT_POLL_CONTENTION" in v for v in res_txop["violations"])

    res_noack = validate_guard_airos(
        tx_queue_len=1000,
        netdev_max_backlog=1000,
        airos6_unpolled_txop_params="0 0",
        airos6_unpolled_no_ack_rate=1,
    )
    assert res_noack["valid"] is False
    assert any("AIROS6_UNPOLLED_UBNT_POLL_CONTENTION" in v for v in res_noack["violations"])


def test_export_r2ac_24ghz_m18_iptv_netjson_template_orders_ff_mcast_last() -> None:
    tpl = export_r2ac_24ghz_m18_iptv_netjson_template()
    assert tpl["stage"] == "47C"
    assert len(tpl["profile_sha256"]) == 64
    script = tpl["config"]["files"][1]["contents"]
    assert "echo 2 > \"/sys/devices/virtual/net/${BR_DEV}/bridge/multicast_igmp_version\"" in script
    assert "multicast_fast_leave" in script
    assert "net.ipv4.tcp_wmem='4096 16384 524288'" in script
    voip_idx = script.index("echo 6 > /proc/sys/dev/uph_wifi0/voip_bias")
    mcast_idx = script.index("echo 5 > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit")
    assert mcast_idx > voip_idx
    ev = load_empirical_stage40a_and_stage42a_evidence()
    assert ev["stage40a_r1_r2ac_24ghz_m18"]["p95_rtt_delta_pct"] == -20.75
    assert ev["stage40a_r1_r2ac_24ghz_m18"]["iptv_loss_pct"] == 0.0
    assert ev["stage40a_r1_r2ac_24ghz_m18"]["voip_loss_pct"] == 0.0


def test_imagebuilder_champion_v13_preserves_sysfs_txq_1000_and_writes_stage47c_manifest() -> None:
    uci_v13 = render_uci_defaults_98_futuramax_champion_v13_aqm("ubnt_lap-120")
    hotplug_wds = render_hotplug_99_futuramax_wds_dms()
    assert "echo 1000 > /sys/class/net/br-lan/tx_queue_len" in uci_v13
    assert "/sys/class/net/phy0-ap0*/tx_queue_len" in uci_v13
    assert "txqueuelen" not in uci_v13
    assert "txqueuelen" not in hotplug_wds
    assert '/sys/class/net/$INTERFACE/tx_queue_len' in hotplug_wds or '/sys/class/net/br-lan/tx_queue_len' in hotplug_wds

    manifest = generate_stage47c_imagebuilder_txq1000_manifest()
    assert STAGE47C_OUTPUT_JSON.exists()
    assert manifest["stage"] == "47C"
    assert len(manifest["targets"]) == 4
    assert manifest["netdev_txq_and_airos6_unpolled_guard"]["valid"] is True
    for t in manifest["targets"].values():
        v13_contents = t["overlay_files"]["files/etc/uci-defaults/98-futuramax-champion-v13-aqm"]["contents"]
        assert "echo 1000 > /sys/class/net/br-lan/tx_queue_len" in v13_contents
        assert "/sys/class/net/phy0-ap0*/tx_queue_len" in v13_contents
        assert "txqueuelen" not in v13_contents


def test_closed_loop_reactor_ingests_s40a_s42a_and_synthesizes_m28_m29() -> None:
    receipt = ingest_stage40a_and_stage42a_and_synthesize_m28_m29()
    assert STAGE47C_REACTOR_S40A_S42A_RECEIPT_JSON.exists()
    loaded = json.loads(STAGE47C_REACTOR_S40A_S42A_RECEIPT_JSON.read_text(encoding="utf-8"))
    assert loaded["stage"] == "47C"
    round_ids = [e["round_id"] for e in loaded["ingested_reactor_events"]]
    assert round_ids == ["S40A-R1", "S40A-R2", "S42A-R1", "S42A-R2", "S42A-R3", "S42A-R4"]
    mids = [m["mechanism_id"] for m in receipt["next_wave_mechanisms_m28_to_m29"]]
    assert mids == ["M28", "M29"]


def test_openwisp_portal_exposes_stage47c_guards_endpoint_and_card_a5() -> None:
    s47c_payload = build_stage47c_guards_and_24ghz_m18_api_payload()
    assert s47c_payload["stage"] == "47C"
    assert s47c_payload["netdev_txq_and_airos6_unpolled_guard_default_validation"]["valid"] is True
    assert s47c_payload["r2ac_24ghz_m18_iptv_netjson_template"]["stage"] == "47C"

    cap = build_iptv_and_capacity_ceiling_api_payload()
    assert "openwisp_r2ac_24ghz_m18_iptv_template" in cap
    assert "stage40a_and_stage42a_evidence" in cap
    assert "stage47c_guards_payload" in cap

    out_html = build_openwisp_portal_html()
    assert out_html == PORTAL_HTML_OUT
    html_text = out_html.read_text(encoding="utf-8")
    assert "a5) Stage 47C" in html_text
    assert "FMX airos8_r2ac_24ghz_m18_iptv_voip_champion_v14" in html_text
