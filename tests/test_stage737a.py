import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "observability" / "audit_stage737a_guarida_backbone_60_61_ampdu_and_shift_preflight.py"
RECEIPT = REPO_ROOT / "artifacts" / "autoresearch" / "stage737a_guarida_backbone_60_61_ampdu_and_shift_preflight.json"
DOC = REPO_ROOT / "docs" / "STAGE737A_GUARIDA_BACKBONE_60_61_AMPDU_AND_SHIFT_PREFLIGHT.md"


def test_stage737a_execution_and_receipt():
    res = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=True)
    assert "status=PASS" in res.stdout
    assert RECEIPT.exists()
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["stage"] == "737A"
    assert data["status"] == "PASS"
    assert data["writes_performed"] == 0


def test_stage737a_preflight_and_lockstep():
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    checks = data["preflight_checklist"]
    assert len(checks) == 5
    assert all(c["status"] == "PASS" for c in checks)
    assert data["backbone_telemetry"]["guarida_61_sta"]["ast_rxorn_to_ppdu_lockstep_pct"] == 98.53
    assert data["expected_shift_outcome"]["net_goodput_gain_mbps"] == 17.17


def test_stage737a_doc_constraints():
    assert DOC.exists()
    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    doc_heads = [l for l in lines if "<!-- doc-head:" in l]
    assert len(doc_heads) == 1
