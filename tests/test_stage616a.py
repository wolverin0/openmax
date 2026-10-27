"""Stage 616A — regression tests.

Pins the `tof` = `autofa` refutation, the zero hits for ranging/rtt/round_trip, the real distance
measurement (cpe_distance + sysfs pair), the absent timing_adv, and cpsample as the CP length.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "build_stage616a_ltu_ame_core_ranging_tof_and_timing_advance_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage616a_ltu_ame_core_ranging_tof_and_timing_advance_re.json")


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "616A"
    for k in ("meta", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_two_modules(ok: list[dict]) -> None:
    assert len(ok) == 2
    assert {r["module"] for r in ok} == {"ame_core.ko", "ame_dev.ko"}


def test_tof_is_autofa(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["tof_token_hits"] == 29
    assert s["tof_is_autofa"] == 1
    assert s["tof_is_autofa_modules"] >= 1
    joined = " ".join(c for r in ok for c in r["tof_contexts"])
    assert "autofa" in joined


def test_no_ranging(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["ranging_token_hits"] == 0
    assert s["ranging_absent"] == 1
    for r in ok:
        assert r["tokens"]["ranging"] == 0
        assert r["tokens"]["rtt"] == 0
        assert r["tokens"]["round_trip"] == 0


def test_distance_measurement_is_real(report: dict) -> None:
    s = report["summary"]
    assert s["cpe_distance_hits"] == 1
    assert s["distance_meter_symbol_hits"] == 1
    assert s["distance_measurement_present"] == 1
    assert s["distance_sysfs_pairs"] == 1
    assert "cpe_distance" in s["distance_symbols"]
    assert "distance_meter_show" in s["distance_symbols"]
    assert "distance_meter_store" in s["distance_symbols"]


def test_timing_advance_absent(report: dict) -> None:
    s = report["summary"]
    assert s["timing_adv_token_hits"] == 0
    assert s["timing_adv_absent"] == 1
    # the ta_ hits are substring noise, not timing advance
    assert s["ta_token_hits"] > 0


def test_cpsample_is_cp_length(report: dict) -> None:
    s = report["summary"]
    assert s["cpsample_hits"] == 2
    assert s["cyclic_token_hits"] == 0
    assert s["cp_alignment_named"] == 0
    assert s["cp_alignment_offset_recovered"] == 0


def test_autofa_is_a_bonus_finding(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["autofa_symbol_count"] == 15
    # the summary truncates to 12; the full list lives on the module row
    joined = " ".join(n for r in ok for n in r["autofa_symbols"])
    assert "autofa_run_config" in joined
    assert "autofa_force_in_dl" in joined
    assert "autofa_stop" in joined
    assert "autofa_set_speed" in joined


def test_nothing_ranging_recovered(report: dict) -> None:
    s = report["summary"]
    assert s["tof_ranging_recovered"] == 0
    assert s["ta_mechanism_recovered"] == 0
    joined = " ".join(report["gaps"])
    assert "tof is a substring of autofa" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "nothing transmitted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
