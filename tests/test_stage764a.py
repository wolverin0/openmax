from __future__ import annotations

from pathlib import Path

from tools.firmware.build_stage764a_ltu_22round_264window_champion_v20 import build_stage764a

ROOT = Path(__file__).resolve().parents[1]


def test_stage764a_ltu_v20_champion() -> None:
    receipt = build_stage764a()
    assert receipt["stage"] == "764A"
    assert receipt["status"] == "CONFIRMED"
    assert receipt["champion_version"] == "v20"
    assert receipt["total_live_campaigns"] == 22
    assert receipt["total_live_ab_rounds"] == 66
    assert receipt["total_live_measurement_windows"] == 264
    assert all(receipt["checks"].values())

    sh_path = ROOT / "firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh"
    sh_txt = sh_path.read_text(encoding="utf-8")
    assert "/dev/ame" not in sh_txt
    assert "fmx_ltu_irq_napi_and_dhcp_guard.sh" in sh_txt
    assert "fmx_ltu_thermal_pa_bias_guard.sh" in sh_txt
