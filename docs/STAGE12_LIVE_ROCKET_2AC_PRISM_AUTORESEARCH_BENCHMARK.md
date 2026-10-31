<!-- doc-head: STAGE12_LIVE_ROCKET_2AC_PRISM_AUTORESEARCH_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 12 — Live `Rocket 2AC Prism` (`2XC.v8.7.11`) 2.4 GHz AirPrism/AirView Architecture & 8-Round `A/B/A/B` Autoresearch Benchmark

## 1. Executive Summary

- **Experiment ID**: `FMX-STAGE12-R2AC-PRISM-LIVE-AUTORESEARCH`
- **Target Hardware**: Ubiquiti `Rocket 2AC Prism` (`R2AC-PRISM`, `board.sysid=0xe2f2`, `MAC PUBLIC_DEVICE_0042`, IP `198.18.0.65`, Firmware `2XC.v8.7.11`)
- **Receipt Artifact**: [`r2ac_prism_live_autoresearch_20261024.json`](<repo>/artifacts/autoresearch/r2ac_prism_live_autoresearch_20261024.json)
- **Key Outcome**:
  1. **Dual-Radio + AirPrism + GPS Hardware Mapping (`CONFIRMED`)**:
     - Host SoC: `QCA9558` (`cpurevision=0x00001130`, MIPS `2.6.32.68`).
     - Primary Radio (`wifi0`): `QCA988x` PCI (`0777:e2f2`) operating in 2.4 GHz (`devdomain=2400`, `txpower.max=27 dBm`, `chanbw=10,20,40 MHz`) with **AirPrism** active RF filter (`i2c_gpio_ath` + `IRQ 64 ATH GPIO ath-spectral-filter`).
     - Auxiliary Radio (`wifi1` / `airview1`): `QCA9558` AHB (`0777:e2f2`) dedicated spectral scanner driven by `/bin/ubntspecd -w -t -g -i wifi1 -j airview1 -m 4 -f 20 -s 200` (`IRQ 2 dummy wifi1`).
     - GPS Receiver: Live fix via `/usr/bin/ubnt-gps-reader -i /dev/ttyS1 -o /proc/sys/dev/uph/gps_info` (`IRQ 22 ATH MISC hs-uart`, live coordinates `-33.915243, -60.634120`, alt `101.00 m`).
  2. **Causal Discovery on `SIGSTOP ubntspecd` vs `udapi-bridge` (`R2AC-R1` `CONFIRMED`)**:
     - Freezing `ubntspecd` with `SIGSTOP` (`R2AC-R1`) eliminates `IRQ 2 (wifi1)` (`1007.4/s -> 0.0/s`), **but** causes `udapi-bridge` to block on the frozen `ubntspecd` IPC socket, increasing control-plane `p50` RTT from `2.25 ms` to `9.85 ms` (`REJECT`, automatically restored). Furthermore, `IRQ 64 (ath-spectral-filter)` continues firing (`26.5 -> 53.8/s`) whenever `wifi0` (`wpa_supplicant` on `ath0`) scans 2.4 GHz channels, proving that `IRQ 64` tracks **both** `wifi0` AirPrism filter tuning/blanking and `wifi1` scanning.
  3. **8-Round Paired `A/B/A/B` Live Autoresearch (`CONFIRMED`)**:
     - **3 rounds (`R2AC-R4` `ptp_xmit=1`, `R2AC-R7` `tcp_low_latency=1 + netdev_budget=600`, `R2AC-R8` `nonaggr_swretry=4 + aggr_swretry=6`) were `KEEP`**, while 5 rounds that regressed `p50` or `p95` under the strict guard were `REJECT` and automatically rolled back.

---

## 2. Live Hardware & `/proc/sys/dev/uph_wifi0` Control Surface (`198.18.0.65`)

