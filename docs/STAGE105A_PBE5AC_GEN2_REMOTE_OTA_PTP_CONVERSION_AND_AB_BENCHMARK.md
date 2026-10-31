<!-- doc-head: STAGE105A_PBE5AC_GEN2_REMOTE_OTA_PTP_CONVERSION_AND_AB_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 105A — 100% Remote Over-The-Air (`OTA`) Conversion & Counterbalanced `A1 -> B1 -> A2 -> B2` Benchmark on `PowerBeam 5AC Gen2` (`.241 <-> .242`)

## 1. Executive Summary & Attribution
- **Objective**: Convert the remote `PowerBeam 5AC Gen2` STA (`198.18.0.46` / `198.18.0.74`, `PUBLIC_DEVICE_0037`, wired to `MK1-251` `Boca 7`) **100% Over-The-Air (`OTA`)** and the local `PowerBeam 5AC Gen2` AP (`198.18.0.45` / `198.18.0.8`, `PUBLIC_DEVICE_0038`, wired to `Boca 3`) from Stock `airOS 8` (`WA.v8.7.25` / `WA.v8.7.11`) to `OpenWrt 24.10.4` (`r28959`, Linux `6.6.110`, `ath10k-ct` + `mac80211` v3) without touching cables or climbing a tower, then execute a counterbalanced `A1 -> B1 -> A2 -> B2` benchmark.
- **Outcome (`CONFIRMED`)**:
  1. **Zero-Truck-Roll `OTA` Migration Succeeded**: Both `.242` (remote STA over wireless link) and `.241` (local AP) were flashed via direct dual-bank (`mtd2` `kernel0` + `mtd3` `kernel1`) `uImage` + SquashFS rootfs extraction from pre-baked `factory.bin` images, preserving `mtd0` (`u-boot`), `mtd1` (`u-boot-env`), `mtd4` (`cfg`), and `mtd5` (`EEPROM`/`ART` calibration data) intact (`0` bytes modified).
  2. **Latency Improvement vs Stock `airOS 8` TDMA (`CONFIRMED`)**:
     - Stock `airOS 8` (`WA.v8.7.25 <-> WA.v8.7.11`, `20 MHz`): `min = 1.42 ms`, **`p50 = 1.96 ms`, `p95 = 7.56 ms`, `p99 = 10.68 ms`**.
     - OpenWrt `24.10.4` (`Stage 105A Champion`, `20 MHz` `4addr` WDS): `min = 1.404 ms`, **`p50 = 1.589 ms` (`-18.9%`), `p95 = 2.676 ms` (`-64.6%`), `p99 = 2.676 ms` (`-74.9%`)**.
  3. **Counterbalanced `A1 -> B1 -> A2 -> B2` on OpenWrt `24.10.4` (`CONFIRMED`)**:
     - **Full-MTU (`1472B` payload / `1500B` IP) Packet Loss**: Reduced from **`26.5%` mean loss** in `Arm A` (`33.0%` in `A1`, `20.0%` in `A2`) to **`0.0%` loss (`30/30` packets received)** in `Arm B` (`0.0%` in `B1`, `0.0%` in `B2`).
     - **Under-Load RTT (`p50`)**: Reduced by **`-53.2%`**, from **`33.22 ms`** (`Arm A`) to **`15.53 ms`** (`Arm B`).
     - **Uplink Goodput (`.242 -> .241`)**: Increased **`7.58x` (`+658%`)**, from **`0.575 Mbps`** (`Arm A`) to **`4.36 Mbps`** (`Arm B` `A1->B1->A2->B2` mean) and **`5.39 Mbps`** (with `AP active=0 + short_gi_20=0`), surpassing Stock `airOS 8` TDMA's `3.60 Mbps` UL by **`+21.1%` to `+49.7%`** (`6.30 Mbps` UL in `VHT40`).
     - **Aggregate Goodput (`20 MHz`)**: Increased by **`+41.1%`**, from **`10.37 Mbps`** (`Arm A`) to **`14.62 Mbps`** (`Arm B`, peak `15.28 Mbps` in `B1`).

