# airMAX AC architecture — measured on live production hardware

Summary: what airMAX actually is on the wire and in the kernel, read off six production
airMAX AC radios on 2026-08-08. Covers the per-mode radio firmware swap, the `ubnt_poll_host`
control surface, role-dependent parameters, and what this means for custom-MAC feasibility.
Keywords: ubnt_poll_host, ubnthal, ol_ath, PTMP firmware, PTP firmware, fixed frame, ATPC,
DAPROT, deferred list, U-AME, QCA988x, custom MAC go/no-go, E4.
Read when: judging whether OpenWrt can replicate airMAX, or scoping W02.
Current verdict: **airMAX ships custom per-mode, per-role QCA radio firmware.** This is the
strongest evidence yet against a custom PtMP MAC on stock firmware. Status: CURRENT.

## Evidence base

Read-only SSH collection from six live production units, `tools/inventory/collect.py`.
Raw (MAC-sanitised) output in `research/raw/hardware/*-2026-08-08.txt`. Evidence grade **A**
— exact target devices, vendor firmware, current production builds.

| Label | Model (board.name) | sysid | airOS | SoC | Role |
|---|---|---|---|---|---|
| lap-gps | **LiteAP GPS** | `0xe7fd` | WA.v8.7.22 | AR934x, 535/400/200 MHz | PTMP **AP** |
| liteap-ac | LiteAP AC | `0xe8e5` | WA.v8.7.22 | AR934x, 535 MHz | PTMP AP |
| litebeam-5ac | LiteBeam 5AC | `0xe7f9` | WA.v8.7.22 | AR934x, 535 MHz | PTMP STA |
| litebeam-5ac-lr | LiteBeam 5AC LR | `0xe7fe` | WA.v8.7.11 | AR934x, 535 MHz | PTMP STA |
| nano-ac | NanoStation 5AC **loco** | `0xe7fa` | WA.v8.7.22 | AR934x, 535 MHz | PTMP STA |
| rocket-prism-2ac | **Rocket Prism 5AC** | `0xe7e9` | XC.v8.7.22 | **QCA955x, 720/600/200 MHz** | PTMP AP |

All six report `ol_ath_attach() TARGET TYPE: 7 Vers 0x4100016c` — the same target version
ath10k identifies as `qca988x hw2.0`. **All six are QCA988x.** RAM 61960 kB (~64 MB).

Two corrections to the operator's labels: the "Rocket Prism 2 AC" is `Rocket Prism 5AC`, and
the "nano ac" is a NanoStation 5AC **loco**, not the full NanoStation.

---

## 1. The headline finding: airMAX swaps QCA radio firmware per mode and per role

Every unit loads radio firmware **twice** at boot — first a PTP image, then a PTMP image:

| Device | Role | PTP image | PTMP image | PTMP banner |
|---|---|---:|---:|---|
| LAP-GPS | AP | 214300 B | **250900 B** | `P 62 V 1 T 194` |
| LiteAP AC | AP | 214300 B | **250900 B** | `P 87 V 1 T 269` |
| Rocket Prism 5AC | AP | 215064 B | **251680 B** | `P 62 V 1 T 194` |
| LiteBeam 5AC | STA | 214300 B | **233512 B** | `P 32 V 1 T 164` |
| LiteBeam 5AC LR | STA | 216060 B | **235272 B** | `P 32 V 1 T 164` |
| NanoStation 5AC loco | STA | 214300 B | **233512 B** | `P 32 V 1 T 164` |

```
ol_transfer_bin_file 259: Download Firmware data len 214300. Mode: PTP
FIRMWARE:P 34 V 1 T 110
ol_transfer_bin_file 259: Download Firmware data len 250900. Mode: PTMP
FIRMWARE:P 62 V 1 T 194
```

The images are **different binaries**, not one image with different runtime config — the byte
lengths differ by role (AP PTMP ≈ 250900, STA PTMP ≈ 233512, PTP ≈ 214300). The `P/V/T`
banner tracks the image: AP builds carry a higher `P` (62/87) than STA builds (32), which is
consistent with `P` being a peer/resource dimension, though that reading is **INFERRED**.

### Why this is the most important thing found so far

