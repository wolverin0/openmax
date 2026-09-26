# Community Call for Collaboration: The FuturaMAX Open Knowledge Hub

> **"We are doing this without knowing a single thing of kernel programming beyond being an everyday WISP provider with real towers and roofs—teaming up with autonomous AI agents to research, verify, and test every physical limit of this hardware in the open."**

---

## 1. An Open Invitation to the Wireless & Open-Source Community

Millions of **Ubiquiti airMAX AC** radios (LiteBeam 5AC Gen2, LiteAP GPS, NanoStation 5AC, Loco 5AC) power broadband connections for rural and underserved communities across the globe. 

However, manufacturer R&D on this 802.11ac hardware family has essentially ended. Vendors have moved their engineering attention to proprietary 60 GHz (Wave) and custom-silicon LTU platforms. As a result, the firmware running on millions of deployed outdoor radios is frozen on 2016–2018 kernel architectures—suffering from 30-retry frame storms during fades, bufferbloat exceeding 2,000 ms, and lack of modern airtime-fair queueing.

**FuturaMAX is an open-source, community-driven research initiative to change that.**

We are combining:
1. **Real-World WISP Infrastructure**: Active towers, commercial rooftops, 24V PoE switches, and real outdoor RF links.
2. **Autonomous AI Research Agents**: Codex, Claude, and Gemini/Antigravity operating under a strict scientific constitution (verifying claims against kernel source code, peer-reviewed literature, and physical testbeds).
3. **Open-Source Tooling**: OpenWrt 24.10.4, Linux mac80211, Candela Technologies ath10k-ct, CAKE, and automated regression runners.

We are building this repository as a **public knowledge hub** so that network operators, kernel developers, and wireless researchers can pool documentation, validate findings, and push this hardware to its absolute physical maximum.

---

## 2. What We Have Built & Discovered So Far

In just our initial development milestones, this project has established:

1. **The Exact Hardware Control Boundary on QCA988x**:
   * Verified in Linux `drivers/net/wireless/ath/ath10k/mac.c` that unicast rate control is firmware-owned (`HAS_RATE_CONTROL`).
   * Proved that Minstrel-HT / IteRate cannot attach to the host driver directly; rate optimization must occur via **supervisory rate-masking (`ratemask-CT`)** and **ingress pacing**.
2. **The 30-Retry Discovery**:
   * Discovered that upstream Qualcomm firmware enforces **30 retries** per frame, causing catastrophic airtime starvation across an entire sector when a single CPE experiences an RF fade.
   * Confirmed that Candela Technologies (`ath10k-ct`) slashes this to 4 retries, freeing massive airtime for fixed links.
3. **The `last_tx_bitrate` Airtime Cliff**:
   * Identified that because QCA988x (Wave 1) lacks firmware airtime reporting (`WMI_SERVICE_REPORT_AIRTIME`), Linux mac80211 calculates airtime based on host estimation.
   * If peer stats are not actively delivering transmission rates, the driver falls off a cliff—assuming every CPE transmits at 6 Mbps and destroying airtime fairness.
4. **The CoTSQ Aggregation Breakthrough**:
   * Synthesized testbed research proving that default Linux TCP Small Queues (TSQ = 1 ms) starves 802.11ac aggregation engines.
   * Sizing queues to **6 ms of airtime** unlocks an order of magnitude goodput gain while preserving sub-40 ms latency under full saturation.
5. **Physical Testbed Engineering**:
   * Solved the "Warehouse Fallacy": Proved mathematically that indoor metal warehouses create destructive Rayleigh multipath echoes and ruin PtMP test validity.
   * Engineered a 2-Tier testbed: Coaxial SMA attenuator matrices on the bench, and a 21-meter cross-building outdoor sector between our commercial WISP office and residential roof.
6. **Automated Unattended Unbricking**:
   * Proved that remote-reset PoE injectors can be automated via USB relays to trigger U-Boot `urescue` recovery mode unattended without physical human presence.

---

## 3. How You Can Help / Ways to Collaborate

You do not need to be a kernel maintainer or a Ph.D. in electrical engineering to contribute. We need help across every tier:

### A. For Wireless ISPs and Network Operators
* **Hardware Profiling**: Run our safe, read-only inventory probe (`tools/inventory/collect.py`) on your bench spares to catalog board revisions, flash memory maps, and bootloader versions.
* **Spectral Captures**: Share anonymized airView spectral logs and RF traces from noisy tower sectors.
* **Canary Testing**: Test our passive sysctl / CAKE queueing configurations on lab testbeds and report loaded latency (Flent RRUL) benchmarks.

### B. For Linux Kernel, ath10k, and OpenWrt Developers
* **Driver Sanity Checks**: Review our analysis in [`knowledge/ATH10K_CT_FIRMWARE_DEEP_DIVE.md`](../knowledge/ATH10K_CT_FIRMWARE_DEEP_DIVE.md) and [`docs/QCA988X_CONTROL_BOUNDARY.md`](QCA988X_CONTROL_BOUNDARY.md).
* **Airtime Fairness Hook Verification**: Help verify whether OpenWrt’s packaged `ath10k-ct` driver properly exports `wake_tx_queue` and populates `last_tx_bitrate` across active stations.
* **Spectral Scan Integration**: Assist with RelayFS userspace daemons to parse raw FFT spectral bins in real time.

### C. For Academic Wireless Researchers
* **Theoretical Validation**: Critique our closed-form aggregation models ([`knowledge/PACED_AGGREGATION_AND_COTSQ.md`](../knowledge/PACED_AGGREGATION_AND_COTSQ.md)) and TDMA-vs-CSMA models ([`knowledge/PTMP_OUTDOOR_TDMA_VS_CSMA.md`](../knowledge/PTMP_OUTDOOR_TDMA_VS_CSMA.md)).
* **Multi-Armed Bandit Optimization**: Help refine the exploration policy for the autonomous research loop ([`knowledge/AUTONOMOUS_WIRELESS_RESEARCH_ENGINE.md`](../knowledge/AUTONOMOUS_WIRELESS_RESEARCH_ENGINE.md)).

---

## 4. How We Work: The Operator + AI Agent Workflow

We believe in complete transparency about how this project is built:
* **The Human Operator**: Formulates high-level research questions, owns the physical lab hardware, solders circuits, routes Ethernet/coaxial cables, mounts antennas, and manages real-world WISP operations.
* **The AI Agents (Codex, Claude, Gemini/Antigravity)**: Read Linux kernel source trees, query academic preprint databases (Scholar, arXiv, NotebookLM), cross-examine driver implementations, write automated test runners, and draft documentation.
* **The Scientific Gatekeeper**: No AI-generated claim is accepted into this repository without citation of an exact source line or physical confirmation on live hardware. Every claim is tagged:
  * `[CONFIRMED]`: Proven on our hardware or in kernel source.
  * `[INFERRED]`: Plausible from peer literature, awaiting testbed run.
  * `[UNKNOWN]`: Unmeasured.
  * `[REFUTED]`: Disproven.

---

## 5. Getting Started

1. Read our master documentation map: [`docs/DOCS-MAP.md`](DOCS-MAP.md).
2. Review our active experiments and test plan: [`docs/EXPERIMENTS.md`](EXPERIMENTS.md).
3. Review our architectural decisions: [`docs/DECISIONS.md`](DECISIONS.md).
4. Check our contribution guide: [`CONTRIBUTING.md`](../CONTRIBUTING.md).
5. Open an Issue or Pull Request on GitHub to join the conversation!
