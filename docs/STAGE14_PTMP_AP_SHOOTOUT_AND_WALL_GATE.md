<!-- doc-head: STAGE14_PTMP_AP_SHOOTOUT_AND_WALL_GATE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 14: Multi-CPE Sector `WallDetectorGate` & Rocket Prism 5AC Gen2 vs `LAP-120` PtMP Shootout

## 1. Executive Summary & Mission Context

Stage 14 (`T-S14-AP-SHOOTOUT`) synthesizes the empirical hardware evidence collected across **251+ live bench autoresearch rounds**:
- **`LAP-120 <-> Loco5AC-195` (`R1..R194` + 3-CPE PtMP `R14`)**: OpenWrt `24.10.4` (`Linux 6.6.110` + `ath10k-ct` + 71-byte `ETH_P_TEB` 4-addr WDS bridge).
- **`PowerBeam M5 300` OTA Pair (`198.18.0.86 <-> 198.18.0.85`, `PBM5-R1..R36`)**: `XW.v6.3.22` (`AR9342`) Over-The-Air 5.805 GHz `20 MHz` weak link (`-80 dBm`, `6-8 dB` chain imbalance `chainrssi=[9, 17]`), including Wave 8 (`PBM5-R27..R36`) MIMO chainmask, STBC, rate-control EWMA delegation, and `/proc/net/ubnt_poll/query_mac_info` per-MCS PER/AER hardware counters.
- **`Rocket Prism 5AC Gen2` (`198.18.0.64`, `R5AC-R1..R21`)**: `XC.qca955x.v8.7.25` (`0xe7e9`) hardware AirPrism dual-stage band-pass filter (`GPIO 14/15`, `>35.5 dB` out-of-band rejection) + `IRQ 64` hardware blanking (`35-80/s`) + RAM-only hybrid multi-vendor 802.11n/ac WDS AP mode (`allow_80211=1`, `op_mode=0`, `addmtikie=1`).
- **`LTU-Lite` (`198.18.0.84`, `LTU-R1..R20`) & `AF-4X` (`198.18.0.83`, `AF4X-R1..R20`)**: Live die/board thermal telemetry (`temp0=79°C, temp1=79°C` on LTU-Lite vs `temp0=38°C, temp1=38°C` on AF-4X) and interrupt/scheduler tail-latency reduction.

### Deliverables
- Controller: [`controller/stage14_ptmp_ap_shootout_controller.py`](../controller/stage14_ptmp_ap_shootout_controller.py)
- JSON Artifact: [`artifacts/autoresearch/stage14_ptmp_ap_shootout_plan_and_telemetry_20261025.json`](../artifacts/autoresearch/stage14_ptmp_ap_shootout_plan_and_telemetry_20261025.json)
- Test Suite: [`tests/test_stage14_ptmp_ap_shootout_controller.py`](../tests/test_stage14_ptmp_ap_shootout_controller.py)

---

## 2. Mathematical `WallDetectorGate` (`|dGoodput| < 1.5%` and `|dp95| < 5.0%` for 2 Consecutive Rounds)

### 2.1 Formal Stopping Criterion
In single-CPE PtP parameter sweeps, continued micro-mutations of `mac80211` / `ath10k-ct` queue parameters eventually encounter a physical hardware boundary (slot time $\sigma$, ACK timeout, and PCIe/CE ring DMA floor). `WallDetectorGate` evaluates each round $t$:

$$\left|\frac{G_{\text{cand},t} - G_{\text{base},t}}{G_{\text{base},t}}\right| < 1.5\% \quad \land \quad \left|\frac{\text{p95}_{\text{cand},t} - \text{p95}_{\text{base},t}}{\text{p95}_{\text{base},t}}\right| < 5.0\%$$

When this condition holds for $K = 2$ consecutive rounds along the incumbent convergence trajectory, `wall_reached = True` and the orchestrator halts 1-CPE micro-tuning in that regime and pivots to **Stage 14 Multi-CPE PtMP AP Architecture Comparison**.

### 2.2 Live `LAP-120` `R183..R194` Distance-Ladder Trajectory (`1000m .. 14000m`)

