import json
import pathlib
import subprocess
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
VERIFY_SCRIPT = REPO_ROOT / "tools" / "verify" / "verify_stage614a_guarida_slot_guard_and_amsdu_gate.py"
VERIFY_RECEIPT = REPO_ROOT / "artifacts" / "verification" / "stage614a_guarida_slot_guard_and_amsdu_gate_receipt.json"
CURATED_DOC = REPO_ROOT / "docs" / "CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md"


def test_stage614a_master_verifier_runs_cleanly():
    res = subprocess.run([sys.executable, str(VERIFY_SCRIPT)], capture_output=True, text=True, check=True)
    assert "status=PASS" in res.stdout
    assert VERIFY_RECEIPT.exists()
    data = json.loads(VERIFY_RECEIPT.read_text(encoding="utf-8"))
    assert data["status"] == "PASS"
    assert data["writes_performed"] == 0
    assert data["fmx_disc_51_curated"] is True
    assert data["fmx_disc_52_curated"] is True


@pytest.mark.parametrize(
    "stage_id",
    ["609A", "610A", "611A", "612A", "613A"],
)
def test_each_stage_receipt_5pillar_compliant(stage_id):
    data = json.loads(VERIFY_RECEIPT.read_text(encoding="utf-8"))
    audits = {r["stage"]: r for r in data["receipt_audits"]}
    assert stage_id in audits
    assert audits[stage_id]["status"] == "PASS"
    assert audits[stage_id]["writes_performed"] == 0
    assert audits[stage_id]["compliant_5pillar"] is True


def test_all_docs_under_220_lines_and_single_doc_head():
    data = json.loads(VERIFY_RECEIPT.read_text(encoding="utf-8"))
    for d in data["doc_audits"]:
        assert d["under_220_lines"] is True, f"{d['doc']} has {d['line_count']} lines"
        assert d["doc_head_count"] == 1, f"{d['doc']} has {d['doc_head_count']} doc-heads"


def test_curated_discoveries_51_and_52():
    text = CURATED_DOC.read_text(encoding="utf-8")
    assert "FMX-DISC-51" in text
    assert "FMX-DISC-52" in text
    assert len(text.splitlines()) < 220
