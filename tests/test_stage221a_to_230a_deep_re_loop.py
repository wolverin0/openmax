"""Stages 221A..230A — unified regression tests for the 10-stage deep RE loop.

Pins the three refuted premises and the honest limits:

  * 225A: the `athwlan_AR9888v2_ptmp_ap_bin` / `_sta_bin` pair is absent, so no WMI handler
    delta is possible.
  * 226A: `eab_driver.ko` does not exist; the DMA analysis runs on `ame_core.ko`.
  * 224A: `WA.v8.7.11` / `XC.v8.7.11` do not exist; the platform axis uses 8.7.25.

And it pins the two results that would otherwise drift: 221A must find indirect-call offsets,
222A must still report **zero** exact sink mappings.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "audit_stage221a_to_230a_deep_re.py"
AR = REPO / "artifacts" / "autoresearch"
STAGES = list(range(221, 231))


def receipt(n: int) -> dict:
    p = AR / f"stage{n}a_deep_re_loop.json"
    assert p.exists(), f"missing receipt for stage {n}A: {p}"
    return json.loads(p.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def r221() -> dict:
    return receipt(221)


@pytest.fixture(scope="module")
def r222() -> dict:
    return receipt(222)


@pytest.fixture(scope="module")
def r223() -> dict:
    return receipt(223)


@pytest.fixture(scope="module")
def r224() -> dict:
    return receipt(224)


@pytest.fixture(scope="module")
def r225() -> dict:
    return receipt(225)


@pytest.fixture(scope="module")
def r226() -> dict:
    return receipt(226)


@pytest.fixture(scope="module")
def r227() -> dict:
    return receipt(227)


@pytest.fixture(scope="module")
def r228() -> dict:
    return receipt(228)


@pytest.fixture(scope="module")
def r229() -> dict:
    return receipt(229)


@pytest.fixture(scope="module")
def r230() -> dict:
    return receipt(230)


def test_all_ten_receipts_exist() -> None:
    for n in STAGES:
        r = receipt(n)
        assert r["meta"]["stage"] == f"{n}A"


def test_221a_recovers_indirect_call_offsets(r221: dict) -> None:
    s = r221["summary"]
    assert s["modules_ok"] == 4
    assert s["distinct_offsets"] >= 20, f"too few pointer-slot candidates: {s['distinct_offsets']}"
    assert s["total_indirect_sites"] >= 100


def test_221a_does_not_claim_register_accessor(r221: dict) -> None:
    gaps = " ".join(r221["gaps"])
    assert "not proven register-write accessors" in gaps


def test_222a_still_zero_exact_mappings(r222: dict) -> None:
    s = r222["summary"]
    assert s["knobs_in_boundary"] == 437
    assert s["exact_sink_mappings"] == 0, "222A must not manufacture knob->sink mappings"


def test_223a_version_axis(r223: dict) -> None:
    s = r223["summary"]
    assert s["pairs"] == 5
    assert s["pairs_ok"] >= 3
    # a version bump should change the binaries
    assert s["total_differing_bytes"] > 0


def test_224a_platform_axis_and_premise(r224: dict) -> None:
    assert "v8.7.11" in r224["meta"]["premise_correction"]
    assert "8.7.25" in r224["meta"]["premise_correction"]
    s = r224["summary"]
    assert s["pairs"] == 3
    assert s["pairs_ok"] >= 2


def test_225a_firmware_pair_absent(r225: dict) -> None:
    s = r225["summary"]
    assert s["ap_sta_pair_present"] is False
    assert s["wmi_handlers_diffed"] == 0
    assert "absent" in " ".join(r225["gaps"])


def test_226a_eab_driver_absent(r226: dict) -> None:
    assert r226["summary"]["eab_driver_present"] is False
    assert "does not exist" in r226["meta"]["premise_correction"]
    assert r226["summary"]["modules_ok"] == 2
    assert r226["summary"]["max_dma_symbols"] > 10


def test_227a_spectral_and_pktlog(r227: dict) -> None:
    s = r227["summary"]
    assert s["modules_ok"] == 4
    assert s["spectral_syms"] > 5
    assert s["pktlog_syms"] > 5


def test_228a_rounds_not_isolated(r228: dict) -> None:
    # no single-knob isolation evidence exists in the sources found
    assert r228["summary"]["rounds_isolated"] == 0
    assert "requires one round per knob" in " ".join(r228["gaps"])


def test_229a_sysctl_inventory(r229: dict) -> None:
    s = r229["summary"]
    assert s["modules_with_registrations"] > 0
    assert s["total_registration_symbols"] > 0
    assert s["images_covered"] == 3


def test_230a_consolidates_nine(r230: dict) -> None:
    s = r230["summary"]
    assert s["stages"] == 9
    assert s["premise_corrections"] == 3
    assert len(r230["ledger"]) == 9
    for key, v in r230["ledger"].items():
        assert len(v["sha256"]) == 64


def test_all_stages_declare_static_only() -> None:
    for n in STAGES:
        assert "static" in receipt(n)["meta"]["radio_safety"].lower()


def test_tool_is_reproducible() -> None:
    before = {n: (AR / f"stage{n}a_deep_re_loop.json").read_bytes() for n in STAGES}
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    after = {n: (AR / f"stage{n}a_deep_re_loop.json").read_bytes() for n in STAGES}
    assert before == after, "the ten receipts are not deterministic across runs"
