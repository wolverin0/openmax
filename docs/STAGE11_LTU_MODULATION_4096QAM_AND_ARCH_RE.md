# Stage 11B — Static Reverse Engineering of Ubiquiti `LTU` (`aflturocket-2.4.2` & `afltu-2.4.2`): Dual-SoC SDR Architecture, `4096-QAM` (`12X`) Code Paths & `OFDMA` Subband Hooks

**Date**: 2026-10-18 (Updated with `gpt-6-astra` `xhigh` Adversarial Audit Remediations `F08–F11`, `F13–F14`)  
**Status**: **Static Reverse-Engineering Complete (`CONFIRMED` Binary/DTB Evidence; Live RF Bench Qualification Queued on `LTU-Lite` / `LTU-Rocket`)**  
**Analyzed Firmware Images**:
- `aflturocket-2.4.2.261009.bin` (`38,918,528` bytes, `SHA256: 0b731cfca2d8be60072a60b6a64c22e36fb8d67977234aa1578042254db75a40`)
- `afltu-2.4.2.261009.bin` (`24,366,210` bytes, `SHA256: 13fa5f9de7a86a17a86be7c5e412008ab37cf459b842b621cf77efdc974e6c98`)
- **Reproducible Audit Evidence**: [`artifacts/adversarial_review_stage10_11/`](../artifacts/adversarial_review_stage10_11/) (`containers.json`, `dtb_properties.json`, `selected_disassembly.json`)

---

## 1. Executive Summary & Epistemic Status

1. **Software-Defined Radio (`AD9361`) + Dual-SoC Architecture (`CONFIRMED` Static)**:
   - Both `LTU-Rocket` (`AME SoC 3 LTU-Rocket Board`) and `LTU-Lite/LR/Pro` (`AME SoC 3 LTU Board`) run Linux **`3.14.65`** on a custom Ubiquiti **`amesoc3`** dual-core ARM Cortex-A9 SoC (`256 MB` RAM, GIC at `0xffffd000`) coupled over a **`40 MHz` SPI bus** (`spi-max-frequency = 0x02625a00`) to an Analog Devices **`AD9361` 2x2 MIMO Agile RF Transceiver** (`70 MHz – 6.0 GHz`, independent TX/RX PLL synthesizers, programmable `200 kHz – 56 MHz` channel bandwidths).
   - **Why `LTU-Rocket` (`aflturocket`) is `38.9 MB` vs `24.3 MB` (`afltu`)**: `LTU-Rocket` includes a second independent SoC — an **Intel / Altera Arria 10 SoC FPGA** (`altr,socfpga-arria10`, dual Cortex-A9 + `128 MB` RAM) running its own Linux **`4.14.0 SMP`** OS + a **`5,490,084`-byte (`5.49 MB`) `.rbf` FPGA bitstream** (`part05_fpga.bin`).
2. **`4096-QAM` (`12X`, Rate Code `31` / `0x1f`) Implementation vs Hardware Guards (`CONFIRMED` Static Paths / `UNKNOWN` Live PtMP RF — `F09` & `F10` Remediated)**:
   - Firmware `v2.4.2` contains real `4096-QAM` (`LDPC 5/6`, internal code `31` / `0x1f`, RS code `30` / `0x1e`) tables, configuration handlers, and RF driver routines:
     - In `ubntbox` (`VA 0x40284`, table at `VA 0xd4b28` / file offset `0xccb28`), `wireless.1.rate.mcs = 0..5` maps directly to LDPC ceiling codes **`[7, 11, 15, 19, 23, 31]`** (`QPSK` through `4096-QAM`), with no `ptpmode` restriction in that parser block.
     - In `ame_core.ko` (`3,318,764` bytes on Rocket, `MD5: 92d1e1e3babacf57f291e7af774892c3`; `MD5: 12ba72a3fb0875439e05be32dcc1d630` on CPE), `AME_Scheduler_AutoMCS_GetPtmpDLCeiling` (`.text + 0x735ac`) accepts `31` (`0x1f`) as a valid PtMP downlink ceiling.
     - `autoMcsUseSisoTbl` and `autoMcsOthersTbl` include `(31, 1)`, and `autoMCS_get_rate_table` (`.text + 0x156098`) selects 7-entry MIMO rate tables containing `31`.
     - `bbp_rf_set_super4096` (`.text + 0x1766bc`) invokes `ame_rfic_req(0x56, ...)`, and rate-adaptation thresholds `startThrd_4096 = 97` / `stayThrd_4096 = 90` are compiled in.
   - **Kernel Hardware Guards to Verify on the Bench (`F09`)**:
     - `ame_bbp_set_Param_mcs` (`.text + 0x194648`) calls **`ame_check_hw_NoLDPC`** on the code path covering rate `31` and rejects unsupported hardware states; TX power backoff also branches on `system_config + 0x20` and `+0x10`.
     - Therefore, while `4096-QAM` is disabled in the PtMP WebUI (`disabled: t` in `getAvailableDataRates`) and Lua validator (`ltuWireless.lua`) and accepted by `ubntconf` (`wireless.1.rate.mcs=5`), **physical bench testing on `LTU-Lite` / `LTU-Rocket` is required** to verify whether `ame_check_hw_NoLDPC`, peer capability negotiation, and the FPGA allow `4096-QAM` constellations over the air in PtMP/PtP modes.
