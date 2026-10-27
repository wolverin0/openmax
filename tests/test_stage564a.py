"""Stage 564A — regression tests.

Pins the three get/set pairs, the four sysfs knobs, the three sub-frame getters including the DFS
variant, the RX/TX frequency pair, and the three token refutations (tdma, TDD, split).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "build_stage564a_ltu_ame_core_tdma_framing_and_split_ul_dl_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage564a_ltu_ame_core_tdma_framing_and_split_ul_dl_re.json")

PAIRS = {"frame_len", "duty_cycle", "bc_dl_symbols"}
SYSFS = {"duty_cycle", "frame_len", "bc_dl_symbols", "frame_pulse_offset"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


@pytest.fixture(scope="module")
def by(ok: list[dict]) -> dict[str, dict]:
    return {r["module"]: r for r in ok}


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "564A"
    for k in ("meta", "absence", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_eab_driver_absent(report: dict) -> None:
    assert report["absence"]["eab_driver"] == 0
    assert report["summary"]["eab_driver_present"] is False


def test_two_modules(ok: list[dict], by: dict[str, dict]) -> None:
    assert len(ok) == 2
    assert by["ame_core.ko"]["bytes"] == 3282052
    assert by["ame_dev.ko"]["bytes"] == 298760


def test_three_get_set_pairs(report: dict, by: dict[str, dict]) -> None:
    s = report["summary"]
    assert s["get_set_pair_count"] == 3
    assert set(s["get_set_pairs"]) == PAIRS
    core = by["ame_core.ko"]
    for key in PAIRS:
        assert core["pairs"][key]["get"] >= 1, key
        assert core["pairs"][key]["set"] >= 1, key


def test_four_sysfs_knobs(report: dict, by: dict[str, dict]) -> None:
    s = report["summary"]
    assert s["sysfs_knob_count"] == 4
    assert set(s["sysfs_knobs"]) == SYSFS
    dev = by["ame_dev.ko"]
    for key in SYSFS:
        assert dev["sysfs"][key]["show"] >= 1, key
        assert dev["sysfs"][key]["store"] >= 1, key


def test_three_subframe_getters(report: dict) -> None:
    s = report["summary"]
    assert s["subframe_getter_count"] == 3
    assert "bbp_get_tx_sub_frame_length" in s["subframe_getters"]
    assert "bbp_get_rx_sub_frame_length" in s["subframe_getters"]
    assert "bbp_get_ul_subframe_length_forDFS" in s["subframe_getters"]


def test_rx_tx_freq_pair(report: dict, ok: list[dict]) -> None:
    assert report["summary"]["rx_tx_freq_pair"] == 1
    joined = " ".join(c for r in ok for c in r["ratio_contexts"])
    assert "rx/tx freq" in joined
    assert "duty_cycle:" in joined


def test_token_refutations(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["tdma_literal_hits"] == 0
    assert s["tdd_literal_hits"] == 1
    assert s["split_is_coincidence"] == 1
    joined = " ".join(c for r in ok for c in r["split_context"])
    assert "smart_split" in joined
    tdd = " ".join(c for r in ok for c in r["tdd_context"])
    assert "TDDeRotCFO" in tdd


def test_no_ratio_literals(report: dict) -> None:
    assert report["summary"]["duty_ratio_values_recovered"] == 0
    joined = " ".join(report["gaps"])
    assert "no named ratio" in joined


def test_values_not_recovered(report: dict) -> None:
    s = report["summary"]
    assert s["ul_symbol_schedule_decoded"] == 0
    assert s["synthesizer_programming_recovered"] == 0


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
