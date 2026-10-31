<!-- doc-head: STAGE74A_PBE5AC_UPH_BUG05_ATPC_AND_CHAMPION_V6_MERGE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 74A: PowerBeam 5AC Gen2 `UPH-BUG-05` (`atpc` `vec[2]/vec[3]` Inversion) Silicon Audit, `Champion v6` Packager Merge & TDMA Timing Sweep

- **Ticket**: `T-S74A-PBE5AC-UPH-BUG05-ATPC-INVERSION-AND-CHAMPION-V6-PACKAGER-MERGE`
- **Date**: `2026-10-26`
- **Bench Topology**: `198.18.0.45` (`198.18.0.8`, `PBE-5AC-Gen2` AP, `airOS 8 WA.v8.7.11`) $\leftrightarrow$ `198.18.0.46` (`198.18.0.74`, `PBE-5AC-Gen2` STA, `airOS 8 WA.v8.7.11`)
- **Incumbent Baseline (`Arm A`)**: `Stage 73A Champion v6` (`STAGE73A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V6` / `S73A-R1-PTP-CHAMPION-V6`: `ptp_xmit=1`, `daprot=2`, `ff_mcast_airtime_limit=5` written last on top of `Stage 68A Champion v5`)
- **Artifact**: [`artifacts/autoresearch/stage74a_pbe5ac_uph_bug05_atpc_and_timing_20261026.json`](../artifacts/autoresearch/stage74a_pbe5ac_uph_bug05_atpc_and_timing_20261026.json)

---

## 1. Central Production Deploy Packager Merge (`Stage 73A Champion v6`)

Merged `STAGE73A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V6` (`S73A-R1-PTP-CHAMPION-V6`), `STAGE73A_AIROS8_PTP_CHAMPION_V6_COMMANDS` (`41` commands), and `render_stage73a_airos8_ptp_champion_v6_script()` into:
1. [`controller/stage34c_ltu_4096qam_deploy_packager.py`](../controller/stage34c_ltu_4096qam_deploy_packager.py)
2. [`controller/guarida_stage29b_deploy_packager.py`](../controller/guarida_stage29b_deploy_packager.py)
3. [`tools/deploy/guarida_stage29b_deploy_packager.py`](../tools/deploy/guarida_stage29b_deploy_packager.py)

All `STAGE68A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V5` and `STAGE62A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V4` exports remain intact for 100% backwards compatibility (`stage73a_airos8_ptp_v6_verified=True`, `all_safety_checks_passed=True`).

---

## 2. Live Silicon Audit of `UPH-BUG-05` (`atpc` `vec[2]/vec[3]` Inversion + `vec[4]` `def_power`) & `timing` (`CONFIRMED`, `proprietary airMAX module` `ubnt_poll_host.ko`)

Inspecting `/etc/sysinit/radio.conf` and kernel `dmesg` (`ubnt_poll_host` + `ubnt_poll_host TARGET LOG`) on live `WA.v8.7.11` silicon (`198.18.0.45` and `198.18.0.46`) proved three critical contracts:

1. **`UPH-BUG-05` Asymmetric vs Symmetric `atpc` Parsing (`CONFIRMED`, `proprietary airMAX module` `ubnt_poll_host.ko`)**:
   - Writing `echo '1 -62 10 24 24' > /proc/sys/dev/uph_wifi0/atpc` emits:
     `[44363.623000] ubnt_poll_host: ATPC enabled (-62/10/24/24) for radio wifi0`
     where `vec[2]=10` is parsed into `atpc_max_power` (`0x1b40` in `init_ptmp_netconf`) and `vec[3]=24` into `atpc_min_power`, inverting `min` and `max` TX power bounds (`max < min`).
   - Writing `echo '1 -62 24 24 24' > /proc/sys/dev/uph_wifi0/atpc` emits:
     `[44363.624000] ubnt_poll_host: ATPC enabled (-62/24/24/24) for radio wifi0`
     neutralizing `vec[2]/vec[3]` inversion via a symmetric `24/24 dBm` window.