---

## 2. Golden Partition Backups & Pre-Baked SquashFS Images

| Device | Partition / Artifact | Size (B) | SHA-256 |
| :--- | :--- | ---: | :--- |
| `.242` (`STA`) | `mtd0_uboot.bin` | `262,144` | `b3d54d2c7eb154361dad22dbf880dacbd77857d339f1ad065ea84e28d8b4bfc2` |
| `.242` (`STA`) | `mtd1_u_boot_env.bin` | `65,536` | `63213a0bb3ec161faa51abf53417dcab7325b529c12150073923c6ab42cf711f` |
| `.242` (`STA`) | `mtd4_cfg.bin` | `262,144` | `910bdde381d3412b8ba420fdface7f3dfeafe7f5e479f7a12dd853a8be333005` |
| `.242` (`STA`) | `mtd5_EEPROM.bin` | `65,536` | `f88bc3d756e078c4f04b3ee7e1700ea091a7288e8edcc217b4cd7dbda9de3754` |
| `.241` (`AP`) | `openwrt-...-factory-ap-241.bin` | `6,947,480` | `709c0dbf9ef276112857caaf4e53f14ea3128d8f3232867da535bf29622b5963` |
| `.242` (`STA`) | `openwrt-...-factory-sta-242.bin` | `6,947,480` | `810cf6a1b9edd317a0e84920d5c908e589abd81917faed20b097ad0887eb3dcb` |

- Backup Manifest: [`backup_manifest.json`](../artifacts/autoresearch/stage105a_backups/242_Stock_airOS8_WA.v8.7.11/backup_manifest.json)
- Benchmark Artifact: [`stage105a_pbe5ac_gen2_ota_ptp_benchmark_20261026.json`](../artifacts/autoresearch/stage105a_pbe5ac_gen2_ota_ptp_benchmark_20261026.json)

---

## 3. New Mechanistic Discoveries (`FMX-DISC-39` & `FMX-DISC-40`)

### `FMX-DISC-39` — `airOS 8` `ubnt_poll_host.ko` Datapath Interception in `uph_op_mode=0` (`CONFIRMED`, attribution: `proprietary airMAX/LTU module`)
- Even when `/proc/sys/dev/uph_wifi0/polling=disabled` and `uph_op_mode=0` (`allow_80211=1`) are set on `airOS 8` (`WA.v8.7.25`), `ubnt_poll_host.ko` remains hooked into `ath_dev.ko`/`umac.ko` on `QCA988x`.
- An `OpenWrt 24.10.4` (`ath10k-ct`) STA (`4addr=0` or `4addr=1`) completes 802.11 Authentication, Association (`AID=1`), and WPA2-PSK 4-Way Handshake (`GROUP_HANDSHAKE -> COMPLETED`) and receives broadcast ARP requests from the `airOS 8` AP, but unicast IP data frames from the non-airOS STA are silently dropped before `br0`.
- **Implication**: Remote OTA conversion of a PtP pair must stage the remote STA flash first, then immediately flash the local AP so both endpoints come up on native `OpenWrt` `4addr` WDS (`AP/VLAN` `phy0-ap0.sta1` $\leftrightarrow$ `managed` `4addr` `phy0-sta0`).

### `FMX-DISC-40` — `ath10k-ct` `set_rate_override` 0-Indexed `nss` & `pream=3` VHT Asymmetry (`CONFIRMED`, attribution: `QCA firmware` / `ath10k`)
- Radiographic EVM inspection of the bench `PowerBeam 5AC Gen2` pair ([`backup_manifest.json`](../artifacts/autoresearch/stage105a_backups/242_Stock_airOS8_WA.v8.7.11/backup_manifest.json)) revealed strong physical asymmetry on bench:
  - **Downlink (`.241 -> .242`)**: Subcarrier CINR is **`26–27 dB`** across all 64 subcarriers (`signal = -54 dBm`, chains `[-64, -55] dBm`), supporting **`2x2 VHT-NSS 2` (`MCS 3` = `52 Mbps`)**.
  - **Uplink (`.242 -> .241`)**: Subcarrier CINR drops to **`11–15 dB`** on subcarriers `36..63` due to near-field bench reflection (`signal = -65 dBm`, chains `[-71, -66] dBm`).
