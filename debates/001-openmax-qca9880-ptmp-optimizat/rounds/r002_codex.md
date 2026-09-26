# Round 2 - Codex

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
