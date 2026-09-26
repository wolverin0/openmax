# The airOS control surface — what stock airMAX already exposes

Summary: the airOS vendor driver DECLARES 134 private ioctls on the radio and ~90 on the VAP,
but lab testing shows the setters are silently discarded. The reachable airOS control surface
is the much shorter `radio.*` key list in system.cfg, and it excludes aggregation and rate control.
Keywords: iwpriv, AMPDULim, AMPDUFrames, rc_mode, vht_mcsmap, enablertscts, damode, dacount,
distance, chanbw, EDCA, cwmin, txoplimit, get_total_PER, ubntspecd, airview, G10.
Read when: choosing between the airOS-first and OpenWrt paths, or picking a candidate technique.
Current verdict: **airOS is configurable via `cfgmtd -w` + reboot, and 62 UNDOCUMENTED
`radio.*` keys exist that the web UI never exposes — including the airMAX fixed-frame
scheduler's own parameters. PROVEN live: adding `polling_ff_flex/dur/dl_ratio` flipped the
scheduler from "Fixed frame mode disabled" to "enabled".** Cost is one reboot per change
(slow-loop only). Status: CURRENT. Evidence grade A.

## How this was collected

Read-only SSH to a live production LiteAP GPS (`sysid 0xe7fd`, airOS WA.v8.7.22, driver
`ath_pci 10.1.467`). **Only getter ioctls were invoked; no `set` was issued on production
hardware.** Full enumeration: `research/raw/hardware/lap-gps-control-surface-2026-08-08.txt`.

## CORRECTION (2026-08-08, same day) — read this before the table below

An earlier version of this file claimed airOS "exposes MORE control than ath10k" and that the
PNOFA aggregation hook was available on the stock stack. **That was an overclaim built on the
*existence* of ioctl names.** I flagged the "declared, not demonstrated" caveat and then leaned
on the claim anyway in the summary. Lab testing on a clientless LiteAP AC (LAP-120, v8.5.12)
subsequently failed to change anything:

| Path tried | Result |
|---|---|
| `iwpriv wifi0 distance 5000` | returns rc=0, **value unchanged** (100000) |
| `iwpriv ath0 enablertscts 1` | returns rc=0, **value unchanged** (0) |
| edit `/tmp/system.cfg` + `ubntconf -c` | config file changes, **radio does not** |
| edit `/tmp/system.cfg` + `rc.softrestart` | config file changes, **radio does not** (chanbw stayed 40) |

**The set-ioctls accept writes silently and discard them.** The ioctl list is a map of what the
*driver* implements, not of what *airOS* lets you reach.

### RESOLVED the same day — the working path is `cfgmtd -w` + reboot

| Step | Result |
|---|---|
| edit `/tmp/system.cfg` (`radio.1.chanbw` 40→20, `ieee_mode` to match) | — |
| `cfgmtd -w -p /etc/ -f /tmp/system.cfg` | RC=0, `Storing Active`, `Active->Backup` |
| `reboot` | — |
| verify | **`get_chanbw` = 20 ✅** — the radio followed |
| restore to 40 + `cfgmtd -w` + reboot | **`get_chanbw` = 40 ✅** clean revert |

**So airOS IS controllable.** The mechanism is: write the config file, persist it to the `cfg`
flash partition with `cfgmtd -w`, reboot. This is exactly what the web UI does on "Apply", and
it writes only the `cfg` partition — never u-boot, u-boot-env or EEPROM.

Two consequences that matter:

1. **Every `radio.*` key in system.cfg is a real, testable lever** — including the airMAX
   polling knobs (`polling`, `pollingpri`, `pollingnoack`) and ACK timing
   (`ackdistance`/`acktimeout`, with `ack.auto` to disable automatic override).
2. **A change costs a reboot.** There is no fast closed-loop control on airOS — no per-frame,
   no per-second adaptation. airOS supports **slow-loop optimisation only** (minutes to hours),
   which is precisely the timescale the research concluded was realistic anyway. Plan
   network-wide optimisation, not reactive control.

The iwpriv setters remain useless (silently discarded) — they are not the configuration path.

## What the config surface actually contains

