"""Verification tests for Stage 100D XC-BUG-03 cross-platform disassembly and LTU read-only metadata verification."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = ROOT / "artifacts" / "autoresearch" / "stage100d_xc_bug03_hs_uart_and_ltu_suid_verify.json"
DOC_PATH = ROOT / "docs" / "STAGE100D_XC_BUG03_HS_UART_DISASM_AND_LTU_VERIFY.md"
SCRIPT_PATH = ROOT / "tools" / "bench" / "run_stage100d_xc_bug03_hs_uart_and_ltu_suid_verify.py"


def test_stage100d_files_exist_and_doc_budget() -> None:
    assert SCRIPT_PATH.exists(), f"Missing script {SCRIPT_PATH}"
    assert ARTIFACT_PATH.exists(), f"Missing artifact {ARTIFACT_PATH}"
    assert DOC_PATH.exists(), f"Missing doc {DOC_PATH}"

    lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 160, f"Doc exceeds 160 lines ({len(lines)})"
    assert lines[0].startswith("<!-- doc-head:"), "Doc must start with <!-- doc-head: -->"


def test_stage100d_xc_bug03_cross_platform_disassembly() -> None:
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "100D"
    assert data["status"] == "CONFIRMED"
    assert str(data.get("pillar_e_memory_master_claim_id", "")).startswith("mm-")

    xc = data["xc_bug03_cross_platform_disassembly"]
    assert xc["exact_byte_match_2xc_vs_5xc"] is True
    assert xc["kallsyms_match_2xc_vs_5xc"] is True
    assert xc["r2ac_2xc_sha256"] == "3e92126565d4b174a26ef1e138fd8abe5cd1f82091bc5b7df1f4fe74fd1867e6"
    assert xc["r5ac_5xc_sha256"] == xc["r2ac_2xc_sha256"]
    assert xc["ath_hs_uart_close_exact_bytes_hex"] == "03e0000800000000"

    close_insns = xc["disassembly"]["ath_hs_uart_close"]
    assert len(close_insns) == 2
    assert close_insns[0]["mnemonic"] == "jr"
    assert close_insns[0]["op_str"] == "$ra"
    assert close_insns[1]["mnemonic"] == "nop"


def test_stage100d_ltu_readonly_metadata_verification() -> None:
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    ltu = data["ltu_live_readonly_metadata_verification"]
    assert len(ltu["suid_binaries_ls_ln"]) == 4
    assert all(line.startswith("-rwsr-xr-x") for line in ltu["suid_binaries_ls_ln"])
    assert len(ltu["dev_ame_nodes_ls_ln"]) == 14
