from __future__ import annotations

from pathlib import Path

from tools.firmware.build_stage765a_universal_wa_xc_xw_v20_squashfs_bake import build_stage765a

ROOT = Path(__file__).resolve().parents[1]


def test_stage765a_wa_xc_xw_v20_bake() -> None:
    receipt = build_stage765a()
    assert receipt["stage"] == "765A"
    assert receipt["status"] == "CONFIRMED"
    assert all(receipt["checks"].values())
    assert receipt["zero_rogue_dhcp_guarantee"] is True
    assert receipt["total_verified_hsqs_images"] == 180
    assert receipt["all_images_have_hsqs_superblock"] is True

    uci_path = ROOT / "firmware/openwrt/common/99-fmx-wa-universal-champion-v20"
    assert uci_path.exists()
    uci_txt = uci_path.read_text(encoding="utf-8")
    assert "uci set dhcp.lan.ignore='1'" in uci_txt
    assert "/etc/init.d/dnsmasq stop" in uci_txt
    assert "/etc/init.d/odhcpd stop" in uci_txt
    assert "fmx_openwrt_lan_rogue_dhcp_and_ani_guard.sh" in uci_txt
