from __future__ import annotations

from pathlib import Path

from tools.firmware.build_stage710a_ltu_20round_240window_champion_v18 import build_stage710a

ROOT = Path(__file__).resolve().parents[1]


def test_stage710a_ltu_v18_champion() -> None:
    receipt = build_stage710a()
    assert receipt["stage"] == "710A"
    assert receipt["status"] == "CONFIRMED"
    assert receipt["champion_version"] == "v18"
    assert receipt["total_live_campaigns"] == 20
    assert receipt["total_live_ab_rounds"] == 60
    assert receipt["total_live_measurement_windows"] == 240
    assert all(receipt["checks"].values())

    sh_path = ROOT / "firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh"
    sh_txt = sh_path.read_text(encoding="utf-8")
    assert "/dev/ame" not in sh_txt
    assert "fmx_ltu_dma_ring_backpressure_guard.sh" in sh_txt
    assert "fmx_ltu_gps_1pps_sync_guard.sh" in sh_txt
