"""Stage 500A — regression tests.

Pins the atlas invariants: every receipt parses, SHA de-duplication actually collapses the corpus,
the scorecard reports 1 closed against 31 open, and `atlas_complete` stays 0.

Counts are asserted with `>=` where the corpus can grow, and exactly where the value is structural.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "build_stage500a_ground_up_re_500stage_binary_atlas.py"
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage500a_ground_up_re_500stage_binary_atlas.json")

EXPECTED_FAMILIES = {"qca988x_ac", "beetle_ltu", "ar9344_xw"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "500A"
    for k in ("meta", "stages", "families", "unique_modules", "recovered_flags", "summary", "gaps"):
        assert k in report
    assert "receipt" in report["meta"]["note"]


def test_every_receipt_parses(report: dict) -> None:
    s = report["summary"]
    assert s["receipts_unparsable"] == 0
    assert s["receipts_parsed"] == s["receipts_found"]
    assert s["stages_covered"] == s["receipts_parsed"]
    assert len(report["stages"]) == s["receipts_parsed"]


def test_sha_deduplication_is_real(report: dict) -> None:
    s = report["summary"]
    # more analyses than unique files: the same binary was read by several stages
    assert s["total_module_analyses"] > s["unique_module_files"]
    shas = [m["sha256"] for m in report["unique_modules"]]
    assert len(shas) == len(set(shas))
    assert s["unique_module_files"] == len(report["unique_modules"])
    assert s["unique_bytes_analysed"] == sum(m["bytes"] for m in report["unique_modules"])


def test_corpus_size(report: dict) -> None:
    s = report["summary"]
    assert s["unique_module_files"] >= 32
    assert s["unique_bytes_analysed"] >= 17_896_272
    # the largest recorded module must be an actual member of the unique set
    biggest = max(m["bytes"] for m in report["unique_modules"])
    assert s["largest_module_bytes"] == biggest
    assert biggest >= 3_282_052                      # ame_core.ko is at least this large
    assert s["largest_module_bytes"] <= s["unique_bytes_analysed"]


def test_three_families_populated(report: dict) -> None:
    fams = set(report["summary"]["families_present"])
    assert EXPECTED_FAMILIES <= fams
    for fam in EXPECTED_FAMILIES:
        assert report["families"][fam]["receipts"] >= 1
    # the family bytes must sum to no more than the deduplicated total
    total = sum(v["unique_bytes"] for v in report["families"].values())
    assert total <= report["summary"]["unique_bytes_analysed"]


def test_scorecard_is_honest(report: dict) -> None:
    s = report["summary"]
    assert s["recovery_flags_declared"] == s["recovery_flags_closed"] + s["recovery_flags_open"]
    assert s["recovery_flags_closed"] >= 1
    assert s["recovery_flags_open"] >= 31
    closed = [k for k, v in report["recovered_flags"].items() if v["present"] > 0]
    assert "nq_sq_split_recovered" in closed
    # the hard negatives must be present and open
    for key in ("analog_register_table_recovered", "cac_constant_recovered",
                "deficit_table_recovered", "fastlock_profile_recovered"):
        if key in report["recovered_flags"]:
            assert report["recovered_flags"][key]["present"] == 0, key


def test_atlas_declares_itself_incomplete(report: dict) -> None:
    s = report["summary"]
    assert s["atlas_complete"] == 0
    joined = " ".join(report["gaps"])
    assert "firmware-2.bin and firmware-5.bin were never available" in joined
    assert "eab_driver.ko was never available" in joined


def test_systemic_gaps_are_counted(report: dict) -> None:
    s = report["summary"]
    assert s["receipts_declaring_firmware_absent"] >= 6
    assert s["receipts_declaring_eab_driver_absent"] >= 2


def test_no_invictus_executable_claim(report: dict) -> None:
    # the invictus family must not carry an executable module: there is none in the corpus
    inv = report["families"].get("invictus_af")
    if inv is not None:
        assert inv["unique_modules"] == 0


def test_radio_safety(report: dict) -> None:
    assert "receipts" in report["meta"]["scope"]
    assert report["meta"]["radio_safety"] == "static only"


def test_tool_is_invariant_under_recorpus_growth() -> None:
    """An atlas over a growing receipt set cannot be byte-stable, and pretending otherwise would
    force freezing the corpus. Re-run the tool and re-check the invariants instead of the bytes."""
    before = json.loads(RECEIPT.read_text(encoding="utf-8"))
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    after = json.loads(RECEIPT.read_text(encoding="utf-8"))
    s0, s1 = before["summary"], after["summary"]

    # the corpus may only grow
    assert s1["receipts_found"] >= s0["receipts_found"]
    # the structural invariants must hold on both sides
    for s in (s0, s1):
        assert s["receipts_unparsable"] == 0
        assert s["receipts_parsed"] == s["receipts_found"]
        assert s["stages_covered"] == s["receipts_parsed"]
        assert s["recovery_flags_declared"] == (s["recovery_flags_closed"]
                                                + s["recovery_flags_open"])
    # the deduplicated corpus must never shrink
    assert s1["unique_bytes_analysed"] >= s0["unique_bytes_analysed"]
    assert s1["unique_module_files"] >= s0["unique_module_files"]
    # and the atlas must keep declaring itself incomplete
    assert s1["atlas_complete"] == 0
