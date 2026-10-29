<!-- doc-head: Consolidated 3-way hardware benchmark comparing Stock airOS 8 vs Tuned airOS 8 vs OpenWrt 24.10.4 openMAX Champion on PtP and PtMP links -->
Covers counterbalanced A1->B1->A2->B2 Triple-Play measurements (Stages 12, 53A, 54A, 55A, 72A, 85A, 491A, 773A, Wave 337/338) and links to installable scripts.
<!-- /doc-head -->

# 3-Way Hardware Benchmark: Stock `airOS 8` vs. Tuned `airOS 8` vs. `OpenWrt 24.10.4` Champion

This document consolidates the physical 3-way hardware measurements across the **openMAX** testbed and live WISP sectors comparing:
1. **Arm 1 — Stock `airOS 8` (`v8.7.11 / v8.7.25`)**: Factory Ubiquiti TDMA (`ubnt_poll_host.ko`), `Linux 3.3.8`, `tx_queue_len=1000`, `netdev_budget=300`, `ampdu=32`, no FQ-CoDel or AQL.
2. **Arm 2 — Tuned `airOS 8` (`openMAX rc.poststart` Kit)**: Stock `airOS 8` firmware tuned in place via [`firmware/public_field_kits/airos8_ptp_ptmp_tuned_champion.sh`](../firmware/public_field_kits/airos8_ptp_ptmp_tuned_champion.sh) (`tx_queue_len=192`, `netdev_budget=600`, `ampduFrames=24`, WMM `AC_VI`/`AC_VO` EDCA tightening, `rmmod ath_pktlog`, `vow_extstats=0`).
3. **Arm 3 — `OpenWrt 24.10.4` (`Linux 6.6.110`) + `openMAX` Champion**: Native `mac80211` + `ath10k` tuned via [`firmware/public_field_kits/openwrt24_ptp_ptmp_champion.sh`](../firmware/public_field_kits/openwrt24_ptp_ptmp_champion.sh) (`FQ-CoDel` capped at `4 MiB`, `fq_quantum=4542/1514`, per-AC `AQL` `VO=300/600`, `VI=1000/2000`, `BE=1500/3000`, `aql_threshold=5000`, Ethernet `BQL` `4542..42392` / `8192`, `CoTSQ tcp_limit_output_bytes=65536`, `vm.min_free_kbytes=4096`, `oom_score_adj=-900`).

---

## 1. Dedicated PtP Comparison (`PowerBeam 5AC Gen2` & `LiteBeam 5AC Gen2`, Triple-Play Load)

All PtP rounds were executed using counterbalanced `A1 -> B1 -> A2 -> B2` windows under simultaneous **Triple-Play saturation**: Bulk TCP + `8.0 Mbps` IPTV UDP (`DSCP CS4`, `1316B`) + `64 kbps` VoIP G.711 (`DSCP EF`, `160B`) + concurrent ICMP probes (`20 MHz` VHT20 & `40 MHz` VHT40).

