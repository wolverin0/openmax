#!/usr/bin/env python3
"""
Tests for Stage 73B (`T-S73B-UPH-BUG01-TO-08-DISCLOSURE-AND-BINARY-PATCH-SYNTHESIS`):
Verifies:
  1. `docs/UBIQUITI_AIRMAX_AC_UPH_BUG_DISCLOSURE_REPORT.md` (`< 200` lines, 1 `<!-- doc-head -->`, bilingual EN/ES summary,
     `UPH-BUG-02..08` with MIPS32 offsets and C fixes).
  2. `tools/re/patch_stage73b_uph_bugs_and_atomic_helper.py` binary patcher (`0` `.rel.text` / `.rel.rodata` overlaps on
     both `WA.v8.7.25` and `XC.v8.7.25` `ubnt_poll_host.ko`).
  3. `render_uph_atomic_apply_sequence()` atomic stock-firmware helper (`enable=0 -> configure -> enable=1`,
     corrected `atpc` `vec[2]=max, vec[3]=min` order, pre-clamped `ff_dl_alloc >= 25`, and `ff_mcast_airtime_limit` last).
  4. `artifacts/autoresearch/stage73b_uph_bugs_patch_and_disclosure_20261026.json` + `ClosedLoopResearchReactor`.
"""

from __future__ import annotations

import json

from elftools.elf.elffile import ELFFile

from tools.re.patch_stage73b_uph_bugs_and_atomic_helper import (
    DISCLOSURE_REPORT_MD,
    STAGE73B_RECEIPT_JSON,
    WA_8725_PATCHED_OUT,
    XC_8725_PATCHED_OUT,
    quantize_ff_dl_alloc_safe,
    render_uph_atomic_apply_sequence,
    run_stage73b_patch_and_disclosure,
)


def test_stage73b_disclosure_report_hygiene_and_completeness() -> None:
    assert DISCLOSURE_REPORT_MD.exists()
    text = DISCLOSURE_REPORT_MD.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 200, f"Expected < 200 lines, got {len(lines)}"
    assert text.count("<!-- doc-head:") == 1
    assert "English Summary" in text
    assert "Resumen Ejecutivo (Español)" in text
    for bug_id in (
        "UPH-BUG-02",
        "UPH-BUG-03",
        "UPH-BUG-04",
        "UPH-BUG-05",
        "UPH-BUG-06",
        "UPH-BUG-07",
        "UPH-BUG-08",
    ):
        assert bug_id in text


def test_stage73b_wa_and_xc_binary_patches_and_zero_relocation_overlaps() -> None:
    payload = run_stage73b_patch_and_disclosure()
    assert STAGE73B_RECEIPT_JSON.exists()
    loaded = json.loads(STAGE73B_RECEIPT_JSON.read_text(encoding="utf-8"))
    assert loaded["stage"] == "73B"
    assert loaded["verdict"] == "CONFIRMED"

    for key, out_path in (("wa_v8_7_25", WA_8725_PATCHED_OUT), ("xc_v8_7_25", XC_8725_PATCHED_OUT)):
        rec = payload["binary_patch_receipts"][key]
        assert rec["elf_verify_patch_status"] == "PASS_ZERO_RELOCATION_OVERLAPS"
        assert rec["rel_text_overlaps"] == 0
        assert rec["rel_rodata_overlaps"] == 0
        assert rec["text_patches_count"] == 4
        assert rec["rodata_patches_count"] == 16
        assert out_path.exists()

        with out_path.open("rb") as f:
            elf = ELFFile(f)
            text_sec = elf.get_section_by_name(".text").data()
            rodata_sec = elf.get_section_by_name(".rodata").data()

        # Verify UPH-BUG-03 patch at .text+0x02fe4
        assert text_sec[0x02FE4 : 0x02FE8].hex() == "24030019"
        # Verify UPH-BUG-06 patches at .text+0x024e8, 0x0288c, 0x02d20
        assert text_sec[0x024E8 : 0x024EC].hex() == "00000000"
        assert text_sec[0x0288C : 0x02890].hex() == "00000000"
        assert text_sec[0x02D20 : 0x02D24].hex() == "00000000"
        # Verify UPH-BUG-07 patches across all 8 .rodata ptmp_netconf profiles
        for idx in range(8):
            base = 0x0B28 + idx * 104
            assert rodata_sec[base + 75] == 6
            assert rodata_sec[base + 84] == 6


def test_stage73b_atomic_apply_sequence_helper() -> None:
    assert quantize_ff_dl_alloc_safe(10) == 25
    assert quantize_ff_dl_alloc_safe(25) == 25
    assert quantize_ff_dl_alloc_safe(33) == 33
    assert quantize_ff_dl_alloc_safe(50) == 50
    assert quantize_ff_dl_alloc_safe(67) == 67
    assert quantize_ff_dl_alloc_safe(80) == 75

    seq = render_uph_atomic_apply_sequence(
        radio_if="wifi0",
        cms_bias=6,
        voip_bias=6,
        daprot=2,
        ff_mcast_airtime_limit=5,
        atpc_tuple=(1, -50, 0, 30, 20),
        timing_tuple=(8000, 8000, 3000),
        fixed_frame_tuple=(8000, 15, 4, 12, 12, 20, 20, 0, 0, 1),
    )
    assert seq["normalized_atpc_vector"] == (1, -50, 30, 0, 20)
    assert seq["normalized_fixed_frame_vector"] == (8000, 25, 4, 12, 12, 20, 20, 0, 0, 1)

    cmds = seq["commands"]
    assert cmds[0].startswith("echo 0 > /proc/sys/dev/uph_wifi0/enable")
    assert cmds[1].startswith("echo 0 > /proc/sys/dev/uph_wifi0/ptp_xmit")
    assert "echo '1 -50 30 0 20' > /proc/sys/dev/uph_wifi0/atpc" in cmds
    assert "echo '8000 8000 3000' > /proc/sys/dev/uph_wifi0/timing" in cmds
    assert "echo '8000 25 4 12 12 20 20 0 0 1' > /proc/sys/dev/uph_wifi0/fixed_frame" in cmds
    # Verify ff_mcast_airtime_limit is written immediately before re-enabling enable=1 / ptp_xmit=1
    assert cmds[-3] == "echo 5 > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit"
    assert cmds[-2].startswith("echo 1 > /proc/sys/dev/uph_wifi0/enable")
    assert cmds[-1].startswith("echo 1 > /proc/sys/dev/uph_wifi0/ptp_xmit")
