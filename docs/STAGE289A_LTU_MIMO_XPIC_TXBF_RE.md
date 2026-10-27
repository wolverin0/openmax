<!-- doc-head: STAGE289A_LTU_MIMO_XPIC_TXBF_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 289A: Binary RE of LTU MIMO Matrix Modes (`2x2` XPIC, `SISO`/`STBC` & Chain Imbalance)

## 1. Binary Provenance (`CONFIRMED` — Attribution: `proprietary airMAX/LTU module`)
- **`afltu_2.4.2/ame_core.ko`**: SHA-256 `fe5d489ea66bd2f32d6844d4ebefc4a12df367c2e5a1df3568973b28685059d2` (`749` MIMO/BBP symbols).
- **`aflturocket_2.4.2/ame_core.ko`**: SHA-256 `a8d58e8d6a0c0665da361b6c188f8d266856b703ec76961927e450acacb143af`.
- **Safety**: 100% static on-disk ELF32 dissection; zero touches on `/dev/ame*` or `.241`/`.242`/`.20`/`.250`.

## 2. Extracted `SISO` vs `2x2 MIMO` Progression Tables (`CONFIRMED`)
- **`startThrd_siso` / `stayThrd_siso`**: `60%` / `0%`.
- **`autoMcsMimoTP` (Throughput Weights)**: `[263, 267, 271, 275, 279]`.
- **`autoMcsSisoTP` (Throughput Weights)**: `[7, 11, 15, 19, 23]`.
- **Cross-Pol & Chain Imbalance**: `4096-QAM` (`12x` spatial multiplexing, `MCS 31`) requires clean dual-slant/dual-pol isolation (`XPD >= 28 dB`) and chain0/chain1 balance within `<= 3.5 dB`; under severe single-chain obstruction (`> 5.5 dB` imbalance), `autoMcsUseSisoTbl` preserves link survival via `1x1`/diversity fallback.
