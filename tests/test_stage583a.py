import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage583a_files_and_schema():
    script = ROOT / "tools" / "benchmarks" / "run_stage583a_live_pbe5ac_vht40_pktlog_zero_champion_v3.py"
    artifact = ROOT / "artifacts" / "autoresearch" / "stage583a_live_pbe5ac_vht40_pktlog_zero_champion_v3.json"
    doc = ROOT / "docs" / "STAGE583A_LIVE_PBE5AC_VHT40_PKTLOG_ZERO_CHAMPION_V3.md"
    assert script.exists()
    assert artifact.exists()
    assert doc.exists()
    lines = doc.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")
    data = json.loads(artifact.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 583A"
    assert data["status"] == "CONFIRMED"
    assert len(data["windows"]) == 4
    assert data["summary"]["arm_b_mean_aggregate_mbps"] > data["summary"]["arm_a_mean_aggregate_mbps"]
