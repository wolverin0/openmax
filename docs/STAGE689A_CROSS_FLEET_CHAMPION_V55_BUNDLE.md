<!-- doc-head: STAGE689A_CROSS_FLEET_CHAMPION_V55_BUNDLE.md preserved document content -->
<!-- /doc-head -->



# Stage 689A — Cross-Fleet Champion `v55.0` Bundle (`728` Total Cross-Lane Windows)

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-689A`
- **Champion Version**: **`v55.0`**
- **Total Counterbalanced Windows (`728`)**: `284` `WA v11` + `228` `Multi-Radio` + `216` `LTU v16`.
- **Guarida `v6.0` Aggregate Capacity**: **`457.90 Mbps`** across `.60-.61` backbone (`153.58 Mbps`) and the 3 Guarida sectors (`.84`, `.82`, `.83` under `Fixed 10ms 67/33` + `39 us` Slot Guard + `7935B`/`3839B` A-MSDU).

## 2. Unified Sub-Champions in `v55.0`
| Sub-Champion | Version | Windows | Headline Metric |
| :--- | :--- | :--- | :--- |
| **`WA Champion`** | **`v11.0`** | `284` | Triple Xtensa Stack (`PB-040` + `PB-050` + `PB-060`) + `WMI_PEER_ASSOC` Sync |
| **`Multi-Radio`** | **`v55.0`** | **`228`** | `97.1 Mbps` (`XC .198`), `96.7 Mbps` (`2XC .253`), `89.4 Mbps` (`XM/XW .20`) |
| **`LTU Champion`** | **`v16.0`** | `216` | `576.4 Mbps`, `78.4%` `4096-QAM` (`12X`), `-42.6 dB` UL EVM |
| **`PtP Champion`** | **`v3.0`** | Certified | `24.83 Mbps` `VHT40`, `0.0%` `1316B` IPTV loss (`CS4 0x80` + `AQL 2000`) |
| **`Guarida Tower`** | **`v6.0`** | `3` Panels / `32` CPEs | **`457.90 Mbps`** aggregate capacity (`+34.84%` DL airtime on `Panel2 .82`) |

## 3. Artifacts & Tests
- **Script**: [`tools/autoresearch/build_stage689a_cross_fleet_champion_v55_bundle.py`](../tools/autoresearch/build_stage689a_cross_fleet_champion_v55_bundle.py)
- **Receipt**: [`artifacts/autoresearch/stage689a_cross_fleet_champion_v55_bundle.json`](../artifacts/autoresearch/stage689a_cross_fleet_champion_v55_bundle.json)
- **Pytest**: [`tests/test_stage689a.py`](../tests/test_stage689a.py)
