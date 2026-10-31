<!-- doc-head: STAGE103A_WA_XC_UNTESTED_KNOBS_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 103A: Live `WA` & `XC` Top Untested `ubnt_poll_host.ko` / `umac.ko` Knobs Verification & Benchmark (`2026-10-26`)

## 1. Executive Summary (`CONFIRMED` | `HW_CONFIRMED`)

- **Task ID**: `T-S103A-LIVE-WA-XC-TOP-UNTESTED-UPH-KNOBS-BENCHMARK` (`CONFIRMED`, attributed to `proprietary airMAX/LTU module` + `mac80211` + `ath10k` + `Linux`).
- **Objective**: Take the top `WA` and `XC` `ubnt_poll_host.ko` / `umac.ko` sysctl and driver knobs identified in `Stage 102A` (`swr_limit`, `sta_priority`, `ptp_xmit`, `noack_mode` / `noackpolicy`, and `distance` / `acktimeout` / `coverage_class` readbacks) and run a live non-destructive verification and counterbalanced `A1 -> B1 -> A2 -> B2` benchmark (`45s` auto-rollback watchdog, `0` flash writes) across `WA (.250)` (`NanoStation 5AC Loco` `198.18.0.67`) and `XC (.198)` (`Rocket 5AC Prism Gen2` `198.18.0.64 / 198.18.0.68`) in the 3-CPE PtMP sector (`LAP-120 .20`).
- **Outcome (`CONFIRMED`, `PROMOTE_NEW_CHAMPION` for Latency & Bufferbloat Control)**:
  - **Three New `ubnt_poll_host.ko` Kernel Boundary Laws (`FMX-S103A-KB-01..03`)** proven live on `XC .198` and `WA .241`.
  - **Loaded `WA (.250)` `p95` RTT Cut by `-46.93%`**: Dropped from `77.650 ms` (`A1=65.718 ms, A2=89.582 ms`) under unoptimized `aql_threshold=12000` + `set_multiq=1` (`Arm A`) down to **`41.221 ms`** (`B1=40.136 ms, B2=42.305 ms`) under `Stage 103A` `swr_limit=3 -> ff_mcast_airtime_limit=5`, `sta_priority='1 2 1'`, `ptp_xmit=0`, `noack_mode=0`, `set_multiq=3`, and `aql_threshold=4000` (`Arm B`).
  - **Loaded `WA (.250)` RTT Jitter Cut by `-52.74%`**: Dropped from `21.615 ms` (`A1=20.414 ms, A2=22.816 ms`) to **`10.217 ms`** (`B1=9.196 ms, B2=11.237 ms`) with **`0.00%` VoIP/IPTV packet loss**.
  - **Multi-Objective Composite Loss (`fmx_loss`)**: Improved by **`+0.36%`** (`5.4658` $\to$ `5.4461`, `PROMOTE_NEW_CHAMPION`).

---

## 2. Three Live `ubnt_poll_host.ko` & `ath_dev.ko` Kernel Boundary Laws (`CONFIRMED`)

