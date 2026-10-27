import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage588a_master_gate():
    script = ROOT / "tools" / "verify" / "verify_stage588a_pbe5ac_ptp_champion_v3_gate.py"
    receipt = ROOT / "artifacts" / "verification" / "stage588a_pbe5ac_ptp_champion_v3_gate_receipt.json"
    doc = ROOT / "docs" / "STAGE588A_PBE5AC_PTP_CHAMPION_V3_GATE.md"
    assert script.exists()
    assert receipt.exists()
    assert doc.exists()
    lines = doc.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")
    data = json.loads(receipt.read_text(encoding="utf-8"))
    assert data["stage"] == "Stage 588A"
    assert data["status"] == "CONFIRMED"
    assert data["all_gates_passed"] is True
