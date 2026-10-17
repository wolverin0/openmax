# Stage 7 — 3-Station Multi-Vendor & Mixed-Generation (`802.11ac` + `MikroTik 802.11n` + `airOS 6 M5`) PtMP Benchmarks

**Date**: October 17, 2026  
**Raw Measurement Receipt**: [`artifacts/stage7_ptmp/stage7_ptmp_3station_results.json`](../artifacts/stage7_ptmp/stage7_ptmp_3station_results.json)  
**Reproducible Benchmark Runner**: [`tools/bench/stage7_ptmp_bench.py`](../tools/bench/stage7_ptmp_bench.py)

---

## 1. Physical Sector Topology

All three stations are associated simultaneously over 5 GHz (Channel 36, `5180 MHz`, `VHT80` center `5210 MHz`) to a **Ubiquiti LiteAP AC (`LAP-120`, `AR9342` + `QCA9882`)** running our tuned OpenWrt 24.10.4 (`ath10k-ct`) stack:

| Role | Hardware | OS / Wireless Driver | PHY Mode & Streams | Physical Placement | RF IP |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Sector AP** | **Ubiquiti LiteAP AC (`LAP-120`)** | OpenWrt 24.10.4 (`ath10k-ct`) | `802.11ac VHT80` 2x2 MIMO | Lab bench | `10.99.0.1` |
| **Station 1 (`loco5ac`)** | **Ubiquiti NanoStation 5AC Loco** | OpenWrt 24.10.4 (`ath10k-ct`) | `802.11ac VHT80` 2x2 MIMO (`650 Mbps` PHY) | Same room (~3 m LOS) | `10.99.0.2` |
| **Station 2 (`sxt`)** | **MikroTik SXT Lite5 (`RBSXT5nDr2`)** | OpenWrt 24.10.4 (`ath9k`) | `802.11n HT40` 2x2 MIMO (`243–270 Mbps` PHY) | Behind wall/door (~6 m NLOS) | `10.99.0.3` |
| **Station 3 (`lbm5`)** | **Ubiquiti LiteBeam M5 (`LBE-M5-23`)** | Stock `airOS 6.1.4` (`ath_hal`, `airMAX=off`) | `802.11n HT40` 1x1 SISO (`150 Mbps` PHY) | Behind wall/door (~6 m NLOS) | `10.99.0.4` |

Traffic is generated from an external x86 Linux host (`Omarchy`, `192.168.1.171`) routed through the `LAP-120` AP (`192.168.1.2 -> phy0-ap0`) with stateless `nftables raw notrack` forwarding so the AP's 535 MHz MIPS CPU performs only kernel L3 forwarding and 802.11 scheduling.

---

## 2. Experiment 7.1 — Output Power & Wall-Attenuation Sweep (`15 dBm` vs `11 dBm` vs `3 dBm`)

By sweeping the `LAP-120` AP's TX power across **`15 dBm`**, **`11 dBm`**, and **`3 dBm`**, we drove the wall-obstructed stations (`MikroTik SXT Lite5` and `Ubiquiti LiteBeam M5`) from moderate attenuation down to edge-of-sector receiver sensitivity while keeping the near `NanoStation 5AC Loco` at high SNR:

| AP TX Power | `Loco 5AC` (`VHT80 2x2`, Room) Alone DL | `LiteBeam M5` (`airOS 6 HT40 1x1`, Wall) Alone DL | `MikroTik SXT` (`ath9k HT40 2x2`, Wall) Alone DL | **All 3 Simultaneous DL (Mean Sector Goodput)** | **Jain's Fairness Index** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`15 dBm` (High)** | `113.82 Mbps` (`27.4 ms` p50) | `67.88 Mbps` (`5.51 ms` p50) | **`55.01 Mbps` (`21.35 ms` p50)** | **`91.55 Mbps`** (`45.5` / `22.5` / `23.5 Mbps`) | **`0.8869`** |
| **`11 dBm` (Mid)** | `118.28 Mbps` (`24.3 ms` p50) | `69.09 Mbps` (`6.35 ms` p50) | `20.15 Mbps` (`72.10 ms` p50) | **`81.85 Mbps`** (`39.8` / `30.1` / `12.0 Mbps`) | **`0.8489`** |
| **`3 dBm` (Edge SNR)** | `90.85 Mbps` (`11.7 ms` p50) | **`5.07 Mbps`** (`36.30 ms` p50) | `18.64 Mbps` (`75.60 ms` p50) | **`73.47 Mbps`** (`51.4` / `17.4` / `4.6 Mbps`) | **`0.6013`** |