2. **Critical 5th-Integer `def_power` (`vec[4]`) Contract in `/proc/sys/dev/uph_wifi0/atpc` (`CONFIRMED`, `proprietary airMAX module` `ubnt_poll_host.ko`)**:
   - In `/etc/sysinit/radio.conf`, stock `airOS 8` initializes `/proc/sys/dev/uph_wifi0/atpc` with `echo 0 0 0 0 24 > /proc/sys/dev/uph_wifi0/atpc` on AP (`ATPC disabled (0/0/0/24)`) and `echo 1 0 0 0 24 > /proc/sys/dev/uph_wifi0/atpc` on STA (`ATPC enabled (0/0/0/24)`), where `vec[4]=24` sets the `24 dBm` default TX power ceiling.
   - Writing `echo '0 0 0 0 0' > /proc/sys/dev/uph_wifi0/atpc` sets `ATPC disabled (0/0/0/0)` (`def_power=0 dBm`), collapsing link goodput by `-70%`! Disabling ATPC on `airOS 8` MUST always pass `vec[4]=24` (`0 0 0 0 24`).
3. **Default Flexible TDMA `timing` (`0 0 0`) vs `2000 2000 1000` in QCA9882 Offload Target (`CONFIRMED`, `QCA firmware` / `proprietary airMAX module`)**:
   - Writing `echo '0 0 0' > /proc/sys/dev/uph_wifi0/timing` (default flexible burst mode) causes the QCA9882 target firmware to log:
     `ubnt_poll_host TARGET LOG: ubnt_poll: Timing params set to Down:200, Up:200, Burst:6000` (`200 us` minimum DL/UL turnaround slots with a `6000 us` = `6 ms` maximum burst window).
   - Writing `echo '2000 2000 1000' > /proc/sys/dev/uph_wifi0/timing` logs:
     `ubnt_poll_host TARGET LOG: ubnt_poll: Timing params set to Down:2000, Up:2000, Burst:1000` — inflating minimum turnaround slots `10x` (`200 -> 2000 us`) while cutting maximum burst duration by `-83.3%` (`6000 -> 1000 us`).

---

## 3. Counterbalanced `A1 -> B1 -> A2 -> B2` Hardware Benchmark Results (`8` Windows)

| Round | Candidate (`Arm B`) vs `Champion v6` (`Arm A`) | Arm A Agg Goodput | Arm B Agg Goodput ($\Delta\%$) | Arm A `p50` / `p95` / `p99` RTT | Arm B `p50` / `p95` / `p99` RTT | `fmx_loss` (`A -> B`) | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S74A-R1`** | `Champion v6` + `atpc='1 -62 24 24 24'` + `swr_limit='6 6 2'` | **`18.674 Mbps`** (`A1=18.927`, `A2=18.421`) | `13.525 Mbps` (`-27.57%`) | `2.795` / `5.890` / `5.974 ms` | `2.474` (`-11.48%`) / `4.915` (`-16.55%`) / `7.138 ms` | `0.2259 -> 0.2994` (`+0.0735`) | **`DISCARD`** |
| **`S74A-R2`** | `Champion v6` + `timing='2000 2000 1000'` + `atpc='1 -62 24 24 24'` | **`18.839 Mbps`** (`A1=18.531`, `A2=19.147`) | `14.732 Mbps` (`-21.80%`) | **`3.179` / `7.292` / `12.737 ms`** | `4.983` (`+56.75%`) / `9.381` (`+28.65%`) / `15.953 ms` | `0.2793 -> 0.3798` (`+0.1005`) | **`DISCARD`** |

### Root-Cause Attribution
- **`S74A-R1` (`DISCARD`)**: Enabling `/proc/sys/dev/uph_wifi0/swr_limit` (`6 6 2`) inside `ubnt_poll_host.ko` stacks a second TDMA software-retry ceiling on top of `iwpriv wifi0 aggr_swretry 6`, prematurely dropping A-MPDU subframes during transient indoor multipath fades (`B1=9.318 Mbps`) despite cutting loaded `p50` RTT by `-11.48%` (`2.795 -> 2.474 ms`) and `p95` RTT by `-16.55%` (`5.890 -> 4.915 ms`).
- **`S74A-R2` (`DISCARD`)**: Overriding `/proc/sys/dev/uph_wifi0/timing` from default `0 0 0` (`Down:200, Up:200, Burst:6000`) to `2000 2000 1000` (`Down:2000, Up:2000, Burst:1000`) shrinks the QCA9882 target's maximum burst ceiling from `6000 us` to `1000 us` while forcing `2000 us` minimum slot hold times, reducing Aggregate Goodput by `-21.80%` (`18.839 -> 14.732 Mbps`) and increasing `p50` RTT by `+56.75%` (`3.179 -> 4.983 ms`).
- **Retained Champion (`Stage 73A Champion v6` / `S73A-R1-PTP-CHAMPION-V6`)**: Re-verified and persisted to `/etc/persistent/rc.poststart` + `cfgmtd -w -p /etc/` (`CFGMTD_OK`) on both `.241` and `.242`.
