"""Stage 388A — regression tests.

Pins the three-part result: the product family is absent from the corpus, the AirFIBER MIB
documents nothing about TDD or cyclic prefix, and the LTU modules expose the frame contract as ten
attribute names with zero ratio or CP tables. The single `TDD` token must stay classified as a
mangled symbol fragment, never as frame control.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "af4x_invictus2_fpga_tdd_cyclic_prefix_re.py"
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage388a_af4x_invictus2_tdd_cp_re.json")

TEN_PARAMS = {"cpsample", "dl_symbols", "duty_cycle", "frame_len", "frame_period",
              "gap0", "gps_sync_timeout", "sample_rate", "sync_mode", "ul_symbols"}


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
    assert report["meta"]["stage"] == "388A"
    for k in ("meta", "modules", "mib", "inventory", "summary", "gaps"):
        assert k in report
    assert len(report["meta"]["premise_corrections"]) == 2


def test_five_ltu_modules(ok: list[dict]) -> None:
    assert len(ok) == 5
    assert {r["module"] for r in ok} == {"ame_core.ko", "ame_dev.ko", "ame_dfs.ko",
                                        "cds_mac_mod.ko", "ubnthal.ko"}
    assert report_module(ok) is True


def report_module(ok: list[dict]) -> bool:
    return all("sha256" in r for r in ok)


def test_no_airfiber_image_exists(report: dict) -> None:
    s = report["summary"]
    assert s["airfiber_firmware_binaries"] == 0
    # the count is not pinned: other workstreams add matching files (Stage 449A receipt, then
    # stage822a documentation archives). What must never change is zero firmware binaries.
    assert s["airfiber_artifacts"] >= 11
    paths = {r["path"] for r in report["inventory"]}
    assert "artifacts/autoresearch/stage449a_af4x_af5x_invictus2_tdd_tuning_kit.json" in paths
    assert not any(p.endswith((".bin", ".ko", ".ipk", ".img")) for p in paths)
    assert all(r["suffix"] not in (".bin", ".ko", ".ipk", ".img")
               for r in report["inventory"])


def test_mib_documents_no_tdd(report: dict) -> None:
    m = report["mib"]
    assert m["object_types"] == 157
    assert m["tdd"] == 0
    assert m["cyclic"] == 0
    assert m["strict"] == 0
    assert m["duty"] == 0
    assert m["revision"] == "201405090000Z"
    assert report["summary"]["mib_tdd_objects"] == 0


def test_ten_parameter_names(by: dict[str, dict], report: dict) -> None:
    assert set(by["ame_dev.ko"]["params"]) == TEN_PARAMS
    assert report["summary"]["param_names_found"] == 10
    assert report["summary"]["modules_with_duty_cycle"] == 3
    assert report["summary"]["modules_with_cpsample"] == 1
    assert report["summary"]["modules_with_frame_symbols"] == 2


def test_frame_descriptor_print(by: dict[str, dict]) -> None:
    ctx = " ".join(by["ame_dev.ko"]["param_contexts"]["duty_cycle"])
    for tok in ("frame_period", "duty_cycle", "sample_rate", "cpsample",
                "dl_symbols", "ul_symbols"):
        assert tok in ctx, tok
    assert "bandwidth" in ctx


def test_dfs_validates_duty_against_load(by: dict[str, dict], report: dict) -> None:
    # the message spells "duty cycle" with a space, so it is captured via `too low for`
    assert report["summary"]["modules_with_duty_validation"] == 1
    ctx = " ".join(by["ame_dfs.ko"]["duty_warn"]["contexts"])
    assert "duty cycle" in ctx
    assert "too low" in ctx
    assert "traffic load" in ctx


def test_no_ratio_table(report: dict, ok: list[dict]) -> None:
    assert report["summary"]["ratio_string_hits"] == 0
    assert report["summary"]["ratio_table_recovered"] == 0
    for r in ok:
        assert sum(r["ratios"].values()) == 0, r["module"]
        for k in ("75/25", "67/33", "50/50"):
            assert r["ratios"][k] == 0


def test_no_cp_table(report: dict, ok: list[dict]) -> None:
    assert report["summary"]["cp_literal_hits"] == 0
    assert report["summary"]["cp_table_recovered"] == 0
    for r in ok:
        for k in ("cp=4", "cp=8", "cp=16", "cp_len", "cp_prefix"):
            assert r["cp_literals"][k] == 0, (r["module"], k)


def test_strict_timing_absent(report: dict, ok: list[dict]) -> None:
    assert report["summary"]["strict_timing_hits"] == 0
    for r in ok:
        assert sum(r["strict"].values()) == 0


def test_single_tdd_token_is_a_symbol_fragment(by: dict[str, dict], report: dict) -> None:
    assert report["summary"]["tdd_token_hits"] == 1
    assert by["ame_core.ko"]["tdd"]["TDD"] == 1
    ctx = " ".join(by["ame_core.ko"]["tdd_contexts"])
    assert "foe_TDDeRotCFO" in ctx
    # it must not be read as frame control
    joined = " ".join(report["gaps"])
    assert "mangled symbol fragment" in joined


def test_duty_cycle_function_symbol(by: dict[str, dict]) -> None:
    ctx = " ".join(by["ame_core.ko"]["param_contexts"]["duty_cycle"])
    assert "ame_bbp_get_duty_cycle" in ctx


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
