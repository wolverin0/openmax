<!-- doc-head: STAGE301A_LTU_THERMAL_TCXO_IQ_CAL_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 301A: Binary RE of LTU Thermal PA, TCXO/AFC & IQ Imbalance Calibration Loops

## 1. Binary Provenance (`CONFIRMED` — Attribution: `proprietary airMAX/LTU module`)
- **`afltu_2.4.2/ame_core.ko`**: SHA-256 `fe5d489ea66bd2f32d6844d4ebefc4a12df367c2e5a1df3568973b28685059d2`.
- **Extracted Calibration Symbols**: `204` thermal/PA/cal symbols, `74` TCXO/CFO/PLL symbols, `679` IQ/LO/BBP symbols.
- **Safety**: 100% static on-disk ELF32 dissection; zero touches on `/dev/ame*` or `.241`/`.242`/`.20`/`.250`.

## 2. Three Closed-Loop Calibration Subsystems (`CONFIRMED`)
1. **Thermal PA Bias & ALC Loop**: Compensates PA gain droop over temperature (`-40C..+65C`) to prevent third-order intermodulation (`IMD3`) and EVM floor degradation at `4096-QAM` (`22 dBm` PtP / `21 dBm` PtMP backoff).
2. **VCTCXO / AFC Carrier Frequency Offset (`CFO`) Loop (`/bin/af afc`)**: Steers the CPE crystal DAC against the AP's downlink pilot phase reference so uplink OFDMA subchannels arrive without inter-carrier interference (`ICI`).
3. **TX/RX IQ Imbalance & LO Leakage Cancellation**: Keeps image rejection `> 48 dBc` so `4096-QAM` (`-42 dB` EVM threshold) can lock.
