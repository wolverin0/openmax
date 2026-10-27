from __future__ import annotations

import json
from pathlib import Path

from tools.bench.run_stage707a_live_ltu110_round20_240window_autoresearch import run_stage707a

ROOT = Path(__file__).resolve().parents[1]


def test_stage707a_ltu110_round20_240window_receipt() -> None:
    receipt = run_stage707a()
    assert receipt["stage"] == "707A"
    assert receipt["status"] == "CONFIRMED"
    assert receipt["safety_audit"]["zero_dev_ame_touches"] is True
    assert receipt["safety_audit"]["touched_241"] is False
    assert receipt["safety_audit"]["touched_242"] is False
    assert receipt["safety_audit"]["touched_20"] is False
    assert receipt["safety_audit"]["touched_250"] is False
    assert receipt["summary_metrics"]["total_rounds"] == 3
    assert receipt["summary_metrics"]["total_windows"] == 12
    assert receipt["summary_metrics"]["cumulative_ltu110_live_campaigns"] == 20
    assert receipt["summary_metrics"]["cumulative_ltu110_live_windows"] == 240
    assert receipt["summary_metrics"]["champion_v18_mean_rtt_ms"] <= receipt["summary_metrics"]["stock_mean_rtt_ms"]

    p = ROOT / "artifacts/autoresearch/stage707a_live_ltu110_round20_240window_autoresearch.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["summary_metrics"]["cumulative_ltu110_live_windows"] == 240
