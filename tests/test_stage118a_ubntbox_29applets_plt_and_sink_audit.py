"""Stage 118A — regression tests for the ubntbox applet/PLT/sink audit.

The receipt is the contract. These tests pin the invariants that would break if the PLT
resolver, the applet table walk or the sink classifier regressed, and they also pin the
version and applet-name corrections so a future run cannot quietly re-adopt the wrong image
or the wrong binary list.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "audit_stage118a_ubntbox_29applets_plt_and_sink_audit.py"
RECEIPT = REPO / "artifacts" / "autoresearch" / "stage118a_ubntbox_29applets_plt_and_sink_audit.json"

EXPECTED_APPLETS = {
    "amstainfo", "bgnd", "certgen", "cfgmtd", "discover", "ethcfg", "factorytest",
    "fcc-lock", "fwupdate.real", "hist-stats.cgi", "infctld", "label", "mca-status",
    "scand", "signal.cgi", "snmp", "speedtd", "sqfsck", "status.cgi", "sysled", "uav",
    "ubnt-caldata", "ubnt-gps-reader", "ubntconf", "ulogger", "uservice", "ust-ctl",
    "ustatsd", "wstalist",
}


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
    assert report["meta"]["stage"] == "118A"


def test_version_correction_recorded(report: dict) -> None:
    # the task asked for v8.7.11; that tree does not exist and the receipt must say so
    notes = " ".join(report["meta"]["version_correction"])
    assert "v8.7.11" in notes
    assert "do not exist" in notes
    assert "v8.7.25" in notes


def test_applet_name_corrections_recorded(report: dict) -> None:
    notes = " ".join(report["meta"]["applet_name_corrections"])
    for name in ("mcad", "udapi-bridge", "tinysnmpd"):
        assert name in notes, f"{name} correction missing from the receipt"


def test_both_images_present_and_distinct(report: dict) -> None:
    ok = [i for i in report["images"] if i.get("status") == "ok"]
    assert len(ok) == 2
    # unlike athbox, ubntbox ships two distinct builds of the same size
    assert len({i["sha256"] for i in ok}) == 2
    assert report["summary"]["images_identical"] is False


def test_twenty_nine_applets(first: dict) -> None:
    assert first["applet_count"] == 29
    assert {a["name"] for a in first["applets"]} == EXPECTED_APPLETS
    assert first["applet_tables"] == 1


def test_every_applet_has_a_handler(first: dict) -> None:
    for a in first["applets"]:
        fn = int(a["fn"], 16)
        ext = int(a["extent"], 16)
        assert fn > 0
        assert ext > fn
        assert ext - fn < 0x40000, f"{a['name']} extent implausible"


def test_plt_resolution(first: dict) -> None:
    assert first["plt_stubs"] == 320
    assert first["jal_total"] > 9000
    ratio = first["jal_resolved"] / first["jal_total"]
    assert ratio > 0.5, f"jal resolution collapsed: {ratio:.3f}"


def test_process_sink_is_scand_only(first: dict) -> None:
    # the single execution sink in ubntbox; already mapped in W4D as scand -> popen
    assert first["totals"]["process"] == 1
    assert first["applets_with_process"] == ["scand"]
    scand = next(a for a in first["applets"] if a["name"] == "scand")
    assert scand["process_count"] == 1
    assert scand["process"][0]["import_"] == "popen"


def test_shared_memory_sink_is_fwupdate(first: dict) -> None:
    assert first["totals"]["ipc_shared_memory"] == 1
    assert first["applets_with_ipc"] == ["fwupdate.real"]
    fw = next(a for a in first["applets"] if a["name"] == "fwupdate.real")
    assert fw["ipc_count"] == 1
    assert fw["ipc"][0]["import_"] in {
        "shmget", "shmat", "shmdt", "shmctl", "msgget", "msgsnd", "msgrcv", "msgctl",
        "semget", "semop", "semctl", "mmap", "munmap", "mq_open", "mq_send",
        "mq_receive", "pipe", "mkfifo",
    }


def test_file_sinks_localised(first: dict) -> None:
    assert first["totals"]["file"] == 19
    assert len(first["applets_with_file"]) == 8
    for a in first["applets"]:
        for s in a["file_sinks"]:
            assert s["import_"] in {
                "fopen", "fopen64", "open", "open64", "openat", "creat", "unlink", "rename",
                "chmod", "fchmod", "chown", "symlink", "link", "truncate", "ftruncate",
                "stat", "lstat", "access", "opendir", "readdir",
            }, s


def test_every_sink_has_a_hex_site(first: dict) -> None:
    for a in first["applets"]:
        for bucket in ("process", "file_sinks", "ipc", "network"):
            for s in a[bucket]:
                assert s["site"].startswith("0x")
                assert 0 <= int(s["site"], 16) <= 0xFFFFFFFF
                assert s["level"] in (0, 1, 2)


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
