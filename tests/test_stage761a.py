from __future__ import annotations

import json
from pathlib import Path

from tools.bench.run_stage761a_live_ltu110_round22_264window_autoresearch import run_stage761a

ROOT = Path(__file__).resolve().parents[1]


def test_stage761a_ltu110_round22_264window_receipt() -> None:
    receipt = run_stage761a()
    assert receipt["stage"] == "761A"
    assert receipt["status"] == "CONFIRMED"
    assert receipt["safety_audit"]["zero_dev_ame_touches"] is True
    assert receipt["safety_audit"]["zero_rogue_dhcp_daemons_on_110"] is True
    assert receipt["safety_audit"]["touched_241"] is False
    assert receipt["safety_audit"]["touched_242"] is False
    assert receipt["safety_audit"]["touched_20"] is False
    assert receipt["safety_audit"]["touched_250"] is False
    assert receipt["summary_metrics"]["total_rounds"] == 3
    assert receipt["summary_metrics"]["total_windows"] == 12
    assert receipt["summary_metrics"]["cumulative_ltu110_live_campaigns"] == 22
    assert receipt["summary_metrics"]["cumulative_ltu110_live_windows"] == 264
    assert receipt["summary_metrics"]["max_rogue_dhcp_daemon_count"] == 0
    assert receipt["summary_metrics"]["champion_v20_mean_rtt_ms"] <= receipt["summary_metrics"]["stock_mean_rtt_ms"]

    p = ROOT / "artifacts/autoresearch/stage761a_live_ltu110_round22_264window_autoresearch.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["summary_metrics"]["cumulative_ltu110_live_windows"] == 264
