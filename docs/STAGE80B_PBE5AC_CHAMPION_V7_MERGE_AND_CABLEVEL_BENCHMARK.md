<!-- doc-head: STAGE80B_PBE5AC_CHAMPION_V7_MERGE_AND_CABLEVEL_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 80B: PowerBeam 5AC Gen2 `Stage 79A Champion v7` Packager Merge, `ATHDEV-BUG-02` `CABlevel`/`ol_ath` Boundary Audit & `Burst:4500` Fine-Grid Benchmark

- **Ticket**: `T-S80B-PROMOTE-PBE5AC-CHAMPION-V7-AND-ATHDEV-CABLEVEL-BENCH`
- **Date**: `2026-10-26`
- **Bench Topology**: `198.18.0.45` (`198.18.0.8`, `PBE-5AC-Gen2` AP, `airOS 8 WA.v8.7.11`) $\leftrightarrow$ `198.18.0.46` (`198.18.0.74`, `PBE-5AC-Gen2` STA, `airOS 8 WA.v8.7.11`)
- **Incumbent Baseline (`Arm A`)**: `Stage 79A Champion v7` (`STAGE79A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V7` / `S79A-R1-PTP-CHAMPION-V7`: `set_multiq=3` [`0x1 | 0x2` `UMAC-BUG-01`], `timing='200 200 5000'` $\rightarrow$ `Down:200, Up:200, Burst:5000`, `ptp_xmit=1`, `daprot=2`, `ff_mcast_airtime_limit=5` written last)
- **Artifact**: [`artifacts/autoresearch/stage80b_pbe5ac_champion_v7_merge_and_cablevel_20261026.json`](../artifacts/autoresearch/stage80b_pbe5ac_champion_v7_merge_and_cablevel_20261026.json)

---

## 1. Central Production Deploy Packager Merge (`Stage 79A Champion v7`)

Merged `STAGE79A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V7` (`S79A-R1-PTP-CHAMPION-V7`), `STAGE79A_AIROS8_PTP_CHAMPION_V7_COMMANDS` (`43` commands), and `render_stage79a_airos8_ptp_champion_v7_script()` (`46` lines) into:
1. [`controller/stage34c_ltu_4096qam_deploy_packager.py`](../controller/stage34c_ltu_4096qam_deploy_packager.py)
2. [`controller/guarida_stage29b_deploy_packager.py`](../controller/guarida_stage29b_deploy_packager.py)
3. [`tools/deploy/guarida_stage29b_deploy_packager.py`](../tools/deploy/guarida_stage29b_deploy_packager.py)

All `STAGE73A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V6`, `STAGE68A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V5`, and `STAGE62A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V4` exports remain intact for 100% backwards compatibility (`stage79a_airos8_ptp_v7_verified=True`, `all_safety_checks_passed=True`).

---

## 2. Live Silicon Audit of `ATHDEV-BUG-02` (`CABlevel` vs `ol_ath` Boundary), Linux `3.3.8` TCP Sysctls & `Burst:4500` (`CONFIRMED`)

1. **`ath_dev.ko` Direct-Attach vs `umac.ko` `ol_ath` (`QCA9882` Offload) Boundary (`CONFIRMED`, `proprietary airMAX module` `ath_dev.ko` / `umac.ko`)**:
   - On `WA.v8.7.11` (`QCA9882` PCIe offload radio `wifi0`), `iwpriv wifi0 CABlevel 15` (`0x1012` $\rightarrow$ `ath_cabq_update` `0x016908`) returns `Invalid command : CABlevel` because `wifi0`'s WEXT table is bound to `umac.ko`'s `ol_ath` offload handler, while `ath_dev.ko` exposes `/sys/module/ath_dev/parameters/CABMinfree=48` (`ACVOMinfree=0`, `ACVIMinfree=16`, `ACBEMinfree=32`, `ACBKMinfree=48`) and `ubnt_poll_host.ko` governs multicast/CAB airtime via `/proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit=5`.
   - On `WA.v8.7.11` (`Linux 3.3.8`), `/proc/sys/net/ipv4/tcp_notsent_lowat` (Linux `3.12+`) and `tcp_limit_output_bytes` (Linux `3.6+`) do not exist (`FMX-DISC-04`); active TCP burst/window sysctls in `/proc/sys/net/ipv4/` are `tcp_tso_win_divisor`, `tcp_low_latency`, `tcp_wmem`, `tcp_rmem`, `tcp_sack`, `tcp_dsack`, and `tcp_ecn`.
