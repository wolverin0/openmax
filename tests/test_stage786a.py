"""Stage 786A — regression tests.

Pins the frame_pulse_offset get/set pair and its sysfs knob, the two SFN sync predicates, and the
semantic refutation: cli_isolation isolates clients, and coloc/sector/panel do not exist.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "dissect_stage786a_ltu_ame_core_colocated_frame_pulse_sync_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage786a_ltu_ame_core_colocated_frame_pulse_sync_re.json")

FPO = {"ame_bbp_set_frame_pulse_offset", "ame_bbp_get_frame_pulse_offset"}
SYNC = {"ame_bbp_is_remote_SFN_synchronized", "bbp_base_is_remote_SFN_synchronized"}
CLI = {"ame_core_get_cli_isolation", "ame_core_set_cli_isolation"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "786A"
    for k in ("meta", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_two_modules(ok: list[dict]) -> None:
    assert len(ok) == 2
    assert {r["module"] for r in ok} == {"ame_core.ko", "ame_dev.ko"}


def test_frame_pulse_offset_is_a_knob(report: dict) -> None:
    s = report["summary"]
    assert s["frame_pulse_offset_getset"] == 1
    assert set(s["frame_pulse_offset_accessors"]) == FPO
    assert s["frame_pulse_offset_sysfs_pairs"] == 1
    assert s["frame_alignment_knob_present"] == 1


def test_sfn_sync_predicates(report: dict) -> None:
    s = report["summary"]
    assert s["sync_predicate_variants"] == 2
    assert set(s["sync_predicates"]) == SYNC
    assert s["remote_sfn_sync_named"] == 1


def test_cli_isolation_is_client_isolation(report: dict) -> None:
    s = report["summary"]
    assert s["cli_isolation_getset"] == 1
    assert set(s["cli_isolation_accessors"]) == CLI
    assert s["cli_isolation_is_client_not_panel"] == 1


def test_coloc_sector_panel_absent(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["assumed_vocabulary_hits"] == 0
    assert s["coloc_sector_panel_absent"] == 1
    for r in ok:
        for tok in ("coloc", "sector", "panel"):
            assert r["assumed"][tok] == 0, tok


def test_panel_isolation_not_recovered(report: dict) -> None:
    s = report["summary"]
    assert s["tx_rx_isolation_recovered"] == 0
    assert s["panel_isolation_scheme_recovered"] == 0
    joined = " ".join(report["gaps"])
    assert "NOT panel isolation" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
