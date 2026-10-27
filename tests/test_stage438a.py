"""Stage 438A — regression tests.

Pins the refutation of the LQ framing (20 tokens, 0 format strings, 4 printable hits inside a
base64-style table) and the real N/S two-class scheduler with NtoS/StoN transition counters.
`eab_driver.ko` must stay absent and the 16-CPE threshold must stay unrecovered.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "build_stage438a_ltu_ame_core_poll_scheduler_and_slot_alloc_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage438a_ltu_ame_core_poll_scheduler_and_slot_alloc_re.json")


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def row(report: dict) -> dict:
    return report["modules"][0]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "438A"
    for k in ("meta", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_eab_driver_still_absent(report: dict) -> None:
    assert report["summary"]["eab_driver_present"] is False


def test_module_identity(row: dict, report: dict) -> None:
    assert row["status"] == "ok"
    assert row["module"] == "ame_core.ko"
    assert row["bytes"] == 3282052
    assert report["summary"]["module_ok"] == 1


def test_sq_is_real(row: dict, report: dict) -> None:
    assert report["summary"]["sq_tokens"] == 6
    assert report["summary"]["sq_string_contexts"] == 6
    ctx = " ".join(h["context"] for h in row["sq"])
    assert "Top NQ CPE" in ctx
    assert "Min SQ CPE" in ctx
    assert "SQ-CPE" in ctx
    assert "numSQ" in ctx


def test_lq_is_not_a_token(row: dict, report: dict) -> None:
    assert report["summary"]["lq_tokens"] == 20
    assert report["summary"]["lq_string_contexts"] == 0
    assert all(h["format"] is False for h in row["lq"])
    # the four printable hits are the base64-style lookup table, not logs
    assert report["summary"]["lq_printable_contexts"] == 4
    printable = [h for h in row["lq"] if h["printable"]]
    assert printable
    assert any("BINSXZ" in h["context"] for h in printable)


def test_queue_words_absent(report: dict, row: dict) -> None:
    assert report["summary"]["long_queue_tokens"] == 0
    assert report["summary"]["short_queue_tokens"] == 0


def test_transition_counters_exist(report: dict, row: dict) -> None:
    assert row["counts"]["NtoS"] == 1
    assert row["counts"]["StoN"] == 1
    assert report["summary"]["ntos_contexts"] == 1
    assert report["summary"]["ston_contexts"] == 1
    ctx = " ".join(h["context"] for h in row["sq"])
    assert "(NtoS=%d)" in ctx
    assert "(StoN=%d)" in ctx


def test_nq_and_swq_present(report: dict) -> None:
    assert report["summary"]["nq_tokens"] == 1
    assert report["summary"]["swq_tokens"] == 3


def test_scheduler_pipeline(row: dict, report: dict) -> None:
    assert report["summary"]["sched_tokens"] == 297
    assert report["summary"]["scheduler_symbols"] == 40
    sample = report["summary"]["scheduler_symbols_sample"]
    assert "AME_HSM_add_sched_result" in sample
    assert "AME_SchedAutoMCS" in sample
    assert "AME_SchedCheckActiveCPE" in sample
    assert report["summary"]["ofdma_tokens"] == 88
    assert report["summary"]["poll_tokens"] == 2
    ctx = " ".join(h["context"] for h in row["poll"])
    assert "enter polling mode" in ctx


def test_slot_is_overloaded(report: dict) -> None:
    assert report["summary"]["slot_tokens"] == 41
    joined = " ".join(report["gaps"])
    assert "crypto keystore slots" in joined


def test_nothing_fabricated(report: dict) -> None:
    s = report["summary"]
    assert s["threshold_16_present"] == 0
    assert s["sq_lq_split_recovered"] == 0
    assert s["nq_sq_split_recovered"] == 1
    joined = " ".join(report["gaps"])
    assert "LQ has zero format-string contexts" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
