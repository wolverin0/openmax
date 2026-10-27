import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "observability" / "audit_stage611a_guarida_panel2_22cpe_slot_guard_and_evm_radiography.py"
RECEIPT = REPO_ROOT / "artifacts" / "autoresearch" / "stage611a_guarida_panel2_22cpe_slot_guard_and_evm_radiography.json"
DOC = REPO_ROOT / "docs" / "STAGE611A_GUARIDA_PANEL2_22CPE_SLOT_GUARD_AND_EVM_RADIOGRAPHY.md"


def test_stage611a_execution_and_receipt():
    res = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=True)
    assert "status=PASS" in res.stdout
    assert RECEIPT.exists()
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["stage"] == "611A"
    assert data["status"] == "PASS"
    assert data["writes_performed"] == 0
    assert data["panel2_summary"]["total_cpes"] == 22


def test_stage611a_duran_and_slot_guard_metrics():
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    duran = data["rocio_belen_duran_spotlight"]
    assert duran["max_abs_evm_gap_db"] == 11.61
    assert duran["rx_evm_ch0_mean_db"] == 30.0
    assert duran["rx_evm_ch1_mean_db"] == 41.61
    assert duran["hidden_evm_excess_over_rssi_db"] == 10.61
    assert data["panel2_summary"]["max_ul_slice_guard_overhead_pct"] == 26.0


def test_stage611a_doc_constraints():
    assert DOC.exists()
    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    doc_heads = [l for l in lines if "<!-- doc-head:" in l]
    assert len(doc_heads) == 1
