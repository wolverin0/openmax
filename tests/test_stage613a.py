import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "observability" / "build_stage613a_guarida_panel2_panel3_safe_tuning_and_migration_matrix_v4.py"
RECEIPT = REPO_ROOT / "artifacts" / "autoresearch" / "stage613a_guarida_panel2_panel3_safe_tuning_and_migration_matrix_v4.json"
DOC = REPO_ROOT / "docs" / "STAGE613A_GUARIDA_PANEL2_PANEL3_SAFE_TUNING_AND_MIGRATION_MATRIX_V4.md"


def test_stage613a_execution_and_receipt():
    res = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=True)
    assert "status=PASS" in res.stdout
    assert RECEIPT.exists()
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["stage"] == "613A"
    assert data["status"] == "PASS"
    assert data["writes_performed"] == 0
    topo = data["guarida_topology_verified"]
    assert topo["total_panels"] == 3
    assert topo["total_cpes"] == 32
    assert topo["sg01_backbone_protected"] is True


def test_stage613a_sectors_and_waves():
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    sectors = {s["sector_id"]: s for s in data["sectors_matrix_v4"]}
    assert set(sectors.keys()) == {"Panel1-Guarida", "Panel2-Guarida", "Panel3-Guarida"}
    assert len(sectors["Panel2-Guarida"]["safe_tuning_and_migration_waves"]) == 3


def test_stage613a_doc_constraints():
    assert DOC.exists()
    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    doc_heads = [l for l in lines if "<!-- doc-head:" in l]
    assert len(doc_heads) == 1
