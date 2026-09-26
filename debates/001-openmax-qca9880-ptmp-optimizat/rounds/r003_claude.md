# Round 3 - Claude

**Consensus Items:**
- Baseline stock airOS first, with A/A calibration (same firmware both cells, swap nothing) to measure the noise floor before any A/B claim.
- Saturated hidden-node uplink is the deciding scenario. Download, upload, and bidirectional are measured separately, loaded latency is the primary metric.
- Rate selection stays in firmware. The host clamps rate ceilings and manages queues, never steers per packet.
- AQL fixes AP-side bufferbloat only. It does not schedule reverse-direction airtime.
- Shaping and research compute cannot run at line rate on the MIPS 74Kc.
- Both ends of a cell must be flashed. Migration is per cell, never per CPE.
- Two APs 21 m apart are one RF domain. Co-channel contamination is real, and channel separation is mandatory for A/B validity.
- Soft-poll via PS-Poll/U-APSD is dead. It cannot grant uplink TXOPs.

**Final Architecture Compromise:**
Run OpenWrt 24.10.4 with stock ath10k, AQL, and airtime fairness as the entire first arm. No custom scheduler. The airOS arm is shaped on downlink only, and that limitation is documented, not hidden. The AP is the shaping point in both arms. The only openMAX-specific code in scope is a rate ceiling clamp and per-station airtime weighting, both host-side and both below the firmware boundary. Uplink contention is addressed by measurement first, and a cooperative CPE admission mechanism is a P2 research question gated on the P0 data showing OpenWrt loses the hidden-node case.

**Prioritized Action Items:**
- **P0: Recovery qualification.** Verify serial console, TFTP recovery, and full mtd backup for both board types before any flash. Codex is right that rollback partitions cannot be assumed.
- **P0: airOS baseline on both cells, then A/A on OpenWrt.** Separate channels with measured adjacent-channel leakage, not weekly role swaps.
- **P0: Hidden-node uplink harness.** 20 CPEs, iperf3 reverse mode, staggered start, loaded RTT via irtt. This is the go/no-go test.
- **P1: Rate clamp and airtime weights** as host-side tunables, evaluated only after P0 shows where stock loses.
- **P1: Downlink CAKE at the AP** in both arms, sized to what the AP CPU actually sustains at measured PPS.
- **P2: Cooperative admission protocol** investigation, contingent on P0 evidence.

**Rejected Ideas / Non-Goals:**
- Soft-poll or any PS-mechanism uplink scheduling. Wrong direction, confirmed by all three.
- CAKE on airOS CPEs or 20 external shaper boxes. Not deployable in this budget.
- Custom TDMA MAC in ath10k firmware. Firmware boundary, no source, no timeline.
- Per-packet rate steering from the host. Latency and CPU make it worse than firmware.
- Weekly role swaps between co-located APs as an isolation strategy.
- Any claim that OpenWrt improves this testbed before the P0 harness runs. That remains UNKNOWN.

**Final Confidence:** 72%
