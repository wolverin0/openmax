# The Autonomous Wireless Research Engine: Karpathy-Style Closed-Loop Optimization for Fixed PtMP

> **Status**: SPECIFICATION & IMPLEMENTATION ARCHITECTURE (Inspired by Andrej Karpathy's autoresearch methodology, the IteRate framework [arXiv:2605.02542], and ADR D-0009).  
> **Mission**: An autonomous, closed-loop experimentation harness where AI agents iteratively propose, instrument, test, statistically validate, and keep/reject wireless system configurations on real Ubiquiti airMAX AC hardware.

---

## 1. Why Autonomous Experimentation for Fixed Wireless?

Modern wireless systems suffer from **high-dimensional parameter explosion**:
A single 802.11ac fixed wireless link is governed by dozens of interacting knobs:
* Kernel socket buffer limits (`tcp_limit_output_bytes` / CoTSQ).
* Queue disciplines (CAKE bandwidth, target RTT, flow isolation).
* mac80211 driver ring limits (`aql_threshold`, `aql_txq_limit`).
* Target firmware aggregation bounds (`htt_max_amsdu_ampdu`).
* Hardware rate-selection bounds (`ratemask-CT`).
* Physical channel parameters (RTS threshold, GI mode, TX power, CCA threshold).

Traditional wireless engineering relies on human heuristics or static vendor presets. But **outdoor fixed wireless is stationary and repetitive**:
* CPEs do not move.
* Antenna patterns, multipath reflections, and path losses are static over long periods.
* Atmospheric changes and diurnal interference follow measurable patterns.

By placing an autonomous AI research agent in a closed loop with physical testbed hardware, the system can systematically explore the parameter space, discovering non-intuitive configurations that extract maximum physical performance from legacy silicon.

---

## 2. System Architecture: The Five-Component Loop

```
┌────────────────────────────────────────────────────────────────────────┐
│                        1. Autonomous AI Agent                          │
│     (Formulates Hypothesis, Selects Knobs via Bayesian Search / LLM)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Propose Configuration θ_k
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       2. Safety Guardrail & Linter                     │
│    (Checks: Valid Range, Legal EIRP, Memory Bounds, Protected MTDs)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Safe Config Validated
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   3. Physical Testbed Orchestrator                     │
│  (Applies to AP & CPEs via SSH/UCI, Executes Flent/iperf3 Workloads)   │
│  [2 APs on WISP Building ◄─── 21m ───► 10-20 CPEs on Residential Roof] │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Harvest High-Resolution Telemetry
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   4. Statistical Regression Gate                       │
│    (Computes J(θ), Tests A/B/A/B Significance, Evaluates p99 Latency)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  ▼                                   ▼
          KEEP: Update Baseline              REJECT: Automated Rollback
          & Document Finding                 (Restore Known-Good Config)
```

### Component Details:

### 1. The Autonomous Agent (Planner / Search Algorithm)
* Maintains a persistent memory of all past experiments (`docs/EXPERIMENTS.md` and `docs/RESEARCH_LEDGER.md`).
* Combines **Bayesian Optimization** (for continuous knobs like AQL thresholds and pacing rates) with **LLM heuristic reasoning** (for discrete architectural choices like rate masks and queue disciplines).
* Proposes a single minimal change per experimental cycle:
  $$\Delta \theta = \theta_{candidate} - \theta_{baseline}$$

### 2. Safety Guardrail & Linter
* **Partition Protection**: Completely blocks any operation that touches `mtd0`, `mtd1`, `mtd5`, or calibration/ART data.
* **Regulatory Compliance**: Enforces hard clamps on TX power (EIRP) and regulatory domain boundaries; forbids DFS radar bypasses.
* **Memory Protection**: Enforces low-memory safety checks on MIPS 74Kc SoCs (preventing allocations that exceed 80% free RAM).

### 3. Physical Testbed Orchestrator
* Communicates with testbed radios over an isolated management VLAN.
* Applies parameter changes live via `sysctl`, `debugfs`, `iw`, or `/etc/config/wireless`.
* Runs standardized, multi-flow traffic workloads:
  * **Interactive / Latency**: Ping flood, VoIP jitter emulation.
  * **Bulk / Aggregation**: Multi-stream iperf3 TCP upload and download.
  * **Mixed / Multi-Client**: Flent RRUL (Realtime Response Under Load) running simultaneous saturated TCP flows while measuring ICMP p50/p95/p99 latency.

### 4. Telemetry Harvester
* Samples metrics at millisecond to second resolution:
  * Goodput (aggregate and per-CPE in Mbps).
  * Latency distribution (p50, p90, p95, p99, max in ms).
  * Retransmission ratio and packet error rate (PER).
  * Kernel queue drop counters (`mac80211`, `ath10k_tx_dropped`).
  * CPU utilization and free memory.

### 5. Statistical Regression Gate
* To eliminate random RF fluctuations and thermal noise, every promising candidate must pass a strict **A/B/A/B qualification protocol**:
  * Run Baseline ($A_1$) $\to$ Run Candidate ($B_1$) $\to$ Re-run Baseline ($A_2$) $\to$ Re-run Candidate ($B_2$).
* Evaluate using the **Mann-Whitney U non-parametric test** ($p < 0.01$). If the improvement is not statistically significant across all runs, it is rejected.

---

## 3. The Multi-Objective Reward Function

Fixed wireless optimization cannot optimize for a single metric like raw speedtest throughput. Squeezing maximum throughput while blowing latency to 2,000 ms destroys real-world subscriber Quality of Experience (QoE).

The Autoresearch engine optimizes a **composite scalar reward function $J(\theta)$**:

$$J(\theta) = w_{thr} \cdot \ln\left(\frac{G_{agg}}{G_{base}}\right) + w_{lat} \cdot \ln\left(\frac{L_{base, p99}}{L_{cand, p99}}\right) + w_{fair} \cdot \mathcal{J}_{fairness} - w_{ret} \cdot \left(\frac{R_{cand}}{R_{base}} - 1\right)$$

Where:
* $G_{agg}$: Aggregate sector goodput (Mbps).
* $L_{p99}$: 99th percentile loaded latency under saturation (ms).
* $\mathcal{J}_{fairness}$: Jain's Fairness Index across all active CPEs:
  $$\mathcal{J} = \frac{\left(\sum_{i=1}^N x_i\right)^2}{N \cdot \sum_{i=1}^N x_i^2}$$
* $R$: Packet retransmission ratio.
* Weights ($w_{thr} = 0.35, w_{lat} = 0.35, w_{fair} = 0.20, w_{ret} = 0.10$): Calibrated to punish latency inflation and unfair client starvation even if aggregate throughput increases slightly.

---

## 4. The Parameter Search Space

```
┌──────────────────────────────────────┬──────────────────────┬──────────────────────────────────────────┐
│ Parameter Name                       │ Type & Range         │ Subsystem & Control Path                 │
├──────────────────────────────────────┼──────────────────────┼──────────────────────────────────────────┤
│ `aql_threshold`                      │ 1,000 – 24,000 µs    │ `mac80211` driver queue threshold        │
│ `tcp_limit_output_bytes` (CoTSQ)     │ 32 KB – 512 KB       │ Linux TCP socket buffer limit            │
│ `htt_max_amsdu_ampdu`                │ 1–64 MPDUs           │ `ath10k-ct` debugfs aggregation bound    │
│ `ratemask-CT`                        │ Bitmask (MCS0–MCS9)  │ WMI peer-association rate constraint     │
│ `rts_threshold`                      │ 256 – 2347 bytes     │ `mac80211` RTS/CTS collision protection  │
│ `cake_bandwidth` / Pacing Rate       │ 5 Mbps – 100 Mbps    │ Linux TC / CAKE shaper at ingress        │
│ `cake_rtt`                           │ 5 ms – 100 ms        │ CAKE target round-trip delay tuning      │
│ `short_gi`                           │ Boolean (0 / 1)      │ Guard interval (800 ns vs 400 ns)        │
│ `coverage_class`                     │ 0 – 30 (distance)    │ Slot time and ACK timeout expansion      │
└──────────────────────────────────────┴──────────────────────┴──────────────────────────────────────────┘
```

---

## 5. Expected Empirical Numbers from Autonomous Search

Based on our empirical literature synthesis (IteRate, Hassani, Gringoli, Høiland-Jørgensen), the expected gains across search stages are:

| Optimization Stage | Primary Knobs Manipulated | Target Throughput Gain | Target Latency Reduction | Airtime Reclaimed |
|:---|:---|:---|:---|:---|
| **Phase 1: Queueing & Bufferbloat** | `aql_threshold`, CoTSQ, CAKE | +5% to +10% | **5× to 10× reduction** (<40 ms) | +5% |
| **Phase 2: Aggregation Pacing** | `htt_max_amsdu_ampdu`, TCP pacing | **+15% to +25%** | Neutral (<5 ms variance) | +10% |
| **Phase 3: Rate-Mask Bounding** | `ratemask-CT`, peer-association | +10% to +15% | -30% jitter | **+15% to +25%** |
| **Phase 4: Airtime Fairness (DRR)** | mac80211 airtime scheduler | **+2× to +5.4×** (on mixed sectors) | Eliminates starvations | Complete isolation |

---

## 6. Crash Recovery & Unattended Self-Healing

The autonomous loop is designed to run unattended overnight. If a candidate parameter triggers a kernel panic, radio firmware crash, or network disconnect:

1. **Watchdog Timer**: The candidate config is applied with a hardware watchdog:
   ```sh
   # If host does not cancel within 60 seconds, auto-reboot to baseline
   (sleep 60 && reboot) &
   ```
2. **Automated PoE Power-Cycle**:
   If the radio fails to respond to ICMP ping after 90 seconds, the central testbed controller commands the managed PoE switch to cycle port power.
3. **Automated Bootloader `urescue` Recovery**:
   If an image flash or persistent config bricks the radio, the controller engages the remote-reset relay on the PoE injector, forcing U-Boot into TFTP `urescue` mode at `192.168.1.20`, where our automated script reflashes stock firmware and restarts the loop.
