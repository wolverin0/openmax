"""Stage 694A — regression tests.

Pins the EAB family size, the BD interface, the split TX/RX queue readers, the paired FIFO delivery
with its extra lane, the super-queue hierarchy, and the refutations: no zerocopy, no ame_ASIC0, no
Cortex-A7 by name.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "dissect_stage694a_ltu_eab_driver_dma_ring_and_zerocopy_tx_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage694a_ltu_eab_driver_dma_ring_and_zerocopy_tx_re.json")


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "694A"
    for k in ("meta", "absence", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_eab_driver_absent(report: dict) -> None:
    assert report["absence"]["eab_driver"] == 0
    assert report["summary"]["eab_driver_present"] is False


def test_two_modules(ok: list[dict]) -> None:
    assert len(ok) == 2
    assert {r["module"] for r in ok} == {"ame_core.ko", "ame_dev.ko"}


def test_eab_family_is_large(report: dict) -> None:
    s = report["summary"]
    assert s["eab_token_hits"] == 573
    assert s["eab_symbol_count"] == 40
    joined = " ".join(s["eab_symbols"])
    assert "AME_EAB_ActivateQueue" in joined


def test_bd_interface(report: dict) -> None:
    s = report["summary"]
    assert s["bd_interface_named"] == 1
    assert "AME_EAB_PeakBDInterface" in s["bd_interface"]
    assert "AME_EAB_CheckRxQBD" in s["bd_interface"]


def test_tx_rx_queue_info_split(report: dict) -> None:
    s = report["summary"]
    assert s["tx_rx_info_split"] == 1
    assert set(s["queue_info_readers"]) == {"AME_EAB_ReadTXQInfo", "AME_EAB_ReadRXQInfo"}


def test_fifo_pairs_with_extra_lane(report: dict) -> None:
    s = report["summary"]
    assert s["fifo_pair_count"] == 4
    assert s["fifo_has_extra_variant"] == 1
    joined = " ".join(s["fifo_delivery"])
    assert "AME_EAB_DeliverTxFIFO" in joined
    assert "AME_EAB_DeliverTxFIFO_extra" in joined
    assert "AME_EAB_ClearallTxFIFO_extra" in joined


def test_super_queue_hierarchy(report: dict) -> None:
    s = report["summary"]
    assert s["super_queue_hierarchy"] == 1
    assert set(s["queue_activation"]) == {"AME_EAB_ActivateQueue",
                                         "AME_EAB_ActivateSuperQueue"}


def test_zerocopy_and_asic_naming_absent(report: dict) -> None:
    s = report["summary"]
    assert s["zerocopy_token_hits"] == 0
    assert s["zerocopy_absent"] == 1
    assert s["cortex_token_hits"] == 0
    assert s["asic_token_hits"] == 1
    assert s["zerocopy_tx_recovered"] == 0
    assert s["descriptor_layout_recovered"] == 0


def test_asic_reports_capabilities(report: dict) -> None:
    s = report["summary"]
    assert s["capability_json_hits"] == 3
    assert s["asic_capability_report"] == 1


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
