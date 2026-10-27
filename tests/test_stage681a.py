import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "re" / "dissect_stage681a_ubnt_poll_dl_scheduler_and_aggr_budget_re.py"
RECEIPT = REPO_ROOT / "artifacts" / "autoresearch" / "stage681a_ubnt_poll_dl_scheduler_and_aggr_budget_re.json"
DOC = REPO_ROOT / "docs" / "STAGE681A_UBNT_POLL_DL_SCHEDULER_AND_AGGR_BUDGET_RE.md"


def test_stage681a_execution_and_receipt():
    res = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=True)
    assert "status=PASS" in res.stdout
    assert RECEIPT.exists()
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["stage"] == "681A"
    assert data["status"] == "PASS"
    assert data["writes_performed"] == 0
    assert data["ptmp_netconf_104b_struct_map"]["struct_size_bytes"] == 104


def test_stage681a_aggr_budget_profiles():
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    profiles = data["per_node_dl_budget_comparison"]
    assert len(profiles) == 4
    assert profiles[0]["aggr_limit_bytes"] == 10035
    assert profiles[2]["aggr_limit_bytes"] == 2710


def test_stage681a_doc_constraints():
    assert DOC.exists()
    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    doc_heads = [l for l in lines if "<!-- doc-head:" in l]
    assert len(doc_heads) == 1
