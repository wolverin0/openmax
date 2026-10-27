"""Stage 668A — regression tests.

Pins the complete SFN family with separate RX/TX counters, the GPS requirement and CIR fallback,
and the three token refutations: 1pps absent, pps = packets per second, ptp = point-to-point.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "dissect_stage668a_ltu_ame_core_gps_1pps_and_frame_sync_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage668a_ltu_ame_core_gps_1pps_and_frame_sync_re.json")

SFN = {"ame_bbp_get_rx_sfn", "ame_bbp_set_rx_sfn", "ame_bbp_get_tx_sfn",
       "ame_bbp_set_tx_sfn", "ame_bbp_op_sync_sfn", "ame_bbp_sync_SFN"}
SYNC = {"ame_bbp_get_sync_sfn_count", "ame_bbp_is_remote_SFN_synchronized",
        "ame_bbp_set_remote_SFN", "ame_bbp_get_sync_mode", "ame_bbp_set_sync_mode"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "668A"
    for k in ("meta", "absence", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_eab_driver_absent(report: dict) -> None:
    assert report["absence"]["eab_driver"] == 0
    assert report["summary"]["eab_driver_present"] is False


def test_two_modules(ok: list[dict]) -> None:
    assert len(ok) == 2
    assert {r["module"] for r in ok} == {"ame_core.ko", "ame_dev.ko"}


def test_sfn_family_is_complete(report: dict) -> None:
    s = report["summary"]
    assert s["sfn_symbol_count"] == 28
    assert s["sfn_token_hits"] == 207
    assert s["sfn_counter_count"] == 6
    assert set(s["sfn_counter_symbols"]) == SFN
    assert s["superframe_clock_named"] == 1


def test_rx_and_tx_sfn_are_separate(report: dict) -> None:
    s = report["summary"]
    assert s["rx_tx_sfn_separate"] == 1
    assert s["remote_sfn_synchronized"] == 1
    assert s["sync_control_count"] == 5
    assert set(s["sync_controls"]) == SYNC


def test_gps_is_a_requirement(report: dict) -> None:
    s = report["summary"]
    assert s["gps_token_hits"] == 44
    assert s["gps_required_message"] == 1
    assert s["gps_sync_required"] >= 1


def test_one_pps_does_not_exist(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["one_pps_hits"] == 0
    assert s["one_pps_absent"] == 1
    for r in ok:
        assert r["tokens"]["1pps"] == 0


def test_pps_means_packets_per_second(report: dict) -> None:
    s = report["summary"]
    assert s["pps_trap_hits"] == 2
    assert s["pps_is_packets_per_second"] == 1


def test_ptp_is_point_to_point(report: dict) -> None:
    s = report["summary"]
    assert s["ptp_token_hits"] == 26
    assert s["ptp_trap_hits"] >= 1
    assert s["ptp_is_point_to_point"] == 1
    joined = " ".join(s["ptp_symbols"])
    assert "PtP" in joined


def test_nothing_claimed_for_the_pps_source(report: dict) -> None:
    s = report["summary"]
    assert s["one_pps_source_recovered"] == 0
    assert s["sfn_epoch_alignment_recovered"] == 0


def test_radio_safety(report: dict) -> None:
    assert report["meta"]["radio_safety"] == "static_only"
    assert "no module loaded" in report["meta"]["scope"]


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
