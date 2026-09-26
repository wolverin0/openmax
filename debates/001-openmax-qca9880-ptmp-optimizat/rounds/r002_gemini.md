# Round 2 - Gemini

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
