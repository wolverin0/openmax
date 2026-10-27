"""Pytest suite for Stage 593A PBE-5AC-Gen2 VHT20/VHT40/VHT80 Triple-Play Pareto."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage593a_pareto_receipt():
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage593a_pbe5ac_vht20_vht40_vht80_triple_play_pareto.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "593A"
    assert data["status"] == "CONFIRMED"
    assert data["live_bench_grounding"]["stage487a_vht40_solo_tcp_mbps"] == 24.83
    assert data["live_bench_grounding"]["stage488a_triple_play_iptv_loss_pct"] == 0.0
    assert data["selected_champion"] == "VHT40_PEER_SYNC_FQ_CODEL_CHAMPION"


def test_stage593a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE593A_PBE5AC_VHT20_VHT40_VHT80_TRIPLE_PLAY_PARETO.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
