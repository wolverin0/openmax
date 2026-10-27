from __future__ import annotations

from pathlib import Path

from tools.firmware.build_stage730a_ltu_thermal_pa_bias_and_gain_guard import build_stage730a

ROOT = Path(__file__).resolve().parents[1]


def test_stage730a_ltu_thermal_pa_bias_and_gain_guard() -> None:
    receipt = build_stage730a()
    assert receipt["stage"] == "730A"
    assert receipt["status"] == "CONFIRMED"
    assert all(receipt["checks"].values())
    assert receipt["guard_script"]["zero_dev_ame_touches"] is True

    sh_path = ROOT / "firmware/ltu_safe_kit/fmx_ltu_thermal_pa_bias_guard.sh"
    assert sh_path.exists()
    sh_txt = sh_path.read_text(encoding="utf-8")
    assert "/dev/ame" not in sh_txt
    assert "thermal_zone0/temp" in sh_txt
    assert "OPTIMAL_4096QAM_EVM" in sh_txt
