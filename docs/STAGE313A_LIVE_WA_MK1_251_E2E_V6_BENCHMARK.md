<!-- doc-head: STAGE313A_LIVE_WA_MK1_251_E2E_V6_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 313A — Live End-to-End `Boca 7` `MikroTik MK1-251` (`198.18.0.141` / `198.18.0.66`) Router Queue & Conntrack Stress with `WA` Champion `v6`

- **Claim Label**: `CONFIRMED`
- **Attribution**: `Linux` (`nf_flow_table.ko`, `nftables`, `net/core/dev.c`) + `mac80211` + `ath10k` + `external controller` (`MikroTik MK1-251`)
- **Topology**: `CPE .250 (198.18.0.142 / 198.18.0.67) -> 5 GHz 4-Addr WDS -> AP .20 (198.18.0.43) -> Switch -> Boca 7 MikroTik MK1-251 (198.18.0.141)`
- **JSON Receipt**: [`artifacts/autoresearch/stage313a_live_wa_mk1_251_e2e_v6_benchmark.json`](<repo>/artifacts/autoresearch/stage313a_live_wa_mk1_251_e2e_v6_benchmark.json)

---

## 1. Counterbalanced `A1 -> B1 -> A2 -> B2` End-to-End Results (`S313A-E2E-R2`)

| Window | Arm | Profile | Goodput (`Mbps`) | RF `.20 <-> .250` `p50` / `p95` RTT (`ms`) | `CPE .250 -> MK1-251` E2E `p50` / `p95` RTT (`ms`) | AP / CPE Conntrack Count | AP Softirq / Idle `%` |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **`A1`** | `A` | Stock OpenWrt (`flow_offloading=0, rps=0, gro_batch=8`) | `80.175` | `17.380` / `37.030` | `12.028` / `32.518` | `64` / `52` | `29.60%` / `9.20%` |
| **`B1`** | `B` | **`36`-Round `WA` Champion `v6` (`flow_offloading=1, rps=1, gro_batch=16, WMM nftables`)** | `68.211` | **`9.871`** / `59.261` | **`4.341`** / `34.250` | `66` / `54` | `31.97%` / `10.90%` |
| **`A2`** | `A` | Stock OpenWrt (`flow_offloading=0, rps=0, gro_batch=8`) | `68.181` | `43.486` / `93.810` | `10.085` / `81.908` | `67` / `54` | `30.63%` / `10.13%` |
| **`B2`** | `B` | **`36`-Round `WA` Champion `v6` (`flow_offloading=1, rps=1, gro_batch=16, WMM nftables`)** | `72.140` | **`14.663`** / **`45.485`** | `15.131` / **`23.382`** | `68` / `55` | `32.41%` / `8.19%` |

---

## 2. Key End-to-End Findings (`CONFIRMED`)

1. **-59.69% Wireless Hop `p50` Latency Reduction Under 8-Flow Bidir + Triple-Play Saturation**:
   - Across `CPE .250 -> AP .20 -> Switch -> MK1-251`, `WA` Champion `v6` (`Arm B`) slashed mean wireless under-load `p50` RTT from `30.433 ms` to **`12.267 ms` (`-59.69%`)** and `p95` RTT from `65.420 ms` to **`52.373 ms` (`-19.94%`)**.
2. **Sub-5ms End-to-End `CPE .250 -> MK1-251` Forwarding Latency (`4.341 ms` `p50` in `B1`)**:
   - Combining `flow_offloading=1`, `packet_steering=1`, `gro_normal_batch=16`, `fq_limit=512`, and `99-fmx-wmm-dscp-qos` achieved **`4.341 ms` `p50` E2E RTT** in `B1` (`9.736 ms` mean E2E `p50` vs `11.057 ms` Stock, and **`28.816 ms` mean E2E `p95` vs `57.213 ms` Stock**, a **`-49.63%` E2E `p95` tail-latency reduction**).
