"""Stage 544A — regression tests.

Pins the TX-power/attenuation conversion pair, the variable-length DPD sysfs interface, the EVM
instrumentation family, 4096-QAM naming, and the `backoff` disambiguation (cross-frame, not TX).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "build_stage544a_ltu_ame_core_tx_power_lut_and_pa_dpd_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage544a_ltu_ame_core_tx_power_lut_and_pa_dpd_re.json")

DPD_IFACE = ["dpd_load", "dpd_show", "dpd_store"]


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
    assert report["meta"]["stage"] == "544A"
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


def test_conversion_pair(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["conversion_pair_hits"] == 5
    assert s["conversion_pair_named"] == 1
    joined = " ".join(r["module"] for r in ok)
    core = by_module(ok, "ame_core.ko")
    assert core["conversion"]["calculate_tx_power_by_attenuation"] >= 1
    assert core["conversion"]["calculate_tx_attenuation_by_power"] >= 1
    assert joined


def by_module(ok: list[dict], name: str) -> dict:
    return next(r for r in ok if r["module"] == name)


def test_dpd_is_variable_length_with_sysfs(report: dict) -> None:
    s = report["summary"]
    assert s["dpd_sysfs_interface"] == DPD_IFACE
    assert s["dpd_table_is_variable_length"] == 1
    assert s["dpd_symbol_count"] == 5
    assert "ame_bbp_set_dpd" in s["dpd_symbols"]
    assert "ame_bbp_get_dpd" in s["dpd_symbols"]


def test_pa_and_txpower(by: dict[str, dict], report: dict) -> None:
    s = report["summary"]
    assert s["pa_symbol_count"] >= 10
    assert s["txpower_symbol_count"] == 17
    core = by["ame_core.ko"]
    assert core["tokens"]["dpd"] >= 1
    assert core["tokens"]["txpower"] >= 1


def test_evm_family(by: dict[str, dict], report: dict) -> None:
    s = report["summary"]
    assert s["evm_symbol_count"] == 23
    evm = " ".join(s["evm_symbols"])
    assert "ame_bbp_op_evm" in evm
    core = by["ame_core.ko"]
    assert core["tokens"]["evm"] >= 20


def test_4096_qam_named(report: dict) -> None:
    s = report["summary"]
    assert s["super4096_named"] == 1
    assert s["super4096_symbols"]
    joined = " ".join(s["super4096_symbols"])
    assert "4096" in joined


def test_backoff_is_crossframe(report: dict, by: dict[str, dict]) -> None:
    s = report["summary"]
    assert s["backoff_is_crossframe_modules"] == 1
    core = by["ame_core.ko"]
    assert core["backoff_is_crossframe"] is True
    assert core["tokens"]["backoff"] == 25
    joined = " ".join(report["gaps"])
    assert "cz_cross_frame_backoff" in joined


def test_calibration_is_ubus(report: dict, by: dict[str, dict]) -> None:
    s = report["summary"]
    assert s["calib_symbol_count"] >= 10
    dev = by["ame_dev.ko"]
    calib = " ".join(dev["calib_symbols"])
    assert "calibrate" in calib
    assert "set_rfic_txgain" in calib or "get_rfic_txgain" in calib


def test_values_not_recovered(report: dict) -> None:
    s = report["summary"]
    assert s["lut_values_recovered"] == 0
    assert s["dpd_coefficients_recovered"] == 0
    assert s["evm_backoff_db_recovered"] == 0


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
