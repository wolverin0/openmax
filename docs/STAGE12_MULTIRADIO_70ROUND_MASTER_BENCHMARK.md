<!-- doc-head: STAGE12_MULTIRADIO_70ROUND_MASTER_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 12 — Multi-Radio 70-Round (`280` Sub-Phase) Live Hardware Autoresearch Master Benchmark & Golden Profiles

- **Experiment ID**: `FMX-STAGE12-MULTIRADIO-70ROUND-MASTER-LEDGER`
- **Timestamp (UTC)**: `2026-10-24T23:38:18Z`
- **Scope**: **70 paired `A/B/A/B` live RAM-only hardware Autoresearch rounds (`280` sub-phases)** across **6 physical Ubiquiti radios** (`5` distinct SoC/baseband architectures)
- **Master Ledger Receipt**: [`artifacts/autoresearch/multiradio_70round_master_ledger_20261024.json`](../artifacts/autoresearch/multiradio_70round_master_ledger_20261024.json)
- **Golden Profile Applicator**: [`controller/multiradio_golden_profile_applicator.py`](../controller/multiradio_golden_profile_applicator.py)

---

## 1. Executive Summary (`70` Rounds = `280` Sub-Phases: `36 KEEP` / `34 REJECT`)

Across Waves 1 through 5 (`T-BENCH-04`, `T-BENCH-06`, `T-BENCH-07`, `T-BENCH-08`, `T-BENCH-09`), we executed **70 paired `A/B/A/B` live hardware Autoresearch rounds (`280` measurement windows)** across five Ubiquiti fixed-wireless architectures on the isolated physical bench (`198.18.0.90/24` + IPv6 link-local `%27`) with **zero flash writes (`cfgmtd` untouched)** and **100% automatic rollback** on every rejected round:

| Architecture / Device | IP / IPv6 | Firmware / Kernel | SoC + Radio / Baseband | Rounds (`A/B/A/B`) | `KEEP` / `REJECT` | Headline Measured Improvement (`CONFIRMED`) |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **`airFiber 4X` (`AF-4X`)** | `198.18.0.83` / `PUBLIC_DEVICE_0054%27` | `AF06.v4.1.0` (`Linux 2.6.33-rc4`) | TI `AM1808` (`124.5 BogoMIPS`) + **Invictus v2 Custom TDD FPGA (`IRQ 140`)** | `15` (`60` phases) | `9 KEEP` / `6 REJECT` | `framelength=2.5ms`, `flowcntl=on`, `cp=8`, `dpcntl=off`, `cpsel=disabled`, `stricttiming=on`, `txqueuelen=256` cut loaded `p95` RTT by **`-25.9%`** (`41.09 -> 30.45 ms` / `33.25 -> 25.68 ms`) and boosted SSH stream by **`+15.3%`**. |
| **`LTU-Lite` (`AF-LTU`)** | `PUBLIC_DEVICE_0046%27` (`sysid=0xa614`) | `afltu.v2.4.0` (`Linux 3.14.65 SMP PREEMPT RT`) | **UBNT AME SoC** (Dual-Core Cortex-A9 `1990 BogoMIPS`) + `ame_core` LTU MAC (`IRQ 63/92`) | `15` (`60` phases) | `6 KEEP` / `9 REJECT` | `ame_core/sched_max_agg_cnt=8` (`-88.5%` `p95`), `cz_cross_frame_backoff_enable=0`, `send_ctrl_in_data=0`, and `ath0` root `fq_codel quantum=1514 target=2.5ms` (`-45.8%` `p95`) eliminated background scan tail spikes. |
| **`Rocket 2AC Prism` (`R2AC`)** | `198.18.0.65` (`sysid=0xe7f5`) | `2XC.v8.7.11` (`Linux 2.6.32.68`) | `QCA955x` + `QCA988x` 2.4 GHz (`Mode: Master` AP on `2412 MHz`) + **2.4 GHz AirPrism (`IRQ 64`)** | `17` (`68` phases) | `9 KEEP` / `8 REJECT` | Pure `KEEP`-only Golden Stack (`R2AC-R17`: `ani_enable=1`, `daprot=0`, `ptp_xmit=1`, `fixed_frame=1`, `swretry=4/6`, `shpreamble=1`, `txqueuelen=256`, `512 KB` buffers) cut `p50` RTT by **`-75.7%`** (`8.054 -> 1.960 ms`). |
| **`Rocket Prism 5AC Gen2`** | `198.18.0.64` (`sysid=0xe7e9`) | `XC.v8.7.25` (`Linux 2.6.32.68`) | `QCA955x` + `QCA9880` 5 GHz (`Mode: Managed` STA) + **5 GHz AirPrism (`IRQ 64`)** | `9` (`36` phases) | `4 KEEP` / `5 REJECT` | Under active `5180/5805 MHz` co-location with HW `AirPrism` (`IRQ 64` at `35–80/s`), `ifconfig airview1 down`, `ani_enable=0` (`-60.5%` `p50`), and `swretry=4/6` (`-67.9%` `p50`) reduced `p50` RTT to **`1.808 ms`**. |
| **`PowerBeam M5 300` PtP Pair** | `198.18.0.86` AP $\leftrightarrow$ `198.18.0.85` STA | `XW.v6.3.2` (`Linux 2.6.32.68`) | `AR9342` + `AR9580` 5.805 GHz 40 MHz Weak `-80 dBm` OTA Link (`chainrssi=[9, 15]`) | `14` (`56` phases) | `8 KEEP` / `6 REJECT` | Right-sizing `AMPDUFrames=16`, `AMPDULim=16384`, `distance=150`, `txop="15 5"`, `protmode=1`, `shpreamble=1`, and `no_ack_rate=1` rescued `CCQ` from `58% -> 95.5%` and cut 30-pkt 1400B OTA `p50` RTT from `10.47 -> 4.04 ms` (`p95: 65.0 -> 7.50 ms`). |