| Metric (`PowerBeam 5AC Gen2` / `LiteBeam 5AC Gen2` PtP) | 1. Stock `airOS 8` (Factory Default) | 2. Tuned `airOS 8` (`airos8_ptp_ptmp_tuned_champion.sh`) | 3. `OpenWrt 24.10.4` + `openMAX` Champion (`openwrt24_ptp_ptmp_champion.sh`) | Primary Source / Stage |
| :--- | :---: | :---: | :---: | :--- |
| **Unloaded RF RTT (`p50` / `p95`)** | `1.96 ms` / `7.56 ms` | `1.63 ms` / `4.80 ms` | **`1.59 ms` / `2.68 ms` (`-64.6%` `p95`)** | [Stage 491A](STAGE491A_PBE5AC_PTP_COMPLETE_DOSSIER_AND_SCORECARD.md) |
| **Loaded RTT under Triple-Play (`p50`)** | `13.78 – 18.78 ms` | **`7.95 – 14.36 ms` (`-42.3%`)** | **`1.59 – 6.33 ms` (`-66%` to `-88%`)** | [Stage 53A](STAGE53A_PBE5AC_PTP_OTA_AUTORESEARCH_BENCHMARK.md) · [Stage 54A](STAGE54A_LITEBEAM_AND_PBE5AC_PTP_AUTORESEARCH_BENCHMARK.md) · [Stage 491A](STAGE491A_PBE5AC_PTP_COMPLETE_DOSSIER_AND_SCORECARD.md) |
| **Loaded Tail RTT under Triple-Play (`p95` / `p99`)** | `25.00 – 34.32 ms` / `36.21 ms` | **`15.76 – 17.05 ms` (`-50.3%` `p95`)** / `16.65 ms` | **`2.68 – 13.40 ms` (`-61%` to `-89%` `p95`)** | [Stage 53A](STAGE53A_PBE5AC_PTP_OTA_AUTORESEARCH_BENCHMARK.md) · [Stage 54A](STAGE54A_LITEBEAM_AND_PBE5AC_PTP_AUTORESEARCH_BENCHMARK.md) · [Stage 491A](STAGE491A_PBE5AC_PTP_COMPLETE_DOSSIER_AND_SCORECARD.md) |
| **VoIP (`G.711 DSCP EF`) Jitter / Loss** | `1.554 ms` / `0.0%` | **`0.714 ms` (`-54.1%` jitter)** / `0.0%` | **`0.420 – 0.710 ms`** / **`0.0%` loss** | [Stage 53A](STAGE53A_PBE5AC_PTP_OTA_AUTORESEARCH_BENCHMARK.md) · [Stage 55A](STAGE55A_M34_M35_BQL_HOLDTIME_AND_OPENWRT_PTP_PROFILE_BENCHMARK.md) |
| **IPTV (`8 Mbps CBR DSCP CS4`) Jitter / Loss** | `0.479 ms` / `0.040 – 0.657%` | **`0.115 – 0.427 ms` (`-27.7%`)** / `0.026%` | **`0.110 – 0.301 ms`** / **`0.000%` loss** | [Stage 53A](STAGE53A_PBE5AC_PTP_OTA_AUTORESEARCH_BENCHMARK.md) · [Stage 54A](STAGE54A_LITEBEAM_AND_PBE5AC_PTP_AUTORESEARCH_BENCHMARK.md) · [Stage 488A](STAGE491A_PBE5AC_PTP_COMPLETE_DOSSIER_AND_SCORECARD.md) |
| **20 MHz Near-Field Attenuated Bench Goodput** | `22.80 – 25.89 Mbps` | **`26.04 – 27.21 Mbps` (`+5.1%` to `+7.3%` TCP)** | **`46.83 – 47.67 Mbps` (`LAP-120 <-> Loco 5AC`)** | [Stage 54A](STAGE54A_LITEBEAM_AND_PBE5AC_PTP_AUTORESEARCH_BENCHMARK.md) · [Stage 55A](STAGE55A_M34_M35_BQL_HOLDTIME_AND_OPENWRT_PTP_PROFILE_BENCHMARK.md) |
| **XC `PowerBeam 5AC-500` PtP Fast-Path (`Stage 85A`)** | Baseline `XC.v8.7.19` | **`+41.01%` total goodput (`+70.60%` Bulk TCP, `-64.80%` `p95` RTT)** | Native `OpenWrt 24.10.4` XC SquashFS kit ready | [README §5.10](../README.md) |

> **Important Note on Untuned OpenWrt (`Arm A` before `openMAX` Champion)**: Flashing stock OpenWrt `24.10.4` *without* the `openMAX` Champion script initially resulted in `10.64 Mbps` and `30%` full-MTU `1472B` ping loss on the near-field PtP bench ([Stage 491A](STAGE491A_PBE5AC_PTP_COMPLETE_DOSSIER_AND_SCORECARD.md)) because default `aql_txq_limit` (`5000/12000 us`), `aql_threshold=24000`, `fq_memory_limit=16 MiB` (25% of 64 MB RAM), and `tcp_limit_output_bytes=1048576` are calibrated for gigabit desktop Wi-Fi, not outdoor WISP PtP/PtMP links. Applying [`openwrt24_ptp_ptmp_champion.sh`](../firmware/public_field_kits/openwrt24_ptp_ptmp_champion.sh) eliminated the `30% -> 0.0%` loss and doubled goodput (`+93.4%`).

---

## 2. Live PtMP Sector Comparison (`LiteAP 120` AP + `LiteBeam 5AC Gen2` / `NanoStation 5AC Loco` CPEs, `20 MHz` VHT20)

Measured on 3-CPE outdoor and testbed PtMP sectors (`20 MHz` channel width, `64 MB` DDR2 `WA` boards):

