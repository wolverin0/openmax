"""Stage 328A — unified regression suite for the deep `.ko` RE series 323A..327A.

Each stage is covered by its own section. The suite pins the results that would otherwise drift,
and the negatives that must not be quietly promoted:

  323A  `eab_driver.ko` is absent; the DMA surface belongs to ame_core/ame_dev
  324A  four of the five frame durations; 1 ms genuinely absent
  325A  AID ceiling 128 present, 64 absent
  326A  `ath_hw_hang_check` present in all three images
  327A  zero shm/specd symbols — the ubntspecd layout is not in these modules
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
AR = REPO / "artifacts" / "autoresearch"

R323 = AR / "stage323a_ltu_eab_driver_dma_ring_re.json"
R324 = AR / "stage324a_ltu_ame_core_scheduler_re.json"
R325 = AR / "stage325a_wa_xc_umac_node_aid_re.json"
R326 = AR / "stage326a_ath_dev_bmiss_hang_recovery_re.json"
R327 = AR / "stage327a_ubnt_spectral_fft_re.json"

TOOLS = {
    "323A": REPO / "tools" / "re" / "ltu_eab_driver_dma_ring_and_interrupt_coalesce_re.py",
    "324A": REPO / "tools" / "re" / "ltu_ame_core_scheduler_and_ul_dl_ratio_re.py",
    "325A": REPO / "tools" / "re" / "wa_xc_umac_ieee80211_node_and_aid_bitmap_re.py",
    "326A": REPO / "tools" / "re" / "ath_dev_bmiss_and_reset_recovery_re.py",
    "327A": REPO / "tools" / "re" / "ubnt_spectral_scan_fft_bin_format_re.py",
}


def load(path: Path) -> dict:
    assert path.exists(), f"missing receipt: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def r323() -> dict:
    return load(R323)


@pytest.fixture(scope="module")
def r324() -> dict:
    return load(R324)


@pytest.fixture(scope="module")
def r325() -> dict:
    return load(R325)


@pytest.fixture(scope="module")
def r326() -> dict:
    return load(R326)


@pytest.fixture(scope="module")
def r327() -> dict:
    return load(R327)


# ------------------------------------------------------------------ structure
def test_all_five_receipts_exist_and_are_labelled() -> None:
    for stage, path in (("323A", R323), ("324A", R324), ("325A", R325),
                        ("326A", R326), ("327A", R327)):
        r = load(path)
        assert r["meta"]["stage"] == stage


def test_all_five_tools_exist() -> None:
    for stage, path in TOOLS.items():
        assert path.exists(), f"{stage} script missing: {path}"


def test_every_receipt_declares_static_scope() -> None:
    for path in (R323, R324, R325, R326, R327):
        r = load(path)
        scope = r["meta"]["scope"].lower()
        assert "static" in scope
        assert "no module loaded" in scope


def test_every_receipt_has_gaps() -> None:
    for path in (R323, R324, R325, R326, R327):
        r = load(path)
        assert r["gaps"], f"{path.name} has no declared gaps"


# ------------------------------------------------------------------ 323A
def test_323a_eab_driver_absent(r323: dict) -> None:
    assert r323["eab_driver_files"] == []
    assert r323["summary"]["eab_driver_present"] is False
    assert r323["summary"]["modules_ok"] == 2


def test_323a_dma_and_irq_counts(r323: dict) -> None:
    assert r323["summary"]["dma_symbols"] == 55
    assert r323["summary"]["irq_symbols"] == 82


# ------------------------------------------------------------------ 324A
def test_324a_four_durations(r324: dict) -> None:
    ok = [m for m in r324["modules"] if m.get("status") == "ok"]
    assert len(ok) == 2
    for m in ok:
        assert {"2000", "2500", "4000", "5000"} <= set(m["frame_us"])
        assert "1000" not in m["frame_us"]


def test_324a_symbol_buckets(r324: dict) -> None:
    rocket = next(m for m in r324["modules"] if "Rocket" in m["module"])
    assert rocket["buckets"]["grant"]["count"] == 314
    assert rocket["buckets"]["modulation"]["count"] == 151


def test_324a_modules_are_arm(r324: dict) -> None:
    for m in r324["modules"]:
        if m.get("status") == "ok":
            assert m["endian"] == "little"


# ------------------------------------------------------------------ 325A
def test_325a_node_and_aid(r325: dict) -> None:
    ok = [m for m in r325["modules"] if m.get("status") == "ok"]
    assert len(ok) == 2
    for m in ok:
        assert m["buckets"]["node"]["count"] == 277
        assert m["buckets"]["aid"]["count"] == 48
        assert m["aid_ceilings"].get("128") == 1
        assert "64" not in m["aid_ceilings"]


# ------------------------------------------------------------------ 326A
def test_326a_three_images_and_abi(r326: dict) -> None:
    ok = [m for m in r326["modules"] if m.get("status") == "ok"]
    assert len(ok) == 3
    abis = {m["abi"] for m in ok}
    assert "2.6.32.68" in abis and "2.6.32.71" in abis


def test_326a_hang_check_present_everywhere(r326: dict) -> None:
    for m in r326["modules"]:
        if m.get("status") == "ok":
            assert "ath_hw_hang_check" in m["hang_check_symbols"], m["image"]


def test_326a_xw_is_larger(r326: dict) -> None:
    by = {m["image"]: m for m in r326["modules"] if m.get("status") == "ok"}
    assert by["XW.v6.3.6"]["bytes"] > by["WA.v8.7.25"]["bytes"]


# ------------------------------------------------------------------ 327A
def test_327a_modules_and_fft(r327: dict) -> None:
    assert r327["summary"]["modules_ok"] == 4
    assert r327["summary"]["spectral_modules"] == 2
    assert r327["summary"]["fft_symbols"] == 38


def test_327a_shm_is_absent(r327: dict) -> None:
    # the ubntspecd layout is NOT in these modules; this must not be "found" later
    assert r327["summary"]["shm_symbols"] == 0
    for m in r327["modules"]:
        if m.get("status") == "ok":
            assert m["buckets"]["shm"]["count"] == 0


def test_327a_bin_candidates(r327: dict) -> None:
    for m in r327["modules"]:
        if m.get("status") == "ok" and "ath_spectral" in m["module"]:
            assert set(m["fft_bin_candidates"]) == {"32", "64", "256", "512"}


# ------------------------------------------------------------------ reproducibility
def test_every_tool_is_reproducible() -> None:
    receipts = {s: p.read_bytes() for s, p in
                (("323A", R323), ("324A", R324), ("325A", R325),
                 ("326A", R326), ("327A", R327))}
    for stage, tool in TOOLS.items():
        subprocess.run([sys.executable, str(tool)], check=True, cwd=str(REPO),
                       stdout=subprocess.DEVNULL)
    for stage, path in (("323A", R323), ("324A", R324), ("325A", R325),
                        ("326A", R326), ("327A", R327)):
        assert path.read_bytes() == receipts[stage], f"{stage} receipt is not deterministic"
