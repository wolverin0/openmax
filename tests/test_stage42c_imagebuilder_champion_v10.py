"""
Tests for Stage 42C (`T-S42C-GEM2-IMAGEBUILDER-CHAMPION-V10-AND-IPTV-FIRSTBOOT-INTEGRATION`):
Verifies that `firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py` embeds:
  1. `files/etc/hotplug.d/net/99-futuramax-wds-dms` (dynamic `phy0-ap0.sta*` `multicast_to_unicast=1` + `multicast_fast_leave=1`),
  2. `files/etc/uci-defaults/98-futuramax-champion-v10-aqm` (`fq_quantum 3028` on AP / `1514` on CPE, `fq_memory_limit 4194304`, `AC_VI 1200/2400`, `AC_BE 1500/3000`, `aql_threshold 5000`),
  3. Dual-NMS coexistence (`files/usr/sbin/fmx_uisp_ws_reporter` + `files/usr/sbin/fmx_netjson_watchdog`),
  4. Generates `artifacts/autoresearch/stage42c_imagebuilder_champion_v10_manifest_20261025.json`.
"""

from __future__ import annotations

from pathlib import Path

from controller.multiradio_golden_profile_applicator import FORBIDDEN_TOKENS
from firmware.openwrt.futuramax_openwrt_imagebuilder_packager import (
    STAGE42C_OUTPUT_JSON,
    TARGET_DEVICE_SPECS,
    build_imagebuilder_overlay_for_target,
    generate_stage42c_imagebuilder_champion_v10_manifest,
    render_hotplug_99_futuramax_wds_dms,
    render_uci_defaults_98_futuramax_champion_v10_aqm,
)


def test_stage42c_wds_dms_hotplug_and_champion_v10_uci_defaults() -> None:
    for target_id in TARGET_DEVICE_SPECS:
        wds_script = render_hotplug_99_futuramax_wds_dms(target_id)
        assert "phy0-ap0*" in wds_script
        assert "multicast_to_unicast" in wds_script
        assert "multicast_fast_leave" in wds_script
        assert "multicast_snooping" in wds_script
        assert "multicast_querier" in wds_script

        v10_script = render_uci_defaults_98_futuramax_champion_v10_aqm(target_id)
        assert "/sys/kernel/debug/ieee80211/phy0/aqm" in v10_script or '$PHY_DIR/aqm' in v10_script
        assert "fq_memory_limit 4194304" in v10_script
        assert 'echo "0 600 1200"' in v10_script
        assert 'echo "1 1200 2400"' in v10_script
        assert 'echo "2 1500 3000"' in v10_script
        assert 'echo "3 500 1000"' in v10_script
        assert "echo 5000 >" in v10_script

        if target_id in ("ubnt_lap-120", "ubnt_rocket-prism-5ac-gen2"):
            assert "fq_quantum 3028" in v10_script
        else:
            assert "fq_quantum 1514" in v10_script

        for script in (wds_script, v10_script):
            for tok in FORBIDDEN_TOKENS:
                assert tok not in script.lower()


def test_stage42c_manifest_and_overlay_bundle(tmp_path: Path) -> None:
    out_file = tmp_path / "stage42c_manifest.json"
    manifest = generate_stage42c_imagebuilder_champion_v10_manifest(output_path=out_file)
    assert out_file.exists()
    assert STAGE42C_OUTPUT_JSON.exists()
    assert manifest["stage"] == "42C"
    assert manifest["targets_count"] == 4
    assert manifest["empirical_hardware_anchors"]["stage36a_champion_v10_aqm"]["s36a_r2_confirmed"]["goodput_delta_pct"] == 2.513
    assert manifest["empirical_hardware_anchors"]["stage36a_champion_v10_aqm"]["s36a_r2_confirmed"]["iptv_ac_vi_tid4_loss_pct"] == 0.0

    for target_id in TARGET_DEVICE_SPECS:
        bundle = build_imagebuilder_overlay_for_target(target_id)
        files = bundle["overlay_files"]
        assert "files/etc/hotplug.d/net/99-futuramax-wds-dms" in files
        assert "files/etc/uci-defaults/98-futuramax-champion-v10-aqm" in files
        assert "files/usr/sbin/fmx_uisp_ws_reporter" in files
        assert "files/usr/sbin/fmx_netjson_watchdog" in files
        assert "files/etc/init.d/fmx_uisp_reporter" in files
