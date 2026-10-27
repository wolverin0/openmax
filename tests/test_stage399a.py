from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage399a_ltu_dualbank_nand_ameimg_re() -> None:
    receipt_path = ROOT / "artifacts/autoresearch/stage399a_ltu_dualbank_nand_ameimg_re.json"
    doc_path = ROOT / "docs/STAGE399A_LTU_DUALBANK_NAND_AMEIMG_RE.md"
    assert receipt_path.exists()
    assert doc_path.exists()

    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "399A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_audit"]["touched_dev_ame_nodes"] is False
    layout = data["ameimg_container_layout"]
    assert len(layout["dual_bank_mtd_partition_map"]) == 12
    assert "0xae08" in layout["ltu_5board_family_ids"]
    assert "0xae06" in layout["ltu_5board_family_ids"]

    doc_lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220
    assert sum(1 for ln in doc_lines if "<!-- doc-head:" in ln) == 1
