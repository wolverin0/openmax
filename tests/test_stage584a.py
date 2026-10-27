import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage584a_files_and_schema():
    script = ROOT / "tools" / "benchmarks" / "run_stage584a_live_pbe5ac_vht80_clean_assoc_and_qpsk_sweep.py"
    artifact = ROOT / "artifacts" / "autoresearch" / "stage584a_live_pbe5ac_vht80_clean_assoc_and_qpsk_sweep.json"
    doc = ROOT / "docs" / "STAGE584A_LIVE_PBE5AC_VHT80_CLEAN_ASSOC_AND_QPSK_SWEEP.md"
    assert script.exists()
    assert artifact.exists()
    assert doc.exists()
    lines = doc.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")
    data = json.loads(artifact.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 584A"
    assert data["status"] == "CONFIRMED"
    assert data["post_restore_vht20_1472b_ping"]["loss_pct"] == 0.0
