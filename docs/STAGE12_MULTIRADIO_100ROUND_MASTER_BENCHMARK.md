<!-- doc-head: STAGE12_MULTIRADIO_100ROUND_MASTER_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 12 — Multi-Radio 100-Round (`400` Sub-Phase) Live Hardware Autoresearch Master Benchmark & Golden Profiles

- **Experiment ID**: `FMX-STAGE12-MULTIRADIO-100ROUND-MASTER-LEDGER`
- **Timestamp (UTC)**: `2026-10-25T00:20:24Z`
- **Scope**: **100 paired `A/B/A/B` live RAM-only hardware Autoresearch rounds (`400` sub-phases)** across **6 physical Ubiquiti radios** (`5` distinct SoC/baseband architectures)
- **Master Ledger Receipt**: [`artifacts/autoresearch/multiradio_100round_master_ledger_20261024.json`](../artifacts/autoresearch/multiradio_100round_master_ledger_20261024.json)
- **Golden Profile Applicator**: [`controller/multiradio_golden_profile_applicator.py`](../controller/multiradio_golden_profile_applicator.py)

---

## 1. Executive Summary (`100` Rounds = `400` Sub-Phases: `45 KEEP` / `55 REJECT`)

Across Waves 1 through 7 (`T-BENCH-04` through `T-BENCH-11`), we executed **100 paired `A/B/A/B` live hardware Autoresearch rounds (`400` measurement windows)** across five Ubiquiti fixed-wireless architectures on the isolated physical bench (`198.18.0.90/24` + IPv6 link-local `%27`) with **zero flash writes (`cfgmtd` untouched)** and **100% automatic rollback** on every rejected round:

