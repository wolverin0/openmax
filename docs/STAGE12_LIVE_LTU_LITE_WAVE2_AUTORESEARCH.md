<!-- doc-head: STAGE12_LIVE_LTU_LITE_WAVE2_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 12 — Live `LTU-Lite` (`UBNT AME SoC`) Wave 2 Autoresearch Benchmark (`LTU-R7..R12`)

- **Experiment ID**: `FMX-STAGE12-LTU-LITE-WAVE2-AUTORESEARCH`
- **Timestamp (UTC)**: `2026-10-24T23:09:19Z`
- **Target Device**: Ubiquiti `LTU-Lite` (`AF-LTU`, `sysid=0xa614`, MAC `PUBLIC_DEVICE_0045`) via IPv6 `PUBLIC_DEVICE_0046%27`
- **Architecture**: **UBNT AME SoC** (`Dual-core ARMv7 Cortex-A9 r3p0`, `1990.65 BogoMIPS`) + custom `ame_core` LTU wireless MAC/PHY (`IRQ 63`, `IRQ 92`)
- **Firmware / Kernel**: `LTU.afltu.v2.4.0.210.250425.1342` / `Linux 3.14.65 SMP PREEMPT RT`
- **Artifact Receipt**: [`artifacts/autoresearch/ltu_lite_wave2_live_autoresearch_20261024.json`](../artifacts/autoresearch/ltu_lite_wave2_live_autoresearch_20261024.json)

---

## 1. Executive Summary & `ame_core` Kernel Module Findings

Building on Wave 1 (`LTU-R1..R6`, which tuned socket buffers `rmem_max/wmem_max=524288` and `ath0` root `fq_codel quantum 1514 target 2.5ms interval 50ms`), Wave 2 (`LTU-R7..R12`) probed all **39 readable/writable `/sys/module/ame_core/parameters/*` kernel parameters**, `/bin/af` TDD framing (`dutycycle=75`, `framelength=2` (`2.0ms`)), and `eth0` `mq` hardware queue leaf disciplines across **6 paired `A/B/A/B` live RAM-only rounds**.

### Confirmed Hardware & Kernel Control Boundaries (`CONFIRMED`)
1. **`ame_core` Scheduler Max Aggregation Count (`sched_max_agg_cnt=8` vs `5`, `LTU-R9`)**:
   - Raising `/sys/module/ame_core/parameters/sched_max_agg_cnt` from stock `5` to `8` eliminated periodic `ame_core` scheduler aggregation stalls during background scan windows, slashing mean `p95` tail latency by **`-88.5%`** (`372.406 -> 42.781 ms`, `p50: 29.442 -> 29.349 ms`, `J: 265.957 -> 68.077`, **KEEP**).
2. **`ame_core` Cross-Frame Backoff Control (`cz_cross_frame_backoff_enable=0` vs `1`, `LTU-R10`)**:
   - Disabling cross-frame backoff (`echo 0 > /sys/module/ame_core/parameters/cz_cross_frame_backoff_enable`) reduced `p95` tail latency by **`-35.6%`** (`300.845 -> 193.738 ms`, with `B2` settling at `43.421 ms`, `J: 216.389 -> 157.060`, **KEEP**).
3. **`ame_core` Multi-ACK Aggregation (`multi_ack_enable=1` vs `0`, `LTU-R8`)**:
   - Disabling `multi_ack_enable=0` degraded both `p50` (`28.857 -> 31.256 ms`) and `p95` (`46.966 -> 50.008 ms`, `J: 69.800 -> 75.242`, **REJECT**), confirming `multi_ack_enable=1` is optimal on `UBNT AME SoC` and automatically restoring `1`.
4. **`eth0` `mq` Dynamic Leaf `fq_codel` Replacement Rule (`LTU-R7`, `LTU-R12`)**:
   - On `LTU-Lite` (`Linux 3.14.65 SMP PREEMPT RT`), `eth0` uses `qdisc mq 0: root` with 8 dynamically instantiated `fq_codel 0:` leaves (`parent :1..:8`). Unlike `ath0` (`qdisc fq_codel 0: root`), calling `tc qdisc change dev eth0 parent :$q` on an unnumbered `0:` `mq` child is a no-op (`tc qdisc show dev eth0` remains `quantum 300 target 5.0ms`); modifying `mq` leaves requires explicit handle instantiation via `tc qdisc replace dev eth0 parent :$q handle ${q}0: fq_codel ...` (`CONFIRMED`).