From `/tmp/system.cfg` on a live unit — this is the real airOS control surface, and it is much
narrower than the ioctl list:

```
radio.1.ack.auto=enabled      radio.1.ackdistance=600     radio.1.acktimeout=31
radio.1.polling=enabled       radio.1.pollingnoack=0      radio.1.pollingpri=
radio.1.chanbw=40             radio.1.cwm.enable=0        radio.1.cwm.mode=1
radio.1.txpower=28            radio.1.ieee_mode=11acvht40 radio.1.ptpmode=0
```

**Present and genuinely airMAX-specific:** polling on/off, ackless (`pollingnoack`), airMAX
priority (`pollingpri`), ACK distance/timeout with an auto mode, channel width, TX power.

**Absent from the DEFAULT config — but see below, this turned out not to mean absent from the
software.**

### CORRECTION #2 — the config surface is far larger than the default file or the web UI

Scanning the airOS binaries for `radio.*` key references found **62 keys that `ubntbox` reads
but that appear in neither the running config nor the web UI.** They are not a random tail —
they are the airMAX fixed-frame scheduler's parameter set, plus the aggregation and rate
knobs this file had just declared unreachable:

**Fixed-frame / polling scheduler**

| Key | Apparent meaning |
|---|---|
| `radio.1.polling_ff_dur` | fixed-frame duration |
| `radio.1.polling_ff_dl_ratio` | downlink/uplink ratio |
| `radio.1.polling_ff_cbp_slots` | contention-based-period slot count |
| `radio.1.polling_ff_timing` | frame timing |
| `radio.1.polling_ff_flex` | flexible framing |
| `radio.1.polling_ff_dl_arq`, `_ul_arq` | ARQ per direction |
| `radio.1.polling_ff_dl_ctrl_rate`, `_ul_ctrl_rate`, `_ctrl_rate_40` | control-frame rates |
| `radio.1.polling_ff_sta_rx_rssi_th` | per-station RX RSSI threshold |
| `radio.1.polling_daprot` | the `DAPROT` printk seen in dmesg (gap G-DAPROT) |
| `radio.1.polling_fh`, `polling_11ac_11n_compat` | — |

**Aggregation / rate / RF** — previously reported as unreachable, incorrectly:
`radio.1.ampdu.status`, `radio.1.ampdu.frames`, `radio.1.amsdu`, `radio.1.rc_mode`,
`radio.1.rate.mcs`, `radio.1.mcastrate`, `radio.1.ani.status`, `radio.1.rx_sensitivity`,
`radio.1.frag`, `radio.1.atpc.status`, `radio.1.atpc.threshold`, `radio.1.atpc.sta.status`,
`radio.1.scan_list.*`, `radio.1.scanbw.status`, `radio.1.cmsbias`.

`radio.1.web_exclude` (referenced by `cfg_utils.lua`) indicates an explicit mechanism for
hiding keys from the web UI — consistent with these being deliberately unexposed.

### PROVEN 2026-08-08 — the hidden keys are live and reach the airMAX scheduler

Tested on the lab LiteAP AC. Three keys that exist in **neither the config file nor the web UI**
were appended to `system.cfg`, persisted with `cfgmtd -w`, and the unit rebooted:

```
radio.1.polling_ff_flex=0
radio.1.polling_ff_dur=8000
radio.1.polling_ff_dl_ratio=75
```

Result, straight from the proprietary airMAX module's own printk:

```
BEFORE:  ubnt_poll_host: Fixed frame mode disabled for radio wifi0
AFTER :  ubnt_poll_host: Fixed frame mode enabled  for radio wifi0
```

**The undocumented keys are honoured, and they reach `ubnt_poll_host` — the airMAX scheduler
module itself.** They also survived the reboot intact rather than being stripped by config
validation. Removing the keys and re-persisting returned the unit to `Fixed frame mode
disabled`, confirming the change was caused by the keys and is fully reversible.

This is the central capability the project was looking for: **airMAX's fixed-frame scheduler
parameters are settable.** `polling_ff_dur` appears adjacent to the literal `8000` in
`ubntbox`'s string table, consistent with a microsecond frame duration and with Ubiquiti's
documented 5 ms / 8 ms framing options.

