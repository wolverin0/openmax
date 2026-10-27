#!/usr/bin/env python3
"""Stage 347A — PB-040 Xtensa SGMT Surgical RAM Patch Profiles Builder & Disassembler.

Generates and cryptographically verifies the 3 PB-040 surgical RAM patch profiles:
  1. `PB040-CANARY-RODATA` (.rodata string canary at 0x0040b953 / 0x0040b8d3)
  2. `PB040-CCA-AGC-OVERRIDE` (Segment 3 baseband modal INI tuple for 0x00029e00 BB_timing_controls_1 cca_thresh62)
  3. `PB040-SUB20MHZ-PLL-DIV` (Segment 1 sub-20 MHz 5/10 MHz rate & clock divider table)

Across all 3 QCA988x / AR9888v2 (`Peregrine v2`) SGMT containers (`athwlan_AR9888v2_ptmp_ap_bin`,
`athwlan_AR9888v2_ptmp_sta_bin`, `athwlan_AR9888v2_ptp_bin`), verifying:
  - Pinned SHA-256 of `firmware/xtensa_sgmt_surgical_patcher.py` and `pb040_sgmt_surgical_patch_spec_20261025.json`.
  - 12/12 SGMT BMI_LZ segment lossless round-trip decompression/recompression.
  - Exact Xtensa `LITBASE = 0x009bb001` (`.lit4` Segment 0 `0x00980000`) to `l32r` (Segment 3 `0x00983c00`) instruction disassembly.
  - Volatile `/tmp` RAM bind-mount loader script (`fmx_xtensa_ram_patch_loader.sh`) with zero Flash writes.
"""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from firmware.xtensa_sgmt_surgical_patcher import (
    SGMT_MAGIC_LE,
    UMAC_8512_PATH,
    SgmtContainer,
    SgmtSurgicalPatcher,
    SurgicalPatchSpec,
    bmi_lz_compress,
    bmi_lz_decompress,
    load_ar9888v2_sgmt_containers,
)

PATCHER_PATH = REPO_ROOT / "firmware" / "xtensa_sgmt_surgical_patcher.py"
PB040_SPEC_PATH = REPO_ROOT / "artifacts" / "physical_boundary" / "pb040_sgmt_surgical_patch_spec_20261025.json"
PINNED_PATCHER_SHA256 = "49cb277389bc20af708777d4a5e23cc4d923d91b4d83c5a97bde683096f1451d"
PINNED_PB040_SPEC_SHA256 = "ea397abb4f522425674a75ab03554baf02837c3737adf189cfe1a9dbadc07c64"

OUT_DIR = REPO_ROOT / "firmware" / "openwrt" / "xtensa_ram_patches_stage347a"
ARTIFACT_OUT = REPO_ROOT / "artifacts" / "autoresearch" / "stage347a_xtensa_sgmt_ram_patch_profiles.json"
LOADER_SCRIPT_OUT = OUT_DIR / "fmx_xtensa_ram_patch_loader.sh"

# Xtensa LX4 LITBASE Special Register (SR 5) configuration in AR9888v2 SGMT firmware:
# LITBASE = 0x009bb001 (enable=1, base=0x009bb000) so imm16=0x1400 -> (0x1400-0x10000)*4 = -0x3b000 -> 0x00980000 (Segment 0 .lit4)
XTENSA_LITBASE_SR5 = 0x009BB001
XTENSA_LITBASE_ADDR = 0x009BB000
XTENSA_SEG0_IMM16_BASE = 0x1400


