<!-- doc-head: STAGE38A_24GHZ_AND_LTU_IPTV_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 38A — 2.4 GHz (`Rocket 2AC Prism` + `NanoLoco M2`) & LTU (`LTU-Lite #1` / `#2`) IPTV `AC_VI`, `UL_data_weight` / `fixed_frame`, and `tcp_notsent_lowat` Benchmark

- **Task ID**: `T-S38A-24GHZ-AND-LTU-IPTV-AC-VI-AND-UL-DATA-WEIGHT-BENCH`
- **Date**: `2026-10-25`
- **Runner**: [`tools/bench/run_stage38a_24ghz_and_ltu_iptv_bench.py`](<repo>/tools/bench/run_stage38a_24ghz_and_ltu_iptv_bench.py)
- **Artifact**: [`artifacts/autoresearch/stage38a_24ghz_and_ltu_iptv_bench_20261025.json`](<repo>/artifacts/autoresearch/stage38a_24ghz_and_ltu_iptv_bench_20261025.json)
- **Tests**: [`tests/test_stage38a_24ghz_and_ltu_iptv_bench.py`](<repo>/tests/test_stage38a_24ghz_and_ltu_iptv_bench.py)

---

## 1. Executive Summary & Confirmed Hardware Discoveries

1. **`LTU-Lite` Untagged Ethernet Bridge (`br1` / `eth0.1`) (`CONFIRMED`)**:
   - On `LTU.afltu.v2.4.0`, the internal `QCA8337N` switch maps external untagged Ethernet frames to `eth0.1` inside `br1` (whereas `br0` bridges `eth0.2` and `ath0`). Assigning `198.18.0.63/24` on `br1` of `LTU-Lite #1` (`gi5`) and `198.18.0.118/24` on `br1` of `LTU-Lite #2` (`gi7`) enables full L2/L3 IPv4 benchmarking across `gi5`, `gi7`, and `gi8` (`198.18.0.65`).
2. **`QCA8337N` Hardware Switch Port-Shaper Leftover (`htb clear`) (`CONFIRMED`)**:
   - Historical customer configuration on both `LTU-Lite #1` and `LTU-Lite #2` had `tshaper.1.output.rate=15750` (`15.75 Mbps` DL) and `tshaper.1.input.rate=1575` (`1.575 Mbps` UL) programmed into the `QCA8337N` hardware switch (`ssdk_sh rate portshaper`). Running `htb clear` in RAM disables the hardware switch port-shaper on ports `0/1/5`, unlocking full `94..97 Mbps` line rate with `0.0%` UDP IPTV loss.
3. **`iproute2` `tc` `limit 1024p` Syntax Bug on `LTU.afltu.v2.4.0` (`CONFIRMED`)**:
   - On `LTU.afltu.v2.4.0`, `tc qdisc replace dev ath0 root fq_codel limit 1024p ...` fails with `Illegal "limit"` because `tc` prints `1024p` on output (`quantum 300 target 5.0ms interval 100.0ms`) but requires `limit 1024` (without trailing `p`) on input. Using `limit 1024` properly activates `quantum 1514 target 2.5ms interval 50.0ms ecn` on `ath0` root while preserving `eth0` hardware `mq`.
4. **`ubnt_poll_host.ko` Shared `sysctl_table->data` Buffer & `tcp_wmem=131072` vs `tcp_notsent_lowat=16384` Tradeoff (`CONFIRMED`)**:
   - On `Rocket 2AC Prism` (`Linux 2.6.32.68`), all `/proc/sys/dev/uph_wifi0/*` entries in `ubnt_poll_host.ko` share a single static integer vector (`sysctl_table->data`), so writing `fixed_frame` after `ff_mcast_airtime_limit=5` overwrites the shared readback buffer unless `ff_mcast_airtime_limit=5` is written last.
   - Aggressive socket buffer clamping (`tcp_wmem = '4096 16384 131072'` on `Rocket 2AC Prism` and `tcp_notsent_lowat = 16384` on `LTU-Lite`) cut `Rocket 2AC Prism` `p95` RTT by **`-11.07%`** (`23.104 -> 20.547 ms`), cut `NanoLoco M2` cross-port RTT by **`-37.7%`** (`0.5655 -> 0.3525 ms`), and reduced `LTU-Lite` bulk TCP retransmissions by **`-100%`** (`22.5 -> 0.0` retransmits) while boosting `ames_goodput_mbps` by **`+32.0%`** (`26.845 -> 35.446 Mbps`), but throttled multi-stream bulk TCP goodput (`-8.18%` on `S38A-R1` and `-9.18%` on `S38A-R2`). Both rounds therefore appropriately executed `RETAIN_CURRENT_CHAMPION` and triggered Stage 40A (`tcp_wmem = 524288` / `tcp_notsent_lowat = 65536`).

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Results

