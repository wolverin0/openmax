<!-- doc-head: STAGE49B_LTU_PB_BOOST_AND_FRAME_LEN_OTA_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 49B — LTU Over-The-Air `pb_boost`, `frame_len` Sysfs Bug Discovery, and Fail-Safe EVM-Matched Auto-Rate Ceiling Benchmark

**Date**: 2026-10-25  
**Task ID**: `T-S49B-LTU-40MHZ-AND-PB-BOOST-OTA-DISTANCE-BENCH`  
**Artifact**: [`artifacts/autoresearch/stage49b_ltu_pb_boost_and_frame_len_ota_bench_20261025.json`](../artifacts/autoresearch/stage49b_ltu_pb_boost_and_frame_len_ota_bench_20261025.json)

---

## 1. Executive Summary & Confirmed Kernel/Driver Discoveries (`CONFIRMED`)

On the live NLOS Over-The-Air link between **`LTU-Lite #1`** (`Boca 5`, `198.18.0.61`, `AP-PTMP(Run)`) and the remote standalone PoE **`LTU-Lite #2`** (`198.18.0.72`, `CPE-PTMP(Run)` at `-76/-69 dBm` DL, `11.4 dB` EVM), Stage 49B uncovered three hardware/driver behaviors and executed a 9-trial counterbalanced Latin-square Triple-Play benchmark with fail-safe remote rollback watchdogs:

1. **`ame_core.ko` Sysfs `frame_len` $\rightarrow$ `duty_cycle` Overwrite Bug (`CONFIRMED`)**:
   - Writing `echo 5000 > /sys/class/ame/ame_ctrl_dev/frame_len` does **not** change `frame_period` in `bandwidthConfig`: instead, a buggy sysfs store handler in `ame_core.ko` overwrites `bandwidthConfig.duty_cycle = 5000` while leaving `frame_period = 2000` (`2.0 ms`, `dl_symbols: 60`, `ul_symbols: 19`) untouched.
   - Restoring `duty_cycle` requires writing `echo 750 > /sys/class/ame/ame_ctrl_dev/duty_cycle` (`duty_cycle: 750`), while changing the TDMA superframe period uses `/bin/af set framelength <2|5>`.
2. **Exact `autoMcsCeiling` vs. `cpe_mcs` (`0x20` = `32`) Register Contract (`CONFIRMED`)**:
   - Probing `/sys/class/ame/ame_ctrl_dev/autoMcsCeiling` against `/bin/af get automcsceil` established the exact `ame_core.ko` MIMO modulation index map:
     - `7` $\rightarrow$ `qpsk (2x)`
     - `11` $\rightarrow$ `16qam (4x)`
     - `15` $\rightarrow$ `64qam (6x)`
     - `19` $\rightarrow$ `256qam (8x)`
     - `23` $\rightarrow$ `1024qam (10x)`
     - `31` $\rightarrow$ `4096qam (12x)`
     - `32` (`0x20`) $\rightarrow$ `automatic (2x)`
   - **Critical `cpe_mcs` Pitfall**: While `autoMcsCeiling` accepts `15` (`64qam (6x)`) or `23` (`1024qam (10x)`), `/sys/class/ame/ame_ctrl_dev/cpe_mcs` (`echo <cpe_id> <mcs_lvl> <opcode>`) requires `mcs_lvl = 32` (`0x20` = `automatic (2x)`) when `opcode` is `0` (`DL Auto Rate`) or `2` (`UL Auto Rate`). Passing `15` or `23` to `cpe_mcs` with `opcode 0/2` corrupts the per-CPE rate state machine (`adj_mix_mcs`) and drops the uplink to `qpsk (1x)` SISO (`5040 kbps`). Restoring `echo 0 32 0 > cpe_mcs; echo 0 32 2 > cpe_mcs` immediately restores full 2x2 MIMO (`36480 kbps` DL / `10080 kbps` UL).
3. **Counterbalanced 9-Trial OTA Benchmark Results (`CONFIRMED`)**:
   - **Enabling `pb_boost=1` (`ON`) + `SWQ_INTERVAL_EXTEND=2` + `DGAIN_DL_ENABLE=1` + `dbg_ptmp_ul_pm_cpe=0` (`S49B-R1-PB-BOOST-ON-2MS`)**:
     - Cut **IPTV UDP packet loss by `-83.9%`** (from `4.731%` in `S49B-R0-STAGE48B-BASELINE` down to **`0.762%`**) and reduced **median loaded ping `p95` RTT by `-38.4%`** (`93.301 ms` $\rightarrow$ **`57.436 ms`**) and **mean `p95` RTT by `-21.3%`** (`79.787 ms` $\rightarrow$ **`62.776 ms`**).
   - **Adding EVM-Matched `autoMcsCeiling=15` (`64qam (6x)`) with Fail-Safe 45s Remote Rollback Watchdog (`S49B-R2-PB-BOOST-AND-EVM-MCS-CEILING`)**:
     - Eliminated high-MCS (`256-QAM`/`1024-QAM`) auto-rate probing retries on the `11.4 dB` EVM NLOS link, reducing **median loaded ping `p95` RTT by `-90.8%`** (`93.301 ms` $\rightarrow$ **`8.617 ms`**, with Rep 1 achieving **`p50 = 4.738 ms / p95 = 5.584 ms`** and Rep 2 achieving **`p50 = 7.346 ms / p95 = 8.617 ms`**) and **mean loaded ping `p95` RTT by `-54.7%`** (`79.787 ms` $\rightarrow$ **`36.175 ms`**), with `0.0%` VoIP packet loss and `1.025 ms` mean VoIP jitter across all trials.

---

## 2. Counterbalanced 9-Trial Over-The-Air Benchmark Summary (`198.18.0.61` $\rightarrow$ `198.18.0.72`)

| Profile | Trials | Mean Aggregate DL (`Mbps`) | Mean Bulk TCP (`Mbps`) | Mean IPTV UDP (`Mbps`) | Mean IPTV Loss (`%`) | Mean VoIP Jitter (`ms`) | Mean VoIP Loss (`%`) | Median Loaded Ping p50 (`ms`) | Median Loaded Ping p95 (`ms`) | Mean Loaded Ping p95 (`ms`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S49B-R0-STAGE48B-BASELINE`** (`pb_boost=2 AUTO`, `autoMcsCeiling=23 1024-QAM`) | 3 | `22.726` | `13.431` | `9.295` | `4.731%` | `1.022` | `0.0%` | `6.812` | `93.301` | `79.787` |
| **`S49B-R1-PB-BOOST-ON-2MS`** (`pb_boost=1 ON`, `SWQ_INTERVAL_EXTEND=2`, `DGAIN_DL=1`, `ul_pm=0`) | 3 | `22.433` | `13.622` | `8.811` | **`0.762%`** (**-83.9%**) | `1.055` | `0.0%` | **`6.432`** | **`57.436`** (**-38.4%**) | **`62.776`** (**-21.3%**) |
| **`S49B-R2-PB-BOOST-AND-EVM-MCS-CEILING`** (`pb_boost=1 ON`, `autoMcsCeiling=15 64-QAM 6x`, `cpe_mcs=32`) | 3 | `21.682` | `13.157` | `8.525` | `2.616%` | `1.025` | `0.0%` | `7.346` | **`8.617`** (**-90.8%**) | **`36.175`** (**-54.7%**) |
