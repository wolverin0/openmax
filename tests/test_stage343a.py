from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage343a_ltu_ad9361_sdr_spi_registers_re() -> None:
    receipt_path = ROOT / "artifacts/autoresearch/stage343a_ltu_ad9361_sdr_spi_registers_re.json"
    doc_path = ROOT / "docs/STAGE343A_LTU_AD9361_SDR_SPI_REGISTERS_RE.md"
    assert receipt_path.exists()
    assert doc_path.exists()

    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "343A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_audit"]["touched_dev_ame_nodes"] is False
    assert data["sdr_spi_symbol_count"] > 20
    reg_map = data["ad9361_agile_sdr_register_map"]
    assert reg_map["rx_lo_synthesizer_regs"]["independent_from_tx_lo"] is True
    assert reg_map["tx_lo_synthesizer_regs"]["enables_true_split_spectrum_fdd_tdd"] is True

    doc_lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220
    assert sum(1 for ln in doc_lines if "<!-- doc-head:" in ln) == 1
