"""Stage 807A — regression tests.

Pins the subchannel-vocabulary refutation, the named ulmap subsystem, the dense OFDMA surface, and
the split-frequency pair plus separate preference keys.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "dissect_stage807a_ltu_split_freq_and_ofdma_subchannel_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage807a_ltu_split_freq_and_ofdma_subchannel_re.json")


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "807A"
    for k in ("meta", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_two_modules(ok: list[dict]) -> None:
    assert len(ok) == 2
    assert {r["module"] for r in ok} == {"ame_core.ko", "ame_dev.ko"}


def test_subchannel_vocabulary_absent(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["subchannel_token_hits"] == 0
    assert s["subchannel_vocabulary_absent"] == 1
    for r in ok:
        for tok in ("subchannel", "sub_chan", "ru_"):
            assert r["tokens"][tok] == 0, tok


def test_ulmap_is_the_real_name(report: dict) -> None:
    s = report["summary"]
    assert s["ulmap_token_hits"] == 20
    assert s["ulmap_symbol_count"] == 17
    assert s["ulmap_is_named_subsystem"] == 1
    joined = " ".join(s["ulmap_symbols"])
    assert "ULMap" in joined


def test_ofdma_surface_is_dense(report: dict) -> None:
    s = report["summary"]
    assert s["ofdma_token_hits"] == 102
    assert s["ofdma_symbol_count"] == 22


def test_split_frequency(report: dict) -> None:
    s = report["summary"]
    assert s["split_freq_pair_present"] == 1
    assert s["split_freq_line_hits"] == 4
    assert s["split_pref_present"] == 1
    assert s["split_preference_keys"] == 2


def test_maps_not_recovered(report: dict) -> None:
    s = report["summary"]
    assert s["subchannel_map_recovered"] == 0
    assert s["ru_allocation_table_recovered"] == 0


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "nothing transmitted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