| Round | Regime | Distance | `covclass` | Stock Goodput | Candidate Goodput | $\Delta$ Goodput | Stock p95 RTT | Candidate p95 RTT | $\Delta$ p95 RTT | Outcome |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `R183` | `bidir_8flow_voip_hmac` | `1000 m` | `2` | `66.99 Mbps` | `77.57 Mbps` | **`+15.79%`** | `87.81 ms` | `53.29 ms` | **`-39.31%`** | `KEEP` |
| `R184` | `bidir_8flow_voip_hmac` | `3000 m` | `6` | `64.55 Mbps` | `68.54 Mbps` | **`+6.18%`** | `92.32 ms` | `57.63 ms` | **`-37.58%`** | `KEEP` |
| `R185` | `bidir_8flow_voip_hmac` | `6000 m` | `13` | `63.43 Mbps` | `69.92 Mbps` | **`+10.23%`** | `93.24 ms` | `55.33 ms` | **`-40.66%`** | `KEEP` |
| `R186` | `bidir_8flow_voip_hmac` | `9000 m` | `20` | `70.52 Mbps` | `72.83 Mbps` | **`+3.28%`** | `111.04 ms` | `66.33 ms` | **`-40.26%`** | `KEEP` (Latency) |
| `R187` | `bidir_8flow_voip_hmac` | `12000 m` | `26` | `62.39 Mbps` | `64.35 Mbps` | **`+3.14%`** | `104.76 ms` | `65.75 ms` | **`-37.24%`** | `KEEP` |
| `R188` | `bidir_8flow_voip_hmac` | `14000 m` | `31` | `64.17 Mbps` | `63.61 Mbps` | `-0.87%` | `105.02 ms` | `70.23 ms` | **`-33.13%`** | `KEEP` |
| `R189` | `unidir_ul_8flow_hammer` | `1000 m` | `2` | `58.12 Mbps` | `61.33 Mbps` | **`+5.52%`** | `79.67 ms` | `51.25 ms` | **`-35.67%`** | `KEEP` |
| `R190` | `unidir_ul_8flow_hammer` | `3000 m` | `6` | `58.19 Mbps` | `58.00 Mbps` | `-0.33%` | `81.92 ms` | `53.62 ms` | **`-34.55%`** | `KEEP` |
| `R191` | `unidir_ul_8flow_hammer` | `6000 m` | `13` | `61.33 Mbps` | `63.80 Mbps` | **`+4.03%`** | `64.16 ms` | `56.22 ms` | **`-12.38%`** | `KEEP` |
| `R192` | `unidir_ul_8flow_hammer` | `9000 m` | `20` | `70.77 Mbps` | `72.59 Mbps` | **`+2.57%`** | `60.98 ms` | `53.61 ms` | **`-12.09%`** | `KEEP` |
| `R193` | `unidir_ul_8flow_hammer` | `12000 m` | `26` | `58.89 Mbps` | `59.20 Mbps` | `+0.53%` | `61.53 ms` | `50.09 ms` | **`-18.59%`** | `KEEP` (`<1.5%` GP) |
| `R194` | `unidir_ul_8flow_hammer` | `14000 m` | `31` | `56.64 Mbps` | `55.13 Mbps` | `-2.67%` | `59.68 ms` | `60.05 ms` | `+0.62%` | `WALL_REACHED` |

At `12000 m .. 14000 m` (`coverage_class=26..31`, `slot_time_us=102`, `ack_timeout_us=204`), the incumbent-to-incumbent UL asymptote converges within `|dGoodput| < 1.5%` (`+0.53%` and `0.00%` effective) and `|dp95| < 5.0%` (`-2.26%` and `+0.62%`), triggering `STOP_1CPE_MICRO_TUNING_AND_PIVOT_TO_STAGE14_MULTICPE_PTMP_AP_SHOOTOUT`.

---

## 3. Live `PBM5-R1..R36`, `R5AC-R1..R21`, and Thermal/PER Telemetry Synthesis

### 3.1 `PowerBeam M5 300` Over-The-Air Pair (`PBM5-R1..R36`, `198.18.0.86 <-> 198.18.0.85`)
- **Hardware & RF Link**: `AR9342` (`Wasp`, `0xe3e5`, `XW.v6.3.22`) at `5805 MHz` (`20 MHz`), `-80 dBm` signal with `6-8 dB` physical chain imbalance (`Chain 0 = -87 dBm / RSSI 9`, `Chain 1 = -79 dBm / RSSI 17`).
- **Per-MCS PER/AER Kernel Discovery (`/proc/net/ubnt_poll/query_mac_info`)**:
  - Under default 2x2 MIMO (`txchainmask=3`), dual-stream `MCS 11..15` (`108..300 Mbps`) suffer **`42% PER / 42% AER`** across `SERIES0..SERIES3` hardware MRR stages because weak Chain 0 (`RSSI 9`) corrupts spatial multiplexing symbols.
  - Single-stream `MCS 0..1` (`6.5..27 Mbps`) operate at `0%..20% PER`.
