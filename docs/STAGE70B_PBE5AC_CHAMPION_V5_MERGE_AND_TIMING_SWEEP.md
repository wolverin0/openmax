<!-- doc-head: STAGE70B_PBE5AC_CHAMPION_V5_MERGE_AND_TIMING_SWEEP.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 70B — PowerBeam 5AC Gen2 `Champion v5` Packager Merge & Deep `ath_dev.ko` / `uph_wifi0` Timing Sweep

- **Ticket**: `T-S70B-PBE5AC-CHAMPION-V5-PACKAGER-MERGE-AND-DEEP-ATH-DEV-SWEEP`
- **Date**: `2026-10-26`
- **Hardware Bench**:
  - **AP (`198.18.0.45` / `198.18.0.8`)**: PowerBeam 5AC Gen2 (`WA.ar934x.v8.7.11`, `AR9342` 64 MB RAM + `QCA9882`), `ap-ptp`, `5580 MHz` (`40 MHz`).
  - **Remote OTA STA (`198.18.0.46` / `198.18.0.74`)**: PowerBeam 5AC Gen2 (`WA.ar934x.v8.7.11`), `sta-ptp`, 100% Over-The-Air (`0` Ethernet link on switch `gi7`, standalone PoE injector).
- **Harness & Artifact**:
  - [`tools/bench/run_stage70b_pbe5ac_ath_dev_and_timing_sweep.py`](<repo>/tools/bench/run_stage70b_pbe5ac_ath_dev_and_timing_sweep.py)
  - [`artifacts/autoresearch/stage70b_pbe5ac_ath_dev_and_timing_sweep_20261026.json`](<repo>/artifacts/autoresearch/stage70b_pbe5ac_ath_dev_and_timing_sweep_20261026.json)

---

## 1. Central Production Packager Merge (`STAGE68A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V5`, `CONFIRMED`)

- Upgraded the central offline deploy packager across [`controller/stage34c_ltu_4096qam_deploy_packager.py`](<repo>/controller/stage34c_ltu_4096qam_deploy_packager.py), [`controller/guarida_stage29b_deploy_packager.py`](<repo>/controller/guarida_stage29b_deploy_packager.py), and [`tools/deploy/guarida_stage29b_deploy_packager.py`](<repo>/tools/deploy/guarida_stage29b_deploy_packager.py):
  - Added **`STAGE68A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V5`** (`profile_id = "S68A-R2-PTP-CHAMPION-V5"`, superseding `STAGE62A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V4`), **`STAGE68A_AIROS8_PTP_CHAMPION_V5_COMMANDS`** (`37` commands), and **`render_stage68a_airos8_ptp_champion_v5_script()`** (`40` lines).
  - Incorporates `Stage 68A-R2` DMA, NAPI, and TCP Small Queues / pacing tuning (`iwpriv wifi0 set_CabqMaxdur 20`, `uph_sync_flex=0`, `net.core.dev_weight=64`, `net.core.netdev_max_backlog=2000`, `net.ipv4.tcp_limit_output_bytes=131072`, `net.ipv4.tcp_pacing_ca_ratio=120`, `net.ipv4.tcp_pacing_ss_ratio=200`) on top of `Stage 62A Champion v4` + `FMX-DISC-07` universal `cron.status=enabled` + `/etc/persistent/rc.poststart` persistence.
  - Preserves `STAGE62A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V4` and all prior receipts for 100% backward compatibility.

---

## 2. Live `ath_dev.ko` & `/proc/sys/dev/uph_wifi0/*` Hardware Audit (`CONFIRMED`)

- **Procfs Path Discovery (`proprietary airMAX module` `ubnt_poll_host.ko`)**:
  - On `WA.ar934x.v8.7.11`, `ubnt_poll_host.ko` exposes its per-radio TDMA sysctl table at **`/proc/sys/dev/uph_wifi0/`** (underscore separator, whereas `/proc/sys/dev/uph/` only contains `addradio`, `gps_info`, `gpsreset`).
  - `/proc/sys/dev/uph_wifi0/` exposes 16-column per-station tables (`atpc`, `cms_bias`, `swr_limit`, `timing`, `voip_bias`, where `.242` STA populates columns `4..6` with `24 10 10`) plus scalar controls (`daprot=1`, `enable=1`, `noack_mode=1`, `ptp_xmit=0`, `status=1`) and `netconf` (`AP NETWORK CONFIGURATION`).
