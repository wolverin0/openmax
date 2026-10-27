"""Stage 113A — regression tests for the athbox applet/PLT/ioctl audit.

These tests check the receipt, not the tool: they are the contract a future run must keep.
They assert structure and invariants that would break if the PLT resolver, the applet table
walk or the ioctl argument slice regressed.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "audit_stage113a_athbox_15applets_plt_and_ioctl_audit.py"
RECEIPT = REPO / "artifacts" / "autoresearch" / "stage113a_athbox_15applets_plt_and_ioctl_audit.json"


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"receipt missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def first(report: dict) -> dict:
    ok = [i for i in report["images"] if i.get("status") == "ok"]
    assert ok, "no image with status=ok"
    return ok[0]


def test_receipt_shape(report: dict) -> None:
    for key in ("meta", "images", "summary", "gaps"):
        assert key in report
    assert report["meta"]["stage"] == "113A"
    assert "athbox" in report["meta"]["tool"]


def test_both_images_audited(report: dict) -> None:
    ok = [i for i in report["images"] if i.get("status") == "ok"]
    assert len(ok) == 2, f"expected WA and XC, got {[i.get('image') for i in ok]}"
    hashes = {i["sha256"] for i in ok}
    # `athbox` is byte-identical in WA and XC, unlike `ubntbox` which ships two distinct
    # builds of the same size. Recording the asymmetry keeps a future run from assuming
    # that "same size" means "same bytes" for either binary.
    assert len(hashes) == 1, f"athbox expected identical across images, got {hashes}"
    assert ok[0]["sha256"] == "c1d37671cafe6c7651f03000fd7dae7755ed8717bde07df1aeffba3aaa9a99e0"


def test_fifteen_applets(first: dict) -> None:
    assert first["applet_count"] == 15
    names = {a["name"] for a in first["applets"]}
    expected = {
        "wlanconfig", "80211debug", "athdebug", "haldebug", "regdomain", "athchans",
        "radartool", "radarprescan", "pktlogconf", "pktlogdump", "athstats",
        "athstatsclr", "80211stats", "apstats", "upollstats",
    }
    assert names == expected, f"applet set drifted: {names ^ expected}"
    assert first["applet_tables"] == 1


def test_every_applet_has_a_handler(first: dict) -> None:
    for a in first["applets"]:
        fn = int(a["fn"], 16)
        ext = int(a["extent"], 16)
        assert fn > 0, a
        assert ext > fn, f"{a['name']} has non-increasing extent"
        assert ext - fn < 0x20000, f"{a['name']} extent implausibly large"


def test_plt_resolution_is_deterministic(first: dict) -> None:
    # 69 stubs on the XC build; resolution must be a substantial fraction of all jal sites
    assert first["plt_stubs"] == 69
    assert first["jal_total"] > 2000
    ratio = first["jal_resolved"] / first["jal_total"]
    assert ratio > 0.8, f"jal resolution collapsed: {ratio:.3f}"


def test_ioctl_requests_are_numeric_strings(first: dict) -> None:
    for a in first["applets"]:
        for site in a["ioctls"]:
            req = site["request"]
            if req is None:
                continue
            assert req.startswith("0x"), req
            assert int(req, 16) == site["request_dec"], site
            # a request is a 32-bit value; anything wider means the slice went wrong
            assert 0 <= site["request_dec"] <= 0xFFFFFFFF, site


def test_known_athero_ioctls_present(first: dict) -> None:
    every = set()
    for a in first["applets"]:
        every.update(a["ioctl_requests"])
    # athstats reads stats, athstatsclr clears them, radartool talks to the radar device
    assert "0x000089f0" in every, "SIOCGATHSTATS-shaped request missing from athstats"
    assert "0x000089f4" in every, "athstatsclr request missing"
    assert "0x000089f5" in every, "the request shared by radartool/80211stats/apstats is missing"


def test_no_execution_sink_in_athbox(first: dict) -> None:
    # this is a finding, not an absence of testing: none of the 15 applets reaches exec
    assert first["execution_total"] == 0
    for a in first["applets"]:
        assert a["execution"] == []
        assert a["execution_count"] == 0


def test_file_sinks_are_localised(first: dict) -> None:
    assert first["file_sink_total"] > 0
    for a in first["applets"]:
        for s in a["file_sinks"]:
            assert s["import_"] in {
                "fopen", "fopen64", "open", "open64", "openat", "creat", "unlink", "rename",
                "chmod", "fchmod", "chown", "symlink", "link", "truncate", "ftruncate",
                "stat", "lstat", "access", "opendir",
            }, s


def test_ioctl_attribution_is_per_applet(first: dict) -> None:
    with_ioctl = [a["name"] for a in first["applets"] if a["ioctl_count"]]
    assert len(with_ioctl) >= 10, f"only {len(with_ioctl)} applets attributed an ioctl"
    assert "athstats" in with_ioctl
    assert "radartool" in with_ioctl
    assert "wlanconfig" in with_ioctl


def test_unnamed_requests_are_declared(first: dict) -> None:
    # 6 of 9 distinct requests have no entry in the known table; the receipt must say so
    assert first["ioctl_requests_unnamed"], "unnamed requests must not be silently dropped"
    assert len(first["ioctl_requests"]) + len(first["ioctl_requests_unnamed"]) == 9


def test_radio_safety_declared(report: dict) -> None:
    meta = report["meta"]
    assert "zero radio contact" in meta["scope"]
    assert ".241" in meta["scope"] and ".242" in meta["scope"]


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    after = RECEIPT.read_bytes()
    assert before == after, "receipt is not deterministic across runs"
