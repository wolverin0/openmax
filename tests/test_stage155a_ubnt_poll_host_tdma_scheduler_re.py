"""Stage 155A — regression tests for the ubnt_poll_host TDMA scheduler dissection.

Pins the premise correction (no 8.7.11 WA/XC pair), the WA/XC identity result, and the
honest limits of the opcode/interval reporting.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "audit_stage155a_ubnt_poll_host_tdma_scheduler_re.py"
RECEIPT = REPO / "artifacts" / "autoresearch" / "stage155a_ubnt_poll_host_tdma_scheduler_re.json"


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"receipt missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def by_image(report: dict) -> dict:
    return {m["image"]: m for m in report["modules"] if m.get("status") == "ok"}


def test_receipt_shape(report: dict) -> None:
    for key in ("meta", "modules", "pair_diff", "summary", "gaps"):
        assert key in report
    assert report["meta"]["stage"] == "155A"


def test_premise_correction_recorded(report: dict) -> None:
    note = report["meta"]["premise_correction"]
    assert "no WA.v8.7.11 / XC.v8.7.11 pair" in note
    assert "8.7.25" in note


def test_three_modules_audited(by_image: dict) -> None:
    assert len(by_image) == 3
    assert "WA.v8.7.25" in by_image
    assert "XC.v8.7.25" in by_image
    assert any(k.startswith("8.7.11") for k in by_image)


def test_wa_and_xc_are_not_identical(report: dict, by_image: dict) -> None:
    assert report["pair_diff"]["identical"] is False
    assert by_image["WA.v8.7.25"]["sha256"] != by_image["XC.v8.7.25"]["sha256"]
    assert by_image["WA.v8.7.25"]["bytes"] == by_image["XC.v8.7.25"]["bytes"] == 189880


def test_8711_build_is_smaller(by_image: dict) -> None:
    v = next(m for k, m in by_image.items() if k.startswith("8.7.11"))
    assert v["bytes"] == 186560


def test_scheduler_surface_present(by_image: dict) -> None:
    wa = by_image["WA.v8.7.25"]
    assert len(wa["defined_buckets"].get("scheduler", [])) >= 50
    assert len(wa["ht_comm_symbols"]) >= 3
    assert len(wa["frame_mode_strings"]) >= 1


def test_slot_and_airtime_are_reported_empty(by_image: dict) -> None:
    # the regex buckets find nothing; recording that is the finding, not an omission
    wa = by_image["WA.v8.7.25"]
    assert wa["defined_buckets"].get("slot", []) == []
    assert wa["defined_buckets"].get("airtime", []) == []


def test_opcode_histogram_is_populated(by_image: dict) -> None:
    wa = by_image["WA.v8.7.25"]
    hist = wa["small_constants"]
    assert hist, "no addiu $zero,N constants in 0..20"
    for k, v in hist.items():
        assert 0 <= int(k) <= 20
        assert v > 0


def test_ht_comm_is_not_overclaimed(report: dict) -> None:
    gaps = " ".join(report["gaps"])
    assert "not as a verified message table" in gaps
    assert "can be an array index or a size" in gaps


def test_frame_mode_not_overclaimed(report: dict) -> None:
    gaps = " ".join(report["gaps"])
    assert "not as a decoded state machine" in gaps


def test_radio_safety_declared(report: dict) -> None:
    assert "no radio contacted" in report["meta"]["scope"]


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    after = RECEIPT.read_bytes()
    assert before == after, "receipt is not deterministic across runs"
