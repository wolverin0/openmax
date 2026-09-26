# Round 3 - Gemini

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
