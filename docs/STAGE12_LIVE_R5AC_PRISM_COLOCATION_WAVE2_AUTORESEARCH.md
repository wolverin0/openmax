<!-- doc-head: STAGE12_LIVE_R5AC_PRISM_COLOCATION_WAVE2_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 12 — Live `Rocket Prism 5AC Gen2` Co-Location Interference Wave 2 Autoresearch Benchmark (`R5AC-R9..R14`)

- **Experiment ID**: `FMX-STAGE12-R5AC-PRISM-COLOCATION-WAVE2-AUTORESEARCH`
- **Timestamp (UTC)**: `2026-10-24T22:59:09Z`
- **Target Device**: Ubiquiti `Rocket Prism 5AC Gen2` (`RP-5AC-Gen2`, `sysid=0xe7e9`, MAC `PUBLIC_DEVICE_0048`) at `198.18.0.64`
- **Architecture**: `AR934x/QCA955x` MIPS `74Kc V4.12` + `QCA9880` (`wifi0` main 5 GHz + `wifi1` dedicated AirView spectral radio) + **Active RF Prism Filter (`IRQ 64 ath_prism_filter_blanking_isr`)**
- **Firmware**: `XC.v8.7.25` (`Linux 2.6.32.68`)
- **Co-Location Environment**: Active 5 GHz indoor bench radiation from `LAP-120` (`5180 MHz`) and `PowerBeam M5 300` PtP pair (`5805 MHz`)
- **Artifact Receipt**: [`artifacts/autoresearch/r5ac_prism_colocation_wave2_live_autoresearch_20261024.json`](../artifacts/autoresearch/r5ac_prism_colocation_wave2_live_autoresearch_20261024.json)

---

## 1. Executive Summary & Hardware Control Boundary Discoveries

In Wave 2 (`R5AC-R9..R14`), we executed **6 paired `A/B/A/B` live RAM-only Autoresearch rounds** on `Rocket Prism 5AC Gen2` (`198.18.0.64`) while monitoring its hardware **Active RF Prism Blanking Filter (`IRQ 64 ath_prism_filter_blanking_isr`)**, `wifi0` (`IRQ 75`), and `wifi1` (`IRQ 2`) under live 5 GHz co-location interference from the adjacent bench radios.

### Key Hardware Control Boundary Findings (`CONFIRMED`)
1. **Hardware Prism Blanking Filter (`IRQ 64`) vs Software ANI Polling (`R5AC-R9`)**:
   - On `Rocket Prism 5AC Gen2`, the hardware Prism filter (`IRQ 64 ath_prism_filter_blanking_isr`, firing at `35–80 IRQ/s` during adjacent 5 GHz transmissions) blanks out-of-band energy in hardware (`ath0` noise floor `-96 dBm`, `airview1` `-109 dBm`).
   - When `wifi0` is in `Mode: Managed` (unassociated station scanning across 5 GHz channels), `iwpriv wifi0 ani_enable 1` performs periodic software ANI register polling across `IRQ 75` that stalls the host CPU (`p50 = 4.575 ms`, `p95 = 25.226 ms`). Disabling software ANI (`iwpriv wifi0 ani_enable 0`) while retaining the hardware Prism blanking ISR cut `p50` RTT by **`-60.5%`** (`4.575 -> 1.808 ms`) and `p95` RTT by **`-34.9%`** (`25.226 -> 16.410 ms`, `J: 18.066 -> 9.037`, **KEEP**).
2. **Bounding Software Retries Under 5 GHz Co-Location (`R5AC-R10`)**:
   - Tightening `iwpriv wifi0 nonaggr_swretry 4` and `aggr_swretry 6` (vs stock `8/8`) reduced `p50` RTT by **`-67.9%`** (`13.917 -> 4.463 ms`), `p95` RTT by **`-12.0%`** (`25.527 -> 22.459 ms`), and increased SSH stream throughput from `26.314 -> 29.255 Mbps` (`J: 27.861 -> 15.823`, **KEEP**).