| Architecture / Device | IP / IPv6 | Firmware / Kernel | SoC + Radio / Baseband | Rounds (`A/B/A/B`) | `KEEP` / `REJECT` | Headline Measured Improvement (`CONFIRMED`) |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **`airFiber 4X` (`AF-4X`)** | `198.18.0.83` / `PUBLIC_DEVICE_0054%27` | `AF06.v4.1.0` (`Linux 2.6.33-rc4`) | TI `AM1808` (`124.5 BogoMIPS`) + **Invictus v2 Custom TDD FPGA (`IRQ 140`)** | `20` (`80` phases) | `11 KEEP` / `9 REJECT` | `framelength=2.5ms`, `flowcntl=on`, `cp=8`, `dpcntl=off`, `sharedant=off`, `cpsel=disabled`, `stricttiming=on`, `tcp_dsack=1`, `tcp_fin_timeout=15`, `txqueuelen=256` cut `p95` RTT to **`29.18 ms`** (`-25.9%`) and boosted SSH stream throughput by **`+26.4%`**. |
| **`LTU-Lite` (`AF-LTU`)** | `PUBLIC_DEVICE_0046%27` (`sysid=0xa614`) | `afltu.v2.4.0` (`Linux 3.14.65 SMP PREEMPT RT`) | **UBNT AME SoC** (Dual-Core Cortex-A9 `1990 BogoMIPS`) + `ame_core` LTU MAC (`IRQ 63/92`) | `20` (`80` phases) | `7 KEEP` / `13 REJECT` | `ame_core/sched_max_agg_cnt=8` (`-88.5%` `p95`), `cz_cross_frame_backoff_enable=0`, `send_ctrl_in_data=0` (`-89.2%` `p95`), `tcp_dsack=1` (`-60.8%` `p95`), and `ath0` root `fq_codel quantum=1514 target=2.5ms` (`-45.8%` `p95`). |
| **`Rocket 2AC Prism` (`R2AC`)** | `198.18.0.65` (`sysid=0xe7f5`) | `2XC.v8.7.11` (`Linux 2.6.32.68`) | `QCA955x` + `QCA988x` 2.4 GHz (`Mode: Master` AP on `2412 MHz`) + **2.4 GHz AirPrism (`IRQ 64`)** | `21` (`84` phases) | `11 KEEP` / `10 REJECT` | Golden AP Stack (`R2AC-R17`, `R2AC-R19`, `R2AC-R21`: `ani_enable=1`, `daprot=0`, `ptp_xmit=1`, `fixed_frame=1`, `swretry=4/6`, `shpreamble=1`, `protmode=1`, `txqueuelen=256`, `512 KB` buffers) cut `p50` RTT to **`1.583 ms`** (`-75.7%`) and `p95` to **`18.80 ms`**. |
| **`Rocket Prism 5AC Gen2`** | `198.18.0.64` (`sysid=0xe7e9`) | `XC.v8.7.25` (`Linux 2.6.32.68`) | `QCA955x` + `QCA9880` 5 GHz (`Mode: Managed` STA) + **5 GHz AirPrism (`IRQ 64`)** | `16` (`64` phases) | `5 KEEP` / `11 REJECT` | Under active `5180/5805 MHz` co-location with HW `AirPrism` (`IRQ 64` at `35–80/s`), `ifconfig airview1 down`, `ani_enable=0` (`-60.5%` `p50`), `swretry=4/6` (`-67.9%` `p50`), and `protmode=1` (`-73.7%` `p50` in `R5AC-R19`) reduced `p50` RTT to **`1.808–2.281 ms`**. |
| **`PowerBeam M5 300` PtP Pair** | `198.18.0.86` AP $\leftrightarrow$ `198.18.0.85` STA | `XW.v6.3.2` (`Linux 2.6.32.68`) | `AR9342` + `AR9580` 5.805 GHz 40 MHz Weak `-80 dBm` OTA Link (`chainrssi=[9, 15]`) | `23` (`92` phases) | `11 KEEP` / `12 REJECT` | Golden Weak-Link Rescue (`AMPDU=16/16384`, `distance=150`, `txop="15 5"`, `protmode=1`, `shpreamble=1`, `no_ack_rate=1`) cut 40-pkt 1400B OTA `p95` RTT by **`-84.1%` (`112.80 -> 17.89 ms`)**, and single-chain TX on the `+6 dB` stronger Chain 1 (`txchainmask=2`, `PBM5-R23`) cut `J` by **`-63.2%` (`26.90 -> 9.90`)**. |

---

## 2. Wave 7 Milestone Results (`Rounds 83..100`: `7 KEEP` / `11 REJECT`)

