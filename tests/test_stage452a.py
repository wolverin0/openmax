"""Stage 452A — regression tests.

Pins the triple absence (deficit, WMM/AC, penalization), the two token disambiguations (`airtime` =
multicast, `BE` = PROBE), and the real per-station surface (priority + RSSI threshold). All three
recovery counters must stay 0.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "build_stage452a_ubnt_poll_airtime_deficit_and_priority_queues_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage452a_ubnt_poll_airtime_deficit_and_priority_queues_re.json")

PRESENT_KEYS = {"airtime", "prio", "sta_priority", "daprot", "ff_mcast_airtime_limit",
                "ff_sta_rx_rssi_th", "ff_unit_shift", "ff_guard_units", "dack_arbit_max",
                "cms_bias", "voip_bias", "ff_cap_rep"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "452A"
    for k in ("meta", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_two_identical_images(ok: list[dict]) -> None:
    assert len(ok) == 2
    assert {r["version"] for r in ok} == {"WA.v8.7.25", "XC.v8.7.25"}
    assert {r["bytes"] for r in ok} == {189880}
    # identical counts on both images
    assert ok[0]["present"] == ok[1]["present"]
    assert ok[0]["deficit"] == ok[1]["deficit"]


def test_deficit_is_absent(report: dict, ok: list[dict]) -> None:
    assert report["summary"]["deficit_tokens"] == 0
    for r in ok:
        for tok in ("deficit", "quantum", "credit", "surplus"):
            assert r["deficit"][tok] == 0, tok


def test_wmm_is_absent(report: dict, ok: list[dict]) -> None:
    assert report["summary"]["wmm_tokens"] == 0
    for r in ok:
        for tok in ("wmm", "WMM", "AC_BE", "AC_VI", "AC_VO", "AC_BK"):
            assert r["wmm"][tok] == 0, tok


def test_penalization_is_absent(report: dict, ok: list[dict]) -> None:
    assert report["summary"]["penalization_tokens"] == 0
    for r in ok:
        for tok in ("penal", "weight", "low_mcs", "mcs"):
            assert r["penal"][tok] == 0, tok


def test_airtime_is_multicast(ok: list[dict], report: dict) -> None:
    assert report["summary"]["airtime_tokens"] == 4
    assert report["summary"]["mcast_airtime_limit_tokens"] == 4
    for r in ok:
        ctx = " ".join(r["airtime_contexts"])
        assert "ff_mcast_airtime_limit" in ctx


def test_be_is_probe(ok: list[dict], report: dict) -> None:
    assert report["summary"]["be_tokens"] == 6
    assert report["summary"]["modules_where_be_is_probe"] == 2
    for r in ok:
        assert r["ambiguous"]["BE"] == 3
        assert r["ambiguous"]["VI"] == 0
        assert r["ambiguous"]["VO"] == 0
        assert r["ambiguous"]["BK"] == 0
        assert r["be_all_probe"] is True
        for c in r["be_contexts"]:
            assert "PROBE" in c.upper()


def test_priority_surface_is_real(ok: list[dict], report: dict) -> None:
    assert report["summary"]["prio_tokens"] == 12
    syms = report["summary"]["priority_symbols"]
    assert "ubnt_poll_host_set_ap_sta_priority" in syms
    for r in ok:
        assert r["present"]["sta_priority"] == 3
        ctx = " ".join(r["prio_contexts"])
        assert "AP forcing priority" in ctx
        assert "no-auto=" in ctx


def test_rssi_threshold_knob(ok: list[dict], report: dict) -> None:
    assert report["summary"]["rssi_threshold_tokens"] == 4
    assert report["summary"]["rssi_threshold_knob_present"] == 1
    for r in ok:
        assert r["present"]["ff_sta_rx_rssi_th"] == 2
        assert set(r["present"]) == PRESENT_KEYS


def test_nothing_recovered(report: dict) -> None:
    s = report["summary"]
    assert s["deficit_table_recovered"] == 0
    assert s["wmm_weights_recovered"] == 0
    assert s["low_mcs_penalty_recovered"] == 0
    assert s["wmm_symbols"] == []


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
