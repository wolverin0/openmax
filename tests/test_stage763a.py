from __future__ import annotations

from pathlib import Path

from tools.firmware.build_stage763a_openwrt_lan_rogue_dhcp_and_ani_guard import build_stage763a

ROOT = Path(__file__).resolve().parents[1]


def test_stage763a_openwrt_lan_rogue_dhcp_and_ani_guard() -> None:
    receipt = build_stage763a()
    assert receipt["stage"] == "763A"
    assert receipt["status"] == "CONFIRMED"
    assert all(receipt["checks"].values())

    sh_path = ROOT / "firmware/openwrt/common/fmx_openwrt_lan_rogue_dhcp_and_ani_guard.sh"
    alias_path = ROOT / "firmware/openwrt/common/fmx_openwrt_lan_rogue_dhcp_guard.sh"
    assert sh_path.exists()
    assert alias_path.exists()
    sh_txt = sh_path.read_text(encoding="utf-8")
    assert "uci set dhcp.lan.ignore='1'" in sh_txt
    assert "uci set dhcp.lan.dhcpv4='disabled'" in sh_txt
    assert "uci set dhcp.lan.dhcpv6='disabled'" in sh_txt
    assert "uci set dhcp.lan.ra='disabled'" in sh_txt
    assert "/etc/init.d/dnsmasq stop" in sh_txt
    assert "/etc/init.d/odhcpd stop" in sh_txt
    assert "WMI_PDEV_PARAM_ANI_ENABLE" in sh_txt
