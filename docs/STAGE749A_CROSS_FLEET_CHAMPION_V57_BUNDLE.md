<!-- doc-head: STAGE749A_CROSS_FLEET_CHAMPION_V57_BUNDLE.md preserved document content -->
<!-- /doc-head -->



# Stage 749A — Cross-Fleet Champion `v57.0` Bundle (`820` Total Cross-Lane Windows)

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-749A`
- **Champion Version**: **`v57.0`**
- **Total Counterbalanced Windows (`820`)**: `316` `WA v12` + `252` `Multi-Radio v57` + `252` `LTU v19`.

## 2. Unified Sub-Champions in `v57.0`
| Sub-Champion | Version | Windows | Headline Metric |
| :--- | :--- | :--- | :--- |
| **`WA Champion`** | **`v12.0`** | `316` | Triple Xtensa Stack + `pktlog=0x0` + Spectral/Radar `PHYERR` Storm Suppression |
| **`Multi-Radio`** | **`v57.0`** | **`252`** | `97.7 Mbps` (`XC .198`), `97.3 Mbps` (`2XC .253`), `90.0 Mbps` (`XM/XW .20`) |
| **`LTU Champion`** | **`v19.0`** | **`252`** | `super4096=1` + `DPD=1` + Thermal PA `2..4 C` Slope Comp (`0.2..0.4 dB` drift) |
| **`PtP Champion`** | **`v4.0`** | Certified | **`25.47 Mbps`** `VHT40`, `0.0%` `1316B` IPTV loss (`9 us` `IFS_SLOT` / `22 us` `ACK`) |
| **`Guarida Tower`** | **`v8.0`** | `3` Panels / `32` CPEs | `457.90 Mbps` aggregate capacity + `7935B` A-MSDU (`1.95x` payload density) |

## 3. Artifacts & Tests
- **Script**: [`tools/autoresearch/build_stage749a_cross_fleet_champion_v57_bundle.py`](../tools/autoresearch/build_stage749a_cross_fleet_champion_v57_bundle.py)
- **Receipt**: [`artifacts/autoresearch/stage749a_cross_fleet_champion_v57_bundle.json`](../artifacts/autoresearch/stage749a_cross_fleet_champion_v57_bundle.json)
- **Pytest**: [`tests/test_stage749a.py`](../tests/test_stage749a.py)
