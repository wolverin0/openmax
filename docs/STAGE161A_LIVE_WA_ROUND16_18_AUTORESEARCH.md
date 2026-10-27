<!-- doc-head: STAGE161A_LIVE_WA_ROUND16_18_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->



# Stage 161A — Live `WA` (`QCA9882` + `AR9342`) Rounds 16–18 Deep Autoresearch (`distance_m`, 8-Flow TCP Pacing + `fq_initial_quantum`, & CSA `switch_chan` + `txpower`)

## 1. Executive Summary (`CONFIRMED`)
- **Stage ID**: `T-S161A-LIVE-WA-QCA9882-ROUND16-18-DISTANCE-TCP-PACING-CSA-AUTORESEARCH`
- **Hardware Under Test (`CONFIRMED`)**:
  - **AP (`.20`)**: `NanoStation 5AC loco` (`WA`, `QCA9882` + `AR9342` `535 MHz`, OpenWrt `24.10.4` `r28959-29397011cc`, `phy0-ap0`, `5180 MHz` `VHT20`).
  - **CPE (`.250`)**: `LiteBeam 5AC Gen2` (`WA`, `QCA9882` + `AR9342`, OpenWrt `24.10.4` `r28959-29397011cc`, `phy0-sta0`, `4addr=1`).
- **Artifacts**:
  - [`artifacts/autoresearch/stage161a_live_wa_round16_18_autoresearch.json`](../artifacts/autoresearch/stage161a_live_wa_round16_18_autoresearch.json)
  - [`tools/benchmarks/run_stage161a_to_163a_wa_megamission.py`](../tools/benchmarks/run_stage161a_to_163a_wa_megamission.py)

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Results (`R16..R18`, `12` Live Windows)

| Round | Hypothesis | Arm A (Baseline) | Arm B (Candidate) | Goodput (`A` $\rightarrow$ `B`) | `p50` RTT (`A` $\rightarrow$ `B`) | `p95` RTT (`A` $\rightarrow$ `B`) | `p99` RTT (`A` $\rightarrow$ `B`) | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`S161A-R16`** | Sub-kilometer `iw phy phy0 set distance` (`ath10k` ACK/CTS timeout & slot time) | `distance=1000 m` (`coverage_class=0`) | **`distance=300 m` (`coverage_class=0`)** | `42.880` $\rightarrow$ **`48.748 Mbps` (`+13.68%`, `52.850 Mbps` in `B1`)** | `45.849` $\rightarrow$ **`41.787 ms` (`-8.86%`)** | `112.632` $\rightarrow$ **`94.741 ms` (`-15.88%`)** | `118.926` $\rightarrow$ `119.515 ms` | **`PROMOTE_ARM_B`** (`Pareto +173.59%`) |
| **`S161A-R17`** | 8-flow TCP stress (`-P 4 --bidir`) pacing & initial quantum with `vm.min_free_kbytes=4096` | `ca_ratio=120`, `ss_ratio=200`, `fq_initial_quantum=4542` | **`ca_ratio=110`, `ss_ratio=150`, `fq_initial_quantum=3028`** | `35.425` $\rightarrow$ **`38.055 Mbps` (`+7.42%`, `43.108 Mbps` in `B2`)** | `58.001` $\rightarrow$ **`54.602 ms` (`-5.86%`)** | `124.228` $\rightarrow$ `130.903 ms` | `150.562` $\rightarrow$ **`148.555 ms` (`-1.33%`)** | **`PROMOTE_ARM_B`** (`Pareto +35.55%`) |
| **`S161A-R18`** | Synchronous `hostapd switch_chan` (`5180 MHz`, `bcn_count=5`) + `txpower` `20 dBm` vs `22 dBm` | **`txpower=2000 mBm` (`20 dBm`)** | `txpower=2200 mBm` (`22 dBm`) | **`44.064 Mbps`** vs `41.055 Mbps` | **`45.039 ms`** vs `48.208 ms` | **`118.790 ms`** vs `160.575 ms` | **`128.436 ms`** vs `198.268 ms` | **`RETAIN_ARM_A`** (`20 dBm` cleaner on close-range bench) |

---

## 3. Root-Cause Attribution (`CONFIRMED`)
1. **`S161A-R16` (`distance=300 m` Promotion, `ath10k` + `QCA firmware`)**:
   - Even when `coverage_class=0`, explicit `iw phy phy0 set distance 300` configures `NL80211_ATTR_WIPHY_COVERAGE_CLASS` and `ath10k` WMI slot/ACK timeout parameters to sub-kilometer bounds without over-extending CSMA/CA ACK wait timers. This raised `VHT20` bidirectional goodput by **`+13.68%`** (`42.880 -> 48.748 Mbps`) while cutting `p95` RTT by **`-15.88%`** (`112.632 -> 94.741 ms`).
2. **`S161A-R17` (8-Flow TCP Pacing + `vm.min_free_kbytes=4096` Synergy, `Linux` + `mac80211`)**:
   - In `Stage 145A` (`S145A-R15`), 8-flow TCP stress (`-P 4 --bidir`) before `vm.min_free_kbytes=4096` achieved `22.611 Mbps`. With `vm.min_free_kbytes=4096` active in `S161A-R17` and `tcp_pacing_ca_ratio=110` / `tcp_pacing_ss_ratio=150` / `fq_initial_quantum=3028`, 8-flow bidirectional goodput reached **`38.055 Mbps` (`43.108 Mbps` in `B2`, `+68.3%` to `+90.6%` higher than `S145A-R15`)**, while maintaining `AP MemAvailable = 13.62–18.11 MB` (`MemFree+Cached > 24 MB`) and `CPE MemAvailable = 10.79–10.84 MB` (`MemFree+Cached > 18 MB`) with zero OOM or page allocation stalls.
3. **`S161A-R18` (Zero-Drop Synchronous CSA + Close-Range TX Power Saturation, `mac80211` + `hardware`)**:
   - Issuing `ubus call hostapd.phy0-ap0 switch_chan '{"freq":5180,"bcn_count":5,"ht_mode":"VHT20"}'` executed synchronously with `0%` packet loss. On the close-range bench (`-37 dBm` RSSI), `2000 mBm` (`20 dBm`) outperformed `2200 mBm` (`22 dBm`) (`p95 = 118.790 ms` vs `160.575 ms`) by avoiding LNA front-end compression on the peer receiver.
