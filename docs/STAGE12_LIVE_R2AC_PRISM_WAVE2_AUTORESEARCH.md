<!-- doc-head: STAGE12_LIVE_R2AC_PRISM_WAVE2_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 12 — Live `Rocket 2AC Prism` (`R2AC`) Wave 2 Autoresearch Benchmark (`R2AC-R9..R14`)

- **Experiment ID**: `FMX-STAGE12-R2AC-PRISM-WAVE2-AUTORESEARCH`
- **Timestamp (UTC)**: `2026-10-24T23:08:44Z`
- **Target Device**: Ubiquiti `Rocket 2AC Prism` (`R2AC`, `sysid=0xe7f5`, MAC `PUBLIC_DEVICE_0058`) at `198.18.0.65`
- **Architecture**: `QCA955x/AR934x` MIPS `74Kc V4.12` + `QCA988x` 2.4 GHz 802.11ac-wave1 (`wifi0` main AP radio on `2412 MHz`, `Mode: Master`) + dedicated `wifi1` (`airview1`) spectral scanner + **2.4 GHz Active RF AirPrism Filter (`IRQ 64 ath_prism_filter_blanking_isr`)**
- **Firmware**: `2XC.v8.7.11` (`Linux 2.6.32.68`)
- **Artifact Receipt**: [`artifacts/autoresearch/r2ac_prism_wave2_live_autoresearch_20261024.json`](../artifacts/autoresearch/r2ac_prism_wave2_live_autoresearch_20261024.json)

---

## 1. Executive Summary & Architectural Contrast (`2.4 GHz AP Mode` vs `5 GHz STA Scan Mode`)

In Wave 2 (`R2AC-R9..R14`), we executed **6 paired `A/B/A/B` live RAM-only rounds** on `Rocket 2AC Prism` (`198.18.0.65`, operating as a 2.4 GHz `Mode: Master` AP on `2412 MHz`) to test whether the Wave 3 findings from `Rocket Prism 5AC Gen2` (`198.18.0.64`, operating as an unassociated 5 GHz `Mode: Managed` STA) transfer across bands and MAC modes.

### Confirmed Hardware Control Boundaries (`CONFIRMED`)
1. **Why `iwpriv wifi0 ani_enable 0` is `REJECT` on 2.4 GHz AP (`R2AC-R9`) but `KEEP` on 5 GHz Scanning STA (`R5AC-R9`)**:
   - On `Rocket 2AC Prism` (`Mode: Master`, fixed channel `2412 MHz` in congested 2.4 GHz indoor spectrum), disabling software ANI (`iwpriv wifi0 ani_enable 0`) **degraded `p50` RTT by `+334%`** (`1.856 -> 8.063 ms`, `J: 11.252 -> 22.306`, **REJECT**, automatically restored to `ani_enable=1`).
   - **Physical Mechanism**: Hardware `AirPrism` (`IRQ 64`) filters out-of-channel interference outside the 20 MHz passband, but in-band 2.4 GHz noise (co-channel Wi-Fi beacons, BLE, microwave energy inside `2402–2422 MHz`) passes through the `AirPrism` passband and requires `QCA988x` Adaptive Noise Immunity (`ani_enable=1`) to adjust CCK/OFDM weak-signal detection thresholds. In contrast, on `Rocket Prism 5AC Gen2` in unassociated `Mode: Managed` scanning across quiet 5 GHz channels, software ANI register polling stalls channel switches.
2. **Clean `airview1` Administrative Quiesce Without `SIGSTOP` (`R2AC-R10`)**:
   - In Wave 1 (`R2AC-R8`), sending `SIGSTOP` to `ubntspecd` stalled `udapi-bridge` IPC sockets (`p95 = 123.7 ms`).
   - In Wave 2 (`R2AC-R10`), bringing `airview1` down (`ifconfig airview1 down` while leaving `ubntspecd` running) reduced `p50` RTT by **`-77.0%`** (`10.146 -> 2.337 ms`, `J: 22.920 -> 12.216`, **KEEP**) with zero `udapi-bridge` IPC stalls (`p95 = 23.026 ms`). `airview1` was restored to `UP` after the round to maintain spectral telemetry.
