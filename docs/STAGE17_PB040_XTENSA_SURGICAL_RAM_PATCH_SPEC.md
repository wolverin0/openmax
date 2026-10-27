<!-- doc-head: STAGE17_PB040_XTENSA_SURGICAL_RAM_PATCH_SPEC.md preserved document content -->
<!-- /doc-head -->

# Stage 17 — Ground-Up Physical Boundary (`PB-040`): Surgical Xtensa `SGMT` Re-Packer, `BMI_LZ` Codec & RAM-Only Patch Specification

- **Task ID**: `T-PB-040-XTENSA-SURGICAL-RAM-PATCH-BUILDER`
- **Surgical Patcher Module**: [`firmware/xtensa_sgmt_surgical_patcher.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/firmware/xtensa_sgmt_surgical_patcher.py)
- **Generated Artifact**: [`artifacts/physical_boundary/pb040_sgmt_surgical_patch_spec_20261025.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/physical_boundary/pb040_sgmt_surgical_patch_spec_20261025.json)
- **Test Suite**: [`tests/test_xtensa_sgmt_surgical_patcher.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_xtensa_sgmt_surgical_patcher.py)
- **Execution Mode**: Strictly Offline Deterministic Re-Pack & Verification (`ZERO_LIVE_DEVICE_CONTACT`)

---

## 1. `BMI_LZ` (BCL LZ77 + 7-Bit Varint) State Machine

When `bmi_segmented_file_header.file_flags == 1` (`BMI_SGMTFILE_FLAG_COMPRESS`), each `PAYLOAD` record (`[addr: u32_le, decoded_size: u32_le]`) is compressed using the Basic Compression Library (BCL) LZ77 stream consumed by the QCA988x / `AR9888v2` ROM bootloader (`BMI_LZ_STREAM_START = 13` + `BMI_LZ_DATA = 14`):

1. **Per-Segment Escape Marker (`byte 0`)**:
   - The first byte of the compressed stream is `marker` (chosen by the encoder as the least-frequent byte in the uncompressed segment).
2. **Token Loop (until `len(out) == decoded_size`)**:
   - If `b != marker`: append `b` literally to `out`.
   - If `b == marker` and `next_byte == 0x00`: consume `0x00` and append literal `marker` to `out`.
   - If `b == marker` and `next_byte != 0x00`: decode two 7-bit big-endian continuation varints `(length, distance)` and copy `length` bytes from `out[-distance]` byte-by-byte (permitting overlapping RLE copies when `distance < length`).

### Round-Trip Verification Across All 12 `AR9888v2` Segments (`3` Images $\times$ `4` Segments)

| Target Symbol (`umac.ko` `8.5.12`) | Orig Container Size | Orig Container SHA-256 | Decoded Total | Seg 0 (`0x00980000`) | Seg 1 (`0x0040b000`) | Seg 2 (`.data`) | Seg 3 (`0x00983c00`) | `decompress(compress(seg)) == seg` |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`athwlan_AR9888v2_ptmp_ap_bin`** | `251,681` B | `55e9c94a2f0b466f...` | `309,464` B | `6,496` B | `8,500` B | `0x0040d140`: `10,864` B | `283,604` B | **`100%` (`4/4` segments)** |
| **`athwlan_AR9888v2_ptmp_sta_bin`** | `234,072` B | `714ca44a2a0b4a9a...` | `289,752` B | `6,232` B | `8,492` B | `0x0040d130`: `10,864` B | `264,164` B | **`100%` (`4/4` segments)** |
| **`athwlan_AR9888v2_ptp_bin`** | `213,701` B | `8e2009b29a2c4a9c...` | `266,072` B | `5,876` B | `7,104` B | `0x0040cbc0`: `10,864` B | `242,228` B | **`100%` (`4/4` segments)** |

---

## 2. Why Exact Segment Byte-Length Preservation Is Mandatory on Xtensa

The QCA988x target CPU uses a windowed little-endian Xtensa core (`CALL8`, `ENTRY`, `RET.N`, `L32R`, `J`, `BNEZ`). In Xtensa machine code:
- **`L32R` (Load 32-bit PC-Relative Literal)** computes its target address as `((PC + 3) & ~3) + (sign_extend(imm16) << 2)`, referencing literal pools embedded directly prior to functions inside Segment 0 (`0x00980000`) and Segment 3 (`0x00983c00`).
- **`CALL8` / `J` / Conditional Branches** use PC-relative offsets.
- Inserting or deleting even a single byte inside any decoded segment would shift all subsequent functions and literal pools, corrupting every PC-relative `L32R` load and `CALL8` target across the `283,604`-byte `.text` segment.
- [`SgmtSurgicalPatcher`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/firmware/xtensa_sgmt_surgical_patcher.py) enforces `len(expected_orig_bytes) == len(patched_bytes)` and `len(patched_seg) == len(orig_seg)`, guaranteeing **zero `L32R` literal-pool or branch-offset drift** while allowing `BMI_LZ` compressed sizes (`len(recompressed)`) to vary freely because the `SGMT` record header stores the uncompressed `decoded_size` (`length`).

---

## 3. Concrete Surgical Patch Specifications (`PB-040`, `PB-050`, `PB-031`, `PB-030`)

| Patch ID | Stage | Segment & Virtual Address (`ptmp_ap`) | Relative Offset | Orig Bytes (Hex) | Patched Bytes (Hex) | Purpose & Sibling Addresses (`ptmp_sta` / `ptp`) |
| :--- | :---: | :--- | :---: | :--- | :--- | :--- |
| **`PB040-CANARY-RODATA`** | `PB-040` | Seg 1 (`0x0040b000`) @ **`0x0040b953`** | `+0x000953` (`2,387`) | `65` (`'e'`) | `45` (`'E'`) | Flips `"ubnt_set_power_range"` $\rightarrow$ `"ubnt_set_power_rangE"` (`0x0040b940` on `ap`/`sta`, `0x0040b8c0` on `ptp`) to verify RAM-only `SGMT` acceptance with zero code/register change. |
| **`PB040-WMI-DISPATCH-0x9064`** | `PB-050` | Seg 2 (`0x0040d140`) @ **`0x0040fb54`** | `+0x002a14` (`10,772`) | `64900000` (`0x00009064`) | `70900000` (`0x00009070`) | Retargets WMI poll tunnel opcode in DRAM `.data` (`0x0040fb44` on `sta`, `0x0040f5d4` on `ptp`), feeding the 51-entry `.text` jump table at `0x009b2037` (case `0x17` at `0x009b207c` $\rightarrow$ `0x009b2578` $\rightarrow$ `0x009b5c02`). |
| **`PB040-CCA-AGC-OVERRIDE`** | `PB-031` | Seg 3 (`0x00983c00`) @ **`0x009c7a78`** | `+0x043e78` (`278,136`) | `009e0200 a0167213 20137213 109e0200` | `009e0200 a0167213 20137613 109e0200` | Modifies the Xtensa `l32r` literal-pool word for `bb_lc_reg.h` `0x00029e00` (`BB_timing_controls_1` / `cca_thresh62`) & `0x00029e10` (`0x009c2e88` on `sta`, `0x009bd8d8` on `ptp`). |
| **`PB040-SUB20MHZ-PLL-DIV`** | `PB-030` | Seg 1 (`0x0040b000`) @ **`0x0040bb40`** | `+0x000b40` (`2,880`) | `060c121824303600` | `060c121824304800` | Surgical in-place edit of the `HALF_RATE` (`10 MHz`) / `QUARTER_RATE` (`5 MHz`) sub-20 MHz rate/divider table (`0x0040bb80` on `sta`, `0x0040ba90` on `ptp`), paired with the 20 MHz OFDM table at `0x0040b688`. |

---

## 4. RAM-Only Sacrificial Bench Test Procedure (Zero Flash Writes)

1. **Stage in Volatile RAM (`/tmp`)**:
   - Copy the re-packed `SGMT` container (or `/tmp/firmware-5.bin` / `/tmp/umac_patched.ko` containing `PB040-CANARY-RODATA`) to `/tmp/pb040/` on the isolated bench radio.
2. **Bind-Mount or Module Reload (Zero MTD / Flash Contact)**:
   - On OpenWrt: `mount --bind /tmp/pb040/firmware-5.bin /lib/firmware/ath10k/QCA988X/hw2.0/firmware-5.bin && rmmod ath10k_pci && insmod ath10k_pci`.
   - On stock airOS lab harness: `rmmod ubnt_poll_host ath_dev umac && insmod /tmp/pb040/umac_patched.ko`.
3. **Verify Target Boot Handshake**:
   - Confirm `ath10k_bmi_fast_download` (`BMI_LZ_STREAM_START` + `BMI_LZ_DATA`) + `ath10k_bmi_execute(0x00983c00)` + `WMI_SERVICE_READY_EVENTID` + `WMI_READY_EVENTID` succeed without target panic (`hi_failure_state` at `0x00400800`).
4. **Instant Rollback**:
   - `umount /lib/firmware/ath10k/QCA988X/hw2.0/firmware-5.bin` or power-cycle immediately restores the unmodified SquashFS image.
