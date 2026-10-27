"""Stage 396A — regression tests.

Pins the two premise corrections (no XM rootfs, register names are macros) and the two positive
results: the chainmask proc/accessor pair in `ath_dev.ko`, and `ubnt_ewma_delegate_on` as a
`module_param` of `ath_rate_atheros.ko`. The MRC path must stay unrecovered.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "xw_ar9344_ath9k_ani_and_chainmask_mrc_re.py"
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage396a_xw_ar9344_ani_chainmask_mrc_re.json")


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


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "396A"
    for k in ("meta", "modules", "summary", "gaps", "xm_roots_found"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_no_xm_rootfs(report: dict) -> None:
    assert report["xm_roots_found"] == []
    assert report["summary"]["xm_root_present"] is False
    assert "there is no XM rootfs" in " ".join(report["meta"]["premise_corrections"])


def test_eight_modules_two_versions(report: dict, ok: list[dict]) -> None:
    assert len(ok) == 8
    assert report["summary"]["versions"] == 2
    assert len({r["module"].split(":")[0] for r in ok}) == 2
    names = {r["module"].split(":")[1] for r in ok}
    assert names == {"ath_hal.ko", "ath_dev.ko", "ath_rate_atheros.ko", "ubnt_ewma_ht.ko"}


def test_register_names_absent(report: dict, ok: list[dict]) -> None:
    assert report["summary"]["register_name_hits"] == 0
    assert report["summary"]["register_names_recovered"] == 0
    for r in ok:
        for tok in ("AR_PHY_MULTICHAIN_GAIN_CTL", "MULTICHAIN_GAIN",
                    "AR_PHY_TIMING2", "TIMING2"):
            assert r["register_names"][tok] == 0, (r["module"], tok)


def test_chainmask_vocabulary(by: dict[str, dict], report: dict) -> None:
    assert report["summary"]["chainmask_hits"] == 64
    assert report["summary"]["modules_with_txchainmask"] == 2
    assert report["summary"]["modules_with_rxchainmask"] == 2
    for ver in ("XW.v6.1.4", "XW.v6.3.6"):
        dev = by[f"{ver}:ath_dev.ko"]
        assert dev["chainmask"]["txchainmask"] == 4
        assert dev["chainmask"]["rxchainmask"] == 3
        assert dev["chainmask"]["chainmask"] == 23


def test_chainmask_has_getters(by: dict[str, dict]) -> None:
    ctx = " ".join(by["XW.v6.3.6:ath_dev.ko"]["chainmask_contexts"]["txchainmask"])
    assert "get_txchainmask" in ctx
    ctx2 = " ".join(by["XW.v6.3.6:ath_dev.ko"]["chainmask_contexts"]["rxchainmask"])
    assert "get_rxchainmask" in ctx2


def test_ewma_delegate_is_a_module_param(by: dict[str, dict], report: dict) -> None:
    assert report["summary"]["exact_ubnt_ewma_delegate_on"] == 1
    for ver in ("XW.v6.1.4", "XW.v6.3.6"):
        rate = by[f"{ver}:ath_rate_atheros.ko"]
        assert rate["ewma"]["ewma_delegate"] == 10
        assert rate["ewma"]["delegate_on"] == 9
        assert "__param_ubnt_ewma_delegate_on" in rate["ewma_symbols"]
        assert "__param_str_ubnt_ewma_delegate_on" in rate["ewma_symbols"]
        assert "ubnt_ewma_delegate_on" in rate["ewma_symbols"]


def test_ewma_module_exports_the_logic(by: dict[str, dict], report: dict) -> None:
    for ver in ("XW.v6.1.4", "XW.v6.3.6"):
        assert len(by[f"{ver}:ubnt_ewma_ht.ko"]["ewma_symbols"]) == 24
    assert report["summary"]["modules_with_ewma_symbols"] == 4
    assert report["summary"]["ewma_hits"] > 0


def test_ani_surface(report: dict) -> None:
    syms = report["summary"]["ani_symbols"]
    assert "ar9300_is_ani_noise_spur" in syms
    assert "ath_hal_log_ani_callback_register" in syms


def test_mrc_path_not_recovered(report: dict) -> None:
    assert report["summary"]["mrc_path_recovered"] == 0
    joined = " ".join(report["gaps"])
    assert "no XM rootfs exists" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
