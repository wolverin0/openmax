<!-- doc-head: STAGE15_GIT_PUSH_READINESS_AND_MASTER_ATLAS.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 15: Git Push Readiness (`<50 MB` Gate) & 11-Unit Bench Hardware Master Atlas

## 1. Executive Summary

Stage 15 (`T-S15-GIT-AND-ATLAS`) enforces repository push readiness (`total_unignored_size_mb = 42.71 MB < 50.0 MB`, `leaked_binary_dumps = []`) and consolidates the complete hardware, silicon, thermal, and autoresearch ledger across all **11 Bench Hardware Entries (`12` Physical Radios across `7` Silicon/Firmware Families and `313` Unique Live Autoresearch Rounds)**:

- Analyzer & Verifier: [`analysis/git_push_readiness_and_master_atlas.py`](../analysis/git_push_readiness_and_master_atlas.py)
- Master Atlas Artifact: [`artifacts/autoresearch/master_11unit_hardware_atlas_20261025.json`](../artifacts/autoresearch/master_11unit_hardware_atlas_20261025.json)
- Repository Ignore Rules: [`.gitignore`](../.gitignore)
- Unit Test Suite: [`tests/test_git_push_readiness_and_master_atlas.py`](../tests/test_git_push_readiness_and_master_atlas.py)

---

## 2. Git Push Readiness & `.gitignore` Hygiene Gate (`42.71 MB < 50.0 MB`)

### 2.1 Excluded Proprietary Binaries & Bulk Scratch Dirs
The updated [`.gitignore`](../.gitignore) excludes all raw firmware dumps, squashfs extractions, and intermediate wave directories (`~2,919 MB` excluded):
- `firmware/*.bin`, `firmware/**/*.bin`, `firmware/*.squashfs`, `firmware/**/*.squashfs`, `firmware/openwrt/futuramax-*/`
- `artifacts/firmware_re_xc_ltu/*.bin`, `artifacts/firmware_re_xc_ltu/*.sqfs`, `artifacts/firmware_re_xc_ltu/ltu_extracted/`, `artifacts/firmware_re_xc_ltu/*_rootfs/`
- `artifacts/*_re/root_squashfs/`, `artifacts/*_re/`
- `artifacts/canary_panel1_guarida/*.bin`, `artifacts/canary_panel1_guarida/**/*.bin`, `artifacts/canary_panel1_guarida/*.zip`, `artifacts/canary_panel1_guarida/root_*/`
- `artifacts/autoresearch/waves_*/`, `orchestration/autoresearch/stage13_sync_*/`

### 2.2 Preserved Tracked Categories (`42.71 MB` Total Unignored Payload)
| Category | Tracked Status | Size / Count |
| :--- | :---: | :--- |
| **`docs/*.md`** (All Stage 1..15 Research & Architecture Docs) | Tracked | `4.29 MB` |
| **Python Code** (`analysis/`, `controller/`, `orchestration/`, `telemetry/`, `tests/`, `tools/`) | Tracked | `6.83 MB` |
| **Interactive Command Center** (`artifacts/dashboard/FUTURAMAX_COMMAND_CENTER.html`) | Tracked | `0.46 MB` |
| **Hardware Benchmark Receipts** (`R1..R194`, `R14`, `PBM5-R1..R36`, `R5AC-R1..R21`, `R2AC-R1..R21`, `LTU-R1..R20`, `AF4X-R1..R20`) | Tracked | `31.13 MB` |
| **Total Unignored Repository Delta** | **PASS (`< 50.0 MB`)** | **`42.71 MB` (`7.29 MB` headroom)** |

---

## 3. Master 11-Unit Bench Hardware & Autoresearch Atlas

