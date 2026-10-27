<!-- doc-head: STAGE601A_CROSS_FLEET_CHAMPION_V52_AND_TESTER_MATRIX.md preserved document content -->
<!-- /doc-head -->



# Stage 601A — Cross-Fleet Champion `v52.0` & Tester Matrix (`600` Cross-Lane Windows)

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-601A`
- **Champion Version**: **`v52.0`**
- **Cumulative Window Milestone (`600` Total Windows)**:
  - **`WA` Lane**: `228` counterbalanced `A1 -> B1 -> A2 -> B2` windows.
  - **Multi-Radio (`XC`/`2XC`/`XM`/`XW`) Lane**: **`192`** counterbalanced windows (`Stage 597A`, `R1..R122`).
  - **`AF-LTU` (`Beetle` + `ame_ASIC0`) Lane**: `180` counterbalanced windows.

## 2. Key Promotions in Cross-Fleet Champion `v52.0`
1. **`WMI_PEER_ASSOC_CMDID` Channel-Width Sync + Dynamic `LGI`/`SGI` (`Stage 597A`)**: Eliminates stale `PEER_CHWIDTH_20MHZ` descriptor rate-control stalls on `VHT40` transitions (`+52.3%` bulk TCP on `WA`/`XC`).
2. **`AF-LTU` Listen-Before-Talk (`LBT`) + Interference Mitigation (`Stage 598A`)**: `lbt_enable=1` (`-72 dBm` ED threshold) + `bbp_rf_set_intf_mitigation=2` (`0.0%` collision loss, `2.95 ms` `RTT p99`, `568.4 Mbps`).
3. **`PBE-5AC-Gen2` & `LBE-5AC-Gen2` Field Certification (`Stage 599A`)**: Certified at `24.83 Mbps` `VHT40` bulk TCP and `0.0%` `1316B` IPTV loss (`CS4` `0x80` + `AQL 2000`).

## 3. Artifacts
- **Script**: [`tools/autoresearch/build_stage601a_cross_fleet_champion_v52_and_tester_matrix.py`](../tools/autoresearch/build_stage601a_cross_fleet_champion_v52_and_tester_matrix.py)
- **Receipt**: [`artifacts/autoresearch/stage601a_cross_fleet_champion_v52_and_tester_matrix.json`](../artifacts/autoresearch/stage601a_cross_fleet_champion_v52_and_tester_matrix.json)
