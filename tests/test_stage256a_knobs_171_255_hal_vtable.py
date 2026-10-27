"""Stage 256A — regression tests for knobs 171..255 against ath_dev.ko / ubnt_poll_host.ko.

Pins the finding: this slice is almost entirely absent from the two modules the stage named
(6/85 and 2/85). A future run that starts reporting 85/85 here is a tool bug, not a discovery.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "dissect_stage256a_knobs_171_255_hal_vtable.py"
RECEIPT = REPO / "artifacts" / "autoresearch" / "stage256a_knobs_171_255_hal_vtable.json"


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "256A"
    for k in ("meta", "modules", "summary", "gaps"):
        assert k in report


def test_slice_bounds(report: dict) -> None:
    sl = report["meta"]["slice"]
    assert sl["lo"] == 170 and sl["hi"] == 255 and sl["count"] == 85


def test_targets_are_ath_dev_and_ubnt_poll(ok: list[dict]) -> None:
    mods = {r["module"].split(":")[1] for r in ok}
    assert mods == {"ath_dev.ko", "ubnt_poll_host.ko"}
    assert len(ok) == 4


def test_ath_dev_holds_six(ok: list[dict]) -> None:
    for r in ok:
        if r["module"].endswith("ath_dev.ko"):
            assert r["knobs_with_literal"] == 6, r["module"]


def test_ubnt_poll_holds_two(ok: list[dict]) -> None:
    for r in ok:
        if r["module"].endswith("ubnt_poll_host.ko"):
            assert r["knobs_with_literal"] == 2, r["module"]


def test_slice_is_mostly_absent(report: dict) -> None:
    # the finding: this slice does not live in the two modules the stage named
    assert report["summary"]["knobs_with_literal"] == 6
    assert report["summary"]["knobs_with_literal"] < 10


def test_no_attribution_manufactured(report: dict, ok: list[dict]) -> None:
    assert report["summary"]["knobs_reaching_vtable"] == 0
    for r in ok:
        assert r["knobs_reaching_vtable"] == 0
    assert report["summary"]["slot_histogram"] == {}


def test_method_limit_declared(report: dict) -> None:
    gaps = " ".join(report["gaps"])
    assert "unsound" in gaps


def test_present_knobs_are_identifiable(ok: list[dict]) -> None:
    for r in ok:
        for k in r["knobs"]:
            if k["literal_present"]:
                assert k["rodata_section"].startswith(".rodata")
                assert k["rodata_offset"].startswith("0x")
            else:
                assert "rodata_section" not in k


def test_radio_safety(report: dict) -> None:
    assert "no module loaded" in report["meta"]["scope"]


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
