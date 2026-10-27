<!-- doc-head: STAGE627A_CROSS_FLEET_CHAMPION_V53_200W_ALL_LANES.md preserved document content -->
<!-- /doc-head -->



# Stage 627A — Cross-Fleet Champion `v53.0` (`200+` Windows Across All 3 Lanes: `648` Total Windows)

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-627A`
- **Champion Version**: **`v53.0`**
- **`200+` Windows Milestone Across Every Lane (`648` Total Windows)**:
  - **`WA` Lane**: **`240`** counterbalanced `A1 -> B1 -> A2 -> B2` windows.
  - **Multi-Radio (`XC`/`2XC`/`XM`/`XW`) Lane**: **`204`** counterbalanced windows (`Stage 623A`, `R1..R128`).
  - **`AF-LTU` (`Beetle` + `ame_ASIC0`) Lane**: **`204`** counterbalanced windows.

## 2. Key Promotions in Cross-Fleet Champion `v53.0`
1. **Adaptive `TxBF`/`STBC`/`LDPC` Near-vs-Far-Field Rule (`Stage 624A`)**: Disables `TxBF` sounding in near-field (`< 6.2 m`) while keeping `LDPC=1` + low-MCS `STBC=1`, and enables `50 ms` `TxBF` sounding in far-field (`152.8 Mbps`, `0.1%` PER).
2. **`AF-LTU` Sub-$\mu$s `ToF` Ranging & `1/8` `CP` (`Stage 625A`)**: `tof_auto_ranging=1` + `CP=1/8` (`-42.6 dB` uplink EVM, `576.4 Mbps`).
3. **Guarida Full-Tower `39 us` Slot Guard & Adaptive `3839B`/`7935B` A-MSDU (`Stage 626A`)**: `+11.4%` uplink slot efficiency on `Panel2` (`.82`) & `Panel3` (`.83`), plus `+8.6 Mbps` on `Panel1` (`.84`).

## 3. Artifacts
- **Script**: [`tools/autoresearch/build_stage627a_cross_fleet_champion_v53_200w_all_lanes.py`](../tools/autoresearch/build_stage627a_cross_fleet_champion_v53_200w_all_lanes.py)
- **Receipt**: [`artifacts/autoresearch/stage627a_cross_fleet_champion_v53_200w_all_lanes.json`](../artifacts/autoresearch/stage627a_cross_fleet_champion_v53_200w_all_lanes.json)
