<!-- doc-head: STAGE719A_800WINDOW_CROSS_LANE_SCORECARD.md preserved document content -->
<!-- /doc-head -->


# Stage 719A — `800+` Live-Window Cross-Lane Scorecard (`824` Windows)

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `Linux` / `mac80211` / `ath10k` / `QCA firmware` / `proprietary airMAX/LTU module` / `hardware`.
- **824-Window Milestone (Surpassing 800 Live Counterbalanced Windows!)**: Reconciles all cumulative live `A1 -> B1 -> A2 -> B2` windows across all active testbenches:
  - **`WA` Champion `v12` (`.20 <-> .250`)**: **`316` windows** (`-83.06%` `p50` RTT `12.60 ms`, `70.85 Mbps` E2E)
  - **`AF-LTU` Champion `v18` (`.110` Boca 5)**: **`240` windows** (`20` rounds, `0.186 ms` RTT, `0` `/dev/ame*` touches)
  - **Multi-Radio Cross-Family Campaigns**: **`216` windows**
  - **`PBE-5AC-Gen2` PtP `v4` (`VHT40` & Triple-Play)**: **`52` windows** (`25.47 Mbps` peak / `24.18 Mbps` mean, `+136.4%` UL)
  - **Total Live Counterbalanced Windows**: **`824` windows**

## 2. Cross-Lane Champion Matrix (`Stage 719A`)
| Bench / Domain | Champion Version | Live Windows | Verified Headline Result |
| :--- | :---: | :---: | :--- |
| **`WA` (`QCA988x`)** | `WA Champion v12` (`Stage 715A`) | **`316`** | `70.85 Mbps` E2E, `12.60 ms` loaded `p50` RTT (`-83.06%`) |
| **`AF-LTU` (`Beetle`)** | `LTU Champion v18` (`Stage 716A`) | **`240`** | `0.186 ms` RTT (`20` rounds), GPS `1PPS` + DMA ring guards |
| **Multi-Radio Fleet** | `WA` / `XC` / `XW` `v18` | **`216`** | `180` SquashFS images across `30` board profiles |
| **`PBE-5AC-Gen2` PtP** | `PtP Champion v4` (`Stage 701A`) | **`52`** | `25.47 Mbps` peak (`beats airOS 8` `22.80 Mbps`), `+136.4%` UL |
| **Guarida Tower (`34` EP)** | `Tower v7` (`Stage 717A`) | SimPy + Canary | **`481.20 Mbps` (`+48.16%`)**, `8.60 ms` `p99` RTT |
| **Zero-FP Engine `v7`** | `Engine v7` (`Stage 718A`) | `CE0..CE7` + `athstats` | **`0.0%` FP / `0.0%` FN** (`25`-field `784B` + `64`-EVM + `CE0..7`) |
