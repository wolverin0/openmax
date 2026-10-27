<!-- doc-head: STAGE599A_PBE5AC_LBE5AC_TRIPLE_PLAY_VHT40_FIELD_CERTIFICATION.md preserved document content -->
<!-- /doc-head -->



# Stage 599A — `PBE-5AC-Gen2` & `LBE-5AC-Gen2` `VHT40` Triple-Play Field Certification

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-599A`
- **Certified Hardware**: `PBE-5AC-Gen2` (`WA`) and `LBE-5AC-Gen2` (`WA` `AR9342` + `QCA9882`).
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `hardware`.

## 2. Certified Benchmarks (`Stages 487A` & `488A`)
| Benchmark / Metric | Baseline / Unoptimized | Certified (`v52`) | Verdict |
| :--- | :--- | :--- | :--- |
| `VHT40` Bulk TCP (`Stage 487A` `WMI_PEER_ASSOC_CMDID` Sync) | `16.30 Mbps` (stale `HT20` peer descriptor) | **`24.83 Mbps`** (`+52.3%`, `-85.4%` retransmits) | **`CONFIRMED`** |
| `1316B` MPEG-TS IPTV Loss under Bulk TCP (`Stage 488A`) | `43.4%` loss (`BE` unmarked) | **`0.0%` loss** (`CS4` `0x80` WMM `VO`/`VI` + AQL `2000`) | **`CONFIRMED`** |
| Concurrent Bulk TCP during `4 Mbps` IPTV Stream | Collapses IPTV | **`6.05 Mbps`** (`1.622 ms` IPTV jitter) | **`CONFIRMED`** |

## 3. Artifacts
- **Script**: [`tools/autoresearch/build_stage599a_pbe5ac_lbe5ac_triple_play_vht40_field_certification.py`](../tools/autoresearch/build_stage599a_pbe5ac_lbe5ac_triple_play_vht40_field_certification.py)
- **Receipt**: [`artifacts/autoresearch/stage599a_pbe5ac_lbe5ac_triple_play_vht40_field_certification.json`](../artifacts/autoresearch/stage599a_pbe5ac_lbe5ac_triple_play_vht40_field_certification.json)
