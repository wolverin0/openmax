# Round 2 - Claude

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
