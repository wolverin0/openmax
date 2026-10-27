<!-- doc-head: STAGE657A_CROSS_FLEET_CHAMPION_V54_BUNDLE.md preserved document content -->
<!-- /doc-head -->



# Stage 657A — Cross-Fleet Champion `v54.0` Bundle (`684` Total Cross-Lane Windows)

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-657A`
- **Champion Version**: **`v54.0`**
- **Total Counterbalanced Windows (`684`)**: `252` `WA` + `216` `Multi-Radio` + `216` `AF-LTU`.

## 2. Unified Sub-Champions in `v54.0`
| Sub-Champion | Version | Core Verified Stack |
| :--- | :--- | :--- |
| **`WA Champion`** | **`v11.0`** | Triple Xtensa RAM Stack (`PB-040` `.text 0x009b7584` + `PB-050` `4000ms` + `PB-060` `1504us` CABQ/TXOP) + `WMI_PEER_ASSOC` Sync |
| **`PtP Champion`** | **`v3.0`** | `24.83 Mbps` `VHT40` + `0.0%` `1316B` IPTV loss (`CS4 0x80` + `AQL 2000`) + 100% OTA Hybrid Interop |
| **`LTU Champion`** | **`v16.0`** | `super4096=1` + `DPD=1` + `2.0/2.5ms` TDMA + `40 MHz` Split + `LBT -72 dBm` + `ToF` `CP 1/8` (`576.4 Mbps`) |
| **`Guarida Tower`** | **`v5.0`** | `.60-.61` `5715 MHz` (`+7.99 dB` EVM, `+17.17 Mbps`) + `.84` `19.36h` 0-disconnect soak + `39 us` Slot Guard + `3839B`/`7935B` A-MSDU |

## 3. Artifacts & Tests
- **Script**: [`tools/autoresearch/build_stage657a_cross_fleet_champion_v54_bundle.py`](../tools/autoresearch/build_stage657a_cross_fleet_champion_v54_bundle.py)
- **Receipt**: [`artifacts/autoresearch/stage657a_cross_fleet_champion_v54_bundle.json`](../artifacts/autoresearch/stage657a_cross_fleet_champion_v54_bundle.json)
- **Pytest**: [`tests/test_stage657a.py`](../tests/test_stage657a.py)
