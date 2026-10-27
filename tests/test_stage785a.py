"""Stage 785A — regression tests.

Pins the board.bin/otp.bin absence, the mtd5 caldata presence and sparsity, the 5 GHz block at
0x5000 behind a six-byte prefix, the board identity string, and the HAL board-value path.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "dissect_stage785a_qca988x_otp_and_board_caldata_eeprom_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage785a_qca988x_otp_and_board_caldata_eeprom_re.json")

HAL_PATH = {"ar9300_eeprom_restore_internal", "ar9300_eeprom_set_board_values",
            "ar9300_set_target_power_from_eeprom", "ar9300_is_nf_cal_done",
            "ar9300_eeprom_get_spur_chans_ptr"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "785A"
    for k in ("meta", "named_files", "mtd5_dumps", "caldata", "modules", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_ath10k_blobs_absent(report: dict) -> None:
    s = report["summary"]
    assert report["named_files"]["board.bin"] == 0
    assert report["named_files"]["otp.bin"] == 0
    assert s["board_bin_present"] is False
    assert s["otp_bin_present"] is False
    assert s["ath10k_blobs_absent"] == 1


def test_caldata_is_present(report: dict) -> None:
    s = report["summary"]
    assert s["mtd5_dumps_found"] == 41
    assert s["mtd5_size"] == 65536
    assert s["five_ghz_offset"] == "0x5000"
    assert s["caldata_block_located"] == 1


def test_board_identity_string(report: dict) -> None:
    s = report["summary"]
    assert s["identity_string_present"] == 1
    assert s["board_identity_ascii"] == "CUS223-720-S0849"


def test_block_headers(report: dict) -> None:
    c = report["caldata"]
    # 2.4 GHz region starts with the a1 variant of the magic
    assert c["header_0x0000"].startswith("784558a1")
    # 5 GHz region has a six-byte prefix, then the a0 variant
    assert c["header_0x5000"].startswith("44082d860203")
    assert "784558a0" in c["header_0x5000"]


def test_dump_is_sparse_and_varied(report: dict) -> None:
    c = report["caldata"]
    assert c["page_count"] == 16
    assert c["pages_with_data"] == 4
    assert c["identical_dumps"] == 10
    # so at least 11 distinct calibrations exist in the corpus
    assert c["identical_dumps"] < report["summary"]["mtd5_dumps_found"]


def test_hal_board_path(report: dict) -> None:
    s = report["summary"]
    assert s["hal_board_path_count"] == 5
    assert set(s["hal_board_path"]) == HAL_PATH
    assert s["target_power_from_eeprom"] == 1
    assert s["nf_cal_done"] == 1
    assert s["eeprom_token_hits"] >= 39


def test_ctl_table_is_not_eeprom(report: dict) -> None:
    s = report["summary"]
    assert s["ctl_table_token_hits"] == 4  # 2 per AC image
    assert s["ctl_table_is_eeprom_symbol"] == 0


def test_values_not_decoded(report: dict) -> None:
    s = report["summary"]
    assert s["eeprom_values_recovered"] == 0
    assert s["subband_table_recovered"] == 0


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no flash written" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
