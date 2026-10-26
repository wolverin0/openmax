# openMAX: Squeezing the Physical Limit from airMAX AC & LTU Hardware

> **An open research knowledge hub and autonomous experimental testbed driven by a real-world WISP and AI agents to extract maximum real-world PtMP/PtP capacity, latency stability, Triple-Play QoE, and spectral efficiency from ubiquitously deployed Ubiquiti airMAX AC, M5, and LTU hardware.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Status: Active R&D (Stage 99D)](https://img.shields.io/badge/Status-Active%20R%26D%20(Stage%2099D)-success.svg)](docs/CURRENT_STATE.md)
[![Hardware: QCA988x / AR934x / QCA9558 / LTU](https://img.shields.io/badge/Hardware-QCA988x%20%7C%20AR934x%20%7C%20QCA9558%20%7C%20LTU-orange.svg)](docs/HARDWARE_MATRIX.md)
[![Method: Autonomous Loop](https://img.shields.io/badge/Method-Autonomous%20Loop%20(Karpathy%20%2F%20IteRate)-purple.svg)](docs/DECISIONS.md#d-0009)

---

## 1. The Manifesto: Why openMAX Exists

### The Reality of Modern Fixed Wireless
Millions of **Ubiquiti airMAX AC, M5, and LTU** radios—LiteAP GPS, LiteBeam 5AC Gen2, NanoStation 5AC, PowerBeam 5AC, Rocket Prism 5AC/2AC, and LTU-Lite/LR/Pro—are deployed on rooftops, towers, and customer premises worldwide. They represent billions of dollars in sunk capital and provide lifeline broadband to rural, suburban, and developing communities.

However, vendor R&D on the airMAX AC line has effectively stalled as manufacturers shifted focus to newer product tiers. The software running on these millions of deployed radios is largely frozen on legacy vendor kernels (`Linux 3.3.8` / `4.14.0`) and driver architectures dating back to 2017–2019.

### The Opportunity Ubiquiti Left Behind
Meanwhile, over the past decade, the open-source Linux kernel and academic wireless research communities have made revolutionary breakthroughs in wireless performance:
* **Airtime-Based Queue Limits (AQL)**: Restricting hardware driver ring buffers to microseconds of pending airtime rather than megabytes of packets, dropping loaded latency by up to two orders of magnitude (>4,000 ms to <60 ms).
* **Controlled TCP Small Queues (CoTSQ)**: Preventing TCP socket buffers from starving 802.11ac frame aggregation engines, unlocking 2× to 10× throughput gains on wireless links.
* **Supervisory Frame Aggregation (PNOFA)**: Outer-loop processes on closed Qualcomm silicon outperforming native chipset aggregation heuristics by +17% UDP / +13% TCP.
* **Kernel `.ko` Fast-Path Datapath Pruning**: Stripping unconsumed per-PPDU packet-logging (`ath_pktlog.ko`), VoW extended statistics (`vow_extstats=0`), and co-processor SPI interrupt storms (`IRQ 2`) from resource-constrained MIPS 74Kc (`535–720 MHz`) and dual-core Cortex-A9 SoCs.
* **Airtime Fairness (DRR)**: Eliminating the 802.11 "performance anomaly" where a single degraded station destroys aggregate sector throughput (5.4× aggregate capacity restoration in real testbeds).

### Our Approach: WISP Infrastructure + AI Research Agents
We are not a venture-backed hardware vendor or a university lab with dozens of Ph.D. students. **We are an active Wireless Internet Service Provider (WISP) with physical towers, roofs, and hardware.**

We have teamed up with autonomous AI research agents (Codex, Claude, Gemini/Antigravity) operating under a strict scientific constitution to research, document, instrument, and autonomously test how much performance can be extracted from this silicon. We are building this project in the open as a **public knowledge hub** for the entire WISP and wireless engineering community.

---

## 2. The Core Mission

> **What is the best fixed-wireless system existing Ubiquiti airMAX AC, M5, and LTU hardware can physically execute when optimized specifically for stationary outdoor PtMP/PtP links, known geometry, known distances, known service tiers, and autonomous closed-loop experimentation?**

We do **NOT** attempt to turn 802.11ac hardware into Wi-Fi 6/7 or fabricate PHY capabilities the silicon does not possess. We optimize for the properties of **stationary outdoor PtMP/PtP**:
* Radios do not walk behind couches like smartphones. CPEs are bolted to poles with static line-of-sight and measurable link histories.
* We control or observe **both ends of the link** (AP and CPE) as well as upstream **MikroTik RouterOS** gateways (`802.1Q VLAN PCP + DSCP` co-design).
* We use counterbalanced `A1 -> B1 -> A2 -> B2` autoresearch loops, discrete-event `SimPy` + `pymoo` (`NSGA-II`) multi-objective optimization, and outer-loop controllers to supervise the closed radio firmware.

---

## 3. Engineering Principles & Scientific Honesty

Every claim in this repository follows the strict source-of-truth hierarchy defined in our **[Project Constitution (AGENTS.md)](AGENTS.md)**:
1. **Measurements from our exact hardware revision** (Grade-A hardware evidence).
2. **Source code & binary verification for the exact build** (verified in OpenWrt / Linux / `ath10k` / `umac.ko` / `ame_core.ko`).
3. **Official hardware and vendor documentation**.
4. **Peer-reviewed real-hardware research** (IEEE, USENIX, ACM).
5. **Preprints with reproducible code and data**.
6. **Simulations and community reports**.

### Mandatory Claim Labeling
* **CONFIRMED**: Proven experimentally on our hardware or verified directly in source/binary code.
* **INFERRED**: Statistically plausible based on real-hardware literature, awaiting direct testbed measurement.
* **UNKNOWN**: Unmeasured or untested on target hardware.
* **REFUTED**: Disproven by experimental measurement or source code analysis.

---

## 4. The Knowledge Hub: Document Directory

| Document | Purpose |
|:---|:---|
| **[docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md](docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md)** | **Master Research & Autoresearch Index (`v29.0`)**: Complete index of verified hardware champions (`PtMP v22`, `PtP v9`, `LTU 12x SMP`), 571-knob catalog, and 5-Pillar research architecture. |
| **[docs/CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md](docs/CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md)** | **32 Confirmed Hardware Discoveries (`FMX-DISC-01..32`)**: Consolidated ledger of physical testbed breakthroughs from Stages 1–99D. |
| **[docs/STAGE7_MULTIVENDOR_PTMP_REPORT.md](docs/STAGE7_MULTIVENDOR_PTMP_REPORT.md)** | **Stage 7 Multi-Vendor PtMP Report**: 3-station (`802.11ac` + `MikroTik ath9k` + `airOS 6 M5`) Near-Far, ATF, `WMM AC_VO` Deficit Bypass (`21x` RTT cut), and `RTS/CTS 256B` (`+18.5%` UL). |
| **[docs/STAGE8_ADAPTIVE_CONTROLLER_AND_SECTOR_SIM.md](docs/STAGE8_ADAPTIVE_CONTROLLER_AND_SECTOR_SIM.md)** | **Stage 8 Adaptive Controller & Sector Sim**: Zero-fork closed-loop daemon (`fmx_adaptive_controller.sh`), `618 KB` Spectral FFT, `VHT40` vs `VHT80` (`2.26x` spectral efficiency), and 6-flow BiDir stress test (`39.1x` RTT cut). |
| **[docs/STAGE9_20MHZ_RATEMASK_COTSQ_AND_PROCD.md](docs/STAGE9_20MHZ_RATEMASK_COTSQ_AND_PROCD.md)** | **Stage 9 `20 MHz` WISP Sector, Rate-Mask Boundary, `CoTSQ` & `procd` Watchdog**: `VHT20` (`3.05x` faster obstructed `SXT`, `0.9531` Jain fairness, `3.342 bit/s/Hz` DL / `3.656 bit/s/Hz` UL), `FMX-0009` `ATH10K_DBG_BUFFER` verification, and `CoTSQ 128 KB`. |
| **[docs/STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md](docs/STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md)** | **Stage 10 Stock `airOS 8` (`v8.5.12`–`v8.7.25`) Interoperability & Zero-Truck-Roll Migration**: Cracked the 4 locks (`ubnt_poll_host_is_ap_valid`, 30s TDMA watchdog, `allow_80211=1` WPA2 filter, `ETH_P_TEB` `0x6558` decapsulation) + `/sbin/uav`-proof `system.cfg` persistence (`78.7 Mbps` UL / `63.6 Mbps` DL in `20 MHz`). |
| **[docs/STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md](docs/STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md)** | **Stage 11A `XC` (`Rocket Prism 5AC Gen2` / `PS-5AC`) & AirPrism Architecture**: Full decompilation of all 34 `XC` board structs, 2-stage AirPrism (`GPIO 13..16` `prism` bank + SPI `hsr` active filter at `0xbf000000`), and `wifi1` `SPECTRAL-XMIT-FILTER`. |
| **[docs/STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md](docs/STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md)** | **Stage 11B `LTU` (`LTU-Rocket` / `LTU-Lite` `v2.4.2`) `4096-QAM` (`12X`) Unlock & Hidden OFDMA**: `amesoc3` + `AD9361` SDR + `Intel Arria 10 SoC FPGA` architecture; proof that `4096-QAM` (`0x1f`) is implemented in `ame_core.ko`/RFIC/PtMP scheduler (`wireless.1.rate.mcs=5`). |
| **[docs/STAGE12_FULL_OPENWRT_SECTOR_AND_UISP_BRIDGE.md](docs/STAGE12_FULL_OPENWRT_SECTOR_AND_UISP_BRIDGE.md)** | **Stage 12 Live Production Sector Cutover (`Live-Sector-1` + `CPE-A` + `CPE-B`) & UISP Bridge**: First live outdoor WISP sector (`LiteAP 120` AP + `NanoStation 5AC loco` + `LiteBeam 5AC Gen2` CPEs) migrated 100% to OpenWrt 24.10.4 (`Linux 6.6.110`), delivering **~10x lower wireless RTT (`22.58 ms` -> `1.93–2.42 ms`)** and **`69.80 Mbps` TCP DL in `20 MHz`**. |
| **[docs/STAGE72A_PTMP_KERNEL_KO_FASTPATH_BENCH.md](docs/STAGE72A_PTMP_KERNEL_KO_FASTPATH_BENCH.md)** | **Stage 72A PtMP Champion `v22`**: Live 3-CPE sector kernel `.ko` fast-path (`rmmod ath_pktlog` + `vow_extstats=0` + `set_multiq=3`) yielding **`+23.35%` sector goodput (`46.53 -> 57.39 Mbps`)**, **`-20.81%` `p99` RTT**, **`-22.58%` IPTV jitter**, and **`0.00%` VoIP loss**. |
| **[docs/STAGE85A_PTP_CHAMPION_V9_AND_HITLESS_CSA_BENCH.md](docs/STAGE85A_PTP_CHAMPION_V9_AND_HITLESS_CSA_BENCH.md)** | **Stage 85A PtP Champion `v9` & Hitless `802.11h` `CSA`**: **`+41.01%` total goodput**, **`+70.60%` Bulk TCP**, **`-64.80%` `p95` RTT**, **`0.000%` VoIP loss**, and **`0.000s` hitless channel hop (`0/80` missed probes)**. |
| **[docs/STAGE89B_DYNAMIC_20_40MHZ_CHANNEL_WIDTH_AUTO_FOLLOWING_BENCH.md](docs/STAGE89B_DYNAMIC_20_40MHZ_CHANNEL_WIDTH_AUTO_FOLLOWING_BENCH.md)** | **Stage 89B Zero-Touch Dynamic `20 MHz <-> 40 MHz` Auto-Following**: Stock `airOS 8` CPEs follow OpenWrt AP `VHT Operation IE` bandwidth transitions in **`8.78s–12.10s` (`< 15s`)** with **`-31.28%` IPTV jitter**. |
| **[docs/STAGE92B_LTU_12X_AND_2AC_PRISM_BENCH.md](docs/STAGE92B_LTU_12X_AND_2AC_PRISM_BENCH.md)** | **Stages 92B–99B `AF-LTU` Master AP Unlock, `80`-Symbol Superframe & `Rocket 2AC Prism` Fast-Path**: `LTU-Lite` `4096-QAM 12x` + `80`-symbol (`61 DL + 19 UL`) superframe + Cortex-A9 SMP IRQ pinning (`189.81 Mbps` SoC TCP, `-12.5%` `p50` RTT) & `Rocket 2AC Prism` `IRQ 2` elimination (`+13.0%` TCP, `-54.3%` `p50` RTT). |
| **[docs/DOCS-MAP.md](docs/DOCS-MAP.md)** | **Master Reading Map**: Status and classification of all project files across Stages 1–99D. |
| **[docs/CURRENT_STATE.md](docs/CURRENT_STATE.md)** | **Living State Log**: Chronological development log and active hardware baselines. |
| **[docs/DECISIONS.md](docs/DECISIONS.md)** | **Architectural Decision Records**: D-0001 through D-0018. |
| **[docs/EXPERIMENTS.md](docs/EXPERIMENTS.md)** | **Experiment Register**: FMX-0001 through FMX-0016 and Stage-3 Campaigns C1–C8. |
| **[safety/recovery/FMX-0002_recovery_runbook.md](safety/recovery/FMX-0002_recovery_runbook.md)** | **Recovery Runbook**: Proven TFTP urescue and return-to-stock procedures. |

---

## 5. Confirmed Research Baselines & Breakthroughs (Stages 1–99D)

1. **OpenWrt 24.10.4 (Kernel 6.6.110) Running at Physical Silicon Ceiling**: Flashed and verified on a physical lab testbed (**Ubiquiti LiteAP 120 `LAP-120` AP ↔ NanoStation 5AC Loco CPE**, both `WA` boards with `AR9342 @ 535 MHz` + `64 MB DDR2` + `QCA9882`).
2. **64 MB RAM OOM Root-Cause Solved (`+14 MB` Usable Headroom, `0 OOMs`)**: Tuning `vm.min_free_kbytes=2048` and `vm.watermark_boost_factor=0` increased `MemAvailable` from `6.5 MB` → **`22.4 MB` on AP** and **`23.8 MB` on CPE**, achieving **100% survival (`0 OOMs`)** under sustained 200+ Mbps saturation.
3. **Clean-Room Interoperability Analysis of `airMAX AC` (`RE1` — `docs/UMAC_DATAPATH.md`)**: Mapped the exact boundary between `umac.ko` and `ubnt_poll_host.ko` (`ath_Airmax_Ops_t` 62-pointer table, `CE4` opcodes `0x9064`/`0x9044`), replacing proprietary polling with open Linux 6.6 `mac80211` primitives (`AQL` + `ATF` + `htt_max_amsdu_ampdu` + Adaptive `RTS/CTS NAV` + upstream `CAKE`) for **100% multi-vendor compatibility (`Ubiquiti AC + Legacy M5 802.11n + MikroTik + Cambium + TP-Link`)**.
4. **Confirmed Physical Bench Progression (80 MHz Indoor NLOS Bench — `research/raw/bench/2026-10-16/`)**:

| Stage / Configuration | UDP Downlink Goodput | UDP Uplink Goodput | TCP Downlink (1S) | Loaded RF RTT (`p50 / p95`) | `MemAvailable` (AP / CPE) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **0. Unoptimized / Legacy State** | `50.99 – 67.22 Mbps` *(OOM crash)* | `50.99 Mbps` *(OOM crash)* | `124.69 Mbps` | `14.1 ms p95 / 30.9 ms p99` | `6.5 MB / 9.4 MB` ❌ |
| **1–3. VM Fix + Zero-NAT Fastpath Baseline** | `121.77 Mbps` (`35.1% loss`) | `53.78 Mbps` (`18.97 ms p95`) | `124.69 Mbps` (`0 retrans`) | `1.47 ms / 2.31 ms` (DL) | `22.4 MB / 23.8 MB` ✅ |
| **4.1. + `AQL` Tightening (`2000/4000 µs`)** | **`186.23 Mbps`** (`2.25% loss`) | **`113.46 Mbps`** (`6.70 ms p95`) | `123.51 Mbps` (`0 retrans`) | `1.41 ms / 2.02 ms` (DL) | `20.8 MB / 21.3 MB` ✅ |
| **4.2. + Upstream Gateway `CAKE` Shaper** | **`191.44 Mbps`** (`1.25% loss`) | **`94.88 Mbps`** (`0.72% loss`) | `128.54 Mbps` (`0 retrans`) | `1.45 ms / 2.00 ms` (UL!) | `20.7 MB / 21.4 MB` ✅ |
| **4.3 / 6. + `15 dBm`, `A-MPDU 64`, `debug_mask=0` (Winner)** | 🏆 **`223.53 Mbps`** (`199.11M` @200M, `0.21% loss`) | 🏆 **`98.53 Mbps`** (`1.90 ms p95`) | 🏆 **`154.58 Mbps`** (`0 retrans`) | 🏆 **`1.35 ms p50 / 1.83 ms p95`** | **`20.8 MB / 21.4 MB` (0 OOMs)** |

5. **The `WA` vs. `XC` Silicon Boundary Across the airMAX AC Lineup**:
   - `LAP-120` / `LAP-GPS` / `Loco 5AC` / `LiteBeam 5AC Gen2` share the **`WA` platform (`AR9342 MIPS 74Kc @ 535 MHz` + `64 MB DDR2`)**, hitting `95.8%` CPU (`88.7% ksoftirqd`) at `223.5 Mbps` (~19,000 pps)—well above real-world `20 MHz` PtMP sector RF capacity (`100–140 Mbps`).
   - Higher-capacity `40/80 MHz` sectors require the **`XC` platform (`QCA9558 @ 720 MHz` + `128 MB DDR2`)** (`Rocket 5AC Lite`, `PrismStation 5AC`, `Rocket Prism 5AC Gen2`, `PowerBeam 5AC-500`).
6. **Stages 7, 8 & 9 — 3-Station Multi-Vendor & Mixed-Generation PtMP Sector Verification**:
   - **`WMM AC_VO DiffServ Deficit Bypass`**: Promoting interactive traffic to `DSCP EF` (`AC_VO`) cut loaded median RTT on a wall-obstructed `MikroTik SXT` by **`21.0x` (`143.0 -> 6.80 ms`)** and on stock `airOS 6` `LiteBeam M5` by **`8.0x` (`36.15 -> 4.53 ms`)**, while `RTS/CTS = 256B` boosted sector UL by **`+18.5%` (`150.40 -> 178.17 Mbps`)**.
   - **Zero-Fork Adaptive Controller (`fmx_adaptive_controller.sh`) & `VHT20`/`VHT40`**: Delivered **`47.6x` `p95` tail-latency reduction** under 3-station contention; `VHT20` (`20 MHz`) raised **Jain's Fairness Index to `0.9531`**, reached **`3.342 bit/s/Hz` DL / `3.656 bit/s/Hz` UL**, and boosted `CoTSQ 128 KB` 3-station UL to **`181.90 Mbps`**.
7. **Stage 10 — Stock `airOS 8` (`WA.v8.5.12`–`WA.v8.7.25`) $\leftrightarrow$ OpenWrt AP Interoperability**:
   - Solved all 4 interoperability locks (`ubnt_poll_host_is_ap_valid`, 30s TDMA watchdog, `allow_80211=1` WPA2 filter, and `ETH_P_TEB` `0x6558` decapsulation in `mac80211.ko`), achieving **`78.7 Mbps` TCP UL (`3.94 bit/s/Hz`) / `63.6 Mbps` TCP DL (`3.18 bit/s/Hz`) in `20 MHz` `VHT20` `WPA2-PSK`** with relocation-safe `.rel.text` patching (`F01`).
8. **Stage 11 — Static Reverse Engineering of `XC` AirPrism & `LTU` (`v2.4.2`) `4096-QAM` (`12X`) + `OFDMA`**:
   - Mapped the 34-entry `XC` `ubnthal.ko` board table (`prism` GPIO 13..16 + SPI `hsr` active filter at `0xbf000000`) and confirmed `LTU` (`amesoc3` Cortex-A9 + `AD9361` SDR + `Arria 10` FPGA) implements `4096-QAM` (`12X`, LDPC code `0x1f`) and `2/4/8`-subband `OFDMA` (`ofdma_mode=0..3`).
9. **Stage 12 — Live Production WISP Sector Cutover (`Live-Sector-1` + `CPE-A` + `CPE-B`) & Native UISP Bridge**:
   - Migrated a live outdoor WISP sector (`LiteAP 120` AP + `CPE-A` `NanoStation 5AC loco` + `CPE-B` `LiteBeam 5AC Gen2`) to **OpenWrt 24.10.4 (`Linux 6.6.110`)**, cutting unloaded wireless RTT **~10x** (`22.58 ms` → **`1.93–2.42 ms` `p50`**), loaded download latency **3.5x–5x** (`8.43–9.86 ms` `p50` at **`69.80 Mbps` TCP**), and upload bufferbloat **12x–18x** (`~200 ms` → **`10.37–16.64 ms` `p50`**), while preserving native `/bin/udapi-bridge` UISP reporting.
10. **Stages 13–99D — Kernel `.ko` Fast-Path Champions (`PtMP v22` & `PtP v9`), Zero-Touch `20/40 MHz`, `AF-LTU` `80`-Symbol SMP & `MikroTik 802.1Q` Co-Design**:
    - **`PtMP Champion v22` (`Stage 72A`)**: Stripping `ath_pktlog.ko` (`rmmod ath_pktlog`), disabling VoW extended stats (`vow_extstats=0`), and enabling `set_multiq=3` across the 3-CPE outdoor sector boosted aggregate goodput by **`+23.35%` (`46.53 -> 57.39 Mbps`)**, cut `p99` RTT by **`-20.81%` (`7.40 -> 5.86 ms`)**, cut IPTV jitter by **`-22.58%` (`0.62 -> 0.48 ms`)**, and held VoIP loss at **`0.00%`**.
    - **`PtP Champion v9` & Hitless `802.11h` `CSA` (`Stage 85A`)**: On `PowerBeam 5AC-500` (`XC.v8.7.19`), combining `rmmod ath_pktlog`, `vow_extstats=0`, `tx_chainmask=3`, `rx_chainmask=3`, and `set_multiq=1` delivered **`+41.01%` total goodput**, **`+70.60%` Bulk TCP**, **`-64.80%` `p95` RTT**, **`0.000%` VoIP loss**, and **`0.000s` hitless `802.11h` `CSA` channel switch (`0/80` missed probes)**.
    - **Zero-Touch Dynamic `20 MHz <-> 40 MHz` Auto-Following (`Stage 89B`)**: Unmodified stock `airOS 8` CPEs (`autochanwidth=enabled`) track OpenWrt AP `VHT Operation IE` (`0xc0`) channel-width transitions in **`8.78s–12.10s` (`< 15s`)**, cutting narrowband `20 MHz` IPTV jitter by **`-31.28%` (`0.438 -> 0.301 ms`)** (`0.00%` loss).
    - **`AF-LTU` `LTU-Lite` Master AP Unlock, `80`-Symbol Superframe & Dual-Core Cortex-A9 SMP (`Stages 92B, 96B & 99B`)**: Unlocked `LTU-Lite` (`v2.3.1`) as an `ap-ptmp` Master AP at **`4096-QAM 12x`** with an **`80`-symbol (`61 DL + 19 UL` at `22.4 MS/s`, `2.0 ms` / `500 Hz`) superframe** (`13` non-dominated `SimPy`/`pymoo` NSGA-II Pareto points) and dual-core SMP interrupt isolation (`IRQ 52/53` `ame_b2h`/`ame_timer` on `CPU0`, `IRQ 63/92` `eth0`/`SPI` on `CPU1`), raising SoC TCP throughput by **`+8.5%` to `+9.9%` (`189.81 Mbps`)** and cutting loaded `p50` RTT by **`-12.5%` (`0.42 ms`)**.
    - **`Rocket 2AC Prism` (`2.4 GHz`, `2XC.v8.7.11`) `IRQ 2` Fast-Path (`Stage 92B`)**: Unbinding the `ath_hsr` SPI bit-banging storm (`100%` elimination of `15,480` `IRQ 2` interrupts) + `rmmod ath_pktlog` + `vow_extstats=0` boosted peak TCP by **`+13.0%` (`34.38 Mbps`)** and cut `p50` RTT by **`-54.3%` (`1.63 -> 0.745 ms`)**.
    - **`MikroTik + OpenWrt 802.1Q VLAN/DSCP` E2E Co-Design (`Stage 95B`)**: Mapping `DSCP EF (46) -> VLAN PCP 6 -> WMM AC_VO` and `DSCP AF41 (34) -> VLAN PCP 5 -> WMM AC_VI` cut E2E `p50` RTT by **`-54.84%` (`4.39 -> 1.98 ms`)** and `p95` RTT by **`-46.18%` (`7.60 -> 4.09 ms`)** under saturated Triple-Play load.

---

## 6. Physical Testbed Architecture, Collaboration & Safety Boundaries

* **2-Tier Physical Testbed**: (1) **Benchtop Coaxial Matrix** (SMA coax + 30–40 dB attenuators + Wilkinson dividers) and (2) **Outdoor Cross-Building Rooftop Sector** (`LiteAP 120`, `PowerBeam 5AC-500`, `Rocket 2AC Prism`, `LTU-Lite`, `MikroTik RB2011`, and multi-generation CPEs) with automated PoE/TFTP `urescue` recovery.
* **Open Collaboration**: We welcome peer review of our ADRs (**[docs/DECISIONS.md](docs/DECISIONS.md)**), adversarial audits (**[docs/ADVERSARIAL_REVIEW_STAGE10_11.md](docs/ADVERSARIAL_REVIEW_STAGE10_11.md)**), and outer-loop `ath10k`/`mac80211` contributions.
* **Strict Safety & Regulatory Boundaries**: We **NEVER** modify regulatory domains, exceed legal EIRP limits, disable DFS radar detection, or write protected flash partitions (`mtd0` `u-boot`, `mtd1` `u-boot-env`, `mtd5` `ART` calibration).
* **License**: Project-authored code, analysis scripts, and documentation are open-sourced under the [MIT License](LICENSE).
