# Round 1 - Claude

**Position:** Flash both ends of the testbed to OpenWrt/ath10k-ct now, but run stock airOS as an interleaved A/B control on the same masts, and treat the uplink contention problem, not downlink, as the make-or-break question.

**Key Arguments & Proposals:**
- The scope is custom firmware, and a flashed CPE cannot associate to a stock airMAX AP, so Stage 1 airOS-only telemetry is a baseline instrument, not the product. Keep 1 AP + N CPEs on airOS as the control arm and 1 AP + N on OpenWrt, swapping roles weekly so RF drift hits both arms.
- Downlink is already a single-transmitter problem. mac80211 airtime scheduler, AQL and CAKE at the AP give us most of TDMA's downlink fairness for free. Measure this first and publish it early.
- Uplink is where CSMA loses. Directional CPEs at the same site are mutually hidden. Propose a host-side "soft poll": AP-driven per-station TXOP grants via power-save triggers plus tight RTS threshold, measured against a firmware-level patch as the fallback.
- Control boundary, stated honestly: firmware owns per-frame rate and A-MPDU. Host owns ratemask per station, AQL deficits, TXQ limits, coverage class, RTS, channel/width, and the scheduler order. Prove what the host knobs buy before touching firmware.
- Safety protocol: never write mtd0 or ART; boot-count watchdog with automatic rollback partition; POE power-cycle as last resort; every experiment carries a revert script that runs unattended.
- Auto-research loop: interleaved ABAB trials, blocked by hour and weather, with A/A runs to establish the noise floor before any keep/rollback decision. Minimum detectable effect set from that floor, not chosen by hope.

**Assumptions & Trade-offs:**
- Assuming ath10k-ct firmware is stable enough under 20 stations with ratemask changes every few seconds. Sacrificing peak MCS aggressiveness for determinism.
- Assuming the AR9342 CPU cannot run CAKE at line rate. Shaping lives at the AP and core, not the CPE.
- Sacrificing the ability to migrate one CPE at a time in production. This is a full-cutover architecture.

**Risks & Failure Modes:**
- Uplink collapse above roughly 8 active CPEs from hidden-node collisions. This is the single result that could kill the CSMA path.
- Firmware crash loops from ratemask or AQL edge cases, leaving a mast dark until POE cycle.
- Auto-research loop chasing weather noise and "keeping" regressions. Guard with A/A calibration and holdout periods.
- Bricking from a mistaken partition write on SPI NOR.

**What Would Change My Mind:**
- Loaded uplink jitter on OpenWrt measurably worse than airOS at 10 CPEs with no host-side mitigation closing the gap. Then a firmware TDMA patch becomes mandatory and the roadmap reorders.
- ath10k-ct firmware instability above 12 stations. Then Stage 1 airOS intelligence becomes the only shippable product for a long time.

**Confidence:** 62%
