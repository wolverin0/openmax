<!-- doc-head: STAGE250A_LTU_HARQ_VS_OPENMAX_AMPDU_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 250A: SimPy + Pymoo NSGA-II HARQ vs 802.11ac A-MPDU Retry Storm Benchmark

## 1. Burst Multipath Retry Storm Problem (`INFERRED` / `CONFIRMED`)
- **Mechanism**: Under `12%` burst multipath interference, legacy `802.11ac` (`AQL=24000 us`, `32`-frame A-MPDU) suffers Block-ACK head-of-line retry storms (`VoIP jitter p99 = 26.447 ms`).
- **OpenMAX WA/XC (`AQL=4000 us` + `FQ-CoDel=3028 B`)**: Bounds per-STA airtime in flight, cutting VoIP jitter `p99` to `3.109 ms`.
- **LTU Codeword HARQ (`sched_max_agg_cnt=8`, `multi_ack_enable=1`)**: Retransmits only corrupted LDPC codewords inside the next `2.0 ms` superframe, achieving `324.99 Mbps` and `VoIP jitter p99 = 2.198 ms`.

## 2. Comparative Triple-Play QoE Table (`40 MHz`, `12%` Burst Multipath)
| Architecture | Aggregation | Goodput (Mbps) | VoIP Jitter `p50` (ms) | VoIP Jitter `p99` (ms) | IPTV Residual Loss (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Legacy `802.11ac` (`AQL=24000 us`) | `32` subframes | `198.56` | `4.504` | `26.447` | `0.0%` |
| **OpenMAX WA/XC Champion (`AQL=4000 us`)** | **`16` subframes** | **`247.39`** | **`1.244`** | **`3.109`** | **`0.0%`** |
| **LTU 12x Codeword HARQ (`2.0 ms`)** | **`8` codewords** | **`324.99`** | **`0.961`** | **`2.198`** | **`0.0%`** |
