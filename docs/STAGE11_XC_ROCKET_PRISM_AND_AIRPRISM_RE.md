# Stage 11A — Static Reverse Engineering of Ubiquiti `XC` (`Rocket Prism 5AC Gen2` & `PrismStation 5AC`) & AirPrism Active RF Filter Architecture

**Date**: 2026-10-18 (Updated with `gpt-6-astra` `xhigh` Adversarial Audit Remediations `F01`, `F04–F07`, `F14`)  
**Status**: **Static Reverse-Engineering Complete (`CONFIRMED` ELF/Disassembly Evidence; Live Bench Qualification Queued on `Rocket Prism 5AC Gen2`)**  
**Analyzed Firmware Images**:
- `XC-8.7.25.260730.bin` (`10,290,738` bytes, `SHA256: b304352f2ab27fa73e55a5646f389cd92fd50171f27750f683fc7620755c828f`)
- `XC-8.7.4-cs.210415.bin` (`9,745,250` bytes, `SHA256: fb4f1dd44e9998d44f212df0556187d0d4e5082e5a922d449bc259180200b712`)
- **Reproducible Audit Evidence**: [`artifacts/adversarial_review_stage10_11/`](../artifacts/adversarial_review_stage10_11/) (`xc_boards.json`, `prism_table.json`, `patch_sites.json`, `selected_disassembly.json`)

---

## 1. Executive Summary & Epistemic Status

1. **Firmware Container & Flash Layout (`CONFIRMED` Static)**:
   - `XC-8.7.25.260730.bin` uses the `UBNT` `FW6` container format (`u-boot`, `kernel`, `rootfs`) targeting a **16 MB SPI NOR flash** (`mx25l12805d`, 64 KB erase sectors):
     - `PARTu-boot`: offset `0x00000000`, size `196,380` bytes (allocated `256 KB` in `mtd0`).
     - `PARTkernel`: offset `0x00040000`, size `1,046,422` bytes (LZMA-compressed `vmlinux` `2.6.32.68`, raw size `3,200,828` bytes, entry `0x80002000`).
     - `PARTrootfs`: offset `0x00140000`, size `9,044,699` bytes (SquashFS 4.0 LZMA).
2. **`ubnthal.ko` (`465,360` Bytes) Hardware Matrix (`CONFIRMED` Static — `F04` Remediated)**:
   - The `XC` board table resides in `ubnthal.ko` at `.data + 0x570` with **34 records of `12,000` bytes each** (not `.rodata` 4,016-byte records).
   - Within each `12,000`-byte board record:
     - `board.sysid` (`uint16`) is at `+0x2d1c`.
     - `radio_count` (`uint8`) is at `+0xcc` (verified via `ubnthal_get_radios_count`).
     - Per-radio descriptors start at `+0xf6c` with a **`3,780`-byte stride** (`ubnthal_get_radio_bus`), where `caps` (`uint32`) is at `+0xf6c + idx * 3780` and `hsr_param` (`uint32`) is at `+0xf8c + idx * 3780`.
   - **`Rocket Prism 5AC Gen2` (`RP-5AC-Gen2`, `sysid = 0xe7e7` and `0xe7e9`)** and **`PrismStation 5AC` (`PS-5AC`, `sysid = 0xe7e6` and `0xe7e8`)** all declare `radio_count = 2`, `wifi0 caps = 0xfce00814` (both **bit 30 `prism`** and **bit 28 `hsr`** enabled), **`hsr_param = 31`**, and `wifi1 caps = 0x0c` (`bus_id = 0` AHB).
3. **AirPrism Stage-1 / Stage-2 GPIO Band-Edge Selector (`CONFIRMED` Static — `F05` Remediated)**:
   - In `umac.ko` (`2,358,768` bytes), `ubnt_prism_hook` (`.text + 0xac874`) calls helper `.text + 0xabeb0`, which tests the **full occupied channel interval** (`lower_edge = center - width/2`, `upper_edge = center + width/2`, and `width <= max_width`) against a **6-entry table of 44-byte structs** (`.data` in `umac.ko`, extracted in [`prism_table.json`](../artifacts/adversarial_review_stage10_11/prism_table.json)):
     - **Stage 1** drives **`GPIO 15` and `GPIO 16`** via `gpio_line_config` / `gpio_line_set`.
     - **Stage 2** drives **`GPIO 13` and `GPIO 14`** via `gpio_line_config` / `gpio_line_set`.
