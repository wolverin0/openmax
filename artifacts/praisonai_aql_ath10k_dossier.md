# Research Dossier on Airtime Queue Limits (AQL) and Controlled TCP Small Queues (CoTSQ)

## Local FuturaMAX Seeds
- AQL is integrated with mac80211 TXQ and airtime scheduling.
- Related work includes FQ-CoDel and CAKE implementations.
- Significant MAC behavior is firmware offloaded on QCA988x platforms.

## Key Findings from arXiv Literature
1. **Data Throughput Influences**:  
   - **Claim**: Data rates, over the Wi-Fi interface, are influenced by the media access protocol, which loses throughput due to delays and unintended collisions when many users are active.  
   - **Evaluation**: CONFIRMED  
   - **Control Boundary**: [LINUX NETWORKING | MAC80211 | ATH10K DRIVER | QCA988X FIRMWARE | PROPRIETARY AIRMAX]  

2. **Bufferbloat Issue**:  
   - **Claim**: High peak throughputs and intermittency can cause significant bufferbloat.  
   - **Evaluation**: CONFIRMED  
   - **Control Boundary**: [LINUX NETWORKING | MAC80211 | ATH10K DRIVER | QCA988X FIRMWARE | PROPRIETARY AIRMAX]  

3. **Low Latency Requirements**:  
   - **Claim**: Heterogeneous wireless networks evolved to satisfy low latency and high throughput application needs.  
   - **Evaluation**: CONFIRMED  
   - **Control Boundary**: [LINUX NETWORKING | MAC80211 | ATH10K DRIVER | QCA988X FIRMWARE | PROPRIETARY AIRMAX]  

## Conclusion and Next Steps
A comprehensive examination of AQL and CoTSQ in conjunction with ath10k reveals validated claims and considerations for improving Wi-Fi performance in outdoor PtMP environments using the Qualcomm QCA9880 hardware.

### Next Steps for FuturaMAX Testbed Experiments:
1. Validate claims through empirical measurements on QCA9880.  
2. Explore enhancements using FQ-CoDel and CAKE in real-world scenarios.  
3. Conduct further investigations into dynamic queueing strategies to mitigate bufferbloat effects.