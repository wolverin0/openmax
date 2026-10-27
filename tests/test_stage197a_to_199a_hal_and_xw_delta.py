"""Stages 197A / 198A / 199A — regression tests.

Pins three negative/structural results:

  * 197A: `ah_reg_write` and `OS_REG_WRITE` do not exist in `ath_hal.ko`; only
    `wmi_unified_cmd_send` is real. The stage's own title named two accessors that are absent.
  * 198A: 18 champion rounds yield candidate knob sets, and **zero** proven equivalences.
  * 199A: XW.v6.3.6 and WA.v8.7.25 share 17 `ubntbox` applets and 10 `athbox` applets, but that
    compares airOS 6 against airOS 8, so the delta conflates version and product line.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "audit_stage197a_to_199a_hal_and_xw_delta.py"
R197 = REPO / "artifacts" / "autoresearch" / "stage197a_ath_hal_vtable_and_wmi_accessor_re.json"
R198 = REPO / "artifacts" / "autoresearch" / "stage198a_18effect_empirical_rosetta_stone.json"
R199 = REPO / "artifacts" / "autoresearch" / "stage199a_xw_vs_wa_ubntbox_athbox_delta_re.json"


@pytest.fixture(scope="module")
def r197() -> dict:
    assert R197.exists(), f"missing: {R197}"
    return json.loads(R197.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def r198() -> dict:
    assert R198.exists(), f"missing: {R198}"
    return json.loads(R198.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def r199() -> dict:
    assert R199.exists(), f"missing: {R199}"
    return json.loads(R199.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- 197A
def test_197a_premise_refuted_in_receipt(r197: dict) -> None:
    note = r197["meta"]["premise_correction"]
    assert "ah_reg_write and OS_REG_WRITE do not exist" in note
    assert "wmi_unified_cmd_send does exist" in note


def test_197a_accessor_presence(r197: dict) -> None:
    s = r197["summary"]
    assert s["ah_reg_write_present"] is False
    assert s["os_reg_write_present"] is False
    assert s["wmi_unified_cmd_send_present"] is True


def test_197a_four_modules(r197: dict) -> None:
    ok = [m for m in r197["modules"] if m.get("status") == "ok"]
    assert len(ok) == 4
    assert r197["summary"]["modules"] == 4


def test_197a_symbol_inventory_non_empty(r197: dict) -> None:
    s = r197["summary"]
    assert s["reg_write_symbols"] > 0, "no reg-write symbols at all is implausible"
    assert s["hal_vtable_symbols"] > 0, "no HAL vtable symbols at all is implausible"


def test_197a_does_not_claim_a_resolved_vtable(r197: dict) -> None:
    gaps = " ".join(r197["gaps"])
    assert "was not traced to a concrete vtable slot" in gaps


# ---------------------------------------------------------------- 198A
def test_198a_eighteen_rounds(r198: dict) -> None:
    assert r198["summary"]["rounds"] == 18
    assert len(r198["rounds"]) == 18
    assert r198["summary"]["champion_rounds_declared"] == 18


def test_198a_candidates_are_candidates(r198: dict) -> None:
    assert r198["summary"]["equivalence_confirmed"] == 0
    assert "candidate" in r198["meta"]["claim_limit"].lower()
    for r in r198["rounds"]:
        assert isinstance(r["airoa_candidates"], list)
        assert r["candidate_count"] == len(r["airoa_candidates"])


def test_198a_partial_coverage_is_the_finding(r198: dict) -> None:
    s = r198["summary"]
    # six rounds describe interventions with no textual overlap with the catalogue
    assert s["rounds_with_candidates"] == 12
    assert s["rounds_with_candidates"] < s["rounds"]


def test_198a_no_equivalence_claimed(r198: dict) -> None:
    gaps = " ".join(r198["gaps"])
    assert "not a mapping" in gaps
    assert "not proofs" in gaps


# ---------------------------------------------------------------- 199A
def test_199a_premise_correction(r199: dict) -> None:
    assert "WA.v8.7.11 does not exist" in r199["meta"]["premise_correction"]
    assert "WA.v8.7.25" in r199["meta"]["premise_correction"]


def test_199a_applet_counts(r199: dict) -> None:
    s = r199["summary"]
    assert s["ubntbox_wa"] == 29
    assert s["ubntbox_xw"] == 25
    assert s["athbox_wa"] == 15
    assert s["athbox_xw"] == 10


def test_199a_delta_sets_are_consistent(r199: dict) -> None:
    d = r199["delta"]["ubntbox"]
    assert d["common_count"] == len(d["common"])
    assert d["common_count"] + len(d["only_in_wa"]) == d["wa_count"]
    assert d["common_count"] + len(d["only_in_xw"]) == d["xw_count"]
    # no overlap between the exclusive sets
    assert not set(d["only_in_wa"]) & set(d["only_in_xw"])


def test_199a_athbox_has_no_xw_only_applet(r199: dict) -> None:
    assert r199["summary"]["athbox_only_xw"] == 0


def test_199a_conflation_is_declared(r199: dict) -> None:
    gaps = " ".join(r199["gaps"])
    assert "conflates versions and product lines" in gaps


# ---------------------------------------------------------------- shared
def test_all_three_declare_radio_safety(r197: dict, r198: dict, r199: dict) -> None:
    for r in (r197, r198, r199):
        assert "static" in r["meta"]["radio_safety"].lower()


def test_tool_is_reproducible() -> None:
    before = {p.name: p.read_bytes() for p in (R197, R198, R199)}
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    after = {p.name: p.read_bytes() for p in (R197, R198, R199)}
    assert before == after, "receipts are not deterministic across runs"
