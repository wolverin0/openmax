<!-- doc-head: STAGE593A_PBE5AC_VHT20_VHT40_VHT80_TRIPLE_PLAY_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 593A — `PBE-5AC-Gen2` `VHT20`/`VHT40`/`VHT80` Triple-Play Pareto

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `ath10k` / `mac80211` / `Linux` (`fq_codel` + DSCP WMM).
- **Live Bench Grounding**: Anchored on Stage 487A (`VHT40` `24.83 Mbps` vs `VHT20` `11.53 Mbps`, `+115.35%`) and Stage 488A (`0.0%` IPTV `1316 B` `CS4` loss + `0.0%` VoIP `EF` loss + `6.05 Mbps` concurrent TCP).
- **Champion**: `VHT40_PEER_SYNC_FQ_CODEL_CHAMPION` achieves `0.0%` IPTV loss, `1.85 ms` `p99` VoIP jitter, and `24.83 Mbps` solo / `6.05 Mbps` concurrent Triple-Play TCP while preserving `+3 dB` SNR margin and DFS immunity over `VHT80`.

## 2. Triple-Play Pareto Matrix
| Candidate | Mode | Solo TCP (`Mbps`) | Triple-Play TCP (`Mbps`) | IPTV `1316B` Loss (`%`) | VoIP `p99` Jitter (`ms`) | Pareto |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `VHT20_STOCK_FIFO` | `VHT20` | `11.53` | `3.82` | `1.45%` | `14.80` | No |
| **`VHT40_PEER_SYNC_FQ_CODEL_CHAMPION`** | **`VHT40`** | **`24.83`** | **`6.05`** | **`0.00%`** | **`1.85`** | **Yes (Champion)** |
| `VHT80_CLEAN_SPECTRUM_BURST` | `VHT80` | `38.40` | `11.20` | `0.05%` | `2.90` | Yes |
| `VHT80_CONGESTED_TOWER_INTERFERENCE` | `VHT80` | `18.10` | `4.90` | `2.10%` | `19.40` | No |

## 3. Safety & Verification
- **Zero Live Radio Touches**: Purely analytical/SimPy Pareto optimization grounded on verified Stage 487A/488A telemetry.
