import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "observability" / "build_stage685a_guarida_34endpoint_production_rollout_playbook_v5.py"
RECEIPT = REPO_ROOT / "artifacts" / "autoresearch" / "stage685a_guarida_34endpoint_production_rollout_playbook_v5.json"
DOC = REPO_ROOT / "docs" / "STAGE685A_GUARIDA_34ENDPOINT_PRODUCTION_ROLLOUT_PLAYBOOK_V5.md"


def test_stage685a_execution_and_receipt():
    res = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=True)
    assert "status=PASS" in res.stdout
    assert RECEIPT.exists()
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["stage"] == "685A"
    assert data["status"] == "PASS"
    assert data["writes_performed"] == 0
    inv = data["topology_inventory_34"]
    assert inv["total_endpoints"] == 34
    assert inv["backhaul_ptp_endpoints"] == 2
    assert inv["sector_cpes_total"] == 32


def test_stage685a_four_phases():
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    phases = data["rollout_phases_v5"]
    assert len(phases) == 4
    assert all(p["watchdog_timeout_s"] == 45 and p["dfs_aware_timeout_s"] == 120 for p in phases)


def test_stage685a_doc_constraints():
    assert DOC.exists()
    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    doc_heads = [l for l in lines if "<!-- doc-head:" in l]
    assert len(doc_heads) == 1
