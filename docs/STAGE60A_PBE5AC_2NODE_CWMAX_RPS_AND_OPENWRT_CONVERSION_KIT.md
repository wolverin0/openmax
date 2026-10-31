<!-- doc-head: STAGE60A_PBE5AC_2NODE_CWMAX_RPS_AND_OPENWRT_CONVERSION_KIT.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 60A — PowerBeam 5AC Gen2 (`0xe3d6`) 2-Node PtP `CWmin/CWmax`, `RPS` & `IRQ 33` Spectral Filter OTA Benchmark + Zero-Touch OpenWrt `24.10.4` Conversion Kit (`T-S60A-PBE5AC-AIROS-GROUND-UP-40MHZ-AND-SPECTRAL-FILTER-OTA-BENCH-PLUS-OPENWRT-PRECONFIG`)

## 1. Hardware Interrupt (`IRQ 33` Spectral Filter) & Softnet Discovery on `PBE-5AC-Gen2` (`CONFIRMED`)

Across the 12 counterbalanced Triple-Play windows (`198.18.0.45 [198.18.0.8] <-> 5205 MHz OTA <-> 198.18.0.46 [198.18.0.74]`):
- **`IRQ 33: ATH GPIO ath-spectral-filter`**: Fired **`+147,926` times** on `.241` (`7,112,477 -> 7,260,403` / `12,047,779 -> 12,195,705`, `~1,640 Hz`) and **`+161,898` times** on `.242` while background AirView (`airview=3`) is active on `WA.v8.7.11`.
- **`IRQ 64: ATH PCI wifi0` (`QCA9882` 5 GHz)**: Fired **`+69,543` times** on `.241` during the 12 windows.
- **`IRQ 4: MIPS eth0` (`AR8035` Gigabit PHY)**: Fired **`+2,722` times** on wired `.241` and **`0` times** on standalone PoE `.242` (confirming `eth0` carrier absence `plugged=false` on `.242`).
- **`/proc/net/softnet_stat`**: `0` packet drops (`dropped = 0`) across all 12 windows on both `.241` (`processed: 692,977 -> 887,271`) and `.242`.

---

## 2. 12-Window Counterbalanced OTA Benchmark Results (`A1 -> B1 -> A2 -> B2`, `15` Loaded Ping Samples/Window)

Artifact: [`artifacts/autoresearch/stage60a_pbe5ac_2node_cwmax_and_rps_ota_bench_20261026.json`](../artifacts/autoresearch/stage60a_pbe5ac_2node_cwmax_and_rps_ota_bench_20261026.json)

