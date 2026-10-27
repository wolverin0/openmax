"""
Stage 48C Verification Suite (`tests/test_stage48c_champion_v14_integration.py`)
================================================================================
Validates `T-S48C-GEM2-STAGE42A-CHAMPION-V14-SYSFS-TXQ256-PACKAGER-AND-REACTOR`:
1. `validate_openwrt_netdev_txq_and_airos6_unpolled_guard` in both
   `controller.openwrt_ptmp_2cpe_aqm_profile` and `controller.airos_stock_champ_profile`
   accepting Stage 42A Champion v14 (`S42A-R5`: `tx_queue_len=256`, `netdev_max_backlog=1000`,
   `tcp_early_retrans=3`, `airos6_unpolled_txop_params='0 0'`, `airos6_unpolled_no_ack_rate=0`)
   while rejecting `tx_queue_len < 256` (`64`, `128`), `netdev_max_backlog > 1500` (`2000`),
   or `tcp_early_retrans != 3` when `tx_queue_len == 256`.
2. `export_openwisp_sysfs_txq256_champion_v14_netjson_template` and
   `load_empirical_stage42a_champion_v14_evidence` in both profile modules encoding `S42A-R5`
   (`M24e_M25e_PURE_SYSFS_WDS_TXQ_256_AND_LBM5_BR0_TXQ_256`: `+3.208%` goodput `45.331 -> 46.785 Mbps`,
   `-7.917%` p95 RTT `104.429 -> 96.161 ms`, `-12.355%` Dual IPTV jitter `1.902 -> 1.667 ms`,
   `-8.110%` VoIP jitter `2.429 -> 2.232 ms`, `0.00%` IPTV/VoIP loss, `0` `tid0_ac2` drops,
   Pareto `+5.9786%`).
3. `controller.futuramax_openwrt_imagebuilder_packager` & `firmware.openwrt.futuramax_openwrt_imagebuilder_packager`
   with `render_uci_defaults_98_futuramax_champion_v14_aqm()` and `render_hotplug_99_futuramax_wds_dms()`
   setting direct sysfs `/sys/class/net/br-lan/tx_queue_len=256` and `/sys/class/net/phy0-ap0*/tx_queue_len=256`
   and writing `artifacts/autoresearch/stage48c_imagebuilder_champion_v14_manifest_20261025.json`.
4. `controller.closed_loop_research_reactor` (`ingest_stage42a_r5_champion_v14_and_synthesize_m30_m31`)
   ingesting `S42A-R1..R5` and synthesizing `M30` and `M31` into
   `artifacts/autoresearch/stage48c_closed_loop_reactor_champion_v14_20261025.json`.
5. `/api/v1/controller/template/champion-v14-aqm/` and Card `a6)` in
   `tools.nms.serve_openwisp_dual_nms_live` and `OPENWISP_DUAL_NMS_PORTAL.html`.
"""
from __future__ import annotations

import json

from controller.airos_stock_champ_profile import (
    export_openwisp_sysfs_txq256_champion_v14_netjson_template as export_v14_airos,
    load_empirical_stage42a_champion_v14_evidence as load_v14_airos,
    validate_openwrt_netdev_txq_and_airos6_unpolled_guard as validate_guard_airos,
)
from controller.closed_loop_research_reactor import (
    STAGE48C_REACTOR_V14_RECEIPT_JSON,
    ingest_stage42a_r5_champion_v14_and_synthesize_m30_m31,
)
from controller.futuramax_openwrt_imagebuilder_packager import (
    STAGE48C_OUTPUT_JSON,
    generate_stage48c_imagebuilder_champion_v14_manifest,
    render_hotplug_99_futuramax_wds_dms,
    render_uci_defaults_98_futuramax_champion_v14_aqm,
)
from controller.openwrt_ptmp_2cpe_aqm_profile import (
    export_openwisp_sysfs_txq256_champion_v14_netjson_template as export_v14_openwrt,
    load_empirical_stage42a_champion_v14_evidence as load_v14_openwrt,
    render_openwrt_sysfs_txq256_champion_v14_script,
    validate_openwrt_netdev_txq_and_airos6_unpolled_guard as validate_guard_openwrt,
)
from tools.nms.serve_openwisp_dual_nms_live import (
    PORTAL_HTML_OUT,
    build_iptv_and_capacity_ceiling_api_payload,
    build_openwisp_portal_html,
    export_openwisp_sysfs_txq256_champion_v14_netjson_template as export_v14_nms,
)


def test_stage42a_guard_accepts_champion_v14_sysfs_txq_256_with_backlog_1000() -> None:
    res = validate_guard_openwrt(
        tx_queue_len=256,
        netdev_max_backlog=1000,
        airos6_unpolled_txop_params="0 0",
        airos6_unpolled_no_ack_rate=0,
        tcp_early_retrans=3,
    )
    assert res["valid"] is True
    assert res["violation_count"] == 0
    assert res["tx_queue_len"] == 256
    assert res["netdev_max_backlog"] == 1000
    assert res["tcp_early_retrans"] == 3