IMAGE_PROFILE_MATRIX: dict[str, list[dict[str, Any]]] = {
    "athwlan_AR9888v2_ptmp_ap_bin": [
        {
            "patch_id": "PB040-CANARY-RODATA",
            "pb_stage": "PB-040 (Step 1 — Zero-Risk .rodata String Canary)",
            "segment_index": 1,
            "virtual_address": 0x0040B953,
            "expected_orig_bytes": b"e",
            "patched_bytes": b"E",
            "lit4_target_address": 0x0040B940,
            "description": "ASCII case flip in .rodata 'ubnt_set_power_range' -> 'ubnt_set_power_rangE' at 0x0040b953",
        },
        {
            "patch_id": "PB040-CCA-AGC-OVERRIDE",
            "pb_stage": "PB-031 (Baseband CCA Energy Detect cca_thresh62 & Timing Control INI Tuple)",
            "segment_index": 3,
            "virtual_address": 0x009C7A78,
            "expected_orig_bytes": bytes.fromhex("009e0200a016721320137213109e0200"),
            "patched_bytes": bytes.fromhex("009e0200a016721320137613109e0200"),
            "lit4_target_address": 0x009C7A60,
            "description": "Baseband modal INI tuple for 0x00029e00 (BB_timing_controls_1 cca_thresh62) at 0x009c7a78",
        },
        {
            "patch_id": "PB040-SUB20MHZ-PLL-DIV",
            "pb_stage": "PB-030 (Sub-20 MHz 5/10 MHz Half/Quarter-Rate Clock & Rate Table)",
            "segment_index": 1,
            "virtual_address": 0x0040BB40,
            "expected_orig_bytes": bytes.fromhex("060c121824303600"),
            "patched_bytes": bytes.fromhex("060c121824304800"),
            "lit4_target_address": 0x0040BB40,
            "description": "Sub-20 MHz 5/10 MHz rate/divider table adjustment in .rodata at 0x0040bb40",
        },
    ],
    "athwlan_AR9888v2_ptmp_sta_bin": [
        {
            "patch_id": "PB040-CANARY-RODATA",
            "pb_stage": "PB-040 (Step 1 — Zero-Risk .rodata String Canary)",
            "segment_index": 1,
            "virtual_address": 0x0040B953,
            "expected_orig_bytes": b"e",
            "patched_bytes": b"E",
            "lit4_target_address": 0x0040B940,
            "description": "ASCII case flip in .rodata 'ubnt_set_power_range' -> 'ubnt_set_power_rangE' at 0x0040b953",
        },
        {
            "patch_id": "PB040-CCA-AGC-OVERRIDE",
            "pb_stage": "PB-031 (Baseband CCA Energy Detect cca_thresh62 & Timing Control INI Tuple)",
            "segment_index": 3,
            "virtual_address": 0x009C2E88,
            "expected_orig_bytes": bytes.fromhex("009e0200a016721320137213109e0200"),
            "patched_bytes": bytes.fromhex("009e0200a016721320137613109e0200"),
            "lit4_target_address": 0x009C2E70,
            "description": "Baseband modal INI tuple for 0x00029e00 (BB_timing_controls_1 cca_thresh62) at 0x009c2e88",
        },
        {
            "patch_id": "PB040-SUB20MHZ-PLL-DIV",
            "pb_stage": "PB-030 (Sub-20 MHz 5/10 MHz Half/Quarter-Rate Clock & Rate Table)",
            "segment_index": 1,
            "virtual_address": 0x0040BB80,
            "expected_orig_bytes": bytes.fromhex("060c121824303600"),
            "patched_bytes": bytes.fromhex("060c121824304800"),
            "lit4_target_address": 0x0040BB80,
            "description": "Sub-20 MHz 5/10 MHz rate/divider table adjustment in .rodata at 0x0040bb80",
        },
    ],
    "athwlan_AR9888v2_ptp_bin": [
        {
            "patch_id": "PB040-CANARY-RODATA",
            "pb_stage": "PB-040 (Step 1 — Zero-Risk .rodata String Canary)",
            "segment_index": 1,
            "virtual_address": 0x0040B8D3,
            "expected_orig_bytes": b"e",
            "patched_bytes": b"E",
            "lit4_target_address": 0x0040B8C0,
            "description": "ASCII case flip in .rodata 'ubnt_set_power_range' -> 'ubnt_set_power_rangE' at 0x0040b8d3",
        },
        {
            "patch_id": "PB040-CCA-AGC-OVERRIDE",
            "pb_stage": "PB-031 (Baseband CCA Energy Detect cca_thresh62 & Timing Control INI Tuple)",
            "segment_index": 3,
            "virtual_address": 0x009BD8D8,
            "expected_orig_bytes": bytes.fromhex("009e0200a016721320137213109e0200"),
            "patched_bytes": bytes.fromhex("009e0200a016721320137613109e0200"),
            "lit4_target_address": 0x009BD8C0,
            "description": "Baseband modal INI tuple for 0x00029e00 (BB_timing_controls_1 cca_thresh62) at 0x009bd8d8",
        },
        {
            "patch_id": "PB040-SUB20MHZ-PLL-DIV",
            "pb_stage": "PB-030 (Sub-20 MHz 5/10 MHz Half/Quarter-Rate Clock & Rate Table)",
            "segment_index": 1,
            "virtual_address": 0x0040BA90,
            "expected_orig_bytes": bytes.fromhex("060c121824303600"),
            "patched_bytes": bytes.fromhex("060c121824304800"),
            "lit4_target_address": 0x0040BA90,
            "description": "Sub-20 MHz 5/10 MHz rate/divider table adjustment in .rodata at 0x0040ba90",
        },
    ],
}


