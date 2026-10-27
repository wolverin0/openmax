<!-- doc-head: STAGE777A_900WINDOW_CROSS_LANE_MASTER_SCORECARD.md preserved document content -->
<!-- /doc-head -->


# Stage 777A — `900+` Live-Window Cross-Lane Master Scorecard (`912` Windows)

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `Linux` / `mac80211` / `ath10k` / `QCA firmware` / `proprietary airMAX/LTU module` / `hardware`.
- **912-Window Milestone (Surpassing 900 Live Counterbalanced Windows!)**: Reconciles all cumulative live `A1 -> B1 -> A2 -> B2` windows across all active testbenches:
  - **`WA` Champion `v13` (`.20 <-> .250` via `MK1-251`)**: **`344` windows** (`78.51 Mbps` peak / `76.55 Mbps` mean in `VHT20`, `-86.37%` `p50` RTT, `dhcp.lan.ignore=1`)
  - **`AF-LTU` Champion `v20` (`.110` Boca 5)**: **`264` windows** (`22` rounds, `0.184 ms` RTT, `br1` `192.168.1.20` rogue DHCP disabled, `0` `/dev/ame*` touches)
  - **Multi-Radio Cross-Family Campaigns**: **`252` windows**
  - **`PBE-5AC-Gen2` / `LBE-5AC-Gen2` Bundle `v5`**: **`52` windows** (`25.47 Mbps` peak / `24.18 Mbps` mean `VHT40`, `+136.4%` UL)
  - **Total Live Counterbalanced Windows**: **`912` windows**

## 2. Master Cross-Lane Scorecard (`Stage 777A`)
| Bench / Domain | Champion Version | Live Windows | Verified Headline Result |
| :--- | :---: | :---: | :--- |
| **`WA` (`QCA988x`)** | `WA Champion v13` (`Stage 773A`) | **`344`** | **`78.51 Mbps` peak / `76.55 Mbps` mean** `VHT20`, **`-86.37%` `p50` RTT** |
| **`AF-LTU` (`Beetle`)** | `LTU Champion v20` (`Stage 774A`) | **`264`** | `0.184 ms` RTT (`22` rounds), `br1` `192.168.1.20` DHCP off |
| **Multi-Radio Fleet** | `WA` / `XC` / `XW` `v20` | **`252`** | `180` SquashFS images across `30` Ubiquiti board profiles |
| **`PBE`/`LBE` PtP `v5`** | `Bundle v5` (`Stage 741A`) | **`52`** | `25.47 Mbps` peak (`beats airOS 8` `22.80 Mbps`), `+136.4%` UL |
| **Guarida Tower (`34` EP)** | `Tower v9` (`Stage 775A`) | SimPy + Canary | **`514.80 Mbps` (`+58.51%`)**, `ff_cbp_slots=4` (`-54.17%` poll waste) |
| **Zero-FP Engine `v9`** | `Engine v9` (`Stage 776A`) | Full Telemetry | **`0.0%` FP / `0.0%` FN** (Rogue DHCP/RA + `ANI` + `CE0..7` + `64`-EVM) |
