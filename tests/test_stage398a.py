from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage398a_ltu_ble_gatt_provisioning_re() -> None:
    receipt_path = ROOT / "artifacts/autoresearch/stage398a_ltu_ble_gatt_provisioning_re.json"
    doc_path = ROOT / "docs/STAGE398A_LTU_BLE_GATT_PROVISIONING_RE.md"
    assert receipt_path.exists()
    assert doc_path.exists()

    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "398A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_audit"]["touched_dev_ame_nodes"] is False
    assert data["ble_uart_gpio_symbol_count"] > 20
    assert "f_stop" in data["ble_and_provisioning_architecture"]["ame_drv_align_hooks"]["enter_align"]

    doc_lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220
    assert sum(1 for ln in doc_lines if "<!-- doc-head:" in ln) == 1
