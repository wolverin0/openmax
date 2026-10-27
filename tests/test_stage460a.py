"""Stage 460A — regression tests.

Pins the coalescing refutation (0 strict tokens), the two incidental look-alikes
(`scheduler_budget_us` and "modern"), and the real ring/pool/ISR surface in `ame_core.ko`.
`interrupt_coalescing_recovered` must stay 0.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "build_stage460a_ltu_beetle_dma_ring_and_irq52_coalescing_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage460a_ltu_beetle_dma_ring_and_irq52_coalescing_re.json")

RING_PRIMS = ["ring_init", "ring_pop", "ring_push"]
POOL_PRIMS = ["pkt_pool_get", "pkt_pool_init"]


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def row(report: dict) -> dict:
    return report["modules"][0]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "460A"
    for k in ("meta", "absence", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_eab_driver_absent_again(report: dict) -> None:
    assert report["absence"]["eab_driver.ko"] == 0
    assert report["summary"]["eab_driver_present"] is False


def test_single_module(row: dict, report: dict) -> None:
    assert row["status"] == "ok"
    assert row["module"] == "ame_core.ko"
    assert row["bytes"] == 3282052
    assert report["summary"]["modules_ok"] == 1


def test_coalescing_is_absent(row: dict, report: dict) -> None:
    s = report["summary"]
    assert s["coalescing_tokens"] == 0
    assert s["irq52_literal"] == 0
    assert s["interrupt_coalescing_recovered"] == 0
    for tok in ("coalesc", "coalesce", "irq52", "napi"):
        assert row["coalesce"][tok] == 0, tok


def test_incidental_lookalikes(row: dict, report: dict) -> None:
    s = report["summary"]
    assert s["incidental_tokens"] == 10
    assert row["incidental"]["budget"] == 8
    assert row["incidental"]["moder"] == 2
    budget_ctx = " ".join(row["incidental_contexts"]["budget"])
    assert "scheduler_budget_us" in budget_ctx
    moder_ctx = " ".join(row["incidental_contexts"]["moder"])
    assert "modern" in moder_ctx


def test_ring_primitives(row: dict, report: dict) -> None:
    s = report["summary"]
    assert s["ring_primitives"] == RING_PRIMS
    assert s["dma_ring_named"] == 1
    assert row["ring"]["ring_push"] == 5
    assert row["ring"]["ring_init"] == 3
    assert row["ring"]["ring_pop"] == 1
    assert row["ring"]["dma_ring"] == 0
    ctx = " ".join(row["ring_contexts"])
    assert "ring_push" in ctx and "ring_pop" in ctx


def test_pool_primitives(row: dict, report: dict) -> None:
    s = report["summary"]
    assert s["pool_primitives"] == POOL_PRIMS
    assert s["buffer_recycling_named"] == 1
    assert row["pool"]["recycl"] == 0
    assert "free_pkt_from_pkt_pool" in s["pool_symbols"]


def test_isr_surface_is_registration_based(row: dict, report: dict) -> None:
    s = report["summary"]
    assert s["beacon_irq_named"] == 1
    isr = s["isr_symbols"]
    assert "__ame_core_hook_isr_register" in isr
    assert "__ame_core_hook_hcam_isr_register" in isr
    assert "__ame_core_hook_hfe_isr_register" in isr
    assert "ame_bbp_rt_rx_isr" in isr
    assert row["fabric"]["irq"] == 12


def test_completion_tracking_is_not_recycling(row: dict, report: dict) -> None:
    assert report["summary"]["completion_messages"] == 4
    ctx = " ".join(row["completion_contexts"])
    assert "Not completed yet" in ctx
    joined = " ".join(report["gaps"])
    assert "not a recycling policy" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
