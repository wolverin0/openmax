import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage587a_files_and_schema():
    script = ROOT / "tools" / "benchmarks" / "build_stage587a_pbe5ac_lbe5ac_multibw_champion_v3_matrix.py"
    artifact = ROOT / "artifacts" / "autoresearch" / "stage587a_pbe5ac_lbe5ac_multibw_champion_v3_matrix.json"
    doc = ROOT / "docs" / "STAGE587A_PBE5AC_LBE5AC_MULTIBW_CHAMPION_V3_MATRIX.md"
    assert script.exists()
    assert artifact.exists()
    assert doc.exists()
    lines = doc.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")
    data = json.loads(artifact.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 587A"
    assert data["status"] == "CONFIRMED"
    assert "comparison_matrix" in data
