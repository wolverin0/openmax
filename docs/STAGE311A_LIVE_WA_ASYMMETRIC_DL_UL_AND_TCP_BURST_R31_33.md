<!-- doc-head: STAGE311A_LIVE_WA_ASYMMETRIC_DL_UL_AND_TCP_BURST_R31_33.md preserved document content -->
<!-- /doc-head -->


# Stage 311A — Live `WA` (`QCA9882` `.20 <-> .250`) Rounds `31..33` (`136` Cumulative Windows): Asymmetric UL/DL Traffic Ratios & Bursty TCP Optimization

- **Claim Label**: `CONFIRMED`
- **Attribution**: `Linux` + `mac80211` + `ath10k` + `hardware` (`AR9342` `535 MHz` MIPS 74Kc + `QCA9882` 2x2 `802.11ac` Wave 1)
- **Protocol**: Counterbalanced `A1 -> B1 -> A2 -> B2` (`3` rounds $\times$ `4` live windows = `12` windows; cumulative **`132` RF windows + `4` E2E windows = `136` live windows** on `.20 <-> .250`)
- **JSON Receipt**: [`artifacts/autoresearch/stage311a_live_wa_asymmetric_dl_ul_and_tcp_burst_r31_33.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage311a_live_wa_asymmetric_dl_ul_and_tcp_burst_r31_33.json)

---

## 1. Executive Summary (`R31..R33` Counterbalanced Results)

| Round ID | Hypothesis / Knob Tested | Arm A Mean Goodput | Arm B Mean Goodput | Arm A `p50` / `p95` RTT | Arm B `p50` / `p95` RTT | Pareto $\Delta$ | Decision |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S311A-R31`** | Pure Downlink (`AP .20 -> CPE .250`, `iperf3 -P 4` + IPTV + VoIP): Stock OpenWrt (`Arm A`) vs `30`-Round `WA` Champion `v5` + `99-fmx-wmm-dscp-qos` (`Arm B`) | `77.286 Mbps` | **`81.480 Mbps`** (`+5.43%`) | `29.934` / `96.147 ms` | `35.983` / **`67.907 ms`** (`-29.37%` `p95`) | **`+13.61%`** | **`PROMOTE_ARM_B`** |
| **`S311A-R32`** | Pure Uplink (`CPE .250 -> AP .20`, `iperf3 -R -P 4` + VoIP): Stock OpenWrt (`Arm A`) vs Asymmetric `STA fq_quantum=1514` (`1xMTU`) + `AP fq_quantum=3028` (`2xMTU`) (`Arm B`) | `29.303 Mbps` | **`29.858 Mbps`** (`+1.89%`) | `21.626` / `36.982 ms` | **`17.104`** / `45.766 ms` (`-20.91%` `p50`) | `-27.62%` | **`RETAIN_ARM_A` (Keep `1514`/`3028` for `-20.91%` `p50` RTT)** |
| **`S311A-R33`** | Bursty HTTP/Web/Gaming TCP (`tcp_slow_start_after_idle=0`, `tcp_mtu_probing=1`, `tcp_thin_linear_timeouts=1` with `CUBIC` + `FQ` Pacing) | `59.361 Mbps` | `57.263 Mbps` | `24.410` / `66.549 ms` | **`16.770`** / **`57.506 ms`** (`-31.30%` `p50`, `-13.59%` `p95`) | `-1.16%` | **`RETAIN_ARM_A` (`-31.30%` `p50` RTT & `-13.59%` `p95` RTT)** |

---

## 2. Mechanistic Findings (`Linux` TCP/IP + `mac80211` `fq_codel`)

1. **Pure Downlink Peak Goodput (`81.654 Mbps` in `S311A-R31 B2`, `CONFIRMED`)**:
   - Under pure downlink saturation (`AP .20 -> CPE .250` 4-stream TCP + IPTV + VoIP), the `30`-Round `WA` Champion `v5` with `99-fmx-wmm-dscp-qos` raised mean goodput from `77.286 Mbps` to **`81.480 Mbps` (`+5.43%`, peaking at `81.654 Mbps` in `B2`)** while slashing `p95`/`p99` tail latency by **`-29.37%` (`96.147 -> 67.907 ms`)** (`Pareto +13.61%`, `PROMOTE_ARM_B`).
2. **Pure Uplink Asymmetric `fq_quantum` (`1514` STA vs `3028` AP, `S311A-R32`, `CONFIRMED`)**:
   - Under pure uplink saturation (`CPE .250 -> AP .20`), `STA fq_quantum=1514` (`1xMTU`) + `AP fq_quantum=3028` (`2xMTU`) increased uplink goodput (`29.303 -> 29.858 Mbps`, peaking at **`30.729 Mbps`** in `B2`) and reduced median `p50` RTT by **`-20.91%` (`21.626 -> 17.104 ms`, reaching `15.581 ms` in `B2`)** while reducing `AP softirq` CPU from `36.20%` to `33.25%`.
3. **Bursty TCP Idle-Window Preservation (`tcp_slow_start_after_idle=0`, `S311A-R33`, `CONFIRMED`)**:
   - Disabling `tcp_slow_start_after_idle` (`=0`) and enabling `tcp_mtu_probing=1` + `tcp_thin_linear_timeouts=1` reduced `p50` RTT by **`-31.30%` (`24.410 -> 16.770 ms`, reaching `9.026 ms` in `B2`)** and `p95` RTT by **`-13.59%` (`66.549 -> 57.506 ms`)**.