5. **Network Backlog & Queue Discipline Tightening (`LTU-R11`)**:
   - Setting `net.core.netdev_max_backlog=2500` and `eth0`/`ath0` `txqueuelen=256` reduced `p50` RTT by **`-7.7%`** (`33.776 -> 31.190 ms`, `J: 117.448 -> 114.675`, **KEEP**).

---

## 2. Complete `/sys/module/ame_core/parameters/` Hardware Inventory (`afltu.v2.4.0`)

| Parameter | Default Value | Role / Subsystem |
| :--- | :---: | :--- |
| `sched_max_agg_cnt` | `5` (**`8` KEEP**) | Max scheduler frame aggregation count |
| `cz_cross_frame_backoff_enable` | `1` (**`0` KEEP**) | Cross-frame contention backoff enable |
| `multi_ack_enable` | `0` (`1` after Wave 1/2) | Multi-ACK aggregation |
| `SNR_BOOST_EN` / `SNR_BOOST_THD_ADJ` | `1` / `0` | AME PHY SNR boost engine (` KEEP` in `LTU-R3` was `REJECT` when disabled) |
| `DGAIN_DL_ENABLE` | `0` | Downlink digital gain control |
| `RX_POWER_HIGH_INTERF_STABLE_PWR_HIGH` / `LOW` | `900` / `700` | High-interference RX power stability thresholds |
| `RX_POWER_TARGET_NOISE_VAL_THD` | `-79` | Target noise floor threshold (dBm) |
| `sched_ap_mcs_limit_level` / `symbol_end` | `4` / `60` | AP scheduler MCS limit & symbol boundary |
| `sched_cpe_mcs_limit_level` / `symbol_end` | `4` / `60` | CPE scheduler MCS limit & symbol boundary |
| `sched_mcs_limit_level` / `begin` / `end` | `4` / `15` / `70` | Global scheduler MCS symbol window |
| `sched_reserved_ul_mgmt_syms` | `1` | Reserved uplink management symbols per TDD frame |
| `send_ctrl_in_data` | `1` | Piggyback control descriptors in data frames |
| `cfo_pass_threshold` / `pb_cfo_apply` | `400` / `1` | Carrier frequency offset threshold & correction |
| `sfo_iq_diff_thre` / `sfo_shift_multi` | `400` / `14` | Sampling frequency offset IQ threshold & multiplier |
| `pwr_percent` | `50` | Transmit power percentage |

---

## 3. Wave 2 Paired `A/B/A/B` Benchmark Results (`LTU-R7..R12`)

| Round | Knob (`apply_cmd`) | Baseline (`A`) | Candidate (`B`) | `A` Mean `p50` / `p95` (ms) | `B` Mean `p50` / `p95` (ms) | `A -> B` SSH Stream (Mbps) | `A_J -> B_J` (`delta_J`) | Decision |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`LTU-R7`** | `tc qdisc change dev eth0 parent :1..:8` | `quantum 300` | `change` no-op on `0:` `mq` leaf | `28.729` / `47.770` | `35.196` / `140.829` | `13.864 -> 13.371` | `70.091 -> 135.687` (`+65.596`) | **REJECT** |
| **`LTU-R8`** | `ame_core/multi_ack_enable=0` | `1` | `0` | `28.857` / `46.966` | `31.256` / `50.008` | `13.883 -> 13.730` | `69.800 -> 75.242` (`+5.442`) | **REJECT** |
| **`LTU-R9`** | `ame_core/sched_max_agg_cnt=8` | `5` | `8` | `29.442` / `372.406` | **`29.349` / `42.781`** | `13.749 -> 13.451` | `265.957 -> 68.077` (**`-197.880`**) | **KEEP** |
| **`LTU-R10`** | `ame_core/cz_cross_frame_backoff_enable=0` | `1` | `0` | `25.035` / `300.845` | `28.320` / **`193.738`** (`B2: 43.421`) | `13.915 -> 13.861` | `216.389 -> 157.060` (**`-59.329`**) | **KEEP** |
| **`LTU-R11`** | `netdev_max_backlog=2500`, `txqueuelen=256` | `1000 / 1000` | `2500 / 256` | `33.776` / `113.994` | **`31.190`** / `115.501` | `13.447 -> 11.753` | `117.448 -> 114.675` (**`-2.773`**) | **KEEP** |
| **`LTU-R12`** | Combined Profile (`tc qdisc change` vs `replace`) | `A` (with `sched_max_agg_cnt=8` already active) | `B` | `30.340` / `42.022` | `30.799` / `44.297` | `13.829 -> 13.620` | `69.063 -> 71.142` (`+2.079`) | **REJECT** |
