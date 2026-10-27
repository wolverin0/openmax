import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "sim" / "run_stage684a_guarida_panel2_panel3_tdma_frame_alignment_pareto.py"
RECEIPT = REPO_ROOT / "artifacts" / "autoresearch" / "stage684a_guarida_panel2_panel3_tdma_frame_alignment_pareto.json"
DOC = REPO_ROOT / "docs" / "STAGE684A_GUARIDA_PANEL2_PANEL3_TDMA_FRAME_ALIGNMENT_PARETO.md"


def test_stage684a_execution_and_receipt():
    res = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=True)
    assert "status=PASS" in res.stdout
    assert RECEIPT.exists()
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["stage"] == "684A"
    assert data["status"] == "PASS"
    assert data["writes_performed"] == 0


def test_stage684a_zero_overlap_champion():
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    champ = data["recommended_tower_alignment_champion"]
    assert champ["profile_id"] == "Synchronized_10ms_67_33_Champion_0us_Offset"
    assert champ["tx_rx_self_interference_overlap_pct"] == 0.0
    assert champ["tower_goodput_gain_vs_current_pct"] > 7.0


def test_stage684a_doc_constraints():
    assert DOC.exists()
    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    doc_heads = [l for l in lines if "<!-- doc-head:" in l]
    assert len(doc_heads) == 1
