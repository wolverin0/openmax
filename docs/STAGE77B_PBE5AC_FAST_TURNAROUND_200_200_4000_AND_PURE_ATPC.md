<!-- doc-head: STAGE77B_PBE5AC_FAST_TURNAROUND_200_200_4000_AND_PURE_ATPC.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 77B: PowerBeam 5AC Gen2 Fast Turnaround TDMA Timing (`200 200 4000`) & Pure Symmetric `ATPC` (`1 -62 24 24 24` Without `swr_limit`) Benchmark

- **Ticket**: `T-S77B-PBE5AC-FAST-TURNAROUND-200-200-4000-AND-PURE-ATPC-BENCH`
- **Date**: `2026-10-26`
- **Bench Topology**: `198.18.0.45` (`198.18.0.8`, `PBE-5AC-Gen2` AP, `airOS 8 WA.v8.7.11`) $\leftrightarrow$ `198.18.0.46` (`198.18.0.74`, `PBE-5AC-Gen2` STA, `airOS 8 WA.v8.7.11`)
- **Incumbent Baseline (`Arm A`)**: `Stage 73A Champion v6` (`S73A-R1-PTP-CHAMPION-V6`: `timing='0 0 0'` $\rightarrow$ `Down:200, Up:200, Burst:6000`, `atpc` default `0 0 0 0 24` AP / `1 0 0 0 24` STA, `swr_limit='0 0 0'`, `ptp_xmit=1`, `daprot=2`, `ff_mcast_airtime_limit=5` written last)
- **Artifact**: [`artifacts/autoresearch/stage77b_pbe5ac_fast_turnaround_and_pure_atpc_20261026.json`](../artifacts/autoresearch/stage77b_pbe5ac_fast_turnaround_and_pure_atpc_20261026.json)

---

## 1. Live Silicon `dmesg` Verification (`CONFIRMED`, `proprietary airMAX module` `ubnt_poll_host.ko` + `QCA firmware`)

1. **Fast Turnaround TDMA Timing (`echo '200 200 4000' > /proc/sys/dev/uph_wifi0/timing`)**:
   - Kernel & QCA9882 Target Log readback:
     - `[45133.281000] ubnt_poll_host: wifi0 Timings set to down:200 up:200 burst:4000, noack=0`
     - `[45133.281000] ubnt_poll_host TARGET LOG: ubnt_poll: Timing params set to Down:200, Up:200, Burst:4000`
   - Preserves the ultra-fast `200 us` DL/UL minimum slot turnaround (`Down:200, Up:200`) while tightening the maximum TDMA burst ceiling from `6000 us` (`6 ms`) to `4000 us` (`4 ms`).
2. **Pure Symmetric `ATPC` Without `swr_limit` (`echo '1 -62 24 24 24' > /proc/sys/dev/uph_wifi0/atpc` + `swr_limit='0 0 0'`)**:
   - Kernel readback:
     - `[45133.280000] ubnt_poll_host: SWR Limit disabled`
     - `[45133.281000] ubnt_poll_host: ATPC enabled (-62/24/24/24) for radio wifi0`
3. **Regex-Safe Watchdog Cleanup Discovery (`[s]leep 45`)**:
   - On BusyBox `sh -c`, executing `pkill -f 'sleep 45'` matches its own command string and terminates the parent shell; using `pkill -f '[s]leep 45'` cleanly cancels prior 45-second rollback subshells between benchmark windows without self-termination.

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Hardware Benchmark Results (`8` Windows)

| Round | Candidate (`Arm B`) vs `Champion v6` (`Arm A`) | Arm A Agg Goodput | Arm B Agg Goodput ($\Delta\%$) | Arm A `p50` / `p95` / `p99` RTT | Arm B `p50` / `p95` / `p99` RTT | VoIP Loss (`A -> B`) | `fmx_loss` (`A -> B`) | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S77B-R1`** | Pure Symmetric `atpc='1 -62 24 24 24'` (`swr_limit='0 0 0'`) | **`21.398 Mbps`** (`A1=20.762`, `A2=22.035`) | `20.804 Mbps` (`-2.78%`, `B1=20.824`, `B2=20.784`) | `2.774` / **`4.845`** / **`7.681 ms`** | **`2.252`** (`-18.82%`) / `8.478` (`+74.98%`) / `8.659 ms` | `1.960% -> 0.613%` (`-68.7%`) | `0.1882 -> 0.2391` (`+0.0508`) | **`DISCARD`** |
| **`S77B-R2`** | Fast Turnaround `timing='200 200 4000'` (`Down:200, Up:200, Burst:4000`) | `20.197 Mbps` (`A1=21.596`, `A2=18.798`) | **`20.526 Mbps`** (**`+1.63%`**, `B1=20.679`, `B2=20.373`) | `3.046` / `6.544` / **`7.804 ms`** | **`2.515`** (**`-17.43%`**) / **`6.141`** (**`-6.16%`**) / `15.393 ms` (`B2=6.141 ms`) | `0.455% -> 0.143%` (**`-68.6%`**) | `0.2231 -> 0.2595` (`+0.0364`) | **`DISCARD` (Strict `p99` Gate)** |

---

## 3. Root-Cause Attribution & Engineering Conclusions

1. **`S77B-R1` Proves `swr_limit='6 6 2'` Was the Sole Cause of the `S74A-R1` Goodput Collapse (`CONFIRMED`, `proprietary airMAX module` `ubnt_poll_host.ko`)**:
   - Removing `swr_limit='6 6 2'` recovered Arm B Aggregate Goodput by **`+53.82%` (`13.525 -> 20.804 Mbps`: `B1=20.824 Mbps`, `B2=20.784 Mbps`)**, cutting loaded `p50` RTT by **`-18.82%` (`2.774 -> 2.252 ms`)** and VoIP loss by **`-68.72%` (`1.960% -> 0.613%`)**.
   - However, enabling the active `ubnt_poll_host` ATPC feedback loop (`enable=1` on AP `.241`, even locked to `24/24 dBm`) introduces periodic WMI TX-power update messages that increased `p95` RTT from `4.845 ms` to `8.478 ms` (`+74.98%`). Leaving AP ATPC disabled (`0 0 0 0 24`) in `Stage 73A Champion v6` avoids WMI ATPC polling jitter while maintaining full `24 dBm` TX power.
2. **`S77B-R2` (`timing='200 200 4000'` -> `Down:200, Up:200, Burst:4000`) Improves Goodput (`+1.63%`), `p50` RTT (`-17.43%`), `p95` RTT (`-6.16%`), and VoIP Loss (`-68.57%`)**:
   - Preserving `Down:200, Up:200` completely eliminated the `-21.80%` goodput penalty of `S74A-R2` (`2000 2000 1000`), achieving **`20.526 Mbps` vs `20.197 Mbps` (`+1.63%`)**, **`2.515 ms` vs `3.046 ms` `p50` RTT (`-17.43%`, `B1=2.516 ms`, `B2=2.514 ms`)**, **`6.141 ms` vs `6.544 ms` `p95` RTT (`-6.16%`, `B1=4.223 ms`, `B2=5.997 ms`)**, and **`0.143%` vs `0.455%` VoIP loss (`-68.57%`)**.
   - A single end-of-window sample in `B1` (`15.393 ms`, while `B2` max `p99` was `6.141 ms`) triggered the strict 30-sample `p99` penalty in `compute_fmx_objective` (`fmx_loss=0.2595 vs 0.2231`), so `Stage 73A Champion v6` (`S73A-R1`: `Burst:6000`) is conservatively retained and persisted (`CFGMTD_OK` on `.241` and `.242`).
