"""Stages 173A / 174A / 175A — regression tests.

Pins the three results that matter:

  * 173A closed the ARM gap: `movw`/`movt` recovery yields real register constants where the
    MIPS `lui/addiu` sweep returned zero by construction.
  * 174A reports co-location, not causality: `effect_confirmed` must stay 0.
  * 175A's name-match rate against the Stage 163A champion is very low, and that is the
    finding: airOS knob names and OpenWrt parameter names do not coincide textually.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "audit_stage173a_to_175a_ltu_re_and_rosetta.py"
R173 = REPO / "artifacts" / "autoresearch" / "stage173a_ltu_movw_movt_and_htcomm_switch_re.json"
R174 = REPO / "artifacts" / "autoresearch" / "stage174a_340knobs_umac_athdev_register_sinks.json"
R175 = REPO / "artifacts" / "autoresearch" / "stage175a_571knob_airos_to_openwrt_rosetta_stone.json"


@pytest.fixture(scope="module")
def r173() -> dict:
    assert R173.exists(), f"missing: {R173}"
    return json.loads(R173.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def r174() -> dict:
    assert R174.exists(), f"missing: {R174}"
    return json.loads(R174.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def r175() -> dict:
    assert R175.exists(), f"missing: {R175}"
    return json.loads(R175.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- 173A
def test_173a_eab_absence_recorded(r173: dict) -> None:
    note = r173["meta"]["premise_correction"]
    assert "eab_driver.ko does not exist" in note
    assert r173["summary"]["eab_driver_present"] is False


def test_173a_six_modules(r173: dict) -> None:
    ok = [m for m in r173["modules"] if m.get("status") == "ok"]
    assert len(ok) == 6
    assert {m["module"] for m in ok} == {"ame_core.ko", "ame_dev.ko", "cds_mac_mod.ko"}


def test_173a_modules_are_arm_little_endian(r173: dict) -> None:
    for m in r173["modules"]:
        if m.get("status") == "ok":
            assert m["endian"] == "little"
            assert m["register_constants"]["method"] == "movw/movt (ARM)"


def test_173a_movw_movt_recovers_registers(r173: dict) -> None:
    s = r173["summary"]
    # this is the whole point: the MIPS sweep gave 0 by construction, movw/movt does not
    assert s["movw_movt_pairs"] > 90_000
    assert s["register_constants_total"] > 0, "ARM sweep must not return zero"
    assert s["register_constants_total"] == 14


def test_173a_htcomm_histogram_ranges(r173: dict) -> None:
    for p in r173["ubnt_poll"]:
        hist = p["htcomm"]["opcode_histogram"]
        assert hist
        for k, v in hist.items():
            assert 0 <= int(k) <= 20
            assert v > 0


def test_173a_htcomm_not_overclaimed(r173: dict) -> None:
    gaps = " ".join(r173["gaps"])
    assert "can be an array index or a size rather than an opcode" in gaps


# ---------------------------------------------------------------- 174A
def test_174a_scope_is_the_present_subset(r174: dict) -> None:
    s = r174["summary"]
    assert s["boundary_total"] == 437
    assert s["knobs_in_scope"] <= s["boundary_total"]
    assert s["knobs_in_scope"] > 0


def test_174a_no_effect_is_claimed(r174: dict) -> None:
    assert r174["summary"]["effect_confirmed"] == 0
    assert "UNKNOWN" in " ".join(r174["gaps"])


def test_174a_claim_limit_is_colocation(r174: dict) -> None:
    limit = r174["meta"]["claim_limit"]
    assert "co-location" in limit.lower()
    assert "not proof" in limit.lower()


def test_174a_modules_audited(r174: dict) -> None:
    ok = [m for m in r174["modules"] if m.get("status") == "ok"]
    assert len(ok) == 4
    assert {m["module"] for m in ok} == {"umac.ko", "ath_dev.ko"}


# ---------------------------------------------------------------- 175A
def test_175a_covers_571(r175: dict) -> None:
    assert r175["summary"]["knobs"] == 571
    assert len(r175["knobs"]) == 571


def test_175a_mapping_is_a_candidate_not_equivalence(r175: dict) -> None:
    assert r175["summary"]["equivalence_confirmed"] == 0
    assert "CANDIDATE" in r175["meta"]["claim_limit"]
    for k in r175["knobs"]:
        assert isinstance(k["mapped"], bool)
        if not k["mapped"]:
            assert k["rosetta_candidate"] is None


def test_175a_low_match_rate_is_the_finding(r175: dict) -> None:
    # airOS knob names and OpenWrt parameter names do not coincide textually
    pct = r175["summary"]["mapped_pct"]
    assert pct < 5.0, f"match rate unexpectedly high: {pct}%"
    assert r175["summary"]["mapped"] == 3


def test_175a_champion_hash_recorded(r175: dict) -> None:
    assert r175["meta"]["champion"].endswith("stage163a_cumulative_18round_wa_champion_v2.json")
    assert len(r175["meta"]["champion_sha256"]) == 64


# ---------------------------------------------------------------- shared
def test_all_three_declare_radio_safety(r173: dict, r174: dict, r175: dict) -> None:
    for r in (r173, r174, r175):
        assert "static" in r["meta"]["radio_safety"].lower()


def test_tool_is_reproducible() -> None:
    before = {p.name: p.read_bytes() for p in (R173, R174, R175)}
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    after = {p.name: p.read_bytes() for p in (R173, R174, R175)}
    assert before == after, "receipts are not deterministic across runs"
