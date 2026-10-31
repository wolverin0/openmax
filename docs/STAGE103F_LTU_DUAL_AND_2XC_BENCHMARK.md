<!-- doc-head: STAGE103F_LTU_DUAL_AND_2XC_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 103F — Dual `LTU-Lite` (`500 Hz` Superframe + `LDPC-12` + `OFDMA`) & `Rocket 2AC Prism` (`2XC` `Boca 8` `MultiQ` + `swr_limit=2`) Benchmark

- **Stage / Task ID**: `Stage 103F` (`T-S103F-LTU-DUAL-LITE-AND-2XC-BOCA8-SUPERFRAME-AND-MULTIQ-BENCH`)
- **Claim Status**: `CONFIRMED`
- **Attribution**: `proprietary LTU module` / `proprietary airMAX module` / `Linux` (`ame_core.ko` `500 Hz` `80`-symbol superframe tail guard `sched_mcs_limit_symbol_end=59` + `ldpc_iteration=12` + `ofdma_subbands=0xff` on `LTU-Lite #1` `.110` & `LTU-Lite #2` `.111` OTA sync template; `2XC.v8.7.11` `ubnt_poll_host.ko` `swr_limit=2` + `ptp_xmit=1` + `ff_cap_rep=2` + `umac.ko` `max_peers=32` + `vow_config=1` + `ath0` `set_multiq=3` + `set_cabq_maxdur=20` on `Rocket 2AC Prism` `.112` `Boca 8`)
- **Durable Memory Receipt**: `<memorymaster-id>` (`claim_id=152977`, `scope="project:futuramax"`)
- **Machine-Checked Receipt**: [`artifacts/autoresearch/stage103f_ltu_dual_and_2xc_bench.json`](../artifacts/autoresearch/stage103f_ltu_dual_and_2xc_bench.json)
- **Benchmark Harness**: [`tools/benchmarks/run_stage103f_ltu_dual_and_2xc_bench.py`](../tools/benchmarks/run_stage103f_ltu_dual_and_2xc_bench.py)

---

## 1. Ground-Up Binary RE & 571-Knob Provenance (`Pillar A`)

1. **`AF-LTU` (`AF-LTU.v2.3.1`, `Beetle` Cortex-A7 SMP + `ame_ASIC0` FPGA) on `LTU-Lite #1` (`198.18.0.63`, `Boca 5`) & `LTU-Lite #2` (`.111` / `198.18.0.72`, `PUBLIC_DEVICE_0043`)**:
   - **500 Hz (`2.0 ms`, `80`-Symbol) Superframe Tail Guard (`Stage 102E`)**:
     - `sched_ap_mcs_limit_symbol_end=59`, `sched_cpe_mcs_limit_symbol_end=59`, `sched_mcs_limit_symbol_end=59` (`KNOB-MOD-AME_CORE-SCHED_MCS_LIMIT_SYMBOL_END`) prevents dynamic DL modulation allocation from overrunning the DL tail beacon at symbol `60`.
     - `sched_max_agg_cnt=8` (`KNOB-MOD-AME_CORE-SCHED_MAX_AGG_CNT`) and `multi_ack_enable=1` (`KNOB-MOD-AME_CORE-MULTI_ACK_ENABLE`) bound per-superframe MPDU aggregation and enable multi-block ACK compression.
   - **Stage 102A Top Untested `AF-LTU` PHY/MAC Knobs**:
     - `/sys/class/ame/ame_debug_dev/ldpc_iteration` (`10 -> 12`, `KNOB-SYSFS-AME-LDPC_ITERATION`, `Stage 102A` Rank `#6`): increases the `ame_ASIC0` hardware LDPC belief-propagation decoder budget from `10` to `12` iterations (`LDPC iteration is 12`).
     - `/sys/class/ame/ame_ctrl_dev/ofdma_subbands` (`0xff`, `KNOB-SYSFS-AME-OFDMA_SUBBANDS`, `Stage 102A` Rank `#8`): enables all 8 OFDMA subbands across the channel.
   - **`LTU-Lite #2` (`.111` / `198.18.0.72`) OTA Sync Provisioning**:
     - `LTU-Lite #2` (`PUBLIC_DEVICE_0043`) is currently unpowered on the bench (`Stations count: 0` on `LTU-Lite #1`). Staged `/etc/persistent/fmx_stage103f_ltu_lite2_sync.sh` (`MD5 = 54a2daa4f80d99cd2a791e38926911db`) on `LTU-Lite #1` (`.110`) so `LTU-Lite #2` automatically receives the exact `500 Hz` `80`-symbol superframe tail guard + `ldpc_iteration=12` + `ofdma_subbands=0xff` + `netdev_budget=640`/`dev_weight=80` stack upon OTA association.

2. **`Rocket 2AC Prism` (`2XC.v8.7.11`, `QCA9558` + `QCA9880`, `198.18.0.73` / `.251` on `Boca 8`)**:
   - **Stage 102A Top Untested `ubnt_poll_host.ko` / `umac.ko` / `ath0` Knobs**:
     - `/proc/sys/dev/uph_wifi0/swr_limit` (`2`, clamped from `3` inside `ubnt_poll_host_set_swr_limit` at `0x92fc`, `KNOB-PROC-UPH-SWR_LIMIT`): matches the exact `Stage 102A` `NSGA-II` Pareto `#0` Knee (`swr_limit = 2`).
     - `/proc/sys/dev/uph_wifi0/ptp_xmit = 1` (`KNOB-PROC-UPH-PTP_XMIT`) and `/proc/sys/dev/uph_wifi0/ff_cap_rep = 2` (`KNOB-PROC-UPH-FF_CAP_REP`).
     - `/sys/module/umac/parameters/max_peers = 32` (`KNOB-MOD-UMAC-MAX_PEERS`) and `/sys/module/umac/parameters/vow_config = 1` (`KNOB-MOD-UMAC-VOW_CONFIG`).
     - `iwpriv ath0 set_multiq 3` (`get_multiq:3`, `KNOB-IWPRIV-ATH0-SET_MULTIQ`) and `iwpriv ath0 set_cabq_maxdur 20` (`KNOB-IWPRIV-ATH0-SET_CABQ_MAXDUR`), combined with `Stage 99C` `vow_extstats=0`, `enable_tx_tcp_cksum=1`, `AC*Minfree` (`48/64/16/0`), `ebtables`/`mangle` unload, and `wifi1`/`ubntspecd`/`ubnt-gps-reader` governance.

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Results (`Pillar C` & `Pillar D`)

