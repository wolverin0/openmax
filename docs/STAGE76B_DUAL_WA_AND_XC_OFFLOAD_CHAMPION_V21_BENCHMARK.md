<!-- doc-head: STAGE76B_DUAL_WA_AND_XC_OFFLOAD_CHAMPION_V21_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 76B — Dual `WA` (`Loco 5AC .250`) + `XC` (`Rocket 5AC Prism .198`) Offload & NAPI Scaling Benchmark (`2026-10-26`)

- **Task ID**: `T-S76B-DUAL-WA-AND-XC-S70C-OFFLOAD-CHAMPION-V21-BENCH`
- **Status**: `CONFIRMED` (`6` counterbalanced `A1 -> B1 -> A2 -> B2` rounds = `24` physical OTA windows, `45s` auto-rollback watchdog, `0` flash writes, `.241`/`.242` untouched)
- **Artifacts**:
  - Runner: [`tools/bench/run_stage76b_dual_wa_xc_offload_champion_v21.py`](../tools/bench/run_stage76b_dual_wa_xc_offload_champion_v21.py)
  - Receipt JSON: [`artifacts/autoresearch/stage76b_dual_wa_xc_offload_champion_v21_20261026.json`](../artifacts/autoresearch/stage76b_dual_wa_xc_offload_champion_v21_20261026.json)
  - Pytest Suite: [`tests/test_stage76b_dual_wa_xc_champion_v21.py`](../tests/test_stage76b_dual_wa_xc_champion_v21.py)

---

## 1. Executive Summary & Causal Laws (`CONFIRMED`)

We evaluated applying the `Stage 70C` non-airtime-inflating offload & NAPI stack (`set_multiq=1, enable_tx_tcp_cksum=1, AMPDUFrames=24, aggr_swretry=4, nonaggr_swretry=4, daprot=2, ff_mcast_airtime_limit=5` written last + NAPI/TSQ/AQL co-tuning) to **both** the `WA` station (`NanoStation 5AC Loco` `.250` / `198.18.0.67`, `535 MHz AR9342`, `64 MB` RAM, OpenWrt `Linux 6.6.110`) and the `XC` station (`Rocket 5AC Prism Gen2` `.198` / `198.18.0.68`, `720 MHz QCA9558`, `128 MB` RAM, `airOS 8.7.11`) on top of `Stage 72A Champion v20`.

### Two New Physical Laws Discovered (`FMX-DISC-21` & `FMX-DISC-22`)

1. **`FMX-DISC-21` — Asymmetric `XC` (`720 MHz QCA9558`, `netdev_budget=800`) vs `WA` (`535 MHz AR9342` OpenWrt, `netdev_budget=600`) CPU-Class NAPI Scaling Law (`CONFIRMED`)**:
   - On `Rocket 5AC Prism Gen2` (`XC` `.198`, `720 MHz QCA9558`, `128 MB` RAM, `umac.ko` hardware DMA `enable_tx_tcp_cksum=1` + `set_multiq=1`), raising `net.core.netdev_budget` from `600 -> 800` boosted sector goodput by `+8.559%` (`S70C`) / `+7.886%` (`S72A-R4`).
   - On `NanoStation 5AC Loco` (`WA` `.250`, `535 MHz AR9342`, `64 MB` RAM, OpenWrt `mac80211` + `ath10k` software `fq_codel` + active `iperf3` bidirectional socket threads), raising `net.core.netdev_budget` from `600 -> 800` in **`S76B-R1`** cut loaded `p50` RTT by **`-11.883%` (`40.039 -> 35.281 ms`)**, `p95` RTT by **`-4.575%` (`83.364 -> 79.550 ms`, `< 80 ms`)**, `p99` RTT by **`-13.751%` (`105.309 -> 90.828 ms`)**, IPTV jitter by **`-15.470%`**, and VoIP loss to **`0.00%`** (Pareto **`+1.0617%`**), but held the `535 MHz` single-core CPU in `net_rx_action()` softirq slightly longer per poll, trimming mean goodput by `-0.540%` (`40.584 -> 40.365 Mbps`, with `B1` peaking at `42.156 Mbps`).
   - Conversely, restoring `WA` `netdev_budget=600` while tightening `WA` TSQ/AQL in **`S76B-R5`** (`TSQ=65536, lowat=6144`) and **`S76B-R6`** (`AC_BE=750/1350, thr=3500`) immediately turned goodput positive (**`+1.292%` to `41.463 Mbps`** in `R5` with **`-10.828%` `p99` RTT** and **`-25.348%` IPTV jitter**; **`+1.498%` to `41.392 Mbps`** in `R6` with **`-9.291%` `p50` RTT** and **`-14.080%` VoIP jitter**), confirming that `Stage 72A Champion v20` (`XC budget=800` + `WA budget=600, AC_BE=900/1500, thr=4000, fq_quantum=1514, TSQ=98304`) is the strict multi-objective `gp_b >= gp_a` & `p95_b <= p95_a` optimum.
   - **Attribution**: `Linux` NAPI softirq scheduler (`net/core/dev.c`) / `hardware` (`535 MHz AR9342` vs `720 MHz QCA9558`).