3. **`OFDMA` Subband Hooks & Numeric Mask Parser (`CONFIRMED` Static / `UNKNOWN` Live RF — `F11` Remediated)**:
   - `ame_core.ko` and `ame_dev.ko` include `ame_bbp_set_ofdma_en`, `sched_ofdma_available` (`.text + 0x63f74`), hardware capability check `ame_check_hw_NoOFDMA` (`.text + 0x5708`), and an 8-bit subband mask setter `ame_bbp_set_ofdma_subbands` (`.text + 0x1979c4` $\to$ `bbp_mrx_band_ofdma_subbands` at `.text + 0x145704`, writing bits `12..19` of a BBP MRX register).
   - **Critical Input Format (`F11`)**: `ame_dev.ko:ofdma_subbands_store` (`.text + 0x1154c`) parses its input via **`simple_strtol(..., 0)`** and truncates to a single unsigned byte (`uxtb` at `0x11568`). Therefore, you **must pass a numeric byte (`255` or `0xff` for all 8 bits)** — passing the string `"11111111"` is parsed as decimal `11,111,111` (`0xa98ac7`) and truncated to `0xc7`!

---

## 2. Exact `AMEIMG` Container Parts & DTB NAND Partition Map (`F08` Remediated)

### A. `AMEIMG` Container Parts (`containers.json` — 0 Trailing Bytes, All 15 Payload MD5s Verified)

| Part Index | Part Name | `aflturocket-2.4.2` Size (Bytes) | `aflturocket-2.4.2` Payload MD5 | `afltu-2.4.2` Size (Bytes) | `afltu-2.4.2` Payload MD5 | Target Subsystem |
| :---: | :--- | ---: | :---: | ---: | :---: | :--- |
| `0` | `spl` | `524,288` | `647ff21a6e82346968255213008fa69d` | `524,288` | `9ec57f3d5397dc5cf4345a468b4475bf` | Primary `amesoc3` SPL |
| `1` | `uboot` | `318,096` | `7b7999c4e5eb15bb4cf61ec33bf96bf7` | `319,344` | `f82f4cf4a5460be21c764f617087b599` | Primary `amesoc3` U-Boot |
| `2` | `dtb` | `6,605` | `f6eb728557c4b7614e3555df9c5f206f` | `6,554` | `63cc45a9e91b6cc9d5f94a9121a97fb1` | Primary `amesoc3` Device Tree |
| `3` | `kernel` | `3,330,408` | `c852580e1664026b4b38be3b5bb2531c` | `3,330,408` | `c852580e1664026b4b38be3b5bb2531c` | Primary Linux `3.14.65` uImage |
| `4` | `rootfs` | `19,398,656` | `348573977514e0952ab672e01fb6681c` | `20,185,088` | `56b5b44cf224ee44792ec85fb7785966` | Primary SquashFS RootFS (`xz`) |
| `5` | `fpga` | `5,490,084` | `0787e883948ee90218a9163274bf1900` | *(Not present)* | `-` | Arria 10 `.rbf` FPGA Bitstream |
| `6` | `socfpga-uboot` | `848,796` | `4c99260a957369168bf6fd83a476bf69` | *(Not present)* | `-` | Arria 10 HPS U-Boot |
| `7` | `socfpga-dtb` | `13,865` | `c4f8f5bc48a944ec2c4a9c6d415206bc` | *(Not present)* | `-` | Arria 10 HPS Device Tree |
| `8` | `socfpga-kernel` | `1,978,944` | `00d5c89e4b9044be15035163cb5b0245` | *(Not present)* | `-` | Arria 10 HPS Linux `4.14.0 SMP` |
| `9` | `socfpga-rootfs` | `7,007,744` | `5c23b8db02719d2b574d0217b4fd4999` | *(Not present)* | `-` | Arria 10 HPS SquashFS RootFS |

### B. Primary `amesoc3` NAND Flash Partition Map (`dtb_properties.json` — Static DTB Evidence)

> [!CAUTION]
> **Critical Partition Boundary (`F08`)**: In the actual `amesoc3` Device Tree (`part02_dtb.bin`), `uboot` occupies `0x00140000..0x00240000` (`1 MB`), **`EEPROM` is at `0x00240000`**, and **`cfg` is at `0x00300000`**. Never write to `0x00160000` or `0x00180000`, which fall inside `uboot`!

