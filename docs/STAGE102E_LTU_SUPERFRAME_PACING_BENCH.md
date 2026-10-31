<!-- doc-head: STAGE102E_LTU_SUPERFRAME_PACING_BENCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 102E — `LTU-Lite #1` (`198.18.0.63`) `500 Hz` (`2.0 ms`, `80`-Symbol) Superframe Tail Guard & Socket/NAPI Burst Pacing Benchmark

- **Status**: `CONFIRMED` (`<memorymaster-id>`, `claim_id=152951`)
- **Attribution**: `proprietary LTU module` (`ame_core.ko` `500 Hz` `80`-symbol superframe tail guard `sched_mcs_limit_symbol_end=59`, `sched_max_agg_cnt=8`, `multi_ack_enable=1` + `ame_ctrl_dev`) + `Linux` (`3.14.65 #1 SMP PREEMPT RT` `netdev_budget=640`, `dev_weight=80`, `rmem_max/wmem_max=4MB`, `tcp_limit_output_bytes=196608`, `ath0` `XPS=1` `CPU0`, `br0/br1` `RPS=2` `CPU1`)
- **Artifacts & Harness**:
  - Harness: [`tools/benchmarks/run_stage102e_ltu_superframe_pacing_bench.py`](<repo>/tools/benchmarks/run_stage102e_ltu_superframe_pacing_bench.py)
  - Receipt: [`artifacts/autoresearch/stage102e_ltu_superframe_pacing_bench.json`](<repo>/artifacts/autoresearch/stage102e_ltu_superframe_pacing_bench.json)
  - Pareto Model Source: [`docs/STAGE99B_LTU_80SYMBOL_SUPERFRAME_SIMPY_PARETO.md`](<repo>/docs/STAGE99B_LTU_80SYMBOL_SUPERFRAME_SIMPY_PARETO.md)
  - Verification Tests: [`tests/test_stage102e_ltu_superframe_pacing_bench.py`](<repo>/tests/test_stage102e_ltu_superframe_pacing_bench.py)

---

## 1. Physical Superframe Tail Guard & `500 Hz` Burst Pacing Architecture (`CONFIRMED`)

In `Stage 99B` (`docs/STAGE99B_LTU_80SYMBOL_SUPERFRAME_SIMPY_PARETO.md`), `SimPy` + `pymoo` NSGA-II Pareto optimization of the `2.0 ms` (`500 Hz`, `80`-symbol, `25.0 µs`/symbol) `AF-LTU` OFDM superframe identified two structural mismatches on `LTU-Lite #1` (`198.18.0.63` on `EdgeSwitch 10XP` `Boca 5` / `gi5`, running in `AP-PTMP(Run)` `4096-QAM 12X` on `5500 MHz`):

1. **`ame_core.ko` Superframe Tail Boundary Overshoot (`index 70` vs `index 59`) (`CONFIRMED`)**:
   - In the `2.0 ms` (`80`-symbol, `duty_cycle = 750`) superframe, the downlink window occupies **`61` symbols (`index 0..60`)**:
     - `index 0`: `F_PREAMBLE` (`1` symbol)
     - `index 1`: `F_BEACON` (`1` primary beacon symbol)
     - `index 2..59`: **`58` dynamic DL symbols** (`F_CNTRL` / `F_MNAGR` / `F_DATA` / `F_ACK`)
     - `index 60`: `F_BEACON` (`1` tail beacon symbol before the `19`-symbol UL window).
   - Stock `ame_core.ko` defaults set `sched_mcs_limit_symbol_begin = 15`, `sched_ap_mcs_limit_symbol_end = 60`, `sched_cpe_mcs_limit_symbol_end = 60`, and **`sched_mcs_limit_symbol_end = 70`** (overshooting the `61`-symbol DL boundary by `10` symbols into the UL window), while capping `sched_max_agg_cnt = 5` and disabling `multi_ack_enable = 0`.
   - **Stage 102E Tail Guard**: Aligns `sched_mcs_limit_symbol_begin = 12`, **`sched_ap_mcs_limit_symbol_end = 59`**, **`sched_cpe_mcs_limit_symbol_end = 59`**, and **`sched_mcs_limit_symbol_end = 59`** (strictly inside the `58`-symbol dynamic DL pool `index 2..59` prior to the tail `F_BEACON` at `index 60`), raises `sched_max_agg_cnt = 8`, and enables `multi_ack_enable = 1`.