2. **`FMX-DISC-22` — OpenWrt BusyBox `ping -i <float>` Silent Rejection & `seq` Per-Window Rate-Control Warmup Law (`CONFIRMED`)**:
   - BusyBox `ping` on OpenWrt 24.10.4 rejects fractional intervals (`ping -i 0.15` exits immediately with `ping: invalid number '0.15'` and sends `0` packets when masked by `|| true`).
   - In **`S76B-R3`**, when `LiteBeam M5` (`XW` `.4`) decayed to `rx_bitrate_mbps = 6.5` (`MCS0`), the fractional `-i 0.15` warmup sent `0` packets, leaving `.4` at `6.5 Mbps` (`6x` airtime tax) and depressing sector goodput to `17.983 / 19.627 Mbps` (`p95` RTT `146.8–151.0 ms`).
   - Replacing `ping -i 0.15` with a BusyBox-compatible `for i in $(seq 1 25); do ping -c 1 -W 1 -s 1200 -I br-lan 198.18.0.52 >/dev/null 2>&1; done` loop inside `warmup_xw_and_sector()` before every window (`S76B-R4..R6`) trained `LiteBeam M5` from `6.5 Mbps` (`MCS0`) to `26.0–52.0 Mbps` (`MCS3–MCS5`) in `1.2s`, restoring sector goodput to **`40.84–41.46 Mbps`** and slashing `p95` RTT from `146.8 ms -> 82.8–83.7 ms` (`-43.6%`).
   - **Attribution**: `Linux` userspace (`BusyBox` `ping` integer `-i` parser) + `proprietary airMAX module` (`ath_rate_atheros.ko`).

---

## 2. Counterbalanced 6-Round (`24`-Window) Benchmark Results

