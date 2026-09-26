# Full Transcript: openMAX QCA9880 PtMP Optimization: Reconciling OpenWrt Hybrid CSMA/AQL vs airOS TDMA on 2 AP + 20 CPE Testbed

**Debate ID:** `001-openmax-qca9880-ptmp-optimizat`  
**Participants:** Claude (Fable 5.1), Codex (GPT-6 Astra), Gemini (Gemini 3.8 Flash)  
**Date:** 2026-09-26 21:38:30Z  

---

## Round 1: Independent Technical Positions

### Claude (Round 1)
**Position:** Flash both ends of the testbed to OpenWrt/ath10k-ct now, but run stock airOS as an interleaved A/B control on the same masts, and treat the uplink contention problem, not downlink, as the make-or-break question.

**Key Arguments & Proposals:**
- The scope is custom firmware, and a flashed CPE cannot associate to a stock airMAX AP, so Stage 1 airOS-only telemetry is a baseline instrument, not the product. Keep 1 AP + N CPEs on airOS as the control arm and 1 AP + N on OpenWrt, swapping roles weekly so RF drift hits both arms.
- Downlink is already a single-transmitter problem. mac80211 airtime scheduler, AQL and CAKE at the AP give us most of TDMA's downlink fairness for free. Measure this first and publish it early.
- Uplink is where CSMA loses. Directional CPEs at the same site are mutually hidden. Propose a host-side "soft poll": AP-driven per-station TXOP grants via power-save triggers plus tight RTS threshold, measured against a firmware-level patch as the fallback.
- Control boundary, stated honestly: firmware owns per-frame rate and A-MPDU. Host owns ratemask per station, AQL deficits, TXQ limits, coverage class, RTS, channel/width, and the scheduler order. Prove what the host knobs buy before touching firmware.
- Safety protocol: never write mtd0 or ART; boot-count watchdog with automatic rollback partition; POE power-cycle as last resort; every experiment carries a revert script that runs unattended.
- Auto-research loop: interleaved ABAB trials, blocked by hour and weather, with A/A runs to establish the noise floor before any keep/rollback decision. Minimum detectable effect set from that floor, not chosen by hope.

**Assumptions & Trade-offs:**
- Assuming ath10k-ct firmware is stable enough under 20 stations with ratemask changes every few seconds. Sacrificing peak MCS aggressiveness for determinism.
- Assuming the AR9342 CPU cannot run CAKE at line rate. Shaping lives at the AP and core, not the CPE.
- Sacrificing the ability to migrate one CPE at a time in production. This is a full-cutover architecture.

**Risks & Failure Modes:**
- Uplink collapse above roughly 8 active CPEs from hidden-node collisions. This is the single result that could kill the CSMA path.
- Firmware crash loops from ratemask or AQL edge cases, leaving a mast dark until POE cycle.
- Auto-research loop chasing weather noise and "keeping" regressions. Guard with A/A calibration and holdout periods.
- Bricking from a mistaken partition write on SPI NOR.

**What Would Change My Mind:**
- Loaded uplink jitter on OpenWrt measurably worse than airOS at 10 CPEs with no host-side mitigation closing the gap. Then a firmware TDMA patch becomes mandatory and the roadmap reorders.
- ath10k-ct firmware instability above 12 stations. Then Stage 1 airOS intelligence becomes the only shippable product for a long time.

**Confidence:** 62%

---

### Codex (Round 1)
**Position:** Advance the OpenWrt lab alongside a measured airOS-plus-CAKE baseline; treat CSMA competitiveness as an experiment, not an architectural promise.

**Key Arguments & Proposals:**