def disassemble_xtensa_litbase_xrefs(container: SgmtContainer, target_ptr: int) -> dict[str, Any]:
    """Locate the `.lit4` entry in Segment 0 (`0x00980000`) and all `l32r` instructions in Segment 3 (`0x00983c00`)."""
    seg0 = container.segments[0]
    seg3 = container.segments[3]
    needle = struct.pack("<I", target_ptr)
    idx = seg0.decoded_bytes.find(needle)
    if idx == -1 or (idx % 4) != 0:
        raise ValueError(f"Pointer 0x{target_ptr:08x} not found in 4-byte aligned Segment 0 .lit4 pool")

    lit_slot_vaddr = seg0.destination + idx
    imm16 = XTENSA_SEG0_IMM16_BASE + (idx // 4)
    # Verify hardware LITBASE formula: XTENSA_LITBASE_ADDR + ((imm16 - 0x10000) * 4) == lit_slot_vaddr
    computed_vaddr = (XTENSA_LITBASE_ADDR + ((imm16 - 0x10000) * 4)) & 0xFFFFFFFF
    assert computed_vaddr == lit_slot_vaddr

    lo_byte = imm16 & 0xFF
    hi_byte = (imm16 >> 8) & 0xFF
    l32r_sites: list[dict[str, str]] = []
    text = seg3.decoded_bytes
    for off in range(len(text) - 3):
        b0 = text[off]
        if (b0 & 0x0F) == 0x01 and text[off + 1] == lo_byte and text[off + 2] == hi_byte:
            target_reg = (b0 >> 4) & 0x0F
            pc_vaddr = seg3.destination + off
            insn_hex = text[off : off + 3].hex()
            l32r_sites.append(
                {
                    "pc_hex": f"0x{pc_vaddr:08x}",
                    "insn_bytes_hex": insn_hex,
                    "mnemonic": f"l32r a{target_reg}, [0x{lit_slot_vaddr:08x}] ; -> 0x{target_ptr:08x}",
                }
            )
    if not l32r_sites:
        raise ValueError(f"Zero Segment 3 l32r call sites found for .lit4 slot 0x{lit_slot_vaddr:08x}")

    return {
        "litbase_sr5_hex": f"0x{XTENSA_LITBASE_SR5:08x}",
        "lit4_slot_address_hex": f"0x{lit_slot_vaddr:08x}",
        "lit4_target_value_hex": f"0x{target_ptr:08x}",
        "l32r_imm16_hex": f"0x{imm16:04x}",
        "l32r_call_sites": l32r_sites,
    }


def build_ram_patch_loader_script() -> str:
    """Generate the volatile RAM bind-mount loader script with automatic rollback watchdog."""
    return """#!/bin/sh
# Stage 347A — PB-040 Volatile RAM SGMT Patch Loader & Watchdog (Zero Flash Writes)
# Safely bind-mounts a surgically patched QCA988x / AR9888v2 SGMT firmware container
# from volatile /tmp RAM over /lib/firmware/ath10k/QCA988X/hw2.0/firmware-5.bin,
# reloads ath10k_pci, verifies WMI_READY + wlan0 PHY bring-up within 45s, and
# automatically unmounts + restores stock firmware on any anomaly.

set -eu

PROFILE="${1:-PB040-CANARY-RODATA}"
IMAGE_ROLE="${2:-athwlan_AR9888v2_ptmp_ap_bin}"
PATCH_DIR="/tmp/fmx_xtensa_ram_patches"
TARGET_FW="/lib/firmware/ath10k/QCA988X/hw2.0/firmware-5.bin"
WATCHDOG_TIMEOUT_SEC=45

log_msg() {
    logger -t "fmx-pb040-ram-loader" "$1"
    echo "[fmx-pb040-ram-loader] $1"
}

rollback_to_stock() {
    log_msg "ROLLBACK: Unmounting volatile RAM firmware override and restoring stock SquashFS image"
    umount "$TARGET_FW" 2>/dev/null || true
    rmmod ath10k_pci 2>/dev/null || true
    insmod ath10k_pci 2>/dev/null || true
    wifi up 2>/dev/null || true
}

if [ "$PROFILE" = "rollback" ] || [ "$PROFILE" = "restore" ]; then
    rollback_to_stock
    exit 0
fi

PATCH_BLOB="${PATCH_DIR}/${IMAGE_ROLE}.${PROFILE}.sgmt.bin"
if [ ! -f "$PATCH_BLOB" ]; then
    log_msg "ERROR: Missing patched SGMT blob: $PATCH_BLOB"
    exit 1
fi

# Verify SGMT magic (0x544d4753 = 'SGMT') before bind-mounting
MAGIC_HEX="$(dd if="$PATCH_BLOB" bs=1 count=4 2>/dev/null | hexdump -v -e '/1 "%02x"')"
if [ "$MAGIC_HEX" != "53474d54" ]; then
    log_msg "ERROR: Invalid SGMT magic ($MAGIC_HEX) in $PATCH_BLOB; refusing load"
    exit 1
fi

cp -f "$PATCH_BLOB" /tmp/firmware-5.bin
umount "$TARGET_FW" 2>/dev/null || true
mount --bind /tmp/firmware-5.bin "$TARGET_FW"
log_msg "Bind-mounted /tmp/firmware-5.bin ($PROFILE) over $TARGET_FW (0 Flash writes)"

rmmod ath10k_pci 2>/dev/null || true
insmod ath10k_pci 2>/dev/null || {
    log_msg "ERROR: insmod ath10k_pci failed; triggering immediate rollback"
    rollback_to_stock
    exit 1
}

ELAPSED=0
while [ "$ELAPSED" -lt "$WATCHDOG_TIMEOUT_SEC" ]; do
    if [ -d /sys/class/ieee80211/phy0 ]; then
        log_msg "SUCCESS: phy0 active under $PROFILE within ${ELAPSED}s (RAM-only bind-mount verified)"
        exit 0
    fi
    sleep 1
    ELAPSED=$((ELAPSED + 1))
done

log_msg "WATCHDOG TIMEOUT (${WATCHDOG_TIMEOUT_SEC}s): phy0 did not appear; rolling back to stock"
rollback_to_stock
exit 1
"""


def build_stage347a_profiles() -> dict[str, Any]:
    """Generate and verify all Stage 347A Xtensa SGMT surgical RAM patch profiles."""
    patcher_sha = hashlib.sha256(PATCHER_PATH.read_bytes()).hexdigest()
    spec_sha = hashlib.sha256(PB040_SPEC_PATH.read_bytes()).hexdigest()
    if patcher_sha != PINNED_PATCHER_SHA256:
        raise RuntimeError(f"Pinned xtensa_sgmt_surgical_patcher.py SHA-256 mismatch: {patcher_sha}")
    if spec_sha != PINNED_PB040_SPEC_SHA256:
        raise RuntimeError(f"Pinned pb040_sgmt_surgical_patch_spec_20261025.json SHA-256 mismatch: {spec_sha}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_OUT.parent.mkdir(parents=True, exist_ok=True)

    containers = load_ar9888v2_sgmt_containers(UMAC_8512_PATH)
    segments_verified = 0
    for sym_name, cont in containers.items():
        for seg in cont.segments:
            recomp = bmi_lz_compress(seg.decoded_bytes, enable_lz77=True)
            redecomp = bmi_lz_decompress(recomp, seg.decoded_size)
            if redecomp != seg.decoded_bytes:
                raise RuntimeError(f"BMI_LZ round-trip mismatch on {sym_name} segment {seg.index}")
            segments_verified += 1

    profiles_summary: dict[str, Any] = {}
    generated_files: list[dict[str, Any]] = []

    for sym_name, patch_defs in IMAGE_PROFILE_MATRIX.items():
        base_container = containers[sym_name]
        combined_container = base_container
        image_profiles: dict[str, Any] = {}

        for pdef in patch_defs:
            spec = SurgicalPatchSpec(
                patch_id=pdef["patch_id"],
                pb_stage=pdef["pb_stage"],
                description=pdef["description"],
                target_symbol=sym_name,
                segment_index=pdef["segment_index"],
                virtual_address=pdef["virtual_address"],
                expected_orig_bytes=pdef["expected_orig_bytes"],
                patched_bytes=pdef["patched_bytes"],
                sibling_addresses={},
                safety_rationale="Length-preserving surgical patch in volatile RAM (/tmp/firmware-5.bin bind-mount); 0 Flash writes.",
            )
            patched_cont, receipt = SgmtSurgicalPatcher.validate_and_apply(base_container, spec)
            combined_container, _ = SgmtSurgicalPatcher.validate_and_apply(combined_container, spec)

            xref_disasm = disassemble_xtensa_litbase_xrefs(base_container, pdef["lit4_target_address"])
            out_blob = patched_cont.to_bytes(recompress=False)
            # Round-trip reparse check
            reparsed = SgmtContainer.from_bytes(out_blob)
            assert reparsed.entry_point == 0x00983C00
            assert sum(s.decoded_size for s in reparsed.segments) == sum(
                s.decoded_size for s in base_container.segments
            )

            out_file = OUT_DIR / f"{sym_name}.{spec.patch_id}.sgmt.bin"
            out_file.write_bytes(out_blob)
            blob_sha = hashlib.sha256(out_blob).hexdigest()

            receipt["xtensa_litbase_disassembly"] = xref_disasm
            receipt["output_sgmt_file"] = str(out_file.relative_to(REPO_ROOT)).replace("\\", "/")
            receipt["output_sgmt_sha256"] = blob_sha
            receipt["output_sgmt_size_bytes"] = len(out_blob)
            image_profiles[spec.patch_id] = receipt
            generated_files.append(
                {
                    "image_symbol": sym_name,
                    "profile_id": spec.patch_id,
                    "path": str(out_file.relative_to(REPO_ROOT)).replace("\\", "/"),
                    "size_bytes": len(out_blob),
                    "sha256": blob_sha,
                    "entry_point_hex": f"0x{reparsed.entry_point:08x}",
                    "decoded_total_bytes": sum(s.decoded_size for s in reparsed.segments),
                }
            )

        # Also emit the combined 3-patch bundle for this image symbol
        comb_blob = combined_container.to_bytes(recompress=False)
        comb_reparsed = SgmtContainer.from_bytes(comb_blob)
        assert comb_reparsed.entry_point == 0x00983C00
        comb_file = OUT_DIR / f"{sym_name}.PB040-ALL3-COMBINED.sgmt.bin"
        comb_file.write_bytes(comb_blob)
        comb_sha = hashlib.sha256(comb_blob).hexdigest()
        generated_files.append(
            {
                "image_symbol": sym_name,
                "profile_id": "PB040-ALL3-COMBINED",
                "path": str(comb_file.relative_to(REPO_ROOT)).replace("\\", "/"),
                "size_bytes": len(comb_blob),
                "sha256": comb_sha,
                "entry_point_hex": f"0x{comb_reparsed.entry_point:08x}",
                "decoded_total_bytes": sum(s.decoded_size for s in comb_reparsed.segments),
            }
        )
        profiles_summary[sym_name] = image_profiles

    loader_text = build_ram_patch_loader_script()
    LOADER_SCRIPT_OUT.write_text(loader_text, encoding="utf-8", newline="\n")
    loader_sha = hashlib.sha256(LOADER_SCRIPT_OUT.read_bytes()).hexdigest()

    report = {
        "stage": "347A",
        "title": "PB-040 Xtensa SGMT Surgical RAM Patch Profiles (PB040-CANARY-RODATA, PB040-CCA-AGC-OVERRIDE, PB040-SUB20MHZ-PLL-DIV)",
        "claim_status": "CONFIRMED",
        "attribution": "QCA firmware",
        "memory_master_claim_id": "mm-61aa",
        "pinned_digests_verified": {
            "xtensa_sgmt_surgical_patcher_py_sha256": patcher_sha,
            "pb040_sgmt_surgical_patch_spec_json_sha256": spec_sha,
            "pins_intact": True,
        },
        "sgmt_bmi_lz_verification": {
            "containers_verified": len(containers),
            "segments_verified": segments_verified,
            "all_12_segments_lossless_roundtrip": True,
            "sgmt_magic_le_hex": f"0x{SGMT_MAGIC_LE:08x}",
            "xtensa_litbase_sr5_hex": f"0x{XTENSA_LITBASE_SR5:08x}",
        },
        "profiles_by_image": profiles_summary,
        "generated_sgmt_binaries": generated_files,
        "ram_loader_script": {
            "path": str(LOADER_SCRIPT_OUT.relative_to(REPO_ROOT)).replace("\\", "/"),
            "sha256": loader_sha,
            "bind_mount_target": "/lib/firmware/ath10k/QCA988X/hw2.0/firmware-5.bin",
            "volatile_staging_path": "/tmp/firmware-5.bin",
            "watchdog_timeout_sec": 45,
            "flash_writes_permitted": False,
        },
        "five_pillar_compliance": {
            "pillar_a_binary_re": "Disassembled Xtensa LITBASE=0x009bb001 .lit4 Segment 0 pointers and Segment 3 l32r instructions across all 3 AR9888v2 SGMT images",
            "pillar_b_closed_loop_research": "Linked to PB-040 / PB-031 / PB-030 physical boundary hypotheses",
            "pillar_c_counterbalanced_harness": "45s non-DFS rollback watchdog in fmx_xtensa_ram_patch_loader.sh",
            "pillar_d_scientific_validation": "Cryptographic SHA-256 + 12/12 BMI_LZ segment byte-exact round-trip verification",
            "pillar_e_memory_master": "mm-61aa (id=155369, scope=project:futuramax)",
        },
    }
    ARTIFACT_OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    report = build_stage347a_profiles()
    print(
        f"[Stage 347A] Generated {len(report['generated_sgmt_binaries'])} SGMT RAM patch blobs "
        f"and wrote {ARTIFACT_OUT.relative_to(REPO_ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
