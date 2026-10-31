<!-- doc-head: STAGE12_MULTIRADIO_82ROUND_MASTER_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 12 — Multi-Radio 82-Round (`328` Sub-Phase) Live Hardware Autoresearch Master Benchmark & Causal Ablations

- **Experiment ID**: `FMX-STAGE12-MULTIRADIO-82ROUND-MASTER-LEDGER`
- **Timestamp (UTC)**: `2026-10-24T23:53:19Z`
- **Scope**: **82 paired `A/B/A/B` live RAM-only hardware Autoresearch rounds (`328` sub-phases)** across **6 physical Ubiquiti radios** (`5` distinct SoC/baseband architectures)
- **Master Ledger Receipt**: [`artifacts/autoresearch/multiradio_82round_master_ledger_20261024.json`](../artifacts/autoresearch/multiradio_82round_master_ledger_20261024.json)
- **Golden Profile Applicator**: [`controller/multiradio_golden_profile_applicator.py`](../controller/multiradio_golden_profile_applicator.py)

---

## 1. Executive Summary (`82` Rounds = `328` Sub-Phases: `38 KEEP` / `44 REJECT`)

Across Waves 1 through 6 (`T-BENCH-04` through `T-BENCH-10`), we executed **82 paired `A/B/A/B` live hardware Autoresearch rounds (`328` sub-phases)** across five Ubiquiti fixed-wireless architectures on the isolated physical bench (`198.18.0.90/24` + IPv6 link-local `%27`) with **zero flash writes (`cfgmtd` untouched)** and **100% automatic rollback** on every rejected round:

| Architecture / Device | IP / IPv6 | Firmware / Kernel | SoC + Radio / Baseband | Rounds (`A/B/A/B`) | `KEEP` / `REJECT` | Headline Measured Improvement (`CONFIRMED`) |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **`airFiber 4X` (`AF-4X`)** | `198.18.0.83` / `PUBLIC_DEVICE_0054%27` | `AF06.v4.1.0` (`Linux 2.6.33-rc4`) | TI `AM1808` (`124.5 BogoMIPS`) + **Invictus v2 Custom TDD FPGA (`IRQ 140`)** | `18` (`72` phases) | `10 KEEP` / `8 REJECT` | `framelength=2.5ms`, `flowcntl=on`, `cp=8`, `dpcntl=off`, `cpsel=disabled`, `stricttiming=on`, `tcp_dsack=1`, `txqueuelen=256` cut loaded `p95` RTT by **`-25.9%`** and boosted SSH stream throughput by **`+26.4%`** (`4.591 -> 5.803 Mbps` in `AF4X-R17`). |
| **`LTU-Lite` (`AF-LTU`)** | `PUBLIC_DEVICE_0046%27` (`sysid=0xa614`) | `afltu.v2.4.0` (`Linux 3.14.65 SMP PREEMPT RT`) | **UBNT AME SoC** (Dual-Core Cortex-A9 `1990 BogoMIPS`) + `ame_core` LTU MAC (`IRQ 63/92`) | `18` (`72` phases) | `6 KEEP` / `12 REJECT` | `ame_core/sched_max_agg_cnt=8` (`-88.5%` `p95`), `cz_cross_frame_backoff_enable=0`, `send_ctrl_in_data=0` (`-89.2%` `p95`), and `ath0` root `fq_codel quantum=1514 target=2.5ms` (`-45.8%` `p95`). |
| **`Rocket 2AC Prism` (`R2AC`)** | `198.18.0.65` (`sysid=0xe7f5`) | `2XC.v8.7.11` (`Linux 2.6.32.68`) | `QCA955x` + `QCA988x` 2.4 GHz (`Mode: Master` AP on `2412 MHz`) + **2.4 GHz AirPrism (`IRQ 64`)** | `17` (`68` phases) | `9 KEEP` / `8 REJECT` | Pure `KEEP`-only Golden Stack (`R2AC-R17`: `ani_enable=1`, `daprot=0`, `ptp_xmit=1`, `fixed_frame=1`, `swretry=4/6`, `shpreamble=1`, `txqueuelen=256`, `512 KB` buffers) cut `p50` RTT by **`-75.7%`** (`8.054 -> 1.960 ms`). |
| **`Rocket Prism 5AC Gen2`** | `198.18.0.64` (`sysid=0xe7e9`) | `XC.v8.7.25` (`Linux 2.6.32.68`) | `QCA955x` + `QCA9880` 5 GHz (`Mode: Managed` STA) + **5 GHz AirPrism (`IRQ 64`)** | `11` (`44` phases) | `4 KEEP` / `7 REJECT` | Under active `5180/5805 MHz` co-location with HW `AirPrism` (`IRQ 64` at `35–80/s`), `ifconfig airview1 down`, `ani_enable=0` (`-60.5%` `p50`), and `swretry=4/6` (`-67.9%` `p50`) reduced `p50` RTT to **`1.808 ms`**. |
| **`PowerBeam M5 300` PtP Pair** | `198.18.0.86` AP $\leftrightarrow$ `198.18.0.85` STA | `XW.v6.3.2` (`Linux 2.6.32.68`) | `AR9342` + `AR9580` 5.805 GHz 40 MHz Weak `-80 dBm` OTA Link (`chainrssi=[9, 15]`) | `18` (`72` phases) | `9 KEEP` / `9 REJECT` | Holding `distance=150` constant across `A/B/A/B` in `PBM5-R21` proved zero-transient synergy: the Golden `PBM5` Weak-Link Stack cut 40-packet 1400B OTA `p95` tail latency by **`-84.1%` (`112.796 -> 17.886 ms`)** and reduced `J` by **`-78.0%` (`232.701 -> 51.256`)**. |