| Component / Path | Live Value / State on `198.18.0.65` | Role |
| :--- | :--- | :--- |
| **`/proc/interrupts` `IRQ 2`** | `8,125,966` (`dummy wifi1`, `0–1162 irq/s`) | AHB `wifi1` (`airview1`) spectral scan bursts |
| **`/proc/interrupts` `IRQ 22`** | `5,717,106` (`ATH MISC hs-uart`, `0–704 irq/s`) | 9600-baud UART GPS NMEA stream (`/dev/ttyS1`) |
| **`/proc/interrupts` `IRQ 64`** | `795,769` (`ATH GPIO ath-spectral-filter`, `14–79 irq/s`) | AirPrism 2.4 GHz filter switching / blanking GPIO interrupt |
| **`/proc/interrupts` `IRQ 75`** | `1,542,041` (`ATH PCI wifi0`, `28–97 irq/s`) | Primary `QCA988x` 2.4 GHz radio PCI interrupt |
| **`/proc/sys/dev/uph_wifi0/`** | `enable=1`, `noack_mode=1`, `daprot=0`, `ptp_xmit=0`, `sta_priority=1 2 0` | `ubnt_poll_host` (`150,776` B) runtime sysctl knobs |
| **`iwpriv wifi0`** | `AMPDU=1`, `AMPDUFrames`, `AMPDULim`, `LDPC`, `txchainmask=3`, `rxchainmask=3`, `nonaggr_swretry`, `aggr_swretry` | `umac.ko` (`2,120,921` B) + `ath_dev.ko` (`224,447` B) driver knobs |

---

## 3. 8-Round Paired `A/B/A/B` Live Autoresearch Results (`198.18.0.65`)

| Round | Knob / Command Mutation | `A` Mean `p50` / `p95` (ms) | `B` Mean `p50` / `p95` (ms) | `IRQ 64` (`A` $\rightarrow$ `B` `/s`) | Mean $J$ (`A` $\rightarrow$ `B`) | $\Delta J$ | Decision |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`R2AC-R1`** | `kill -STOP $(pidof ubntspecd)` vs active `-f 20 -s 200` | `2.255` / `24.419` | `9.854` / `19.873` | `26.50` $\rightarrow$ `53.77` | `15.1466` $\rightarrow$ `19.4646` | `+4.3180` | **`REJECT` (Restored)** |
| **`R2AC-R2`** | `iwpriv wifi0 AMPDUFrames 64 && iwpriv wifi0 AMPDULim 65535` | `2.320` / `26.084` | `2.463` / **`21.533`** | `20.06` $\rightarrow$ `16.73` | `16.4645` $\rightarrow$ `13.1838` | `-3.2807` | **`REJECT` (`p50` +6.1% > +4% guard; Rolled Back)** |
| **`R2AC-R3`** | `echo 1 > /proc/sys/dev/uph_wifi0/daprot` | `1.770` / `16.438` | `1.661` / `22.316` | `27.39` $\rightarrow$ `28.51` | `8.9731` $\rightarrow$ `13.0826` | `+4.1095` | **`REJECT` (Rolled Back to `0`)** |
| **`R2AC-R4`** | `echo 1 > /proc/sys/dev/uph_wifi0/ptp_xmit` | `8.534` / `24.352` | **`5.119`** / **`21.398`** | `52.35` $\rightarrow$ **`33.12`** | `21.4221` $\rightarrow$ **`16.0310`** | **`-5.3911`** | **`KEEP`** |
| **`R2AC-R5`** | `ifconfig ath0 txqueuelen 256 && ifconfig eth0 txqueuelen 256` | `7.186` / `26.306` | `7.683` / `25.239` | `9.28` $\rightarrow$ `39.86` | `21.6053` $\rightarrow$ `20.9148` | `-0.6905` | **`REJECT` (`p50` guard; Rolled Back)** |
| **`R2AC-R6`** | `sysctl net.core.rmem_max=524288 wmem_max=524288 netdev_max_backlog=2500` | `7.239` / `26.153` | `8.262` / `24.855` | `58.92` $\rightarrow$ `29.60` | `21.1801` $\rightarrow$ `21.2874` | `+0.1073` | **`REJECT` (Rolled Back)** |
| **`R2AC-R7`** | `sysctl net.ipv4.tcp_low_latency=1 net.core.netdev_budget=600` | `6.942` / `22.709` | **`6.602`** / **`22.244`** | `15.10` $\rightarrow$ `23.01` | `18.3032` $\rightarrow$ **`17.6512`** | **`-0.6520`** | **`KEEP`** |
| **`R2AC-R8`** | `iwpriv wifi0 nonaggr_swretry 4 && iwpriv wifi0 aggr_swretry 6` | `8.525` / `25.432` | **`7.133`** / **`24.354`** | `78.73` $\rightarrow$ **`29.01`** | `21.4841` $\rightarrow$ **`19.2740`** | **`-2.2101`** | **`KEEP`** |
