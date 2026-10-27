"""Stage 451A — regression tests.

Pins the headline correction (`PDEV` → `VDEV`), the four packer symbols, the eleven noise-floor
symbols, and the `bin_` disambiguation. Both format-recovery counters must stay 0.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "build_stage451a_qca988x_spectral_scan_fft_and_nf_cal_re.py"
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage451a_qca988x_spectral_scan_fft_and_nf_cal_re.json")

PACKER = ["dump_search_fft_report", "get_fft_bin_count",
          "process_search_fft_report", "spectral_dump_fft"]


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


@pytest.fixture(scope="module")
def by(ok: list[dict]) -> dict[str, dict]:
    return {r["module"]: r for r in ok}


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "451A"
    for k in ("meta", "firmware_images", "modules", "summary", "gaps"):
        assert k in report


def test_firmware_images_absent(report: dict) -> None:
    assert report["firmware_images"] == {"firmware-2.bin": 0, "firmware-5.bin": 0}
    assert report["summary"]["firmware_images_present"] == 0


def test_six_modules(ok: list[dict]) -> None:
    assert len(ok) == 6
    names = {r["module"].split(":")[1] for r in ok}
    assert names == {"umac.ko", "ath_dev.ko", "ath_spectral.ko"}


def test_pdev_prefix_is_refuted(report: dict, by: dict[str, dict]) -> None:
    s = report["summary"]
    assert s["pdev_spectral_hits"] == 0
    assert s["vdev_spectral_hits"] > 0
    assert s["pdev_prefix_refuted"] == 1
    assert s["wmi_pdev_command_hits"] == 0
    assert s["wmi_vdev_command_hits"] == 4


def test_vdev_command_names_present(by: dict[str, dict]) -> None:
    for ver in ("WA", "XC"):
        u = by[f"{ver}:umac.ko"]
        assert u["commands"]["WMI_PDEV_SPECTRAL_SCAN_CONFIGURE_CMDID"] == 0
        assert u["commands"]["WMI_PDEV_SPECTRAL_SCAN_ENABLE_CMDID"] == 0
        assert u["commands"]["WMI_VDEV_SPECTRAL_SCAN_CONFIGURE_CMDID"] == 1
        assert u["commands"]["WMI_VDEV_SPECTRAL_SCAN_ENABLE_CMDID"] == 1


def test_fft_packer_symbols(report: dict, by: dict[str, dict]) -> None:
    assert report["summary"]["packer_symbols"] == PACKER
    assert report["summary"]["packer_symbol_count"] == 4
    assert report["summary"]["fft_packer_located"] == 1
    spec = by["WA:ath_spectral.ko"]
    assert spec["bytes"] == 37656
    for name in PACKER:
        assert name in spec["packer_symbols"]


def test_nf_calibration_symbols(report: dict) -> None:
    s = report["summary"]
    assert s["nfcal_symbol_count"] == 11
    assert s["nf_cal_located"] == 1
    assert "adjust_rssi_with_nf_dbm" in s["nfcal_symbols"]
    assert "get_nfc_ctl_rssi" in s["nfcal_symbols"]
    assert "get_nfc_ext_rssi" in s["nfcal_symbols"]
    assert "spectral_get_noise_power" in s["nfcal_symbols"]
    assert "ol_if_spectral_get_chain_noise_floor" in s["nfcal_symbols"]


def test_enable_path(report: dict) -> None:
    s = report["summary"]
    assert s["enable_symbol_count"] == 5
    assert s["scan_enable_located"] == 1
    assert "spectral_scan_enable" in s["enable_symbols"]
    assert "spectral_scan_enable_params" in s["enable_symbols"]


def test_bin_is_firmware_blob(by: dict[str, dict], report: dict) -> None:
    assert report["summary"]["modules_with_bin_as_blob"] == 2
    for ver in ("WA", "XC"):
        u = by[f"{ver}:umac.ko"]
        assert u["bin_is_firmware_blob"] is True
        joined = " ".join(u["bin_contexts"])
        assert "bin_len" in joined or "ol_transfer" in joined


def test_formats_not_recovered(report: dict) -> None:
    s = report["summary"]
    assert s["fft_bin_format_recovered"] == 0
    assert s["nf_cal_table_recovered"] == 0
    joined = " ".join(report["gaps"])
    assert "FFT bin byte layout cannot be read" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no firmware loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
