"""Stage 589A — regression tests.

Pins the location correction (UMAC only), the per-rate SGI mask, the phymode accessor family, and
the two runtime log lines that make the descriptor observable.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "build_stage589a_qca988x_wmi_peer_rate_retry_and_sgi_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage589a_qca988x_wmi_peer_rate_retry_and_sgi_re.json")

WMI = {"WMI_PEER_ASSOC_CMDID", "WMI_PEER_RATE_RETRY_SCHED_CMDID"}
SGI_MACHINERY = {"_RATE_SetSGIMasks", "_RATE_GetSGIFlag", "g_default_sgi_per_thresh"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "589A"
    for k in ("meta", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_six_modules(ok: list[dict], report: dict) -> None:
    assert len(ok) == 6
    assert report["summary"]["modules_ok"] == 6
    names = {r["module"].split(":")[1] for r in ok}
    assert names == {"umac.ko", "ath_dev.ko", "ubnt_poll_host.ko"}


def test_vocabulary_is_umac_only(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["vocab_is_umac_only"] == 1
    assert s["non_umac_modules"] == 4
    assert s["non_umac_modules_with_zero_tokens"] == 4
    totals = s["token_totals"]
    assert totals["WA:umac.ko"] == 95
    assert totals["XC:umac.ko"] == 95
    for key, val in totals.items():
        if "umac" not in key:
            assert val == 0, key


def test_both_wmi_names_present(report: dict) -> None:
    s = report["summary"]
    assert s["wmi_command_count"] == 2
    assert set(s["wmi_command_names"]) == WMI


def test_sgi_is_a_per_rate_mask(report: dict) -> None:
    s = report["summary"]
    assert s["sgi_machinery_count"] == 3
    assert set(s["sgi_machinery"]) == SGI_MACHINERY
    assert s["sgi_is_per_rate_mask"] == 1
    assert s["sgi_default_present"] == 1


def test_phymode_family(report: dict) -> None:
    s = report["summary"]
    assert s["phymode_symbol_count"] == 10
    joined = " ".join(s["phymode_symbols"])
    assert "phymode" in joined
    assert s["peer_ratectxt_present"] == 1


def test_runtime_log_lines(report: dict) -> None:
    s = report["summary"]
    assert s["rate_descriptor_line_present"] == 1
    assert s["sgi_count_line_present"] == 1


def test_descriptor_values_not_recovered(report: dict) -> None:
    s = report["summary"]
    assert s["sgi_mask_values_recovered"] == 0
    assert s["retry_descriptor_values_recovered"] == 0
    joined = " ".join(report["gaps"])
    assert "series_bw is absent" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