Every wave-1 report assumed the airMAX/OpenWrt difference was **host-side**: a proprietary
scheduler module versus mac80211. It is not only host-side. Ubiquiti ships **its own QCA988x
radio firmware, built per operating mode and per AP/STA role.**

Consequences, in order of importance:

1. **Flashing OpenWrt does not just remove `ubnt_poll_host` — it replaces the radio
   firmware.** ath10k loads stock QCA `firmware-6.bin` (10.2.4). Whatever AP-side scheduling
   primitives live in Ubiquiti's 250900-byte PTMP-AP image are gone, and no host-side work
   recovers them.
2. **This raises the floor on any airOS-vs-OpenWrt comparison to three simultaneous
   changes**: host scheduler module, host driver (`ol_ath` → ath10k), *and* radio firmware.
   An A/B test of "the same hardware" is nothing of the sort, and must be reported as such.
3. **It reframes E4/E5 (custom MAC) from "is the silicon capable?" to "can we get firmware
   source?"** Ubiquiti demonstrably built scheduled-MAC firmware for this exact chip, so
   QCA988x *is* capable. FuturaMAX's blocker is access, not silicon. That is a different —
   and more honest — go/no-go question than any report posed.
4. **It weakens the "just add external intelligence to OpenWrt" path** relative to the
   airOS-first path already recorded as the project's preferred architecture, because the
   thing being given up is larger than assumed.

**Open:** whether these images are Ubiquiti-built or Qualcomm-built-for-Ubiquiti, and how
they differ from stock 10.2.4. Extracting them from the rootfs and hashing/comparing is the
obvious next W02 step (gap G08, now much higher priority).

---

## 2. `ubnt_poll_host` — the host-side control surface, per role

```
ubnt_poll_host: Polling enabled for radio wifi0
ubnt_poll_host: noack_mode set to 0 for radio wifi0
ubnt_poll_host: DAPROT set to 0 for radio wifi0
ubnt-poll-host: [wifi0] Station priority configured to 2 (no-auto=0)
ubnt_poll_host: Fixed frame mode {enabled|disabled} for radio wifi0
ubnt_poll_host: Initialized in PTMP {AP|STA} mode for device wifi0
ubnt_poll_host: ATPC {enabled|disabled} (46/0/0/19) for radio wifi0
```

| Device | Fixed frame | Mode | ATPC |
|---|---|---|---|
| LAP-GPS | **enabled** | PTMP AP | enabled (46/0/0/19) |
| Rocket Prism 5AC | **enabled** | PTMP AP | disabled (0/0/0/28) |
| LiteAP AC | disabled | PTMP AP | enabled (36/0/0/24) |
| LiteBeam 5AC / LR / Nano loco | disabled | PTMP STA | disabled (0/0/0/25) |

Observations:

- **Fixed frame mode is live on the GPS AP and the Prism**, disabled on LiteAP AC. That is a
  real deployed configuration difference in your own network, not a lab setting.
- **`DAPROT` is a parameter no wave-1 report mentions and that does not appear in the 2017
  boot log.** Meaning UNKNOWN. Plausibly a protection mode, but do not guess — it is a
  concrete, greppable handle for W02.
- ATPC's 4-tuple `(a/0/0/b)` differs per unit; the last field tracks tx power (19/24/25/28)
  and the first appears to be an active setpoint when enabled. **INFERRED, not confirmed.**
- `Station priority configured to 2 (no-auto=0)` is airMAX Priority, set identically on all
  six.

### Scheduler internals are observable from the host

```
ubnt_poll_host: STA <OUI>:XX:XX:XX added to deferred list
```

27 occurrences each on LAP-GPS and Rocket Prism 5AC — **and zero on every STA-mode unit**.
A "deferred list" of stations is a scheduler-side data structure, and it is printk-visible on
AP-mode devices. This is the first concrete evidence of airMAX's scheduling state being
externally observable at all, and it is a strong lead for W02: if a deferred list is exposed,
other state may be reachable through the `ubnt_poll_host` char device (major 190).

---

## 3. `U-AME` is not airPrISM — C15/G09 substantially weakened

