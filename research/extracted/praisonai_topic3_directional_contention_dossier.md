### Executive Summary
The investigation into uplink contention mitigation for directional PtMP (Point-to-Multipoint) systems highlighted critical issues around the hidden terminal problem and proposed solutions. Key findings reveal that the hidden terminal problem poses significant challenges in wireless networks and that current methods, such as directional RTS/CTS, do not fully address these issues. Opportunities for deeper exploration include assessing dynamic CCA, hardware RTS/CTS, and airtime-deficit scheduling under conditions of high inter-CPE isolation.

### Exact Technical Mechanisms & Claims
1. **Hidden Terminal Problem:**
   - **Claim:** "Hidden terminal problem is notorious in wireless networks."
   - **Evidence:** "Due to the irregular topology and the limited communication range of terminals, a practical challenge for AutoCA is the hidden terminal problem, which is notorious in wireless networks."
   - **Classification:** CONFIRMED (Subsystem: MAC80211)

2. **Directional RTS/CTS Ineffectiveness:**
   - **Claim:** "Directional RTS/CTS mechanism hardly resolves hidden terminal problem."
   - **Evidence:** "The directional RTS/CTS mechanism of mm-wave Wi-Fi hardly resolves the hidden terminal problem perfectly."
   - **Classification:** CONFIRMED (Subsystem: MAC80211)

### Epistemic Evaluation Table
| Claim                                                   | Evidence                                                                                                                | Classification | Subsystem        |
|---------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|----------------|------------------|
| Hidden terminal problem is notorious in wireless networks.| Due to the irregular topology and the limited communication range of terminals, a practical challenge…                  | CONFIRMED      | MAC80211         |
| Directional RTS/CTS mechanism hardly resolves hidden terminal problem. | The directional RTS/CTS mechanism of mm-wave Wi-Fi hardly resolves the hidden terminal problem perfectly.             | CONFIRMED      | MAC80211         |

### Control Boundary Analysis
- **Host-Owned:** CPE configurations, RSSI management, and MAC behaviors.
- **Firmware-Owned:** RTS/CTS handling, CCA mechanisms, and dynamic spectrum access methodologies.

### Concrete Proposed Experiments
1. **Experiment to Quantify Dynamic CCA Efficacy:**
   - **Hypothesis:** Dynamic CCA improves uplink contention mitigation under high inter-CPE isolation.
   - **Hardware:** Ubiquiti LiteAP GPS / LAP-GPS APs, LiteBeam 5AC Gen2 CPEs.
   - **Metrics:** Aggregate goodput, p95/p99 latency, airtime distribution.

2. **Selective Hardware RTS/CTS Implementation Evaluation:**
   - **Hypothesis:** Implementing selective RTS/CTS reduces collision rates and increases throughput.
   - **Hardware:** Same as above.
   - **Metrics:** Collision rate, throughput variance.

3. **Airtime-Deficit Scheduling Analysis:**
   - **Hypothesis:** Airtime-deficit scheduling provides more equitable resource distribution among CPEs.
   - **Hardware:** Deploy in conditions mirroring real-world deployment scenarios.
   - **Metrics:** Jain fairness index, per-CPE throughput.