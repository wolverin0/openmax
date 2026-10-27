<!-- doc-head: STAGE595A_600STAGE_PRE_MILESTONE_READINESS_AUDIT.md preserved document content -->
<!-- /doc-head -->


# Stage 595A — 600-Stage Pre-Milestone Readiness Audit

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `Linux` / `mac80211` / `ath10k` / `QCA firmware` / `proprietary airMAX/LTU module` / `hardware`.
- **Milestone Audit**: Validates cumulative counterbalanced live `A1 -> B1 -> A2 -> B2` windows and Ground-Up 5-Pillar deliverables ahead of the 600-stage milestone:
  - **`WA` (`QCA988x`) Live Windows**: `228` windows
  - **`AF-LTU` (`.110` Boca 5) Live Windows**: `180` windows (`15` rounds)
  - **Multi-Radio Cross-Family Windows**: `168` windows
  - **`PBE-5AC-Gen2` `VHT40` & Triple-Play PtP Windows**: `36` windows
  - **Total Live Counterbalanced Windows**: **`612` windows**

## 2. Five Ground-Up Pillars Readiness Matrix
| Ground-Up Pillar | Flagship Verified Deliverable | Status |
| :--- | :--- | :---: |
| **Pillar 1 (PHY & Spectral)** | `Super4096` PA DPD guard (`Stage 558A`), `DCXO` vs `TCXO` (`Stage 515A`), Subcarrier-51 notch (`Stage 480A`) | `CONFIRMED` |
| **Pillar 2 (ToF & Fresnel)** | `80 MHz` (`1.873 m`) ToF drift (`Stage 446A`), `6.15 m` near-field (`Stage 481A`), `peer_phymode` SGI (`Stage 591A`) | `CONFIRMED` |
| **Pillar 3 (Xtensa Target)** | Adaptive ANI `0x900d..0x900f` (`Stage 545A`), `0x9044` `50 us` HW retry (`Stage 447A`), DFS `120 s` CAC (`Stage 513A`) | `CONFIRMED` |
| **Pillar 4 (Coop Tower)** | Guarida v4 bundle (`Stage 516A`), `cbp_dur=900us` `+37.65%` Pareto (`Stage 547A`), `SOSA_Joaquin` EVM alerter (`Stage 594A`) | `CONFIRMED` |
| **Pillar 5 (Universal Kits)** | `180` `WA`/`XC`/`XW` SquashFS `v13` images (`Stage 561A`), `LTU` 5-board `v13` (`Stage 560A`) & LBT helper (`Stage 592A`) | `CONFIRMED` |
