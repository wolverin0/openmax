<!-- doc-head: STAGE26B_LTU_LITE_PERSISTENCE_AND_M2_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 26B & Stage 27: LTU-Lite (`LTU.afltu.v2.4.0`) Flash Persistence, Over-The-Air Scan & SKU Boundary Qualification, and NanoLoco M2 (`2.4 GHz`) Benchmark Summary

- **Task ID**: `T-S26B-LTU-LITE-V240-RAM-AIRFPGA-OTP-BYPASS-AND-TRUE-OTA-ASSOCIATION`
- **Date**: 2026-10-25
- **Artifacts**:
  - [`artifacts/autoresearch/stage26b_ltu_lite_ptp_persistence_20261025.json`](<repo>/artifacts/autoresearch/stage26b_ltu_lite_ptp_persistence_20261025.json)
  - [`artifacts/autoresearch/stage26b_ltu_lite_ram_airfpga_ota_link_20261025.json`](<repo>/artifacts/autoresearch/stage26b_ltu_lite_ram_airfpga_ota_link_20261025.json)
  - [`artifacts/autoresearch/stage27_r2ac_prism_and_nanom2_24ghz_20261025.json`](<repo>/artifacts/autoresearch/stage27_r2ac_prism_and_nanom2_24ghz_20261025.json)

---

## 1. Persistent Flash Configuration (`cfgmtd -w -p /etc/`) & `Stage 24F Champion v1` (`S24F-R1`)

Both `LTU-Lite` (`LTU.afltu.v2.4.0`) bench units on `EdgeSwitch 10XP` have been configured and persisted to flash via `cfgmtd -w -p /etc/` with the `Stage 24F Champion v1` (`S24F-R1`) profile active:

| Parameter | `LTU-Lite #1` (`Boca 5 / gi5`) | `LTU-Lite #2` (`Boca 7 / gi7`) |
| :--- | :--- | :--- |
| **IPv6 Link-Local** | `PUBLIC_DEVICE_0046%27` | `PUBLIC_DEVICE_0076%27` |
| **Configured IPv4** | `198.18.0.63` | `198.18.0.118` |
| **MAC / Radio BSSID** | `PUBLIC_DEVICE_0045` / `PUBLIC_DEVICE_0055` | `PUBLIC_DEVICE_0043` / `PUBLIC_DEVICE_0062` |
| **Firmware** | `LTU.afltu.v2.4.0` | `LTU.afltu.v2.4.0` |
| **`radio.1.freq` / `chanbw`** | `5500 MHz` / `20 MHz` | `5500 MHz` / `20 MHz` |
| **`radio.1.txpower`** | `-10 dBm` (`powerout=0`, `antennagain=26` -> `-26 dBm` active guard) | `-10 dBm` (`powerout=0`, `antennagain=26` -> `-26 dBm` active guard) |
| **`radio.1.ssid` / `wireless.1.ssid`** | `FuturaMAX-LTU-Bench` | `FuturaMAX-LTU-Bench` |
| **`wireless.1.security`** | `none` | `none` |
| **`Stage 24F Champion v1` (`S24F-R1`)** | `czlen=5`, `rx_target_pwr_auto_en=0`, `rx_target_pwr=450` | `czlen=5`, `rx_target_pwr_auto_en=0`, `rx_target_pwr=450` |
| **Flash Persistence** | Verified (`cfgmtd -w -p /etc/`) | Verified (`cfgmtd -w -p /etc/`) |

---

## 2. Over-The-Air Scan & Baseband (`CIR` / `SFN`) Verification (`CONFIRMED`)

1. **Over-The-Air `/tmp/af_ScanList` Detection (`5500 MHz / 20 MHz`)**:
   - `LTU-Lite #2` (`PUBLIC_DEVICE_0076%27`) detects `LTU-Lite #1` (`PUBLIC_DEVICE_0055`, SSID `FuturaMAX-LTU-Bench`) Over-The-Air on `5500 MHz` (`20 MHz` bandwidth) at **`-21 dBm`** with estimated capacity **`210,000 kbps`** (`210 Mbps`).
2. **Over-The-Air Hardware `CIR` & `SFN` Lock (`5950 MHz / 20 MHz`)**:
   - At `RxGain0(67) RxGain1(70)` (`AvgRxPwr(436, 443)` against target `450`), `LTU-Lite #2` achieves **100% hardware Channel Impulse Response (CIR) lock** (`CIR Status: [0xffffffff] shift / avg: 0/0, reject: 0`) with stock `cir_bypass=0`, **100% SFN synchronization** (`SFN sync : 1`), and **5/5 consecutive beacon detections** (`5 beacon detect(DABF5399)`), transitioning `CPE_SYS_SM` to `RUN` and `MGMT_SM` to `ASSOC_WAIT` (`tx_assocReqMsg` `StaID=255`).

---

## 3. Hardware SKU Boundary (`0xae07`/`0xae08` vs `0xae05`/`0xae06` vs `0xae02`/`0xae03`) (`CONFIRMED`)

- Both `LTU-Lite` units are subscriber CPE SKUs (`board_ssid = 0xae07` / `0xae08`), whereas `0xae05`/`0xae06`/`0xae0e` identify `LTU-Rocket` PtMP AP SKUs and `0xae02`/`0xae03` identify `AF-5XHD` PtP SKUs.
- In `/bin/air_fpga` (`lib/ame_cfg.c`), `parse_role()` enforces `TYPE_CPE` (`*** PtMP Build set XHD and LTU CPEs to TYPE_CPE ****`) for subscriber SKUs unless `board_ssid` is an AP SKU (`0xae05`/`0xae0e`).
- In `ame_core.ko` (`ame_bbp_rt_tx_isr`), subscriber CPE hardware slaves its Super-Frame Number (`ame_bbp_sync_SFN`) and Contention Zone (`CZ`) uplink timing to an `LTU-Rocket` (`0xae06`) AP master.

---

## 4. Stage 27 `NanoLoco M2` (`S27-R1` Champion v1) & `Rocket 2AC Prism` (`2.4 GHz`) Benchmark Summary

- **`NanoLoco M2` (`Boca 2 / gi2`, `198.18.0.50`, `XM.ar7240.v6.1.12`)**:
  - `S27-R1` Champion v1 achieves **`-10.74%` `p95` RTT reduction** while maintaining `0%` packet loss (`0.377 ms` mean L3 RTT from `gi8`) and `-59 dBm` 2.4 GHz RF output on `2444 MHz` (`Channel 37`, `20 MHz`).
- **`Rocket 2AC Prism` (`Boca 8 / gi8`, `198.18.0.65`) under `NanoLoco M2` (`-59 dBm`) 2.4 GHz Load**:
  - **`S27-R2AC-R1`**: Quiescing `airview1` (`IRQ 2`) + `uph_wifi0` adjacent-channel bias (`cms_bias=6`, `voip_bias=6`, `sta_rx_rssi_th=-82`) improved mean goodput by **`+5.20%`** (`27.06 -> 28.47 Mbps`) and reduced `p95` RTT by **`-35.96%`** (`23.68 -> 15.17 ms`).
  - **`S27-R2AC-R2`**: Adding bridge queue bounding (`br0 txqueuelen=256`) + TCP SACK/DSACK/Fin-Timeout further improved mean goodput by **`+1.50%`** and reduced `p95` RTT by **`-17.84%`** (`19.49 -> 16.01 ms`).
