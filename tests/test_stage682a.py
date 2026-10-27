import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "observability" / "audit_stage682a_guarida_panel3_6cpe_slot_guard_and_evm_radiography.py"
RECEIPT = REPO_ROOT / "artifacts" / "autoresearch" / "stage682a_guarida_panel3_6cpe_slot_guard_and_evm_radiography.json"
DOC = REPO_ROOT / "docs" / "STAGE682A_GUARIDA_PANEL3_6CPE_SLOT_GUARD_AND_EVM_RADIOGRAPHY.md"


def test_stage682a_execution_and_receipt():
    res = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=True)
    assert "status=PASS" in res.stdout
    assert RECEIPT.exists()
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["stage"] == "682A"
    assert data["status"] == "PASS"
    assert data["writes_performed"] == 0
    assert data["panel3_summary"]["total_cpes"] == 6


def test_stage682a_sosa_joaquin_metrics():
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    sosa = data["sosa_joaquin_spotlight"]
    assert sosa["abs_delta_rssi_db"] == 0
    assert sosa["abs_rx_evm_gap_db"] == 14.21
    assert sosa["abs_tx_evm_gap_db"] == 16.26
    assert sosa["total_sub27db_samples_across_256"] == 115
    rem = data["sosa_remediation_impact"]
    assert rem["ul_airtime_reduction_per_mbit_pct"] == 54.99
    assert rem["dl_airtime_reduction_per_mbit_pct"] == 32.49


def test_stage682a_doc_constraints():
    assert DOC.exists()
    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    doc_heads = [l for l in lines if "<!-- doc-head:" in l]
    assert len(doc_heads) == 1
