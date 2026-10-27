"""
Tests for Stage 45C (`T-S45C-GEM2-CHAMPION-V12-WDS-FAST-LEAVE-AND-UPH-BUFFER-CLOBBER-GUARD`):
Verifies:
  1. `load_empirical_stage39a_champion_v12_evidence()`, `render_openwrt_wds_fast_leave_champion_v12_script()`,
     and `export_openwisp_wds_fast_leave_champion_v12_netjson_template()` in `controller/wisp_iptv_ptmp_sector_optimizer.py`.
  2. `ubnt_poll_host.ko` shared `sysctl_table->data` buffer clobber guard: `ff_mcast_airtime_limit=5` is written LAST
     and `voip_bias` is never written after `ff_mcast_airtime_limit`.
  3. `render_hotplug_99_futuramax_wds_dms()` and `render_uci_defaults_98_futuramax_champion_v12_aqm()` enforce
     Single-Querier IGMPv2 (`multicast_igmp_version=2`, AP `multicast_querier=1`, CPE `multicast_querier=0`)
     and `multicast_fast_leave=1`.
  4. `ingest_stage39a_champion_v12_and_synthesize_m24_m25()` ingests `S39A-R1` (`REFUTED`), `S39A-R2` (`REFUTED`),
     and `S39A-R3` (`CONFIRMED` Champion v12) and synthesizes `M24` and `M25`.
"""

from __future__ import annotations

from pathlib import Path

from controller.multiradio_golden_profile_applicator import FORBIDDEN_TOKENS
from controller.wisp_iptv_ptmp_sector_optimizer import (
    export_openwisp_wds_fast_leave_champion_v12_netjson_template,
    load_empirical_stage39a_champion_v12_evidence,
    render_openwrt_wds_fast_leave_champion_v12_script,
)
from firmware.openwrt.futuramax_openwrt_imagebuilder_packager import (
    STAGE45C_OUTPUT_JSON,
    TARGET_DEVICE_SPECS,
    build_imagebuilder_overlay_for_target,
    generate_stage45c_imagebuilder_champion_v12_manifest,
    render_hotplug_99_futuramax_wds_dms,
    render_uci_defaults_98_futuramax_champion_v12_aqm,
)
from tools.research.closed_loop_research_reactor import (
    STAGE45C_REACTOR_V12_RECEIPT_JSON,
    VAULT_ROOT,
    ingest_stage39a_champion_v12_and_synthesize_m24_m25,
)
from tools.serve_openwisp_dual_nms_live import (
    PORTAL_HTML_OUT,
    build_iptv_and_capacity_ceiling_api_payload,
    build_openwisp_portal_html,
)


def test_stage45c_champion_v12_evidence_and_netjson_template() -> None:
    ev = load_empirical_stage39a_champion_v12_evidence()
    assert ev["s39a_r1_igmpv3_and_uph_clobber_refuted"]["claim_status"] == "REFUTED"
    assert ev["s39a_r1_igmpv3_and_uph_clobber_refuted"]["clobbered_ff_mcast_airtime_limit_readback"] == 1
    assert ev["s39a_r2_midwindow_mdb_qdisc_flush_refuted"]["claim_status"] == "REFUTED"

    r3 = ev["s39a_r3_champion_v12_promoted"]
    assert r3["claim_status"] == "CONFIRMED"
    assert r3["decision"] == "PROMOTE_NEW_CHAMPION"
    assert r3["goodput_delta_pct"] == 5.863
    assert r3["p95_rtt_delta_pct"] == -5.361
    assert r3["p50_rtt_delta_pct"] == -8.747
    assert r3["iptv_loss_pct"] == 0.0
    assert r3["voip_loss_pct"] == 0.0
    assert r3["multicast_igmp_version"] == 2
    assert r3["uph_ff_mcast_airtime_limit_written_last"] == 5

    script = render_openwrt_wds_fast_leave_champion_v12_script()
    assert "multicast_igmp_version" in script
    assert "multicast_fast_leave" in script
    assert "ff_mcast_airtime_limit" in script
    assert "voip_bias" not in script.split("ff_mcast_airtime_limit")[-1]
    for tok in FORBIDDEN_TOKENS:
        assert tok not in script.lower()

    tpl = export_openwisp_wds_fast_leave_champion_v12_netjson_template()
    assert tpl["name"] == "FMX openwrt_wds_fast_leave_igmpv2_uph_guard_champion_v12"
    assert len(tpl["profile_sha256"]) == 64
    apply_cmds = tpl["config"]["files"][0]["contents"]
    assert "ff_mcast_airtime_limit" in apply_cmds