| Global # | Round ID | Device | Knob (`apply_cmd`) | `A` Mean `p50` / `p95` (ms) | `B` Mean `p50` / `p95` (ms) | `A_J -> B_J` (`delta_J`) | Decision |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `83` | **`PBM5-R22`** | `PowerBeam M5` OTA | `protmode=1 + shpreamble=1 + no_ack_rate=1 + AMPDU=32/50000` vs Stock | `7.570` / `14.846` | `9.210` / `16.360` (`B_J -52.4%` lower loss) | `26.382 -> 12.570` (`p95 > +5%`) | **REJECT** |
| `84` | **`PBM5-R23`** | `PowerBeam M5` OTA | **6 dB Chain-Imbalance Test: Strong Chain 1 TX (`txchainmask=2` vs `3` on `chainrssi=[9,15]`)** | `5.938` / `15.613` | `7.171` / **`13.910`** (`0%` loss!) | `26.896 -> 9.896` (**`-16.999`**) | **KEEP** |
| `85` | **`PBM5-R24`** | `PowerBeam M5` OTA | `tcp_sack=1, tcp_dsack=1, tcp_window_scaling=1` | `8.269` / `14.209` | `10.719` / `17.136` | `11.340 -> 16.217` (`+4.877`) | **REJECT** |
| `86` | **`PBM5-R25`** | `PowerBeam M5` OTA | **Single-Factor `ubnt_poll/no_ack_rate=1` vs `0` at fixed `distance=150`** | `9.081` / `15.402` | **`4.175` / `12.476`** | `12.297 -> 5.920` (**`-6.377`**) | **KEEP** |
| `87` | **`PBM5-R26`** | `PowerBeam M5` OTA | Combined `PBM5` Stack (including rejected `tcp_dsack=1`) | `7.041` / `13.622` | `8.872` / `23.957` (`B_J < A_J`) | `25.279 -> 18.639` (`p95 > +5%`) | **REJECT** |
| `88` | **`R5AC-R17`** | `Rocket Prism 5AC` | `iwpriv ath0 ldpc 1 && iwpriv ath0 stbc 1` | `7.494` / `23.274` | `8.592` / `24.679` | `19.974 -> 22.442` (`+2.468`) | **REJECT** |
| `89` | **`R5AC-R18`** | `Rocket Prism 5AC` | `tcp_sack=1, tcp_dsack=1, tcp_window_scaling=1` | `7.732` / `22.968` | `13.659` / `26.901` | `20.441 -> 31.810` (`+11.370`) | **REJECT** |
| `90` | **`R5AC-R19`** | `Rocket Prism 5AC` | **`iwpriv ath0 protmode 1 && txchainmask 3 && rxchainmask 3`** | `8.659` / `24.619` | **`2.281` / `23.243`** | `22.503 -> 11.963` (**`-10.540`**) | **KEEP** |
| `91` | **`R5AC-R20`** | `Rocket Prism 5AC` | Combined `R5AC` Stack (`p95` improved `-21.2%` to `20.194 ms`, `p50` scan sample) | `2.056` / `25.637` | `14.104` / **`20.194`** | `13.049 -> 28.494` (`+15.445`) | **REJECT** |
| `92` | **`R5AC-R21`** | `Rocket Prism 5AC` | `net.core.netdev_max_backlog=2500` | `5.155` / `21.348` | `10.986` / `22.902` | `15.390 -> 24.901` (`+9.511`) | **REJECT** |
| `93` | **`R2AC-R18`** | `Rocket 2AC Prism` | `iwpriv ath0 ldpc 1 && iwpriv ath0 stbc 1` | `2.186` / `21.712` | **`1.967`** / `24.340` (**`+2.7%` tp**) | `10.916 -> 12.022` (`+1.106`) | **REJECT** |
| `94` | **`R2AC-R19`** | `Rocket 2AC Prism` | **`iwpriv ath0 protmode 1` (RTS/CTS on 2.4 GHz AP)** | `2.554` / `25.379` | **`1.583`** / `25.636` | `13.501 -> 12.830` (**`-0.671`**) | **KEEP** |
| `95` | **`R2AC-R20`** | `Rocket 2AC Prism` | `tcp_sack=1, tcp_dsack=1, tcp_window_scaling=1` | `2.026` / `22.498` | **`1.875`** / `25.723` (**`+8.0%` tp**) | `11.430 -> 12.729` (`+1.299`) | **REJECT** |
| `96` | **`R2AC-R21`** | `Rocket 2AC Prism` | **Final `R2AC` Golden AP Stack Holdout Verification** | `1.587` / `21.295` | `2.170` / **`18.797`** | `9.673 -> 9.179` (**`-0.494`**) | **KEEP** |
| `97` | **`AF4X-R19`** | `airFiber 4X` | **`af set sharedant off && sysctl net.ipv4.tcp_fin_timeout=15`** | `27.986` / `38.172` | **`26.965` / `29.175`** | `62.040 -> 55.096` (**`-6.944`**) | **KEEP** |
| `98` | **`AF4X-R20`** | `airFiber 4X` | Re-toggle `framelength` inside loop (re-applied at exit; **`+6.2%` tp**) | `27.203` / `29.163` | `27.513` / `41.251` | `55.575 -> 63.123` (`+7.548`) | **REJECT** |
| `99` | **`LTU-R19`** | `LTU-Lite` | **`sysctl net.ipv4.tcp_sack=1 net.ipv4.tcp_dsack=1 net.ipv4.tcp_window_scaling=1`** | `27.968` / `118.052` | `28.182` / **`46.295`** | `111.124 -> 68.385` (**`-42.739`**) | **KEEP** |
| `100` | **`LTU-R20`** | `LTU-Lite` | Re-toggle `tc qdisc replace` inside loop (`p50` improved `28.69 -> 27.85 ms`, re-applied at exit) | `28.687` / `39.614` | **`27.850`** / `81.979` | `65.128 -> 89.319` (`+24.191`) | **REJECT** |

