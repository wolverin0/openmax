from __future__ import annotations

from pathlib import Path

from tools.firmware.build_stage731a_qca_spectral_radar_phyerr_guard import build_stage731a

ROOT = Path(__file__).resolve().parents[1]


def test_stage731a_qca_spectral_radar_phyerr_guard() -> None:
    receipt = build_stage731a()
    assert receipt["stage"] == "731A"
    assert receipt["status"] == "CONFIRMED"
    assert all(receipt["checks"].values())

    sh_path = ROOT / "firmware/openwrt/common/fmx_qca_spectral_radar_phyerr_guard.sh"
    assert sh_path.exists()
    sh_txt = sh_path.read_text(encoding="utf-8")
    assert "ATH10K_PHYERR_SPECTRAL" in sh_txt
    assert "ATH10K_PHYERR_RADAR" in sh_txt
    assert "WMI_VDEV_SPECTRAL_SCAN_CONFIGURE_CMDID" in sh_txt
