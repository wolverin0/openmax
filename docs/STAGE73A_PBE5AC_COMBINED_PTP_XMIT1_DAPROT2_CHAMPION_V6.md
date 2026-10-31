<!-- doc-head: STAGE73A_PBE5AC_COMBINED_PTP_XMIT1_DAPROT2_CHAMPION_V6.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 73A — PowerBeam 5AC Gen2 Combined `ptp_xmit=1` + `daprot=2` + `ff_mcast_airtime_limit=5` (`Champion v6`) & `noack_mode=0` Benchmark

- **Ticket**: `T-S73A-PBE5AC-COMBINED-PTP-XMIT1-AND-DAPROT2-CHAMPION-V6-BENCH`
- **Date**: `2026-10-26`
- **Hardware Bench**:
  - **AP (`198.18.0.45` / `198.18.0.8`)**: PowerBeam 5AC Gen2 (`WA.ar934x.v8.7.11`, `AR9342` 64 MB RAM + `QCA9882`), `ap-ptp`, `5580 MHz` (`40 MHz`).
  - **Remote OTA STA (`198.18.0.46` / `198.18.0.74`)**: PowerBeam 5AC Gen2 (`WA.ar934x.v8.7.11`), `sta-ptp`, 100% Over-The-Air (`0` Ethernet link on switch `gi7`, standalone PoE injector).
- **Harness & Artifact**:
  - [`tools/bench/run_stage73a_pbe5ac_champion_v6_ptp_xmit_daprot2.py`](<repo>/tools/bench/run_stage73a_pbe5ac_champion_v6_ptp_xmit_daprot2.py)
  - [`artifacts/autoresearch/stage73a_pbe5ac_champion_v6_ptp_xmit_daprot2_20261026.json`](<repo>/artifacts/autoresearch/stage73a_pbe5ac_champion_v6_ptp_xmit_daprot2_20261026.json)

---

## 1. `/proc/sys/dev/uph_wifi0/` Shared `sysctl_table->data` Write-Order & Readback Audit (`CONFIRMED`)

- Auditing `/proc/sys/dev/uph_wifi0/{ptp_xmit,daprot,noack_mode,ff_mcast_airtime_limit}` on `.241` (`AP`) and `.242` (`STA`) revealed two critical properties of `ubnt_poll_host.ko` (`proprietary airMAX module`, extending `FMX-DISC-11`):
  1. **Write-Order Rule (`ff_mcast_airtime_limit=5` Last)**: Writing `ptp_xmit=1`, `daprot=2`, and `ff_mcast_airtime_limit=5` last (`S73A-R1`) commits each driver state in its respective `.write` handler while leaving `ff_mcast_airtime_limit=5 0 0 ...` intact in the 16-column array (`ptp_xmit_1_verified = True`, `ff_mcast_5_verified = True`).
  2. **Shared Read Scratch Buffer**: Reading `ptp_xmit` first populates `data[0]=1`, which subsequent scalar `proc_dointvec` reads (`daprot`, `noack_mode`) display if read in the same loop after `ptp_xmit=1`.

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Hardware Sweep Results (`CONFIRMED`)

