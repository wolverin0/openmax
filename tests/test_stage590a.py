"""Stage 590A — regression tests.

Pins the LBT API, the four config parameters (including the listen window and the pause-txframe
hook), the one-show/three-store sysfs shape, the interference detectors, the seven auto-channel
keys, and the `mitigat` refutation.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "build_stage590a_ltu_ame_core_interference_mitigation_and_auto_channel_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage590a_ltu_ame_core_interference_mitigation_and_auto_channel_re.json")

CFG = {"lbt_cfg_listen_window", "lbt_cfg_pause_txframe",
       "lbt_cfg_threshold", "lbt_cfg_reset"}
AUTO = {"freq_list_enabled", "auto_freq_list", "auto_freq_mode", "smart_scan",
        "prefer_work_txfreq", "prefer_work_rxfreq", "reg_obey"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "590A"
    for k in ("meta", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_two_modules(ok: list[dict]) -> None:
    assert len(ok) == 2
    names = {r["module"] for r in ok}
    assert names == {"ame_core.ko", "ame_dev.ko"}


def test_lbt_api(report: dict) -> None:
    s = report["summary"]
    assert s["lbt_symbol_count"] == 24
    assert s["lbt_api_count"] == 6
    assert "lbt_init" in s["lbt_api_controls"]
    assert "is_lbt_required" in s["lbt_api_controls"]
    assert "lbt_set_cfg" in s["lbt_api_controls"]


def test_lbt_config_parameters(report: dict) -> None:
    s = report["summary"]
    assert s["lbt_cfg_count"] == 4
    assert set(s["lbt_cfg_params"]) == CFG
    assert s["lbt_has_listen_window"] == 1
    assert s["lbt_has_pause_txframe"] == 1


def test_lbt_detection_counters(report: dict) -> None:
    s = report["summary"]
    assert s["lbt_counter_count"] == 2
    assert set(s["lbt_counters"]) == {"lbt_incr_detect_cnt", "lbt_get_detect_cnt"}
    assert s["lbt_has_detect_counter"] == 1


def test_sysfs_is_three_pairs_plus_split_store(report: dict) -> None:
    s = report["summary"]
    assert s["sysfs_pair_count"] == 3
    assert set(s["sysfs_lbt_pairs"]) == {"lbt_detects", "lbt_enable", "lbt_reset"}
    assert s["lbt_cfg_has_split_store"] == 1
    assert set(s["lbt_cfg_store_variants"]) == {"window", "threshold", "pauselen"}


def test_interference_detection(report: dict) -> None:
    s = report["summary"]
    assert s["interference_detection_named"] == 1
    assert len(s["interference_controls"]) == 4
    assert set(s["interference_controls"]) == {
        "interference_det_init", "interference_det_deinit",
        "get_rf_interference_avg", "get_rf_interference_curr"}


def test_auto_channel_keys(report: dict) -> None:
    s = report["summary"]
    assert s["auto_channel_key_count"] == 7
    assert set(s["auto_channel_keys"]) == AUTO
    assert s["auto_channel_hooks_named"] == 1


def test_mitigation_word_absent(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["mitigation_word_hits"] == 0
    assert s["mitigation_word_absent"] == 1
    for r in ok:
        assert r["tokens"]["mitigat"] == 0


def test_values_not_recovered(report: dict) -> None:
    s = report["summary"]
    assert s["lbt_threshold_recovered"] == 0
    assert s["auto_channel_policy_recovered"] == 0
    assert s["spectral_scan_hook_recovered"] == 0


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "nothing transmitted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