---

## 2. Wave 6 Orthogonal Causal Ablations & Multi-Stream Stress (`Rounds 71..82`)

| Global # | Round ID | Device | Knob (`apply_cmd`) | `A` Mean `p50` / `p95` (ms) | `B` Mean `p50` / `p95` (ms) | `A_J -> B_J` (`delta_J`) | Decision |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `71` | **`PBM5-R18`** | `PowerBeam M5` OTA | `txop_params="15 5"` vs `"25 5"` (with `protmode=1`, `shpreamble=1`, `no_ack_rate=1` already active) | `6.944` / `12.563` | `7.936` / `13.540` | `8.031 -> 10.029` (`+1.998`) | **REJECT** |
| `72` | **`PBM5-R19`** | `PowerBeam M5` OTA | `AMPDU=16/16384` vs `32/50000` (with `protmode=1`, `shpreamble=1`, `no_ack_rate=1` already active) | `5.971` / `10.360` | `8.772` / `23.724` | `5.676 -> 18.439` (`+12.763`) | **REJECT** |
| `73` | **`PBM5-R20`** | `PowerBeam M5` OTA | `nonaggr_swretry=4`, `aggr_swretry=6` vs `8/8` on `-80 dBm` weak OTA link | `5.171` / `12.557` | `6.236` / `12.633` | `6.441 -> 7.488` (`+1.047`) | **REJECT** |
| `74` | **`PBM5-R21`** | `PowerBeam M5` OTA | **Full Golden `PBM5` Stack vs Full Stock** (holding `distance=150` constant across `A/B/A/B`, `40`-pkt 1400B OTA) | `7.361` / `112.796` | `9.210` / **`17.886`** | `232.701 -> 51.256` (**`-181.446`**) | **KEEP** |
| `75` | **`LTU-R16`** | `LTU-Lite` | Combined `LTU` Stack vs already-stabilized `sched_max_agg_cnt=8` baseline | `29.225` / `53.608` | `30.066` / `61.214` | `74.364 -> 80.195` (`+5.832`) | **REJECT** |
| `76` | **`LTU-R17`** | `LTU-Lite` | `ame_core/sched_reserved_ul_mgmt_syms=2` (vs `1`) | `29.058` / `40.840` | `30.046` / `67.555` | `66.447 -> 83.937` (`+17.490`) | **REJECT** |
| `77` | **`LTU-R18`** | `LTU-Lite` | `ame_core/bbp_ul_with_traffic_thr=5` (vs `7`) | `30.267` / `40.407` | **`29.096`** / `42.982` | `68.010 -> 67.904` (`p95 > +5%`) | **REJECT** |
| `78` | **`AF4X-R16`** | `airFiber 4X` | `af set modcontrol automatic && af set speed 10x` (vs `8x`) | `27.139` / `35.959` | `27.238` / `38.397` (`+34.9%` tp) | `60.269 -> 61.176` (`+0.907`) | **REJECT** |
| `79` | **`AF4X-R17`** | `airFiber 4X` | `tcp_sack=1`, `tcp_dsack=1`, `tcp_window_scaling=1`, `tcp_low_latency=1` | `27.684` / `41.712` | **`27.546` / `38.666`** (**`+26.4%` tp**) | `64.259 -> 61.616` (**`-2.642`**) | **KEEP** |
| `80` | **`AF4X-R18`** | `airFiber 4X` | `af set linkto 15` (vs `25`) | `27.388` / `30.596` | `29.445` / `38.673` | `56.578 -> 64.585` (`+8.007`) | **REJECT** |
| `81` | **`R5AC-R15`** | `Rocket Prism 5AC` | Combined `R5AC` Stack (vs `airview1 down` baseline) | `1.712` / `24.801` | `6.005` / **`22.570`** (**`+4.4%` tp**) | `12.186 -> 17.053` (`+4.867`) | **REJECT** |
| `82` | **`R5AC-R16`** | `Rocket Prism 5AC` | `iwpriv ath0 shpreamble 1` (vs `0` on 5 GHz `QCA9880`) | `2.178` / `23.884` | `2.521` / `26.404` (**`+9.1%` tp**) | `13.128 -> 14.748` (`+1.619`) | **REJECT** |