def test_stage42a_guard_rejects_txq_below_256_or_backlog_above_1500_or_bad_early_retrans() -> None:
    for bad_txq in (64, 128, 255):
        res_low = validate_guard_openwrt(
            tx_queue_len=bad_txq,
            netdev_max_backlog=1000,
            airos6_unpolled_txop_params="0 0",
            airos6_unpolled_no_ack_rate=0,
            tcp_early_retrans=3,
        )
        assert res_low["valid"] is False
        assert any("NETDEV_TXQ_STARVATION" in v for v in res_low["violations"])

    res_backlog = validate_guard_airos(
        tx_queue_len=256,
        netdev_max_backlog=2000,
        airos6_unpolled_txop_params="0 0",
        airos6_unpolled_no_ack_rate=0,
        tcp_early_retrans=3,
    )
    assert res_backlog["valid"] is False
    assert any("NETDEV_MAX_BACKLOG_BLOAT" in v for v in res_backlog["violations"])

    res_er = validate_guard_openwrt(
        tx_queue_len=256,
        netdev_max_backlog=1000,
        airos6_unpolled_txop_params="0 0",
        airos6_unpolled_no_ack_rate=0,
        tcp_early_retrans=0,
    )
    assert res_er["valid"] is False
    assert any("TCP_EARLY_RETRANS_MISMATCH" in v for v in res_er["violations"])


def test_champion_v14_evidence_and_netjson_template_match_s42a_r5() -> None:
    ev = load_v14_openwrt()
    assert ev == load_v14_airos()
    r5 = ev["s42a_r5_champion_v14_promoted"]
    assert r5["round_id"] == "S42A-R5"
    assert r5["mechanism_id"] == "M24e_M25e_PURE_SYSFS_WDS_TXQ_256_AND_LBM5_BR0_TXQ_256"
    assert r5["goodput_delta_pct"] == 3.208
    assert r5["p95_rtt_delta_pct"] == -7.917
    assert r5["iptv_jitter_delta_pct"] == -12.355
    assert r5["voip_jitter_delta_pct"] == -8.110
    assert r5["iptv_loss_pct"] == 0.0
    assert r5["voip_loss_pct"] == 0.0
    assert r5["tid0_ac2_drops"] == 0
    assert r5["pareto_score_delta_pct"] == 5.9786

    tpl = export_v14_openwrt()
    assert tpl == export_v14_airos()
    assert tpl == export_v14_nms()
    assert tpl["stage"] == "48C"
    assert "v14" in tpl["champion_version"]
    assert len(tpl["profile_sha256"]) == 64

    script = render_openwrt_sysfs_txq256_champion_v14_script()
    assert "/sys/class/net/br-lan/tx_queue_len" in script
    assert "echo 256 > \"$q\"" in script
    assert "net.core.netdev_max_backlog=1000" in script
    assert "net.ipv4.tcp_early_retrans=3" in script
    assert "echo 5 > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit" in script
    assert "ubnt_ewma_delegate_on" in script


def test_imagebuilder_champion_v14_sets_sysfs_txq_256_and_writes_stage48c_manifest() -> None:
    uci_v14 = render_uci_defaults_98_futuramax_champion_v14_aqm("ubnt_lap-120")
    hotplug_wds = render_hotplug_99_futuramax_wds_dms()
    assert "echo 256 > /sys/class/net/br-lan/tx_queue_len" in uci_v14
    assert "/sys/class/net/phy0-ap0*/tx_queue_len" in uci_v14
    assert "net.core.netdev_max_backlog=1000" in uci_v14
    assert "net.ipv4.tcp_early_retrans=3" in uci_v14
    assert "/sys/class/net/phy0-ap0*/tx_queue_len" in hotplug_wds
    assert "echo 256 > /sys/class/net/br-lan/tx_queue_len" in hotplug_wds
    assert "txqueuelen" not in uci_v14
    assert "txqueuelen" not in hotplug_wds

    manifest = generate_stage48c_imagebuilder_champion_v14_manifest()
    assert STAGE48C_OUTPUT_JSON.exists()
    assert manifest["stage"] == "48C"
    assert "v14" in manifest["champion_version"]
    assert len(manifest["targets"]) == 4
    assert manifest["netdev_txq_and_airos6_unpolled_guard"]["valid"] is True
    assert manifest["netdev_txq_and_airos6_unpolled_guard"]["tx_queue_len"] == 256
    for t in manifest["targets"].values():
        v14_contents = t["overlay_files"]["files/etc/uci-defaults/98-futuramax-champion-v14-aqm"]["contents"]
        assert "echo 256 > /sys/class/net/br-lan/tx_queue_len" in v14_contents


def test_closed_loop_reactor_ingests_s42a_r5_champion_v14_and_synthesizes_m30_m31() -> None:
    receipt = ingest_stage42a_r5_champion_v14_and_synthesize_m30_m31()
    assert STAGE48C_REACTOR_V14_RECEIPT_JSON.exists()
    loaded = json.loads(STAGE48C_REACTOR_V14_RECEIPT_JSON.read_text(encoding="utf-8"))
    assert loaded["stage"] == "48C"
    assert loaded["champion_version"] == "v14"
    assert loaded["champion_round_id"] == "S42A-R5"
    round_ids = [e["round_id"] for e in loaded["ingested_reactor_events"]]
    assert round_ids == ["S42A-R1", "S42A-R2", "S42A-R3", "S42A-R4", "S42A-R5"]
    mids = [m["mechanism_id"] for m in receipt["next_wave_mechanisms_m30_to_m31"]]
    assert mids == ["M30", "M31"]


def test_openwisp_portal_exposes_champion_v14_aqm_template_and_card_a6() -> None:
    cap = build_iptv_and_capacity_ceiling_api_payload()
    assert "openwisp_sysfs_txq256_champion_v14_template" in cap
    assert "stage42a_champion_v14_evidence" in cap
    assert "v14" in cap["openwisp_sysfs_txq256_champion_v14_template"]["champion_version"]

    out_html = build_openwisp_portal_html()
    assert out_html == PORTAL_HTML_OUT
    html_text = out_html.read_text(encoding="utf-8")
    assert "a6) Stage 48C" in html_text
    assert "FMX openwrt_sysfs_txq256_champion_v14" in html_text
