import json
import pathlib
import subprocess
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
VERIFY_SCRIPT = REPO_ROOT / "tools" / "verify" / "verify_stage686a_guarida_dl_sched_and_panel3_gate.py"
VERIFY_RECEIPT = REPO_ROOT / "artifacts" / "verification" / "stage686a_guarida_dl_sched_and_panel3_gate_receipt.json"
CURATED_DOC = REPO_ROOT / "docs" / "CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md"


def test_stage686a_master_verifier_runs_cleanly():
    res = subprocess.run([sys.executable, str(VERIFY_SCRIPT)], capture_output=True, text=True, check=True)
    assert "status=PASS" in res.stdout
    assert VERIFY_RECEIPT.exists()
    data = json.loads(VERIFY_RECEIPT.read_text(encoding="utf-8"))
    assert data["status"] == "PASS"
    assert data["writes_performed"] == 0
    assert data["fmx_disc_53_curated"] is True
    assert data["fmx_disc_54_curated"] is True


@pytest.mark.parametrize(
    "stage_id",
    ["681A", "682A", "683A", "684A", "685A"],
)
def test_each_stage_receipt_5pillar_compliant(stage_id):
    data = json.loads(VERIFY_RECEIPT.read_text(encoding="utf-8"))
    audits = {r["stage"]: r for r in data["receipt_audits"]}
    assert stage_id in audits
    assert audits[stage_id]["status"] == "PASS"
    assert audits[stage_id]["writes_performed"] == 0
    assert audits[stage_id]["compliant_5pillar"] is True


def test_all_docs_under_200_lines_and_single_doc_head():
    data = json.loads(VERIFY_RECEIPT.read_text(encoding="utf-8"))
    for d in data["doc_audits"]:
        assert d["under_200_lines"] is True, f"{d['doc']} has {d['line_count']} lines"
        assert d["doc_head_count"] == 1, f"{d['doc']} has {d['doc_head_count']} doc-heads"


def test_curated_discoveries_53_and_54():
    text = CURATED_DOC.read_text(encoding="utf-8")
    assert "FMX-DISC-53" in text
    assert "FMX-DISC-54" in text
    assert len(text.splitlines()) < 220
