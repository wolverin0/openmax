<!-- doc-head: STAGE248A_LTU_5BOARD_CPE_FAMILY_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 248A: Binary RE of 5-Board LTU CPE Family (`0xae02` / `0xae07` / `0xae08` / `0xae09` / `0xae0b`)

## 1. Binary Provenance (`CONFIRMED` — Attribution: `proprietary airMAX/LTU module`)
- **`afltu_2.4.2/ame_core.ko`**: SHA-256 `fe5d489ea66bd2f32d6844d4ebefc4a12df367c2e5a1df3568973b28685059d2` (`3282052` B).
- **`afltu_2.4.2/bin/air_fpga`**: SHA-256 `4233baa6f19bde37a87f9c836e0e23e2b0a0c7288b257b51b8f498f8c8ab0994` (`2359369` B).
- **Safety**: 100% static on-disk ELF32 dissection; zero touches on `/dev/ame*` or `.241`/`.242`/`.20`/`.250`.

## 2. 5-Board LTU CPE Descriptor & PA/LNA Matrix (`CONFIRMED`)
| `board.sysid` | Model | Antenna Gain (dBi) | Max Conducted TX (dBm) | Max EIRP (dBm) | PA Backoff Table | Low-Band 4096-QAM TX (dBm) |
| :---: | :--- | :---: | :---: | :---: | :--- | :---: |
| `0xae02` | **LTU-Pro (AF-LTU5)** | `24 dBi` | `22 dBm` | `46 dBm` | `af_ltu5_mcs_txpwr_freq_dbm` | `0.01 dBm` |
| `0xae07` | **LTU-LR (Long-Range)** | `26 dBi` | `22 dBm` | `48 dBm` | `af_ltuLR_mcs_txpwr_freq_dbm` | `0.02 dBm` |
| `0xae08` | **LTU-Lite** | `13 dBi` | `22 dBm` | `35 dBm` | `af_ltu5_mcs_txpwr_freq_dbm` | `0.01 dBm` |
| `0xae09` | **LTU-XR (Extreme-Range)** | `29 dBi` | `22 dBm` | `51 dBm` | `af_ltuLR_mcs_txpwr_freq_dbm` | `0.02 dBm` |
| `0xae0b` | **LTU-Instant** | `13 dBi` | `22 dBm` | `35 dBm` | `af_ltu5_mcs_txpwr_freq_dbm` | `0.01 dBm` |