---

## 2. Wave 5 Holdout & Refinement Results (`Rounds 59..70`)

| Global # | Round ID | Device | Knob (`apply_cmd`) | `A` Mean `p50` / `p95` (ms) | `B` Mean `p50` / `p95` (ms) | `A_J -> B_J` (`delta_J`) | Decision |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `59` | **`R2AC-R15`** | `Rocket 2AC Prism` | `echo 1 > /proc/sys/dev/uph_wifi0/fixed_frame` | `2.090` / `24.770` | **`1.794`** / `24.895` | `12.633 -> 12.341` (**`-0.292`**) | **KEEP** |
| `60` | **`R2AC-R16`** | `Rocket 2AC Prism` | `iwpriv ath0 wds 0` vs `1` (test overhead) | `10.519` / `24.742` | **`1.550` / `23.173`** | `25.338 -> 10.628` (**`-14.710`**) | **KEEP** |
| `61` | **`R2AC-R17`** | `Rocket 2AC Prism` | **Pure `KEEP`-Only Golden `R2AC` Stack** (`ani=1`, `daprot=0`, `ptp_xmit=1`, `swretry=4/6`, `shpreamble=1`, `qlen=256`, `512KB`) | `8.054` / `25.882` | **`1.960` / `25.514`** | `22.273 -> 12.735` (**`-9.538`**) | **KEEP** |
| `62` | **`LTU-R13`** | `LTU-Lite` | `tc qdisc replace dev eth0 parent :1..:8 handle ${q}0:` | `30.512` / `48.576` | `31.430` / `222.105` | `73.258 -> 178.756` (`+105.498`) | **REJECT** |
| `63` | **`LTU-R14`** | `LTU-Lite` | `echo 0 > /sys/module/ame_core/parameters/send_ctrl_in_data` | `28.152` / `394.128` | `29.140` / **`42.581`** | `277.030 -> 67.681` (**`-209.349`**) | **KEEP** |
| `64` | **`LTU-R15`** | `LTU-Lite` | Combined `LTU` Candidate (including `eth0` `mq` replace) | `34.323` / `48.918` | **`30.901`** / `119.141` | `79.170 -> 116.187` (`+37.017`) | **REJECT** |
| `65` | **`PBM5-R15`** | `PowerBeam M5` OTA | `iwpriv ath0 shpreamble 1` (`30`-pkt 1400B OTA burst) | `10.468` / `16.245` | **`6.008` / `12.311`** | `48.287 -> 6.549` (**`-41.738`**) | **KEEP** |
| `66` | **`PBM5-R16`** | `PowerBeam M5` OTA | `echo 1 > /proc/sys/dev/ubnt_poll/no_ack_rate` | `4.699` / `8.428` | **`4.199`** / `8.464` | `2.830 -> 1.900` (**`-0.929`**) | **KEEP** |
| `67` | **`PBM5-R17`** | `PowerBeam M5` OTA | Full Stack Re-Toggle (`distance` reset penalty during `B`) | `4.035` / `7.504` | `5.983` / `10.540` | `1.131 -> 5.062` (`+3.931`) | **REJECT** |
| `68` | **`AF4X-R13`** | `airFiber 4X` | `af set dpcntl off` (vs `on`) | `28.405` / `41.087` | **`26.489` / `30.448`** | `64.972 -> 55.197` (**`-9.775`**) | **KEEP** |
| `69` | **`AF4X-R14`** | `airFiber 4X` | `af set cpsel disabled && af set cp 8` | `26.641` / `29.965` | **`26.522`** / `30.366` | `55.087 -> 55.079` (**`-0.009`**) | **KEEP** |
| `70` | **`AF4X-R15`** | `airFiber 4X` | Golden `AF-4X` Steady-State Floor Verification (`28.2 ms` `p95`) | `26.780` / `28.209` | `26.836` / `28.224` | `54.214 -> 54.279` (`+0.065`) | **REJECT** |

