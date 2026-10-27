"""Stage 416A — regression tests.

Pins the identical duration vocabulary across WA / XC / 2XC, the three literals that do not exist
(`gps_sync`, `frame_offset`, any `coloc` marker), and the hard blocker: `ubnt-gps-reader` is a
zero-byte file. `sync_state_machine_recovered` must stay 0.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "ubnt_poll_gps_sync_1pps_timingslot_re.py"
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage416a_ubnt_poll_gps_sync_1pps_re.json")

DURATIONS = {"down_dur": 24, "up_dur": 18, "cbp_dur": 12, "fixed_frame": 3}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "416A"
    for k in ("meta", "modules", "gps_reader_candidates", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_three_modules(ok: list[dict]) -> None:
    assert len(ok) == 3
    names = {r["module"].split(":")[0] for r in ok}
    assert names == {"WA.v8.7.25", "XC.v8.7.25", "2XC.v8.7.11"}
    sizes = {r["bytes"] for r in ok}
    assert sizes == {189880, 186560}


def test_duration_vocabulary_is_identical(ok: list[dict], report: dict) -> None:
    assert report["summary"]["duration_hits"] == DURATIONS
    assert report["summary"]["fixed_frame_present"] == 1
    for r in ok:
        assert r["durations"]["down_dur"] == 8
        assert r["durations"]["up_dur"] == 6
        assert r["durations"]["cbp_dur"] == 4
        assert r["durations"]["fixed_frame"] == 1


def test_gps_and_pps_present(ok: list[dict], report: dict) -> None:
    assert report["summary"]["pps_hits"] == 12
    assert report["summary"]["gps_hits"] == 9
    assert report["summary"]["modules_with_pps"] == 3
    for r in ok:
        assert r["sync"]["pps"] == 4
        assert r["sync"]["gps"] == 3


def test_sync_literals_absent(report: dict, ok: list[dict]) -> None:
    assert report["summary"]["gps_sync_literal"] == 0
    assert report["summary"]["frame_offset_literal"] == 0
    for r in ok:
        assert r["sync"]["gps_sync"] == 0
        assert r["sync"]["frame_offset"] == 0
        assert r["sync"]["1pps"] == 0


def test_no_coloc_marker(report: dict, ok: list[dict]) -> None:
    assert report["summary"]["coloc_hits"] == 0
    for r in ok:
        for tok in ("coloc", "co-loc", "colocated", "auto_interference", "sector"):
            assert r["coloc"][tok] == 0, (r["module"], tok)


def test_gps_reader_is_empty(report: dict) -> None:
    s = report["summary"]
    assert s["gps_reader_files"] == 4
    assert s["gps_reader_readable"] == 0
    existing = [c for c in report["gps_reader_candidates"] if c["exists"]]
    assert len(existing) == 2
    for c in existing:
        assert c["bytes"] == 0
        assert c["readable"] is False


def test_frame_periods_not_enumerated(report: dict) -> None:
    strings = report["summary"]["frame_ms_strings"]
    assert set(strings) == {"5ms", "8ms", "10ms", "5 ms", "8 ms", "10 ms"}
    assert all(v == 0 for v in strings.values()), strings


def test_state_machine_not_recovered(report: dict) -> None:
    assert report["summary"]["sync_state_machine_recovered"] == 0
    joined = " ".join(report["gaps"])
    assert "zero-byte files" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