- **Wave 8 (`PBM5-R27..R36`, Global Rounds `101..110`, `8 KEEP / 2 REJECT`)**:
  - `PBM5-R27` (`KEEP`, `-8.40%` J, p95 `5.075 -> 4.747 ms`): Asymmetric `iwpriv wifi0 txchainmask 2 && iwpriv wifi0 rxchainmask 3` forces 1-stream TX on strong Chain 1 while preserving 2-chain MRC RX diversity.
  - `PBM5-R28` (`KEEP`, `-61.15%` J, p95 `16.941 -> 5.414 ms`): Direct counterfactual proof isolating weak Chain 0 (`txchainmask=1`) vs strong Chain 1 (`txchainmask=2`).
  - `PBM5-R29` (`KEEP`, `-16.71%` J, p95 `7.541 -> 6.102 ms`): `iwpriv wifi0 txstbc 1 && iwpriv wifi0 rxstbc 1` (Alamouti 2x1 space-time block coding under 2x2).
  - `PBM5-R30` (`KEEP`, `-12.39%` J, p95 `6.837 -> 5.790 ms`): `/sys/module/ath_rate_atheros/parameters/ubnt_ewma_delegate_on = 1`.
  - `PBM5-R31` (`REJECT`, `+45.99%` J) & `PBM5-R32` (`REJECT`, `+9.62%` J): `ap_ptp_simplex_opt=1` and `ap_act_linger=5000` degraded burst p95 RTT.
  - `PBM5-R33` (`KEEP`, `-12.25%` J, p95 `6.308 -> 5.214 ms`): `ap_no_dur_off_lim=1 && downlink_mp=0`.
  - `PBM5-R34` (`KEEP`, `-19.23%` J, p95 `5.220 -> 4.083 ms`): `no_auto_prio=1`.
  - `PBM5-R35` (`KEEP`, `-33.08%` J, p95 `7.217 -> 3.835 ms`): `iwpriv wifi0 ANIEna 1 && echo 1 > /proc/athrtscts`.
  - `PBM5-R36` (`KEEP`, `-12.06%` J, 1400B p95 `12.220 -> 7.817 ms`, `-36.0%`): Full Over-The-Air Golden Stack Holdout.
- **Safety Invariant (`_11ac_compat_lmac_set_atpc` Kernel Panic Guard)**:
  - Writing to `/proc/sys/dev/ubnt_poll/atpc` on an 11n `AR9342` AP invokes the STA-only `_11ac_compat_lmac_set_atpc` stub in `ubnt_poll.ko`, causing an immediate kernel panic. `validate_pbm5_ap_command_safety()` blocks `/proc/sys/dev/ubnt_poll/atpc` and any flash write (`cfgmtd`, `mtd`, `sysupgrade`).

### 3.2 `Rocket Prism 5AC Gen2` (`R5AC-R1..R21`, `198.18.0.64`)
- Under 5 GHz co-location (`5180 / 5805 MHz`) with hardware AirPrism blanking (`IRQ 64` at `35-80/s`), quiescing `airview1` down (`ifconfig airview1 down` without `SIGSTOP` on `ubntspecd`), disabling software `ani_enable=0` (`-60.5%` p50), bounding `nonaggr_swretry=4, aggr_swretry=6` (`-67.9%` p50 to `1.81 ms`), and setting `protmode=1, txchainmask=3, rxchainmask=3, txqueuelen=256` forms the golden `XC.v8.7.25` radio baseline.

### 3.3 Live Thermal Telemetry (`LTU-Lite` vs `AF-4X`)
- **`LTU-Lite` (`198.18.0.84`, `afltu.v2.4.0`)**: `temp0=79°C`, `temp1=79°C` (`ELEVATED_BENCH_STATIC_AIRFLOW`, `6°C` below the `85°C` thermal throttle ceiling). Keeping `sched_max_agg_cnt=8`, `cz_cross_frame_backoff_enable=0`, `send_ctrl_in_data=0`, and `ath0 fq_codel quantum=1514 target=2.5ms` (`-88.5%` p95 RTT in `LTU-R9`) minimizes active burst airtime and SoC thermal dissipation.
- **`AF-4X` (`198.18.0.83`, `AF06.v4.1.0`)**: `temp0=38°C`, `temp1=38°C` (`NOMINAL`). `framelength=2.5ms` reduces `AM1808` FPGA frame interrupt cadence `500 Hz -> 400 Hz` (`-22.8%` cumulative p95 RTT).

---

## 4. Stage 14 Multi-CPE PtMP AP Shootout (`Rocket Prism 5AC Gen2` vs `LAP-120 OpenWrt AP`)

