<!-- doc-head: HARDWARE_MATRIX.md continuation 1 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](HARDWARE_MATRIX.md) | Part 1/2
<a id="what-this-table-corrected"></a> [What this table corrected](HARDWARE_MATRIX_CONTINUATION_d411365af3_002.md#what-this-table-corrected) | <a id="open-hardware-questions-after-the-sweep"></a> [Open hardware questions after the sweep](HARDWARE_MATRIX_CONTINUATION_d411365af3_002.md#open-hardware-questions-after-the-sweep) | <a id="standing-safety-rule"></a> [Standing safety rule](HARDWARE_MATRIX_CONTINUATION_d411365af3_002.md#standing-safety-rule)

<!-- stage822a-payload-begin -->

Stock WA8/XC8 and four-generation PtMP confirmed by run17/run25/run8.
Original dated benchmarks/static findings keep their hardware and firmware scope.
No new performance, TDMA/GPS, relay, production or E2 acceptance follows.
Current authoritative state and source receipts are linked below.


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
Current four-CPE fixture: stock WA8 Loco195 + stock XC8 Rocket198 + SXT OpenWrt24.10.4 ath9k + stock XW6.1.4 M5. FMX-0018/0020 usable-memory and worker subchecks cover LAP-120/Rocket198 only; they do not qualify untested Loco/LTU worker targets.



# FuturaMAX hardware matrix

Summary: verified per-model silicon, memory, flash layout, radio firmware and driver stack
for the airMAX AC target family, separating Grade-A evidence from inherited assumption.
Keywords: AR9342, QCA988X hw2.0, NanoStation 5AC, LiteAP AC, LiteBeam 5AC Gen2, Loco 5AC,
flash layout, EEPROM calibration, ubnthal, ubnt_poll_host, firmware 10.2.4-1.0-00037.
Read when: sizing anything against the target hardware, or before assuming two models in
this family share a board. Current verdict: **all six target models CONFIRMED Grade-A from live hardware; gap G04 is
CLOSED.** Status: CURRENT (2026-08-08).

## Evidence grades used here

`A` exact target device, primary measurement or vendor/upstream boot evidence ·
`B` comparable 802.11ac hardware with a credible porting path ·
`C` adjacent chipset, concept transfers, implementation uncertain ·
`E` unverified community or model assertion.

## Matrix — all six models measured on live hardware 2026-08-08 (Grade A)

Collected read-only over SSH from production units (`tools/inventory/collect.py`); raw
MAC-sanitised output in `research/raw/hardware/`. **Every row below is Grade A.**

| Model (board.name) | sysid | SoC | Radio | RAM | airOS | Role |
|---|---|---|---|---|---|---|
| **LiteAP GPS** | `0xe7fd` | AR934x 535/400/200 MHz | QCA988x (`TARGET TYPE 7 Vers 0x4100016c`) | 64 MB | WA.v8.7.22 | PTMP AP |
| LiteAP AC | `0xe8e5` | AR934x 535 MHz | QCA988x | 64 MB | WA.v8.7.22 | PTMP AP |
| LiteBeam 5AC | `0xe7f9` | AR934x 535 MHz | QCA988x | 64 MB | WA.v8.7.22 | PTMP STA |
| LiteBeam 5AC LR | `0xe7fe` | AR934x 535 MHz | QCA988x | 64 MB | WA.v8.7.11 | PTMP STA |
| NanoStation 5AC loco | `0xe7fa` | AR934x 535 MHz | QCA988x | 64 MB | WA.v8.7.22 | PTMP STA |
| **Rocket Prism 5AC** | `0xe7e9` | **QCA955x 720/600/200 MHz** | QCA988x | 64 MB | XC.v8.7.22 | PTMP AP |

All six report the same radio target version, so **the entire fleet is QCA988x Wave 1** — no
QCA9888/Wave 2 anywhere, settling C12 for every model rather than by inference.

`0x0777` is the Ubiquiti PCI subvendor; `radio.1.subsystemid` equals the board `sysid` on
each unit, so sysid alone identifies the board. Read it rather than trusting the label — the
unit labelled "Rocket Prism 2 AC" reports `Rocket Prism 5AC`, and "nano ac" is a
NanoStation 5AC **loco**.

**Rocket Prism 5AC is the outlier worth remembering**: QCA955x at 720 MHz with 600 MHz DDR,
versus AR934x at 535/400 for everything else. If an on-device controller is ever wanted, it
is the only target with meaningful CPU headroom.

Per-model capability detail, the radio-firmware finding and the `ubnt_poll_host` control
surface are in **`knowledge/AIRMAX_ARCHITECTURE.md`** — read that before designing anything.

## Grade-A detail: NanoStation AC (S1) — 2017-era boot logs

> **Historical.** This section predates the 2026-08-08 live sweep and is kept because it is
> the only source with a full **OpenWrt** boot log on target-family hardware (ath10k
> attaching to QCA988x), which the airOS units cannot show. Where it disagrees with the live
> sweep, the live sweep wins. Its `sysid 0xe7fb` is the full NanoStation 5AC; the unit
> sampled live is the **loco** variant, `0xe7fa`.

Source `S1` = OpenWrt device page `https://openwrt.org/toh/ubiquiti/nanostation_ac`,
page last modified 2024-02-12, read through a browser on 2026-08-08 (plain HTTP gets a bot
challenge). It carries two complete boot logs, which is why this is Grade A rather than
Grade C wiki assertion.

### Board identity

```
U-Boot 1.1.4-s1038 (May 18 2017)
Board: Ubiquiti Networks AR9342 board (e7fb-141837.1122.0030.0031)
DRAM: 64 MB   Flash: 16 MB   Radio: 0777:e7fb
ubnthal: board found, sysid = 0xe7fb, name = NanoStation 5AC
```

`sysid 0xe7fb` and PCI subsystem `0777:e7fb` are the machine-checkable identity. Read these
from every unit during E0 inventory rather than trusting the model name on the label.

### Radio, as seen by OpenWrt/ath10k (Grade A)

```
ath10k_pci: qca988x hw2.0 target 0x4100016c chip_id 0x043222ff sub 0777:e7fb
firmware ver 10.2.4-1.0-00037 api 5
features no-p2p,raw-mode,mfp,allows-mesh-bcast
htt-ver 2.1  wmi-op 5  htt-op 2  cal file  max-sta 128  raw 0  hwcrypto 1
```

Four things here matter more than anything any model report said:

1. **`QCA988X hw2.0` is confirmed on a target device.** Wave 1, not Wave 2.
2. **Stock firmware is `10.2.4-1.0-00037`** — the exact branch the ath10k mailing-list
   per-peer pktlog telemetry work targeted (that work was tested on `10.2.4.70.48`). The
   telemetry question is therefore testable on this hardware, not hypothetical.
3. **`raw-mode` is advertised as a firmware feature.** This is the single most interesting
   line in the log for the custom-MAC question and no run mentioned it for target hardware.
4. **`max-sta 128`** is the driver-reported station ceiling — relevant to sector sizing.

### Flash layout and protected partitions (Grade A)

| mtd | Name | Size | Protected? |
|---|---|---|---|
| mtd0 | u-boot | 256 KiB | **NEVER WRITE** |
| mtd1 | u-boot-env | 64 KiB | **NEVER WRITE** |
| mtd2 | firmware (kernel+rootfs) | 15744 KiB | writable target |
| — | cfg | 256 KiB | Ubiquiti device config / persistent storage |
| — | **EEPROM** | 64 KiB | **NEVER WRITE — Atheros radio calibration data** |

This is the concrete basis for the lab-safety constraint. `EEPROM` at the top 64 KiB of
flash is the ART/calibration region; `u-boot` + `u-boot-env` are the recovery path. Stock
airOS logs confirm the radio depends on it: `Restoring Cal data from Flash`,
`qc98xx_verify_checksum: flash checksum passed: 0x5cc6`.

### What stock airOS actually runs (Grade A) — the most valuable discovery

The OEM boot log shows airOS does **not** use ath10k. It uses the Qualcomm vendor offload
stack plus Ubiquiti proprietary kernel modules:

```
ath_pci: 10.1.467 (Atheros/multi-bss)      <- QCA vendor "ol_ath" offload driver
Ubiquiti U-AME chipset detected
ol_transfer_bin_file: Download Firmware data len 215408. Mode: PTP
ubnthal: module license 'Proprietary' taints kernel
ubnt_poll_host: Initialized in PTP STA mode for device wifi0
ubnt_poll_host: Polling enabled for radio wifi0
ubnt_poll_host: Fixed frame mode disabled for radio wifi0
ubnt_poll_host: noack_mode set to 0 for radio wifi0
ubnt-poll-host: [wifi0] Station priority configured to 2 (no-auto=0)
ubnt_poll_host: ATPC enabled (0/0/0/25) for radio wifi0
```

**`ubnt_poll_host` is airMAX.** It is a proprietary kernel module sitting on top of the QCA
`ol_ath` offload driver, and its printk parameters map one-to-one onto the airMAX features
every report described only from marketing pages: polling, fixed-frame mode, ackless
<!-- stage822a-payload-end -->