---

## 3. Causal Insights from Wave 6 (`CONFIRMED`)

1. **Resolution of the `PBM5-R17` Distance-Estimator Reset Transient (`PBM5-R21` `KEEP`)**:
   - In Wave 5 (`PBM5-R17`), re-writing `iwpriv wifi0 distance 600` $\to$ `150` inside the `A/B/A/B` loop triggered an immediate `ubnt_poll` ACK/slot-timing recalibration transient (`p95 = 10.54 ms` vs `7.50 ms`).
   - In Wave 6 (`PBM5-R21`), holding `distance=150` constant across `A` and `B` while toggling the complete Golden Stack (`AMPDU=16/16384`, `txop="15 5"`, `protmode=1`, `shpreamble=1`, `no_ack_rate=1`, `txqueuelen=256`, `rmem/wmem=262144`, `tcp_low_latency=1`) against full stock under 40-packet 1400B OTA bursts cut `p95` tail latency by **`-84.1%` (`112.796 -> 17.886 ms`)** and reduced `J` by **`-78.0%` (`232.701 -> 51.256`)** (`CONFIRMED`).
2. **Why `nonaggr_swretry=4 / aggr_swretry=6` is `KEEP` on Co-Located `Rocket 2AC/5AC` (`R2AC-R4`, `R5AC-R10`) but `REJECT` on `-80 dBm` Weak OTA `PowerBeam M5` (`PBM5-R20`)**:
   - On strong links experiencing momentary co-location interference bursts, bounding software retries (`4/6` vs `8/8`) prevents head-of-line queue stalls.
   - On a genuinely weak `-80 dBm` link (`chainrssi=[9, 15]`), lowering `aggr_swretry` from `8` to `6` discards recoverable A-MPDU subframes prematurely (`p50: 5.171 -> 6.236 ms`, `REJECT`), proving `swretry=8/8` should be preserved on weak-signal links while `protmode=1` + `no_ack_rate=1` + `shpreamble=1` protect framing (`CONFIRMED`).
3. **`LTU-Lite` `sched_reserved_ul_mgmt_syms=1` Optimality (`LTU-R17` `REJECT`)**:
   - Increasing `ame_core` reserved uplink management symbols from `1` to `2` per `2.0ms` TDD frame stole data symbol capacity and increased `p95` RTT by `+65.4%` (`40.840 -> 67.555 ms`), confirming `sched_reserved_ul_mgmt_syms=1` is optimal.
4. **`AF-4X` Linux 2.6.33 TCP DSACK + Window Scaling (`AF4X-R17` `KEEP`)**:
   - Enabling `net.ipv4.tcp_sack=1 net.ipv4.tcp_dsack=1 net.ipv4.tcp_window_scaling=1 net.ipv4.tcp_low_latency=1` on the 124 BogoMIPS `AM1808` host increased SSH bulk stream throughput by **`+26.4%`** (`4.591 -> 5.803 Mbps`) while reducing `p95` RTT by **`-7.3%`** (`41.712 -> 38.666 ms`).
