"""Stage 154A — regression tests for the AF-LTU ame_core / ame_dev dissection.

The most important assertions here are negative: `eab_driver.ko` does not exist, v2.4.0 is
not on disk, and the ASIC-register count is **zero by construction** because the sweep uses
the MIPS `lui/addiu` idiom while these modules are ARM little-endian. A future run must not
read that zero as evidence that no register is addressed.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "audit_stage154a_ltu_ame_eab_full_re.py"
RECEIPT = REPO / "artifacts" / "autoresearch" / "stage154a_ltu_ame_eab_full_re.json"


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"receipt missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def modules(report: dict) -> dict:
    return {m["path"]: m for i in report["images"] for m in i["modules"]
            if m.get("status") == "ok"}


def test_receipt_shape(report: dict) -> None:
    for key in ("meta", "images", "summary", "gaps"):
        assert key in report
    assert report["meta"]["stage"] == "154A"


def test_eab_driver_absence_recorded(report: dict) -> None:
    notes = " ".join(report["meta"]["premise_corrections"])
    assert "eab_driver.ko does not exist" in notes
    assert report["summary"]["eab_driver_present"] is False


def test_v240_absence_recorded(report: dict) -> None:
    notes = " ".join(report["meta"]["premise_corrections"])
    assert "v2.4.0 does not exist" in notes


def test_four_modules_audited(modules: dict) -> None:
    assert set(modules) == {"ame_core.ko", "ame_dev.ko"}
    ok = [m for i in json.loads(RECEIPT.read_text(encoding="utf-8"))["images"]
          for m in i["modules"] if m.get("status") == "ok"]
    assert len(ok) == 4, "ame_core and ame_dev in both LTU images"


def test_core_is_large_and_symbol_rich(modules: dict) -> None:
    core = modules["ame_core.ko"]
    assert core["bytes"] > 3_000_000
    assert core["symbols_total"] > 9000


def test_dev_is_small_and_has_ioctl_symbols(modules: dict) -> None:
    dev = modules["ame_dev.ko"]
    assert dev["bytes"] == 298760
    assert dev["ioctl"]["ioctl_symbol_count"] >= 4


def test_register_count_is_zero_by_construction(modules: dict) -> None:
    for name in ("ame_core.ko", "ame_dev.ko"):
        rc = modules[name]["register_constants"]
        assert rc["count"] == 0
        assert rc["applicable"] == "no", "these modules are ARM little-endian"
        assert "ARM" in rc["note"]


def test_arm_caveat_present_in_gaps(report: dict) -> None:
    gaps = " ".join(report["gaps"])
    assert "ZERO BY CONSTRUCTION" in gaps
    assert "movw/movt" in gaps


def test_modulation_surface_is_non_empty(modules: dict) -> None:
    for name in ("ame_core.ko", "ame_dev.ko"):
        m = modules[name]
        assert m["modulation_string_count"] > 0, f"{name} shows no modulation strings"
        assert m["modulation_symbol_count"] > 0, f"{name} shows no modulation symbols"


def test_core_dma_and_modulation_imports(modules: dict) -> None:
    core = modules["ame_core.ko"]
    subs = core["imports_by_subsystem"]
    assert "dma" in subs or "regmap" in subs, "no DMA/regmap imports in ame_core"
    assert "modulation" in subs, "no modulation imports in ame_core"


def test_radio_safety_declared(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no module loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    after = RECEIPT.read_bytes()
    assert before == after, "receipt is not deterministic across runs"
