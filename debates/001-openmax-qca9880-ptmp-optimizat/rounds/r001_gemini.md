# Round 1 - Gemini

**Position:** Execute a strict Stage 1 airOS baseline first, then deploy OpenWrt with `ath10k-ct`, mac80211 AQL, and dynamic MCS ceiling clamps; pure CSMA cannot beat airMAX TDMA on saturated uplink without hardware RTS/CTS and airtime pacing.

**Key Arguments & Proposals:**
- **Two-Phase Evolution:** Baseline airOS under Flent RRUL loads (collecting latency, jitter, throughput) before flashing. This establishes an empirical ground truth and prevents optimizing against imaginary targets.
- **Respect the QCA9880 Boundary:** The AR9342 MIPS 74Kc (533–600 MHz) cannot process per-packet host rate control. Reject custom host-level rate control. Instead, use `ath10k-ct` firmware and control rate adaptation macroscopically: clamp per-station MCS ceilings via `nl80211` ratemasks, tune htt-tx buffer depth, and cap A-MPDU duration to $\le 4\text{ ms}$ (max 32 subframes) to prevent single-station airtime hogging.
- **Tame CSMA PtMP via AQL + CAKE:** In mac80211, configure Airtime Queue Limits (AQL) to bound intermediate driver queues to $\le 6\text{ ms}$. Run CAKE at the AP egress (downlink) and ingest at CPEs with per-station isolation. Enforce dynamic hardware RTS/CTS thresholds ($\approx 512\text{ bytes}$) and explicit `coverage_class` to eliminate hidden-node degradation across 10–20 stations.
- **Differential Auto-Research Loop:** Outdoor RF is non-stationary. Parameter mutation loops must use an A/B split architecture: AP1 runs the candidate mutation while AP2 serves as an un-mutated control link running identical traffic. Evaluate fitness via differential $\Delta\text{Latency-Under-Load}$ and $\Delta\text{JFI}$ (Jain’s Fairness Index) to normalize weather and ISM interference.

**Assumptions & Trade-offs:**
- *Assumption:* The 100m testbed exhibits sufficient RF cross-talk and asymmetric path loss to trigger hidden-station phenomena typical of multi-kilometer WISP cells.
- *Trade-off:* Capping A-MPDU size and enabling RTS/CTS trades absolute peak single-client aggregate throughput (down ~15%) for deterministic p99 latency and multi-client fairness under heavy contention.

**Risks & Failure Modes:**
- **MIPS CPU Saturation:** In-kernel CAKE and softirq overhead on the single-core MIPS 74Kc may bottleneck system throughput before the QCA9880 air interface saturates.
- **ath10k-ct Firmware Desync:** Aggressive htt-tx descriptor starving by AQL may cause internal firmware queue underflows or target watchdog resets.

**What Would Change My Mind:**
- Empirical Flent RRUL tests showing OpenWrt CSMA suffers >50% throughput collapse or >200ms latency bloat relative to airOS TDMA on a 20-CPE saturated uplink, even with tuned RTS/CTS and AQL.
- Proof that MIPS 74Kc CPU utilization hits 100% on CAKE packet scheduling at aggregate rates below 80 Mbps.

**Confidence:** 82%
