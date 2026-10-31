<!-- doc-head: STAGE167A_LIVE_WA_ROUND19_21_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 167A — Live `WA` (`QCA9882` + `AR9342`) Rounds 19–21 Autoresearch (`VHT40` Synchronous CSA Probe, Stock vs `18`-Round Champion `v2`, Wide-Channel AQL & TCP Buffer Ceiling)

## 1. Executive Summary (`CONFIRMED`)
- **Stage ID**: `T-S167A-LIVE-WA-QCA9882-ROUND19-21-CSA-AQL-TCPMEM-AUTORESEARCH`
- **Hardware Under Test (`CONFIRMED`)**:
  - **AP (`.20`)**: `LAP-120` / `WA` (`QCA9882` + `AR9342` `535 MHz`, OpenWrt `24.10.4` `r28959-29397011cc`, `phy0-ap0` + `phy0-ap0.sta1`, `5180 MHz`).
  - **CPE (`.250` / `198.18.0.67`)**: `NanoStation 5AC loco` (`WA`, `QCA9882` + `AR9342`, OpenWrt `24.10.4` `r28959-29397011cc`, `phy0-sta0`, `4addr=1`).
- **Artifacts**:
  - [`artifacts/autoresearch/stage167a_live_wa_round19_21_autoresearch.json`](../artifacts/autoresearch/stage167a_live_wa_round19_21_autoresearch.json)
  - [`tools/benchmarks/run_stage167a_to_169a_wa_megamission.py`](../tools/benchmarks/run_stage167a_to_169a_wa_megamission.py)

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Results (`R19..R21`, `12` Live Windows)

| Round | Hypothesis | Arm A (Baseline) | Arm B (Candidate) | Goodput (`A` $\rightarrow$ `B`) | `p50` RTT (`A` $\rightarrow$ `B`) | `p95` RTT (`A` $\rightarrow$ `B`) | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`S167A-R19`** | Synchronous CSA Probe & Full Head-to-Head: Stock OpenWrt Baseline vs Cumulative `18`-Round `WA` Champion `v2` | Stock OpenWrt (`AQL=5000/12000`, `threshold=24000`, `fq_quantum=300`, `rps=0`, `distance=1000m`) | **Cumulative `18`-Round `WA` Champion `v2`** (`AQL=1500/3000`, `threshold=4000`, `fq_quantum=3028/1514`, `distance=300m`, `rps=1`, `flow_offload=1`) | `47.373` $\rightarrow$ **`59.643 Mbps` (`+25.90%`, `59.677 Mbps` in `B1`)** | `65.779` $\rightarrow$ **`40.537 ms` (`-38.37%`, `38.150 ms` in `B1`)** | `145.089` $\rightarrow$ **`78.728 ms` (`-45.74%`, `70.351 ms` in `B1`)** | **`PROMOTE_ARM_B`** |
| **`S167A-R20`** | Wide-Channel `ath10k` per-AC `aql_txq_limit` Scaling under Triple-Play | **`BE=4000/4000 us`, `aql_threshold=4000 us`** | `BE=6000/6000 us`, `aql_threshold=6000 us` | **`56.935 Mbps` (`58.351 Mbps` in `A1`)** vs `54.727 Mbps` | **`44.652 ms` (`41.115 ms` in `A2`)** vs `61.599 ms` | **`98.474 ms` (`82.678 ms` in `A2`)** vs `96.597 ms` | **`RETAIN_ARM_A`** (`4000/4000` wins for `VHT40`) |
| **`S167A-R21`** | `net.ipv4.tcp_rmem`/`wmem` & `net.core.optmem_max` under `64 MB` `WA` RAM Budget (`vm.min_free_kbytes=4096`) | **`tcp_rmem='4096 87380 2097152'`, `tcp_wmem='4096 65536 2097152'`, `optmem_max=20480`** | `tcp_rmem='4096 131072 3145728'`, `tcp_wmem='4096 131072 3145728'`, `optmem_max=65536` | **`60.149 Mbps` (`60.323` in `A1`, `59.975` in `A2`)** vs `57.459 Mbps` (`61.121` in `B1`) | **`37.751 ms` (`36.263 ms` in `A2`)** vs `50.140 ms` | **`80.329 ms`** vs `110.903 ms` | **`RETAIN_ARM_A`** (`2 MB` TCP ceiling prevents socket bloat) |

---

## 3. Root-Cause Attribution & Key Discoveries (`CONFIRMED`)
1. **`FMX-DISC-35` — Synchronous `VHT40` `switch_chan` vs STA `uci htmode=VHT20` (`hostapd` + `wpa_supplicant` + `netifd`)**:
   - Issuing `ubus call hostapd.phy0-ap0 switch_chan '{"freq":5180,"bcn_count":5,"center_freq1":5190,"bandwidth":40,"sec_channel_offset":1,"ht":true,"vht":true}'` on `.20` (`phy0-ap0`) synchronously widened the AP to **`channel 36 (5180 MHz), width: 40 MHz, center1: 5190 MHz`** without restarting `hostapd`.
   - However, when an OpenWrt STA (`loco`) has `option htmode 'VHT20'` in `/etc/config/wireless`, `netifd` restricts `wpa_supplicant` to `20 MHz` (`disable_ht40=1`). For zero-drop dynamic `20 <-> 40 MHz` CSA, the STA must be configured with `option htmode 'VHT40'` (which associates to both `20 MHz` and `40 MHz` APs). Also, issuing a second `switch_chan` before the first 5-beacon CSA finishes triggers `hostapd: Cannot set beacons during CSA period`.
2. **`S167A-R19` (`+25.90%` Goodput & `-45.74%` `p95` RTT over Stock OpenWrt, `Linux` + `mac80211` + `ath10k`)**:
   - In direct counterbalanced head-to-head comparison, the Cumulative `18`-Round `WA` Champion `v2` (`Arm B`) reached **`59.643 Mbps` mean goodput** vs `47.373 Mbps` on Stock OpenWrt (`+12.27 Mbps`, **`+25.90%`**), cut `p50` RTT by **`-38.37%`** (`65.779 -> 40.537 ms`), and cut `p95` RTT by **`-45.74%`** (`145.089 -> 78.728 ms`).
3. **`S167A-R20` & `S167A-R21` (`4000/4000 us` Wide-Channel AQL & `2 MB` TCP Buffer Ceiling)**:
   - For wider channels (`VHT40`), `BE=4000/4000 us` (`aql_threshold=4000 us`) beat `6000/6000 us` by `+2.21 Mbps` and `-16.95 ms` `p50` RTT. In `R21`, keeping `tcp_rmem`/`tcp_wmem` max at `2097152` (`2 MB`) achieved **`60.149 Mbps` mean goodput** and **`37.751 ms` mean `p50` RTT** (`36.263 ms` in `A2`) with `14.09 MB` `MemAvailable`.
