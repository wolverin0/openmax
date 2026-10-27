<!-- doc-head: STAGE377A_LTU_SUBBAND_CINR_PUNCTURING_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 377A — Ground-Up Binary RE of LTU Per-Subband `CINR` / Constellation `EVM` Telemetry & Adaptive Sub-Channel Puncturing

- **Status**: `CONFIRMED`
- **Attribution**: `proprietary airMAX/LTU module`, `hardware`
- **Symbols Dissected**: **`819`** `CINR`/`EVM`/subband/modulation/LDPC symbols across `ame_core.ko` and `cds_mac_mod.ko` (`afltu_2.4.2` & `aflturocket_2.4.2`).

## 1. 8-Subband Pilot `CINR` Slicer & Modulation Thresholds (`CONFIRMED`)
The `ame_asic0` (`Beetle` FPGA) divides any `40/50/60/80/100 MHz` channel into **`8` contiguous OFDMA subbands** (`5.0 MHz` each at `40 MHz`, `6.25 MHz` at `50 MHz`, `12.5 MHz` at `100 MHz`) and computes per-subband pilot Constellation Error Vector Magnitude (`EVM` / `CINR`) at `0.25 dB` resolution every `2 ms` superframe:

| LTU Rate Multiplier | Constellation & Code Rate | Required Subband `CINR` (`dB`) | Equivalent Pilot `EVM` (`dB`) |
| :--- | :--- | :--- | :--- |
| **`12x`** | `4096-QAM` (`9/10` LDPC) | **`>= 38.0 dB`** | `<= -38.0 dB` (`-43 dB` PA floor) |
| **`10x`** | `1024-QAM` (`5/6` LDPC) | **`>= 33.0 dB`** | `<= -33.0 dB` |
| **`8x`** | `256-QAM` (`3/4` LDPC) | **`>= 27.0 dB`** | `<= -27.0 dB` |
| **`6x`** | `64-QAM` (`2/3` LDPC) | **`>= 21.0 dB`** | `<= -21.0 dB` |
| **`4x`** | `16-QAM` (`1/2` LDPC) | **`>= 14.0 dB`** | `<= -14.0 dB` |

## 2. Adaptive Sub-Channel Puncturing vs `802.11ac` Wideband Step-Down (`CONFIRMED`)
- **Legacy `802.11ac` (`QCA988x` `ath10k`) Weakness**: A single narrowband `5..10 MHz` spur or adjacent-sector overlap corrupts coded bits across the entire `40/80 MHz` OFDM symbol, forcing `ratectrl` to step the entire `80 MHz` channel down from `8x` (`256-QAM`) to `4x` (`16-QAM`), losing `> 50%` of link capacity.
- **LTU Subband Puncturing / Bit-Loading (`ame_core.ko` + `cds_mac_mod.ko`)**: `modemer` (`SCHED_FIFO 55`) masks or steps down **only the corrupted `1/8th` subband** while keeping the other **`7/8th` (`87.5%`) of the spectrum running at `4096-QAM 12x`**.
