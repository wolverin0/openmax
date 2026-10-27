"""Stage 727A — regression tests.

Pins the PHYERR handler lifecycle, the twelve-symbol spectral surface, the five radar processors with
their four silicon generations, the per-domain regulatory tables, and the predicate's true location.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "dissect_stage727a_qca988x_spectral_scan_fft_and_radar_phyerr_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage727a_qca988x_spectral_scan_fft_and_radar_phyerr_re.json")

LIFECYCLE = {"ol_ath_phyerr_attach", "ol_ath_phyerr_detach",
             "ol_ath_phyerr_enable", "ol_ath_phyerr_disable"}
PROCESSORS = {"dfs_process_phyerr", "dfs_process_phyerr_bb_tlv",
              "dfs_process_phyerr_merlin", "dfs_process_phyerr_owl",
              "dfs_process_phyerr_sowl"}
GENS = {"tlv", "merlin", "owl", "sowl"}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "727A"
    for k in ("meta", "modules", "summary", "gaps", "ath10k_modules"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_ath10k_absent(report: dict) -> None:
    assert report["ath10k_modules"] == 0
    assert report["summary"]["ath10k_core_present"] is False


def test_eight_modules(ok: list[dict], report: dict) -> None:
    assert len(ok) == 8
    assert report["summary"]["modules_ok"] == 8
    names = {r["module"].split(":")[1] for r in ok}
    assert names == {"umac.ko", "ath_dev.ko", "ath_spectral.ko", "ath_dfs.ko"}


def test_phyerr_lifecycle(report: dict) -> None:
    s = report["summary"]
    assert s["phyerr_lifecycle_count"] == 4
    assert s["phyerr_handler_named"] == 1
    assert set(s["phyerr_lifecycle"]) == LIFECYCLE


def test_five_processors_four_generations(report: dict) -> None:
    s = report["summary"]
    assert s["phyerr_processor_count"] == 5
    assert set(s["phyerr_processors"]) == PROCESSORS
    assert s["chip_generation_count"] == 4
    assert set(s["chip_generations"]) == GENS
    assert s["per_generation_dispatch"] == 1


def test_regulatory_tables_are_per_domain(report: dict) -> None:
    s = report["summary"]
    assert s["regulatory_tool_count"] == 2
    assert set(s["regulatory_radar_tools"]) == {"etsi_radartool_alow",
                                                "fcc_radartool_alow"}


def test_predicate_lives_in_ath_spectral(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["spectral_predicate_present"] == 1
    mods = s["spectral_predicate_modules"]
    assert mods
    # the predicate is carried by the spectral module, not by the WMI or device layer
    assert any("ath_spectral" in m for m in mods)


def test_wmi_commands_are_vdev_scoped(report: dict) -> None:
    s = report["summary"]
    assert s["wmi_command_count"] == 2
    assert set(s["wmi_spectral_commands"]) == {
        "WMI_VDEV_SPECTRAL_SCAN_CONFIGURE_CMDID",
        "WMI_VDEV_SPECTRAL_SCAN_ENABLE_CMDID"}


def test_symbol_counts(report: dict) -> None:
    s = report["summary"]
    assert s["spectral_symbol_count"] >= 12
    assert s["radar_symbol_count"] >= 5
    assert s["phyerr_symbol_count"] >= 4


def test_tables_not_recovered(report: dict) -> None:
    s = report["summary"]
    assert s["phyerr_code_table_recovered"] == 0
    assert s["spectral_bin_format_recovered"] == 0


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
