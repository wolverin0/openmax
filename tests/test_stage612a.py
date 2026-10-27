import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "sim" / "run_stage612a_guarida_panel2_frame_duration_and_dl_ul_ratio_pareto.py"
RECEIPT = REPO_ROOT / "artifacts" / "autoresearch" / "stage612a_guarida_panel2_frame_duration_and_dl_ul_ratio_pareto.json"
DOC = REPO_ROOT / "docs" / "STAGE612A_GUARIDA_PANEL2_FRAME_DURATION_AND_DL_UL_RATIO_PARETO.md"


def test_stage612a_execution_and_receipt():
    res = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=True)
    assert "status=PASS" in res.stdout
    assert RECEIPT.exists()
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["stage"] == "612A"
    assert data["status"] == "PASS"
    assert data["writes_performed"] == 0
    assert len(data["candidate_simulations"]) == 6
    assert len(data["nsga2_pareto_front"]) >= 1


def test_stage612a_champion_and_ul_constraint():
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    champ = data["recommended_fixed_frame_champion"]
    assert champ["config_id"] == "Fixed_10ms_67_33_Champion"
    assert champ["dl_goodput_gain_vs_baseline_pct"] >= 33.0
    assert champ["ul_goodput_mbps"] >= 18.0


def test_stage612a_doc_constraints():
    assert DOC.exists()
    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    doc_heads = [l for l in lines if "<!-- doc-head:" in l]
    assert len(doc_heads) == 1