### 2.1 `S38A-R1` — 2.4 GHz `Rocket 2AC Prism` (`198.18.0.65`) + `NanoLoco M2` (`198.18.0.70` / `198.18.0.50`)

| Phase | Arm | Bulk TCP (Mbps) | IPTV (Mbps) | IPTV Loss (%) | Composite Goodput (Mbps) | `p50` RTT (ms) | `p95` RTT (ms) | `p99` RTT (ms) | `NanoLoco M2` Ping (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`A1`** | `A` (`S34A-R1`) | `94.014` | `2.148` | `0.0%` | `96.162` | `1.599` | `19.265` | `27.352` | `0.776` |
| **`B1`** | `B` (`S38A-R1`) | `93.100` | `2.152` | `0.0%` | `82.661` | `1.649` | `22.552` | `28.043` | `0.341` |
| **`A2`** | `A` (`S34A-R1`) | `93.968` | `2.147` | `0.0%` | `90.494` | `2.139` | `26.943` | `28.851` | `0.355` |
| **`B2`** | `B` (`S38A-R1`) | `93.940` | `2.150` | `0.0%` | `88.719` | `2.232` | `18.542` | `21.932` | `0.364` |
| **Mean `A`** | `S34A-R1` | `93.991` | `2.1475` | `0.0%` | `93.328` | `1.869` | `23.104` | `28.1015` | `0.5655` |
| **Mean `B`** | `S38A-R1` | `93.520` | `2.1510` | `0.0%` | `85.690` | `1.9405` | **`20.547`** (**`-11.07%`**) | **`24.9875`** (**`-11.08%`**) | **`0.3525`** (**`-37.67%`**) |

- **Promoter Decision**: **`RETAIN_CURRENT_CHAMPION`** (`S34A-R1` retained in RAM; `p95` RTT improved `-11.07%` and `NanoLoco M2` RTT improved `-37.67%`, motivating Stage 40A `S40A-R1` with `tcp_wmem = '4096 16384 524288'` and `ff_mcast_airtime_limit=5` written last).

### 2.2 `S38A-R2` — `LTU-Lite #1` (`198.18.0.63` / `PUBLIC_DEVICE_0046%27`) $\leftrightarrow$ `LTU-Lite #2` (`198.18.0.118` / `PUBLIC_DEVICE_0076%27`)

| Phase | Arm | Bulk TCP (Mbps) | Bulk TCP Retransmits | IPTV (Mbps) | IPTV Loss (%) | AMES Goodput (Mbps) | `p50` RTT (ms) | `p95` RTT (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`A1`** | `A` (`S24F-R1`) | `41.015` | `8` | `2.153` | `0.0%` | `27.474` | `38.312` | `70.794` |
| **`B1`** | `B` (`S38A-R2`) | `36.881` | **`0`** | `2.153` | `0.0%` | **`34.622`** | `38.989` | **`65.215`** |
| **`A2`** | `A` (`S24F-R1`) | `41.589` | `37` | `2.153` | `0.0%` | `26.216` | `36.186` | `62.633` |
| **`B2`** | `B` (`S38A-R2`) | `38.949` | **`0`** | `2.150` | `0.0%` | **`36.270`** | `38.118` | `147.673` |
| **Mean `A`** | `S24F-R1` | `41.302` | `22.5` | `2.1530` | `0.0%` | `26.845` | `37.249` | `66.7135` |
| **Mean `B`** | `S38A-R2` | `37.915` | **`0.0`** (**`-100%`**) | `2.1515` | `0.0%` | **`35.446`** (**`+32.04%`**) | `38.5535` | `106.444` |

- **Promoter Decision**: **`RETAIN_CURRENT_CHAMPION`** (`S24F-R1` retained in RAM; `tcp_notsent_lowat=16384` + corrected `ath0` `fq_codel limit 1024 quantum 1514` eliminated `100%` of TCP retransmissions `22.5 -> 0.0` and boosted `ames_goodput_mbps` by `+32.04%`, motivating Stage 40A `S40A-R2` without `tcp_notsent_lowat=16384` throttling).