`Ubiquiti U-AME chipset detected` appears on **all six units**, including the three plain
CPEs. It is therefore a generic Ubiquiti identifier across the airMAX AC line, **not** a
marker of a special accelerator in premium hardware.

This materially undercuts the reading of C15 (glm's reseller-sourced claim that airMAX AC
uses "a proprietary ASIC [that] provides hardware acceleration to the airMAX scheduler").
The Rocket Prism — the device the airPrISM marketing actually attaches to — shows the *same*
identifier as a LiteBeam. Whatever U-AME denotes, it does not distinguish Prism hardware.

**Verdict: the "airMAX scheduler ASIC" claim remains UNSUPPORTED, and the one primary-source
lead toward it has now been checked and does not support it.** The scheduling advantage is
better explained by the custom PTMP firmware in §1 than by special silicon.

---

## 4. Radio capabilities from `board.info` (Grade A)

```
radio.1.subvendorid=0x0777      radio.1.subsystemid=0xe7fd
radio.1.chains=2                radio.1.antenna.1.gain=17 (builtin)
radio.1.txpower.max=25          radio.1.txpower.min=-4     radio.1.txpower.offset=2
radio.1.chanbw=10,20,30,40,50,60,80
radio.1.ptp_only=1  radio.1.ptp_sta=1  radio.1.ptmp_only=1  radio.1.ptmp_sta=1
radio.1.distance_limit=0        radio.1.eirp.limit=1
radio.1.regdomain_flags=fcc_new_grant
board.fcc_id=SWX-LAPGPS         board.gps=1  feature.gps=1  feature.gps.leds=1
```

- **`chanbw=10,20,30,40,50,60,80`** — airMAX exposes 30/50/60 MHz channel widths that
  standard 802.11ac does not define. Given the measured finding that your 5 GHz band is full
  and no channel can be widened conventionally, **non-standard intermediate widths are a real
  and previously unconsidered lever**. Whether ath10k/OpenWrt can reach them is UNKNOWN and
  worth a targeted check.
- GPS is confirmed present and feature-flagged on LAP-GPS only.
- **`board.fcc_id=SWX-LAPGPS`** is a direct, high-value W02 lead: FCC filings include internal
  photos and can settle the accelerator question independently of marketing pages.

## 5. Flash map — protected partitions confirmed on the AP

| mtd | Name | Size | Status |
|---|---|---|---|
| mtd0 | u-boot | 256 KiB | **NEVER WRITE** |
| mtd1 | u-boot-env | 64 KiB | **NEVER WRITE** |
| mtd2 | kernel | 1 MiB | — |
| mtd3 | rootfs | 14.4 MiB | contains the radio firmware images (§1) |
| mtd4 | cfg | 256 KiB | device config |
| mtd5 | **EEPROM** | 64 KiB | **NEVER WRITE — radio calibration** |

## 6. Driver stack, confirmed across the fleet

```
ath_pci: 10.1.467 (Atheros/multi-bss)          <- QCA vendor ol_ath offload driver
ath_hal: 0.9.17.1 (AR9380, REGOPS_FUNC, 11D)
ubnthal: module license 'Proprietary'
```

No ath10k anywhere. The earlier finding — airOS runs `ol_ath` + proprietary modules, not
ath10k — is confirmed on current production firmware (8.7.22, built 2026-02-27), not just on
a 2017 wiki boot log.

## What changed in the project because of this

- **G04 CLOSED.** All six target models are Grade-A identified; LAP-GPS is no longer the weak row.
- **C11 confirmed fleet-wide**: AR934x @ 535 MHz. google's QCA9563 @ 750 MHz is wrong for
  every unit. (Rocket Prism is QCA955x @ 720 MHz — a genuinely faster host, and the best
  candidate if any on-device controller is ever wanted.)
- **C15/G09 effectively resolved negative**: U-AME is fleet-wide, not a Prism accelerator.
- **G08 promoted to high priority**: extract and compare the PTMP firmware images.
- **New open question**: non-standard 30/50/60 MHz channel widths.
- **CUSTOM_MAC_GO_NO_GO gains its first real input** and it points toward NO-GO on stock
  firmware — while showing the chip itself is capable. That distinction matters.
