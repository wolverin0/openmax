# openMAX Architecture & Strategy Debate: QCA9880 PtMP Optimization

## Background & Mission
openMAX (formerly FuturaMAX) is an open R&D project to determine how much real-world performance, spectral efficiency, PtMP capacity, latency under load (bufferbloat), fairness, and operational intelligence can be extracted from existing Ubiquiti airMAX AC hardware (QCA9880 / AR9342 chipset family) through software, open firmware (OpenWrt/ath10k), custom rate control, queue management, telemetry, and automated experimentation loops.

### Target Hardware
- **Access Points**: Ubiquiti LiteAP GPS (LAP-GPS), LiteAP 120 (LAP-120)
- **CPEs / Stations**: LiteBeam 5AC Gen2 (LBE-5AC-Gen2), NanoStation 5AC Loco (Loco5AC)
- **SoC / Radio Architecture**: Atheros AR9342 MIPS 74Kc host CPU with Qualcomm Atheros QCA9880/QCA9882 802.11ac 3x3/2x2 radio over PCIe.
- **Flash/Boot**: SPI NOR flash, U-Boot bootloader. Strict safety rules protect bootloader (`mtd0`), calibration/ART (`mtd5` or `mtd1`), and EEPROM partitions.

### The Physical Testbed
- Real-world deployment between two buildings (~100m line of sight in an urban/suburban RF environment):
  - Rooftop station 1 (-33.895755, -60.575875)
  - Main WISP building station 2 (-33.895600, -60.575744)
  - 2 Access Points + 10 to 20 CPEs mounted, powered via POE switches with software-controllable power cycling and recovery safeguards.

---

## Core Debate Dilemmas

### 1. The CSMA vs. TDMA Outdoor PtMP Dilemma
- **airOS Baseline**: Ubiquiti uses a proprietary software/FPGA/silicon airMAX AC TDMA protocol. It achieves collision-free scheduling, deterministic slotting, and immunity to hidden-node collapses under heavy multi-client load, but is a black box with zero open telemetry, closed rate control, and outdated queueing.
- **OpenWrt / ath10k Alternative**: Provides complete open access to Linux network stack, CAKE/FQ-CoDel, modern Airtime Queue Limits (AQL), mac80211 station airtime scheduling, spectral FFT capture, and potential fast per-station rate-masking (`ratemask-CT`). However, standard 802.11ac in OpenWrt uses CSMA/CA with backoff.
- **Key Question**: Can open-source CSMA/CA augmented with AQL, CAKE, coverage-class timing, and aggressive per-station rate masking genuinely compete with or beat airMAX AC TDMA in outdoor PtMP scenarios with 10-20 active CPEs? Or will hidden nodes and contention backoffs fundamentally degrade loaded throughput and jitter?

### 2. Control Boundary & Firmware Offload Reality
- On QCA9880/ath10k, rate control and frame aggregation (A-MPDU) are predominantly offloaded to the on-chip firmware (`qca988x/hw2.0/firmware-5.bin` or `ath10k-ct`).
- Host mac80211 cannot do microsecond-level per-frame unicast rate selection like ath9k/Minstrel.
- What is the true software control boundary? Can we achieve meaningful algorithmic control via `ratemask` constraints, CoTSQ 6 ms socket buffer limits, AQL airtime deficit tuning, and dynamic A-MPDU max subframe controls, or is a custom ath10k-ct firmware patch strictly necessary?

### 3. Evolutionary Path: Stage 1 (airOS Intelligence) vs. Stage 2/3 (OpenWrt Stack)
- Should openMAX focus immediately on replacing firmware with OpenWrt on the testbed, or should it first deploy a Stage 1 non-destructive intelligence layer on stock airOS (SSH/SNMP telemetry harvesting, core-network CAKE pacing, spectral scanning, and predictive channel/power optimization)?

### 4. Karpathy Auto-Research Loop Feasibility
- We want to implement an autonomous optimization loop (inspired by Andrej Karpathy's auto-research paradigm):
  `Hypothesis -> Parameter Mutation (TXQ, AQL, ratemask, MCS ceiling, aggregation, channel width) -> Automated Workload (iperf3, Flent/RRUL, mixed interactive/bulk) -> Telemetry Capture -> Statistical Regression Evaluation -> Keep/Rollback Decision`.
- How can this loop be safely and rigorously structured in an outdoor RF environment where weather, interference, and multipath fluctuate naturally?

---

## Advisor Goals for this Debate
- **Claude (Fable 5.1)**: Systems architecture, fail-safe protocols, control boundary rigor, and testing methodology.
- **Codex (GPT-6 Astra)**: Low-level driver implementation (ath10k/mac80211), MIPS kernel performance, memory/queue data structures, and concrete code paths.
- **Gemini (Gemini 3.8 Flash)**: Comprehensive mathematical models, spectral analysis, algorithmic queueing theory (AQL/CAKE), and holistic synthesis.