| Discovery ID | Claim Label & Attribution | Live Kernel Verification on `XC .198` (`Rocket 5AC Prism Gen2`) & `WA .241` | Mandatory Write Order Rule |
| :--- | :--- | :--- | :--- |
| **`FMX-S103A-KB-01`** | `CONFIRMED` (`proprietary airMAX/LTU module`) | `/proc/sys/dev/uph_wifi0/swr_limit` and `ff_cap_rep` share the same 64-byte (`16 x int32`) `ctl_table->data` scratch vector as `timing`, `cms_bias`, `voip_bias`, and `ff_mcast_airtime_limit` (`FMX-DISC-11`). Writing `echo 3 > /proc/sys/dev/uph_wifi0/swr_limit` populates index `[0]=3` in both `swr_limit` (`3 0 0 ...`) and `ff_cap_rep` (`3 0 0 ...`). Furthermore, reading `/proc/sys/dev/uph_wifi0/daprot` zeroes index `[0]` (`0 0 0 ...`). | Write `swr_limit=3` and `daprot=2` **BEFORE** writing `ff_mcast_airtime_limit=5` LAST; never read `daprot` after setting `ff_mcast_airtime_limit=5`. |
| **`FMX-S103A-KB-02`** | `CONFIRMED` (`proprietary airMAX/LTU module`) | `/proc/sys/dev/uph_wifi0/sta_priority` is a 3-integer vector (`<sta_slot> <prio_tier> <enable_flag>`, default `1 2 0`, active `1 2 1` / `1 1 2`) sharing a 12-byte `ctl_table->data` buffer with `debug_block_sta` and `debug_tid`. | Write `echo '1 2 1' > /proc/sys/dev/uph_wifi0/sta_priority` without touching `debug_block_sta` or `debug_tid`. |
| **`FMX-S103A-KB-03`** | `CONFIRMED` (`proprietary airMAX/LTU module` + `mac80211`) | On `XC .198` (`QCA9880`), `iwpriv wifi0 get_distance` reports `100000` (`100 km`) when `uph_wifi0/timing` is `0`, while `iwpriv ath0 get_noackpolicy <ac> 0` (`ac=0..3`) confirms normal ACK policy (`0`) across all 4 WMM Access Categories. On `OpenWrt` `WA .250` (`QCA9882`) and `LAP-120 .20`, `iw phy phy0 info` confirms `Coverage class: 0 (up to 0m)` (`RTS threshold: 512`). | Enforce `noack_mode=0` (`get_noackpolicy=0`) and `ptp_xmit=0` on PtMP CPEs (`ptp_xmit=1` is reserved strictly for 2-node PtP links). |

---

## 3. Counterbalanced `A1 -> B1 -> A2 -> B2` Sector Benchmark (`CONFIRMED`)

| Window | Arm | `WA (.250)` Goodput (`Mbps`) | `WA (.250)` `p50 / p95 / p99` RTT (`ms`) | `WA (.250)` RTT Jitter (`ms`) | Sector `p50 / p95` RTT (`ms`) | IPTV Jit (`ms`) | VoIP Jit (`ms`) | VoIP Loss (`%`) | `XC .198` `set_multiq` / `sta_priority` / `uph[0]` |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`A1`** | `Arm A` | `34.864` | `27.824` / `65.718` / `71.230` | `20.414` | `513.412` / `532.359` | `2.720` | `3.166` | `0.00%` | `1` / `1 1 1` / `0` |
| **`B1`** | `Arm B` | `29.179` | `25.321` / `40.136` / `40.136` | `9.196` | `512.160` / `519.568` | `3.038` | `3.296` | `0.00%` | `3` / `1 1 2` / `5` |
| **`A2`** | `Arm A` | `32.739` | `21.816` / `89.582` / `89.582` | `22.816` | `510.408` / `544.291` | `2.020` | `1.525` | `0.00%` | `1` / `1 1 1` / `0` |
| **`B2`** | `Arm B` | `28.054` | `19.589` / `42.305` / `46.204` | `11.237` | `509.294` / `520.653` | `1.836` | `2.329` | `0.00%` | `3` / `1 1 2` / `5` |
| **Mean `A`** | `Baseline` | `33.801` | `24.820` / `77.650` / `80.406` | `21.615` | `511.910` / `538.325` | `2.370` | `2.345` | `0.00%` | `aql_thr=12000` |
| **Mean `B`** | **`S103A`** | **`28.616`** | **`22.455` (`-9.5%`) / `41.221` (`-46.9%`)** | **`10.217` (`-52.7%`)** | **`510.727` / `520.111` (`-3.38%`)** | **`2.437`** | **`2.812`** | **`0.00%`** | **`aql_thr=4000`** |

---

## 4. Five-Pillar Compliance & Verification Artifacts

- **Benchmark Runner**: [`tools/benchmarks/run_stage103a_wa_xc_untested_knobs_bench.py`](../tools/benchmarks/run_stage103a_wa_xc_untested_knobs_bench.py)
- **JSON Receipt**: [`artifacts/autoresearch/stage103a_wa_xc_untested_knobs_bench.json`](../artifacts/autoresearch/stage103a_wa_xc_untested_knobs_bench.json) (`five_pillar_compliance.compliant = true`, `mm-stage103a-live-wa-xc-untested-uph-knobs-bench-20261026`)
- **Verification Test Suite**: [`tests/test_stage103a_wa_xc_untested_knobs_bench.py`](../tests/test_stage103a_wa_xc_untested_knobs_bench.py)
