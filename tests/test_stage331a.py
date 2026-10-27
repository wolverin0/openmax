from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage331a_ltu_dfs_radar_engine_re() -> None:
    receipt_path = ROOT / "artifacts/autoresearch/stage331a_ltu_dfs_radar_engine_re.json"
    doc_path = ROOT / "docs/STAGE331A_LTU_DFS_RADAR_ENGINE_RE.md"
    assert receipt_path.exists()
    assert doc_path.exists()

    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "331A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_audit"]["touched_dev_ame_nodes"] is False
    assert data["dfs_radar_symbol_count"] > 20
    assert data["beetle_fpga_radar_detectors"]["zero_wait_cac_architecture"]["standard_cac_seconds"] == 60
    assert data["beetle_fpga_radar_detectors"]["zero_wait_cac_architecture"]["twdr_cac_seconds"] == 600

    doc_lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220
    assert sum(1 for ln in doc_lines if "<!-- doc-head:" in ln) == 1
