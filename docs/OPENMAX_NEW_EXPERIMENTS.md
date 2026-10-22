<!-- doc-head: Prioritized backlog of 10 falsifiable OpenMax experiments (FMX-0016..FMX-0025) ordered by ROI/risk with PASS/FAIL/STOP/ROLLBACK gates -->
Integrates confirmed Stage 10/11 and Step 1C (run17 PASS) baselines so proven work is never repeated.
Every experiment specifies exact sysid/firmware, baseline, counterfactual, primary/secondary metrics, 1-day refutation test, and deterministic rollback.
No production mutation or unauthorized radio access is permitted; Stage 0/1/2/3/4/5 progression gates apply.
<!-- /doc-head -->

# OpenMax Prioritized New Experiment Backlog (`FMX-0016` – `FMX-0025`)

**Date**: 2026-10-22  
**Parent Deliverable**: [`docs/OPENMAX_MASTER_RESEARCH_PROMPT.md`](OPENMAX_MASTER_RESEARCH_PROMPT.md) §§7–10  
**Prerequisite Audit (What We Do NOT Repeat)**:
- **`FMX-0001..0014` (`CONFIRMED`)**: Hardware inventory (`6` models), bootloader recovery (`urescue`), Gateway `CAKE` + CPE `CoTSQ`/`fq_codel`, OpenWrt `AQL` + `ATF` + `WMM AC_VO Bypass`, `VHT80/40/20` spectral/width optimization, and `ratemask-CT` WMI verification.
- **`FMX-0015` / `Step 1C` (`run17` `PASS` — `2026-10-22`, [`docs/BENCH_PLAN.md`](BENCH_PLAN.md#L1-L58))**: Direct 100% AP-side zero-touch association (`auth=true`, `assoc=true`, `authorized=true`, `wds=true`, `aid=1`, `71.735s` stable, bidirectional `ping6` `0%` loss, exact RAM/config restoration) between `LAP-120` (`OpenWrt 24.10.4` with `wds=1` + `0.5s` broadcast-triggered Ubiquiti IE withdrawal) and **100% unmodified Stock `airOS WA.v8.7.25` `Loco195`** (`0xe7fa`).
- **Stage 11A & 11B Static + Bench Qualification (`CONFIRMED`, [`docs/STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md`](STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md), [`docs/STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md`](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md))**: `Rocket Prism 5AC Gen2` (`0xe7e9`, `XC.v8.7.25`) GPIO `13..16` band-edge `prism` table + `IRQ 64` `ath-spectral-filter` verified live; `LTU-Lite` (`0xae08`, `afltu.v2.4.0`) `NO_LDPC=0`, `NO_OFDMA=0`, `autoMcsCeiling=31` (`4096-QAM` `12x`, `560.64 Mbps` @ `40 MHz` `frmcfg`) and `ofdma_subbands` numeric bitmask verified live in sysfs.

---

## 1. Summary Ranking Table (`FMX-0016` – `FMX-0025`, Ordered by ROI / Information-to-Risk Ratio)

| Exp ID | Title & Research Question | Stage | Target Hardware & Firmware | Expected Value / ROI | Risk | Early 1-Day Refutation Criterion |
| :---: | :--- | :---: | :--- | :---: | :---: | :--- |
| **`FMX-0016`** | **Passive Fleet Cooperative Sensor Observatory (Airtime-Tax, Differential Outage & Cross-Sector Reassociation Recommender)** | Stage 1 (Read-Only) | NOC Controller + Existing `mca-status` / `wstalist` / `ameeng.cgi` across `1,800` radios | **Very High** (Immediate WISP QoE & capacity gain, zero RF risk) | **Zero** (100% passive read-only) | Refuted if differential correlation fails to separate AP/sector events from single-CPE foliage/alignment drops with `>= 90%` precision on historical incidents. |
| **`FMX-0017`** | **Step 1D / OTA Discovery-IE Withdrawal & Multi-CPE Loaded Goodput Qualification on Unmodified Stock `airOS 8`** | Stage 2 (Bench) | `LAP-120` (`0xe8e5` OpenWrt `24.10.4` `wds=1`) $\leftrightarrow$ Stock `WA.v8.7.25` `Loco195` (`0xe7fa`) | **Critical** (Unlocks zero-touch AP migration without touching CPEs) | **Low** (Isolated bench, RAM-only) | Refuted if an already-associated Stock CPE disconnects when the AP temporarily re-injects the `msg_type=1` Beacon IE for a newly scanning 2nd Stock CPE (`Gate 2` collision). |
| **`FMX-0018`** | **PoE / Ethernet Link-Partner Flap, Cable SNR & Memory-Leak Early-Warning Detector** | Stage 1/2 (Read-Only) | Stock `airOS 8` (`WA`/`XC` `ethtool`/`dmesg`/`/proc/meminfo`) & `LTU` (`amesoc3`) | **High** (Eliminates misdiagnosed "RF tickets" caused by water-damaged UTP/PoE) | **Zero** (Read-only) | Refuted if `ethtool` / GMAC PHY counters on `AR8033` / `AR9342` do not increment prior to 100Mbps$\to$10Mbps downshift or watchdog reboot. |
| **`FMX-0019`** | **`Rocket Prism 5AC Gen2` (`0xe7e9`) `wifi1` (`AirView` AHB + `IRQ 64` TX-Blanking) Zero-Impact Continuous Spectrum Observatory** | Stage 2 (Bench) | `Rocket Prism 5AC Gen2` (`0xe7e9`, `XC.v8.7.25`) + `Loco195` (`0xe7fa`) | **High** (Zero-sawtooth 5 GHz spectrum scanning during active PtMP load) | **Low** (Bench read/telemetry) | Refuted if running `ubntspecd` / `wifi1` sweep degrades `wifi0` (`QCA9880v2`) loaded TCP goodput by `> 2%` or increases `p99` RTT by `> 1.5 ms`. |
| **`FMX-0020`** | **RAM-Only `/tmp/fmx_micro_worker` Idle-Compute Bench Qualification (`5%`/`10%` Duty Cycle & `< 200 ms` Traffic Preemption)** | Stage 2 (Bench) | `Loco195` (`0xe7fa`, `AR9342` `64 MB`) & `LTU-Lite` (`0xae08`, `amesoc3` `256 MB`) | **High** (Proves or falsifies Section 5 distributed compute on real hardware) | **Low** (`/tmp` RAM-only, 90s TTL) | Refuted if `< 200 ms` preemption fails under burst load, `p95` RTT rises by `> 0.5 ms`, or `MemFree + Cached` drops below `18 MB`. |
| **`FMX-0021`** | **`LTU-Rocket` (`0xae02`) $\leftrightarrow$ `LTU-Lite` (`0xae08`) Over-the-Air `4096-QAM` (`12X`, `0x1f`) & `OFDMA` Subband Notching** | Stage 2/3 (Bench) | `LTU-Rocket` (`aflturocket-2.4.2`) + `LTU-Lite` (`afltu-2.4.0/2.4.2`) | **High** (`+20%` peak spectral efficiency `10x -> 12x` = `560.64 Mbps` @ `40 MHz` if FPGA/RF passes) | **Low** (Bench sysfs/RAM only) | Refuted in 1 day if `LTU-Rocket` Arria 10 FPGA clamps OTA constellation to `1024-QAM` (`23`) or if LDPC `bler_rate` exceeds `5%` at high SNR (`>= 38 dB`). |
| **`FMX-0022`** | **`QCA988x` Single-Radio Simultaneous `STA + AP` / `STA + 802.11s` Same-Channel Relay Feasibility & Airtime-Tax Gate** | Stage 3 (Bench) | `LAP-120` (AP) + `CPE-A` (OpenWrt `QCA988x` Relay) + `CPE-B` (Weak CPE) | **Medium** (Settles Section 2.A single-radio cooperative relay question definitively) | **Medium** (Bench RF only) | Refuted in 1 day if (a) `10.1-ct-8x-__fW-022` / `10.2.4` fails simultaneous `STA+AP` beacon/auth under load, (b) directional sidelobe `A<->B` SNR `< 15 dB`, or (c) 2-hop half-duplex airtime reduces net sector goodput. |
| **`FMX-0023`** | **Secondary `2.4 GHz` Management Radio (`wifi1` `QCA9558` / `WA` Management) Short-Range Emergency Relay & Link-Budget Gate** | Stage 2/3 (Bench) | `Rocket Prism 5AC Gen2` (`0xe7e9`) / Dual-Radio CPEs (`wifi1` `2.4 GHz`) | **Low-Medium** (Settles Section 2.B with measured link budget, expected `NO-GO` beyond `< 50 m`) | **Low** (Bench only) | Refuted in 1 day if internal PCB antenna gain (`~1–2 dBi`) + `2.4 GHz` urban noise floor yields `< 10 Mbps` or `> 5%` PER at `30–50 m` non-LOS. |
| **`FMX-0024`** | **Dual-CPE Ethernet Back-to-Back Cooperative Relay (`CPE-B -> Ethernet -> Aux-Radio @ CPE-A -> AP`) vs Sector Re-Parenting** | Stage 3 (Bench) | 2x CPEs coupled via L3/Ethernet or re-parented to alternate AP BSSID | **High** (Practical engineering solution for obstructed subscribers) | **Low** (Standard topology) | Refuted only if cost/complexity exceeds standard pole re-location or alternate-sector re-parenting. |
| **`FMX-0025`** | **Central NOC `ZeroClaw` Copilot vs Deterministic Rule Engine (`controller/advisory_mode.py`) Blind Incident-Triage Benchmark** | Stage 1 (Offline) | NOC Server (`omarchygwy`) running replay of `stage1_production_telemetry_audit.json` | **Medium** (Quantifies whether LLM copilot adds diagnostic precision over deterministic rules) | **Zero** (100% offline replay) | Refuted if `ZeroClaw` fails to beat deterministic rule classification accuracy (`100%` on chain-imbalance/airtime-tax) or hallucinates unsafe RF mutations. |

---

## 2. Detailed Experiment Specifications (`FMX-0016` – `FMX-0025`)

### `FMX-0016` — Passive Fleet Cooperative Sensor Observatory (Airtime-Tax, Differential Outage & Reassociation Recommender)
- **Hypothesis**: Combining passive read-only CPE telemetry (`mca-status`, `wstalist`, `/proc/net/dev`, chain0/chain1 RSSI delta, CINR, TX/RX retry ratio) across all CPEs on a sector can automatically classify:
  1. **Sector-Wide / AP / Backhaul Degradation** ($\ge 50\%$ of CPEs on AP show simultaneous RTT/CINR drop within same 60s window),
  2. **Localized RF Interferer Cluster** (2–4 azimuthally adjacent CPEs degrade in CINR/noise floor while opposite-azimuth CPEs on the same AP remain normal),
  3. **Single-CPE Alignment / Foliage / Hardware Fault** (1 CPE shows `|chain0 - chain1| >= 6 dB`, e.g., `GALEANO_Rocio_Del_Lujan` at `10 dB` chain delta on `Panel3-Guarida`), and
  4. **Airtime-Tax Culprit** (1 low-MCS CPE consuming `> 30%` of sector TX time while delivering `< 5%` of sector bytes).
- **Mechanism & Preconditions**: Runs 100% at the NOC (`controller/advisory_mode.py` + `controller/capacity_forecasting.py`) over existing read-only SSH/HTTP snapshots. Zero CPE writes.
- **Baseline vs Counterfactual**: Manual operator ticket triage vs automated multi-CPE spatio-temporal clustering.
- **Metrics**: Classification precision/recall on injected and historical anomalies; NOC poll bandwidth (`< 4 KB/CPE/poll`); CPU impact on CPE (`< 0.5%` instantaneous during `mca-status`).
- **Gates**:
  - **`PASS`**: `>= 95%` accuracy distinguishing single-CPE chain/alignment fault from sector-wide interference; zero CPE config mutations.
  - **`FAIL`**: False-positive rate `> 10%` or poll overhead `> 1%` sector airtime.
  - **`STOP` / `ROLLBACK`**: Disable polling timer at NOC if management traffic exceeds `16 kbps/sector`.

---

### `FMX-0017` — Step 1D: Multi-CPE OTA Discovery-IE Withdrawal & Re-Entry Qualification on Stock `airOS 8`
- **Hypothesis**: Following today's `Step 1C` (`run17` `PASS`) single-CPE direct association (`LAP-120` OpenWrt `wds=1` $\leftrightarrow$ unmodified Stock `WA.v8.7.25` `Loco195`), an OpenWrt AP can onboard a **second** unmodified Stock `airOS 8` CPE (or re-onboard a rebooted CPE) by pulsing the Ubiquiti `msg_type=1` Beacon IE for `0.5s` upon broadcast Probe Request **without** causing an already-associated Stock `airOS 8` CPE (`Path B`, `connected_ap == NULL`) to enter `Path A` or drop its session.
- **Mechanism (Grounded in Static RE of `ubnt_poll_host.ko` `0x88b0`, [`docs/STAGE10_11_COMPLETE_RE_AND_BENCH_ARCHIVE_20261021.md`](STAGE10_11_COMPLETE_RE_AND_BENCH_ARCHIVE_20261021.md#L45-L66))**:
  - In `ubnt_poll_host_on_beacon_rx` (`0x88b0`), when `CPE-1` is already associated in `Normal AP` mode (`handle->connected_ap == NULL`), receiving a `0.5s` burst of `msg_type=1` Beacons temporarily adds the AP's BSSID to `CPE-1`'s `handle->sta_list` (`0x10ec`), and when the IE is withdrawn `0.5s` later, `step=0` (`0x8b60`) removes it again—while `handle->connected_ap` (`0x10f0`) is **only** populated inside `ubnt_poll_host_on_sta_connect` (`0x83e4`) at association time!
- **Hardware**: `LAP-120` (`OpenWrt 24.10.4`) + `Loco195` (`Stock WA.v8.7.25`) + monitor capture / 2nd CPE on isolated bench (`5180 MHz / 20 MHz / 0 dBm`).
- **Metrics**: `CPE-1` packet loss (`0%` target), `authorized=true` uptime across 10 simulated `0.5s` Beacon-IE pulses, loaded TCP goodput, and `p95`/`p99` RTT.
- **Gates**:
  - **`PASS`**: `CPE-1` maintains `authorized=true` with `0` disconnects and `0%` ping loss across 10 discovery-IE pulses, and `CPE-2` (or re-associating CPE) completes 4-way WPA2 handshake within `<= 35s`.
  - **`FAIL`**: Any disconnect or `polling_enable=1` transition on already-associated `CPE-1`.
  - **`STOP` / `ROLLBACK`**: `240s` independent radio-off guard + exact wireless hash restoration (`f8e679e4639fc5c26b6c96d646e1e56b57fb58064a75eb215c34ad0462285a6a`).

---

### `FMX-0018` — PoE / Cable Degradation, Ethernet Speed-Downshift & Memory-Drift Early-Warning Probe
- **Hypothesis**: Correlating `eth0` link speed (`1000Mb/s` vs `100Mb/s` vs `10Mb/s` auto-negotiation downshift), GMAC FCS/alignment/carrier errors, uptime/reset reason (`watchdog` vs `power-on`), and `MemFree` slope across the fleet catches physical PoE/water-ingress cable faults days before customer link loss.
- **Hardware**: Read-only telemetry collector across `WA`, `XC`, and `LTU` units.
- **Metrics**: Detection lead time before hard outage; false-positive rate (`< 2%`).
- **Gates**: `PASS` if 100% passive read-only probe identifies simulated `100Mbps -> 10Mbps` / high-CRC links with `< 50 ms` execution time.

---

### `FMX-0019` — `Rocket Prism 5AC Gen2` (`0xe7e9`) Dedicated `wifi1` (`AirView`) + `IRQ 64` TX-Blanking Spectrum Observatory
- **Hypothesis**: Unlike single-radio `LAP-120` (`0xe8e5`), where off-channel `ap-force` scanning causes a `102.4 ms` RTT sawtooth on `wifi0` (`DEC-013`), the `Rocket Prism 5AC Gen2` (`0xe7e9`) can continuously sweep `5150–5875 MHz` using its secondary `wifi1` (`ath_ahb`) radio synchronized via hardware **`GPIO 21` / `IRQ 64` (`ath-spectral-filter`)** with **zero measurable `p99` RTT penalty** on `wifi0`.
- **Hardware**: Bench `Rocket Prism 5AC Gen2` (`0xe7e9`, `XC.v8.7.25`) + `Loco195` (`0xe7fa`, `WA.v8.7.25`).
- **Baseline vs Counterfactual**: `wifi0` loaded TCP + UDP ping with `ubntspecd` / `wifi1` AirView disabled (A) vs enabled (B) in `A/B/A/B` blocks.
- **Metrics**: `wifi0` TCP goodput, `p50`/`p95`/`p99` RTT, `IRQ 64` interrupt rate (`/proc/interrupts`), and spectral FFT resolution.
- **Gates**:
  - **`PASS`**: `wifi0` goodput degradation `< 1.5%` and `p99` RTT delta `< 1.0 ms` while `wifi1` captures full-band 5 GHz spectrum waterfall.
  - **`FAIL` / `ROLLBACK`**: Kill `ubntspecd` / disable `wifi1` scan if `p99` RTT degrades `> 2.0 ms`.

---

### `FMX-0020` — Bench Qualification of `/tmp/fmx_micro_worker` Idle-Window Compute (`5%`/`10%` Duty & `< 200 ms` Preemption)
- **Hypothesis**: The static C micro-worker (`controller/fmx_micro_worker.c`) running in `/tmp` on `Loco195` (`AR9342` `535 MHz`, `64 MB` RAM) at `5%` and `10%` explicit duty cycle maintains `p95`/`p99` wireless RTT within `0.25 ms` of idle baseline and preempts within **`< 200 ms`** when customer traffic (`>= 64 kbps`) starts.
- **Hardware**: Bench `Loco195` (`0xe7fa`) $\leftrightarrow$ `LAP-120` (`0xe8e5`).
- **Metrics**: Measured `/proc/stat` CPU %, `MemFree + Cached` kB, preemption latency (`ms` via `CLOCK_MONOTONIC`), incremental PoE power draw ($\Delta P$ in mW), and `p99` RTT.
- **Gates**:
  - **`PASS`**: Preemption `< 200 ms`, `p99` RTT delta `< 0.5 ms`, free RAM `>= 18 MB`, self-termination on lease TTL expiry (`90s`) confirmed.
  - **`FAIL` / `STOP`**: Immediate `rm -f /tmp/fmx_micro_worker` if preemption exceeds `200 ms` or RTT increases `> 1.0 ms`.

---

### `FMX-0021` — `LTU-Rocket` (`0xae02`) $\leftrightarrow$ `LTU-Lite` (`0xae08`) Over-the-Air `4096-QAM` (`12X`) & `OFDMA` Subband Notching
- **Hypothesis**: Raising `autoMcsCeiling` from `23` (`1024-QAM` `10x`) to `31` (`4096-QAM` `12x`) via `/sys/class/ame/ame_ctrl_dev/autoMcsCeiling` on both a bench `LTU-Rocket` AP and `LTU-Lite` CPE achieves live over-the-air `4096-QAM` modulation and `+15%..+20%` TCP/UDP goodput at high CINR (`>= 36 dB`), while `ofdma_subbands` (`0x01..0xff`) selectively notches a narrowband interferer inside a `40 MHz` channel.
- **Hardware**: Bench `LTU-Rocket` (`0xae02`) + `LTU-Lite` (`0xae08`, `e0:63:da:bf:53:99`).
- **Metrics**: OTA negotiated TX/RX modulation (`ameeng.cgi` / `status.cgi`), LDPC `bler_rate`, `iperf3` goodput, `p95`/`p99` RTT.
- **Gates**:
  - **`PASS`**: OTA `12x` (`4096-QAM`) sustained for `>= 300s` with `bler_rate < 2%` and measurable goodput gain `>= +12%` over `10x` (`1024-QAM`) baseline.
  - **`FAIL` / `ROLLBACK`**: Echo `23 > autoMcsCeiling` and `255 > ofdma_subbands` in RAM; zero flash writes.

---

### `FMX-0022` — `QCA988x` Single-Radio 5 GHz Cooperative Relay (`STA + AP` / `STA + WDS`) Feasibility & Airtime-Tax Refutation Gate
- **Hypothesis (Adversarial Falsification Test for Section 2.A)**: Evaluate whether an OpenWrt `QCA988x` CPE (`CPE-A`) can simultaneously maintain a 4-address WDS `STA` uplink to `AP` and a local `AP` (or `802.11s` mesh) vdev on the same 5 GHz channel to relay traffic for an obstructed `CPE-B`, and whether the resulting **two-hop half-duplex airtime tax + directional antenna sidelobe penalty** helps or hurts net sector capacity.
- **Physical Constraints Tested**:
  1. `ath10k-ct` `10.1-ct-8x-__fW-022` multi-vdev beacon/TSF stability when `STA` vdev tracks remote AP TSF.
  2. Directional antenna geometry: `CPE-A` (`LBE-5AC-Gen2` `23 dBi` dish, `~10°` beamwidth, or `Loco 5AC` `13 dBi` patch, `~45°` beamwidth) pointed at `AP` has **`15–28 dB` sidelobe/backlobe attenuation** toward `CPE-B` unless `CPE-B` lies nearly collinear with `CPE-A -> AP`.
  3. Half-duplex airtime math: a packet `B -> A -> AP` transmitted on the same channel consumes $\frac{1}{R_{B\to A}} + \frac{1}{R_{A\to AP}}$ of sector airtime plus double MAC/contention overhead. It only reduces total sector airtime if:
     $$\frac{1}{R_{B\to A}} + \frac{1}{R_{A\to AP}} < \frac{1}{R_{B\to AP\text{ (direct)}}}$$
     which requires **both** $R_{B\to A} > 2\,R_{B\to AP}$ **and** $R_{A\to AP} > 2\,R_{B\to AP}$.
- **Gates**:
  - **`PASS` (Narrow Collinear Case Only)**: Only if `STA+AP` runs stably for `>= 1h` without beacon loss, $R_{B\to A\to AP}$ improves `CPE-B` goodput by `>= 2.0x`, **and** total sector airtime consumed per delivered Mbit decreases.
  - **`FAIL` (`NO-GO` for Single-Radio Same-Channel Relay)**: If `STA+AP` causes TSF/beacon stalls, sidelobe SNR is insufficient, or 2-hop contention degrades `CPE-A` / sector `p95` RTT by `> 25%`.

---

### `FMX-0023` — Secondary `2.4 GHz` Management Radio (`wifi1`) Short-Range Link-Budget Gate
- **Hypothesis (Fast Falsification for Section 2.B)**: Measure RSSI, noise floor, and TCP throughput of the `2.4 GHz` management radio (`wifi1`) across `5 m`, `25 m`, and `50 m` with real outdoor/wall attenuation.
- **Expected Outcome & Gate**: Internal PCB trace antenna (`~1.5 dBi`), low TX power (`<= 14 dBm`), and `1x1` HT20 in crowded `2.4 GHz` spectrum make `wifi1` unsuitable for inter-building WISP backhaul (`NO-GO` beyond `< 25 m` same-rooftop emergency management access).

---

### `FMX-0024` — Dual-Radio Ethernet Relay (`CPE-B -> Dedicated Short-Hop / Wired -> CPE-A -> AP`) vs Sector Re-Parenting
- **Hypothesis (Section 2.C Practical Alternative)**: Compare (a) re-parenting an obstructed CPE to an alternate AP sector with better Fresnel clearance (identified via `FMX-0016` scan matrix) vs (b) deploying a dedicated secondary NanoStation Loco5AC (`~$49` BOM) at `Node A` on a non-overlapping channel connected via Ethernet/L3 to `CPE-A`.
- **Gates**: Quantify $/Mbps, airtime saved on primary sector, and failure isolation (`PASS` when primary sector airtime tax drops to `0%` for the obstructed hop).

---

### `FMX-0025` — Offline Benchmark: Central `ZeroClaw` Copilot vs Deterministic Controller on Real WISP Telemetry
- **Hypothesis**: Test whether adding a central NOC `ZeroClaw` agent over `stage1_production_telemetry_audit.json` improves root-cause narrative speed for human operators without ever touching the deterministic safety gate (`controller/advisory_mode.py`).
- **Gates**: `PASS` only as a read-only NOC operator copilot; `HARD NO-GO` for autonomous un-gated radio execution.