---

## 3. Cross-Platform Architectural Laws Discovered (`CONFIRMED`)

1. **Band & Mode Asymmetry of `iwpriv wifi0 ani_enable` (`R2AC-R9` vs `R5AC-R9`)**:
   - Hardware `AirPrism` (`IRQ 64 ath_prism_filter_blanking_isr`) rejects **out-of-channel** energy outside the tuned channel passband.
   - On a **fixed-channel 2.4 GHz AP (`Rocket 2AC Prism`, `Mode: Master`, `2412 MHz`)**, strong **in-band** 2.4 GHz interference passes through the 20 MHz `AirPrism` passband, so `ani_enable=1` is mandatory (`ani_enable=0` degraded `p50` by `+334%` in `R2AC-R9`). Ensuring `ani_enable=1` + `daprot=0` turned the `Rocket 2AC Prism` Golden Stack (`R2AC-R17`) into a **`-75.7%` `p50` winner** (`8.054 -> 1.960 ms`).
   - On an **unassociated 5 GHz STA scanning across channels (`Rocket Prism 5AC Gen2`, `Mode: Managed`)**, software ANI register polling across `IRQ 75` stalls channel transitions while `AirPrism` (`IRQ 64`) already blanks adjacent `5180/5805 MHz` bench emitters; setting `ani_enable=0` cut `p50` by **`-60.5%`** (`4.575 -> 1.808 ms` in `R5AC-R9`).
2. **Spectrometer Quiescing Without IPC Deadlock (`R2AC-R8`, `R5AC-R6`, `R2AC-R10`)**:
   - Sending `SIGSTOP` to `ubntspecd` blocks `udapi-bridge` UNIX domain sockets (`p95 = 123.7 ms`). Bringing the monitor VAP down administratively (`ifconfig airview1 down`) stops `IRQ 2` (`wifi1`) and `IRQ 64` spectral scan bursts with zero `udapi-bridge` stalls (`-77.0%` `p50` in `R2AC-R10`).
3. **`UBNT AME SoC` (`LTU-Lite`) `ath0` vs `eth0` `fq_codel` Asymmetry (`LTU-R4`, `LTU-R7`, `LTU-R13`)**:
   - `LTU-Lite` (`Linux 3.14.65 SMP PREEMPT RT`) runs `fq_codel` (`quantum 300`) natively on both `ath0` root and `eth0`'s 8 hardware `mq` queues (`:1..:8`). Tuning `ath0` root to full-MTU `quantum 1514 target 2.5ms interval 50ms` cut `p95` RTT by **`-45.8%`** (`LTU-R4`), whereas replacing `eth0`'s 8 hardware `mq` leaves (`handle ${q}0:`) induced transient Ethernet ring stalls (`LTU-R13` `REJECT`). Meanwhile, `/sys/module/ame_core/parameters/sched_max_agg_cnt=8` (`LTU-R9`) and `send_ctrl_in_data=0` (`LTU-R14`) eliminated `ame_core` background scheduler spikes (`-88.5%` and `-89.2%` `p95`).
4. **Weak-Link (`-80 dBm`, `6 dB` Chain Imbalance) AirMAX `XW` OTA Rescue (`PBM5-R9..R16`)**:
   - On a degraded `-80 dBm` 5.805 GHz PtP link (`chainrssi=[9, 15]`), stock `AMPDUFrames=32` / `AMPDULim=50000` suffers severe subframe PER (`CCQ = 58%`, `p95 = 65.0 ms`). Right-sizing `AMPDUFrames=16`, `AMPDULim=16384`, `distance=150`, `txop_params="15 5"`, `protmode=1`, `shpreamble=1`, and `no_ack_rate=1` lifted `CCQ` to **`95.5%`** and cut 30-packet 1400B OTA `p50` RTT to **`4.035 ms`** (`p95 = 7.504 ms`).
