"""Stage 648A — regression tests.

Pins the ARQ/HARQ naming refutation, the per-CPE BLER pair with its coded and per-MCS variants, the
tunable LDPC iteration count, the queue retry descriptor, and the four sysfs pairs.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "build_stage648a_ltu_ame_core_arq_retrans_and_fec_ldpc_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage648a_ltu_ame_core_arq_retrans_and_fec_ldpc_re.json")

SYSFS = {"bler", "c_bler", "each_bler", "ldpc_iteration"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "648A"
    for k in ("meta", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_two_modules(ok: list[dict]) -> None:
    assert len(ok) == 2
    assert {r["module"] for r in ok} == {"ame_core.ko", "ame_dev.ko"}


def test_no_arq_or_harq(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["assumed_token_hits"] == 0
    assert s["arq_harq_absent"] == 1
    for r in ok:
        for tok in ("arq", "ARQ", "harq", "HARQ", "retrans", "nack"):
            assert r["assumed"].get(tok, 0) == 0 or r["tokens"][tok] == 0, tok


def test_bler_is_per_cpe(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["bler_token_hits"] == 42
    assert s["bler_symbol_count"] == 20
    assert s["cpe_rx_tx_bler_pair"] == 1
    # the summary truncates to 10; the full list lives on the module row
    joined = " ".join(n for r in ok for n in r["bler_symbols"])
    assert "cpeRxBler" in joined
    assert "cpeTxBler" in joined


def test_coded_and_per_mcs_bler(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["coded_bler_present"] == 1
    assert s["each_bler_present"] == 1
    joined = " ".join(n for r in ok for n in r["bler_symbols"])
    assert "check_cbler_decode" in joined
    assert "autoMCS_get_each_bler" in joined


def test_ldpc_iteration_is_tunable(report: dict) -> None:
    s = report["summary"]
    assert s["ldpc_token_hits"] == 22
    assert s["ldpc_symbol_count"] == 7
    assert s["ldpc_iteration_controls"] == 4
    assert s["ldpc_iteration_tunable"] == 1
    assert s["ldpc_capability_check"] >= 1
    assert s["no_ldpc_message"] >= 1


def test_retry_descriptor_is_a_queue_triple(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["retry_descriptor_lines"] == 2
    assert s["retry_descriptor_present"] == 1
    joined = " ".join(c for r in ok for c in r["retry_contexts"])
    assert "reIdx=%d, retry=%d" in joined
    assert "tail=%d" in joined


def test_four_sysfs_pairs(report: dict) -> None:
    s = report["summary"]
    assert s["sysfs_pair_count"] == 4
    assert set(s["sysfs_pairs"]) == SYSFS


def test_state_machines_not_recovered(report: dict) -> None:
    s = report["summary"]
    assert s["arq_state_machine_recovered"] == 0
    assert s["harq_combining_recovered"] == 0
    assert s["fec_block_table_recovered"] == 0


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
