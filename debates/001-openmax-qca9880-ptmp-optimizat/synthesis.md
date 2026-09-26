# Debate Synthesis: openMAX QCA9880 PtMP Optimization: Reconciling OpenWrt Hybrid CSMA/AQL vs airOS TDMA on 2 AP + 20 CPE Testbed

## Advisor Summary Table

| Advisor | Final Position | Confidence | Key Contribution |
|---|---|---|---|
| **Claude** | Pragmatic minimalist OpenWrt deployment; stock driver + host rate-clamping; AP-focused shaping boundary. | 72% | Formalized the A/A baseline calibration protocol and enforced the RF co-location penalty (21 m separation = single RF domain). |
| **Codex** | Rigorous empirical research harness; off-box symmetric shaping; formal experimental controls before architectural optimization. | 90% | Enforced hardware validation (LAP-120 vs. LAP-GPS), identified ath10k TX-rate reporting inaccuracies, and mandated whole-cell crossovers. |
| **Gemini** | Hybrid offloaded architecture; upstream x86/ARM shaping engine paired with lightweight CPE ingress rate-limiting and RTS/CTS. | 95% | Proved the MIPS 74Kc CPU collapse under line-rate CAKE, defining the split-plane shaping architecture (external downlink gateway + CPE TBF). |

---

## Consensus (Unanimously Agreed)

- **MIPS 74Kc CPU Limits:** The Atheros AR9342 SoC (533–600 MHz MIPS 74Kc) cannot execute line-rate CAKE shaping or research telemetry processing under high packet-per-second (PPS) loads without inducing severe CPU starvation, buffer depletion, and packet drops.
- **Firmware-Owned Rate Control:** The QCA9880 3x3 802.11ac radio firmware strictly controls real-time frame transmission and rate selection. The host driver cannot steer per-packet rates; host-side optimization is strictly confined to setting MCS ceilings, rate masks, and queue pacing parameters via `mac80211`/`ath10k`.
- **AQL Boundary Definition:** Airtime Queue Limits (AQL) bounds bufferbloat exclusively in the AP’s local transmit ring. It has zero visibility into or control over reverse-direction (uplink) airtime or CPE transmission schedules.
- **Decisive Stress Scenario:** Saturated hidden-node uplink across 20 CPEs is the critical failure mode for CSMA/CA. It represents the go/no-go benchmark against airOS TDMA (airMAX ac).
- **Mandatory Stock Baseline:** Testing must begin with an unadulterated stock airOS TDMA baseline across both cells, backed by A/A calibration (identical firmware across both cells) before any comparative A/B OpenWrt claims can be validated.
- **Cell-Level Flash Boundary:** Transitioning between airOS and OpenWrt must happen at whole-cell granularity (1 AP + 10 CPEs). CPEs cannot run hybrid CSMA against an airMAX TDMA AP.
- **Rejection of Soft-Poll:** Unscheduled PS-Poll / U-APSD uplink pseudo-TDMA schemes are dead on arrival; APs cannot grant reverse-direction TXOPs via 802.11 power-save mechanisms without massive latency jitter and framing overhead.

---

## Key Disputed Issues & Resolutions

| Issue | Claude View | Codex View | Gemini View | Final Resolution |
|---|---|---|---|---|
| **Uplink Contention & Shaping Placement** | Shape only at the AP on downlink; uplink contention must be handled by airtime weighting and measured at the AP. Avoid deploying extra shaper nodes behind CPEs. | Shaping must be strictly symmetric. POP-side upload policing fails to mitigate RF contention; endpoints or existing routers behind CPEs must pace uplink traffic before RF transmission. | Run lightweight on-box egress shaping (TBF/basic HTB) directly on OpenWrt CPEs, augmented by aggressive hardware RTS/CTS thresholds to tame hidden nodes. | **Adopt Gemini's on-CPE lightweight shaping + Codex's test-endpoint isolation.** Dedicated test runners behind CPEs pace uplink traffic during benchmark runs. In production, OpenWrt CPEs run lightweight TBF (avoiding MIPS CAKE overhead) combined with dynamic RTS/CTS to mitigate hidden-node collisions before RF entry. AP-side ingress policing is rejected as a collision remedy. |
| **Downlink AQM / CAKE Placement** | Run CAKE directly on the AP's MIPS 74Kc, capped conservatively to whatever bandwidth/PPS the CPU can sustain. | POP-side off-box shaping upstream of the radio link. Keep all compute-heavy queue algorithms off the embedded AP board. | Offload downlink CAKE entirely to an external x86/ARM gateway router upstream of the AP. Run stock AQL + `fq_codel` locally on the AP. | **Adopt Gemini & Codex: External Gateway Offload.** The AP's AR9342 will not execute CAKE. Downlink traffic must be pre-shaped by an upstream edge box (x86/ARM) running CAKE. The AP runs native `ath10k` AQL with driver-level `fq_codel`. |
| **Inter-Cell RF Isolation & Experimental Crossover** | Two APs at 21 m form a single RF domain. Use fixed, widely separated non-overlapping channels and measure adjacent-channel leakage; reject frequent role swaps. | Crossover is mandatory to eliminate physical/hardware confounders. Execute scheduled, fully recorded block-level whole-cell crossovers after A/A qualification. | Automate dynamic channel and role swaps within the orchestration suite to continuously randomize RF interference variables. | **Adopt Claude’s isolation with Codex’s scheduled block crossover.** Frequent automated role swaps introduce RF chaos. The testbed will establish static, orthogonal frequency assignments with documented adjacent-channel leakage profiles, run baseline A/A passes, and execute a single mid-campaign whole-cell physical crossover to eliminate hardware bias. |

