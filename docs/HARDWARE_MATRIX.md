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
(`noack_mode`), airMAX Priority (`Station priority ... no-auto`), and ATPC.

Consequences that change the research plan:

- The proprietary boundary is a **host kernel module**, not (only) opaque radio firmware.
  `ubnt_poll_host` and `ubnthal` are the artifacts to characterise in W02 — and they are
  far better search handles than "airMAX TDMA".
- **airOS and OpenWrt do not share a driver.** Every airOS-vs-OpenWrt comparison is
  `ol_ath 10.1.467 + ubnt_poll_host` versus `ath10k + mac80211`, changing two layers at
  once. Any A/B experiment must say so; "same hardware" is not "same stack".
- Radio firmware is loaded in **`Mode: PTP`** with a 215408-byte image, distinct from the
  ath10k `firmware-6.bin` path. Whether the airOS radio firmware differs from stock
  QCA 10.2.4 is now a concrete, answerable question.
- `Ubiquiti U-AME chipset detected` — **SUPERSEDED by the 2026-08-08 live sweep.** It was
  the only lead toward the disputed "airMAX ASIC" claim (C15); the sweep found it on all six
  units including plain CPEs, so it is a fleet-wide identifier, not a premium-hardware
  accelerator marker. See `knowledge/AIRMAX_ARCHITECTURE.md` section 3.
- airOS carries its own spectral module (`ath_spectral 2.0.0`, `HAL_CAP_SPECTRAL_SCAN:
  Capable`) but logs `SPECTRAL: No ADVANCED SPECTRAL SUPPORT`. Spectrum telemetry may be
  reachable **without leaving airOS** — which would fit the airOS-first architecture
  decision far better than flashing OpenWrt.

## What this table corrected

| Was claimed | By | Reality (Grade A) |
|---|---|---|
| NanoStation AC uses **QCA9888** (Wave 2) | glm source ledger | **QCA988X** Wave 1 |
| Target SoC is **QCA9563 @ 750 MHz** | google | **AR9342 @ 535 MHz** |
| QCA988x is 802.11ac **Wave 2** | mistral | Wave 1 |
| OpenWrt "can't boot on Ubiquiti AC gear, u-boot unavailable" | glm blocker #4 | Refuted — full OpenWrt boot log on this device |

## Open hardware questions after the sweep

Closed by the 2026-08-08 collection: LAP-GPS identity, per-model radio generation, GPS
presence, flash layout, and the QCA9888-vs-QCA988x question.

Still open:

1. **Extract and compare the per-mode radio firmware images** (PTP ~214 KB, PTMP-AP ~250 KB,
   PTMP-STA ~233 KB) against stock QCA 10.2.4. Highest-value remaining W02 item — see
   `AIRMAX_ARCHITECTURE.md` section 1. (gap G08, promoted)
2. **`DAPROT`** — an `ubnt_poll_host` parameter present on all six units, absent from the
   2017 boot log, and unmentioned by any research run. Meaning UNKNOWN.
3. **Non-standard channel widths.** `radio.1.chanbw=10,20,30,40,50,60,80` exposes 30/50/60 MHz.
   Can ath10k/OpenWrt reach them, and can airOS be driven to them per-link?
4. **FCC ID `SWX-LAPGPS`** — internal photos would independently settle whether any
   accelerator silicon exists, without relying on marketing pages.
5. Whether `raw-mode` (advertised by stock ath10k firmware on this chip) is usable.
6. Board revision variation *within* a model — one unit per model was sampled, not one per
   revision.

## Standing safety rule

Never write `u-boot`, `u-boot-env` or `EEPROM`. Never modify calibration/ART or board data.
Lab units only, recovery proven first. This is not advice — it is the project constraint
recorded in MemoryMaster and it is now backed by the exact partition map above.
