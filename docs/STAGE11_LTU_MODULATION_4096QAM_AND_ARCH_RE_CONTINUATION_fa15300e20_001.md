<!-- doc-head: STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md continuation 1 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md) | Part 1/2
<a id="5-physical-lab-bench-qualification-results-on-ltu-lite-2026-10-21"></a> [5. Physical Lab Bench Qualification Results on `LTU-Lite` (`2026-10-21`)](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_002.md#5-physical-lab-bench-qualification-results-on-ltu-lite-2026-10-21) | <a id="51-step-1-results--live-hardware-nand-partition-map--capability-bits-confirmed"></a> [5.1 Step 1 Results — Live Hardware, NAND Partition Map & Capability Bits (`CONFIRMED`)](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_002.md#51-step-1-results--live-hardware-nand-partition-map--capability-bits-confirmed) | <a id="52-step-2-results--live-4096-qam-12x-0x1f-kernel--scheduler-activation-confirmed"></a> [5.2 Step 2 Results — Live `4096-QAM` (`12X`, `0x1f`) Kernel & Scheduler Activation (`CONFIRMED`)](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_002.md#52-step-2-results--live-4096-qam-12x-0x1f-kernel--scheduler-activation-confirmed) | <a id="53-step-3-results--live-ofdma-subband-mask--persistence-hooks-confirmed"></a> [5.3 Step 3 Results — Live `OFDMA` Subband Mask & Persistence Hooks (`CONFIRMED`)](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE_CONTINUATION_fa15300e20_002.md#53-step-3-results--live-ofdma-subband-mask--persistence-hooks-confirmed)

<!-- stage822a-payload-begin -->

D1 native UISP loopback qualification remains accepted on bench Loco195.
D2 ran on LTU-Lite2.4.0: ceiling31 worked; fixed1f reverted20, retention not accepted.
All14 discrete AirMAC samples were0; original23/20 profile and owned RAM restored.
D3 captured Rocket198/e7e9/XC8.7.25 inventory with unchanged boot/config/network.
AirPrism active filter, HSR transport and unexposed GPIO remain UNKNOWN.
No production, flash, RF-performance or real UISP/TLS qualification follows.


## October23 current result: native LTU probe restored; Rocket inventory captured

The operator confirmed the isolated indoor LTU bench without an active AP and authorized D2 then readonly D3. The earlier RF-prerequisite receipt below remains unchanged as historical evidence; it is no longer the current blocker. Actual LTU firmware is2.4.0, with no2.4.2 qualification or upgrade.

[Requested D2 live receipt](../artifacts/stage11_ltulite_4096qam_ofdma_live_20261023.json) and [independent review](../artifacts/stage11_ltulite_live_review_20261023.json): ceiling31 yielded af4096qam12x/scheduler4096l. Literal uppercase4096L printed usage/rc0, leaving adj0x20; native lowercase4096l immediately yielded0x1f. Adj read0x20 by the subsequent mask0xff snapshot. The raw run remains NOT_ACCEPTED_NATIVE_TREATMENT/FIXED_RATE_READBACK, with reversion cause UNKNOWN. Writing0xff was idempotent and does not prove OFDMA activation. All14 discrete AirMAC observations were0; original ceiling23/adj0x20/autoMcs4096=10/scheduler1024Ql/mask0xff plus four hashes/network/boot restored exactly. Owned guard and RAM closed. CONFIRMED native controls do not prove retained mode, OTA4096-QAM, negotiated peer support or multiuser scheduling.

[Requested D3 readonly inspection](../artifacts/stage11_rocket_prism_198_inspection_20261023.json) identifies Rocket198/e7e9/XC.v8.7.25 with unchanged boot, four hashes and normalized network throughout the initial capture and two followups. Board.info/version/MTD/modules and radio/feature/GPIO observations are retained. Board phycount1, PCI/AHB descriptors and virtual wifi1 are distinct facts; literal radio0/radio1 sysfs labels were absent. uph_wifi0 enable1/status1 and newline-only hsr_diag are measured, but AirPrism active filter and HSR transport/blanking remain UNKNOWN. The exact running ubnt_poll_host matches the held module; the read-side hsr_diag path returns diagnostic scratch state without invoking the write-side HSR command. GPIO13/14/15/16/21 are unexported and debug GPIO is absent, so values remain UNKNOWN. No export, toggle, mount, module load, RF/config/flash or production operation ran. [Independent D3 review](../artifacts/stage11_rocket_prism_198_readonly_review_20261023.json) assesses only this exposed-state inventory.

The requested probe/inspection sequence is closed. Physical waveform/performance, persistent fixed mode and hidden HSR/GPIO behavior remain unqualified; no optional follow-on experiment is active. Historical static tables and accepted earlier writes below must not be promoted to a current RF result.

## October23 historical D2 observation before operator physical confirmation

[The live receipt](../artifacts/stage11_ltulite_4096qam_ofdma_bench_20261023.json) records exact LTU-Lite E063DABF5399/sysid0xae08/rev9, pinned after a first-seen key was bound to the operator-named EUI64 bench identity. Actual firmware is afltu.v2.4.0, not requested2.4.2. Native getters report ceiling23/adj0x20/autoMcs4096=10/scheduler1024Ql/mask0xff, and hardware flags NO_LDPC0/NO_OFDMA0. These observations do not exercise the setters or prove constellation/OFDMA scheduling.

Fresh RegObey is disabled, TX reports5970MHz, and readonly ameeng.cgi reports airMACEnabled0 without creating an engineering flag. Physical RF containment/compliance remains unconfirmed; the operator was asked for the exact enclosure/conducted-attenuation condition. No requested MCS/OFDMA/config/file/flash/regulatory/power/frequency write was performed. [Postchecks](../artifacts/stage11_ltulite_readonly_postcheck_20261023.json) confirm the same boot, network, original control getters and four configuration/script hashes. The code31/0xff treatment stays incomplete, with its original native rollback recipe retained in [the prerequisite](../artifacts/stage11_ltulite_rf_precondition_20261023.json). Historical accepted writes and2.4.2 static code below are not a new live acceptance result.

Publication note: the older scratch/disassembly archive links below refer to retained local-only evidence, outside this bounded Git delivery. The [publication manifest](../artifacts/canary_panel1_guarida/fmx0017_publication_manifest_20261022.json) identifies the receipts published for the October22 order.

## October22 evidence alignment - current bench scope

The accepted exact-device receipts supersede any universal present-tense reading
of older incompatibility or topology statements below: run17 establishes stock
WA.v8.7.25 Loco195 bidirectional association with the held LAP-120 OpenWrt AP;
run25 adds stock XC.v8.7.25 Rocket198 concurrently (61.031s authorization,
64/64 radio-qualified pings each); FMX-0016 run8 adds SXT OpenWrt/ath9k and
stock airOS6 M5 concurrently (60.5s,64/64 each,256 matched radio echo pairs).
All modified state was restored and the AP radio disabled. These are exact
bench compatibility results; they do not establish capacity, performance gain,
TDMA/GPS, all-revision support, physical relay or production acceptance.

Sources: [current state](CURRENT_STATE.md),
[run8 receipt](../artifacts/canary_panel1_guarida/root_four_cpe_result_20261022.json),
[Oct22 scoped evidence alignment](../artifacts/canary_panel1_guarida/fmx_docs_alignment_20261022.json).
Existing E2 remains `NOT_ACCEPTED` with its original gates. Original dated
measurements, failures, static control limits and firmware scopes remain
historical evidence, not permission to resume those recipes.
No Oct22 stock WA/XC or LAP/Rocket worker subcheck exercises an LTU radio. LTU4096-QAM/OFDMA paths below remain scoped static findings; no LTU RF or distributed-compute runtime acceptance follows.



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

---
<!-- stage822a-payload-end -->