**What is still NOT established:** that any particular value *improves* anything. Enabling
fixed-frame on a clientless bench AP proves the control path, not a performance benefit.
Measuring benefit needs a real link — see the caveat on aggregation below, which remains
untested.

## The original enumeration (still accurate as a driver-capability map)

The ioctls below exist in the driver. Several are unreachable from airOS userspace. Kept
because it maps what the *vendor driver* implements — useful for firmware/driver work, not a
list of things you can change today.

`iwpriv wifi0` lists **134 entries**. `iwpriv ath0` lists roughly 90 more. Between them stock
airOS exposes, on the radio the airMAX scheduler is actively driving:

| Capability | ioctl | vs ath10k |
|---|---|---|
| **A-MPDU enable / length limit / subframe count** | `AMPDU` (1006), `AMPDULim` (1007), `AMPDUFrames` (1008) | ath10k-ct offers only a device-wide `htt_max_amsdu_ampdu` |
| **Rate-control mode** | `rc_mode` (019F) | ath10k: firmware-owned, no mode selector |
| **Rate-control retries** | `rc_retries` (0133) | ath10k: not exposed |
| **VHT MCS map** | `vht_mcsmap` (012F) | ath10k: constrained contiguous masks only |
| **RTS/CTS enable** | `enablertscts` (012B) | comparable |
| **Dynamic ACK mode / count / period** | `damode` (1095), `dacount` (1094), `daperiod` (1096) | **no ath10k equivalent** |
| **Distance** | `distance` (1093) | ath10k: fragile coverage-class register hack |
| **Channel bandwidth incl. 30/50/60 MHz** | `chanbw` (1098) | ath10k: standard widths only |
| **EDCA per AC** (cwmin/cwmax/aifs/txoplimit/ACM/noack) | `cwmin`…`noackpolicy` (0001-0006) | mac80211 exposes these too |
| **TX/RX chainmask** | `txchainmask`/`rxchainmask` (1001/1002) | comparable |
| **LDPC** | `LDPC` (1020) | not host-selectable on ath10k |
| **SW retry, aggregated and non-aggregated** | `aggr_swretry` (1075), `nonaggr_swretry` (1074) | **no ath10k equivalent** |
| **Total PER telemetry** | `get_total_PER` (1059) | ath10k: sampled peer stats only |
| **Offload stats** | `enable_ol_stats` (200C / 0131) | roughly comparable |
| **Diagnostic log subsystem** with timestamp resolution | `dl_reporten`, `dl_reportsize`, `dl_tstamprez`, `dl_loglevel`, `dl_vapon/off`, `dl_modon/off` | **no ath10k equivalent** |
| **HAL parameter get/set** | `getHALparam`/`setHALparam` (8BE0/8BE1) | no equivalent |
| Antenna gain / cable loss / sensitivity | `ant_gain`, `cable_loss`, `sens_level` | partly via regulatory paths |
| Station kickout, deauth count, DSCP→TID map | `sta_kickout`, `setdeauthcnt`, `dscp_tid_map` | partly |

### Why this table is a capability map, not a to-do list

`getAMPDU`, `getAMPDULim`, `getAMPDUFrames` and `getLDPC` return **"Operation not supported"**
— those getters collide on ioctl `8BE1` (`getHALparam`) and are unimplemented, so nothing here
can be read back. And the setters that *do* have getters (`distance`, `enablertscts`) were
tested on a lab unit and **silently discarded the written value**.

So this table records what the **vendor driver implements**, which is genuinely useful for
firmware/driver work and for understanding what the silicon supports. It does **not** record
what an operator can change on a running airOS box. For that, see the config surface above.

## Measured configuration of a live production AP

Read from the LiteAP GPS serving real subscribers:

| Setting | Value | Comment |
|---|---|---|
| `txchainmask` / `rxchainmask` | 3 / 3 | both chains, 2x2 |
| `distance` | 900 | |
| `damode` / `dacount` / `daperiod` | 0 / 25 / 0 | Dynamic ACK |
| `chanbw` | 20 | 20 MHz — consistent with the measured finding that the band has no room to widen |
| `ant_gain` / `cable_loss` | 17 / 0 | |
| `get_total_PER` | 0 | telemetry live and readable |
| **`enablertscts`** | **0** | **RTS/CTS is OFF on this sector** |
| `rc_mode` / `rc_retries` / `vht_mcsmap` | 0 / 0 / 0 | defaults — nothing tuned |
| `ptpmode` | 2 | PtMP |
| `multiq` | 1 | multi-queue on |
| EDCA cwmin (AC0-3) | 4 / 4 / 3 / 2 | |
| EDCA cwmax (AC0-3) | 6 / 10 / 4 / 3 | |
| EDCA aifs (AC0-3) | 3 / 7 / 1 / 1 | |
| EDCA txoplimit (AC0-3) | 0 / 0 / 3008 / 1504 | |

Two observations worth acting on:

1. **RTS/CTS is disabled** on a sector with known hidden nodes. Whether it *should* be on is
   an empirical question — airMAX's scheduler may already remove the need — but it is a
   one-ioctl experiment with a clear hypothesis, and nobody has tested it here.
2. **Every rate-control knob is at its default.** `rc_mode`, `rc_retries` and `vht_mcsmap`
   are all 0. The supervisory rate-control idea ranked highly in wave 1 has simply never
   been tried on this network.

## G10 answered: spectral works under stock airOS

```
/bin/ubntspecd -w -t -a -i wifi1 -j airview1 -m 4 -f     (running)
/bin/airview      /bin/ubntspecd (47,192 B)
```

A Ubiquiti spectral daemon is **already running** on the production AP. Combined with
`ath_spectral 2.0.0` and `HAL_CAP_SPECTRAL_SCAN: Capable` in the boot log, this confirms
spectrum telemetry is reachable **without leaving airOS**.

Caveat: the running instance is bound to `wifi1` (the 2.4 GHz AR9380 radio), not `wifi0` (the
5 GHz QCA988x carrying subscribers). Whether `ubntspecd` can be pointed at `wifi0`, and at
what cost to the serving radio, is **UNKNOWN** and is the obvious next experiment — on a lab
unit, since it touches the serving radio.

## Why this changes the plan

The airOS-first decision still stands, but for a **weaker** reason than this file first
claimed. The honest position:

- OpenWrt gives you mac80211's queueing (AQL, FQ-CoDel, airtime) but costs you the airMAX
  scheduler *and* the custom radio firmware, and its airtime estimate degrades to a 6 Mbps
  assumption without peer stats.
- airOS keeps the scheduler and the firmware, and exposes **polling, ackless, airMAX priority,
  ACK distance/timeout, channel width and TX power** — real levers, but a short list, and one
  that does **not** include aggregation or rate control.
- **Neither stack gives you the aggregation control PNOFA needs.** That candidate is currently
  blocked on both paths, which is a materially worse position than this file first reported.

The strongest candidate techniques from wave 1 — adaptive aggregation, supervisory rate
constraint, hidden-node/RTS policy, distance-timing calibration, spectrum-driven channel
planning — all have plausible airOS-side hooks. The main thing OpenWrt still offers that
airOS does not is modern **queue management** (CAKE/FQ-CoDel/AQL), and that can be applied
at the POP/router rather than on the radio.

## Next steps, in priority order

1. ~~Settle whether airOS config can change the radio.~~ **DONE — it does**, via `cfgmtd -w`
   + reboot. See the RESOLVED section above.
2. **A/B the airMAX levers that exist in config** — `polling`, `pollingnoack`, `pollingpri`,
   and `ackdistance`/`acktimeout` with `ack.auto=disabled`. These have never been tuned on this
   network and are now demonstrably reachable. Needs a second radio to form a link.
3. Point `ubntspecd` at `wifi0` and measure the cost to serving traffic (spectral is the one
   capability confirmed working under stock airOS).
4. Aggregation is blocked on both stacks — either find a firmware-level route or drop the
   PNOFA candidate. Do not keep it in the backlog as "available".
5. `setHALparam` ID decoding needs MIPS disassembly (string analysis already failed).