---

## Risks & Failure Modes

| Risk | Identified By | Severity | Mitigation Strategy |
|---|---|---|---|
| **Hardware Variant Bricking (LAP-120 vs. LAP-GPS)** | Codex | **CRITICAL** | Audit board IDs, partition tables, and SPI flash layouts via U-Boot serial console prior to flashing. Validate TFTP recovery paths on a sacrificial bench unit before provisioning the 22-node testbed. |
| **MIPS 74Kc CPU Starvation** | Gemini / Claude | **HIGH** | Offload all CAKE instances, heavy telemetry collection, and distributed coordination engines off the AP/CPE hardware to external edge infrastructure. Maintain local AP usage strictly for the network stack, `ath10k`, and basic `fq_codel`. |
| **Hidden-Node Uplink Collapse** | All | **HIGH** | Enforce hardware-assisted RTS/CTS thresholds on all CPEs in the OpenWrt cell when station count > 5. Implement strict per-CPE ingress rate clamps (TBF) to prevent radio ring exhaustion. |
| **ath10k Telemetry Desynchronization** | Codex | **MEDIUM** | Do not trust instantaneous tx-rate telemetry reported by `ath10k` firmware for real-time control loops. Use end-to-end active probe telemetry (`irtt`, OWAMP) from test harness endpoints for control decisions. |
| **Adjacent-Channel Leakage Contamination** | Claude | **MEDIUM** | Separate the two co-located APs (21 m apart) across UNII-1 and UNII-3 bands. Verify receiver noise floors via spectrum analysis with Cell A transmitting at full EIRP while Cell B is idle. |

---

## Actionable Engineering Roadmap

```
Phase 1 (P0: Recovery & Baselines)
├── Verify 22 boards (LAP-120/GPS) & serial/TFTP recovery
├── Build automated test harness (iperf3, irtt)
├── Run airOS vs airOS (A/A) baseline (1/10/20 CPEs)
└── Run unoptimized OpenWrt baseline on Cell A

Phase 2 (P1: Hybrid CSMA Stack Optimization)
├── Deploy external x86/ARM CAKE shaping gateway (Downlink)
├── Configure ath10k AQL + host-side MCS rate clamping on AP
├── Deploy lightweight TBF egress shaping + RTS/CTS on CPEs
└── Execute isolated Uplink/Downlink/Bidirectional load matrices

Phase 3 (P2: Multi-Cell & Autonomous Policy Engine)
├── Execute scheduled whole-cell crossover (swap firmware between cells)
├── Evaluate host-side dynamic airtime weighting (mac80211)
└── Finalize openMAX deployment policy guidelines
```

### Phase 1: Immediate Critical Path (P0)
- **Board Inventory & Recovery Qualification:** Verify partition maps and board IDs across all 22 nodes (specifically distinguishing LiteBeam AP-120 from LAP-GPS). Flash and validate bootloader TFTP recovery mechanisms on bench units. Create full raw `mtd` partition backups for every unit.
- **Harness & Automation Deployment:** Stand up an out-of-band management network and Linux test endpoints behind each CPE. Deploy automated benchmarking runners executing `iperf3` (throughput) and `irtt` (deterministic loaded latency/jitter), recording p95/p99 RTT, goodput, retransmissions, and airtime metrics.
- **Stock airOS TDMA Baseline:** Run systematic A/A benchmarks on stock airOS across both cells simultaneously. Sweep load scenarios: 1, 10, and 20 CPEs under pure downlink, pure uplink, and bidirectional saturated streams. Record noise floor and adjacent-channel leakage across the 21 m baseline.
- **OpenWrt Baseline Arm:** Flash Cell A with stock OpenWrt (latest stable, vanilla `ath10k`, default AQL enabled). Run identical traffic matrices to quantify the unoptimized CSMA vs. airOS TDMA delta, focusing explicitly on the hidden-node uplink case.

