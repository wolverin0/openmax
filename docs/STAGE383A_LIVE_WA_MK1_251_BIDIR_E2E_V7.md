<!-- doc-head: STAGE383A_LIVE_WA_MK1_251_BIDIR_E2E_V7.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 383A — Live End-to-End `CPE .250 -> AP .20 -> Boca 7 MK1-251` Bidirectional Stress Validation (`S383A-E2E-R3`)

## 1. Executive Summary (`CONFIRMED`)
- **Stage ID**: `Stage 383A` (`S383A-E2E-R3`)
- **End-to-End Topology**: `CPE 198.18.0.145` $\xrightarrow{\text{5220 MHz VHT40}}$ `AP 198.18.0.144` $\xrightarrow{\text{ar934x GMAC0 eth0}}$ `MikroTik Switch Boca 7` $\xrightarrow{\text{100FDX}}$ `MK1-251 (198.18.0.146)`.
- **Traffic Profile**: Simultaneous 4-stream TCP Downlink + 4-stream TCP Uplink + Gaming UDP (`250 pps` `EF`) + VoIP UDP (`50 pps` `EF`) + dual ICMP probes (`CPE .250 -> AP .20` wireless segment and `CPE .250 -> MK1-251 .251` full wireless-plus-wired switch path).
- **Primary Artifact**: [`artifacts/autoresearch/stage383a_live_wa_mk1_251_bidir_e2e_v7.json`](<repo>/artifacts/autoresearch/stage383a_live_wa_mk1_251_bidir_e2e_v7.json)

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` End-to-End Comparison

| Metric | `Arm A`: Stock `OpenWrt 24.10.4` (`A1`, `A2`) | `Arm B`: Universal `WA` Champion `v7` (`B1`, `B2`) | Improvement (`Arm B` vs `Arm A`) |
| :--- | :---: | :---: | :---: |
| **Mean Total Goodput (`Mbps`)** | `43.967 Mbps` (`43.829`, `44.106`) | **`54.623 Mbps`** (`51.370`, **`57.876`**) | **`+24.24%` (`+10.656 Mbps`)** |
| **Wireless Hop `RF_p50` (`CPE .250 -> AP .20`)** | `67.216 ms` (`69.439`, `64.994`) | **`15.007 ms`** (`15.274`, `14.741`) | **`-77.67%` (`-52.209 ms`)** |
| **Wireless Hop `RF_p95` (`CPE .250 -> AP .20`)** | `157.589 ms` (`152.976`, `162.202`) | **`70.305 ms`** (`59.589`, `81.021`) | **`-55.39%` (`-87.284 ms`)** |
| **End-to-End `MK1_p50` (`CPE .250 -> MK1-251`)** | `88.574 ms` (`83.077`, `94.072`) | **`8.987 ms`** (**`7.357`**, `10.617`) | **`-89.85%` (`-79.587 ms`)** |
| **End-to-End `MK1_p95` (`CPE .250 -> MK1-251`)** | `169.365 ms` (`166.921`, `171.810`) | **`42.735 ms`** (**`27.515`**, `57.955`) | **`-74.77%` (`-126.630 ms`)** |
| **End-to-End `MK1_p99` (`CPE .250 -> MK1-251`)** | `189.035 ms` (`174.160`, `203.910`) | **`49.687 ms`** (**`27.798`**, `71.576`) | **`-73.72%` (`-139.348 ms`)** |
| **Pareto Composite Score** | `18.305` | **`198.338`** | **`+983.52%` (`PROMOTE_ARM_B`)** |

## 3. Attribution Across Wireless & Wired Segments (`CONFIRMED`)
- **Attribution**: `Linux` (`sch_fq_codel` `limit 512 quantum 300 target 3ms interval 40ms ecn`, `bql.max_limit=24576`, `gro_normal_batch=16`, `tcp_autocorking=0`) + `mac80211` (`aql_threshold=4000`, `aql_txq_limit=3000/4000`, `rts off`) + `ath10k` (`htt_max_amsdu_ampdu='2 64'`).
- Eliminating both `mac80211` AQL queueing delay and `eth0` GMAC0 descriptor bloat reduces end-to-end `CPE .250 -> Boca 7 MK1-251` median latency under bidirectional saturation from **`88.574 ms` to `8.987 ms` (`-89.85%`)** while simultaneously lifting bidirectional goodput by **`+24.24%` (`43.967 -> 54.623 Mbps`)**.
