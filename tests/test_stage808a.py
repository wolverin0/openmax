"""Stage 808A — regression tests.

Pins the AirView userspace finding, the four readable daemons, the layer split between DMA and PCIe,
and the single `coexist` reference.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "dissect_stage808a_xc_qca9558_pcie_dma_and_airview_coexistence_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage808a_xc_qca9558_pcie_dma_and_airview_coexistence_re.json")


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "808A"
    for k in ("meta", "modules", "daemons", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_three_xc_modules(ok: list[dict]) -> None:
    assert len(ok) == 3
    assert {r["module"] for r in ok} == {"XC:ath_dev.ko", "XC:umac.ko", "XC:ath_hal.ko"}


def test_airview_is_not_in_the_kernel(report: dict, ok: list[dict]) -> None:
    s = report["summary"]
    assert s["kernel_airview_hits"] == 0
    assert s["airview_in_kernel"] == 0
    for r in ok:
        assert r["tokens"]["airview"] == 0
        assert r["tokens"]["AirView"] == 0


def test_airview_is_a_userspace_binary(report: dict) -> None:
    s = report["summary"]
    assert s["airview_is_userspace"] == 1
    assert s["airview_bytes"] == 8647
    assert s["airview_self_name_hits"] == 60


def test_daemons_are_all_readable(report: dict) -> None:
    s = report["summary"]
    assert s["daemons_present"] == 4
    assert s["daemons_readable"] == 4
    names = {d["name"] for d in report["daemons"]}
    assert names == {"airview", "ubntspecd", "dfsprescan", "provmode"}
    for d in report["daemons"]:
        assert d["bytes"] > 0
    assert s["ubntspecd_bytes"] == 47192


def test_layer_split_dma_vs_pci(report: dict) -> None:
    s = report["summary"]
    assert s["dev_dma_tokens"] == 43
    assert s["umac_pci_tokens"] == 62
    assert s["dma_in_device_layer"] == 1
    assert s["pci_in_umac"] == 1


def test_coexist_is_thin(report: dict) -> None:
    s = report["summary"]
    assert s["coexist_token_hits"] == 1
    assert s["coexist_is_thin"] == 1
    assert s["airview_kernel_arbitration_recovered"] == 0


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
