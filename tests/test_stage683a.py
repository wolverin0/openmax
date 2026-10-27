import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "observability" / "audit_stage683a_panel1_guarida_84_per_tid_aql_and_atf_20h.py"
RECEIPT = REPO_ROOT / "artifacts" / "autoresearch" / "stage683a_panel1_guarida_84_per_tid_aql_and_atf_20h.json"
DOC = REPO_ROOT / "docs" / "STAGE683A_PANEL1_GUARIDA_84_PER_TID_AQL_AND_ATF_20H.md"


def test_stage683a_execution_and_receipt():
    res = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=True)
    assert "status=PASS" in res.stdout
    assert RECEIPT.exists()
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["stage"] == "683A"
    assert data["status"] == "PASS"
    assert data["writes_performed"] == 0


def test_stage683a_zero_non_tid0_drops_over_20h():
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    s = data["sector_summary_20h"]
    assert s["total_packets_all_tids"] == 39405365
    assert s["total_tid0_be_packets"] == 38158175
    assert s["total_non_tid0_packets"] == 1247190
    assert s["non_tid0_codel_drops"] == 0
    assert s["total_aql_overlimit_events"] == 0
    assert s["active_backlog_bytes_all_tids"] == 0


def test_stage683a_doc_constraints():
    assert DOC.exists()
    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    doc_heads = [l for l in lines if "<!-- doc-head:" in l]
    assert len(doc_heads) == 1