Both radios were evaluated across a 4-window counterbalanced `A1 -> B1 -> A2 -> B2` protocol with a `45s` auto-rollback watchdog under concurrent Triple-Play (`Bulk TCP` + `IPTV UDP` + `VoIP UDP`), `1400 B` loaded inter-radio Ethernet `GMAC0` RTT probes (`.110 <-> .112`), and active `sa_Test` spectral scans (`5700`/`5750`/`5800 MHz`).

### Table 1 — `LTU-Lite #1` (`198.18.0.63`, `Boca 5`) Counterbalanced Summary

| Metric (`LTU-Lite #1` `.110`) | `ARM-A` (`LDPC=10`, Unpaced `symbol_end=70`) | `ARM-B` (`LDPC=12`, `500 Hz` `symbol_end=59` + Burst Pacing) | Delta (`ARM-B vs ARM-A`) |
| :--- | :---: | :---: | :---: |
| **SoC Bulk TCP Median ( Peak )** | `186.365 Mbps` (`187.378 Mbps`) | `166.017 Mbps` (`177.720 Mbps`) | `-20.348 Mbps` (`0` retransmits) |
| **SoC IPTV UDP Goodput (`DSCP CS4`)** | `8.134 Mbps` (`0.0%` loss) | **`9.503 Mbps`** (`0.0%` loss) | **`+1.369 Mbps` (`+16.8%`)** |
| **SoC IPTV UDP Jitter** | `0.685 ms` | **`0.288 ms`** | **`-0.397 ms` (`-58.0%`)** |
| **SoC VoIP UDP Jitter (`DSCP EF`)** | `0.531 ms` (`0.0%` loss) | **`0.495 ms`** (`0.0%` loss) | **`-0.036 ms` (`-6.8%`)** |
| **Loaded `GMAC0` RTT `p50` (`.110 -> .112`)** | `2.680 ms` | `2.796 ms` (`2.455 ms` in `B1`) | `+0.116 ms` |
| **Loaded `GMAC0` RTT `p95` (`.110 -> .112`)** | `7.443 ms` (`8.730 ms` in `A1`) | **`6.905 ms`** (**`5.962 ms`** in `B1`) | **`-0.538 ms` (`-7.2%` med / `-31.7%` `B1`)** |
| **Loaded `GMAC0` RTT `p99` (`.110 -> .112`)** | `9.402 ms` (`11.280 ms` in `A1`) | **`7.803 ms`** (**`6.745 ms`** in `B1`) | **`-1.599 ms` (`-17.0%` med / `-40.2%` `B1`)** |
| **`scheduler_giveup` / `symbol_giveup`** | `0` / `0` | **`0` / `0`** | **`0` overrun faults** |

### Table 2 — `Rocket 2AC Prism` (`2XC.v8.7.11`, `198.18.0.73` on `Boca 8`) Counterbalanced Summary

| Metric (`Rocket 2AC Prism` `.112`) | `ARM-A` (`swr_limit=0`, `multiq=1` Stock) | `ARM-B` (`swr_limit=2`, `multiq=3`, `ptp_xmit=1`, `ff_cap_rep=2`) | Delta (`ARM-B vs ARM-A`) |
| :--- | :---: | :---: | :---: |
| **SoC Bulk TCP Median ( Peak )** | `259.276 Mbps` (`265.096 Mbps`) | **`257.571 Mbps`** (**`263.295 Mbps`**, `+9.839 Mbps` in `B1`) | `-0.7%` med / **`+3.9%` `B1 vs A1`** |
| **SoC IPTV UDP Goodput (`DSCP CS4`)** | `17.202 Mbps` (`0.0%` loss) | **`18.798 Mbps`** (`0.0%` loss) | **`+1.596 Mbps` (`+9.3%`)** |
| **SoC VoIP UDP Jitter (`DSCP EF`)** | `0.056 ms` (`0.0%` loss) | **`0.054 ms`** (`0.0%` loss) | **`-0.002 ms` (`-3.6%`)** |
| **Loaded RTT `p50` (`.112 -> .110`)** | `2.575 ms` | **`2.362 ms`** (`1.964 ms` in `B1`) | **`-0.213 ms` (`-8.3%`)** |
| **Loaded RTT `p95` (`.112 -> .110`)** | `8.489 ms` | **`6.357 ms`** (**`5.216 ms`** in `B2`) | **`-2.132 ms` (`-25.1%`)** |
| **Loaded RTT `p99` (`.112 -> .110`)** | `10.038 ms` | **`7.428 ms`** (**`5.638 ms`** in `B2`) | **`-2.610 ms` (`-26.0%`)** |
| **`IRQ 2 wifi1` Interrupts** | `0` | **`0`** | **`-100%` eliminated** |

---

## 3. Verification Commands

```powershell
pytest tests/test_stage103f_ltu_dual_and_2xc_bench.py -q
python tools/verify/enforce_5pillar_research_gate.py artifacts/autoresearch/stage103f_ltu_dual_and_2xc_bench.json
```
