<!-- doc-head: STAGE219A_LTU_SPLIT_SPECTRUM_AND_100MHZ_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 219A: Binary RE of LTU Split-Spectrum & `10..100 MHz` Bandwidth Tables

## 1. Binary Provenance (`CONFIRMED` — Attribution: `proprietary airMAX/LTU module`)
- **`aflturocket_2.4.2/ame_core.ko`**: SHA-256 `a8d58e8d6a0c0665da361b6c188f8d266856b703ec76961927e450acacb143af` (`3318764` B).
- **`afltu_2.4.2/ame_core.ko`**: SHA-256 `fe5d489ea66bd2f32d6844d4ebefc4a12df367c2e5a1df3568973b28685059d2` (`3282052` B).
- **`cds_mac_mod.ko` & `ame_dev.ko`**: SHA-256 `883a8c29b8fd3c58a29f1e76ece68178b415540c263679c95e12b6df6953369c` & `912a7c1923aad381ac38ae922b78f69888cec0bd1558c09abf2de68657c8b955`.
- **Safety**: 100% static on-disk ELF32 dissection; zero touches on `/dev/ame*` or `.241`/`.242`/`.20`/`.250`.

## 2. Independent TX/RX Split-Spectrum Architecture (`CONFIRMED`)
- **INI / Control Knobs (`/sys/devices/platform/ame_ctrl_dev/config`)**: `prefer_work_txfreq`, `prefer_work_rxfreq`, `txfreq`, `rxfreq` (in `/bin/ame_adj.sh` and `/var/etc/ame_ptmp_ap.cfg`).
- **Operational Advantage**: Allows placing Downlink (`AP TX -> CPE RX`) in a clean rural CPE receive band while placing Uplink (`CPE TX -> AP RX`) in a separate low-noise tower receive frequency, decoupling tower co-site uplink noise from downlink capacity.

## 3. Extracted 8-Bandwidth Tables (`10 / 20 / 30 / 40 / 50 / 60 / 80 / 100 MHz`) (`CONFIRMED`)
| Bandwidth (MHz) | `2.0 MHz` Subchannels | PtP Support | PtMP Support | `table_ptpPwrRange` 4096-QAM RX Sens (dBm) | `table_ptmpAPPwrRange` Low-Band 4096-QAM Target (dBm) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `10 MHz` | `5` | `True` | `True` | `-59` | `-66` |
| `20 MHz` | `10` | `True` | `True` | `-56` | `-63` |
| `30 MHz` | `15` | `True` | `True` | `-59` | `-61` |
| `40 MHz` | `20` | `True` | `True` | `-55` | `-60` |
| `50 MHz` | `25` | `True` | `True` | `-50` | `-58` |
| `60 MHz` | `30` | `True` | `False` | `None` | `-56` |
| `80 MHz` | `40` | `True` | `False` | `None` | `-54` |
| `100 MHz` | `50` | `True` | `False` | `None` | `-52` |
