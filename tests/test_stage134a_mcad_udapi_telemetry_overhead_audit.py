"""Stage 134A — regression tests for the mcad / udapi-bridge telemetry audit.

The central finding these tests protect is a negative one: `mcad` does **not** collect radio
telemetry through `SIOCGATHSTATS`/`SIOCG80211STATS` and reads no `/proc` or `/sys` path. It is
a UDP/libevent discovery daemon with a single ioctl. If a future run starts reporting
telemetry paths for `mcad`, that is a regression in the tool, not a discovery.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "audit_stage134a_mcad_udapi_telemetry_overhead_audit.py"
RECEIPT = REPO / "artifacts" / "autoresearch" / "stage134a_mcad_udapi_telemetry_overhead_audit.json"


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"receipt missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def first(report: dict) -> dict:
    bins = {b["path"]: b for b in report["images"][0]["binaries"] if b.get("status") == "ok"}
    assert set(bins) == {"mcad", "udapi-bridge"}, sorted(bins)
    return bins


def test_receipt_shape(report: dict) -> None:
    for key in ("meta", "images", "summary", "gaps"):
        assert key in report
    assert report["meta"]["stage"] == "134A"


def test_premise_corrections_recorded(report: dict) -> None:
    notes = " ".join(report["meta"]["premise_corrections"])
    assert "not ubntbox applets" in notes
    assert "v8.7.11" in notes and "do not exist" in notes
    assert "REFUTED" in notes, "the telemetry premise correction must be explicit"


def test_four_binaries_audited(report: dict) -> None:
    ok = [b for i in report["images"] for b in i["binaries"] if b.get("status") == "ok"]
    assert len(ok) == 4, "mcad and udapi-bridge in both WA and XC"


def test_mcad_is_identical_across_images(report: dict) -> None:
    mcad = [b for i in report["images"] for b in i["binaries"] if b["path"] == "mcad"]
    assert len({b["sha256"] for b in mcad}) == 1
    assert report["summary"]["binaries_identical"] is True


def test_mcad_has_no_telemetry_ioctl_surface(first: dict) -> None:
    m = first["mcad"]
    # one lone ioctl, and it is not one of the Atheros stats requests
    assert m["ioctl_sites"] == 1
    for req in m["ioctl_requests"]:
        assert req not in ("0x000089f0", "0x00008b30"), \
            "mcad must not be reported as reading SIOCGATHSTATS/SIOCG80211STATS"


def test_mcad_reads_no_proc_or_sys(first: dict) -> None:
    m = first["mcad"]
    assert m["proc_sys_count"] == 0
    assert m["proc_sys_paths"] == []


def test_mcad_is_event_driven(first: dict) -> None:
    m = first["mcad"]
    cm = m["cost_model"]
    assert cm["model"] == "NOT_APPLICABLE"
    assert "event-driven" in cm["reason"]
    assert m["network_sites"] > 0
    # the UDP discovery stack must be visible
    for imp in ("socket", "bind", "recvfrom", "sendto"):
        assert imp in m["network_imports"], f"{imp} missing from mcad network imports"


def test_udapi_bridge_does_have_the_telemetry_surface(first: dict) -> None:
    u = first["udapi-bridge"]
    assert u["ioctl_sites"] >= 10
    assert u["proc_sys_count"] >= 5
    assert u["timer_sites"] >= 1
    assert u["cost_model"]["model"] == "INFERRED"
    assert u["cost_model"]["ops_per_second"] is not None


def test_udapi_bridge_proc_paths_are_real(first: dict) -> None:
    paths = first["udapi-bridge"]["proc_sys_paths"]
    for p in paths:
        assert p.startswith("/proc/") or p.startswith("/sys/"), p


def test_udapi_interval_is_flagged_as_inferred(first: dict) -> None:
    cm = first["udapi-bridge"]["cost_model"]
    assert "caveat" in cm
    assert "does not estimate CPU milliseconds" in cm["caveat"]


def test_cost_model_never_claims_measured_cpu(first: dict) -> None:
    for name in ("mcad", "udapi-bridge"):
        cm = first[name]["cost_model"]
        assert "cpu_ms" not in cm and "cpu_milliseconds" not in cm


def test_radio_safety_declared(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "zero radio contact" in scope
    assert ".241" in scope and ".242" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    after = RECEIPT.read_bytes()
    assert before == after, "receipt is not deterministic across runs"
