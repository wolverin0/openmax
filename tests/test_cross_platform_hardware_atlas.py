"""Unit tests for Cross-Platform Firmware & Hardware Capability Atlas."""

from __future__ import annotations

from pathlib import Path

from analysis.cross_platform_hardware_atlas import (
    DEFAULT_ATLAS_OUTPUT_PATH,
    generate_cross_platform_hardware_atlas,
)


def test_cross_platform_hardware_atlas_completeness_and_determinism(tmp_path: Path) -> None:
    out_file = tmp_path / "atlas.json"
    a1 = generate_cross_platform_hardware_atlas(output_path=out_file)
    a2 = generate_cross_platform_hardware_atlas(output_path=out_file)

    assert a1["atlas_sha256"] == a2["atlas_sha256"]
    summary = a1["summary"]
    assert summary["platforms_cataloged"] == 6
    assert summary["interop_pairs_verified"] == 5
    assert summary["host_per_frame_rate_control_platforms"] == ["UBNT_AIRMAX_M5_XW_XM"]
    assert "UBNT_AIRMAX_AC_WA" in summary["firmware_offloaded_rate_control_platforms"]
    assert DEFAULT_ATLAS_OUTPUT_PATH.exists()


def test_platform_channel_widths_and_modulation_ceilings(tmp_path: Path) -> None:
    atlas = generate_cross_platform_hardware_atlas(output_path=tmp_path / "atlas.json")
    by_id = {p["platform_id"]: p for p in atlas["platforms"]}

    assert by_id["UBNT_AIRMAX_AC_WA"]["supported_channel_widths_mhz"] == [5, 10, 20, 30, 40, 80]
    assert "4096-QAM" in by_id["UBNT_LTU_AMESOC3"]["max_modulation"]
    assert by_id["UBNT_AIRMAX_M5_XW_XM"]["per_frame_host_rate_control"] is True
    assert by_id["UBNT_AIRMAX_AC_XC"]["per_frame_host_rate_control"] is False