4. **`hsr` (`hsr_param = 31`) Capability Query & Remaining Bench Trace (`CONFIRMED` Static / `UNKNOWN` Transport — `F06` Remediated)**:
   - In `umac.ko`, `.text + 0xbbf64` calls `ubnthal_get_radio_cap(..., "hsr")` (using string literal `.rodata + 0x15890`) and stores the returned `hsr_param` (`31` on `RP-5AC-Gen2` / `PS-5AC`, `31`/`43` on `R5AC-PTMP`, `171` on `R5AC-PTP`) at driver state offset **`+0x1e8c0`**.
   - *(Correction from Adversarial Audit `F06`: the instructions at `.text + 0x8cb4c` decode `board.sysid` with 4-byte XOR key `81 93 e0 c4`, not `hsr` GPIO bit-banging. The exact hardware consumer of `+0x1e8c0` is marked `UNKNOWN` offline and queued as Check 1 on the physical `Rocket Prism 5AC Gen2` bench unit.)*
5. **Spectral Filter Interrupt (`ath_spectral_filter_init` — `CONFIRMED` Static — `F07`)**:
   - In `ath_dev.ko`, `ath_spectral_filter_init` (`.text + 0x27c00`) configures **`GPIO 21`** and requests **`IRQ 64`** (`ath-spectral-filter`, handler at `.text + 0x27be0`). Exact polarity, hardware routing, and FFT blanking timing on `0xe7e9` will be measured on the bench unit.
6. **Stock `XC.v8.7.25` `ubnt_poll_host.ko` Parity & Relocation-Safe Patch (`CONFIRMED` Static — `F01`, `S01`)**:
   - `XC.v8.7.25`'s `ubnt_poll_host.ko` (`189,880` bytes, `MD5: 5b26b076967befe129f669096539ae21`) is byte-identical in the 96-byte neighborhoods around all 3 hybrid patch sites (`30784`, `31816`, `41976`) and shares the exact same `.rel.text` relocation index (`idx 1192`, `file offset 168536`) as `WA.v8.7.25`.
   - Applying the **4-site relocation-safe patch** (`S1 = 30784`, `S_panic = 31816`, `S_ret = 41976`, `R1 = 168536`) produces `MD5: 7b490ac4d9573dab010b5f4fb95c3765` on `XC.v8.7.25` (and `e46cb619a0baa0384a64f4fc67220806` on `XC.v8.7.4-cs`).

---

## 2. Complete 34-Entry `XC` Board Matrix (`ubnthal.ko` `.data + 0x570`, `12,000`-Byte Stride)

Extracted directly from `xc_8725_rootfs/lib/modules/2.6.32.68/ubnthal.ko` (`465,360` bytes) into [`artifacts/adversarial_review_stage10_11/xc_boards.json`](../artifacts/adversarial_review_stage10_11/xc_boards.json):

