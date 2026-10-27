<!-- doc-head: STAGE645A_650STAGE_MILESTONE_CROSS_LANE_SCORECARD.md preserved document content -->
<!-- /doc-head -->


# Stage 645A — `650`-Stage Milestone Cross-Lane Scorecard

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `Linux` / `mac80211` / `ath10k` / `QCA firmware` / `proprietary airMAX/LTU module` / `hardware`.
- **700-Window Live Milestone**: Reconciles all multi-lane counterbalanced `A1 -> B1 -> A2 -> B2` campaigns and 5-Pillar deliverables at the `650`-Stage mark:
  - **`WA` Champion `v10` Windows**: **`256` windows** (`-81.96%` `p50` RTT `74.38 -> 13.42 ms`, `69.95 Mbps` E2E)
  - **`AF-LTU` Champion `v15` Windows**: **`204` windows** (`17` rounds on `.110`, `0` `/dev/ame*` touches)
  - **Multi-Radio Cross-Family Windows**: **`204` windows**
  - **`PBE-5AC-Gen2` PtP `VHT40` & Triple-Play Windows**: **`36` windows** (`24.83 Mbps`, `0.0%` IPTV loss)
  - **Total Verified Live Windows**: **`700` windows**

## 2. Cross-Lane Deliverable Scorecard
| Lane / Domain | Flagship Verified Deliverable | Cumulative Windows / Scope | Status |
| :--- | :--- | :---: | :---: |
| **`WA` (`QCA988x`)** | `fmx_wa_v10_256window_field_kit.sh` (`Stage 641A`) | `256` live windows | `CONFIRMED` |
| **`AF-LTU` (`Beetle`)** | `fmx_ltu_v15_204window_field_kit.sh` (`Stage 642A`) | `204` live windows (`5` boards) | `CONFIRMED` |
| **Guarida Tower (`34` EP)** | Full-Tower `v5` (`+35.78%` `441.0 Mbps`, `Stage 643A`) | `32` CPEs + `2` PtP | `CONFIRMED` |
| **Observability `v5`** | `25`-Field `784 B` `SIOCGATHSTATS` + `64`-EVM (`Stage 644A`) | `0.0%` FP / `0.0%` FN | `CONFIRMED` |
| **SquashFS & Showcase** | `180` SquashFS `v13` images + Showcase `v6` (`Stage 621A`) | `30` `WA`/`XC`/`XW` boards | `CONFIRMED` |