3. **AP-Mode (`Mode: Master`) Acceptance of `/proc/sys/dev/uph_wifi0/daprot` (`R2AC-R11`)**:
   - Unlike `Rocket Prism 5AC Gen2` (where `ath0` is in `Mode: Managed` and `daprot` rejects writes, returning `0`), `Rocket 2AC Prism` (`Mode: Master`) accepts `echo 1 > /proc/sys/dev/uph_wifi0/daprot` (`verified_apply_state: "1"`). However, with zero associated CPEs on the AP, `daprot=1` added polling-protection overhead (`p50: 1.671 -> 4.870 ms`) and was **REJECTED** for zero-client idle operation.
4. **2.4 GHz Short Preamble (`shpreamble=1`) & Queue/Buffer Right-Sizing (`R2AC-R12`, `R2AC-R13`)**:
   - Enabling `iwpriv ath0 shpreamble 1` (`R2AC-R12`) cut `p50` RTT by **`-54.3%`** (`4.309 -> 1.968 ms`) and `p95` RTT by **`-7.8%`** (`25.368 -> 23.392 ms`, `J: 16.291 -> 11.877`, **KEEP**).
   - Tightening `ath0`/`eth0` `txqueuelen=256` with `rmem_max=524288`, `wmem_max=524288`, `netdev_max_backlog=2500` (`R2AC-R13`) further reduced `p50` RTT by **`-30.2%`** (`2.439 -> 1.702 ms`, `J: 11.855 -> 11.080`, **KEEP**).

---

## 2. Wave 2 Paired `A/B/A/B` Benchmark Results (`R2AC-R9..R14`)

| Round | Knob (`apply_cmd`) | Baseline (`A`) | Candidate (`B`) | `A` Mean `p50` / `p95` (ms) | `B` Mean `p50` / `p95` (ms) | `A -> B` SSH Stream (Mbps) | `A_J -> B_J` (`delta_J`) | Decision |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`R2AC-R9`** | `iwpriv wifi0 ani_enable 0` | `ani_enable=1` | `ani_enable=0` | `1.856` / `23.356` | `8.063` / `25.658` | `30.806 -> 28.801` | `11.252 -> 22.306` (`+11.054`) | **REJECT** |
| **`R2AC-R10`** | `ifconfig airview1 down` (no `SIGSTOP`) | `airview1 UP` | `airview1 DOWN` | `10.146` / `22.177` | **`2.337` / `23.026`** | `31.141 -> 28.361` | `22.920 -> 12.216` (**`-10.704`**) | **KEEP** |
| **`R2AC-R11`** | `echo 1 > /proc/sys/dev/uph_wifi0/daprot` | `0` | `1` (AP Mode: Master) | `1.671` / `22.921` | `4.870` / `24.473` | `30.899 -> 27.998` | `10.696 -> 16.950` (`+6.254`) | **REJECT** |
| **`R2AC-R12`** | `iwpriv ath0 shpreamble 1` + `chainmask 3/3` | `shpreamble=0` | `shpreamble=1` | `4.309` / `25.368` | **`1.968` / `23.392`** | `29.968 -> 28.398` | `16.291 -> 11.877` (**`-4.414`**) | **KEEP** |
| **`R2AC-R13`** | `txqueuelen=256`, `rmem/wmem=512KB`, `backlog=2500` | `1000 / 128KB` | `256 / 512KB / 2500` | `2.439` / `22.553` | **`1.702` / `23.180`** | `29.639 -> 29.889` | `11.855 -> 11.080` (**`-0.775`**) | **KEEP** |
| **`R2AC-R14`** | Combined Candidate (including `ani=0`, `daprot=1`) | Stock defaults | Combined (penalized by `ani=0` + `daprot=1` in `B1`) | `4.303` / `23.129` | `6.995` / **`20.654`** | `28.912 -> 30.950` (**`+7.0%`**) | `15.128 -> 17.315` (`+2.187`) | **REJECT** |
