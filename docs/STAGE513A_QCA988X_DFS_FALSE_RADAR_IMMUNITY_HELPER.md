<!-- doc-head: Stage 513A QCA988x DFS False-Radar Pulse Discriminator & 120s CAC Watchdog Helper (FMX-DISC-24) -->
Documents `fmx_qca988x_dfs_immunity_helper.sh`, integrating Stage 485A's `CSA`/`UCSA`/`swbmiss` binary RE and `FMX-DISC-24` (`120 s` DFS Channel Availability Check watchdog vs `45 s` Non-DFS watchdog) for `5250–5720 MHz` UNII-2A/2C operation.
<!-- /doc-head -->

# Stage 513A — `QCA988x` DFS False-Radar Pulse Discriminator & `120 s` CAC Watchdog Helper (`FMX-DISC-24`)

- **Epistemic Status**: `CONFIRMED` (`Stage 485A` `umac.ko` `CSA`/`UCSA`/`swbmiss` RE + `FMX-DISC-24` `60 s` CAC timing proof)
- **Attribution**: `QCA firmware` (`QCA988x` PHY radar pulse detector & `nf_cal_period`) · `proprietary airMAX/LTU module` (`ieee80211_add_ubnt_csa`)
- **Helper Script**: [`fmx_qca988x_dfs_immunity_helper.sh`](../firmware/openwrt/common/fmx_qca988x_dfs_immunity_helper.sh) (`SHA-256: 2eccbbfd45a0627e...`, strict `LF`)
- **JSON Receipt**: [`stage513a_qca988x_dfs_false_radar_immunity_helper.json`](../artifacts/autoresearch/stage513a_qca988x_dfs_false_radar_immunity_helper.json)

---

## 1. Two DFS Failure Modes on Multi-Sector WISP Towers

1. **Premature Watchdog Rollback During `60 s` DFS CAC (`FMX-DISC-24`)**:
   - On `5250–5720 MHz` (`UNII-2A` / `UNII-2C`), `hostapd` / `mac80211` must listen silently for **`60 seconds`** (`Channel Availability Check`) before transmitting a single beacon. A `45 s` rollback watchdog fires at `t = 45 s`—`15 seconds` before the AP is legally allowed to beacon!
   - `fmx_qca988x_dfs_immunity_helper.sh` automatically selects **`120 s`** for `5250–5720 MHz` and **`45 s`** for `UNII-1` (`5150–5240 MHz`) and `UNII-3` (`5725–5875 MHz`).
2. **Co-Located OFDM Sidelobe False Radar Triggers (`Stage 451A` & `Stage 485A`)**:
   - When an adjacent tower sector transmits high-power bursts, drifting noise-floor calibration causes the local `QCA988x` AGC to misclassify short OFDM preamble edges as radar pulses, triggering `ieee80211_start_csa` / `ieee80211_add_ubnt_csa` (`Stage 485A`) and `30-minute` Non-Occupancy Period (`NOP`) channel abandonment.
   - Stabilizing `nf_cal_period = 1000 ms` anchors the hardware NF baseline without ever bypassing regulatory radar compliance.

---

## 2. Channel Band & Watchdog Selection Matrix

| Center Freq (`MHz`) | Regulatory Band | Mandatory CAC (`s`) | Selected Watchdog (`s`) | Immunity & CSA Mode |
| :---: | :--- | :---: | :---: | :--- |
| **`5180 MHz`** | `UNII-1` (Indoor/Outdoor) | `0 s` | **`45 s`** | `NON_DFS_FAST_LOCK` |
| **`5260 MHz`** | `UNII-2A` (`DFS`) | `60 s` | **`120 s`** | `DFS_60S_CAC_NF_STABILIZED` (`nf_cal_period=1000`) |
| **`5500 MHz`** | `UNII-2C` (`DFS`) | `60 s` | **`120 s`** | `DFS_60S_CAC_NF_STABILIZED` (`nf_cal_period=1000`) |
| **`5620 MHz`** | `UNII-2C` (`TDWR` Weather) | `600 s` | **`120 s`** | `TDWR_AVOID_OR_EXTENDED_CAC` |
| **`5805 MHz`** | `UNII-3` (ISM/PtP) | `0 s` | **`45 s`** | `NON_DFS_FAST_LOCK` |
