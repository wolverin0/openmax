<!-- doc-head: ADVERSARIAL_REVIEW_STAGE10_11.md continuation 2 of 3; source lines preserved -->
<!-- /doc-head -->

[Document router](ADVERSARIAL_REVIEW_STAGE10_11.md) | Part 2/3
<a id="adversarial-review--stage-10-stage-11a-stage-11b-and-public-claims"></a> [Adversarial review — Stage 10, Stage 11A, Stage 11B and public claims](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_001.md#adversarial-review--stage-10-stage-11a-stage-11b-and-public-claims) | <a id="executive-verdict-and-severity-table"></a> [Executive verdict and severity table](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_001.md#executive-verdict-and-severity-table) | <a id="evidence-method-and-reproducibility"></a> [Evidence, method and reproducibility](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_001.md#evidence-method-and-reproducibility) | <a id="detailed-findings--stage-10-wa-stock-airos-8-interoperability"></a> [Detailed findings — Stage 10: WA stock airOS 8 interoperability](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_001.md#detailed-findings--stage-10-wa-stock-airos-8-interoperability) | <a id="f01--critical-a-retained-elf-relocation-invalidates-the-nop-claim"></a> [F01 — CRITICAL: a retained ELF relocation invalidates the NOP claim](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_001.md#f01--critical-a-retained-elf-relocation-invalidates-the-nop-claim) | <a id="remaining-watchdog-reconnect-and-dfs-paths"></a> [Remaining watchdog, reconnect and DFS paths](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_001.md#remaining-watchdog-reconnect-and-dfs-paths) | <a id="f02--high-persistence-is-not-a-transactional-fail-safe"></a> [F02 — HIGH: persistence is not a transactional fail-safe](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_001.md#f02--high-persistence-is-not-a-transactional-fail-safe) | <a id="f03--high-the-bridging-claim-lacks-the-decisive-implementation-and-packets"></a> [F03 — HIGH: the bridging claim lacks the decisive implementation and packets](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_001.md#f03--high-the-bridging-claim-lacks-the-decisive-implementation-and-packets) | <a id="detailed-findings--stage-11a-xc-rocket-prism-and-airprism"></a> [Detailed findings — Stage 11A: XC Rocket Prism and AirPrism](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_001.md#detailed-findings--stage-11a-xc-rocket-prism-and-airprism) | <a id="f04--high-the-published-board-layout-and-hardware-matrix-are-not-faithful-to-the-elf"></a> [F04 — HIGH: the published board layout and hardware matrix are not faithful to the ELF](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_001.md#f04--high-the-published-board-layout-and-hardware-matrix-are-not-faithful-to-the-elf) | <a id="audit-of-reddit-readme-and-propagated-public-claims"></a> [Audit of Reddit, README and propagated public claims](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_003.md#audit-of-reddit-readme-and-propagated-public-claims) | <a id="f12--high-the-current-public-post-is-not-ready-to-publish"></a> [F12 — HIGH: the current public post is not ready to publish](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_003.md#f12--high-the-current-public-post-is-not-ready-to-publish) | <a id="f14--low-reproducibility-and-documentation-hygiene"></a> [F14 — LOW: reproducibility and documentation hygiene](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_003.md#f14--low-reproducibility-and-documentation-hygiene) | <a id="concrete-corrections-and-bench-verification-checklist"></a> [Concrete corrections and bench verification checklist](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_003.md#concrete-corrections-and-bench-verification-checklist) | <a id="immediate-documentarysource-corrections"></a> [Immediate documentary/source corrections](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_003.md#immediate-documentarysource-corrections) | <a id="stage-10-isolated-bench-acceptance-after-separate-authorization"></a> [Stage 10 isolated bench acceptance, after separate authorization](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_003.md#stage-10-isolated-bench-acceptance-after-separate-authorization) | <a id="xc-airprism-acceptance-after-separate-authorization"></a> [XC AirPrism acceptance, after separate authorization](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_003.md#xc-airprism-acceptance-after-separate-authorization) | <a id="ltu-acceptance-only-if-separately-approved-as-a-lab-experiment"></a> [LTU acceptance, only if separately approved as a lab experiment](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_003.md#ltu-acceptance-only-if-separately-approved-as-a-lab-experiment) | <a id="final-disposition"></a> [Final disposition](ADVERSARIAL_REVIEW_STAGE10_11_CONTINUATION_fb6b09e882_003.md#final-disposition)

<!-- stage822a-payload-begin -->

Selected corrected rows from [`xc_boards.json`](../artifacts/adversarial_review_stage10_11/xc_boards.json):

| Held board identity | Sysid | Radios | wifi0 caps | HSR parameter | Scope of confirmation |
| :--- | :--- | :---: | :--- | :---: | :--- |
| `PBE-5AC-500-ISO` (two records) | `0xe3d5` | 2 | `0xace00814` | 0 | Neither prism bit 30 nor HSR bit 28; “single radio” is false for these records |
| `R5AC-PTP` | `0xe3f5` | 2 | `0xbce00814` | 171 | HSR bit set; prism bit clear |
| `R5AC-PTMP` (two variants) | `0xe3f5` | 2 | `0xbee00814` | 31 / 43 | Same sysid is insufficient to choose the variant |
| `PS-5AC` | `0xe7e6`, `0xe7e8` | 2 | `0xfce00814` | 31 | Both prism and HSR capabilities |
| `RP-5AC-Gen2` | `0xe7e7`, `0xe7e9` | 2 | `0xfce00814` | 31 | Both prism and HSR capabilities |

**REFUTED:** the brief's `0xe7f9 = Rocket Prism Gen2`; the report's `0xe7f8/e7f9/e7fa` mapping of these old Rocket records; and its blanket ISO single-radio table. `0xe7f9` is absent from this XC board table. The corrected evidence does support an ISO example without active prism/HSR capability, but not every model/revision and not the published list of attributes.

The second-radio capability values are `0x0c` on the selected Gen2 boards and `0x14` on the old Rocket/ISO records. The actual cap-name mapping describes 11n and chain-count capabilities; those words do not prove a universal dedicated 5 GHz scanner. Do not transplant a WA or similarly named product's sysid into an XC flash decision.

### F05 — HIGH: the prism algorithm tests the full channel interval

**CONFIRMED:** `umac.ko:ubnt_prism_hook` at `.text+0xac874` calls helper `.text+0xabeb0` using lower and upper channel edges derived from center and half-width. The helper requires:

```text
entry.stage == requested_stage
lower_channel_edge >= entry.start
upper_channel_edge <= entry.end
channel_width <= entry.maximum_width
```

**REFUTED:** the published center-only condition. Example: center `5240 MHz`, width `80 MHz` spans `5200..5280`. It does not fit the stage-1 `5150..5250` range, although its center does. The held code therefore reaches the wide entry where the published center-only algorithm would select the narrow bank.

The table is **six entries of 44 bytes**, not Reddit's “44-entry table.” Its original order is stage-1 low, stage-1 high, stage-2 low, stage-2 high, stage-1 fallback, stage-2 fallback. GPIOs 15/16 belong to stage 1 and 13/14 to stage 2. The code references `gpio_line_config` / `gpio_line_set`; do not substitute invented `ubnthal_gpio_Export` calls as a literal disassembly quotation.

**INFERRED risk:** a wrong/uninitialized RF filter state can attenuate the wanted signal, distort a wide channel, reduce selectivity or worsen blockers and EVM. **UNKNOWN:** power-on state, complete board routing, safe switching order, calibrated gain, rejection, insertion loss and the actual effect on an OpenWrt port. The report's quantitative `20–35 dB` penalty is not supported by a physical measurement here. A two-stage GPIO selector does not by itself prove the separate HSR chip, bus or programming protocol.

### F06 — HIGH: the purported HSR SPI/GPIO sequence is misattributed

Stage 11A attributes an `ubnthal_get_radio_cap(...,"hsr")` call and pin selection to `.text+0x8cb4c` / `0x8cbac..0x8cc2c`. **REFUTED by direct disassembly:** at `0x8cb4c` the instruction is `addiu a0,s1,0xd7c`; the following call is to local `.text+0x654d0`. The cited neighborhood contains data/checksum processing, not the stated capability call and GPIO exports.

The nearby `.data+0xd7c` string decodes to `board.sysid` with the repeating key bytes `81 93 e0 c4`, not the claimed single-byte XOR key `d6`. Security/board-validation strings and shared flash-SPI access cannot be relabeled a frequency-tuning protocol merely because the same controller is touched. The audit did not bypass or modify those checks.

A real call querying the `hsr` capability occurs around `.text+0xbbf64`, using the literal at `.rodata+0x15890`, and stores the result at a large driver-state offset (`+0x1e8c0`). The corrected HAL table independently confirms the capability values. **CONFIRMED:** HSR-related state is present. **UNKNOWN:** exact external chip identity, whether the relevant transport is the claimed SPI path or another host/firmware path, the meaning of all parameter bits, complete tuning transactions, and pins 11/12/17 or 11/12/13/15.

Consequently the brief's apparent GPIO 13–15 conflict is **UNKNOWN**, not a demonstrated electrical collision. It rests on an unverified HSR pin map. Do not resolve it by assuming pins are multiplexed, or port the purported sequence into a driver. Required evidence is a traced capability-consumer/tuning call chain and board-specific bus/pin confirmation. Existing SPI locking and error strings are insufficient.

### F07 — MEDIUM: spectral filtering and hybrid mode need narrower claims

**CONFIRMED:** `ath_dev.ko:ath_spectral_filter_init` at `.text+0x27c00` configures GPIO 21, requests IRQ 64 with a handler at `.text+0x27be0`, and uses the `ath-spectral-filter` identifier. This is meaningful evidence of a hardware-assisted spectral-filter interrupt path.

**UNKNOWN:** wire polarity, interrupt routing on each board, measured timing, whether it blanks every relevant FFT window, and whether the protected path is specifically the second radio's LNA rather than sample eligibility/control. The public “scanner never deafened” explanation and microsecond timing need actual hardware evidence.

Likewise, retaining the stock `umac` module plausibly preserves vendor tuning. It does not certify XC AP or STA hybrid operation, hostapd behavior, all channel changes, DFS, rekey or filter restoration. Shared patch offsets and a `polling=disabled` parser are insufficient for “works without changing a single byte” and “100% compatibility.” Stage 11 remains static until exact-board acceptance.

## Detailed findings — Stage 11B: LTU 4096-QAM, OFDMA and architecture

### F08 — CRITICAL: the published flash map contradicts the actual DTB

The actual trees are `ltu_extracted/aflturocket_2.4.2/rootfs_extracted` and `ltu_extracted/afltu_2.4.2/rootfs_extracted`, with modules under **`3.14.65`**. The brief's `_242_rootfs_squashfs` / `3.10.20-ubnt-mtk` paths do not identify these inputs.

**CONFIRMED:** held containers are `38918528` bytes (Rocket) and `24366210` bytes (CPE). They contain 10 and 5 AMEIMG parts. All 15 parsed payload MD5 values match the embedded values, and the parser consumes each entire file with **zero trailing bytes**. The documented `11,148/11,580`-byte outer signature footer is **REFUTED for these files**; this does not prove absence of every other integrity/authentication mechanism.

The primary part names are `spl`, `uboot`, `dtb`, `kernel`, `rootfs`, and their sizes differ from the report:

| Part | Rocket bytes | CPE bytes |
| :--- | ---: | ---: |
| spl | 524288 | 524288 |
| uboot | 318096 | 319344 |
| dtb | 6605 | 6554 |
| kernel | 3330408 | 3330408 |
| rootfs | 19398656 | 20185088 |

Both primary DTBs give the following NAND map; this table records **static DTB evidence only**, not an authorized flash recipe:

| Label | Start | Length |
| :--- | :--- | :--- |
| spl | `0x00000000` | `0x00080000` |
| uboot_env0 | `0x00080000` | `0x00060000` |
| uboot_env1 | `0x000e0000` | `0x00060000` |
| uboot | `0x00140000` | `0x00100000` |
| EEPROM | `0x00240000` | `0x000c0000` |
| cfg | `0x00300000` | `0x000c0000` |
| dtb0 | `0x003c0000` | `0x00060000` |
| kernel0 | `0x00420000` | `0x00500000` |
| rootfs0 | `0x00920000` | `0x02800000` |
| dtb1 | `0x03120000` | `0x00060000` |
| kernel1 | `0x03180000` | `0x00500000` |
| rootfs1 | `0x03680000` | `0x02800000` |
| reserved | `0x05e80000` | `0x02180000` |

**REFUTED:** Stage 11B's EEPROM at `0x00160000` and configuration at `0x00180000`. Both fall inside the actual DTB U-Boot range. Using that documentation for a write or restore could destroy boot code while believing the target was configuration/calibration. No such operation was performed here.

Other architecture corrections: Rocket's primary model is `AME SoC 3 LTU-Rocket Board`; the CPE model is `AME SoC 3 LTU Board`. The DTB's AD9361 SPI maximum is `0x02625a00` = **40 MHz**, not 20 MHz. The main GIC region is at `0xffffd000`, not the stated `0xf8f01000`.

**CONFIRMED SOLID:** dual Cortex-A9 / 256 MB primary descriptions, the `ame_ad9361` compatible node, and Rocket-only companion parts 5–9. The companion DTB identifies `altr,socfpga-arria10`, two CPUs and 128 MB RAM. The held `.rbf`/HPS boot/kernel/rootfs payload sizes in the report are mostly reproducible, including `5490084` bytes for part 5.

The HPS MTD numbering in the prose is also wrong: its DTB has intervening environment partitions before `core-rbf` and rootfs, plus redundant/factory partitions. Use the full recorded DTB rather than the claimed simple `mtd0..mtd5` sequence. **UNKNOWN:** exactly which baseband/aggregation/DSP work the opaque FPGA fabric performs, and whether it implements the claimed “channel stitching” explanation for 100 MHz. A companion FPGA's presence does not prove that explanation.

### F09 — HIGH: meaningful 4096-QAM software exists; a qualified PtMP unlock is unproven

The Rocket `ame_core.ko` under review is `3318764` bytes, MD5 `92d1e1e3babacf57f291e7af774892c3`. CPE `ame_core.ko` differs (MD5 `12ba72a3fb0875439e05be32dcc1d630`); AP offsets must not be applied mechanically to it.

The following are **CONFIRMED static observations**:

1. Rocket `ubntbox` has the MCS bound check around VA `0x40284`; its table at **VA** `0xd4b28` (file offset `0xccb28`) is `[7,11,15,19,23,31]`. Configuration value 5 can translate to internal ceiling 31 in the inspected path. No `ptpmode` check was found in that local validation/serialization block.
2. `AME_Scheduler_AutoMCS_GetPtmpDLCeiling` at `.text+0x735ac` accepts 31 in its validation and has a fallback to global `system_config+0x174`. This is positive evidence against an unconditional 1024-QAM clamp in **that function**.
3. `ame_bbp_set_autoMcsCeiling` at `0x196af0` stores the requested ceiling and invokes power/backoff machinery. Setting a ceiling is not forcing each transmission to that rate; the setter also selects the automatic-MCS path.
4. `autoMcsUseSisoTbl` and `autoMcsOthersTbl` contain `(31,1)`. `autoMCS_get_rate_table` at `0x156098` branches on SISO, operating configuration, training state and board identifiers (`0xae05`/`0xae0e`). The inspected non-SISO paths select seven-entry tables containing 31; the SISO branch selects five entries. This supports a real MIMO table entry, not a universal operational guarantee.
5. `bbp_rf_set_super4096` at `0x1766bc` reads/changes RF state and reaches `ame_rfic_req(0x56,...)`. Its symbol name and register actions support a specialized path, not a measured low-EVM profile or confirmed calibration quality.
6. `startThrd_4096 = 97` and `stayThrd_4096 = 90` are present. Their exact units and conversion to the report's `38–42 dB CINR` are **UNKNOWN**.

The kernel has additional guards. `ame_bbp_set_Param_mcs` at `0x194648` calls `ame_check_hw_NoLDPC` on a path covering code 31, and rejects unsupported cases; it also has a `NoRS` path for the RS code range. Backoff behavior is conditional on configuration/mode fields, including checks at `system_config+0x20` and `+0x10`. The actual values on each board, peer capability negotiation, width-dependent limits, training behavior and FPGA support were not established by this audit.

Therefore **REFUTED as a complete description:** “only WebUI/Lua validation exists.” **UNKNOWN:** whether those other guards block 4096 on a particular supported PtMP pair. No universal PtMP clamp to 29 was identified in the examined paths, and the report must not invent one. Code **29 is RS 1024-QAM**; LDPC 1024-QAM is **23**. The brief's bare “1024 = 29” is incomplete.

**UNKNOWN:** why Ubiquiti disabled the UI option, whether historical releases had the same behavior, AD9361 EVM/phase-noise margin in this board, PA headroom, LDPC throughput limits at a given width, and sustained net benefit. Marketing motive cannot be inferred from strings. A complete answer requires tracing peer capability consumers/FPGA status and then an authorized isolated RF test, not bypassing hardware or regulatory checks.

The honest replacement claim is: **“Firmware v2.4.2 contains 4096-QAM-related rate tables, configuration paths and RF-driver routines; a configuration ceiling of 31 is accepted in inspected paths. Usable PtMP 4096-QAM and its limits remain unverified.”**

### F10 — HIGH: rate mapping is wrong, and ceiling is not fixed modulation

The actual `ame_adj.sh` mapping and the `ubntconf` table agree on the following six LDPC codes. The script labels these named modulation entries as 5/6; that label alone is not a measured PHY coding implementation.

| Config MCS | Actual modulation / nominal UI label | LDPC code | RS code from script |
| :---: | :--- | :---: | :---: |
| 0 | QPSK; `1X` SFBC or `2X` depending on NSS selection | `0x07` | `0x19` |
| 1 | 16-QAM / `4X` | `0x0b` | `0x1a` |
| 2 | 64-QAM / `6X` | `0x0f` | `0x1b` |
| 3 | 256-QAM / `8X` | `0x13` | `0x1c` |
| 4 | 1024-QAM / `10X` | `0x17` | `0x1d` |
| 5 | 4096-QAM / `12X` | `0x1f` | `0x1e` |

**REFUTED:** Stage 11B's extra QPSK row at config 1, shifted 16/64/256-QAM labels, duplicate config 4 mapping, and mixed coding-rate assignments. The WebUI snippet shown as extracted code similarly shifts labels/values. The actual `getAvailableDataRates` offers `0@0` for QPSK+SFBC and `0@1` for 2X QPSK, then `1@1` through `5@1`. The 12X entry's `disabled:t` is real; the surrounding quoted table must be corrected.

`ame_adj.sh mcs 4096l` writes the fixed/adjusted-MCS interface (`adj_mcs`), not merely `autoMcsCeiling`. Per-CPE and global operations also differ. These are not interchangeable ways of measuring a working “unlock.” Net spectral efficiency additionally depends on coding, pilots, framing, guard intervals, retransmissions and scheduler airtime; `12X` is not a measured 12 bit/s/Hz payload guarantee.

### F11 — HIGH: OFDMA parsing and notch interpretation are overstated

**CONFIRMED:** `ame_dev.ko:ofdma_subbands_store` at `.text+0x1154c` calls `simple_strtol` with base 0 and truncates to an unsigned byte (`uxtb` at `0x11568`) before invoking its hook. Thus the literal string **`11111111` is decimal 11,111,111 and becomes `0xc7`**, not `0xff`. It is not an eight-character binary-string parser. Leading-zero and prefixed-number behavior must be treated as numeric parsing, not a visual bit map.

`ame_core:ame_bbp_set_ofdma_subbands` at `0x1979c4` complements the byte into `system_config+0x10a`, then reaches `bbp_mrx_band_ofdma_subbands` at `0x145704`, which writes an eight-bit field at bits 12–19 in a BBP register in the `+0x48000` region. **CONFIRMED:** a real RX-side mask/configuration path exists. **UNKNOWN:** how its bit polarity, frequency ordering and receiver configuration map to usable over-the-air allocations or transmitted spectral notches.

Additional meaningful code is present: `ame_bbp_set_ofdma_en`, subband-type setters and `sched_ofdma_available` at `0x63f74`. The availability function checks enable state at `system_config+0x154` and resource/size conditions. `ame_check_hw_NoOFDMA` at `0x5708` reads a hardware-capability bit; it is consumed in capability-message construction. This is not evidence of a purely empty stub, but it is also not proof that every board/FPGA/peer combination supports 2/4/8-subband service.

The report's `ubntconf` address range around `0x42304..0x42390` includes literal data, not the asserted executable proof of every mode translation. Configuration strings exist; the full mode-to-scheduler/FPGA path remains incomplete. **UNKNOWN:** all supported `ofdma_mode` semantics, operational subcarrier allocation, uplink/downlink asymmetry, compatibility negotiation, allowed widths and net gain. Remove “already notches out interference” until spectrum and traffic measurements establish it.

### F13 — MEDIUM: higher-layer ideas are portable; the actuator is not automatic

**CONFIRMED:** LTU exposes a custom baseband/RF architecture distinct from the held QCA988x 802.11ac stack. Copying LTU setting names cannot add 4096-QAM, LTU framing or its subband scheduler to QCA988x. The broad “not a drop-in PHY upgrade” boundary is sound.

**UNKNOWN:** the report's absolute assertions about QCA shared-LO internals, precise retune timing and all possible nonstandard widths are not established by the LTU binaries. Separate TX/RX-frequency configuration paths support split-frequency operation as a design capability; they do not prove simultaneous full-duplex traffic or the claimed 100-MHz FPGA implementation. Keep those explanations conditional until their exact sources/hardware are verified.

Per-peer quality history, spectral scoring, pacing and desired-rate policies are higher-layer concepts that can inform a new QCA-side implementation. They require independently verified telemetry and control hooks. The report's “directly portable WMI rate ceiling” claim ignores the project's own documented rate-mask authority failure on the tested firmware: host API acceptance/reassociation did not establish enforced over-the-air masks. Preserve that limitation.

Two concrete CLI corrections from the held script:

- `mix_mcs` help gives **`<cpe_id> <q_id> <portion> <sub_mcs> <sub_mimo> [offset]`**, and writes `adj_mix_mcs`; it does not accept four queue percentages as the report suggests.
- `cpe_mcs` writes the **`cpe_mcs`** sysfs interface, not the stated `cpe_fixrate` path.

<!-- stage822a-payload-end -->