2. **Fine-Grid TDMA Burst Ceiling (`echo '200 200 4500' > /proc/sys/dev/uph_wifi0/timing`, `CONFIRMED`, `ubnt_poll_host.ko` + `QCA firmware`)**:
   - Kernel & QCA9882 Target Log readback:
     - `[46107.863000] ubnt_poll_host: wifi0 Timings set to down:200 up:200 burst:4500, noack=0`
     - `[46107.863000] ubnt_poll_host TARGET LOG: ubnt_poll: Timing params set to Down:200, Up:200, Burst:4500`

---

## 3. Counterbalanced `A1 -> B1 -> A2 -> B2` Hardware Benchmark Results (`8` Windows)

| Round | Candidate (`Arm B`) vs `Champion v7` (`Arm A`) | Arm A Agg / Bulk Goodput | Arm B Agg / Bulk Goodput ($\Delta\%$) | Arm A `p50` / `p95` / `p99` RTT | Arm B `p50` / `p95` / `p99` RTT | `fmx_loss` (`A -> B`) | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S80B-R1`** | `Champion v7` + `CABlevel=15` + `tcp_notsent_lowat=16384` | **`19.632` / `11.229 Mbps`** (`A1=21.833`, `A2=17.431`) | `17.486` (`-10.93%`) / `8.995 Mbps` (`-19.89%`) | **`2.606`** / `14.911` / `26.381 ms` | `2.816` (`+8.06%`) / **`7.729` (`-48.17%`)** / **`8.430 ms`** | `0.4269 -> 0.2764` (`-0.1505`) | **`DISCARD` (GP Floor Guard)** |
| **`S80B-R2`** | `Champion v7` + `timing='200 200 4500'` (`Down:200, Up:200, Burst:4500`) | **`18.387` / `10.230 Mbps`** (`A1=18.388`, `A2=18.385`) | `17.767` (`-3.37%`) / `9.270 Mbps` (`-9.38%`) | **`2.529` / `5.415` / `11.439 ms`** | `3.357` (`+32.74%`) / `7.888` (`+45.67%`) / `20.441 ms` | **`0.2600 -> 0.3461` (`+0.0861`)** | **`DISCARD`** |

---

## 4. Complete 4-Point TDMA Burst Duration Pareto Curve (`Down:200, Up:200`)

Across Stages `74A`, `77B`, `79A`, and `80B`, we have now mapped the complete 4-point TDMA burst ceiling curve (`4000 us`, `4500 us`, `5000 us`, `6000 us`) at `Down:200, Up:200` on live `PBE-5AC-Gen2` silicon:
- **`Burst:4000` (`Stage 77B-R2`)**: `20.526 Mbps`, `p50=2.515 ms`, `p95=6.141 ms`, `p99=15.393 ms` (`fmx_loss=0.2595`, `DISCARD`).
- **`Burst:4500` (`Stage 80B-R2`)**: `17.767 Mbps` (`-3.37%`), `p50=3.357 ms` (`+32.74%`), `p95=7.888 ms` (`+45.67%`), `p99=20.441 ms` (`fmx_loss=0.3461`, `DISCARD`).
- **`Burst:5000` + `set_multiq=3` (`Stage 79A-R1 Champion v7`)**: **`21.268 Mbps` (`+5.33%`), `p50=2.494 ms` (`-10.51%`), `p95=5.107 ms` (`-29.76%`), `p99=5.301 ms` (`-31.98%`, `fmx_loss=0.1785`, GLOBAL PARETO OPTIMUM)**.
- **`Burst:6000` (`Stage 73A-R1 Champion v6`)**: `20.191 Mbps`, `p50=2.787 ms`, `p95=7.271 ms`, `p99=7.793 ms` (`fmx_loss=0.2296`).

**Retained & Persisted Champion**: `Stage 79A Champion v7` (`S79A-R1`: `set_multiq=3`, `timing='200 200 5000'`, `ptp_xmit=1`, `daprot=2`, `ff_mcast_airtime_limit=5` last) re-verified and persisted (`CFGMTD_OK` on `.241` and `.242`).
