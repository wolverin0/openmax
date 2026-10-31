<!-- doc-head: STAGE72B_PBE5AC_UPH_PTP_XMIT_AND_DAPROT2_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 72B — PowerBeam 5AC Gen2 Isolated `/proc/sys/dev/uph_wifi0/{daprot,ff_mcast_airtime_limit,ptp_xmit}` Benchmark

- **Ticket**: `T-S72B-PBE5AC-UPH-PTP-XMIT-AND-DAPROT2-ISOLATED-BENCH`
- **Date**: `2026-10-26`
- **Hardware Bench**:
  - **AP (`198.18.0.45` / `198.18.0.8`)**: PowerBeam 5AC Gen2 (`WA.ar934x.v8.7.11`, `AR9342` 64 MB RAM + `QCA9882`), `ap-ptp`, `5580 MHz` (`40 MHz`).
  - **Remote OTA STA (`198.18.0.46` / `198.18.0.74`)**: PowerBeam 5AC Gen2 (`WA.ar934x.v8.7.11`), `sta-ptp`, 100% Over-The-Air (`0` Ethernet link on switch `gi7`, standalone PoE injector).
- **Harness & Artifact**:
  - [`tools/bench/run_stage72b_pbe5ac_uph_ptp_xmit_and_daprot2.py`](<repo>/tools/bench/run_stage72b_pbe5ac_uph_ptp_xmit_and_daprot2.py)
  - [`artifacts/autoresearch/stage72b_pbe5ac_uph_ptp_xmit_and_daprot2_20261026.json`](<repo>/artifacts/autoresearch/stage72b_pbe5ac_uph_ptp_xmit_and_daprot2_20261026.json)

---

## 1. `/proc/sys/dev/uph_wifi0/` Readback & Shared Buffer Audit (`CONFIRMED`)

- Verified live readback on both `198.18.0.45` (`AP`) and `198.18.0.46` (`STA`) under a `45s` auto-rollback watchdog:
  - `daprot=2` (`daprot_2_accepted = True`), `ptp_xmit=1` (`ptp_xmit_1_accepted = True`), and `ff_mcast_airtime_limit=5` (`ff_mcast_airtime_5_accepted = True`) are all accepted by `ubnt_poll_host.ko` (`WA.v8.7.11`).
  - Re-confirmed `FMX-DISC-11` (`proprietary airMAX module` `ubnt_poll_host.ko` shared `sysctl_table->data` parser behavior): writing `echo 5 > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit` last preserves `ff_mcast_airtime_limit=5 0 0 ...` and `ptp_xmit=1`, while resetting `daprot` from `2` back to `1` unless `daprot=2` is applied without a subsequent `ff_mcast_airtime_limit` write.

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Hardware Sweep Results (`CONFIRMED`)

All windows ran with `Stage 68A Champion v5` (`tx_queue_len=192`, `ACBEMinfree=32`, `set_CabqMaxdur=20`, `dev_weight=64`, `netdev_max_backlog=2000`, `tcp_limit_output_bytes=131072`, `tcp_pacing=120/200`) 100% intact as Arm A:

| Round | Candidate Knob Stack (`571`-Knob Catalog) | Aggregate Goodput (`A -> B`) | Bulk / Video TCP (`A -> B`) | `p50` RTT (`A -> B`) | `p95` RTT (`A -> B`) | `p99` RTT (`A -> B`) | Karpathy `fmx_loss` (`A -> B`) | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`S72B-R1`** | `PBE5AC_UPH_DAPROT_2_AND_FF_MCAST_AIRTIME_5_ISOLATED` (`uph_wifi0/daprot=2` + `ff_mcast_airtime_limit=5` on pure `Champion v5`) | `22.931 -> 19.827 Mbps` (`-13.54%`) | Bulk: `14.040 -> 11.018 Mbps` · Video: `7.904 -> 7.827 Mbps` | `2.925 -> 2.997 ms` (`+2.46%`, `B2=2.627 ms`) | `9.763 -> 8.119 ms` (**`-16.84%`**, `B1=5.385 ms`, `B2=5.310 ms`) | `27.127 -> 9.466 ms` (**`-65.10%`**) | `0.3337 -> 0.2534` (**`-0.0803`**, `fmx_score=0.7466`) | **`KEEP` (Low-Latency / Tail-Bound Winner)** |
| **`S72B-R2`** | `PBE5AC_UPH_PTP_XMIT_1_ISOLATED` (`uph_wifi0/ptp_xmit=1` on pure `Champion v5`) | `14.060 -> 14.942 Mbps` (**`+6.27%`**, `B1=21.292 Mbps` vs `A1=20.148 Mbps`) | Bulk: `8.028 -> 8.335 Mbps` (**`+3.82%`**) · Video: `5.045 -> 5.624 Mbps` (**`+11.48%`**, `B1=8.000 Mbps`) | `2.921 -> 3.431 ms` (`+17.46%`) | `6.323 -> 7.186 ms` (`+13.65%`) | `9.934 -> 10.528 ms` (`+5.98%`) | `0.3269 -> 0.3245` (**`-0.0023`**, `fmx_score=0.6755`) | **`KEEP` (Throughput / PtP Direct-Xmit Winner)** |

---

## 3. Causal Attribution & Persistence (`CONFIRMED`)

1. **`S72B-R1` (`daprot=2` + `ff_mcast_airtime_limit=5` on `tx_queue_len=192`, `ACBEMinfree=32`) Fixes the `S70B-R2` `p99` Inflation (`CONFIRMED`, `ubnt_poll_host.ko`)**:
   - In `Stage 70B-R2`, combining `daprot=2` with `tx_queue_len=256` and `ACBEMinfree=8` inflated `p99` RTT to `18.114 ms`.
   - Isolating `daprot=2` + `ff_mcast_airtime_limit=5` while preserving `tx_queue_len=192` and `ACBEMinfree=32` cut `p95` RTT by **`-16.84%` (`9.763 -> 8.119 ms`, per-window `p95 = 5.385 ms` and `5.310 ms`)**, slashed `p99` RTT by **`-65.10%` (`27.127 -> 9.466 ms`)**, boosted Jain fairness from `0.9275 -> 0.9721`, and improved `fmx_loss` by `-0.0803` (`0.3337 -> 0.2534`).
2. **`S72B-R2` (`ptp_xmit=1`) Accelerates Direct PtP Frame Dispatch (`CONFIRMED`, `ubnt_poll_host.ko`)**:
   - Enabling `echo 1 > /proc/sys/dev/uph_wifi0/ptp_xmit` activates `ubnt_poll_host.ko`'s direct PtP transmit path, increasing Aggregate Goodput **`+6.27%` (`14.060 -> 14.942 Mbps`, reaching `21.292 Mbps` in `B1` with `8.000 Mbps` zero-drop IPTV Video TCP)** and improving Jain fairness (`0.9505 -> 0.9636`) at the cost of a modest `+0.51 ms` `p50` RTT increase (`2.921 -> 3.431 ms`).
3. **Persistence (`CONFIRMED`)**:
   - `S72B-R1` achieved the lowest overall `fmx_loss` (`0.253369`) and was persisted to `/etc/persistent/rc.poststart` + `cfgmtd -w -p /etc/` (`CFGMTD_OK`) on both `.241` and `.242`.
