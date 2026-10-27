"""Stage 824A — regression tests.

Pins the module-location correction (ame_dfs.ko, not ame_core.ko), the three classifier entry
points, the selectable pulse filter, the pulse percent/max report, and the LNA refutation.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "dissect_stage824a_ltu_ame_core_dfs_radar_pulse_classifier_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage824a_ltu_ame_core_dfs_radar_pulse_classifier_re.json")

CLASSIFIER = {"DFSdetect", "DFSChanActivity", "DFS_heavy_env_det"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "824A"
    for k in ("meta", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_three_modules(ok: list[dict]) -> None:
    assert len(ok) == 3
    assert {r["module"] for r in ok} == {"ame_core.ko", "ame_dev.ko", "ame_dfs.ko"}


def test_classifier_is_in_ame_dfs(report: dict) -> None:
    s = report["summary"]
    assert s["ame_dfs_present"] is True
    assert s["ame_dfs_bytes"] == 141472
    assert s["pulse_tokens_in_ame_dfs"] == 82
    assert s["pulse_tokens_in_ame_core"] == 22
    assert s["classifier_in_dfs_module"] == 1


def test_three_classifier_symbols(report: dict) -> None:
    s = report["summary"]
    assert s["classifier_symbol_count"] == 3
    assert set(s["classifier_symbols"]) == CLASSIFIER
    assert s["heavy_env_detector"] == 1
    assert s["channel_activity"] == 1


def test_lifecycle_and_ubus(report: dict) -> None:
    s = report["summary"]
    assert s["lifecycle_count"] == 7
    assert s["ubus_hook_count"] == 4


def test_pulse_filter_is_selectable(report: dict) -> None:
    s = report["summary"]
    assert s["filter_is_selectable"] == 1
    assert s["pulse_percent_max_reported"] == 1
    assert s["pulse_stats_hits"] >= 1
    assert s["hit_counter_hits"] >= 1


def test_lna_saturation_is_not_named(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["lna_token_hits"] == 0
    assert s["lna_saturation_named"] == 0
    assert s["lna_saturation_immunity_recovered"] == 0
    for r in ok:
        assert r["tokens"]["lna"] == 0
        assert r["tokens"]["LNA"] == 0


def test_tables_not_recovered(report: dict) -> None:
    assert report["summary"]["pw_pri_table_recovered"] == 0
    joined = " ".join(report["gaps"])
    assert "no pulse-width or PRI threshold table" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "nothing transmitted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
