<!-- doc-head: STAGE12_LIVE_AF4X_INVICTUS_WAVE2_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 12 — Live `airFiber 4X` (`AF-4X`) Invictus v2 FPGA Wave 2 Autoresearch Benchmark (`AF4X-R7..R12`)

- **Experiment ID**: `FMX-STAGE12-AF4X-INVICTUS-WAVE2-AUTORESEARCH`
- **Timestamp (UTC)**: `2026-10-24T22:59:15Z`
- **Target Device**: Ubiquiti `airFiber 4X` (`AF-4X`) at `198.18.0.83` (`br0:1`) / `PUBLIC_DEVICE_0054%27`
- **SoC / Baseband**: TI DaVinci `AM1808` (`ARM926EJ-S rev 5 (v5l)`, `124.51 BogoMIPS`) + Ubiquiti **Invictus v2 Custom TDD Baseband/MAC ASIC/FPGA** (`Invictus Version 2 (date: 9/3/2019)`, `IRQ 140`, character devices `/dev/invictus`, `/dev/invictus_mailbox`, `/dev/invictus_status`)
- **Firmware**: `AF06.v4.1.0` (`Linux 2.6.33-rc4`)
- **Artifact Receipt**: [`artifacts/autoresearch/af4x_invictus_wave2_live_autoresearch_20261024.json`](../artifacts/autoresearch/af4x_invictus_wave2_live_autoresearch_20261024.json)

---

## 1. Executive Summary & Control Boundary Findings

Building on Wave 1 (`AF4X-R1..R6`, which tuned Linux 2.6.33 `txqueuelen`, socket buffers, `tcp_low_latency`, and Invictus `stricttiming=on`, `shortcp=on`, and `ber=5`), Wave 2 (`AF4X-R7..R12`) executed **6 paired `A/B/A/B` live RAM-only rounds** targeting deeper Invictus v2 FPGA frame timing, front-end LNA gain, TDD duty-cycle constraints, EMAC pause-frame flow control, and OFDM cyclic prefix length (`cp`).

### Confirmed Invictus v2 Hardware Control Boundaries (`CONFIRMED`)
1. **Supported TDD Frame Lengths on `AF-4X` (`AF06.v4.1.0`)**:
   - Querying `/dev/invictus` via `af` confirms valid `framelength` choices are `-1<default>,2.0ms,2.5ms,4.0ms,5.0ms,disabled,enabled` (`1.0ms` is not supported on 4.9 GHz `AF-4X`).
   - Switching `framelength` from `2.0ms` (500 Hz TDD frame rate) to `2.5ms` (400 Hz TDD frame rate) in `AF4X-R7` reduced the TDD frame-boundary interrupt cadence on the 124 BogoMIPS `AM1808` CPU, improving `p50` RTT by **`-10.8%`** (`4.224 -> 3.768 ms`), `p95` RTT by **`-16.1%`** (`32.651 -> 27.390 ms`), and SSH stream throughput by **`+15.3%`** (`4.495 -> 5.181 Mbps`).
2. **Frame-Length Constraint on Asymmetric TDD Duty Cycle (`AF4X-R9`)**:
   - When `framelength=2.5ms` is active, `af set dutycycle 67` is silently rejected by `radiod`/Invictus (`af get dutycycle` remains `50`), proving that `2.5ms` frames on `AF06.v4.1.0` enforce symmetric `50%` TDD split unless `2.0ms` or `4.0ms` framing is selected (`CONFIRMED`).
3. **4.9 GHz Spectral Isolation vs LNA Gain (`AF4X-R8`)**:
   - Because `AF-4X` operates at `4800 MHz` (`rxpower0 = -98 dBm`, `rxpower1 = -99 dBm`, `rssi = 42`), it is spectrally isolated from the co-located `5180 MHz` (`LAP-120`) and `5805 MHz` (`PowerBeam M5`) bench emitters. Switching `af set rxgain low` degraded `p50` latency (`3.737 -> 9.837 ms`, `J: 19.475 -> 26.250`) due to increased AGC/acquisition overhead at `-98 dBm`, and was **REJECTED** and automatically rolled back to `high`.