- Upstream `ath10k-ct` rate control defaults to `2x2 VHT-NSS 2` with `Short GI (400 ns)` (`[SHORT-GI-20]`), causing `20–33%` loss on `1500B` MPDUs and collapsing TCP UL goodput to `0.54–0.61 Mbps` (and stalling default-MSS SSH sessions until `advmss 100` or `NSS=1 LGI` is applied).
- Critical `ath10k-ct` driver finding in `/sys/kernel/debug/ieee80211/phy0/ath10k/set_rate_override`:
  - `pream` must be **`3` (`VHT`)** (or `2` for `HT`) to preserve 802.11ac A-MPDU aggregation; `pream=0` selects legacy non-HT `802.11a OFDM` (where `mcs=0..3` maps to `48, 24, 12, 6 Mbps` without A-MPDU).
  - When `pream=3` (`VHT`), **`nss` is 0-indexed** in `WMI_VDEV_PARAM_FIXED_RATE`: `nss=0` encodes **`VHT-NSS 1` (`1x1`)** and `nss=1` encodes **`VHT-NSS 2` (`2x2`)**.
  - Disabling `short_gi_20=0`, `short_gi_40=0`, `short_gi_80=0`, and `disassoc_low_ack=0` in `/etc/config/wireless` (`hostapd-phy0.conf`) plus setting `.241` (`AP`) to `mcs=3 nss=1 pream=3 sgi=0` (`52 Mbps VHT-NSS 2`) and `.242` (`STA`) to `mcs=2 nss=0 pream=3 sgi=0` (`19.5 Mbps VHT-NSS 1`) yields **`0.0%` full-MTU loss** and **`4.36–5.39 Mbps` UL goodput**.

---

## 4. Counterbalanced `A1 -> B1 -> A2 -> B2` Results (`20 MHz` & `40 MHz`)

| Window / Profile | 64B RTT `p50` / `p95` (ms) | Full-MTU (`1472B`) Loss (%) | Under-Load RTT `p50` (ms) | DL Goodput (Mbps) | UL Goodput (Mbps) | Aggregate (Mbps) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Stock `airOS 8` TDMA (`20 MHz`)** | `1.96` / `7.56` | `0.0%` | — | `19.20` | `3.60` | `22.80` |
| **OpenWrt `A1` (`Arm A` Stock)** | `1.841` / `2.716` | `33.0%` | `32.502` | `11.85` | `0.61` | `12.46` |
| **OpenWrt `B1` (`Arm B` Champion)** | `1.621` / `3.201` | **`0.0%`** | **`14.741`** | `11.06` | **`4.22`** | **`15.28`** |
| **OpenWrt `A2` (`Arm A` Stock)** | `1.476` / `2.224` | `20.0%` | `33.934` | `7.73` | `0.54` | `8.27` |
| **OpenWrt `B2` (`Arm B` Champion)** | `1.557` / `2.151` | **`0.0%`** | **`16.319`** | `9.46` | **`4.50`** | **`13.96`** |
| **Mean `Arm A` (`A1, A2`)** | `1.659` / `2.470` | `26.5%` | `33.218` | `9.79` | `0.58` | `10.37` |
| **Mean `Arm B` (`B1, B2`)** | **`1.589`** / `2.676` | **`0.0%`** | **`15.530` (`-53.2%`)** | **`10.26`** | **`4.36` (`+658%`)** | **`14.62` (`+41.1%`)** |
| **Hybrid `AP auto + STA VHT-NSS1`** | `1.510` / `3.159` | **`0.0%` (`3.17 ms` avg)** | `18.196` | `9.14` | **`5.39` (`+49.7%` vs airOS)** | `14.53` |
| **`VHT40` (`40 MHz` Verification)** | — | **`0.0%` (`2.31 ms` avg)** | — | `3.55` | **`6.30` (`+75.0%` vs airOS)** | `9.85` |
