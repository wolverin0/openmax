# Executive Summary
This dossier investigates outer-loop contextual rate-mask bounding, multi-armed bandits, and rate mask contextual translation (ratemask-CT) in 802.11ac outdoor stationary PtMP links. Special attention is given to how the host can eliminate high-order MCS probing without affecting on-chip rate microcode.

# Exact Technical Mechanisms & Claims
1. **Rate adaptation in 802.11 WLANs**:
   - **Claim**: Rate adaptation in 802.11 WLANs has received a lot of attention from the research community, with most proposals aiming at maximizing throughput based on network conditions.
   - **Classification**: CONFIRMED (Subsystem: MAC80211)
   - **Spans**: \[0: 180\]  
   - **Evidence**: Rate adaptation mechanisms aim to maximize throughput.

2. **Adaptive Resetting Bandit Algorithm**:
   - **Claim**: This paper proposes the adaptive resetting bandit (ADR-bandit), leveraging adaptive windowing techniques from data stream literature.
   - **Classification**: INFERRED (Subsystem: GATEWAY SHAPER)
   - **Spans**: \[0: 166\] 
   - **Evidence**: Multi-armed bandit algorithms are relevant for rate adaptation.

3. **Nonstationary Multi-Armed Bandit Problems**:
   - **Claim**: We consider nonstationary multi-armed bandit problems where the model parameters of the arms change over time.
   - **Classification**: INFERRED (Subsystem: GATEWAY SHAPER)
   - **Spans**: \[0: 110\]  
   - **Evidence**: Contextual bandit approaches can adapt to changing network conditions.

4. **Impact of External Interference**:
   - **Claim**: A Wi-Fi transmitter (TX) is selected to avoid beam angles toward victim radar; this interaction must be thoroughly studied.
   - **Classification**: UNKNOWN (Subsystem: MAC80211)
   - **Spans**: (No specific spans identified)
   - **Evidence**: Rate adaptation must consider external interference from other systems.

# Epistemic Evaluation Table
| Claim Description                                                  | Classification  | Subsystem          |
|-------------------------------------------------------------------|------------------|--------------------|
| Rate adaptation in 802.11 WLANs aims at maximizing throughput.   | CONFIRMED      | MAC80211           |
| Adaptive resetting bandit (ADR-bandit) for rate adaptation.      | INFERRED       | GATEWAY SHAPER     |
| Nonstationary bandit problems adapt to change over time.         | INFERRED       | GATEWAY SHAPER     |
| Selecting TX to avoid radar requires thorough study.              | UNKNOWN        | MAC80211           |

# Control Boundary Analysis
**Host-Owned vs Firmware-Owned**:
- The host can dictate parameters for rate adaptation but must do so without interference with firmware's on-chip rate microcode.
- Recommendations suggest adopting adaptive bandit algorithms while maintaining firmware integrity, ensuring seamless operation under external factors.

# Concrete Proposed Experiments
1. **Evaluation of Rate-Mask Techniques**: Test high-order MCS probing elimination techniques on multiple PtMP links while monitoring for any firmware discrepancies.  
2. **External Interference Analysis**: Simulate varying degrees of external interference and assess rate adaptation's robustness under such conditions.  
3. **Bandit Algorithms Implementation**: Deploy ADR-bandit algorithms in real-time rate adaptation scenarios and measure throughput compared to traditional mechanisms.