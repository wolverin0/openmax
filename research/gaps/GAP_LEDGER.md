# FuturaMAX gap ledger

Summary: every evidence gap wave 1 left open, classified filled / partially_filled /
not_found / requires_physical_experiment, with the method and owner that closes it.
Keywords: gap ledger, R4, targeted research, critical path, LAP-GPS, ubnt_poll_host,
airtime scheduler, rate control ownership, A-MPDU control, raw-mode.
Read when: assigning targeted research, or deciding whether a question needs a search, a
source read, or hardware. Current verdict: **Tier-1 and G08/G09/G21/G22 all CLOSED.** Live
work is now G10 (spectral under airOS), G24 (raw-mode) and the effect-size checks G11-G16.
Status: CURRENT (2026-08-08).

## Classification

- `filled` — answered by a primary source that has been opened and read.
- `partially_filled` — answered for adjacent hardware or at an unclear date.
- `not_found` — searched by at least one wave-1 run and not located.
- `requires_physical_experiment` — no document can answer it.

## Tier 1 — critical path — ALL CLOSED 2026-08-08

| ID | Gap | Class | Method | Owner |
|---|---|---|---|---|
| G01 | ~~airtime scheduler on ath10k~~ | **filled** | **Yes, hooks exist (2017 claim superseded) — but on QCA988x it runs on ESTIMATED airtime with a 6 Mbps fallback cliff when peer stats are off.** `QCA988X_CONTROL_BOUNDARY.md` §2. | done |
| G02 | ~~rate control ownership~~ | **filled** | **Firmware.** ath10k sets `HAS_RATE_CONTROL`; no `rate_control_ops`, no minstrel reference. Minstrel-HT does not run. | done |
| G03 | ~~A-MPDU / Block-ACK control~~ | **partially_filled** | Device-wide setter exists (`htt_max_amsdu_ampdu` → HTT AGGR_CFG in ath10k-ct); **not** per-peer, and BA bitmaps are not exposed. Firmware honouring it is UNVERIFIED. | E2 |
| G04 | ~~silicon in LAP-GPS and the rest~~ | **filled** | **Six live units read.** All QCA988x Wave 1 on AR934x @535 MHz; Rocket Prism 5AC on QCA955x @720. `HARDWARE_MATRIX.md`. | done |

## Tier 2 — opened by primary evidence, not by wave 1

| ID | Gap | Class | Method | Owner |
|---|---|---|---|---|
| G05 | `ubnt_poll_host` / `ubnthal` internals | **partially_filled** | Both modules now in hand from the public image (186 KB / 412 KB, MIPS). Parameters known from printks; internal logic needs disassembly — see G22. | W02 |
| G06 | airOS runs `ol_ath 10.1.467` (QCA vendor offload driver), not ath10k. How does its control surface differ, and does any airMAX behaviour survive a driver swap? | not_found | QCA `qcawifi`/`ol_ath` sources where public; compare WMI/HTT generation against ath10k. | W02/W03 |
| G07 | `raw-mode` on stock ath10k firmware — what does it expose? | not_found | Duplicated as **G24**, which now carries the priority: it is the last unexplored lever against the custom-MAC NO-GO. | W03 → E2 |
| G08 | ~~Does the airOS radio firmware differ from stock QCA 10.2.4?~~ | **filled** | **YES — three custom per-mode/per-role images containing Ubiquiti polling code absent from stock.** Extracted from the PUBLIC download, no device needed. See `knowledge/RADIO_FIRMWARE_ANALYSIS.md`. | done |
| G09 | ~~`U-AME` / the "airMAX ASIC" claim~~ | **filled (negative)** | U-AME appears on all six units incl. plain CPEs, so it is not an accelerator marker. The scheduling advantage is explained by custom firmware (G08), not silicon. | done |
| G10 | ~~Spectral without leaving airOS?~~ | **filled** | **YES.** `/bin/ubntspecd` is RUNNING on the production AP (`-i wifi1 -j airview1`). Open question is only whether it can target `wifi0` and at what cost. | done |

G10 matters disproportionately: if spectrum telemetry works under stock airOS, the highest
ranked candidate in every wave-1 run becomes available **without giving up airMAX** — which
is exactly the airOS-first architecture already recorded as the project's preferred path.

## Tier 3 — effect sizes to verify against the paper PDFs

Each is a wave-1 number that at least two runs stated differently (C05–C09). All are
`partially_filled`: the paper exists and is reachable, the number has not been checked.

| ID | Claim to verify | Disputed between |
|---|---|---|
| G11 | hMAC hidden-node aggregate: 4.2→8.8 Mbit/s, or 12→28 Mbps? | cg vs go |
| G12 | WiLDNet: which link distance, which numbers, and which OS/driver? | cg vs go vs gl |
| G13 | PNOFA: +29% max / +17% mean, or +18–32%? | cg+gk vs go |
| G14 | NeuRA: +14%/+16% with non-overlapping CIs, or "−40% prediction error"? | cg vs go |
| G15 | GPS Sync magnitude — four different vendor-grade figures, none research-grade. | cg vs gl vs mi |
| G16 | AQL on ath10k: what was actually measured, and were the reported underflow bugs fixed? | gl vs gk vs go |

## Tier 4 — searched and not found (record so nobody re-searches)

