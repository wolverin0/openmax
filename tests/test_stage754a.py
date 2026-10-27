"""Stage 754A — regression tests.

Pins the three refutations (no NAPI, no coalescing, gic inside vermagic), the scheduler budget, and
the real interrupt surface: PtMP and PtP scheduler IRQ entries plus a frequency-jump check and an
air-queue monitor.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "dissect_stage754a_ltu_eab_driver_irq_coalescing_and_napi_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage754a_ltu_eab_driver_irq_coalescing_and_napi_re.json")

SCHED_IRQ = {"ptmp_sched_irq_entry", "ptp_sched_irq_entry"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "754A"
    for k in ("meta", "absence", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_eab_driver_absent(report: dict) -> None:
    assert report["absence"]["eab_driver"] == 0
    assert report["summary"]["eab_driver_present"] is False


def test_two_modules(ok: list[dict]) -> None:
    assert len(ok) == 2
    assert {r["module"] for r in ok} == {"ame_core.ko", "ame_dev.ko"}


def test_no_napi(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["napi_token_hits"] == 0
    assert s["napi_absent"] == 1
    for r in ok:
        assert r["tokens"]["napi"] == 0
        assert r["tokens"]["NAPI"] == 0


def test_no_coalescing(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["coalescing_token_hits"] == 0
    assert s["coalescing_absent"] == 1
    for r in ok:
        assert r["tokens"]["coalesc"] == 0
        assert r["tokens"]["COALESC"] == 0


def test_gic_is_vermagic(report: dict) -> None:
    s = report["summary"]
    assert s["gic_token_hits"] == 2
    assert s["vermagic_hits"] == 2
    assert s["gic_is_vermagic"] == 1


def test_budget_is_the_scheduler(report: dict) -> None:
    s = report["summary"]
    assert s["sched_budget_hits"] == 2
    assert s["budget_is_scheduler"] == 1
    assert s["poll_is_polling_mode"] == 1
    assert s["polling_mode_hits"] == 2


def test_irq52_is_not_a_string(report: dict) -> None:
    s = report["summary"]
    assert s["irq52_literal"] == 0
    assert s["irq_number_is_a_string"] == 0


def test_scheduler_scoped_irq_entries(report: dict) -> None:
    s = report["summary"]
    assert s["sched_irq_count"] == 2
    assert s["ptmp_ptp_split"] == 1
    assert set(s["sched_irq_entries"]) == SCHED_IRQ
    assert s["airq_exception_handler"] == 1


def test_nothing_recovered(report: dict) -> None:
    s = report["summary"]
    assert s["napi_poll_budget_recovered"] == 0
    assert s["irq_coalescing_recovered"] == 0
    assert s["gic_vector_map_recovered"] == 0


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
