"""Stage 127A — regression tests for the ubntconf provenance and ubntbox diff audit.

The receipt is the contract. These tests pin both the verdict (paths are static, not
user-controlled) and the asymmetry that the task statement had inverted (ubntbox differs,
athbox does not), so neither can silently regress.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "audit_stage127a_ubntconf_and_wa_xc_ubntbox_diff.py"
RECEIPT = REPO / "artifacts" / "autoresearch" / "stage127a_ubntconf_and_wa_xc_ubntbox_diff.json"

EXPECTED_NAMES = ["presysinit", "postsysinit", "prestart", "poststart", "prestop", "poststop"]


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"receipt missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ubntconf(report: dict) -> dict:
    return report["ubntconf"]


def test_receipt_shape(report: dict) -> None:
    for key in ("meta", "ubntconf", "binary_diff", "summary", "gaps"):
        assert key in report
    assert report["meta"]["stage"] == "127A"


def test_version_correction_recorded(report: dict) -> None:
    notes = " ".join(report["meta"]["version_correction"])
    assert "v8.7.11" in notes and "do not exist" in notes and "v8.7.25" in notes


def test_premise_correction_recorded(report: dict) -> None:
    # the task said WA == XC for ubntbox; the receipt must state the opposite
    note = report["meta"]["premise_correction"]
    assert "7.18%" in note
    assert "athbox" in note


def test_ubntconf_geometry(ubntconf: dict) -> None:
    assert ubntconf["fn"] == "0x0040cf24"
    assert ubntconf["size"] == 584
    assert ubntconf["path_sink_count"] == 3, "ubntconf has 3 direct path sinks, not 5"


def test_ubntconf_sinks_are_the_expected_imports(ubntconf: dict) -> None:
    imports = [s["import_"] for s in ubntconf["path_sinks"]]
    assert imports.count("stat") == 2
    assert imports.count("unlink") == 1
    for s in ubntconf["path_sinks"]:
        assert s["site"].startswith("0x")


def test_ubntconf_templates_include_the_path_literals(ubntconf: dict) -> None:
    values = set(ubntconf["templates"].values())
    assert "/etc/%s" in values
    assert "/etc/persistent/rc.%s" in values
    assert "/usr/lib/cs" in values
    assert "presysinit" in values
    # the delay-slot window also picks up neighbouring literals; the path ones must be there
    assert len(values) >= 5


def test_name_array_is_static_hooks(ubntconf: dict) -> None:
    arr = ubntconf["name_array"]
    assert arr["count"] == 6
    assert arr["entries"] == EXPECTED_NAMES
    assert arr["start"] == "0x004b6ce0"


def test_no_system_cfg_on_the_ubntconf_path(ubntconf: dict) -> None:
    # the binary does reference /tmp/system.cfg elsewhere (24 occurrences), but not here
    assert ubntconf["syscfg_strings_in_ubntconf"] == 0
    assert ubntconf["syscfg_strings_in_binary"] > 0


def test_verdict_is_refuted(ubntconf: dict) -> None:
    v = ubntconf["verdict"]
    assert v["user_controlled"] == "NO"
    assert "REFUTED" in v["label"]
    assert "presysinit" in v["basis"]


def test_ubntbox_diff_is_not_identical(report: dict) -> None:
    d = report["binary_diff"]["ubntbox"]
    assert d["identical"] is False
    assert d["differing_bytes"] == 64575
    assert d["differing_pct"] == 7.1815
    assert d["cluster_count"] == 411
    assert d["wa_sha256"] != d["xc_sha256"]
    assert d["wa_bytes"] == d["xc_bytes"] == 899180


def test_athbox_is_identical(report: dict) -> None:
    d = report["binary_diff"]["athbox"]
    assert d["identical"] is True
    assert d["differing_bytes"] == 0
    assert d["wa_sha256"] == d["xc_sha256"]


def test_diff_clusters_are_localised(report: dict) -> None:
    d = report["binary_diff"]["ubntbox"]
    assert d["clusters"], "clusters must be reported, not just a count"
    for c in d["clusters"]:
        assert c["offset"].startswith("0x")
        assert c["length"] > 0
        assert c["end_offset"].startswith("0x")


def test_summary_matches_details(report: dict) -> None:
    s = report["summary"]
    assert s["ubntconf_path_sinks"] == report["ubntconf"]["path_sink_count"]
    assert s["ubntconf_reads_system_cfg"] == 0
    assert s["ubntbox_identical"] is False
    assert s["athbox_identical"] is True


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
