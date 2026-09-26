# Round 1 - Codex

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
