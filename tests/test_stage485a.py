"""Stage 485A — regression tests.

Pins the software-timer bmiss lifecycle, the three CSA variants, the roam timer inside the
connection SM, and the absence of `WMI_VDEV_PARAM_BMISS_COUNT_MAX`.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "build_stage485a_qca988x_bmiss_and_csa_channel_switch_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage485a_qca988x_bmiss_and_csa_channel_switch_re.json")

LIFECYCLE = ("alloc_id", "enable", "disable", "free_id")


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "485A"
    for k in ("meta", "firmware_images", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_firmware_absent(report: dict) -> None:
    assert report["firmware_images"] == {"firmware-2.bin": 0, "firmware-5.bin": 0}
    assert report["summary"]["firmware_images_present"] == 0


def test_two_identical_images(ok: list[dict], report: dict) -> None:
    assert len(ok) == 2
    assert ok[0]["bmiss"] == ok[1]["bmiss"]
    assert report["summary"]["modules_ok"] == 2


def test_bmiss_is_a_software_timer(report: dict) -> None:
    s = report["summary"]
    assert s["bmiss_symbol_count"] == 20
    assert s["swbmiss_lifecycle_named"] == 1
    assert s["bmiss_state_machine_named"] == 1
    swb = s["swbmiss_symbols"]
    assert len(swb) == 14
    for stage in LIFECYCLE:
        assert any(stage in n for n in swb), stage
    assert any("print_status" in n for n in swb)


def test_bmiss_reset_and_indication(ok: list[dict]) -> None:
    for r in ok:
        named = " ".join(r["bmiss_symbols"])
        assert "ieee80211_mlme_reset_bmiss" in named
        assert "ieee80211_mlme_sta_bmiss_ind" in named
        assert "beacon_miss" in named


def test_three_csa_variants(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["csa_variant_count"] == 3
    assert s["csa_variants"] == ["CSA", "E-CSA", "UCSA"]
    assert s["csa_symbol_count"] == 16
    assert s["csa_state_machine_named"] == 1
    ctx = " ".join(ok[0]["csa_contexts"])
    assert "UCSA new channel" in ctx
    assert "E-CSA new channel" in ctx
    assert "center1" in ctx


def test_csa_phases(report: dict) -> None:
    syms = " ".join(report["summary"]["csa_symbols"])
    for tok in ("recv_csa", "chanswitch_continue", "start_csa", "vap_request_csa"):
        assert tok in syms, tok


def test_wmi_switch_both_directions(report: dict) -> None:
    wmi = report["summary"]["wmi_switch_symbols"]
    assert "wmi_unified_vdev_chan_switch_send" in wmi
    assert "wmi_unified_chan_switch_handler" in wmi


def test_roam_is_a_timer_in_connection_sm(report: dict) -> None:
    s = report["summary"]
    assert s["roam_symbol_count"] == 14
    assert s["roam_state_machine_named"] == 1
    joined = " ".join(s["roam_symbols"])
    assert "connection_sm" in joined or "roam_check" in joined


def test_bmiss_count_max_absent(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["wmi_param_name_hits"] == 0
    assert s["bmiss_count_max_present"] == 0
    for r in ok:
        for tok in ("WMI_VDEV_PARAM", "VDEV_PARAM", "BMISS_COUNT_MAX", "max_bmiss"):
            assert r["wmi_param"][tok] == 0, tok


def test_values_not_claimed(report: dict) -> None:
    s = report["summary"]
    assert s["bmiss_threshold_recovered"] == 0
    assert s["csa_switch_sequence_recovered"] == 0
    joined = " ".join(report["gaps"])
    assert "arming argument was not traced" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no firmware loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
