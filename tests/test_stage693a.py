"""Stage 693A — regression tests.

Pins the seven WMI identifiers, the paired vdev sequence, the channel-specific start sender, and the
directional 40 MHz phymode pair.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "dissect_stage693a_ath10k_wmi_service_ready_and_vdev_start_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage693a_ath10k_wmi_service_ready_and_vdev_start_re.json")

REQUIRED = {"WMI_SERVICE_READY_EVENTID", "WMI_VDEV_START_REQUEST_CMDID",
            "WMI_VDEV_UP_CMDID"}
PHY = {"11ACVHT20", "11ACVHT40", "11ACVHT40MINUS", "11ACVHT40PLUS", "11ACVHT80"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "693A"
    for k in ("meta", "modules", "summary", "gaps", "ath10k_modules"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_ath10k_absent(report: dict) -> None:
    assert report["ath10k_modules"] == 0
    assert report["summary"]["ath10k_core_present"] is False


def test_two_vendor_modules(ok: list[dict], report: dict) -> None:
    assert len(ok) == 2
    assert report["summary"]["modules_ok"] == 2
    assert {r["module"] for r in ok} == {"WA:umac.ko", "XC:umac.ko"}


def test_all_three_required_identifiers(report: dict) -> None:
    s = report["summary"]
    assert s["wmi_name_count"] == 7
    assert REQUIRED <= set(s["wmi_names"])
    assert s["required_three_present"] == 1


def test_vdev_sequence_is_paired(report: dict) -> None:
    s = report["summary"]
    assert s["vdev_sequence_complete"] == 1
    assert "WMI_VDEV_START_RESP_EVENTID" in s["wmi_names"]
    assert "WMI_VDEV_STOPPED_EVENTID" in s["wmi_names"]
    assert s["restart_variant_present"] == 1


def test_host_path_has_channel_variant(report: dict) -> None:
    s = report["summary"]
    assert s["host_path_count"] == 7
    assert s["channel_start_variant"] == 1
    assert "wmi_unified_vdev_start_chan_send" in s["host_path_symbols"]
    assert "wmi_unified_vdev_start_send" in s["host_path_symbols"]


def test_phymode_is_directional(report: dict) -> None:
    s = report["summary"]
    assert s["phymode_count"] == 5
    assert set(s["phymode_strings"]) == PHY
    assert s["vht40_directional"] == 1
    assert "11ACVHT40PLUS" in s["phymode_strings"]
    assert "11ACVHT40MINUS" in s["phymode_strings"]


def test_resource_limits_not_recovered(report: dict) -> None:
    s = report["summary"]
    assert s["resource_limits_recovered"] == 0
    assert s["service_ready_payload_recovered"] == 0
    joined = " ".join(report["gaps"])
    assert "service-ready" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
