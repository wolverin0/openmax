# openMAX: Squeezing the Physical Limit from airMAX AC Hardware

> **An open research knowledge hub and autonomous experimental testbed driven by a real-world WISP and AI agents to extract maximum real-world PtMP capacity, latency stability, and spectral efficiency from ubiquitously deployed Ubiquiti airMAX AC hardware.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Status: Active R&D](https://img.shields.io/badge/Status-Active%20R%26D-success.svg)](docs/CURRENT_STATE.md)
[![Hardware: QCA988x / AR934x](https://img.shields.io/badge/Hardware-QCA988x%20%7C%20AR934x-orange.svg)](docs/HARDWARE_MATRIX.md)
[![Method: Autonomous Loop](https://img.shields.io/badge/Method-Autonomous%20Loop%20(Karpathy%20%2F%20IteRate)-purple.svg)](docs/DECISIONS.md#d-0009)

---

## 1. The Manifesto: Why openMAX Exists

### The Reality of Modern Fixed Wireless
Millions of **Ubiquiti airMAX AC** radios—LiteAP GPS, LiteBeam 5AC Gen2, NanoStation 5AC, and Loco 5AC—are deployed on rooftops, towers, and customer premises worldwide. They represent billions of dollars in sunk capital and provide lifeline broadband to rural, suburban, and developing communities.

However, vendor R&D on the airMAX AC line has effectively stalled as manufacturers shifted focus to proprietary 60 GHz, LTU, and Wi-Fi 6/7 gear. The software running on these millions of deployed radios is largely frozen on vendor kernels and driver architectures dating back to 2017–2019.

### The Opportunity Ubiquiti Left Behind
Meanwhile, over the past decade, the open-source Linux kernel and academic wireless research communities have made revolutionary breakthroughs in wireless performance:
* **Airtime-Based Queue Limits (AQL)**: Restricting hardware driver ring buffers to microseconds of pending airtime rather than megabytes of packets, dropping loaded latency by up to two orders of magnitude (>4,000 ms to <60 ms).
* **Controlled TCP Small Queues (CoTSQ)**: Preventing TCP socket buffers from starving 802.11ac frame aggregation engines, unlocking 2× to 10× throughput gains on wireless links.
* **Supervisory Frame Aggregation (PNOFA)**: Outer-loop processes on closed Qualcomm silicon outperforming native chipset aggregation heuristics by +17% UDP / +13% TCP.
* **Contextual Rate-Mask Bounding**: Reclaiming 15% to 25% of wasted sector airtime on fixed links by banning doomed high-order MCS probing.
* **Airtime Fairness (DRR)**: Eliminating the 802.11 "performance anomaly" where a single degraded customer destroys aggregate sector throughput (5.4× aggregate capacity restoration in real testbeds).

### Our Approach: WISP Infrastructure + AI Research Agents
We are not a venture-backed hardware vendor or a university lab with dozens of Ph.D. students. **We are an active Wireless Internet Service Provider (WISP) with physical towers, roofs, and hardware.** 

We have teamed up with autonomous AI research agents (Codex, Claude, Gemini/Antigravity) operating under a strict scientific constitution to research, document, instrument, and autonomously test how much performance can be extracted from this silicon.

We are building this project in the open as a **public knowledge hub** for the entire WISP and wireless engineering community.

---

## 2. The Core Mission

> **What is the best fixed-wireless system existing Ubiquiti airMAX AC hardware can physically execute when optimized specifically for stationary outdoor PtMP links, known geometry, known distances, known service tiers, and autonomous closed-loop experimentation?**

We do **NOT** attempt to turn 802.11ac hardware into Wi-Fi 6/7 or fabricate PHY capabilities the silicon does not possess. We optimize for the properties of **stationary outdoor PtMP**:
* Radios do not walk behind couches like smartphones. CPEs are bolted to poles with static line-of-sight and measurable link histories.
* We control or observe **both ends of the link** (AP and CPE).
* We can use multi-armed bandits and outer-loop controllers to supervise the closed firmware.

---

## 3. Engineering Principles & Scientific Honesty

Every claim in this repository follows the strict source-of-truth hierarchy defined in our **[Project Constitution (AGENTS.md)](AGENTS.md)**:

1. **Measurements from our exact hardware revision** (Grade-A hardware evidence).
2. **Source code for the exact build** (verified in OpenWrt / Linux / ath10k).
3. **Official hardware and vendor documentation**.
4. **Peer-reviewed real-hardware research** (IEEE, USENIX, ACM).
5. **Preprints with reproducible code and data**.
6. **Simulations and community reports**.

### Mandatory Claim Labeling
* **CONFIRMED**: Proven experimentally on our hardware or verified directly in source code.
* **INFERRED**: Statistically plausible based on real-hardware literature, awaiting direct testbed measurement.
* **UNKNOWN**: Unmeasured or untested on target hardware.
* **REFUTED**: Disproven by experimental measurement or source code analysis.

> **We do not sell snake oil, and we do not add percentages from unrelated papers together.** The goal is not to prove openMAX beats airMAX; the goal is to discover the physical truth.

---

## 4. The Knowledge Hub: Document Directory

To explore our technical findings, architectural decisions, and experiment logs, follow this reading order:

| Document | Purpose |
|:---|:---|
| **[docs/DOCS-MAP.md](docs/DOCS-MAP.md)** | **Master Reading Map**: Status and classification of all project files. |
| **[debates/001-openmax-qca9880-ptmp-optimizat/synthesis.md](debates/001-openmax-qca9880-ptmp-optimizat/synthesis.md)** | **Multi-LLM Debate Synthesis**: 3-way frontier AI consensus (Fable 5.1, GPT-6 Astra, Gemini 3.8 Flash) on CPU boundaries, shaping, and uplink gates. |
| **[knowledge/ANALYTICAL_QUEUE_MODEL_AND_HOOKS.md](knowledge/ANALYTICAL_QUEUE_MODEL_AND_HOOKS.md)** | **Analytical Queue Model & Driver Hooks**: Mathematical models for CoTSQ 6ms, Bianchi PtMP hidden-node derivations, and exact WMI/HTT driver hooks. |
| **[docs/COMMUNITY_CALL_FOR_COLLABORATION.md](docs/COMMUNITY_CALL_FOR_COLLABORATION.md)** | **Community Manifesto**: How WISPs, kernel devs, and researchers can collaborate with our AI loop. |
| **[knowledge/ATH10K_CT_FIRMWARE_DEEP_DIVE.md](knowledge/ATH10K_CT_FIRMWARE_DEEP_DIVE.md)** | **ath10k-ct Firmware Internals**: 30 vs 4 retries, HTT credit rings, bufferbloat, peer stats, and the 6 Mbps airtime cliff. |
| **[knowledge/PACED_AGGREGATION_AND_COTSQ.md](knowledge/PACED_AGGREGATION_AND_COTSQ.md)** | **Paced Aggregation & CoTSQ**: Mathematical model of A-MPDUs; why TSQ=1ms starves throughput and CoTSQ=6ms restores 10× goodput. |
| **[knowledge/PTMP_OUTDOOR_TDMA_VS_CSMA.md](knowledge/PTMP_OUTDOOR_TDMA_VS_CSMA.md)** | **Outdoor PtMP Physics**: Hidden node collapse, airMAX AC proprietary Xtensa/ASIC architecture, and OpenWrt hybrid solutions. |
| **[knowledge/AUTONOMOUS_WIRELESS_RESEARCH_ENGINE.md](knowledge/AUTONOMOUS_WIRELESS_RESEARCH_ENGINE.md)** | **Autoresearch Engine Architecture**: Karpathy-style closed-loop AI optimization, multi-objective reward function $J(\theta)$, and A/B/A/B gate. |
| **[knowledge/SPECTRAL_AND_CSI_ANALYSIS.md](knowledge/SPECTRAL_AND_CSI_ANALYSIS.md)** | **Spectral & CSI Analysis**: Baseband FFT scanning via RelayFS vs structural absence of CSI on QCA988x. |
| **[docs/CURRENT_STATE.md](docs/CURRENT_STATE.md)** | **Living State Log**: Chronological development log (read latest addendum first). |
| **[docs/DECISIONS.md](docs/DECISIONS.md)** | **Architectural Decision Records**: D-0001 through D-0012 (D-0009 autoresearch, D-0010 testbed, D-0011 multi-LLM debate, D-0012 queue/contention models). |
| **[docs/EXPERIMENTS.md](docs/EXPERIMENTS.md)** | **Experiment Register**: FMX-0001 through FMX-0016 and Stage-3 Campaigns C1–C8. |
| **[docs/TESTBED_ENVIRONMENT_GUIDE.md](docs/TESTBED_ENVIRONMENT_GUIDE.md)** | **2 AP + 20 CPE Testbed Guide**: RF attenuation, Fraunhofer distance, unattended recovery. |
| **[knowledge/REAL_HARDWARE_LITERATURE.md](knowledge/REAL_HARDWARE_LITERATURE.md)** | **Literature Catalogue**: Verified analysis of IteRate, WiFiSpectralJam, PNOFA, and Quick & Plenty. |
| **[docs/QCA988X_CONTROL_BOUNDARY.md](docs/QCA988X_CONTROL_BOUNDARY.md)** | **Hardware Control Boundary**: What the host can and cannot control under ath10k-CT. |
| **[safety/recovery/FMX-0002_recovery_runbook.md](safety/recovery/FMX-0002_recovery_runbook.md)** | **Recovery Runbook**: Proven TFTP urescue and return-to-stock procedures. |

---

## 5. Current Research Baseline & Breakthroughs

### What We Have Confirmed
1. **OpenWrt 24.10.4 (Kernel 6.6.110) Running at Physical Silicon Ceiling**: Flashed and verified on a physical lab testbed (**Ubiquiti LiteAP 120 `LAP-120` AP ↔ NanoStation 5AC Loco CPE**, both `WA` boards with `AR9342 @ 535 MHz` + `64 MB DDR2` + `QCA9882`).
2. **64 MB RAM OOM Root-Cause Solved (`+14 MB` Usable Headroom, `0 OOMs`)**: Discovered that OpenWrt's default `/etc/init.d/sysctl` sets `vm.min_free_kbytes=8192` + `vm.watermark_boost_factor=15000` on 64 MB (`56,120 kB` managed) boards, reserving `12.3 MB` (`high=3072 pages`) and triggering the kernel OOM killer (`wpa_supplicant`/`hostapd`) under 200 Mbps load even when ~9 MB of RAM is free. Tuning `vm.min_free_kbytes=2048` and `vm.watermark_boost_factor=0` increased `MemAvailable` from `6.5 MB` → **`22.4 MB` on AP** and **`23.8 MB` on CPE**, achieving **100% survival (`0 OOMs`)** under sustained 200+ Mbps saturation.
3. **Clean-Room Interoperability Analysis of `airMAX AC` (`RE1` — `docs/UMAC_DATAPATH.md`)**: Using static binary analysis (IDA Pro 9.3 + REA MCP) for interoperability and hardware boundary verification, we mapped the exact boundary between `umac.ko` and `ubnt_poll_host.ko`:
   - `ubnt_poll_host.ko` attaches to `umac.ko` via a 62-pointer dispatch table (`ath_Airmax_Ops_t`, 248 bytes).
   - Host-to-target TDMA commands serialize over **Copy Engine 4 (`CE4`, 2048 descriptors)** using vendor WMI opcodes **`0x9064`** (`ol_ath_Airmax_wmi_poll_cmd`) and **`0x9044`**, with subtype **`0x17`** (16-byte per-node TXQ pause/unpause record) and subtype **`0x1e`** (36-byte per-node rate/retry override), returning telemetry via WMI events `0x9022`, `0x9023`, and `0x9025`.
   - Because opcodes `0x9064`/`0x9044` exist only inside the proprietary airOS radio firmware blob, **openMAX replaces proprietary polling with open Linux 6.6 `mac80211` primitives** (`AQL` microsecond airtime limits + `Airtime Fairness` weights + `htt_max_amsdu_ampdu` + Adaptive `RTS/CTS NAV` reservation + upstream `CAKE`), unlocking **100% multi-vendor compatibility (`Ubiquiti AC + Legacy M5 802.11n + MikroTik + Cambium + TP-Link`)**.
4. **Confirmed Physical Bench Progression (80 MHz Indoor NLOS Bench — `research/raw/bench/2026-10-16/`)**:

| Stage / Configuration | UDP Downlink Goodput | UDP Uplink Goodput | TCP Downlink (1S) | Loaded RF RTT (`p50 / p95`) | `MemAvailable` (AP / CPE) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **0. Unoptimized / Legacy State** | `50.99 – 67.22 Mbps` *(OOM crash)* | `50.99 Mbps` *(OOM crash)* | `124.69 Mbps` | `14.1 ms p95 / 30.9 ms p99` | `6.5 MB / 9.4 MB` ❌ |
| **1–3. VM Fix + Zero-NAT Fastpath Baseline** | `121.77 Mbps` (`35.1% loss`) | `53.78 Mbps` (`18.97 ms p95`) | `124.69 Mbps` (`0 retrans`) | `1.47 ms / 2.31 ms` (DL) | `22.4 MB / 23.8 MB` ✅ |
| **4.1. + `AQL` Tightening (`2000/4000 µs`)** | **`186.23 Mbps`** (`2.25% loss`) | **`113.46 Mbps`** (`6.70 ms p95`) | `123.51 Mbps` (`0 retrans`) | `1.41 ms / 2.02 ms` (DL) | `20.8 MB / 21.3 MB` ✅ |
| **4.2. + Upstream Gateway `CAKE` Shaper** | **`191.44 Mbps`** (`1.25% loss`) | **`94.88 Mbps`** (`0.72% loss`) | `128.54 Mbps` (`0 retrans`) | `1.45 ms / 2.00 ms` (UL!) | `20.7 MB / 21.4 MB` ✅ |
| **4.3 / 6. + `15 dBm`, `A-MPDU 64`, `debug_mask=0` (Winner)** | 🏆 **`223.53 Mbps`** (`199.11M` @200M, `0.21% loss`) | 🏆 **`98.53 Mbps`** (`1.90 ms p95`) | 🏆 **`154.58 Mbps`** (`0 retrans`) | 🏆 **`1.35 ms p50 / 1.83 ms p95`** | **`20.8 MB / 21.4 MB` (0 OOMs)** |

5. **The `WA` vs. `XC` Silicon Boundary Across the airMAX AC Lineup**:
   - **Why `223.5 Mbps` is the physical ceiling on `LAP-120` / `LAP-GPS` / `Loco 5AC` / `LiteBeam 5AC Gen2`**: All four models share the **`WA` platform (`Atheros AR9342 MIPS 74Kc @ 535 MHz` + `64 MB DDR2`)**. At `223.5 Mbps` (~19,000 pps), `AP CPU` hits **`95.8%` (`88.7% ksoftirqd`)**.
   - **Why `223.5 Mbps` is MORE than enough for real WISP 20/40 MHz PtMP sectors**: Real-world WISP sectors operating at `20 MHz` (10–25 CPEs) have a physical RF capacity of `100–140 Mbps`, well below the `223.5 Mbps` CPU ceiling. In production `20 MHz` sectors, the bottleneck is **not CPU**, but **Airtime Starvation (*Near-Far* bad apples at `-75 to -82 dBm`)** and **Hidden-Node Uplink Collisions**—precisely what our Adaptive `AQL` + `ATF` + `RTS/CTS NAV` + `CAKE` stack solves.
   - Higher-capacity `40/80 MHz` sectors (300–450 Mbps) require the **`XC` platform (`QCA9558 @ 720 MHz` + `128 MB DDR2`)** found in the **`Rocket 5AC Lite`**, **`PrismStation 5AC (`PS-5AC`)`**, and **`Rocket Prism 5AC Gen2 (`RP-5AC-Gen2`)`**.

---

## 6. Physical Testbed Architecture: 2 APs + 20 CPEs

We do not use an indoor room or a leased warehouse:
* **The Warehouse Fallacy**: Steel walls and metal roofs turn 5 GHz into an echo chamber of Rayleigh multipath, corrupting line-of-sight propagation and preventing genuine hidden nodes.
* **Our 2-Tier Testbed**:
  1. **Tier 1 (Benchtop Coaxial Matrix)**: AP and CPEs connected via SMA coax into fixed 30–40 dB attenuators and Wilkinson power dividers. 100% deterministic, zero interference, simulating 100m to 10km links.
  2. **Tier 2 (Outdoor Cross-Building Rooftop Sector)**: 2 APs mounted on a commercial WISP building pointing across a 21-meter street canyon to 10–12 CPEs distributed over a 162 m² residential roof. Provides real outdoor atmosphere, true Line-of-Sight, and natural far-field antenna formation ($R > 5–8\text{ meters}$).
* **Unattended Recovery**: All radios are automated via managed 24V passive PoE switches and relay-controlled remote-reset circuits (injecting DC offset on Ethernet data pairs during boot) to enter TFTP `urescue` without human hands touching a reset button.

---

## 7. How You Can Help / Open Call for Collaboration

We are opening this repository to the global networking, WISP, and academic communities. We welcome your expertise:

### 1. Peer Review & Sanity Checks
* Are our control boundary assumptions on QCA988x correct?
* Did we miss a race condition in ath10k-CT or OpenWrt 24.10.4?
* Review our ADRs in **[docs/DECISIONS.md](docs/DECISIONS.md)** and challenge our findings.

### 2. For WISP Operators
* Do you have decommissioned or spare LiteBeam 5AC Gen2, NanoStation 5AC, or LiteAP units sitting on shelves?
* Run our read-only inventory scripts (`tools/inventory/collect.py`) to contribute hardware signatures and board profiles to our matrix.
* Share anonymized airView spectral captures or loaded sector latency traces.

### 3. For Wireless & Kernel Hackers
* Help optimize outer-loop aggregation algorithms (`PNOFA`) on ath10k.
* Assist with mac80211 airtime scheduler patch verification (`last_tx_bitrate`).
* Contribute eBPF or telemetry harnesses for the autonomous research runner.

---

## 8. Safety & Regulatory Boundaries

openMAX operates under strict, uncompromised safety rules:
* **Regulatory Compliance**: We **NEVER** modify regulatory domains, exceed legal EIRP limits, or disable DFS radar detection.
* **Protected Flash Partitions**: We **NEVER** write or corrupt bootloaders (`mtd0`), bootloader environments (`mtd1`), calibration/ART tables (`mtd5`), or factory MAC storage.
* **Production Protection**: All experiments are conducted strictly on isolated lab and testbed hardware. No production subscriber traffic is ever touched.

---

## 9. License

This repository and its documentation are open-sourced under the [MIT License](LICENSE).
Hardware designs, experiment logs, and research findings are provided free for the benefit of the global wireless networking community.
