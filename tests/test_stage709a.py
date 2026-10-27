from __future__ import annotations

from pathlib import Path

from tools.firmware.build_stage709a_qca_wmi_vdev_start_and_phymode_guard import build_stage709a

ROOT = Path(__file__).resolve().parents[1]


def test_stage709a_qca_wmi_vdev_start_and_phymode_guard() -> None:
    receipt = build_stage709a()
    assert receipt["stage"] == "709A"
    assert receipt["status"] == "CONFIRMED"
    assert all(receipt["checks"].values())

    sh_path = ROOT / "firmware/openwrt/common/fmx_qca_wmi_vdev_start_guard.sh"
    assert sh_path.exists()
    sh_txt = sh_path.read_text(encoding="utf-8")
    assert "WMI_SERVICE_READY_EVENTID" in sh_txt
    assert "WMI_VDEV_START_REQUEST_CMDID" in sh_txt
    assert "for p in phy0 phy1 phy2; do" in sh_txt