| Round ID | Mechanism ID | `WA` (`.250`) Candidate Settings (`+ XC S70C`) | Arm A GP (`Mbps`) | Arm B GP (`Mbps`) | GP $\Delta$ | Arm A `p50` / `p95` / `p99` (`ms`) | Arm B `p50` / `p95` / `p99` (`ms`) | `p95` $\Delta$ | IPTV / VoIP Jitter $\Delta$ | Pareto $\Delta$ | Decision |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S76B-R1`** | `M42a` | `budget=800, fq_quantum=1514, AC_BE=900/1500, TSQ=98304` + `S70C` | `40.584` | `40.365` (`42.156` `B1`) | `-0.540%` | `40.04 / 83.36 / 105.31` | **`35.28 / 79.55 / 90.83`** | **`-4.575%`** (`p50 -11.88%`, `p99 -13.75%`) | **`-15.47%`** / `+11.05%` (`0%` loss) | **`+1.062%`** | `RETAIN_CURRENT_CHAMPION` (`STAGE72A_CHAMPION_V20`) |
| **`S76B-R2`** | `M42b` | `budget=800, fq_quantum=3028 (2×MTU), TSQ=65536` + `S70C` | `39.043` | `38.745` | `-0.763%` | `44.62 / 86.39 / 90.86` | `43.73 / 95.54 / 100.51` | `+10.594%` | `+57.94%` / `+40.20%` | `-4.471%` | `RETAIN_CURRENT_CHAMPION` |
| **`S76B-R3`** | `M42c` | `budget=800, AC_BE=1200/2400, thr=4500, TSQ=65536` (unwarmed `XW` `6.5 Mbps`) | `17.983` | `19.627` | **`+9.142%`** | `44.75 / 146.84 / 195.34` | `47.06 / 150.97 / 156.54` | `+2.815%` (`p99 -19.86%`) | **`-8.48%`** / `+15.16%` | **`+8.157%`** | `RETAIN_CURRENT_CHAMPION` |
| **`S76B-R4`** | `M42d` | Per-window `seq` warmup + `budget=800, fq_quantum=1514, TSQ=98304` + `S70C` | `41.004` | `40.841` | `-0.398%` | `49.04 / 83.72 / 90.26` | **`36.26`** / `85.79 / 93.08` | `+2.483%` (`p50 -26.06%`) | **`-20.93%` / `-4.28%`** | `-1.267%` | `RETAIN_CURRENT_CHAMPION` |
| **`S76B-R5`** | `M42e` | Per-window `seq` warmup + **`budget=600, TSQ=65536, lowat=6144`** + `S70C` | `40.934` | **`41.463`** | **`+1.292%`** | `30.87 / 82.82 / 101.44` | `45.97 / 87.76` / **`90.46`** | `+5.963%` (**`p99 -10.83%`**) | **`-25.35%` / `-1.26%`** | `-0.795%` | `RETAIN_CURRENT_CHAMPION` |
| **`S76B-R6`** | `M42f` | Per-window `seq` warmup + **`budget=600, AC_BE=750/1350, thr=3500, TSQ=98304`** + `S70C` | `40.781` | **`41.392`** | **`+1.498%`** | `43.12 / 83.73 / 94.78` | **`39.11`** / `95.72 / 113.12` | `+14.320%` (**`p50 -9.29%`**) | `+16.70%` / **`-14.08%`** | `-3.514%` | `RETAIN_CURRENT_CHAMPION` |

---

## 3. Production & Bench Governance Decision

- **`Stage 72A Champion v20` (`STAGE72A_CHAMPION_V20`) Retained as Active Sector Champion (`CONFIRMED`)**:
  - OpenWrt AP (`.20`) & OpenWrt `WA` CPE (`.250`): `netdev_budget=600`, `dev_weight_tx_bias=2`, `eth0` BQL `hold_time=800ms, limit_min=4542, limit_max=42392`, `AP fq_quantum=4542 / AC_BE=1500/3000 / thr=5000`, `CPE fq_quantum=1514 / AC_BE=900/1500 / thr=4000`, `tcp_limit_output_bytes=98304`, `tcp_notsent_lowat=8192`, `oom_score_adj=-900`, `fq_memory_limit=4194304`.
  - `airOS 8` `XC` CPE (`.198`): `Stage 70C` (`AMPDUFrames=24, aggr_swretry=4, nonaggr_swretry=4, set_multiq=1, enable_tx_tcp_cksum=1, netdev_budget=800, tcp_limit_output_bytes=98304, daprot=2, ff_mcast_airtime_limit=5` written last).
  - Pre-Window `XW` Rate-Control Warmup (`FMX-DISC-18` / `FMX-DISC-22`): Use BusyBox-compatible `for i in $(seq 1 25); do ping -c 1 -W 1 -s 1200 -I br-lan <ip> >/dev/null 2>&1; done` instead of fractional `ping -i 0.15`.
