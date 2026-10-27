"""Stage 423A — regression tests.

Pins the one thing that works (the address resolves under DRAM base 0x00400000) and the two things
that do not (no firmware-2/5.bin, and the 32 words there are not pointers). `hook_table_recovered`
must stay 0.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "build_stage423a_qca988x_xtensa_target_polling_hooks_re.py"
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage423a_qca988x_xtensa_target_polling_hooks_re.json")

FIRST_WORDS = ["0x71a91f4a", "0x400006f2", "0x3f56c0ff", "0x010682aa",
               "0xa872049f", "0x020692a9"]


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "423A"
    for k in ("meta", "named_files", "container", "base_windows", "chunk",
              "pointer_runs", "summary", "gaps"):
        assert k in report
    assert report["meta"]["target_address"] == "0x0040f688"
    assert report["meta"]["target_entries"] == 32


def test_named_files_absent(report: dict) -> None:
    assert report["named_files"] == {"firmware-2.bin": 0, "firmware-5.bin": 0}
    assert report["summary"]["named_files_present"] == 0
    assert len(report["meta"]["premise_corrections"]) == 2


def test_container_is_the_openwrt_blob(report: dict) -> None:
    c = report["container"]
    assert c["bytes"] == 204796
    assert c["version"] == "10.1-ct-8x-__fW-022-ecad3248"
    assert c["segments"] == 2
    assert c["tail_pad"] == 3


def test_only_dram_base_resolves(report: dict) -> None:
    s = report["summary"]
    assert s["address_resolvable"] == 1
    assert s["resolving_base"] == "0x00400000"
    assert s["file_offset"] == "0x0112e0"
    wins = report["base_windows"]
    assert len(wins) == 10                      # 5 bases x 2 segments
    inside = [w for w in wins if w["inside"]]
    assert len(inside) == 1
    assert inside[0]["base"] == "0x00400000"
    assert inside[0]["segment"] == 3
    assert inside[0]["rel"] == "0x00f688"


def test_chunk_is_code_not_pointers(report: dict) -> None:
    ch = report["chunk"]
    assert ch["count"] == 32
    assert ch["distinct"] == 32
    assert ch["in_range"] == 0
    assert ch["aligned"] == 0
    assert ch["verdict"] != "pointer table"
    assert report["summary"]["chunk_looks_like_code"] == 1
    assert report["summary"]["valid_pointers_in_chunk"] == 0
    assert ch["words"][:6] == FIRST_WORDS


def test_no_32_entry_table_anywhere(report: dict) -> None:
    s = report["summary"]
    assert s["exact_32_runs"] == 0
    assert s["best_run_length"] == 9
    assert s["pointer_runs_8plus"] == 1
    assert report["pointer_runs"]["4"] == []
    run = report["pointer_runs"]["3"][0]
    assert run == {"at": "0x001144", "length": 9}


def test_hook_table_not_recovered(report: dict) -> None:
    assert report["summary"]["hook_table_recovered"] == 0
    joined = " ".join(report["gaps"])
    assert "zero in-range pointers" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no firmware loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