| Partition Label | Start Offset | Length | Size | Notes |
| :--- | :---: | :---: | :---: | :--- |
| `spl` | `0x00000000` | `0x00080000` | `512 KB` | Primary preloader (Protected) |
| `uboot_env0` | `0x00080000` | `0x00060000` | `384 KB` | Primary U-Boot env |
| `uboot_env1` | `0x000e0000` | `0x00060000` | `384 KB` | Redundant U-Boot env |
| `uboot` | `0x00140000` | `0x00100000` | `1,024 KB` | Primary U-Boot (Protected) |
| **`EEPROM`** | **`0x00240000`** | **`0x000c0000`** | **`768 KB`** | **RF Calibration / Factory Data (Protected)** |
| **`cfg`** | **`0x00300000`** | **`0x000c0000`** | **`768 KB`** | **Persistent `/etc/persistent` (`cfgmtd`)** |
| `dtb0` | `0x003c0000` | `0x00060000` | `384 KB` | Bank 0 Device Tree |
| `kernel0` | `0x00420000` | `0x00500000` | `5,120 KB` | Bank 0 Kernel |
| `rootfs0` | `0x00920000` | `0x02800000` | `40,960 KB` | Bank 0 RootFS |
| `dtb1` | `0x03120000` | `0x00060000` | `384 KB` | Bank 1 Device Tree |
| `kernel1` | `0x03180000` | `0x00500000` | `5,120 KB` | Bank 1 Kernel |
| `rootfs1` | `0x03680000` | `0x02800000` | `40,960 KB` | Bank 1 RootFS |
| `reserved` | `0x05e80000` | `0x02180000` | `34,304 KB` | Reserved NAND tail |

---

## 3. Corrected `LTU` Modulation & Rate-Code Table (`F10` Remediated)

Verified across `ubntbox` (`VA 0xd4b28`), `/usr/bin/ame_adj.sh`, and WebUI `getAvailableDataRates`:

| `wireless.1.rate.mcs` | WebUI `getAvailableDataRates` Key | Nominal UI Label | Modulation | Internal LDPC Code (`ubntbox` / `ame_adj.sh`) | Internal RS Code (`ame_adj.sh`) | PtMP WebUI Status |
| :---: | :---: | :---: | :--- | :---: | :---: | :--- |
| **`0`** | `0@0` / `0@1` | `1X` (SFBC) / `2X` (MIMO) | `QPSK` | **`7` (`0x07`)** | `25` (`0x19`) | Enabled |
| **`1`** | `1@1` | `4X` | `16-QAM` | **`11` (`0x0b`)** | `26` (`0x1a`) | Enabled |
| **`2`** | `2@1` | `6X` | `64-QAM` | **`15` (`0x0f`)** | `27` (`0x1b`) | Enabled |
| **`3`** | `3@1` | `8X` | `256-QAM` | **`19` (`0x13`)** | `28` (`0x1c`) | Enabled |
| **`4`** | `4@1` | `10X` | `1024-QAM` | **`23` (`0x17`)** | `29` (`0x1d`) | Enabled (Default Max) |
| **`5`** | `5@1` | **`12X`** | **`4096-QAM`** | **`31` (`0x1f`)** | `30` (`0x1e`) | **`disabled: t` when `isPtmp()`** |

---

## 4. Non-Destructive Live Bench Test Plan for `LTU-Lite` & `LTU-Rocket` (`F09–F11`, `F13` Remediated)

When the operator connects the **`LTU-Lite`** (and **`LTU-Rocket`**) on the bench, all tests will be performed **strictly in RAM / sysfs first (zero flash writes)** to answer the exact hardware/FPGA questions identified by the adversarial audit:

1. **Step 1 — Read-Only Hardware & Capability Bit Inspection**:
   - Inspect `dmesg`, `/proc/mtd` (verifying match against the DTB NAND map), `/sys/class/ame/ame_ctrl_dev/*`, and check the live state of the hardware capability bits queried by `ame_check_hw_NoLDPC` and `ame_check_hw_NoOFDMA`.
2. **Step 2 — Distinguish `autoMcsCeiling` (`31`) vs Fixed/Adjusted MCS (`adj_mcs` / `cpe_mcs`)**:
   - Test raising the automatic ceiling in sysfs:
     ```sh
     echo 31 > /sys/class/ame/ame_ctrl_dev/autoMcsCeiling
     ```
   - And separately test per-CPE / link adjusted rate via `/usr/bin/ame_adj.sh`:
     - `ame_adj.sh mcs 4096l 0` (writes `adj_mcs`)
     - `ame_adj.sh cpe_mcs <cpe_id> 4096l 0` (writes `/sys/class/ame/ame_ctrl_dev/cpe_mcs`)
     - `ame_adj.sh mix_mcs <cpe_id> <q_id> <portion> <sub_mcs> <sub_mimo> [offset]` (writes `adj_mix_mcs`)
   - Measure whether the **actual transmitted/received modulation constellation** (`status.cgi` / `ame-debug-sched` / EVM / LDPC BLER / PER) reaches `4096-QAM` (`31`) across `20 / 40 / 50 MHz` widths on a high-SNR bench link, or if `ame_check_hw_NoLDPC` / FPGA bitstreams clamp it.
3. **Step 3 — Test `OFDMA` Subband Hooks with Proper Numeric Mask (`0..255`)**:
   - Test `ofdma_en` and `ofdma_subbands` using numeric byte values (e.g., `echo 255 > /sys/class/ame/ame_ctrl_dev/ofdma_subbands` or `echo 0xfe > ...`, never `"11111111"`), reading back `system_config + 0x10a` and BBP MRX register `+0x48000` bits `12..19`.
