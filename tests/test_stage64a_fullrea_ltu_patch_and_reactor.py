from __future__ import annotations

import json
import struct
from pathlib import Path

from tools.ltu.patch_ltu_ame_core_binary import (
    parse_elf32_sections_and_symbols,
    run_all_ltu_patches,
)
from tools.research.closed_loop_research_reactor import (
    STAGE64A_HYPERRESEARCH_VAULT_JSON,
    STAGE64A_REACTOR_RECEIPT_JSON,
    ingest_stage55a_60a_64a_and_synthesize_m36_m37_ltu_m1,
)

ROOT = Path(__file__).resolve().parents[1]


def test_stage64a_surgical_ltu_binary_patcher_zero_relocation_overlaps() -> None:
    summary = run_all_ltu_patches()
    assert summary["Status"] == "CONFIRMED"
    assert summary["zero_relocation_corruption_verified"] is True

    mods = summary["modules_patched"]
    assert set(mods.keys()) == {
        "afltu_2.4.2_ame_core",
        "aflturocket_2.4.2_ame_core",
        "afltu_2.4.2_ame_dev",
        "aflturocket_2.4.2_ame_dev",
    }

    for key, rec in mods.items():
        verify = rec["elf_verify_patch"]
        assert verify["size_preserved"] is True
        assert verify["total_overlapped_relocations"] == 0, f"{key} overlapped relocations: {verify}"
        assert rec["orig_sha256"] != rec["patched_sha256"]


def test_stage64a_ame_core_rodata_data_and_text_patches_verified_in_bytes() -> None:
    out_dir = ROOT / "artifacts" / "autoresearch" / "stage64a_patched_modules"
    patched_cpe = out_dir / "ame_core_fmx_afltu_2.4.2.ko"
    data = patched_cpe.read_bytes()
    _, sec_by_name, syms, rel_text = parse_elf32_sections_and_symbols(data)

    text_off = sec_by_name[".text"][1][4]
    rodata_off = sec_by_name[".rodata"][1][4]
    data_off = sec_by_name[".data"][1][4]

    # Verify startThrd_4096 == 90 and stayThrd_4096 == 82
    start_val = struct.unpack("<I", data[rodata_off + syms["startThrd_4096"][0] : rodata_off + syms["startThrd_4096"][0] + 4])[0]
    stay_val = struct.unpack("<I", data[rodata_off + syms["stayThrd_4096"][0] : rodata_off + syms["stayThrd_4096"][0] + 4])[0]
    assert start_val == 90
    assert stay_val == 82

    # Verify table_ptpPwrRange 60/80/100 MHz (bw 5, 6, 7) at 4096-QAM (mod 6) are unlocked (non-zero)
    pwr_base = data_off + syms["table_ptpPwrRange"][0]
    for prof_idx in range(4):
        for bw_idx in (5, 6, 7):
            off = pwr_base + prof_idx * 112 + bw_idx * 14 + 6 * 2
            assert data[off] == 20
            assert data[off + 1] in (50, 52, 55)

    # Verify ame_bbp_set_autoMcsCeiling + 20 is `b +8` (00 00 00 ea) and not in .rel.text
    ceil_patch_off = syms["ame_bbp_set_autoMcsCeiling"][0] + 20
    assert ceil_patch_off not in rel_text
    assert data[text_off + ceil_patch_off : text_off + ceil_patch_off + 4] == bytes.fromhex("000000ea")


def test_stage64a_ame_dev_frame_len_store_hook_offset_fix() -> None:
    out_dir = ROOT / "artifacts" / "autoresearch" / "stage64a_patched_modules"
    patched_dev = out_dir / "ame_dev_fmx_afltu_2.4.2.ko"
    data = patched_dev.read_bytes()
    _, sec_by_name, syms, rel_text = parse_elf32_sections_and_symbols(data)

    text_off = sec_by_name[".text"][1][4]
    fl_patch_off = syms["frame_len_store"][0] + 48
    assert fl_patch_off not in rel_text
    # Fixed instruction loads g_core_hooks + 0x5c (ame_bbp_set_frame_len) instead of + 0x54 (ame_bbp_set_duty_cycle)
    assert data[text_off + fl_patch_off : text_off + fl_patch_off + 4] == bytes.fromhex("5c3092e5")


def test_stage64a_closed_loop_reactor_and_scholar_jev_vault() -> None:
    payload = ingest_stage55a_60a_64a_and_synthesize_m36_m37_ltu_m1()
    assert payload["stage"] == "64A"
    assert payload["status"] == "CONFIRMED"
    assert STAGE64A_REACTOR_RECEIPT_JSON.exists()
    assert STAGE64A_HYPERRESEARCH_VAULT_JSON.exists()

    vault = json.loads(STAGE64A_HYPERRESEARCH_VAULT_JSON.read_text(encoding="utf-8"))
    assert vault["verifier_model"] == "jev-1.14.0"
    assert vault["papers_count"] == 3
    paper_ids = {p["paper_id"] for p in vault["verified_papers"]}
    assert paper_ids == {"2509.03855v7", "2608.01555v1", "0711.1273v1"}
    for p in vault["verified_papers"]:
        assert p["verification_status"] == "supported"
        assert p["verification_probability"] >= 0.85

    mids = [m["mechanism_id"] for m in payload["synthesized_candidate_mutations"]]
    assert mids == ["M36", "M37", "LTU-M1"]
