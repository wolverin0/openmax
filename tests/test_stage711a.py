from __future__ import annotations

from pathlib import Path

from tools.firmware.build_stage711a_universal_wa_xc_xw_v18_squashfs_bake import build_stage711a

ROOT = Path(__file__).resolve().parents[1]


def test_stage711a_wa_xc_xw_v18_bake() -> None:
    receipt = build_stage711a()
    assert receipt["stage"] == "711A"
    assert receipt["status"] == "CONFIRMED"
    assert all(receipt["checks"].values())
    assert receipt["total_verified_hsqs_images"] == 180
    assert receipt["all_images_have_hsqs_superblock"] is True

    uci_path = ROOT / "firmware/openwrt/common/99-fmx-wa-universal-champion-v18"
    assert uci_path.exists()
    uci_txt = uci_path.read_text(encoding="utf-8")
    assert "fmx_qca_wmi_vdev_start_guard.sh" in uci_txt
    assert "for p in phy0 phy1 phy2; do" in uci_txt