2. **`500 Hz` (`2.0 ms`, `80`-Symbol) Linux NAPI, TSQ & Queue Burst Pacing (`CONFIRMED`)**:
   - Previously, `net.core.rmem_max = 524288` (`512 KB`) and `net.core.wmem_max = 524288` clamped TCP socket buffers despite `tcp_rmem`/`tcp_wmem` max values of `1.98 MB`, while `net.core.netdev_budget = 300`, `net.core.dev_weight = 64`, `ath0 tx_queue_len = 1000`, `br0 tx_queue_len = 0`, and `ath0/queues/tx-0/xps_cpus = 0` were unsynchronized to the `500 Hz` (`IRQ 52/53`) superframe cadence.
   - **Stage 102E `500 Hz` Burst Pacing**:
     - `net.core.dev_weight = 80` (`1` packet per OFDM symbol in an `80`-symbol superframe) and `net.core.netdev_budget = 640` (`8` NAPI rounds $\times$ `80` symbols).
     - `net.core.rmem_max = 4194304`, `net.core.wmem_max = 4194304`, `net.ipv4.tcp_rmem = "4096 131072 4194304"`, `net.ipv4.tcp_wmem = "4096 131072 4194304"`, and `net.ipv4.tcp_limit_output_bytes = 196608` (`192 KB` = `3` superframes of `64 KB` burst pacing, preventing TSQ starvation across `250 ms` `sa_Test` spectral scans while bounding queue bloat).
     - `/sys/class/net/ath0/tx_queue_len = 256`, `/sys/class/net/br0/tx_queue_len = 256`, `/sys/class/net/eth0/tx_queue_len = 512`, `/sys/class/net/ath0/queues/tx-0/xps_cpus = 1` (`CPU0` aligned with `skb_fpga_thread` + `IRQ 52/53`), and `/sys/class/net/br0/queues/rx-0/rps_cpus = 2`, `/sys/class/net/br1/queues/rx-0/rps_cpus = 2` (`CPU1` aligned with `IRQ 63 GMAC0`).

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Benchmark Under Active Spectral Scan Load (`CONFIRMED`)

Each trial drove concurrent Triple-Play traffic (Bulk TCP on `5201` + `25 Mbps` IPTV UDP `1316B` `TOS 0x80` on `5202` + `64 kbps` VoIP UDP `160B` `TOS 0xb8` on `5203`) + active background spectral scans across `5700/5750/5800 MHz` (`/sys/class/ame/ame_ctrl_dev/sa_Test`) + `270` `1400B` `GMAC0` ICMP echo probes to `198.18.0.48` (`Boca 8`):

| Trial / Summary | Arm ID | SoC Bulk TCP (`Mbps`) | IPTV UDP (`Mbps` / Jitter / Loss) | VoIP Jitter / Loss | Loaded `GMAC0` RTT `p50` / `p95` / `p99` (`ms`) | `IRQ 52/53` `CPU0` $\Delta$ | `scheduler` / `symbol` Giveup |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Trial 1 (`A1`)** | `S102E-ARM-A-UNPACED-SUPERFRAME-BASELINE` | `165.544` | `5.914` / `1.700 ms` / `0%` | `1.485 ms` / `0%` | `3.484` / `5.988` / `7.621` | `7,896` / `7,896` | `0` / `0` |
| **Trial 2 (`B1`)** | `S102E-ARM-B-500HZ-SUPERFRAME-TAIL-GUARD-AND-BURST-PACING` | **`200.758` (`+21.3%`)** | `7.280` / **`0.377 ms`** / `0%` | **`0.340 ms`** / `0%` | `2.647` / `5.973` / `6.378` | `7,613` / `7,614` | **`0` / `0`** |
| **Trial 3 (`A2`)** | `S102E-ARM-A-UNPACED-SUPERFRAME-BASELINE` | `184.694` | `9.689` / `1.081 ms` / `0%` | `0.449 ms` / `0%` | `2.310` / `6.614` / `12.146` | `7,806` / `7,806` | `0` / `0` |
| **Trial 4 (`B2`)** | `S102E-ARM-B-500HZ-SUPERFRAME-TAIL-GUARD-AND-BURST-PACING` | `160.400` | `8.849` / **`0.373 ms`** / `0%` | **`0.437 ms`** / `0%` | `2.793` / **`4.379` / `5.231`** | `7,519` / `7,520` | **`0` / `0`** |
| **Median (`Arm A`)** | `S102E-ARM-A-UNPACED-SUPERFRAME-BASELINE` | `175.119` | `7.801` / `1.390 ms` / `0%` | `0.967 ms` / `0%` | `2.897` / `6.301` / `9.884` | `15,702` total | `0` / `0` |
| **Median (`Arm B`)** | `S102E-ARM-B-500HZ-SUPERFRAME-TAIL-GUARD-AND-BURST-PACING` | **`180.579` (`+3.1%`, peak `200.758`)** | **`8.065` (`+3.4%`)** / **`0.375 ms` (`-73.0%`)** / `0%` | **`0.389 ms` (`-59.8%`)** / `0%` | **`2.720` (`-6.1%`) / `5.176` (`-17.9%`) / `5.805` (`-41.3%`)** | `15,132` total | **`0` / `0`** |