def test_stage45c_imagebuilder_champion_v12_single_querier_and_manifest(tmp_path: Path) -> None:
    for target_id in TARGET_DEVICE_SPECS:
        wds_script = render_hotplug_99_futuramax_wds_dms(target_id)
        v12_script = render_uci_defaults_98_futuramax_champion_v12_aqm(target_id)
        assert "multicast_igmp_version" in wds_script
        assert "multicast_igmp_version" in v12_script
        assert "ff_mcast_airtime_limit" in v12_script

        if target_id in ("ubnt_lap-120", "ubnt_rocket-prism-5ac-gen2"):
            assert "echo 1 > /sys/class/net/br-lan/bridge/multicast_querier" in wds_script
            assert 'echo 1 > "$BR_DIR/bridge/multicast_querier"' in v12_script
            assert "fq_quantum 4542" in v12_script
        else:
            assert "echo 0 > /sys/class/net/br-lan/bridge/multicast_querier" in wds_script
            assert 'echo 0 > "$BR_DIR/bridge/multicast_querier"' in v12_script
            assert "fq_quantum 1514" in v12_script

        bundle = build_imagebuilder_overlay_for_target(target_id)
        assert "files/etc/uci-defaults/98-futuramax-champion-v12-aqm" in bundle["overlay_files"]

    out_manifest = tmp_path / "stage45c_manifest.json"
    manifest = generate_stage45c_imagebuilder_champion_v12_manifest(output_path=out_manifest)
    assert out_manifest.exists()
    assert manifest["stage"] == "45C"
    assert manifest["targets_count"] == 4


def test_stage45c_reactor_v12_and_portal_integration(tmp_path: Path) -> None:
    out_receipt = tmp_path / "stage45c_reactor.json"
    res = ingest_stage39a_champion_v12_and_synthesize_m24_m25(output_path=out_receipt)
    assert out_receipt.exists()
    assert res["stage"] == "45C"
    events = {e["round_id"]: e for e in res["ingested_reactor_events"]}
    assert events["S39A-R1"]["empirical_status"] == "HW_REFUTED_OR_BOUNDED"
    assert events["S39A-R2"]["empirical_status"] == "HW_REFUTED_OR_BOUNDED"
    assert events["S39A-R3"]["empirical_status"] == "HW_CONFIRMED"
    assert events["S39A-R3"]["gp_delta_pct"] == 5.863

    mids = [m["mechanism_id"] for m in res["next_wave_mechanisms_m24_to_m25"]]
    assert mids == ["M24", "M25"]

    fb_dir = VAULT_ROOT / "notes" / "empirical_feedback"
    assert (fb_dir / "empirical_feedback_S39A-R1.md").exists()
    assert (fb_dir / "empirical_feedback_S39A-R2.md").exists()
    assert (fb_dir / "empirical_feedback_S39A-R3.md").exists()

    api_payload = build_iptv_and_capacity_ceiling_api_payload()
    assert "openwisp_wds_fast_leave_champion_v12_template" in api_payload
    assert "stage39a_champion_v12_evidence" in api_payload

    html_out = build_openwisp_portal_html(out_path=tmp_path / "portal.html")
    html_text = html_out.read_text(encoding="utf-8")
    assert "WISP IPTV &amp; 6-Family Capacity Ceiling" in html_text
    assert "FMX openwrt_wds_fast_leave_igmpv2_uph_guard_champion_v12" in html_text
    assert STAGE45C_OUTPUT_JSON.parent.exists()
    assert STAGE45C_REACTOR_V12_RECEIPT_JSON.parent.exists()
    assert PORTAL_HTML_OUT.parent.exists()