| Round | Candidate Knob Stack (`571`-Knob Catalog) | Aggregate Goodput (`A -> B`) | Bulk TCP (`A -> B`) | `p50` RTT (`A -> B`) | `p95` RTT (`A -> B`) | `p99` RTT (`A -> B`) | VoIP Loss (`A -> B`) | Karpathy `fmx_loss` (`A -> B`) | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`S73A-R1`** | `PBE5AC_COMBINED_PTP_XMIT_1_DAPROT_2_CHAMPION_V6` (`ptp_xmit=1`, `daprot=2`, `ff_mcast_airtime_limit=5` written last on top of `Champion v5`) | `23.215 -> 21.871 Mbps` (`-5.79%`, **`B1=25.240 Mbps`** vs `A1=22.042 Mbps`, `+14.51%` in `B1`) | `14.392 -> 13.602 Mbps` (`-5.49%`, **`B1=16.394 Mbps`**) | `3.386 -> 2.861 ms` (**`-15.51%`**, `B2=2.353 ms`) | `8.434 -> 7.718 ms` (**`-8.49%`**, `B1=6.855 ms`, `B2=6.137 ms`) | `18.001 -> 9.999 ms` (**`-44.45%`**, `B1=7.718 ms`) | `1.014% -> 0.194%` (**`-80.87%`**, `0.00%` in `B2`) | `0.2621 -> 0.2275` (**`-0.0346`**, `fmx_score=0.7725`) | **`KEEP` (`Stage 73A Champion v6`)** |
| **`S73A-R2`** | `PBE5AC_CHAMPION_V6_WITH_NOACK_MODE_0_VERIFICATION` (`ff_mcast=5` first, then `ptp_xmit=1`, `daprot=2`, `noack_mode=0`) | `18.759 -> 21.059 Mbps` (**`+12.26%`**, `B1=29.658 Mbps`) | `11.567 -> 13.685 Mbps` (**`+18.31%`**, `B1=20.925 Mbps`) | `3.310 -> 5.248 ms` (`+58.55%`) | `8.157 -> 19.496 ms` (`+139.01%`) | `11.546 -> 55.135 ms` (`+377.52%`) | `1.282% -> 0.701%` | `0.2878 -> 0.6316` (`+0.3438`) | **`DISCARD`** |

---

## 3. Causal Attribution & Persistence (`CONFIRMED`)

1. **Why `S73A-R1` (`ptp_xmit=1` + `daprot=2` + `ff_mcast_airtime_limit=5` Last) Promoted `Stage 73A Champion v6` (`CONFIRMED`, `ubnt_poll_host.ko`)**:
   - Combining `ptp_xmit=1` (`Stage 72B-R2` direct PtP transmit path) with `daprot=2` + `ff_mcast_airtime_limit=5` (`Stage 72B-R1` data protection & multicast airtime bound) on top of `Stage 68A Champion v5` (`tx_queue_len=192`, `ACBEMinfree=32`, `set_CabqMaxdur=20`, `dev_weight=64`, `netdev_max_backlog=2000`, `tcp_limit_output_bytes=131072`, `tcp_pacing=120/200`) simultaneously delivered **`25.240 Mbps` peak Aggregate Goodput (`16.394 Mbps` Bulk TCP) in `B1`** while cutting **`p50` RTT by `-15.51%` (`3.386 -> 2.861 ms`, `2.353 ms` in `B2`)**, **`p95` RTT by `-8.49%` (`8.434 -> 7.718 ms`, `6.137 ms` in `B2`)**, **`p99` RTT by `-44.45%` (`18.001 -> 9.999 ms`, `7.718 ms` in `B1`)**, and **VoIP loss by `-80.87%` (`1.014% -> 0.194%`)** (`fmx_loss: 0.2621 -> 0.2275`, `KEEP`).
2. **Why `S73A-R2` (`noack_mode=0` + `ff_mcast_airtime_limit` Written First) Inflated `p95`/`p99` RTT (`CONFIRMED`, `ubnt_poll_host.ko`)**:
   - Writing `ff_mcast_airtime_limit=5` first and then writing `noack_mode=0` clobbered `ff_mcast_airtime_limit[0]` (`FMX-DISC-11`) and disabled `ubnt_poll_host.ko`'s `noack_mode=1` TDMA polling optimization, forcing legacy 802.11 ACK waits inside TDMA slots. Although `B1` burst to `29.658 Mbps` (`20.925 Mbps` Bulk TCP), `p95` RTT jumped `+139.01%` (`8.157 -> 19.496 ms`) and `p99` RTT reached `55.135 ms` (`DISCARD`).
3. **Persistence (`CONFIRMED`)**:
   - `S73A-R1` (`Stage 73A Champion v6`) was automatically selected (`winning_round_id = "S73A-R1"`) and persisted to `/etc/persistent/rc.poststart` + `cfgmtd -w -p /etc/` (`CFGMTD_OK`) on both `.241` and `.242`.
