"""Stage 728A — regression tests.

Pins the vocabulary refutation (thermal/pa_bias absent), the two temperature readers, the five-symbol
gain surface with its fetch/apply split, the stepped autotune, the loopback temperature buffer, and
the compensate ambiguity.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "dissect_stage728a_ltu_ame_core_thermal_and_pa_bias_cal_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage728a_ltu_ame_core_thermal_and_pa_bias_cal_re.json")

TEMPS = {"bbp_rf_get_temperature", "fty_rf_get_temperature"}
GAIN = {"ame_bbp_get_tx_gain", "ame_bbp_set_tx_gain",
        "bbp_rf_fetch_tx_gain", "bbp_rf_apply_tx_gain",
        "ame_bbp_obs_set_txgain"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "728A"
    for k in ("meta", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_two_modules(ok: list[dict]) -> None:
    assert len(ok) == 2
    assert {r["module"] for r in ok} == {"ame_core.ko", "ame_dev.ko"}


def test_thermal_vocabulary_absent(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["thermal_word_hits"] == 0
    assert s["thermal_word_absent"] == 1
    assert s["pa_bias_hits"] == 0
    assert s["pa_bias_absent"] == 1
    for r in ok:
        assert r["tokens"]["thermal"] == 0
        assert r["tokens"]["pa_bias"] == 0
        assert r["tokens"]["bias"] == 0


def test_two_temperature_readers(report: dict) -> None:
    s = report["summary"]
    assert s["temperature_tokens"] == 6
    assert s["temperature_reader_count"] == 2
    assert s["two_temperature_paths"] == 1
    assert set(s["temperature_readers"]) == TEMPS


def test_gain_surface_is_staged(report: dict) -> None:
    s = report["summary"]
    assert s["txgain_tokens"] == 41
    assert s["tx_gain_control_count"] == 5
    assert s["fetch_apply_split"] == 1
    assert GAIN <= set(s["tx_gain_controls"])


def test_autotune_has_a_step(report: dict) -> None:
    s = report["summary"]
    assert s["autotune_present"] == 1
    assert s["autotune_has_step"] == 1
    assert set(s["autotune_controls"]) == {"fty_rf_autotune_txgain",
                                          "fty_rf_adjust_step_txgain"}


def test_power_cal_compensate_and_loopback(report: dict) -> None:
    s = report["summary"]
    assert s["power_cal_compensate"] == 1
    assert s["loopback_temp_buf"] == 1


def test_compensate_is_ambiguous(report: dict) -> None:
    s = report["summary"]
    assert s["compensate_is_airtime"] == 1
    joined = " ".join(report["gaps"])
    assert "sched_airtime_compensate_by_l2bps" in joined


def test_calibration_is_ubus_triggered(report: dict) -> None:
    s = report["summary"]
    assert s["ubus_calibration"] == 1
    assert set(s["ubus_hooks"]) == {"calibrate", "set_rfic_txgain", "get_rfic_txgain"}


def test_curves_not_recovered(report: dict) -> None:
    s = report["summary"]
    assert s["temp_to_gain_curve_recovered"] == 0
    assert s["pa_bias_value_recovered"] == 0


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
