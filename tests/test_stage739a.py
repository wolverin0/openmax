import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "observability" / "build_stage739a_guarida_34endpoint_operator_field_action_card_v6.py"
RECEIPT = REPO_ROOT / "artifacts" / "autoresearch" / "stage739a_guarida_34endpoint_operator_field_action_card_v6.json"
DOC = REPO_ROOT / "docs" / "STAGE739A_GUARIDA_34ENDPOINT_OPERATOR_FIELD_ACTION_CARD_V6.md"


def test_stage739a_execution_and_receipt():
    res = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=True)
    assert "status=PASS" in res.stdout
    assert RECEIPT.exists()
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["stage"] == "739A"
    assert data["status"] == "PASS"
    assert data["writes_performed"] == 0
    assert data["summary"]["total_endpoints_scored"] == 34


def test_stage739a_all_34_endpoints_have_semaphore_and_action():
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    cards = data["endpoints_scorecard_34"]
    assert len(cards) == 34
    valid_statuses = {"OK", "REMEDIAR ANTENA", "AJUSTAR TDMA"}
    for c in cards:
        assert c["semaphore_status"] in valid_statuses
        assert c["expected_gain_mbps"] > 0
        assert len(c["one_line_action"]) > 15


def test_stage739a_doc_constraints():
    assert DOC.exists()
    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    doc_heads = [l for l in lines if "<!-- doc-head:" in l]
    assert len(doc_heads) == 1