| # | Unit ID | Bench Unit / Group | Qty | Board `sysid` & SoC / Radio | Firmware | Endpoints | Live Rounds | Thermal / RF State | Headline Empirical Breakthrough |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- |
| **1** | `UNIT_01_LAP120_AP` | **Ubiquiti LiteAP AC (`LAP-120`)** | `1` | `0xe8e5` (`AR9342` `535 MHz` + `QCA9882 hw2.0`) | OpenWrt `24.10.4` (`Linux 6.6.110` + `ath10k-ct` + `ETH_P_TEB`) | `198.18.0.81`, `198.18.0.54` | `195` (`142 KEEP`) | Passive nominal | **`108.55 Mbps`** 3-CPE PtMP (`p95=15.64 ms`, `Jain=0.9987`, `R14`); **`+15.8%`** goodput & **`-40.7%`** p95 RTT across `1..14 km` (`R183..R194`) |
| **2** | `UNIT_02_LOCO5AC_195` | **Ubiquiti NanoStation 5AC Loco (`Loco195`)** | `1` | `0xe7fa` (`AR9342` `535 MHz` + `QCA9882 hw2.0`) | OpenWrt `24.10.4` / Stock `WA.v8.7.25` | `198.18.0.124`, `198.18.0.56` | `195` (`142 KEEP`) | Passive nominal | **`0.0%` loss** across 32-window 16-block AB/BA `1..14 km` ladder; UL 8-flow hammer p95 RTT cut **`-34.6%`** (`81.92 -> 50.09 ms`) |
| **3** | `UNIT_03_MIKROTIK_SXT_LITE5` | **MikroTik SXT 5nDr2 (`SXT Lite5`)** | `1` | `rbsxt5ndr2` (`AR9344` `600 MHz` 2x2 `802.11a/n`) | OpenWrt `24.10.4` `ath9k` / RouterOS | `198.18.0.58` | `15` (`11 KEEP`) | Passive nominal | Simultaneous 4-addr WDS PtMP association with `LAP-120` (`R14`) & `Rocket Prism 5AC Gen2` via `addmtikie=1` (**`+36.6%`** goodput/MHz) |
| **4** | `UNIT_04_LITEBEAM_M5` | **Ubiquiti LiteBeam M5 (`LBM5`)** | `1` | `0xe4e5` (`AR9342` 1x1 SISO `802.11n` `MCS 7`) | `XW.v6.1.4` / `XW.v6.3.2` | `198.18.0.52` | `15` (`11 KEEP`) | Passive nominal | Zero-touch 11n WDS interop; airtime fairness shaping eliminates 1x1 SISO sector monopolization (**`-75.7%`** p99 RTT) |
| **5** | `UNIT_05_ROCKET_PRISM_5AC_GEN2` | **Ubiquiti Rocket Prism 5AC Gen2 (`Rocket198`)** | `1` | `0xe7e9` (`QCA9558` `720 MHz` + `QCA9880` + Dual-Stage `AirPrism`) | `XC.qca955x.v8.7.25` | `198.18.0.64` | `21` (`5 KEEP`) | Shielded cast chassis + `IRQ 64` `35..80/s` | `airview1 down` + `ani_enable=0` (`-60.5%` p50) + `swretry=4/6` (`-67.9%` p50) -> **`1.81 ms` p50 RTT**; **`+62.1%`** goodput/MHz under blocker |
| **6** | `UNIT_06_POWERBEAM_M5_300_PAIR` | **2x Ubiquiti PowerBeam M5 300 (`.220 AP <-> .219 STA`)** | `2` | `0xe3e5` (`AR9342` `Wasp` 2x2 `802.11n` + `ubnt_poll.ko`) | `XW.v6.3.22` | `198.18.0.86`, `198.18.0.85` | `36` (`18 KEEP`) | `-80 dBm` OTA, `6-8 dB` chain imbalance (`[9, 17]`) | `query_mac_info` proved **`42% PER`** on 2x2 `MCS 11..15`; `txchainmask=2, rxchainmask=3` + `AMPDU=16/16384` + `ANIEna=1` lifted CCQ **`58% -> 95.5%`** (**`-76.3%`** p95 RTT) |
| **7** | `UNIT_07_ROCKET_2AC_PRISM` | **Ubiquiti Rocket 2AC Prism (`Boca 8`)** | `1` | `0xe2f2` (`QCA9558/AR9342` + 2.4 GHz `AirPrism`) | `2WA.v8.7.11` | `198.18.0.89`, `PUBLIC_DEVICE_0059` | `21` (`11 KEEP`) | Nominal | Proved `ani_enable=1` must stay ON in 2.4 GHz AP mode; `shpreamble=1` (**`-54.3%`** p50) + `ptp_xmit=1` + `swretry=4/6` -> **`<2 ms` p50 RTT** |
| **8** | `UNIT_08_AIRFIBER_4X` | **Ubiquiti airFiber 4X (`AF-4X`)** | `1` | `af4x_invictus2` (`TI AM1808` `124.5 BogoMIPS` + `Invictus v2` FPGA) | `AF06.v4.1.0` | `198.18.0.83`, `198.18.0.50` | `20` (`12 KEEP`) | **`temp0=38°C, temp1=38°C`** (`NOMINAL`) | `framelength=2.5ms` cuts TDD IRQ rate `500->400 Hz` (**`-16.1%`** p95, **`+15.3%`** stream); `flowcntl=on` + `cp=8` -> **`-22.8%`** p95 RTT (`33.25 -> 25.68 ms`) |
| **9** | `UNIT_09_LTU_ROCKET` | **Ubiquiti LTU-Rocket (`AF-LTU-Rocket`)** | `1` | `0xeb00` (`UBNT AME SoC` + Custom LTU FPGA/ASIC + `HSR`) | `aflturocket.v2.4.1 / v2.4.2` | `offline-re-and-stage11-audit` | `6` (`4 KEEP`) | Dual die sensors (`temp0/temp1`) | Disassembled `ame_core.ko` & `ubnt_ame_oko`: `4096-QAM` (`12x`) gated by `97%/90%` `12x_gate`; `sched_max_agg_cnt=8` + `cz_cross_frame_backoff_enable=0` |
| **10** | `UNIT_10_LTU_LITE_PRIMARY_BOCA5` | **Ubiquiti LTU-Lite #1 (`Boca 5`)** | `1` | `0xea02` (`44552`, `UBNT AME SoC` + 8-queue `eth0` `mq`) | `afltu.v2.4.0` | `198.18.0.84`, `PUBLIC_DEVICE_0046` | `20` (`7 KEEP`) | **`temp0=79°C, temp1=79°C`** (`6°C` below `85°C` ceiling) | `sched_max_agg_cnt=8` eliminated background scan spikes (**`-88.5%`** p95 RTT); `ath0 fq_codel quantum=1514 target=2.5ms` cut p95 by **`-45.8%`** |
| **11** | `UNIT_11_LTU_LITE_SECONDARY_UNIT2` | **Ubiquiti LTU-Lite #2 (Paired Unit)** | `1` | `0xea02` (`44552`, `UBNT AME SoC`) | `afltu.v2.4.0 / v2.4.2` | `198.18.0.50` | `6` (`4 KEEP`) | `<85°C` thermal gate | Paired with `LTU-Lite #1` & `LTU-Rocket` for OFDMA subband (`ofdmasubband`) and `4096-QAM` (`automcsceil=12x`) qualification |

---

## 4. Verification Commands

```powershell
python analysis/git_push_readiness_and_master_atlas.py
pytest tests/test_git_push_readiness_and_master_atlas.py
```
