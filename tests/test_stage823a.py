"""Stage 823A — regression tests.

Pins the airMagic naming refutation, the ubntspecd daemon as the real carrier, the three scoring
tiers, the two capacity guards, the tone geometry, and the refusal to claim the formula.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "dissect_stage823a_airos_ubnt_poll_airmagic_spectral_channel_scoring_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage823a_airos_ubnt_poll_airmagic_spectral_channel_scoring_re.json")


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "823A"
    for k in ("meta", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_five_targets(ok: list[dict], report: dict) -> None:
    assert len(ok) == 5
    assert report["summary"]["modules_ok"] == 5
    names = {r["module"].split(":")[1] for r in ok}
    assert names == {"ubnt_poll_host.ko", "umac.ko", "ubntspecd"}


def test_airmagic_is_not_a_kernel_symbol(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["efficiency_token_hits"] == 0
    assert s["kernel_magic_hits"] == 3
    kern = [r for r in ok if not r["module"].endswith("ubntspecd")]
    for r in kern:
        assert r["tokens"]["airmagic"] == 0
        assert r["tokens"]["Airmagic"] == 0


def test_daemon_is_a_real_binary(report: dict) -> None:
    s = report["summary"]
    assert s["daemon_bytes"] == 47192
    assert s["daemon_is_real_binary"] == 1


def test_three_scoring_tiers(report: dict) -> None:
    s = report["summary"]
    assert s["scoring_tier_count"] == 3
    assert s["scoring_tiers"] == ["BPS", "SCORE", "RATING"]
    assert s["scoring_line_hits"] >= 2
    assert s["best_marker_hits"] >= 1


def test_per_bandwidth_selection(report: dict) -> None:
    s = report["summary"]
    assert s["per_bandwidth_selection"] >= 1
    assert s["channel_list_hits"] >= 1
    assert s["channel_limits_hits"] >= 1


def test_two_capacity_guards(report: dict) -> None:
    s = report["summary"]
    assert s["capacity_guard_count"] == 2
    assert set(s["capacity_guards"]) == {"AMG_MAX_CHANS", "AMG_NUM_CONTROL"}


def test_tone_geometry(report: dict) -> None:
    s = report["summary"]
    assert s["tone_geometry_hits"] >= 1
    assert s["channel_descriptor_hits"] >= 1
    assert s["tone_to_freq_mapping"] == 1


def test_formula_not_claimed(report: dict) -> None:
    s = report["summary"]
    assert s["formula_interface_recovered"] == 1
    assert s["formula_coefficients_recovered"] == 0
    assert s["bps_per_hz_expression_recovered"] == 0
    joined = " ".join(report["gaps"])
    assert "the arithmetic between them is not" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no radio contacted" in scope
    assert "no channel changed" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