3. **Station-Mode (`Mode: Managed`) Lockout of AP-Only `ubnt_poll_host` Sysctls (`R5AC-R12`, `R5AC-R14`)**:
   - Unlike `Rocket 2AC Prism` (`198.18.0.65`, where `ath0` is in `Mode: Master` and `daprot=1` / `ptp_xmit=1` stick in `/proc/sys/dev/uph_wifi0/`), `Rocket Prism 5AC Gen2` (`198.18.0.64`) has `ath0` in `Mode: Managed` (STA mode).
   - Writing `echo 1 > /proc/sys/dev/uph_wifi0/daprot` or `ptp_xmit` in STA mode is ignored by `ubnt_poll_host.ko` (`cat` immediately returns `0`), whereas `noack_mode` accepts `1` (`CONFIRMED` mode-dependent kernel sysctl gate).

---

## 2. Wave 2 Paired `A/B/A/B` Benchmark Results (`R5AC-R9..R14`)

| Round | Knob (`apply_cmd`) | Baseline (`A`) | Candidate (`B`) | `A` Mean `p50` / `p95` (ms) | `B` Mean `p50` / `p95` (ms) | `IRQ 64` Prism Blanking (/s) | `A_J -> B_J` (`delta_J`) | Decision |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`R5AC-R9`** | `iwpriv wifi0 ani_enable 0` | `ani_enable=1` | `ani_enable=0` (Prism HW blanking active) | `4.575` / `25.226` | **`1.808` / `16.410`** | `35.35 -> 42.97` | `18.066 -> 9.037` (**`-9.029`**) | **KEEP** |
| **`R5AC-R10`** | `nonaggr_swretry=4`, `aggr_swretry=6` | `8 / 8` | `4 / 6` | `13.917` / `25.527` | **`4.463` / `22.459`** | `11.06 -> 13.81` | `27.861 -> 15.823` (**`-12.038`**) | **KEEP** |
| **`R5AC-R11`** | `iwpriv wifi0 dyntxchain 1` | `dyntxchain=0` | `dyntxchain=1` | `2.890` / `23.413` | `6.046` / `25.814` | `60.45 -> 29.77` | `15.557 -> 20.848` (`+5.291`) | **REJECT** |
| **`R5AC-R12`** | `echo 1 > /proc/sys/dev/uph_wifi0/noack_mode` | `0` | `1` | `7.937` / `26.188` | `8.847` / `25.873` | `0.00 -> 0.00` | `22.501 -> 22.830` (`+0.329`) | **REJECT** |
| **`R5AC-R13`** | `ifconfig ath0/eth0 txqueuelen 128` | `256` | `128` | `8.556` / `24.933` | `7.835` / `26.489` | `0.00 -> 0.00` | `21.618 -> 22.311` (`+0.693`) | **REJECT** |
| **`R5AC-R14`** | Combined Profile (`AMPDU=64`, `tcp_low_latency=1`, `budget=600`) | Stock defaults | Combined (with `ani_enable=0`, `swretry=4/6` already active) | `4.888` / `24.456` | `8.660` / `20.759` | `0.00 -> 0.00` | `17.612 -> 18.931` (`p95` improved `-15.1%`, `p50` noisy from scan) | **REJECT** |

---

## 3. Cumulative `Rocket Prism 5AC Gen2` Findings (`R6..R14`, RAM-Only)

Across all 9 rounds executed on `Rocket Prism 5AC Gen2` (`R5AC-R6..R8` in Wave 1 + `R5AC-R9..R14` in Wave 2):
- **Kept Knobs**:
  - `ifconfig airview1 down` (`R5AC-R6`, eliminating `IRQ 2 wifi1` spectral scan interrupts while keeping `udapi-bridge` responsive).
  - `txqueuelen=256`, `net.core.rmem_max=524288`, `net.core.wmem_max=524288`, `net.ipv4.tcp_low_latency=1` (`R5AC-R7`).
  - `iwpriv wifi0 ani_enable 0` (`R5AC-R9`, avoiding software ANI register-polling stalls when hardware Prism filter blanking `IRQ 64` is active).
  - `iwpriv wifi0 nonaggr_swretry 4 && iwpriv wifi0 aggr_swretry 6` (`R5AC-R10`).
- **Rejected Knobs (Automatically Rolled Back)**:
  - `dyntxchain=1` (`R5AC-R11`), `noack_mode=1` (`R5AC-R12`), `txqueuelen=128` (`R5AC-R13`), and STA-mode `daprot/ptp_xmit` (`R5AC-R8`, `R5AC-R14`).
