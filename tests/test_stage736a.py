import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "observability" / "audit_stage736a_guarida_panel2_22cpe_dl_aggr_collapse_and_airtime_hog.py"
RECEIPT = REPO_ROOT / "artifacts" / "autoresearch" / "stage736a_guarida_panel2_22cpe_dl_aggr_collapse_and_airtime_hog.json"
DOC = REPO_ROOT / "docs" / "STAGE736A_GUARIDA_PANEL2_22CPE_DL_AGGR_COLLAPSE_AND_AIRTIME_HOG.md"


def test_stage736a_execution_and_receipt():
    res = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=True)
    assert "status=PASS" in res.stdout
    assert RECEIPT.exists()
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["stage"] == "736A"
    assert data["status"] == "PASS"
    assert data["writes_performed"] == 0
    assert data["sector_hog_summary"]["total_cpes"] == 22


def test_stage736a_hog_metrics():
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    s = data["sector_hog_summary"]
    assert s["ideal_mcs15_aggr_limit_bytes"] == 10035
    assert s["min_aggr_limit_bytes"] == 2710
    assert s["max_airtime_hog_multiplier"] == 3.7
    assert s["sector_dl_capacity_gain_pct"] > 15.0


def test_stage736a_doc_constraints():
    assert DOC.exists()
    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    doc_heads = [l for l in lines if "<!-- doc-head:" in l]
    assert len(doc_heads) == 1
