"""Stage 372A — regression tests.

Pins the positive results (the full command name, the id as an aligned literal at index 17 of a
dense slot array, five of six schema tokens present) and the negatives that must never be
quietly promoted (no `lui`+`ori` build of the id, no `series_bw`, no WMI surface in
`ubnt_poll_host.ko`, no recovered retry table).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "wmi_0x9044_peer_rate_retry_sched_re.py"
RECEIPT = REPO / "artifacts" / "autoresearch" / "stage372a_wmi_0x9044_peer_rate_retry_sched_re.json"


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


@pytest.fixture(scope="module")
def umacs(ok: list[dict]) -> list[dict]:
    return [r for r in ok if r["module"].endswith("umac.ko")]


@pytest.fixture(scope="module")
def poll(ok: list[dict]) -> list[dict]:
    return [r for r in ok if r["module"].endswith("ubnt_poll_host.ko")]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "372A"
    for k in ("meta", "modules", "summary", "gaps"):
        assert k in report
    assert report["meta"]["wmi_id"] == "0x9044"


def test_four_modules_two_of_each(ok: list[dict], umacs: list[dict], poll: list[dict]) -> None:
    assert len(ok) == 4
    assert len(umacs) == 2
    assert len(poll) == 2


def test_command_name_is_present_and_complete(umacs: list[dict]) -> None:
    for r in umacs:
        assert r["probe_hits"]["PEER_RATE_RETRY"] == 1
        assert r["probe_hits"]["RETRY_SCHED"] == 1
        ctx = r["peer_rate_retry_context"]
        assert ctx, "no context captured for PEER_RATE_RETRY"
        assert "WMI_PEER_RATE_RETRY_SCHED_CMDID" in ctx[0]["context"]
        nt = r["name_table_position"]
        assert nt is not None
        assert nt["preceding_strings"] == 7485
        assert nt["section_strings"] == 8295


def test_poll_host_has_no_wmi_surface(poll: list[dict]) -> None:
    for r in poll:
        assert r["probe_hits"]["PEER_RATE_RETRY"] == 0
        assert r["name_table_position"] is None
        assert r["id_literals"]["aligned_count"] == 0
        assert r["wmi_id_site_count"] == 0


def test_id_is_never_built_by_instruction_pair(umacs: list[dict], report: dict) -> None:
    # REFUTED: no lui+ori materialises 0x9044
    for r in umacs:
        assert r["wmi_id_site_count"] == 0
        assert r["wmi_id_sites"] == []
    assert report["summary"]["modules_with_numeric_id"] == 0
    assert report["summary"]["numeric_id_sites"] == 0


def test_unaligned_hits_are_coincidences(umacs: list[dict], poll: list[dict],
                                         report: dict) -> None:
    """The alignment split is the whole discriminator.

    `umac.ko` carries 1 aligned literal per image (the slot-array entry) and 11 unaligned
    coincidences. `ubnt_poll_host.ko` carries 69 unaligned and 0 aligned — on raw word count it
    would look like the busiest WMI module, which it is not.
    """
    for r in umacs:
        lit = r["id_literals"]
        assert lit["aligned_count"] == 1
        assert lit["unaligned_count"] == 11
    for r in poll:
        lit = r["id_literals"]
        assert lit["aligned_count"] == 0
        assert lit["unaligned_count"] == 69
        assert lit["verdict"] == "no aligned literal: all hits straddle instructions"
    for r in umacs + poll:
        for off in r["id_literals"]["unaligned"]:
            assert int(off, 16) % 4 != 0
        for off in r["id_literals"]["aligned"]:
            assert int(off, 16) % 4 == 0
    assert report["summary"]["unaligned_id_literals"] == 160  # 2*11 + 2*69
    assert report["summary"]["aligned_id_literals"] == 2


def test_id_sits_at_index_17_of_a_dense_slot_array(umacs: list[dict]) -> None:
    for r in umacs:
        run = r["id_table_run"]
        assert run is not None
        assert run["contains_target"] is True
        assert run["count"] == 32           # capture cap reached, so >= 32
        assert run["trailing_values"] == ["0x00000102"]
        ids = [e["id"] for e in run["entries"]]
        assert ids[0] == "0x9000"
        # dense stride-4 enumeration
        for a, b in zip(ids, ids[1:]):
            assert int(b, 16) - int(a, 16) == 4
        assert ids[17] == "0x9044"
        # 8 bytes per entry
        ats = [int(e["at"], 16) for e in run["entries"]]
        for a, b in zip(ats, ats[1:]):
            assert b - a == 8


def test_trailing_word_never_varies(umacs: list[dict]) -> None:
    # therefore it cannot be a per-command length
    for r in umacs:
        assert len(r["id_table_run"]["trailing_values"]) == 1


def test_series_tokens_present_but_series_bw_absent(umacs: list[dict],
                                                    report: dict) -> None:
    for r in umacs:
        h = r["probe_hits"]
        for tok in ("LDPC", "STBC", "SGI", "txchainmask", "2x2", "CDD"):
            assert h[tok] > 0, f"{tok} unexpectedly absent"
        assert h["series_bw"] == 0
        assert h["retry_sched"] == 0
        assert h["peer_rate_retry"] == 0
    assert report["summary"]["series_field_names_found"] == 4


def test_retry_table_never_reported_recovered(report: dict) -> None:
    assert report["summary"]["retry_table_recovered"] == 0
    joined = " ".join(report["gaps"])
    assert "no 4-series table was reconstructed" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
