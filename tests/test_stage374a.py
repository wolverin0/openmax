"""Stage 374A — regression tests.

Pins the two premise corrections (XW has no `ubnt_poll_host.ko`; WA/XC carry no AirSelect
vocabulary) and the positive result that XW implements the feature as `fh_*`. The distinction
between `state_machine_located = 1` and `state_machine_recovered = 0` is asserted explicitly so a
later run cannot silently upgrade located to decoded.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "ubnt_airselect_and_freq_hop_state_machine_re.py"
RECEIPT = REPO / "artifacts" / "autoresearch" / "stage374a_ubnt_airselect_state_machine_re.json"

FH_TOKENS = ("fh_list", "fh_hops", "fh_retries", "fh_time", "fh_announce_cnt",
             "tx_sync_master", "tx_sync_mode", "chanidx")


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


@pytest.fixture(scope="module")
def by(ok: list[dict]) -> dict[str, dict]:
    return {r["module"]: r for r in ok}


@pytest.fixture(scope="module")
def xw(by: dict[str, dict]) -> dict:
    return next(v for k, v in by.items() if "ubnt_poll.ko" in k)


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "374A"
    for k in ("meta", "modules", "summary", "gaps", "help_docs", "userspace_carriers",
              "xw_expected_module"):
        assert k in report


def test_xw_has_no_poll_host_module(report: dict) -> None:
    assert report["xw_expected_module"]["exists"] is False
    assert report["xw_expected_module"]["path"].endswith(
        "2.6.32.71/ubnt_poll_host.ko")
    assert report["summary"]["xw_poll_host_present"] is False
    assert len(report["meta"]["premise_corrections"]) == 2


def test_three_modules_and_xw_is_ubnt_poll(ok: list[dict]) -> None:
    assert len(ok) == 3
    names = {r["module"].split(":")[1] for r in ok}
    assert names == {"ubnt_poll_host.ko", "ubnt_poll.ko"}
    xw_mod = [r for r in ok if r["module"].startswith("XW.")]
    assert len(xw_mod) == 1
    assert xw_mod[0]["module"].endswith("ubnt_poll.ko")
    assert xw_mod[0]["bytes"] == 529284


def test_ac_polling_modules_have_zero_airselect_vocabulary(ok: list[dict]) -> None:
    ac = [r for r in ok if "ubnt_poll_host.ko" in r["module"]]
    assert len(ac) == 2
    for r in ac:
        assert r["bytes"] == 189880
        assert r["token_count"] == 0
        assert r["tokens"] == {}
        assert r["airselect_surface"] == 0
    assert report_summary_zero(ac)


def report_summary_zero(ac: list[dict]) -> bool:
    return all(r["tokens"] == {} for r in ac)


def test_kernel_airselect_surface_is_zero(report: dict, ok: list[dict]) -> None:
    # not even the string "airselect" appears in any polling module
    assert report["summary"]["kernel_airselect_surface"] == 0
    for r in ok:
        for tok in ("airselect", "AirSelect", "AIRSELECT"):
            assert tok not in r["tokens"], (r["module"], tok)


def test_xw_carries_the_fh_family(xw: dict) -> None:
    for tok in FH_TOKENS:
        assert tok in xw["tokens"], f"missing {tok}"
        assert xw["tokens"][tok]["count"] >= 1
    assert xw["tokens"]["fh_"]["count"] == 15


def test_hop_log_sites_name_penalty_and_failure(xw: dict) -> None:
    hop = " ".join(c["context"] for c in xw["tokens"]["hopping to chanidx"]["contexts"])
    failed = " ".join(c["context"] for c in xw["tokens"]["failed hop to freq"]["contexts"])
    announce = " ".join(c["context"] for c in
                        xw["tokens"]["channel change announce"]["contexts"])
    assert "penalty" in hop
    assert "Channel not found" in failed or "flags" in failed
    assert "announce" in announce


def test_located_is_not_decoded(report: dict) -> None:
    s = report["summary"]
    assert s["state_machine_located"] == 1
    assert s["state_machine_recovered"] == 0
    joined = " ".join(report["gaps"])
    assert "located is not decoded" in joined


def test_documented_contract(report: dict) -> None:
    s = report["summary"]
    assert s["help_docs_present"] == 4
    assert s["default_hop_interval_ms"] == 3000
    assert s["announce_example_ms"] == 1000
    hop = next(d for d in report["help_docs"] if d["doc"] == "airselecthopint.html")
    assert 3000 in hop["integers"]
    acount = next(d for d in report["help_docs"] if d["doc"] == "airselectacount.html")
    assert 10000 in acount["integers"] and 10 in acount["integers"]


def test_userspace_vocabulary_is_only_a_library(report: dict) -> None:
    carriers = report["userspace_carriers"]
    assert len(carriers) == 1
    assert carriers[0]["path"] == "lib/tinysnmp/ubnt.so"
    assert carriers[0]["airselect"] == 1
    assert report["summary"]["binaries_with_vocabulary"] == 0


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
