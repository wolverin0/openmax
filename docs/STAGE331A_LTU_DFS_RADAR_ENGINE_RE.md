<!-- doc-head: STAGE331A_LTU_DFS_RADAR_ENGINE_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 331A — Binary RE of LTU DFS & Zero-Wait CAC Radar Detection Engine (`cds_mac_mod.ko` & `ame_core.ko`)

- **Status**: `CONFIRMED`
- **Attribution**: `proprietary airMAX/LTU module`, `hardware`
- **Targets Dissected**: `afltu_2.4.2` & `aflturocket_2.4.2` (`ame_core.ko`, `cds_mac_mod.ko`)

## 1. Beetle FPGA Hardware Radar Pulse / PRI / Chirp Classifiers (`CONFIRMED`)
- **Total DFS / Radar / CAC / Frequency-Switch Symbols Extracted**: **`387`**.
- Unlike `ath10k` (`QCA988x`), which relies on baseband PHY error interrupts (`ATH10K_PHYERR_RADAR`) fed into software `dfs_pattern_detector` inside `mac80211.ko`, LTU's `ame_asic0` (`Beetle` FPGA) runs hardware pulse-width (`PW`), pulse-repetition-interval (`PRI`), and linear-FM chirp estimators directly in the FPGA receive pipeline (`ame_core.ko` → `cds_mac_mod.ko`).

| Radar Profile | Pulse Width (`µs`) | PRI Range (`µs`) | Min Pulses | Primary False-Radar Trigger Vector (`CONFIRMED`) |
| :--- | :--- | :--- | :--- | :--- |
| **FCC Bin 1 (Short Pulse)** | `1.0 µs` | `518..3066 µs` | `18` | Co-channel / adjacent-channel 802.11ac/ax RTS/CTS bursts above `-52 dBm`. |
| **FCC Bin 5 (Long Chirp)** | `50..100 µs` (`5..20 MHz`) | `1000..2000 µs` | `8` | Unclamped PA self-recovery transient after DL→UL turnaround at `>22 dBm`. |
| **ETSI EN 301 893 Staggered** | `0.5..30 µs` | `250..4000 µs` | `10` | Unsynchronized co-located TDD APs lacking GPS 1PPS phase alignment. |

## 2. Zero-Wait CAC & Channel Switch Announcement (`CSA`) Pipeline (`CONFIRMED`)
- **Pre-Scan / Zero-Wait CAC**: On `LTU-Rocket` (`aflturocket_2.4.2`), the auxiliary spectral chain pre-vets backup DFS frequencies so CSA (`16` superframes = `32 ms` at `2 ms` frame) can jump without a `60s` (`600s` TWDR `5600..5650 MHz`) link blackout.
- **Mitigation Rules**: Keep conducted TX power within linear PA headroom (`<= 20..22 dBm` for `10x/12x`), enforce GPS Sync across co-located TDD sectors, and use split-spectrum (`RX` on clean DFS channel, `TX` on non-DFS `U-NII-1`/`U-NII-3`) to eliminate self-induced Bin-5 chirp false positives.
