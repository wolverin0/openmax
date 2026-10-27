#!/usr/bin/env python3
"""Pytest suite for Stage 347A — PB-040 Xtensa SGMT Surgical RAM Patch Profiles."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from firmware.xtensa_sgmt_surgical_patcher import SgmtContainer
from tools.firmware.build_stage347a_xtensa_sgmt_ram_patch_profiles import (
    ARTIFACT_OUT,
    LOADER_SCRIPT_OUT,
    OUT_DIR,
    PATCHER_PATH,
    PB040_SPEC_PATH,
    PINNED_PATCHER_SHA256,
    PINNED_PB040_SPEC_SHA256,
    build_stage347a_profiles,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage347a_pinned_files_untouched() -> None:
    assert hashlib.sha256(PATCHER_PATH.read_bytes()).hexdigest() == PINNED_PATCHER_SHA256
    assert hashlib.sha256(PB040_SPEC_PATH.read_bytes()).hexdigest() == PINNED_PB040_SPEC_SHA256


def test_stage347a_profiles_and_xtensa_disassembly() -> None:
    report = build_stage347a_profiles()
    assert ARTIFACT_OUT.exists()
    loaded = json.loads(ARTIFACT_OUT.read_text(encoding="utf-8"))
    assert loaded["stage"] == "347A"
    assert loaded["memory_master_claim_id"] == "mm-61aa"
    assert loaded["sgmt_bmi_lz_verification"]["segments_verified"] == 12
    assert loaded["sgmt_bmi_lz_verification"]["all_12_segments_lossless_roundtrip"] is True
    assert len(loaded["generated_sgmt_binaries"]) == 12

    for item in loaded["generated_sgmt_binaries"]:
        bin_path = REPO_ROOT / item["path"]
        assert bin_path.exists()
        raw = bin_path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == item["sha256"]
        parsed = SgmtContainer.from_bytes(raw)
        assert parsed.entry_point == 0x00983C00
        assert sum(s.decoded_size for s in parsed.segments) == item["decoded_total_bytes"]

    ap_profiles = report["profiles_by_image"]["athwlan_AR9888v2_ptmp_ap_bin"]
    assert ap_profiles["PB040-CCA-AGC-OVERRIDE"]["xtensa_litbase_disassembly"]["lit4_slot_address_hex"] == "0x009810dc"
    assert (
        ap_profiles["PB040-CCA-AGC-OVERRIDE"]["xtensa_litbase_disassembly"]["l32r_call_sites"][0]["pc_hex"]
        == "0x009ad001"
    )

    assert LOADER_SCRIPT_OUT.exists()
    loader_txt = LOADER_SCRIPT_OUT.read_text(encoding="utf-8")
    assert "mount --bind /tmp/firmware-5.bin" in loader_txt
    assert "WATCHDOG_TIMEOUT_SEC=45" in loader_txt