| ID | Gap | Note |
|---|---|---|
| G17 | Any published experiment comparing OpenWrt/ath10k against airMAX AC TDMA on a loaded multi-CPE outdoor sector. | cg searched and found none; go supplied numbers with no locator (C04). **This is the project's central question and no document answers it.** → `requires_physical_experiment` |
| G18 | A Ubiquiti patent that can be honestly summarised as "the propagation-aware airMAX TDMA scheduling patent". | cg looked and declined to name one. Candidates exist (US10057021B2, US20250266982A1) but need claim-by-claim reading. |
| G19 | Primary evidence for a separately programmable airMAX hardware accelerator. | Only a reseller marketing page (C15). G09 is the live lead. |
| G20 | Open-source QCA988x target firmware. | Never released. Not a gap to keep searching. |

## What does *not* need more research

Six runs of the same prompt produced one consensus and seventeen disagreements. A seventh
run adds a seventh opinion. **Wave 2, if run at all, must be narrowly scoped to specific
gaps above and must require the model to quote the primary source, not summarise it.**

The Tier-1 items G01-G03 were answered by reading three source trees, and G04 by reading six
radios. None needed a web-research agent. G08 was answered by downloading a public firmware
image. **The pattern is consistent: every question that actually moved this project was
settled by opening a primary artifact, not by asking another model.**

## Added 2026-08-08 after the hidden-config-key discovery

| ID | Gap | Class | Method | Owner |
|---|---|---|---|---|
| G29 | ~~Do the 62 hidden `radio.*` keys work?~~ **PROVEN YES** — `polling_ff_flex/dur/dl_ratio` flipped `ubnt_poll_host` from "Fixed frame mode disabled" to "enabled", survived reboot, fully reversible. Remaining: which of the other keys work, and whether any value IMPROVES anything (needs a link). Original text: `ubntbox` references fixed-frame scheduler params (`polling_ff_dur`, `polling_ff_dl_ratio`, `polling_ff_cbp_slots`, `polling_ff_timing`, `polling_ff_sta_rx_rssi_th`, `polling_daprot`) plus aggregation (`ampdu.frames`, `ampdu.status`, `amsdu`) and rate (`rc_mode`, `rate.mcs`) — none in the default config or the web UI. **This is the surface the whole project was looking for.** | requires_physical_experiment | Add key to system.cfg, `cfgmtd -w`, reboot, verify via driver getter / dmesg / over-the-air. One key at a time. Lab unit. | **E2 — top priority** |
| G30 | Which of the 62 are settable inputs vs read-only status keys? | not_found | Cross-reference against `ubntbox` usage and the udapi Lua modules that also reference them. Offline. | W02 |
| G31 | Does `radio.1.web_exclude` gate UI visibility, and does it reveal a documented-but-hidden knob list? | not_found | Read `lib/lua/udapi/cfg_utils.lua` from the extracted rootfs. Offline, cheap. | W02 |

## Added 2026-08-08 after the airOS control-surface sweep

| ID | Gap | Class | Method | Owner |
|---|---|---|---|---|
| G25 | **Do the airOS set-ioctls actually take effect?** `AMPDULim`/`AMPDUFrames`/`LDPC` getters return "Operation not supported", so the values cannot be read back. Setters are declared but UNVERIFIED. | requires_physical_experiment | Issue a set on a **LAB** unit and measure over the air. Never on production. | E2 |
| G26 | Decode `setHALparam`/`getHALparam` parameter IDs. | **not_found (attempted)** | String analysis of `umac.ko` and `ath_hal.ko` found only the two ioctl NAMES — the param IDs are numeric constants in code, with no enum strings. **Requires MIPS disassembly of the ioctl handler.** Explicitly NOT attempted by fuzzing `getHALparam` on production: probing an undocumented vendor ioctl on radios serving customers risks wedging them. Lab unit only. | W02 (disasm) |
| G27 | Can `ubntspecd` be pointed at `wifi0` (the 5 GHz serving radio), and what does it cost serving traffic? | requires_physical_experiment | Lab unit. | W09 |
| G28 | Is RTS/CTS (`enablertscts`, currently **0**) worth enabling on a hidden-node sector, or does airMAX scheduling already remove the need? | requires_physical_experiment | One-ioctl A/B on a lab/low-risk sector. | E3 |

## Added 2026-08-08 after the firmware extraction

| ID | Gap | Class | Method | Owner |
|---|---|---|---|---|
| G21 | ~~Cross-version firmware diff~~ | **filled** | **14 releases 2016-2026 swept.** Role-split (ptmp_ap + ptmp_sta replacing a generic image) landed in **v8.3.1, 2017-07-28**, the Fixed-Frame/GPS-Sync release. `ubnt-poll` present since v7.2.4. Radio firmware byte-identical 8.7.22=8.7.25 and 8.7.13=8.7.17. | done |
| G22 | ~~Host/target split~~ | **filled** | **`ubnt_poll_host.ko` has ZERO scheduling primitives** (no slot/tdma/airtime/sched/tsf/framing across 150 functions). It is control-plane: station table, 802.11 management hooks, IE negotiation, config push to target. **The scheduler is in firmware.** | done |
| G23 | What does the PtMP/AP-only firmware code do? | **partially_filled** | PtMP-only strings (`POLL-ENABLE`, `LASTTXPEND`, `NO-TX-DETECT`, `CONG-DROP`, `NONPAUSE_TID`, `TX ABORT`) read as a polling scheduler with per-station queue accounting. INFERRED — string archaeology, not disassembly. | W02 |
| G24 | Is `raw-mode` (advertised by stock ath10k firmware on this chip) enough to recover any MAC authority? The last unexplored lever against the custom-MAC NO-GO. | not_found | ath10k raw-encap patches, then physical test. | W03 → E2 |
