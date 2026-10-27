"""Stage 543A — regression tests.

Pins the eight-symbol ANI lifecycle, the EEPROM spur list, the independent OFDM/CCK knobs, the
PHY-error rate telemetry, and the corrected firstep split (HAL and UMAC, not XW-only).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "build_stage543a_qca988x_ani_ofdm_cck_weak_signal_and_spur_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage543a_qca988x_ani_ofdm_cck_weak_signal_and_spur_re.json")

LIFECYCLE_VERBS = ("attach", "detach", "init_defaults", "reset", "control", "ar_poll")
KNOBS = {"ani_poll_len", "ani_listen_len", "ani_ofdm_level", "ani_cck_level", "dyntxchain"}


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
    assert report["meta"]["stage"] == "543A"
    for k in ("meta", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_seven_modules(ok: list[dict], report: dict) -> None:
    assert len(ok) == 7
    assert report["summary"]["modules_ok"] == 7
    names = {r["module"].split(":")[1] for r in ok}
    assert names == {"ath_hal.ko", "ath_dev.ko", "umac.ko"}


def test_ani_lifecycle_is_complete(report: dict) -> None:
    s = report["summary"]
    assert s["ani_lifecycle_count"] == 8
    assert s["ani_lifecycle_complete_of_6"] == 6
    assert s["ani_state_machine_named"] == 1
    joined = " ".join(s["ani_lifecycle"])
    for verb in LIFECYCLE_VERBS:
        assert verb in joined, verb
    assert "ar9300_ani_get_current_state" in s["ani_lifecycle"]
    assert "ar9300_ani_get_current_stats" in s["ani_lifecycle"]


def test_spur_list_is_eeprom_calibration(report: dict) -> None:
    s = report["summary"]
    assert s["spur_symbol_count"] == 7
    assert s["spur_chans_in_eeprom"] == 1
    joined = " ".join(s["spur_symbols"])
    assert "ar9300_eeprom_get_spur_chans_ptr" in joined
    assert "ar9300_is_ani_noise_spur" in joined
    assert "ar9300_set_spur_info" in joined


def test_immunity_and_gate(report: dict) -> None:
    s = report["summary"]
    assert s["immunity_named"] == 1
    assert "ar9300_set_immunity" in s["immunity_symbols"]
    assert s["ani_enabled_symbol"] == 1


def test_ofdm_and_cck_are_independent(report: dict) -> None:
    s = report["summary"]
    assert s["proc_knob_count"] == 5
    assert set(s["proc_knobs"]) == KNOBS
    assert s["ofdm_and_cck_independent"] == 1


def test_phy_error_rates(report: dict) -> None:
    s = report["summary"]
    assert s["phy_error_rate_count"] == 4
    for key in ("ofdm_phy_err_rate", "cck_phy_err_rate"):
        assert key in s["phy_error_rates"]


def test_firstep_split_is_hal_vs_umac(report: dict) -> None:
    s = report["summary"]
    assert s["firstep_in_xw_hal"] == 1
    assert s["firstep_in_ac_umac"] == 1
    assert s["firstep_hal_umac_split"] == 1
    mods = s["firstep_modules"]
    assert any(m.startswith("XW") and "ath_hal" in m for m in mods)
    assert any("umac" in m for m in mods)


def test_values_not_claimed(report: dict) -> None:
    s = report["summary"]
    assert s["threshold_values_recovered"] == 0
    assert s["ani_state_graph_recovered"] == 0
    joined = " ".join(report["gaps"])
    assert "no numeric firstep" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
