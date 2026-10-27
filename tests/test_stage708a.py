from __future__ import annotations

from pathlib import Path

from tools.firmware.build_stage708a_ltu_dma_ring_backpressure_guard import build_stage708a

ROOT = Path(__file__).resolve().parents[1]


def test_stage708a_ltu_dma_ring_backpressure_guard() -> None:
    receipt = build_stage708a()
    assert receipt["stage"] == "708A"
    assert receipt["status"] == "CONFIRMED"
    assert all(receipt["checks"].values())
    assert receipt["guard_script"]["zero_dev_ame_touches"] is True

    sh_path = ROOT / "firmware/ltu_safe_kit/fmx_ltu_dma_ring_backpressure_guard.sh"
    assert sh_path.exists()
    sh_txt = sh_path.read_text(encoding="utf-8")
    assert "/dev/ame" not in sh_txt
    assert "eab_driver.ko" in sh_txt
    assert "ame_core.ko" in sh_txt
