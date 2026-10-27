from __future__ import annotations

from pathlib import Path

from tools.firmware.build_stage762a_ltu_irq_napi_and_dhcp_guard import build_stage762a

ROOT = Path(__file__).resolve().parents[1]


def test_stage762a_ltu_irq_napi_and_dhcp_guard() -> None:
    receipt = build_stage762a()
    assert receipt["stage"] == "762A"
    assert receipt["status"] == "CONFIRMED"
    assert all(receipt["checks"].values())
    assert receipt["guard_script"]["zero_dev_ame_touches"] is True

    sh_path = ROOT / "firmware/ltu_safe_kit/fmx_ltu_irq_napi_and_dhcp_guard.sh"
    assert sh_path.exists()
    sh_txt = sh_path.read_text(encoding="utf-8")
    assert "/dev/ame" not in sh_txt
    assert "netdev_budget" in sh_txt
    assert "udhcpd|dnsmasq|odhcpd" in sh_txt