- **INFERRED—access method:** AQL can reduce queued airtime; it cannot eliminate hidden-node collisions or schedule CPE uplinks from the AP. Expect the hardest case to be simultaneous hidden-node uploads. Test download, upload, and bidirectional traffic separately, with controlled RTS/CTS comparisons.
- **CONFIRMED—control boundary:** QCA firmware retains rate selection. CT exposes rate constraints, but support and semantics depend on firmware generation. Verify peer versus interface scope, update latency, and actual transmitted rates before building a controller. Existing CT capabilities may suffice without custom firmware. [CT documentation](https://www.candelatech.com/ath10k-ug.php)
- **Implementation priority:** Trace `mac80211 → ath10k TXQ dequeue → HTT submission → completion`. Measure pending bytes, estimated airtime, completion delay, stale rate estimates, CPU/softirq utilization, and allocation failures. Verify the installed CT branch actually integrates AQL; upstream support alone proves nothing about this build.
- **Aggregation:** The project’s source audit identifies `htt_max_amsdu_ampdu` as **device-wide**, with hardware enforcement still unverified. Sweep it independently of rate masks. A configured maximum does not prove actual aggregate length. [Control-boundary audit](<G:/_OneDrive/OneDrive/Desktop/Py Apps/futuraMAX/knowledge/QCA988X_CONTROL_BOUNDARY.md>)
- **Queue placement:** Run CAKE and optimization on a capable external controller/core. Place uplink pacing before CPE wireless transmission. A 6-ms CoTSQ setting is an experimental sender policy—not a universal optimum or control over forwarded TCP sockets.
- **Experiment design:** Compare stock airOS, airOS with external queue management, and OpenWrt with equivalent shaping. Scale 1→5→10→20 CPEs. Use randomized crossover blocks, matched offered load, washout periods, and confidence intervals over independent runs. Swap AP assignments; concurrent co-channel tests otherwise contaminate each other.
- **Automation:** Freeze evaluator, traffic traces, safety limits, and rollback logic. Permit one bounded mutation per trial. Preserve failures; reject invalid runs using predefined rules. Promote candidates only after held-out days/topologies satisfy goodput, p99 latency, fairness, and stability gates.

**Assumptions & Trade-offs:**  
**UNKNOWN:** exact-board capabilities and RF geometry. The supplied coordinates imply approximately **21 m**, not 100 m. Verify distance and the CPE-to-CPE interference graph. Keep research compute off the MIPS radios.

**Risks & Failure Modes:**  
Hidden-node collapse; firmware buffering defeating host pacing; rate-mask starvation; stale airtime estimates; telemetry overhead; optimizer overfitting interference. TDMA is not immune to external interference. Recovery must use exact-board qualification, never assumed MTD numbering.

**What Would Change My Mind:**  
Repeated hidden-node mixed-load wins would justify OpenWrt expansion. Persistent losses after verified queue/rate controls would favor retaining airMAX operationally.

**Confidence:** 87%

---

### Gemini (Round 1)
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

---

## Round 2: Cross-Examination & Stress-Testing

### Claude (Round 2)
**Agreements:** Baseline airOS before flashing. Rate selection stays in firmware; the host clamps, never steers per packet. Shaping and research compute live off the MIPS 74Kc. Saturated hidden-node uplink is the deciding case, and download/upload/bidirectional must be measured separately. Codex is right that 21 m, not 100 m, is what the coordinates imply, and that co-channel APs contaminate each other.

**Critique of Codex:**
- **"airOS plus CAKE" is not deployable as stated.** airOS radios cannot host CAKE, so uplink shaping requires an external box behind each of 20 CPEs. Either budget those boxes or admit the airOS arm is shaped on downlink only.
- **Crossover blocks ignore the flash constraint.** A custom-firmware CPE cannot associate with a stock airMAX AP, so the whole cell flips together. Reflashing 11 devices per block makes fine-grained crossover impractical. Blocks must be per day, per cell.
- **Sequential single mutations confound treatment with time** on non-stationary RF unless a concurrent control cell exists. Codex rejects concurrent cells but offers no substitute.

**Critique of Gemini:**
- **Per-station MCS ceilings via nl80211 do not exist.** The bitrate mask is per interface. Per-peer control on QCA9880 is a CT debugfs path with unverified semantics, exactly what Codex flagged.
- **A 512-byte RTS threshold means RTS on every aggregate.** Each exchange burns roughly 100 µs at the basic rate, and the RTS frames themselves still collide between mutually hidden CPEs. It reduces collision cost. It does not eliminate hidden nodes.
- **A subframe cap is not a duration cap.** Thirty-two subframes at a rate-controlled MCS1 last far longer than 4 ms. Bounding airtime needs firmware TXOP limits, which the audit says are unverified on this device.
- **The 21 m testbed likely has no hidden nodes.** Directional CPEs at that range hear each other through back-lobes and reflections. CSMA will look artificially good. Hidden nodes must be manufactured with attenuators or shielding, and the interference graph measured before any trial counts.
- **Coverage class at 21 m is noise.** It tunes ACK timeouts for kilometre links.

**Defended / Refined Position:** Both peers treat CPEs as uncontrollable stations. They are not. The project flashes both ends, so the CPE side can enforce coarse cooperative uplink pacing in software: the AP signals per-station transmit budgets and each CPE gates its own TXQ. That is a soft-TDMA layer above CSMA, built from mac80211 airtime weights plus CPE queue gating, and it is the only lever that addresses hidden-node uplink without firmware. Design: airOS baseline, engineered hidden-node topology, external CAKE, concurrent control cell on a separated channel plus day-level ABAB on the same cell, one mutation per trial. Promotion gate: saturated 20-CPE uplink within 15% of airMAX goodput at lower p99 latency. Fail that after cooperative pacing, and airMAX stays operational.

**Confidence:** 84%

---

### Codex (Round 2)
**Agreements:** Both correctly prioritize loaded latency, uplink contention, repeatable controls, and firmware control boundaries. Claude’s A/A calibration and Gemini’s stock-airOS baseline belong together. **UNKNOWN:** whether OpenWrt improves this exact testbed; neither scheduler architecture nor published gains establish that.

**Critique of Claude:** “Flash now” precedes board-specific recovery qualification. An automatic rollback partition cannot be assumed to exist or fit; protecting only mtd0/ART is insufficient.

The proposed soft poll has a directionality problem: **CONFIRMED**, PS-Poll/U-APSD mechanisms let stations request buffered downlink traffic; they do not establish AP-granted, contention-free uplink TXOPs. A cooperative CPE admission protocol could be investigated, but bounded firmware queues and release timing remain unproven. [Linux power-save documentation](https://www.kernel.org/doc/html/latest/driver-api/80211/mac80211.html)

Downlink has one AP transmitter, but competing uplink traffic, TCP acknowledgments, and neighboring sectors still matter. AQL plus airtime scheduling does not automatically reproduce TDMA fairness or isolation. Finally, failure of CSMA does not make a firmware TDMA patch feasible or mandatory.

**Critique of Gemini:** Several numeric prescriptions are unsupported: 32 subframes does not imply ≤4 ms across packet sizes and rates; an AQL setting is not a hard wall-clock queue-delay guarantee; 512-byte RTS cannot guarantee elimination of hidden-node degradation.

Per-station MCS ceilings through ordinary nl80211 require exact implementation proof. CT’s documented controls include firmware-specific interfaces and limitations; demonstrate enforcement over the air, separately for AP downlink and CPE uplink. [CT firmware guide](https://www.candelatech.com/ath10k-ug.php)

CPE ingress shaping occurs after downlink airtime has already been consumed; uplink requires control before CPE transmission. CPU concerns also conflict with assuming AP-local CAKE is viable. Benchmark forwarding and shaping separately, initially using an external shaper.

A 100 m setup does not establish representative hidden-node geometry. Concurrent APs may interfere, violating the assumption of independent controls. Neither an 8/12-station failure threshold nor a 15% throughput penalty has supporting measurements.

**Defended / Refined Position:** Qualify recovery, capture stock baselines, then compare upstream ath10k and ath10k-ct on isolated units. Prove each knob before combining treatments. Use randomized crossover blocks, characterize cross-sector interference, and retain untouched holdout runs.

Explicitly distinguish two 10-CPE sectors from one 20-CPE contention domain. Test both, with downlink, uplink, mixed traffic, and measured hidden-node relationships. Predefine goodput, p95/p99 latency, fairness, and reset gates. **INFERRED:** cooperative pacing merits investigation; custom TDMA remains gated by demonstrated control authority. Keeping airMAX with external intelligence remains a valid outcome.

**Confidence:** 88%

---

### Gemini (Round 2)
**Agreements:**
Both peers correctly identify hidden-node uplink contention as the existential threat to OpenWrt CSMA, acknowledge that the AR9342 MIPS CPU cannot sustain local CAKE shaping at line rate, and recognize that AQL manages AP-side bufferbloat rather than scheduling reverse-direction RF access. Rigorous A/B isolation is mandatory.

**Critique of Claude:**
1. **The "Soft-Poll" Fallacy:** AP-driven power-save triggers (PS-Poll/U-APSD) cannot substitute for TDMA uplink scheduling. Standard 802.11ac station firmware responds to trigger frames with unpredictable latency and contention windows, adding severe frame-exchange overhead that exacerbates airtime exhaustion under load.
2. **RF Cross-Contamination:** Weekly role swaps between co-located APs ignore adjacent-channel leakage and desensitization in a dense 21m–100m deployment. Running concurrent tests without synchronized silent periods invalidates comparative telemetry.
3. **Flashing Prematurity:** Flashing all CPEs immediately burns bridgeheads before validating whether ath10k-ct's host-ratemask updates cause memory leaks or softirq storms on MIPS under 20-station load.

**Critique of Codex:**
1. **Scope Paralysis:** Codex treats OpenWrt as an observational lab trial while over-investing in optimizing proprietary airOS with external shaping. The mission is delivering an open PtMP architecture, not tuning legacy Ubiquiti binaries.
2. **Static Audit Dogmatism:** Codex relies on a static code audit of `htt_max_amsdu_ampdu` being device-wide. Candela Technologies firmware builds frequently expose vendor-specific debugfs hooks (`/sys/kernel/debug/ieee80211/phyX/ath10k/`) that bypass standard HTT aggregation limits per-VAP or peer. This should be verified dynamically on live hardware rather than assumed dead on paper.

**Defended / Refined Position:**
We must pursue OpenWrt, but abandon Claude’s host-side software-polling fantasy and Codex's status-quo bias:
1. **Uplink Strategy:** Rely on aggressive, station-count-scaled RTS/CTS thresholds paired with strict ingress token-bucket rate limiting at the CPE boundary (simple `htb` or `tbf`, which the AR9342 *can* handle, offloading CAKE to the core).
2. **Hard Gate for Firmware TDMA:** Define an explicit milestone at Phase 2: If OpenWrt loaded uplink p99 jitter exceeds airOS by >2.5× at 10 hidden CPEs despite RTS optimization and rate capping, abandon pure CSMA and immediately pivot engineering resources to low-level TDMA framing patches in ath10k-ct.
3. **Execution Safety:** Qualify 1 AP + 5 CPEs on an isolated RF channel first; verify CT debugfs knobs for dynamic peer-aggregation control before committing the remaining 15 nodes.

**Confidence:** 78%

---

## Round 3: Convergence & Roadmap Proposals

### Claude (Round 3)
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

---

### Codex (Round 3)
**Consensus Items:** Baseline stock airOS before conversion. Keep research compute and heavy shaping off the radios. Firmware owns rate selection; host constraints require verification. Measure download, upload, and bidirectional traffic separately. Saturated hidden-node uplink is the decisive stress case. **UNKNOWN:** whether OpenWrt improves this exact fleet.

**Final Architecture Compromise:** Build openMAX as an OpenWrt research stack with an external controller, instrumented ath10k/mac80211 queues, and ordinary CSMA access. Retain airOS TDMA as the benchmark and operational fallback. AQL bounds local transmit queues; it does not grant CPE uplink slots.

Make shaping symmetric between comparison arms: POP-side shaping before downlink RF transmission, and Linux traffic endpoints or capable customer routers behind **each participating CPE** for uplink shaping. Dedicated extra boxes are unnecessary if those endpoints already exist; deployment costs must still be counted. POP-side upload policing cannot substitute for shaping before RF contention. [CAKE research](https://arxiv.org/abs/1804.07617)

Convert whole cells during scheduled maintenance blocks. Start with one transmitting AP; qualify simultaneous two-AP operation separately. Use repeated within-firmware A/A runs and fewer, fully recorded whole-cell crossovers. Without crossover, hardware/site differences remain confounders.

**Prioritized Action Items:**

| Priority | Build / action | Rationale |
|---|---|---|
| **P0** | Verify all 22 board identities, exact image support, partition protection, backups, physical recovery and health checks. Resolve LAP-GPS versus LAP-120 before selecting images. | Prevent unsafe conversion and invalid hardware assumptions. |
| **P0** | Reproducible runner: pinned builds/configurations, raw telemetry, offered-load traces, A/A calibration, randomized workload order, repeated measurements and confidence intervals. | Establish trustworthy experimental evidence. |
| **P0** | Stock baseline, then OpenWrt baseline: 1→10→20 CPEs where association capacity permits; hidden/exposed nodes, mixed MCS, overload, all three traffic directions. Measure per-CPE goodput, p95/p99 latency, loss, fairness, CPU and resets. | Expose contention and stability limits before optimization. |
| **P1** | One-factor experiments: verified AQL/TXQ behavior, symmetric pacing, upstream versus CT, rate masks, RTS/CTS and aggregation controls. Validate telemetry freshness. | Attribute gains to demonstrated hooks; ath10k documents TX-rate reporting limitations. [Driver documentation](https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k.html) |
| **P2** | Spectral history, channel planning and bounded automated search with immutable acceptance gates. | Automate only after measurement reliability and useful controls are established. |

**Rejected Ideas / Non-Goals:** No PS-Poll/U-APSD “uplink TDMA,” assumed dual-image rollback, per-packet host rate steering, immediate custom MAC, or deep-learning controller. Defer MAC work until timing, queue ownership and synchronization gates pass. Short indoor or attenuated links do not prove long-distance performance. Reject gains that violate preregistered latency, stability or fairness limits.

**Final Confidence:** 90% in this roadmap; comparative performance remains unmeasured.

---

### Gemini (Round 3)
**Consensus Items:**
1. The AR9342 MIPS CPU cannot run CAKE shaping at line rate.
2. QCA9880 firmware controls rate selection; host-side optimization is limited to MCS/rate clamping.
3. AQL manages AP bufferbloat but does not schedule uplink RF medium access.
4. Saturated hidden-node uplink is the critical failure mode for CSMA.
5. A stock airOS TDMA baseline is mandatory for comparison.

**Final Architecture Compromise:**
To reconcile OpenWrt CSMA with airOS TDMA without CPU exhaustion:
1. **AP Downlink:** The OpenWrt AP runs `ath10k` with AQL and `fq_codel`. Heavy CAKE shaping is offloaded to an external x86/ARM gateway upstream of the AP.
2. **CPE Uplink:** CPEs run lightweight egress shaping (TBF or basic HTB) to limit uplink bufferbloat, combined with aggressive hardware RTS/CTS thresholds to mitigate hidden-node collisions.
3. **Comparison:** This optimized OpenWrt hybrid stack is benchmarked directly against stock airOS TDMA.

**Prioritized Action Items:**

| Priority | Action Item | Rationale |
| :--- | :--- | :--- |
| **P0** | **Recovery & Baselines** | Document TFTP/serial recovery for AR9342. Measure stock airOS TDMA vs. unoptimized OpenWrt CSMA under isolated downlink, uplink, and bidirectional saturated loads. |
| **P1** | **Hybrid CSMA Stack** | Deploy the external x86 CAKE gateway. Configure AP AQL and CPE-side egress shaping + hardware RTS/CTS. |
| **P2** | **Automated Testing** | Implement automated channel/role-swap orchestration to isolate adjacent-channel leakage and co-channel interference. |

**Rejected Ideas / Non-Goals:**
*   *U-APSD / PS-Poll "Soft-Poll" Scheduling:* Rejected. Station firmware latency variability and frame-exchange overhead exacerbate airtime starvation.
*   *On-box CAKE on MIPS 74Kc:* Rejected due to CPU starvation.
*   *Custom Host-Driven Rate Control:* Rejected; ath10k firmware rate selection cannot be bypassed per-packet.

**Final Confidence:** 95%
