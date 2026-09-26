# Round 3 - Codex

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