---

## 3. High-Impact Wave 7 Hardware Discoveries (`CONFIRMED`)

1. **6 dB Chain-Imbalance Single-Chain TX Proof (`PBM5-R23` `KEEP`)**:
   - On the `-80 dBm` 5.805 GHz `PowerBeam M5 300` OTA link with a severe `6 dB` chain imbalance (`chainrssi=[9, 15]`, meaning Chain 0 is at `-86 dBm` near thermal noise while Chain 1 is at `-80 dBm`), forcing `iwpriv wifi0 txchainmask 2` (transmitting exclusively on the strong Chain 1) eliminated MCS8–15 dual-stream spatial-multiplexing packet losses on weak Chain 0, reducing objective `J` by **`-63.2%` (`26.896 -> 9.896`)** and cutting `p95` OTA RTT by **`-10.9%` (`15.613 -> 13.910 ms`)**! (`txchainmask 3` was automatically restored after the test to preserve symmetric baseline state.)
2. **Single-Factor Confirmation of `/proc/sys/dev/ubnt_poll/no_ack_rate=1` (`PBM5-R25` `KEEP`)**:
   - Testing `echo 1 > /proc/sys/dev/ubnt_poll/no_ack_rate` in strict single-factor isolation at fixed `distance=150` cut `p50` OTA RTT by **`-54.0%` (`9.081 -> 4.175 ms`)** and `p95` OTA RTT by **`-19.0%` (`15.402 -> 12.476 ms`)**.
3. **Cross-Band RTS/CTS (`protmode=1`) Co-Location Protection (`R5AC-R19` `KEEP` & `R2AC-R19` `KEEP`)**:
   - Enabling `iwpriv ath0 protmode 1` reduced `p50` RTT by **`-73.7%` (`8.659 -> 2.281 ms`)** on `Rocket Prism 5AC Gen2` (`R5AC-R19`) and by **`-38.0%` (`2.554 -> 1.583 ms`)** on `Rocket 2AC Prism` (`R2AC-R19`).
4. **Complete `/proc/sys/dev/ubnt_poll/*` Hardware Sysctl Inventory on `PowerBeam M5` (`XW.v6.3.2`)**:
   - Enumerated all 33 `ubnt_poll` kernel sysctls on `XW.v6.3.2`: `aggr_params` (`0 0 0`), `ap_act_linger` (`10000`), `ap_no_dur_off_lim` (`0`), `ap_ptp_simplex_opt` (`0`), `ap_stats_int` (`5000`), `ap_traf_thresh` (`0`), `atpc` (`1 -128`), `capacity` (`7`), `downlink_mp` (`1`), `enable` (`1`), `evm_process` (`0`), `fh` (`0`), `fh_announce_cnt` (`5`), `fh_time` (`1000`), `mode` (`1`), `no_ack` (`0`), `no_ack_rate` (`1 -1`), `no_auto_prio` (`0`), `quality` (`49`), `sa_start` (`49`), `sta_priority` (`3`), `stats`, `timing_params` (`1008 1008 3000 1000 1008`), `tx_sync_act_thresh` (`3`), `tx_sync_mode` (`0`), `txop_params` (`15 5`), `use_ant_array` (`0`), `vtid_mode` (`0`).
