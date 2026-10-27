"""Stage 714A — regression tests.

Pins the conversion log line, the complete RTT-to-register chain across four modules, both HAL
setters, the readback event, the proc knobs, and the refutation of the ath9k register macros.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "dissect_stage714a_ubnt_poll_ack_cts_timeout_and_distance_clamp_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage714a_ubnt_poll_ack_cts_timeout_and_distance_clamp_re.json")

RTT_CHAIN = {"ubnt_poll_host_set_node_rtt", "ol_ath_rtt_meas_req",
             "wmi_rtt_meas_report_event_handler"}
HAL = {"ar9300_set_ack_timeout", "ar9300_get_ack_timeout", "ar9300_set_slot_time"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "714A"
    for k in ("meta", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_four_modules(ok: list[dict], report: dict) -> None:
    assert len(ok) == 4
    assert report["summary"]["modules_ok"] == 4
    names = {r["module"].split(":")[1] for r in ok}
    assert names == {"ubnt_poll_host.ko", "ath_dev.ko", "ath_hal.ko", "umac.ko"}


def test_conversion_is_named(report: dict) -> None:
    s = report["summary"]
    assert s["conversion_message_hits"] == 1
    assert s["conversion_named"] == 1


def test_rtt_chain_complete(report: dict) -> None:
    s = report["summary"]
    assert s["rtt_chain_count"] == 3
    assert s["rtt_chain_complete"] == 1
    assert set(s["rtt_chain"]) == RTT_CHAIN


def test_both_registers_writable(report: dict) -> None:
    s = report["summary"]
    assert s["hal_setter_count"] == 3
    assert s["both_registers_writable"] == 1
    assert set(s["hal_setters"]) == HAL


def test_readback_path(report: dict) -> None:
    s = report["summary"]
    assert s["readback_present"] == 1
    joined = " ".join(s["readback_path"])
    assert "WMI_ACK_CTS_READ_EVENTID" in joined
    assert "wmi_unified_ack_cts_read_event_handler" in joined


def test_proc_knobs_on_ath_dev(ok: list[dict]) -> None:
    dev = next(r for r in ok if r["module"].endswith("ath_dev.ko"))
    assert dev["tokens"]["distance"] > 0
    # the proc field is spelled acktimeout with no underscore, and it is a string-level
    # name rather than an ELF symbol
    assert dev["tokens"]["acktimeout"] >= 1
    assert dev["tokens"]["get_acktimeout"] >= 1


def test_register_macros_absent(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["register_macro_hits"] == 0
    assert s["register_macros_absent"] == 1
    for r in ok:
        for tok in ("MAC_PCU", "GBL_IFS", "ni_distance", "cts_timeout"):
            assert r["registers"][tok] == 0, tok


def test_formula_and_clamp_not_claimed(report: dict) -> None:
    s = report["summary"]
    assert s["distance_formula_recovered"] == 0
    assert s["distance_clamp_recovered"] == 0
    joined = " ".join(report["gaps"])
    assert "the coefficient" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