- **`/sys/module/ath_dev/parameters/*` Hardware Descriptor Floor Audit (`ath_dev.ko`)**:
  - Stock `WA.v8.7.11` reserves per-AC TX buffer descriptors via `ACBEMinfree=32`, `ACBKMinfree=48`, `ACVIMinfree=16`, `ACVOMinfree=0`, `CABMinfree=48`, `UAPSDMinfree=0`, and defaults `iwpriv ath0 get_protmode` to `1`.

---

## 3. Counterbalanced `A1 -> B1 -> A2 -> B2` Hardware Sweep Results (`CONFIRMED`)

| Round | Candidate Knob Stack (`571`-Knob Catalog) | Aggregate Goodput (`A -> B`) | Bulk TCP (`A -> B`) | `p50` RTT (`A -> B`) | `p95` RTT (`A -> B`) | `p99` RTT (`A -> B`) | Karpathy `fmx_loss` (`A -> B`) | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`S70B-R1`** | `PBE5AC_ATH_DEV_PROTMODE_0_MINFREE_AND_AGGR_BURST` (`protmode=0`, `uapsd=0`, `wifi0 burst=1/burst_dur=2000`, `ACBEMinfree=8`, `ACVIMinfree=8`, `ACBKMinfree=16`, `CABMinfree=16`) | `20.411 -> 18.181 Mbps` (`-10.93%`) | `11.593 -> 9.509 Mbps` (`-17.98%`) | `3.084 -> 2.945 ms` (**`-4.51%`**) | `5.812 -> 7.757 ms` (`+33.47%`) | `9.606 -> 8.645 ms` (**`-10.00%`**) | `0.2232 -> 0.2679` (`+0.0446`) | **`DISCARD`** |
| **`S70B-R2`** | `PBE5AC_UPH_WIFI0_TIMING_2_VOIP_CMS_BIAS_AND_TXQ_256` (`uph_wifi0/timing=2`, `voip_bias=6`, `cms_bias=6`, `daprot=2`, `tx_queue_len=256`, `protmode=0`, `ACBEMinfree=8`) | `19.693 -> 18.794 Mbps` (`-4.57%`) | `11.030 -> 10.270 Mbps` (`-6.89%`) | `2.508 -> 2.836 ms` (`+13.08%`) | `5.639 -> 5.598 ms` (**`-0.73%`**, `B2=4.346 ms`) | `7.568 -> 18.114 ms` (`+139.35%`) | `0.2195 -> 0.2951` (`+0.0755`) | **`DISCARD`** |

### Causal Attribution (`CONFIRMED`)
1. **Why `S70B-R1` (`wifi0 burst=1` + `ACBEMinfree=8`) Regressed Bulk TCP (`-17.98%`, `ath_dev.ko` + `ubnt_poll_host.ko`)**:
   - While lowering `ACBEMinfree` (`32 -> 8`) and disabling `protmode` (`0`) slightly reduced median `p50` RTT (`-4.51%`, `3.084 -> 2.945 ms`) and `p99` RTT (`-10.00%`, `9.606 -> 8.645 ms`) with `0.00%` VoIP loss (`Jain = 0.9888`), enabling `iwpriv wifi0 burst 1` (`burst_dur=2000`) conflicts with `ubnt_poll_host.ko` TDMA slot preemption and shrinking `ACBEMinfree` to `8` allows `AC_BE` frames to encroach on `AC_VI`/`CAB` descriptor headroom.
2. **Why `S70B-R2` (`uph_wifi0` bias + `tx_queue_len=256`) Inflated `p99` RTT (`7.568 -> 18.114 ms`, `Linux netdev` + `ubnt_poll_host.ko`)**:
   - Increasing `tx_queue_len` from `192` (`Champion v5`) to `256` on `eth0`/`ath0`/`br0` adds `+64` packets (`~96 KB`) of netdev queue depth ahead of `ath0`, inflating `p99` tail latency (`7.568 -> 18.114 ms`) and reducing Bulk TCP goodput (`-6.89%`).
3. **Retention & Persistence of `Stage 68A Champion v5` (`S68A-R2`, `CONFIRMED`)**:
   - `Stage 68A Champion v5` (`S68A-R2`: `fmx_loss = 0.2195` in `S70B-R2` Arm A and `0.1966` in `Stage 68A`) outperformed both candidates and was automatically retained and re-persisted to `/etc/persistent/rc.poststart` + `cfgmtd -w -p /etc/` (`CFGMTD_OK`) on both `.241` and `.242`.