---

## 3. Experiment 7.2 — Multi-Station `Airtime Fairness (ATF)` + `AQL` + Bounded `A-MPDU` at `3 dBm` Edge SNR

At `3 dBm` AP TX power (severe Near-Far asymmetry with `LiteBeam M5` at `5.07 Mbps` and `MikroTik SXT` behind the wall), we evaluated four MAC/queue scheduling treatments under simultaneous 3-station TCP download:

| Treatment (`AP @ 3 dBm`) | `Loco 5AC` (`VHT80`) Loaded RTT (`p50 / p95`) & Retrans | `LiteBeam M5` (`HT40`) Loaded RTT (`p50 / p95`) & Retrans | `MikroTik SXT` (`HT40`) Loaded RTT (`p50 / p95`) | Mean Sector DL Goodput |
| :--- | :--- | :--- | :--- | :--- |
| **`T1`: Legacy Queue (`ATF=Off`, `AQL 24000`, `Agg 3x64`)** | `51.35 ms / 88.45 ms` (`158` retrans/trial) | `56.25 ms / 610.0 ms` (`80` retrans/trial) | `402.3 ms / 1955.5 ms` | `71.84 Mbps` |
| **`T2`: Equal `ATF` (`256:256:256`, `AQL 2000/4000`, `Agg 3x64`)** | `15.78 ms / 26.00 ms` (`12` retrans/trial) | `20.70 ms / 340.0 ms` (`21` retrans/trial) | `311.8 ms / 1054.5 ms` | **`76.69 Mbps`** |
| **`T3`: FuturaMAX Bounded Agg (`1x16`, `AQL 1500/3000`, Equal `ATF`)** | **`12.65 ms / 28.65 ms` (`16` retrans/trial)** | **`14.23 ms / 141.0 ms` (`14.5` retrans/trial)** | **`222.0 ms / 919.0 ms`** (Trial 2 `476 ms`) | `72.72 Mbps` |
| **`T4`: FuturaMAX Weighted `ATF` (`1024 AC : 128 SXT : 128 M5`)** | `15.10 ms / 24.00 ms` (`12` retrans/trial) | `16.33 ms / 175.3 ms` (Trial 2 `p95=22.6 ms`) | `266.0 ms / 1575.5 ms` | `74.34 Mbps` |

* Enabling `mac80211` `AIRTIME_FAIRNESS` (`airtime_flags=3`) + tightened `AQL` (`1500/3000 µs`) + bounded aggregation (`1x16` / `2x32`) reduced the fast `802.11ac` station's loaded median latency by **`4.06x` (`51.35 -> 12.65 ms`)**, reduced its TCP retransmissions by **`10x` (`158 -> 16`)**, and reduced the `LiteBeam M5`'s median latency by **`3.95x` (`56.25 -> 14.23 ms`)**.

---

## 4. Experiment 7.3 — 3-Station Simultaneous Uplink Contention & `RTS/CTS 256B` Protection (`+18.5%` Sector Uplink Gain)

When all 3 stations transmit Uplink (`UL`) simultaneously (`Loco 5AC` in the room + `MikroTik SXT` and `LiteBeam M5` behind the wall/door):