### Phase 2: Scalability & Engine Optimization (P1)
- **External Shaping Gateway Integration:** Insert an external x86/ARM router at the POP/AP boundary. Configure dual-tier CAKE shaping instances directed at AP downlink queues, enforcing fair queuing and bandwidth limits before packets reach the AR9342 network driver.
- **AP Driver & Queue Optimization:** Tune `ath10k` AQL parameters and verify ring-buffer sizing to eliminate local bufferbloat without stalling radio pipelines. Configure host-side MCS ceilings based on RF link margins to prevent firmware rate-hunting collapse on lossy links.
- **CPE Ingress Pacing & Collision Defense:** Configure OpenWrt CPEs with lightweight egress rate-limiters (`tc-tbf`) to bound transmission buffers. Enable and tune hardware RTS/CTS thresholds on the CPE radios to protect uplink transmissions against hidden-node interference.
- **Comparative Multi-Factor Benchmark:** Execute the full traffic suite against the optimized OpenWrt cell versus the stock airOS TDMA cell.

### Phase 3: Advanced Intelligence & Autonomy (P2)
- **Whole-Cell Crossover Validation:** Invert the cell configurations (Cell A transitions to airOS, Cell B transitions to OpenWrt) during a scheduled maintenance window. Rerun the P1 matrix to decouple radio/RF site anomalies from firmware performance metrics.
- **Dynamic Host Airtime Weighting:** Evaluate dynamic `mac80211` station airtime weighting on the AP to penalize low-MCS stations during mixed-rate saturation events.
- **Policy Synthesis & Archival:** Aggregate empirical data into an open-source openMAX deployment guide detailing where hybrid CSMA/AQL remains viable and defining the precise scale limits where TDMA remains mandatory.

---

## Non-Goals & Discarded Ideas

- **Soft-Poll / U-APSD Uplink Pseudo-TDMA:** Discarded entirely. Stations cannot be reliably polled without standard MAC modifications, firmware scheduling jitter introduces untenable latency variance, and the framing overhead degrades aggregate airtime.
- **On-Box CAKE on MIPS AR9342:** Discarded due to hard CPU constraints. Saturated packet rates will push the MIPS 74Kc into software interrupt (ksoftirqd) saturation, introducing severe processing latency and packet loss.
- **Per-Packet Host-Driven Rate Selection:** Discarded. The QCA9880 firmware architecture handles frame aggregation and rate stepping internally via closed-source microcode. Injecting real-time host steering violates the driver/firmware separation boundary and induces rate-selection instability.
- **Continuous / Dynamic Channel Role Swapping:** Discarded. Automated alternating role swaps between two co-located APs introduce unpredictable spectral coupling and adjacent-channel interference dynamics, corrupting long-term telemetry trends.
- **Custom TDMA MAC Engine inside ath10k:** Discarded as out of scope for the testbed budget and project timeline. Modifying closed firmware binaries without source is untenable.

---

## Verification & Next Steps

1. **Gate Zero (Bench Test):** Confirm serial U-Boot break-in and TFTP recovery on one AR9342 AP and one CPE. If unbricking fails via TFTP, halt testing.
2. **Telemetry Validation:** Run a single-station iperf3 saturation test into `ath10k` on OpenWrt; compare active `irtt` one-way delay against kernel queue drops to confirm AQL is actively regulating the AP queue without CPU starvation.
3. **Execution of the Decisive Test (Go/No-Go Gate):**
   - Populate the 20-CPE OpenWrt cell in a hidden-node configuration.
   - Run 20 concurrent saturated `iperf3` reverse-mode (uplink) streams with staggered starts.
   - Concurrently measure loaded latency via `irtt` at 20 pps per station.
   - **Success Threshold:** The OpenWrt hybrid stack must achieve a p99 loaded round-trip latency under 150 ms and aggregate goodput within 25% of the airOS TDMA baseline under identical RF conditions. If CSMA collapses into packet-retry livelock (p99 latency > 1000 ms, > 30% drop rate), OpenWrt PtMP on QCA9880 is empirically restricted to low-density or line-of-sight/non-hidden-node topologies.