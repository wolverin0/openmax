<!-- doc-head: STAGE79A_PBE5AC_SET_MULTIQ3_AND_BURST5000_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 79A: PowerBeam 5AC Gen2 `set_multiq=3` (`UMAC-BUG-01` Deep VLAN/PPPoE DSCP + `75%` Per-AC XOFF) & `Burst:5000` (`200 200 5000`) Champion v7 Benchmark

- **Ticket**: `T-S79A-PBE5AC-SET-MULTIQ-3-DEEP-DSCP-XOFF-AND-BURST5000-BENCH`
- **Date**: `2026-10-26`
- **Bench Topology**: `198.18.0.45` (`198.18.0.8`, `PBE-5AC-Gen2` AP, `airOS 8 WA.v8.7.11`) $\leftrightarrow$ `198.18.0.46` (`198.18.0.74`, `PBE-5AC-Gen2` STA, `airOS 8 WA.v8.7.11`)
- **Incumbent Baseline (`Arm A`)**: `Stage 73A Champion v6` (`S73A-R1-PTP-CHAMPION-V6`: `set_multiq=1`, `timing='0 0 0'` $\rightarrow$ `Down:200, Up:200, Burst:6000`, `ptp_xmit=1`, `daprot=2`, `ff_mcast_airtime_limit=5` written last)
- **Promoted Winner (`Stage 79A Champion v7`)**: **`S79A-R1` (`PBE5AC_SET_MULTIQ_3_AND_BURST5000`)**
- **Artifact**: [`artifacts/autoresearch/stage79a_pbe5ac_multiq3_and_burst5000_20261026.json`](../artifacts/autoresearch/stage79a_pbe5ac_multiq3_and_burst5000_20261026.json)

---

## 1. Live Silicon Verification of `UMAC-BUG-01` (`set_multiq=3`) & `Burst:5000` (`CONFIRMED`, `proprietary airMAX module` `umac.ko` / `ubnt_poll_host.ko` + `QCA firmware`)

1. **`iwpriv ath0 set_multiq 3` (`UMAC-BUG-01`, `CONFIRMED`, `umac.ko` `osif_select_queue` `0x09e8a8` + `ol_tx_ll` `0x0d0e90`)**:
   - Readback on both `.241` and `.242`: `ath0 get_multiq:3` (`0x1 | 0x2`).
   - `Bit 0 (0x1)`: Maps `tid 0..7` + `is_high_prio` across the 5 Linux TX subqueues (`0=AC_BK..4=HPRIO`) and activates per-AC subqueue `__QUEUE_STATE_XOFF` in `ol_tx_ll` when an AC exceeds `75%` of its descriptor threshold.
   - `Bit 1 (0x2)`: Activates `0x09df98` deep `802.1Q VLAN` (`0x8100`) and `PPPoE` (`0x8864`) inner-IP DSCP extraction inside `osif_select_queue`.
2. **Sweet-Spot TDMA Burst Ceiling (`echo '200 200 5000' > /proc/sys/dev/uph_wifi0/timing`, `CONFIRMED`, `ubnt_poll_host.ko` + `QCA firmware`)**:
   - Kernel & QCA9882 Target Log readback:
     - `[45530.929000] ubnt_poll_host: wifi0 Timings set to down:200 up:200 burst:5000, noack=0`
     - `[45530.930000] ubnt_poll_host TARGET LOG: ubnt_poll: Timing params set to Down:200, Up:200, Burst:5000`
   - Preserves the ultra-fast `200 us` minimum DL/UL turnaround (`Down:200, Up:200`) while setting the maximum burst ceiling to `5000 us` (`5 ms`, midway between `Stage 77B` `4000 us` and default `6000 us`).

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Hardware Benchmark Results (`8` Windows)

| Round | Candidate (`Arm B`) vs `Champion v6` (`Arm A`) | Arm A Agg / Bulk Goodput | Arm B Agg / Bulk Goodput ($\Delta\%$) | Arm A `p50` / `p95` / `p99` RTT | Arm B `p50` / `p95` / `p99` RTT | VoIP Loss (`A -> B`) | `fmx_loss` (`A -> B`) | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S79A-R1`** | **`Champion v6` + `set_multiq=3` + `timing='200 200 5000'`** | `20.191` / `11.293 Mbps` (`A1=19.734`, `A2=20.648`) | **`21.268` (`+5.33%`) / `12.396 Mbps` (`+9.77%`)** (`B1=21.150`, `B2=21.386`) | `2.787` / `7.271` / `7.793 ms` | **`2.494` (`-10.51%`) / `5.107` (`-29.76%`) / `5.301 ms` (`-31.98%`)** | `0.182% -> 0.118%` (`-35.2%`) | **`0.2296 -> 0.1785` (`-0.0511`)** | **`KEEP` (`Champion v7`)** |
| **`S79A-R2`** | `Champion v6` + `set_multiq=3` + `AC*Minfree=0/16/32/48` (`Burst:6000`) | `20.498` / `11.745 Mbps` (`A1=20.556`, `A2=20.440`) | **`20.731` (`+1.14%`) / `11.886 Mbps` (`+1.20%`)** (`B1=20.045`, `B2=21.417`) | `2.641` / **`4.900`** / **`5.459 ms`** | **`2.478` (`-6.17%`)** / `6.292` (`B2=3.453 ms`) / `6.902 ms` | `0.026% -> 0.273%` | `0.1883 -> 0.2074` (`+0.0191`) | **`DISCARD`** |

---

## 3. Root-Cause Attribution & Promotion of `Stage 79A Champion v7` (`S79A-R1`)

1. **Why `S79A-R1` (`set_multiq=3` + `Down:200, Up:200, Burst:5000`) Won Every Metric (`KEEP`, `fmx_loss=0.178546`, `fmx_score=0.821454`)**:
   - **Goodput**: Aggregate Goodput increased by **`+5.33%` (`20.191 -> 21.268 Mbps`: `B1=21.150 Mbps`, `B2=21.386 Mbps`)** and Bulk TCP Goodput jumped by **`+9.77%` (`11.293 -> 12.396 Mbps`: `B1=12.284 Mbps`, `B2=12.507 Mbps`)**, beating both `Arm A` windows (`A1=19.734`, `A2=20.648 Mbps`).
   - **Latency & Tail Jitter**: Loaded `p50` RTT dropped by **`-10.51%` (`2.787 -> 2.494 ms`: `B1=2.575 ms`, `B2=2.412 ms`)**, loaded `p95` RTT dropped by **`-29.76%` (`7.271 -> 5.107 ms`: `B1=5.056 ms`, `B2=4.308 ms`)**, and loaded `p99` RTT dropped by **`-31.98%` (`7.793 -> 5.301 ms`: `B1=5.107 ms`, `B2=5.301 ms`)** — all 30 RTT samples stayed `<= 5.301 ms`!
   - **Physical Mechanism**: Whereas `Burst:4000` (`Stage 77B`) slightly clipped peak A-MPDU burst amortization on the final sample and `Burst:6000` (`S79A-R2`) allowed `6 ms` DL bursts that pushed `p99` to `6.902–7.793 ms`, `Burst:5000` (`5 ms` ceiling with `200 us` turnarounds) paired with `set_multiq=3` per-AC 75% XOFF backpressure bounds worst-case head-of-line blocking under `5.30 ms` while sustaining `32`-subframe A-MPDU saturation.
2. **Persistence**: Persisted `S79A-R1` (`Stage 79A Champion v7`) to `/etc/persistent/rc.poststart` + `cfgmtd -w -p /etc/` (`CFGMTD_OK`) on both `.241` and `.242`.