| Index(es) | `sysid` | Model Code | Marketing Name | `radio_count` (`+0xcc`) | `wifi0` (`bus_id=1`) `caps` | `prism` (Bit 30) | `hsr` (Bit 28) | `hsr_param` (`+0xf8c`) | `wifi1` (`bus_id=0`) `caps` |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `0..2` | `0xe1f5` | `R5AC-Lite` | Rocket 5AC Lite | `2` | `0xace00814` | `0` | `0` | `0` | `0x14` |
| `3` | `0xe1f5` | `R5AC-Lite` | Rocket 5AC Lite | `1` | `0xace00814` | `0` | `0` | `0` | `-` |
| `4..5` | `0xe3d5` | `PBE-5AC-500-ISO` | PowerBeam 5AC 500 ISO | `2` | `0xace00814` | `0` | `0` | `0` | `0x14` |
| `6..7` | `0xe3d5` | `PBE-5AC-500` | PowerBeam 5AC 500 | `2` | `0xace00814` | `0` | `0` | `0` | `0x14` |
| `8..9` | `0xe3d5` | `PBE-5AC-500` | PowerBeam 5AC 500 | `1` | `0xace00814` | `0` | `0` | `0` | `-` |
| `10` | `0xe4f5` | `NBE-5AC-19` | NanoBeam 5AC 19 | `2` | `0xace00814` | `0` | `0` | `0` | `0x14` |
| `11` | `0xe3f5` | `R5AC-PTP` | Rocket 5AC PTP | `2` | `0xbce00814` | `0` | **`1`** | **`171`** | `0x14` |
| `12` | `0xe3f5` | `R5AC-PTMP` | Rocket 5AC PTMP (BOM A) | `2` | `0xbee00814` | `0` | **`1`** | **`31`** | `0x14` |
| `13` | `0xe3f5` | `R5AC-PTMP` | Rocket 5AC PTMP (BOM B) | `2` | `0xbee00814` | `0` | **`1`** | **`43`** | `0x14` |
| `14..16` | `0xe5f5` | `PBE-5AC-620` | PowerBeam 5AC 620 | `2` | `0xace00814` | `0` | `0` | `0` | `0x14` |
| `17..18` | `0xe7e5` | `R5AC-PRISM` | Rocket 5AC Prism (Gen1) | `2` | `0xfce00814` | **`1`** | **`1`** | **`31`** | `0x14` |
| `19` | `0xe3d7` | `NBE-5AC-Gen2` | NanoBeam 5AC Gen2 | `2` | `0xace00814` | `0` | `0` | `0` | `0x0c` |
| `20` | `0xe3d8` | `NS-5ACL` | NanoStation 5AC loco (`XC`) | `2` | `0xace00814` | `0` | `0` | `0` | `0x0c` |
| `21..23` | `0xe7e6` | `PS-5AC` | PrismStation 5AC | `2` | `0xfce00814` | **`1`** | **`1`** | **`31`** | `0x0c` |
| `24` | `0xe7e8` | `PS-5AC` | PrismStation 5AC | `2` | `0xfce00814` | **`1`** | **`1`** | **`31`** | `0x0c` |
| `25..28` | `0xe7e7` | `RP-5AC-Gen2` | **Rocket Prism 5AC Gen2** | `2` | `0xfce00814` | **`1`** | **`1`** | **`31`** | `0x0c` |
| `29..31` | **`0xe7e9`** | **`RP-5AC-Gen2`** | **Rocket Prism 5AC Gen2** | **`2`** | **`0xfce00814`** | **`1`** | **`1`** | **`31`** | **`0x0c`** |
| `32..33` | `0xdc97` | `Prism-AP` | Prism AP | `2` | `0xfce00814` | **`1`** | **`1`** | **`31`** | `0x0c` |

---

## 3. Exact `umac.ko:ubnt_prism_hook` Band-Edge Selector (`GPIO 13..16`)

In `umac.ko` (`2,358,768` bytes), `ubnt_prism_hook` at `.text + 0xac874` computes the **lower channel edge** (`center_mhz - width_mhz / 2`) and **upper channel edge** (`center_mhz + width_mhz / 2`) and calls `.text + 0xabeb0` twice (`requested_stage = 1`, then `requested_stage = 2`).

For each stage, `.text + 0xabeb0` scans the **6-entry, 44-byte-per-entry table** in original order and selects the first entry satisfying **all four conditions**:
```c
entry.stage == requested_stage &&
lower_channel_edge_mhz >= entry.start_mhz &&
upper_channel_edge_mhz <= entry.end_mhz &&
channel_width_mhz <= entry.max_width_mhz
```

### Original 6-Entry `prism` Table (`prism_table.json`)

