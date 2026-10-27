import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "sim" / "run_stage738a_guarida_panel2_activity_aging_and_cbp_pareto.py"
RECEIPT = REPO_ROOT / "artifacts" / "autoresearch" / "stage738a_guarida_panel2_activity_aging_and_cbp_pareto.json"
DOC = REPO_ROOT / "docs" / "STAGE738A_GUARIDA_PANEL2_ACTIVITY_AGING_AND_CBP_PARETO.md"


def test_stage738a_execution_and_receipt():
    res = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=True)
    assert "status=PASS" in res.stdout
    assert RECEIPT.exists()
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["stage"] == "738A"
    assert data["status"] == "PASS"
    assert data["writes_performed"] == 0


def test_stage738a_champion_metrics():
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    champ = data["recommended_champion"]
    assert champ["profile_id"] == "Champion_10ms_67_33_Aging1500_CBP240"
    assert champ["dl_gain_vs_current_pct"] > 34.0
    assert champ["wakeup_latency_reduction_pct"] > 39.0


def test_stage738a_doc_constraints():
    assert DOC.exists()
    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    doc_heads = [l for l in lines if "<!-- doc-head:" in l]
    assert len(doc_heads) == 1
