"""Stage 373A — regression tests.

Pins the container parse (which is only accepted because it tiles), the SGMT fingerprint, the
absence of WHAL names inside the firmware, and the exact per-module token distribution that makes
the AC/XW asymmetry a fact rather than a reading.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "qca988x_whal_cca_agc_register_table_re.py"
RECEIPT = REPO / "artifacts" / "autoresearch" / "stage373a_qca988x_whal_cca_agc_re.json"


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
    assert report["meta"]["stage"] == "373A"
    for k in ("meta", "container", "modules", "summary", "gaps"):
        assert k in report


def test_container_tiles(report: dict) -> None:
    c = report["container"]
    assert c["parsed"] is True
    assert c["tiled"] is True
    assert c["magic"] == "QCA-ATH10K"
    assert c["version_len"] == 28
    assert c["version"] == "10.1-ct-8x-__fW-022-ecad3248"
    assert c["file_len"] == 204796
    assert c["tail_pad"] == 3
    assert c["end"] == "0x031ff9"


def test_tlv_chain_exact(report: dict) -> None:
    ies = report["container"]["ies"]
    assert [ie["id"] for ie in ies] == [1, 2, 30, 4, 3]
    assert [ie["len"] for ie in ies] == [4, 8, 16, 7140, 197537]
    assert report["summary"]["tlvs"] == 5


def test_two_sgmt_segments(report: dict) -> None:
    s = report["summary"]
    assert s["sgmt_segments"] == 2
    assert s["sgmt_bytes"] == 204677
    assert [ie["tag"] for ie in report["container"]["sgmt"]] == ["SGMT", "SGMT"]
    # 99.9 % of the container lives in these two payloads
    assert s["sgmt_bytes"] / report["container"]["file_len"] > 0.999


def test_sgmt_prefix_is_shared(report: dict) -> None:
    heads = [ie["head"] for ie in report["container"]["sgmt"]]
    # first 12 bytes identical: "SGMT" + 01 00 00 00 + 00 00 98 00
    assert len({h[:24] for h in heads}) == 1
    assert all(h.startswith("53474d540100000000009800") for h in heads)
    assert report["summary"]["sgmt_u32_at_12"] == [148, 5484]


def test_firmware_has_no_whal_names(report: dict) -> None:
    sweep = report["container"]["token_sweep"]
    assert sweep, "container token sweep missing"
    assert all(v == 0 for v in sweep.values()), sweep
    assert report["summary"]["firmware_whal_tokens"] == 0
    assert report["summary"]["analog_register_table_recovered"] == 0
    assert report["summary"]["name_to_register_map"] == 0


def test_module_token_distribution(report: dict, by: dict[str, dict]) -> None:
    s = report["summary"]
    assert s["modules_ok"] == 5
    assert s["cca_thresh_modules"] == 2      # WA + XC ath_hal only
    assert s["nf_cal_modules"] == 2
    assert s["firstep_modules"] == 2
    assert s["cycpwr_modules"] == 2
    assert "cca_thresh" in by["WA:ath_hal.ko"]["tokens"]
    assert "cca_thresh" in by["XC:ath_hal.ko"]["tokens"]


def test_ac_hal_differs_from_xw_hal(by: dict[str, dict]) -> None:
    wa, xc, xw = by["WA:ath_hal.ko"], by["XC:ath_hal.ko"], by["XW:ath_hal.ko"]
    # WA and XC ath_hal.ko are NOT the same file
    assert wa["bytes"] == 367456
    assert xc["bytes"] == 360896
    assert wa["sha256"] != xc["sha256"]
    # XW names the INI/ANI side and none of the ar9300 cca surface
    for tok in ("firstep", "cycpwr"):
        assert tok in xw["tokens"], tok
    for tok in ("cca_thresh", "nf_cal", "noise_floor", "strong_signal"):
        assert tok not in xw["tokens"], f"{tok} unexpectedly present in XW ath_hal.ko"


def test_named_functions_in_symbol_context(by: dict[str, dict]) -> None:
    ctx = by["WA:ath_hal.ko"]["tokens"]["cca_thresh"]["contexts"][0]["context"]
    assert "ar9300_set_cca_threshold" in ctx
    nf = by["WA:ath_hal.ko"]["tokens"]["nf_cal"]["contexts"][0]["context"]
    assert "ar9300_is_nf_cal_done" in nf
    ss = by["WA:ath_hal.ko"]["tokens"]["strong_signal"]["contexts"][0]["context"]
    assert "ar9300_disable_strong_signal" in ss


def test_ani_state_vector_string(by: dict[str, dict]) -> None:
    ctx = by["WA:umac.ko"]["tokens"]["firstep"]["contexts"][0]["context"]
    for tok in ("firstep", "firstep_low", "cycpwr_thr", "self_corr_low"):
        assert tok in ctx, tok
    assert "ANI UPDATE" in ctx


def test_xw_ini_override_strings(by: dict[str, dict]) -> None:
    firstep = by["XW:ath_hal.ko"]["tokens"]["firstep"]["contexts"][0]["context"]
    cycpwr = by["XW:ath_hal.ko"]["tokens"]["cycpwr"]["contexts"][0]["context"]
    assert "firstep[level]" in firstep and "ini=" in firstep and "def:" in firstep
    assert "cycpwrThr1[level]" in cycpwr and "ini=" in cycpwr


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    for phrase in ("no firmware loaded", "no module loaded", "no radio contacted"):
        assert phrase in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