| Entry # | `stage` | `start_mhz` | `end_mhz` | `gpio_mask` | `gpio_val` | `GPIO 15` | `GPIO 16` | `GPIO 13` | `GPIO 14` | `max_width_mhz` | Role |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **0** | `1` | `5150` | `5250` | `0x18000` (`98304`) | `0x18000` (`98304`) | `1` | `1` | `0` | `0` | `160 MHz` | Stage-1 Low Band (`U-NII-1`) |
| **1** | `1` | `5470` | `5860` | `0x18000` (`98304`) | `0x08000` (`32768`) | `1` | `0` | `0` | `0` | `50 MHz` | Stage-1 High Band Narrow (`<= 50 MHz`) |
| **2** | `2` | `5200` | `5300` | `0x06000` (`24576`) | `0x02000` (`8192`) | `0` | `0` | `1` | `0` | `160 MHz` | Stage-2 Low-Mid Band (`5200..5300`) |
| **3** | `2` | `5725` | `5860` | `0x06000` (`24576`) | `0x04000` (`16384`) | `0` | `0` | `0` | `1` | `160 MHz` | Stage-2 Upper Band (`U-NII-3`) |
| **4** | `1` | `3000` | `6200` | `0x18000` (`98304`) | `0x10000` (`65536`) | `0` | `1` | `0` | `0` | `160 MHz` | Stage-1 Wideband Fallback (`> 50 MHz` or `U-NII-2A`) |
| **5** | `2` | `3000` | `6200` | `0x06000` (`24576`) | `0x06000` (`24576`) | `0` | `0` | `1` | `1` | `160 MHz` | Stage-2 Wideband Fallback |

* **Why Band-Edge Checking Matters (`F05`)**: If a channel is centered at `5240 MHz` with `width = 80 MHz`, its occupied edges are `5200..5280 MHz`. Because `5280 > 5250`, Entry #0 (`5150..5250`) does **not** match Stage 1; the selector falls through to Entry #4 (`Stage-1 Wideband Fallback`, `GPIO 15=0, GPIO 16=1`) so the narrow `5150..5250` filter does not clip the upper `30 MHz` of the `80 MHz` signal!

---

## 4. Two-Track Bench Execution Plan for the Operator's `Rocket Prism 5AC Gen2`

When the operator connects the physical **`Rocket Prism 5AC Gen2` (`sysid = 0xe7e9`)** on the bench:

### Track 1 (Immediate, Low-Risk) — Stock `XC.v8.7.25` Hybrid Mode + Live `hsr` Consumer Trace
1. **Verify Identity & Full Partition Backups**:
   - Confirm `board.sysid=0xe7e9`, `XC.v8.7.25`, and back up `mtd0` (`u-boot`), `mtd1` (`u-boot-env`), `mtd4` (`cfg`), and `mtd5` (`EEPROM/ART`).
2. **Trace Live `hsr_param = 31` (`+0x1e8c0`) & `GPIO 13..16 / 21` Behavior Across Channel Changes**:
   - Observe `dmesg`, `/proc/interrupts` (`IRQ 64` `ath-spectral-filter`), GPIO states (`0xb8040000` `GPIO_OE`/`GPIO_OUT`), and the consumer of `umac.ko` offset `+0x1e8c0` when switching channels (`5180`, `5240`, `5500`, `5785 MHz`) and widths (`20`, `40`, `80 MHz`) on stock `XC.v8.7.25`.
3. **Test Relocation-Safe Hybrid Mode (`MD5: 7b490ac4d9573dab010b5f4fb95c3765`)**:
   - Apply the 4-site relocation-safe `/tmp/uph.ko` patch in RAM while retaining stock `umac.ko` and `ath_dev.ko` so AirPrism (`prism` + `hsr`) stays 100% controlled by Ubiquiti's stock driver, and benchmark throughput, adjacent-channel rejection, and loaded latency against our bench CPEs.

### Track 2 (Conditional on Track 1 `hsr` Trace) — OpenWrt `ath79` Support
- Only after Track 1 identifies the exact runtime consumer of `hsr_param = 31` (`+0x1e8c0`) and measures stock AirPrism adjacent-channel rejection will we evaluate an `initramfs` OpenWrt test image incorporating the exact 6-entry band-edge `prism` selector and `hsr` driver.
