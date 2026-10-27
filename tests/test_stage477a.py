from __future__ import annotations

import json
from pathlib import Path

from tools.sim.run_stage477a_pb050_rc_probe_dampener_vs_stock_pareto import (
    OUT_JSON,
    run_stage477a_pareto,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs/STAGE477A_PB050_RC_PROBE_DAMPENER_VS_STOCK_PARETO.md"


def test_stage477a_pb050_rc_probe_dampener_vs_stock_pareto() -> None:
    rep = run_stage477a_pareto()
    assert OUT_JSON.exists()
    loaded = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert loaded["stage"] == "477A"
    assert loaded["status"] == "CONFIRMED"
    assert loaded["live_devices_touched"] is False

    deltas = loaded["deltas_pb050_vs_stock"]
    assert deltas["goodput_gain_mbps"] > 100.0
    assert deltas["p99_latency_reduction_pct"] > 5.0
    assert deltas["fmx_loss_delta"] < -0.4
    assert loaded["nsga2_pareto_front_count"] >= 5

    audit = audit_stage_receipt_5pillars(loaded)
    assert audit["compliant"] is True

    assert DOC_PATH.exists()
    doc_lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220
    assert doc_lines[0].startswith("<!-- doc-head:")
