import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage585a_files_and_schema():
    script = ROOT / "tools" / "benchmarks" / "run_stage585a_live_pbe5ac_pb040_pb050_silicon_reg_proof.py"
    artifact = ROOT / "artifacts" / "autoresearch" / "stage585a_live_pbe5ac_pb040_pb050_silicon_reg_proof.json"
    doc = ROOT / "docs" / "STAGE585A_LIVE_PBE5AC_PB040_PB050_SILICON_REG_PROOF.md"
    assert script.exists()
    assert artifact.exists()
    assert doc.exists()
    lines = doc.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")
    data = json.loads(artifact.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 585A"
    assert data["status"] == "CONFIRMED"
    assert data["zero_flash_bytes_modified"] is True
    assert data["ap_241_verified"] is True
    assert data["sta_242_verified"] is True
    assert data["post_reload_1472b_ping"]["loss_pct"] == 0.0
