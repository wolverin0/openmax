from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage330a_ltu_management_ipc_re() -> None:
    receipt_path = ROOT / "artifacts/autoresearch/stage330a_ltu_management_ipc_re.json"
    doc_path = ROOT / "docs/STAGE330A_LTU_MANAGEMENT_IPC_RE.md"
    assert receipt_path.exists()
    assert doc_path.exists()

    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "330A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_audit"]["touched_dev_ame_nodes"] is False
    assert data["kernel_ipc_symbol_count"] > 20
    assert len(data["userspace_management_binaries"]) >= 1
    assert data["ipc_architecture"]["polling_intervals_ms"]["ame_core_tdma_superframe_tick_ms"] == 2

    doc_lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220
    assert sum(1 for ln in doc_lines if "<!-- doc-head:" in ln) == 1
