<!-- doc-head: STAGE723A_CROSS_FLEET_CHAMPION_V56_BUNDLE.md preserved document content -->
<!-- /doc-head -->



# Stage 723A — Cross-Fleet Champion `v56.0` Bundle (`796` Total Cross-Lane Windows)

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-723A`
- **Champion Version**: **`v56.0`**
- **Total Counterbalanced Windows (`796`)**: `316` `WA v12` + `240` `Multi-Radio v56` + `240` `LTU v18`.
- **PtP Champion `v4.0` Benchmark**: **`25.47 Mbps`** `VHT40` bulk TCP (`0.0%` `1316B` IPTV loss) with `pktlog_filter=0x0` and distance-aligned `IFS_SLOT` / `ACK_CTS_TIMEOUT`.

## 2. Unified Sub-Champions in `v56.0`
| Sub-Champion | Version | Windows | Headline Metric |
| :--- | :--- | :--- | :--- |
| **`WA Champion`** | **`v12.0`** | `316` | Triple Xtensa Stack + `pktlog_filter=0x0` (`CE2`/`CE7` DMA relief) + Distance `ACK`/`Slot` |
| **`Multi-Radio`** | **`v56.0`** | **`240`** | `97.4 Mbps` (`XC .198`), `97.0 Mbps` (`2XC .253`), `89.7 Mbps` (`XM/XW .20`) |
| **`LTU Champion`** | **`v18.0`** | **`240`** | `576.4 Mbps`, `78.4%` `4096-QAM` (`12X`), `-42.6 dB` UL EVM |
| **`PtP Champion`** | **`v4.0`** | Certified | **`25.47 Mbps`** `VHT40` (`0.0%` `1316B` IPTV loss, `9 us` `IFS_SLOT` / `22 us` `ACK_TIMEOUT`) |
| **`Guarida Tower`** | **`v6.0`** | `3` Panels / `32` CPEs | `457.90 Mbps` aggregate capacity + `7935B` A-MSDU (`1.95x` payload density) |

## 3. Artifacts & Tests
- **Script**: [`tools/autoresearch/build_stage723a_cross_fleet_champion_v56_bundle.py`](../tools/autoresearch/build_stage723a_cross_fleet_champion_v56_bundle.py)
- **Receipt**: [`artifacts/autoresearch/stage723a_cross_fleet_champion_v56_bundle.json`](../artifacts/autoresearch/stage723a_cross_fleet_champion_v56_bundle.json)
- **Pytest**: [`tests/test_stage723a.py`](../tests/test_stage723a.py)
