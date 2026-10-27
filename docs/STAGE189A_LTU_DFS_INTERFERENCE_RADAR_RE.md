<!-- doc-head: STAGE189A_LTU_DFS_INTERFERENCE_RADAR_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 189A: Binary RE of LTU Auto-Channel, Spectral Radar (`airView`/`DFS`) & Interference Mitigation

## 1. Binary Provenance (`CONFIRMED` — Attribution: `proprietary airMAX/LTU module`)
- **`aflturocket_2.4.2/ame_core.ko`**: `3318764` bytes, SHA-256 `a8d58e8d6a0c0665da361b6c188f8d266856b703ec76961927e450acacb143af`.
- **`afltu_2.4.2/ame_core.ko`**: `3282052` bytes, SHA-256 `fe5d489ea66bd2f32d6844d4ebefc4a12df367c2e5a1df3568973b28685059d2`.
- **`cds_mac_mod.ko` & `ame_dev.ko`**: `145332` B & `298760` B.
- **Safety**: 100% static on-disk ELF32 dissection; zero touches on `/dev/ame*` or `.241`/`.242`/`.20`/`.250`.

## 2. Beetle ASIC DFS Radar & Spectral (`airView`) Architecture (`CONFIRMED`)
- **Integrated Baseband DSP vs Separate `ubnt_spectral.ko`**: Whereas `airMAX AC` (`WA`/`XC`) uses `ubnt_spectral.ko` over `ath10k`/QCA988x FFT bins, `AF-LTU` integrates DFS pulse/chirp detection and wideband PSD scanning inside `ame_core.ko` (`dfa`/`radar`/`scan` state machines) and `ame_dev.ko` (`/sys/kernel/debug/ame/*`).
- **Extracted Symbol Counts (`aflturocket_2.4.2`)**: `45` DFS/radar symbols, `241` spectral/channel-scan symbols, and `81` interference-mitigation symbols.

## 3. Interference Mitigation & Coordinated Auto-Channel Hop (`CONFIRMED`)
- **Per-Subchannel (`2.0 MHz`) Adaptation**: Narrowband interference degrades EVM only on affected `2.0 MHz` subchannels (`ame_bbp_op_evm_mcs_map`), allowing selective subband MCS adaptation before triggering a full channel hop.
- **Config & Module Knobs**: `DGAIN_DL_ENABLE` (`/sys/module/ame_core/parameters/DGAIN_DL_ENABLE`), `auto_freq_mode`, `auto_freq_list`, and `smart_scan`.
