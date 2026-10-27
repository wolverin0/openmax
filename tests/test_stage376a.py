from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage376a_ltu_rocket_arria10_fpga_mailbox_re() -> None:
    receipt_path = ROOT / "artifacts/autoresearch/stage376a_ltu_rocket_arria10_fpga_mailbox_re.json"
    doc_path = ROOT / "docs/STAGE376A_LTU_ROCKET_ARRIA10_FPGA_MAILBOX_RE.md"
    assert receipt_path.exists()
    assert doc_path.exists()

    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "376A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_audit"]["touched_dev_ame_nodes"] is False
    arch = data["dual_soc_fpga_architecture"]
    assert arch["ap_vs_cpe_code_delta_bytes"] == 5660
    assert 100 in arch["channel_100mhz_synthesis"]["supported_bandwidths_mhz"]
    assert data["fpga_mailbox_symbol_count"] > 20

    doc_lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220
    assert sum(1 for ln in doc_lines if "<!-- doc-head:" in ln) == 1
