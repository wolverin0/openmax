"""Stage 424A — regression tests.

Pins the five absences, the 36 config-file near-miss with zero subband/fpga keys, the real EAB
surface in `ame_core.ko`, and the three vocabulary traps (`subband` = OFDMA, `mask` = GEM
interrupt, `null` = null-CPE). Both recovery counters must stay 0.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "build_stage424a_ltu_arria10_fpga_subband_mask_re.py"
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage424a_ltu_arria10_fpga_subband_mask_re.json")


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def row(report: dict) -> dict:
    return report["modules"][0]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "424A"
    for k in ("meta", "absence", "modules", "prior_art", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_five_absences(report: dict) -> None:
    a = report["absence"]
    assert a["names"]["eab_driver.ko"] == 0
    assert a["names"]["libltu"] == 0
    assert a["af_ltu_dirs"] == 0
    assert a["bitstreams"] == {"*.rbf": 0, "*.sof": 0}
    s = report["summary"]
    assert s["eab_driver_present"] is False
    assert s["libltu_present"] is False
    assert s["af_ltu_tree_present"] is False
    assert s["bitstreams"] == 0


def test_af_ltu_near_miss_is_config_only(report: dict) -> None:
    a = report["absence"]
    assert a["af_ltu_config_files"] == 36
    assert a["af_ltu_paths"] == 36
    assert report["summary"]["af_ltu_config_files"] == 36
    # the configs carry no fabric vocabulary at all
    assert report["summary"]["af_ltu_subband_keys"] == 0
    assert report["summary"]["af_ltu_fpga_keys"] == 0


def test_eab_surface_is_real_in_ame_core(row: dict, report: dict) -> None:
    assert row["status"] == "ok"
    assert row["module"] == "ame_core.ko"
    assert row["bytes"] == 3282052
    assert report["summary"]["eab_tokens"] == 359
    assert report["summary"]["eab_upper_tokens"] == 208
    assert report["summary"]["eab_symbol_count"] == 23
    sample = report["summary"]["eab_symbols_sample"]
    assert "ame_modem_bbp_eab_testmode_handler" in sample
    assert any(n.startswith("ame_core_eab_") for n in sample)


def test_fabric_words_are_absent(row: dict, report: dict) -> None:
    for tok in ("tone", "notch", "punctur", "arria", "fpga"):
        assert row["tokens"][tok] == 0, tok
    assert report["summary"]["tone_tokens"] == 0
    assert report["summary"]["arria_tokens"] == 0
    assert report["summary"]["fpga_tokens"] == 0
    assert report["summary"]["puncture_tokens"] == 0


def test_subband_is_ofdma(row: dict, report: dict) -> None:
    assert report["summary"]["subband_tokens"] == 17
    assert report["summary"]["ofdma_subband_type"] == 6
    ctx = " ".join(row["contexts"]["subband"])
    assert "ofdma_subband_type" in ctx
    assert "ofdma_en" in ctx
    assert "ofdma_start" in ctx
    assert "ofdma_len" in ctx


def test_mask_is_gem_interrupt(row: dict, report: dict) -> None:
    assert report["summary"]["mask_tokens"] == 2
    ctx = " ".join(row["contexts"]["mask"])
    assert "GEM queue intr mask" in ctx
    assert "punctur" not in ctx


def test_null_is_cpe_scheduling(row: dict, report: dict) -> None:
    assert report["summary"]["null_tokens"] == 11
    ctx = " ".join(row["contexts"]["null"])
    assert "last_cpe_null" in ctx
    assert "null cpe" in ctx


def test_prior_art_is_cross_referenced(report: dict) -> None:
    prior = report["prior_art"]
    assert prior is not None
    assert prior["mailbox_symbol_count"] == 195
    assert report["summary"]["prior_mailbox_symbols"] == 195
    assert "Arria" in (prior["fabric"] or "")


def test_nothing_recovered(report: dict) -> None:
    s = report["summary"]
    assert s["subband_mask_registers_recovered"] == 0
    assert s["tone_null_ioctl_recovered"] == 0
    joined = " ".join(report["gaps"])
    assert "eab_driver.ko does not exist" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