| Uplink Mode (`AP @ 11 dBm`) | `Loco 5AC` (`VHT80` Room) UL | `LiteBeam M5` (`airOS 6` Wall) UL | `MikroTik SXT` (`ath9k` Wall) UL | **Total Sector Uplink Goodput** |
| :--- | :--- | :--- | :--- | :--- |
| **Each Station ALONE (No Contention)** | `136.64 Mbps` | `62.90 Mbps` | `44.38 Mbps` | *(Sum = `243.92 Mbps`)* |
| **All 3 Simultaneous UL — `RTS/CTS = OFF`** | `119.21 Mbps` (`119.7 / 118.8`) | `29.23 Mbps` (`30.4 / 28.1`) | **`1.97 Mbps`** (`1.18 / 2.75` — *starved!*) | **`150.40 Mbps`** |
| **All 3 Simultaneous UL — `RTS/CTS = 256B`** | **`137.94 Mbps`** (`136.6 / 139.3`) | **`34.21 Mbps`** (`33.4 / 35.0`) | **`6.03 Mbps`** (`3.54 / 8.52` — **`3.07x` gain!**) | **`178.17 Mbps` (`+18.5%` / `+27.8 Mbps`!)** |

* Unlike single-station LOS testing (where `RTS/CTS` was pure overhead), under 3-station wall-attenuated Uplink contention, enabling `RTS/CTS = 256B` on the stations caused the `LAP-120` AP to broadcast `CTS` frames heard across the entire sector, boosting total sector Uplink goodput by **`+18.5%` (`150.40 -> 178.17 Mbps`, peaking at `182.82 Mbps`)** while recovering the wall-obstructed `MikroTik SXT` by **`3.07x` (`1.97 -> 6.03 Mbps`)**.

---

## 5. Experiment 7.4 — Kernel Discovery: `WMM AC_VO DiffServ Deficit Bypass` (`21.0x` Weak-Station Latency Cut)

Inspecting `/sys/kernel/debug/ieee80211/phy0/netdev:phy0-ap0/stations/64:d1:54:1b:96:97/airtime` during 3-station saturation revealed why the wall-obstructed `MikroTik SXT` experienced ~140–200 ms ping latency when saturating its own bulk TCP download at `3 dBm`:
* When hardware rate fallback and retries occur on an obstructed station during bulk `AC_BE` traffic, completed `tx_duration` reported by `ath10k-ct` drives that station's `Deficit: BE` down to **`-67,099 µs` (`-67.1 ms`)**:
  ```text
  Weight: 256
  Deficit: VO: 256 us   VI: 256 us   BE: -67099 us   BK: 256 us
  ```
* Because `mac80211` tracks `Deficit` and `AQL` independently per WMM Access Category (`VO`, `VI`, `BE`, `BK`) per station, promoting interactive packets (`ICMP`, `DNS`, `NTP`, `SIP/VoIP`) to `DSCP EF` (`AC_VO`) in `fmx_fastpath` routes them through `Deficit: VO (+256 µs)`, completely bypassing the station's negative `BE` deficit penalty box:

| 3-Station Saturation Mode | `MikroTik SXT` (Behind Wall) Loaded RTT (`p50 / p95`) | `LiteBeam M5` (Behind Wall) Loaded RTT (`p50 / p95`) | `Loco 5AC` (Room) Loaded RTT (`p50 / p95`) | Mean Sector DL Goodput |
| :--- | :--- | :--- | :--- | :--- |
| **`3 dBm` — `AC_BE` Default** | `143.00 ms / 509.50 ms` | `36.15 ms / 209.50 ms` | `14.43 ms / 31.30 ms` | `62.07 Mbps` |
| **`3 dBm` — `AC_VO` DiffServ Bypass (`ip dscp set ef`)** | **`6.80 ms` (`21.0x` cut!) / `131.5 ms` (Trial 1 `17.0 ms`!)** | **`4.53 ms` (`8.0x` cut!) / `70.5 ms` (Trial 2 `8.1 ms`!)** | **`4.54 ms / 8.15 ms` (`3.84x` p95 cut!)** | **`78.97 Mbps` (`+27.2%`)** |
| **`11 dBm` — `AC_BE` Default** | `54.98 ms / 142.00 ms` | `29.90 ms / 41.55 ms` | `33.58 ms / 44.85 ms` | `94.99 Mbps` |
| **`11 dBm` — `AC_VO` DiffServ Bypass (`ip dscp set ef`)** | **`30.13 ms / 83.45 ms` (Trial 2 `37.9 ms`!)** | **`28.05 ms / 38.00 ms`** | **`28.73 ms / 35.30 ms`** | **`104.94 Mbps` (`+10.5%`)** |
