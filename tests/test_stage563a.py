"""Stage 563A — regression tests.

Pins the seven-stage PAPRD pipeline, the thermal and GreenTX interactions, the EEPROM target power,
and the naming refutation: olpc/clpc do not exist, the loop distinction is tpc and ctl.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "build_stage563a_qca988x_paprd_and_olpc_tx_power_control_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage563a_qca988x_paprd_and_olpc_tx_power_control_re.json")

PIPELINE = ["create_curve", "init_table", "populate_paprd", "swizzle",
            "setup_gain_table", "set_paprd_tx_desc", "is_done"]
LOOP = {"enable_tpc", "get_tpc_tables", "get_rate_tpc", "get_ctl_by_country",
        "get_ctl_chan_nf", "update_loc_ctl_reg"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "563A"
    for k in ("meta", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_seven_modules(ok: list[dict], report: dict) -> None:
    assert len(ok) == 7
    assert report["summary"]["modules_ok"] == 7
    names = {r["module"].split(":")[1] for r in ok}
    assert names == {"ath_hal.ko", "ath_dev.ko", "umac.ko"}


def test_paprd_pipeline_is_complete(report: dict) -> None:
    s = report["summary"]
    assert s["paprd_pipeline_complete_of_7"] == 7
    assert s["paprd_pipeline_stages"] == PIPELINE
    assert s["paprd_pipeline_named"] == 1
    assert s["paprd_has_transmit_path"] == 1


def test_paprd_symbols_span_both_layers(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["paprd_symbol_count"] == 29
    joined = " ".join(s["paprd_symbols"])
    assert "ar9300_paprd_create_curve" in joined
    assert "ath_apply_paprd_table" in joined
    assert "ath_tx_paprd_draintxq" in joined


def test_thermal_and_greentx(report: dict) -> None:
    s = report["summary"]
    assert s["thermal_link"] == 1
    assert s["green_tx_skips_paprd"] == 1
    assert s["target_power_from_eeprom"] == 1


def test_loop_vocabulary_is_tpc_and_ctl(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["tpc_symbol_count"] == 15
    assert s["ctl_symbol_count"] == 22
    assert s["loop_control_count"] == 6
    assert set(s["loop_controls_present"]) == LOOP
    assert s["ctl_by_country"] == 1
    assert s["txctl_cap"] == 1


def test_olpc_and_clpc_do_not_exist(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["assumed_loop_token_hits"] == 0
    assert s["olpc_clpc_literals_absent"] == 1
    for r in ok:
        for tok in ("olpc", "clpc", "open_loop", "closed_loop"):
            assert r["assumed"][tok] == 0, (r["module"], tok)
        for tok in ("olpc", "OLPC", "clpc", "CLPC"):
            assert r["tokens"][tok] == 0, (r["module"], tok)


def test_values_not_recovered(report: dict) -> None:
    s = report["summary"]
    assert s["paprd_table_values_recovered"] == 0
    assert s["tpc_tables_recovered"] == 0
    assert s["thermal_curve_recovered"] == 0
    joined = " ".join(report["gaps"])
    assert "olpc and clpc do not exist as tokens" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "nothing transmitted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
