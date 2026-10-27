from __future__ import annotations

from pathlib import Path

from tools.firmware.build_stage732a_ltu_21round_252window_champion_v19 import build_stage732a

ROOT = Path(__file__).resolve().parents[1]


def test_stage732a_ltu_v19_champion() -> None:
    receipt = build_stage732a()
    assert receipt["stage"] == "732A"
    assert receipt["status"] == "CONFIRMED"
    assert receipt["champion_version"] == "v19"
    assert receipt["total_live_campaigns"] == 21
    assert receipt["total_live_ab_rounds"] == 63
    assert receipt["total_live_measurement_windows"] == 252
    assert all(receipt["checks"].values())

    sh_path = ROOT / "firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh"
    sh_txt = sh_path.read_text(encoding="utf-8")
    assert "/dev/ame" not in sh_txt
    assert "fmx_ltu_thermal_pa_bias_guard.sh" in sh_txt
    assert "fmx_ltu_dma_ring_backpressure_guard.sh" in sh_txt
