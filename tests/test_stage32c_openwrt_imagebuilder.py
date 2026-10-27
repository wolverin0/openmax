import json
from pathlib import Path
import pytest

from firmware.openwrt.futuramax_openwrt_imagebuilder_packager import (
    CONFIRMED_MAC80211_KO_SHA256,
    CONFIRMED_MAC80211_KO_SIZE_BYTES,
    CONFIRMED_MAC80211_PATCH_DELTA_BYTES,
    DEFAULT_OUTPUT_JSON,
    TARGET_DEVICE_SPECS,
    build_imagebuilder_overlay_for_target,
    generate_stage32c_imagebuilder_catalog,
    render_etc_config_openwisp,
    render_hotplug_99_futuramax_champion_v8,
    render_mac80211_eth_p_teb_quilt_patch,
    validate_openwrt_release_toh_safety,
    verify_eth_p_teb_mac80211_patch,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
STAGE32C_DOC = ROOT_DIR / "docs" / "STAGE32C_OPENWRT_IMAGEBUILDER_AND_ZERO_TOUCH_PROVISIONING.md"


def test_stage32c_spi_nor_release_safety_gate():
    for bad_rel in ("23.05.0", "23.05.2", "24.10.0", "24.10.2"):
        res = validate_openwrt_release_toh_safety(bad_rel)
        assert res["spi_nor_lock_safe"] is False
        assert res["status"] == "REJECT_SPI_NOR_READONLY_BUG"
        with pytest.raises(ValueError, match="SR_BP"):
            build_imagebuilder_overlay_for_target("ubnt_lap-120", openwrt_release=bad_rel)

    for good_rel in ("23.05.3", "24.10.3", "24.10.4"):
        res = validate_openwrt_release_toh_safety(good_rel)
        assert res["spi_nor_lock_safe"] is True
        assert res["status"] == "SAFE_FOR_MX25L12805D_OVERLAYFS"


def test_stage32c_eth_p_teb_0x6558_mac80211_patch_verifier():
    patch = render_mac80211_eth_p_teb_quilt_patch()
    ver = verify_eth_p_teb_mac80211_patch(
        candidate_patch_text=patch,
        raw_module_bytes=b"\x00\x11\x65\x58\xff",
    )
    assert ver["verified"] is True
    assert ver["source_patch_valid"] is True
    assert ver["binary_metadata_valid"] is True
    assert ver["confirmed_module_sha256"] == CONFIRMED_MAC80211_KO_SHA256
    assert ver["confirmed_module_size_bytes"] == CONFIRMED_MAC80211_KO_SIZE_BYTES
    assert ver["patch_delta_bytes"] == CONFIRMED_MAC80211_PATCH_DELTA_BYTES
    assert ver["unpatched_module_size_bytes"] == 665237
    assert ver["ethertype_hex"] == "0x6558"


def test_stage32c_hotplug_and_openwisp_overlays_all_4_targets():
    expected_targets = {
        "ubnt_lap-120",
        "ubnt_nanostation-ac-loco",
        "ubnt_litebeam-ac-gen2",
        "ubnt_rocket-prism-5ac-gen2",
    }
    assert set(TARGET_DEVICE_SPECS.keys()) == expected_targets

    for target in expected_targets:
        hotplug = render_hotplug_99_futuramax_champion_v8(target)
        assert "aql_txq_limit" in hotplug
        assert "quantum 3028" in hotplug
        assert "quantum 1514" in hotplug
        assert "tcp_notsent_lowat=16384" in hotplug

        uci = render_etc_config_openwisp(target)
        assert "option test_config '1'" in uci
        assert "option test_script '/usr/sbin/fmx_netjson_watchdog'" in uci
        assert "__VAULT_INJECTED_OPENWISP_SHARED_SECRET__" in uci


def test_stage32c_catalog_generation_and_files(tmp_path):
    out_json = tmp_path / "stage32c.json"
    cat = generate_stage32c_imagebuilder_catalog(openwrt_release="24.10.4", output_path=out_json)
    assert out_json.exists()
    assert cat["stage"] == "32C"
    assert cat["targets_count"] == 4
    assert cat["mac80211_eth_p_teb_0x6558_verifier"]["verified"] is True

    # Also ensure the canonical artifact and markdown doc exist in the repo
    generate_stage32c_imagebuilder_catalog(openwrt_release="24.10.4", output_path=DEFAULT_OUTPUT_JSON)
    assert DEFAULT_OUTPUT_JSON.exists()
    saved = json.loads(DEFAULT_OUTPUT_JSON.read_text(encoding="utf-8"))
    assert set(saved["targets"].keys()) == {
        "ubnt_lap-120",
        "ubnt_nanostation-ac-loco",
        "ubnt_litebeam-ac-gen2",
        "ubnt_rocket-prism-5ac-gen2",
    }
    assert STAGE32C_DOC.exists()
    assert STAGE32C_DOC.stat().st_size > 1000
