"""Stage 499A — regression tests.

Pins the four discriminator families, the per-chip chirp test, the `blakc` misspelling, the
tunable false-radar surface, and the two hard negatives: no 600 s constant and no bin detectors on
either M5 image.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "build_stage499a_qca988x_dfs_radar_pulse_detector_and_cac_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage499a_qca988x_dfs_radar_pulse_detector_and_cac_re.json")

FAMILIES = ["bin", "bin5", "chirp", "pri_blacklist"]
KNOBS = {"DFS_SET_CAC_TIME_OVERRIDE_MS", "DFS_SET_IGNORE_CAC",
         "DFS_SET_FALSE_RSSI_THRESHOLD", "DFS_SET_FILTER_RSSI_OFFSET",
         "DFS_SET_PRI_MULTIPLIER", "DFS_SET_MUTE_TIME"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


@pytest.fixture(scope="module")
def by(ok: list[dict]) -> dict[str, dict]:
    return {r["image"]: r for r in ok}


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "499A"
    for k in ("meta", "firmware_images", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_firmware_absent(report: dict) -> None:
    assert report["firmware_images"] == {"firmware-2.bin": 0, "firmware-5.bin": 0}
    assert report["summary"]["firmware_images_present"] == 0


def test_five_variants(ok: list[dict], report: dict) -> None:
    assert len(ok) == 5
    assert report["summary"]["modules_ok"] == 5
    sizes = {r["image"]: r["bytes"] for r in ok}
    assert sizes["WA.v8.7.25"] == 203796
    assert sizes["XC.v8.7.4cs"] == 199932
    assert sizes["XW.v6.1.4"] == 191100
    assert sizes["XW.v6.3.6"] == 176248


def test_four_discriminator_families(report: dict) -> None:
    s = report["summary"]
    assert s["discriminator_family_count"] == 4
    assert s["discriminator_families"] == FAMILIES
    assert s["bin5_symbol_count"] == 9
    for name in ("dfs_bin5_check", "dfs_bin5_check_pulse", "dfs_bin5_addpulse"):
        assert name in s["bin5_symbols"]


def test_chirp_is_per_chip(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["chirp_is_per_chip"] == 1
    names = " ".join(s["chirp_names"])
    assert "dfs_check_chirping_merlin" in names
    # the collector is lowercase-only, so the upper-case symbol appears as its suffix
    assert "chirp_protect" in names


def test_vendor_typo_blakc(report: dict) -> None:
    s = report["summary"]
    assert s["pri_blacklist_typo"] == 1
    joined = " ".join(s["pri_blacklist_symbols"])
    assert "DFS_check_PRI_blakc_list" in joined
    assert "PRI_black_list_delta" in joined


def test_false_radar_surface_is_tunable(report: dict) -> None:
    s = report["summary"]
    assert s["knob_count"] == 6
    assert set(s["knobs_present"]) == KNOBS
    assert s["false_rssi_threshold_modules"] == 3
    assert s["ignore_cac_modules"] == 3
    assert s["cac_override_ms_modules"] == 5


def test_cac_is_milliseconds_not_constants(report: dict) -> None:
    s = report["summary"]
    assert s["cac_600_literals"] == 0
    assert s["cac_constant_recovered"] == 0
    joined = " ".join(report["gaps"])
    assert "not evidence of anything" in joined


def test_bin_detectors_are_ac_only(by: dict[str, dict]) -> None:
    for ac in ("WA.v8.7.25", "XC.v8.7.25", "XC.v8.7.4cs"):
        assert by[ac]["family_hits"]["bin5"] == 9
        assert by[ac]["family_hits"]["bin"] == 5
    for xw in ("XW.v6.1.4", "XW.v6.3.6"):
        assert by[xw]["family_hits"]["bin5"] == 0
        assert by[xw]["family_hits"]["bin"] == 0
    # 6.1.4 carries no discriminator family at all
    assert sum(by["XW.v6.1.4"]["family_hits"].values()) == 0


def test_tables_not_recovered(report: dict) -> None:
    s = report["summary"]
    assert s["pulse_width_table_recovered"] == 0
    assert s["chirp_table_recovered"] == 0


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no firmware loaded" in scope
    assert "nothing transmitted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
