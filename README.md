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
| **[docs/COMMUNITY_CALL_FOR_COLLABORATION.md](docs/COMMUNITY_CALL_FOR_COLLABORATION.md)** | **Community Manifesto**: How WISPs, kernel devs, and researchers can collaborate with our AI loop. |
| **[knowledge/ATH10K_CT_FIRMWARE_DEEP_DIVE.md](knowledge/ATH10K_CT_FIRMWARE_DEEP_DIVE.md)** | **ath10k-ct Firmware Internals**: 30 vs 4 retries, HTT credit rings, bufferbloat, peer stats, and the 6 Mbps airtime cliff. |
| **[knowledge/PACED_AGGREGATION_AND_COTSQ.md](knowledge/PACED_AGGREGATION_AND_COTSQ.md)** | **Paced Aggregation & CoTSQ**: Mathematical model of A-MPDUs; why TSQ=1ms starves throughput and CoTSQ=6ms restores 10× goodput. |
| **[knowledge/PTMP_OUTDOOR_TDMA_VS_CSMA.md](knowledge/PTMP_OUTDOOR_TDMA_VS_CSMA.md)** | **Outdoor PtMP Physics**: Hidden node collapse, airMAX AC proprietary Xtensa/ASIC architecture, and OpenWrt hybrid solutions. |
| **[knowledge/AUTONOMOUS_WIRELESS_RESEARCH_ENGINE.md](knowledge/AUTONOMOUS_WIRELESS_RESEARCH_ENGINE.md)** | **Autoresearch Engine Architecture**: Karpathy-style closed-loop AI optimization, multi-objective reward function $J(\theta)$, and A/B/A/B gate. |
| **[knowledge/SPECTRAL_AND_CSI_ANALYSIS.md](knowledge/SPECTRAL_AND_CSI_ANALYSIS.md)** | **Spectral & CSI Analysis**: Baseband FFT scanning via RelayFS vs structural absence of CSI on QCA988x. |
| **[docs/CURRENT_STATE.md](docs/CURRENT_STATE.md)** | **Living State Log**: Chronological development log (read latest addendum first). |
| **[docs/DECISIONS.md](docs/DECISIONS.md)** | **Architectural Decision Records**: D-0001 through D-0010 (D-0009 autoresearch, D-0010 testbed). |
| **[docs/EXPERIMENTS.md](docs/EXPERIMENTS.md)** | **Experiment Register**: FMX-0001 through FMX-0011 and Stage-3 Campaigns C1–C8. |
| **[docs/TESTBED_ENVIRONMENT_GUIDE.md](docs/TESTBED_ENVIRONMENT_GUIDE.md)** | **2 AP + 20 CPE Testbed Guide**: RF attenuation, Fraunhofer distance, unattended recovery. |
| **[knowledge/REAL_HARDWARE_LITERATURE.md](knowledge/REAL_HARDWARE_LITERATURE.md)** | **Literature Catalogue**: Verified analysis of IteRate, WiFiSpectralJam, PNOFA, and Quick & Plenty. |
| **[docs/QCA988X_CONTROL_BOUNDARY.md](docs/QCA988X_CONTROL_BOUNDARY.md)** | **Hardware Control Boundary**: What the host can and cannot control under ath10k-CT. |
| **[safety/recovery/FMX-0002_recovery_runbook.md](safety/recovery/FMX-0002_recovery_runbook.md)** | **Recovery Runbook**: Proven TFTP urescue and return-to-stock procedures. |

---

## 5. Current Research Baseline & Breakthroughs

### What We Have Confirmed
1. **OpenWrt 24.10.4 is Running on Lab Hardware**: Successfully flashed and booted on a lab Ubiquiti LiteAP 120 (LAP-120, AR9342 + QCA988x, sysid `0xe8e5`) via our verified `dd-unlock` pipeline.
2. **Bootloader Recovery is Proven**: U-Boot 1.1.4-s1100 enforces RSA signatures over TFTP `urescue`, refusing unsigned images, but reliably restoring stock airOS signed binaries without serial or case opening.
3. **The Radio Firmware Architecture**: airMAX AC loads three distinct proprietary radio firmware binaries (`_ptp_bin`, `_ptmp_ap_bin`, `_ptmp_sta_bin`) directly into the radio's Xtensa processor. airMAX polling runs partly on the radio core.
4. **The Host Control Surface**: Unicast rate selection is firmware-offloaded on QCA988x (`HAS_RATE_CONTROL`). However, outer-loop control over **A-MPDU bounds (`htt_max_amsdu_ampdu`)**, **rate masks (`ratemask-CT`)**, **AQL queue limits**, and **spectral FFT capture** is completely viable from the host.

### What the Autonomous Loop Targets (Inferred Gains)

```
┌──────────────────────────────────────┬──────────────────────┬──────────────────────────────────────────┐
│ Performance Metric                   │ Expected Target      │ Core Mechanism                           │
├──────────────────────────────────────┼──────────────────────┼──────────────────────────────────────────┤
│ Clean Single-CPE Speedtest           │ +5% to +10%          │ PHY ceiling already maxed by 256-QAM.    │
│ Loaded Sector Usable Capacity (PtMP) │ +25% to +35%         │ Aggregation tuning + retry-probe bypass. │
│ Loaded p99 Latency (Under Saturation)│ 5× to 10× reduction  │ AQL + CAKE bufferbloat elimination.      │
│ Airtime Reclaimed from Waste         │ 15% to 25%           │ Restricting rate masks via ratemask-CT.  │
│ Weak-Client Isolation                │ Near-total           │ Airtime-deficit round-robin scheduling.  │
└──────────────────────────────────────┴──────────────────────┴──────────────────────────────────────────┘
```

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