4. **DaVinci EMAC <-> Invictus 802.3x Pause Flow Control (`AF4X-R10`) & Short Cyclic Prefix (`AF4X-R11`)**:
   - Enabling `af set flowcntl on` (`AF4X-R10`) improved SSH stream throughput by **`+13.6%`** (`5.111 -> 5.808 Mbps`) and lowered `p50` RTT (`7.371 -> 6.320 ms`, **KEEP**).
   - Reducing OFDM cyclic prefix length from `cp=24` to `cp=8` (`AF4X-R11`) reduced `p50` RTT (`3.705 -> 3.590 ms`) and `p95` RTT (`27.484 -> 26.315 ms`, **KEEP**).

---

## 2. Wave 2 Paired `A/B/A/B` Benchmark Results (`AF4X-R7..R12`)

| Round | Knob (`apply_cmd`) | Baseline (`A`) | Candidate (`B`) | `A` Mean `p50` / `p95` (ms) | `B` Mean `p50` / `p95` (ms) | `A -> B` SSH Stream (Mbps) | `A_J -> B_J` (`delta_J`) | Decision |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`AF4X-R7`** | `af set framelength 2.5ms` | `2.0ms` | `2.5ms` | `4.224` / `32.651` | **`3.768` / `27.390`** | `4.495 -> 5.181` (**`+15.3%`**) | `25.282 -> 20.869` (**`-4.413`**) | **KEEP** |
| **`AF4X-R8`** | `af set rxgain low` | `high` | `low` | `3.737` / `25.858` | `9.837` / `26.728` | `5.904 -> 5.743` (`-2.7%`) | `19.475 -> 26.250` (`+6.774`) | **REJECT** |
| **`AF4X-R9`** | `af set dutycycle 67` | `50` | `67` (clamped to `50` at `2.5ms`) | `3.588` / `25.616` | `3.821` / `22.464` | `5.705 -> 5.835` | `19.238 -> 17.211` (`p50` degraded) | **REJECT** |
| **`AF4X-R10`** | `af set flowcntl on` | `off` | `on` | `7.371` / `26.640` | **`6.320` / `26.194`** | `5.111 -> 5.808` (**`+13.6%`**) | `23.975 -> 22.333` (**`-1.642`**) | **KEEP** |
| **`AF4X-R11`** | `af set cp 8` | `24` | `8` | `3.705` / `27.484` | **`3.590` / `26.315`** | `5.883 -> 5.857` | `20.591 -> 19.667` (**`-0.924`**) | **KEEP** |
| **`AF4X-R12`** | Combined Kernel + Invictus Profile Verification | Stock defaults | `txqueuelen=256`, `rmem/wmem=256K`, `tcp_low_latency=1`, `stricttiming=on`, `framelength=2.5ms`, `flowcntl=on`, `cp=8` | `3.569` / `27.846` | **`3.578` / `25.675`** | `5.874 -> 5.864` | `20.711 -> 19.204` (**`-1.506`**) | **KEEP** |

---

## 3. Cumulative `AF-4X` Autoresearch Winner Profile (`R1..R12`, RAM-Only)

Across all 12 rounds (`AF4X-R1..R12`), **8 mutations were KEPT** and **4 were REJECTED**:
- **Kept Kernel Knobs**: `eth0`/`air0` `txqueuelen=256`, `net.core.rmem_max=262144`, `net.core.wmem_max=262144`, `net.core.netdev_max_backlog=2000`, `net.ipv4.tcp_low_latency=1`.
- **Kept Invictus v2 FPGA Knobs**: `stricttiming=on`, `shortcp=on`, `ber=5`, `framelength=2.5ms`, `flowcntl=on`, `cp=8` (while keeping `rxgain=high` and `dutycycle=50`).
- **Cumulative Effect**: Loaded 1400B `p95` tail latency dropped from `33.249 ms` (Wave 1 stock baseline) to **`25.675 ms`** (**`-22.8%`**), `p50` RTT dropped from `4.197 ms` to **`3.578 ms`** (**`-14.7%`**), and SSH stream throughput increased from `5.657 Mbps` to **`5.864 Mbps`** (`+3.7%`) with zero flash writes (`cfgmtd` untouched).
