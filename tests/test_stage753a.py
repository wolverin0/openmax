"""Stage 753A — regression tests.

Pins the two-phase ANI loop, the OFDM and CCK action sets, mrc_cck and barker_threshold, the
diagnosed reset, the separate proc knobs, the HAL lifecycle with its logging callback, and the
spur-immunity controls.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "dissect_stage753a_qca988x_ani_ofdm_cck_immunity_steppers_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage753a_qca988x_ani_ofdm_cck_immunity_steppers_re.json")

OFDM = {"firstep", "cycpwr"}
CCK = {"mrc_cck", "barker_threshold"}
KNOBS = {"ani_poll_len", "ani_listen_len", "ani_ofdm_level", "ani_cck_level", "dyntxchain"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "753A"
    for k in ("meta", "modules", "summary", "gaps", "ath10k_modules"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_ath10k_absent(report: dict) -> None:
    assert report["ath10k_modules"] == 0
    assert report["summary"]["ath10k_core_present"] is False


def test_six_modules(ok: list[dict], report: dict) -> None:
    assert len(ok) == 6
    assert report["summary"]["modules_ok"] == 6
    names = {r["module"].split(":")[1] for r in ok}
    assert names == {"umac.ko", "ath_dev.ko", "ath_hal.ko"}


def test_two_phase_loop(report: dict) -> None:
    s = report["summary"]
    assert s["update_line_count"] == 2
    assert s["control_line_count"] == 3
    assert s["two_phase_loop"] == 1


def test_ofdm_and_cck_action_sets(report: dict) -> None:
    s = report["summary"]
    assert s["ofdm_action_set"] == 1
    assert s["cck_action_set"] == 1
    assert set(s["ofdm_actions"]) == OFDM
    assert set(s["cck_actions"]) == CCK


def test_mrc_cck_and_barker(report: dict) -> None:
    s = report["summary"]
    assert s["mrc_cck_present"] == 1
    assert s["mrc_cck_hits"] == 6
    assert s["barker_threshold_present"] == 1


def test_reset_is_diagnosed(report: dict) -> None:
    s = report["summary"]
    assert s["reset_line_hits"] == 2
    assert s["reset_is_diagnosed"] == 1


def test_proc_knobs_are_separate(report: dict) -> None:
    s = report["summary"]
    assert s["proc_knob_count"] == 5
    assert set(s["proc_knobs"]) == KNOBS


def test_hal_owns_lifecycle_and_logs(report: dict) -> None:
    s = report["summary"]
    assert s["hal_lifecycle_count"] == 6
    assert s["spur_immunity_present"] == 1
    assert s["log_callback_present"] == 1


def test_thresholds_not_recovered(report: dict) -> None:
    s = report["summary"]
    assert s["thresholds_recovered"] == 0
    assert s["stepper_increments_recovered"] == 0
    assert s["state_machine_named"] == 1


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