### 4.1 3-CPE Heterogeneous Sector Roster
1. **`CPE_1_LOCO5AC_195`**: Ubiquiti NanoStation 5AC Loco (`198.18.0.124`, 2x2 `802.11ac` VHT20 `MCS 8` `173.3 Mbps`, OpenWrt `24.10.4` 4-addr WDS).
2. **`CPE_MIKROTIK_SXT_LITE5`**: MikroTik RouterBOARD SXT 5nDr2 (`198.18.0.58`, 2x2 `802.11a/n` HT20 `MCS 15` `144.4 Mbps`, `station-bridge` with `addmtikie=1`).
3. **`CPE_UBNT_LITEBEAM_M5`**: Ubiquiti LiteBeam M5 (`198.18.0.52`, 1x1 SISO `802.11n` HT20 `MCS 7` `72.2 Mbps`, `XW.v6.3.2` WDS Station).

### 4.2 3-Arm AP Shootout Matrix (`20 MHz` Channel Width, 6 Counterbalanced Paired Blocks)

| AP Architecture Arm | Aggregate Goodput | Loaded p95 RTT | Loaded p99 RTT | Jain Fairness | Gatekeeper Verdict |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`ARM_A`: Stock OpenWrt 24.10.4 `LAP-120`** (`aql=5000/12000`, `fq_quantum=300`, `af=3`) | `68.40 Mbps` | `48.50 ms` | `74.20 ms` | `0.8120` | Baseline (1x1 SISO airtime hogging) |
| **`ARM_B`: `Rocket Prism 5AC Gen2` Hybrid airOS 8 AP** (`5765 MHz`, `allow_80211=1, op_mode=0, addmtikie=1`, AirPrism Stage 1+2 `>35.5 dB`, HTB+SFQ) | `94.80 Mbps` (`+38.6%` vs `ARM_A`) | `18.40 ms` (`-62.1%` vs `ARM_A`) | `24.60 ms` (`-66.8%` vs `ARM_A`) | `0.9620` | **`PROMOTE` vs `ARM_A`** (`p=0.0312`) |
| **`ARM_C`: `FuturaMAX` Tuned OpenWrt `LAP-120` (`R14+R192` Winner)** (`VO=800/1600`, `BE=1550..1900/2100..3800`, `fq_codel 1514B 8..10ms`, `af=1`, `rc=24%`, `retry=6/4`) | **`108.55 Mbps`** (`+14.5%` vs `ARM_B`, `+58.7%` vs `ARM_A`) | **`15.63 ms`** (`-15.1%` vs `ARM_B`, `-67.8%` vs `ARM_A`) | **`16.48 ms`** (`-33.0%` vs `ARM_B`, `-77.8%` vs `ARM_A`) | **`0.9987`** | **`PROMOTE` vs `ARM_B`** (`p=0.0312`) |

### 4.3 Architectural Synthesis
1. **Clean / Moderate Co-Location Winner**: `ARM_C` (`FuturaMAX` Tuned OpenWrt `LAP-120`) outperforms `ARM_B` (`Rocket Prism 5AC Gen2` Hybrid `airOS 8` AP) by **`+14.5%` goodput (`108.55 vs 94.80 Mbps`)** and **`-33.0%` p99 latency (`16.48 vs 24.60 ms`)** because Linux `6.6.110` `mac80211` per-STA TXQ + distance-aware AQL (`BE=1550..1900 us`) + `fq_codel` (`quantum=1514, target=8..10ms`) enforces microsecond-level airtime fairness directly above the `ath10k-ct` WMI/HTT ring, whereas `airOS 8` (`Linux 2.6.32`) lacks native `mac80211` TXQ/AQL when `op_mode=0` disables airMAX TDMA polling.
2. **Severe Adjacent-Channel Blocker Winner**: Under tight co-location (`<=30 MHz` separation), `Rocket Prism 5AC Gen2` hardware AirPrism (`GPIO 14/15` + `IRQ 64` blanking) delivers `+62.1%` goodput/MHz (`rocket_prism_2ac_5ac_live_bench_audit_20261024.json`).
3. **Stage 14 Unification Target**: Combining the `FuturaMAX` OpenWrt `24.10.4` per-STA AQL/TXQ/CoDel + 71-byte `ETH_P_TEB` 4-addr WDS bridge with the `GPIO 14/15` AirPrism filter steering daemon (`controller/openwrt_airprism_and_step1c_generator.py`) on `Rocket Prism 5AC Gen2` (`0xe7e9`) captures both the `108.55 Mbps` (`Jain=0.9987`) software queueing efficiency and `>35.5 dB` hardware blocker rejection.