| Metric (`20 MHz` VHT20 PtMP Sector) | 1. Stock `airOS 8` (`WA.v8.7.25`) | 2. Tuned `airOS 8` (`Stage 72A` `.ko` Fast-Path + Queue Tuning) | 3. `OpenWrt 24.10.4` + `openMAX` Champion (`Wave 338` Verified) | Primary Source / Stage |
| :--- | :---: | :---: | :---: | :--- |
| **Unloaded Sector RTT (`p50`)** | `22.58 ms` | `~8.5 – 11.0 ms` | **`1.93 – 2.42 ms` (`~10x` lower)** | [README §4 / Stage 12](../README.md) |
| **Loaded Download RTT (`p50` under saturation)** | `42.0 – 65.0 ms` | `14.3 – 19.2 ms` | **`8.43 – 9.86 ms` (`-86.37%` loaded `p50`)** | [Stage 773A](STAGE773A_WA_CHAMPION_V13_344WINDOW_FIELD_ROLLOUT_KIT.md) · [README §4](../README.md) |
| **Loaded Upload RTT (`p50` under saturation)** | `~180 – 200 ms` *(bufferbloat)* | `28.0 – 35.0 ms` | **`10.37 – 16.64 ms` (`-88.57%` to `-88.9%`)** | [CURRENT_STATE](CURRENT_STATE.md) · [README §5.9](../README.md) |
| **3-CPE Sector Aggregate Goodput (`20 MHz`)** | `46.53 Mbps` | **`57.39 Mbps` (`+23.35%`, `-20.81%` `p99` RTT)** | **`64.0 – 78.51 Mbps` peak TCP in `20 MHz`** | [Stage 773A](STAGE773A_WA_CHAMPION_V13_344WINDOW_FIELD_ROLLOUT_KIT.md) · [MATRIZ E2E](MATRIZ_MAESTRA_AVANCES_Y_BRECHAS_E2E_ES.md) |
| **Free RAM (`MemAvailable` on 64 MB Radio)** | `6.5 – 9.4 MB` | `8.0 – 11.0 MB` | **`10.6 – 22.4 MB` (`0` OOMs, `fq_memory_limit=4 MiB`)** | [MATRIZ E2E](MATRIZ_MAESTRA_AVANCES_Y_BRECHAS_E2E_ES.md) · [README §5.2](../README.md) |
| **Live Production Read-Back Audit (`Wave 338`)** | N/A | N/A | **`38/38` AP & `25/25` CPE knobs `100% MATCH` (`0 differs`)** | [`wave338_lane3_panel1_sysctl_fix_gate.json`](../artifacts/verification/wave338_lane3_panel1_sysctl_fix_gate.json) |

---

## 3. Summary: Which Option Should a WISP Operator Use?

1. **If you want an immediate latency & jitter upgrade on existing `airOS 8` links with zero firmware flashing:**
   - Run **[`firmware/public_field_kits/airos8_ptp_ptmp_tuned_champion.sh`](../firmware/public_field_kits/airos8_ptp_ptmp_tuned_champion.sh)** (`--apply-ram` to test, `--persist` to save to `/etc/persistent/rc.poststart`).
   - Cuts loaded `p50`/`p95` latency by **42%–50%**, cuts VoIP jitter by **54%**, and boosts multi-flow TCP goodput by **+7% to +41%** by eliminating the `tx_queue_len=1000` FIFO bufferbloat, `ampdu=32` head-of-line blocking, and `ath_pktlog` CPU tax.
2. **If you migrate the link or sector to `OpenWrt 24.10.4` (`Linux 6.6.110`):**
   - **Never leave OpenWrt at stock Wi-Fi defaults on 64 MB `WA` hardware.** Always apply **[`firmware/public_field_kits/openwrt24_ptp_ptmp_champion.sh`](../firmware/public_field_kits/openwrt24_ptp_ptmp_champion.sh)** (`--persist --role ptp|ptmp-ap|ptmp-cpe`).
   - Unlocks true `mac80211` `FQ-CoDel` + per-AC `AQL` airtime fairness + `BQL` + `CoTSQ 64 KB`, cutting unloaded RTT to **`~2 ms`** and loaded saturation RTT by **`-86%` to `-89%`** while protecting 64 MB radios from OOM resets.
