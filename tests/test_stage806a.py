"""Stage 806A — regression tests.

Pins the per-segment plan: two segments, 111 ASCII runs, anchors present but none rate-control, zero
viable, and no patch emitted.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "firmware"
        / "build_stage806a_pb070_xtensa_rc_probe_per_sgmt_patch.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage806a_pb070_xtensa_rc_probe_per_sgmt_patch.json")


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "806A"
    assert report["meta"]["gate"] == "PB-070"
    for k in ("meta", "container", "probe_plan", "summary", "gaps"):
        assert k in report


def test_two_segments_with_dual_bases(report: dict) -> None:
    plan = report["probe_plan"]
    assert len(plan) == 2
    assert [p["segment"] for p in plan] == [4, 3]
    assert [p["bytes"] for p in plan] == [7140, 197537]
    for p in plan:
        assert p["load_base_le"] == "0x00980000"
        assert p["load_base_be"] == "0x00009800"


def test_anchors_exist_but_none_is_ratecontrol(report: dict) -> None:
    s = report["summary"]
    assert s["total_ascii_runs"] == 111
    assert s["segments_with_anchor"] == 2
    for p in report["probe_plan"]:
        assert p["anchor_found"] is True
        assert p["anchor_looks_like_rc"] is False


def test_no_patch_emitted(report: dict) -> None:
    s = report["summary"]
    assert s["segments_viable"] == 0
    assert s["patch_emitted"] == 0
    assert s["patch_bytes_would_be"] == 4
    assert s["blocking_reason"]


def test_reasons_are_stated(report: dict) -> None:
    for p in report["probe_plan"]:
        assert p["viable"] is False
        assert p["reason"]


def test_nothing_written(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no firmware written" in scope
    assert "no flash touched" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