| Round | Treatment & Verified Readbacks | Aggregate Goodput (`A -> B`) | Bulk TCP (`A -> B`) | Loaded `p50` RTT (`A -> B`) | Loaded `p95` / `p99` RTT (`A -> B`) | IPTV Jitter / Loss (`A -> B`) | VoIP Jitter / Loss (`A -> B`) | Key Finding |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`S60A-R1`** | `RPS` (`rps_cpus=1`) + `txq=192` + `budget=600` + `ampdu=24` + `ack=25us` | `23.112 -> 21.724 Mbps` (`-6.01%`) | `15.190 -> 13.761 Mbps` (`-9.41%`) | `2.604 -> 3.183 ms` | **`10.102 -> 8.378 ms` (`-17.07%` `p95`)** / **`13.451 -> 9.005 ms` (`-33.05%` `p99`)** | **`1.075 -> 0.772 ms` (`-28.19%`)** / `0.013%` | **`0.897 -> 0.839 ms` (`-6.47%`)** / `0.00%` | `ampduFrames=24` cuts `p95` RTT `-17.1%` and `p99` RTT `-33.1%`, but reduces TCP goodput vs 32 frames. |
| **`S60A-R2`** | `txq=160` + 2-Node PtP `AC_BE` `cwmin=3, cwmax=7` (`get_cwmin:3, get_cwmax:7`) | `20.886 -> 20.812 Mbps` (`-0.35%`) | `12.941 -> 12.886 Mbps` (`-0.43%`) | `2.441 -> 2.721 ms` | `9.873 -> 13.904 ms` | **`0.738 -> 0.383 ms` (`-48.10%`)** / **`0.00%`** | **`2.507 -> 1.020 ms` (`-59.30%`)** / **`0.00%`** | Cuts TCP retransmits `-29.1%` (`43 -> 30.5`), IPTV jitter `-48.1%`, and VoIP jitter `-59.3%` (`0.0%` loss). |
| **`S60A-R3`** | **2-Node PtP `AC_BE` `cwmin=3, cwmax=6` (`get_cwmin:3, get_cwmax:6`) + `ampdu=32` + `txq=192` + `budget=600` + `RPS`** | **`22.090 -> 24.314 Mbps` (`+10.07%`, `B2=26.861 Mbps`)** | **`14.115 -> 16.370 Mbps` (`+15.98%`, `B2=18.928 Mbps`)** | `2.396 -> 2.489 ms` | `6.842 -> 18.949 ms` (`B2=10.205 ms`) | **`0.484 -> 0.372 ms` (`-23.14%`)** / **`0.00%` (vs `0.014%` A)** | `1.408 -> 1.442 ms` / **`0.00%`** | **`+15.98%` Bulk TCP and `+10.07%` Aggregate Goodput with `0.00%` IPTV/VoIP loss (`-23.14%` IPTV jitter).** |

### Native `cfgmtd -w -p /etc/` Persistence Receipts (`CFGMTD_RC=0`)
- **`.241` (`FMX-PBE5AC-AP-ETH3`)**: `Storing Active[1] ... [%100] Active->Backup[2] ... [%100] CFGMTD_RC=0`, `md5sum /etc/persistent/rc.poststart = 02400076a36a0aec1c5dd559ff9ed14e`
- **`.242` (`FMX-PBE5AC-STA-ETH7`)**: `Storing Active[2] ... [%100] Active->Backup[1] ... [%100] CFGMTD_RC=0`, `md5sum /etc/persistent/rc.poststart = 483d923107ad4038010415a87bd6413e`

---

## 3. Zero-Touch Pre-Configured OpenWrt `24.10.4` PtP Conversion Kit (`FMX-STAGE60A-PBE5AC-GEN2-OPENWRT-24.10.4-PTP-KIT`)

Built and validated via [`tools/deploy/prepare_pbe5ac_openwrt_ptp_conversion_kit.py`](../tools/deploy/prepare_pbe5ac_openwrt_ptp_conversion_kit.py) into [`firmware/openwrt/pbe5ac_gen2_ptp_kit/`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/):
- **AP Profile (`99-fmx-pbe5ac-ptp-ap`, SHA-256 `2382fb9a53d5eac825c4906f2724b7b8b21f2aae6cd268d169d3a382be09b90d`)**: Configures `198.18.0.45/24` + `198.18.0.8/24`, `WDS 4-addr AP` (`ssid='FMX-PBE5AC-PTP'`, `channel='40'`, `VHT20`, `24 dBm`), and **Stage 55A Champion v19** (`eth0` BQL `limit_min=4542, limit_max=42392, hold_time=800`, `fq_quantum=4542`, `dev_weight_tx_bias=2`).
- **STA Profile (`99-fmx-pbe5ac-ptp-sta`, SHA-256 `67d4adfe38e7a8357aaa4dfca6b10a3b0577fa88f4292da266f38507977560db`)**: Configures `198.18.0.46/24` + `198.18.0.74/24`, `WDS 4-addr STA` (`ssid='FMX-PBE5AC-PTP'`, `channel='40'`, `VHT20`, `24 dBm`), and **Stage 55A Champion v19** (`eth0` BQL `limit_min=4542, limit_max=42392, hold_time=800`, `fq_quantum=1514`, `dev_weight_tx_bias=2`), preventing `.242` from ever being stranded over-the-air by OpenWrt's default `disabled='1'`.
