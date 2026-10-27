<!-- doc-head: STAGE12_QCA988X_TARGET_DRAM_AND_CHANNEL_DUMP_ANALYZER.md preserved document content -->
<!-- /doc-head -->

# Stage 12 — QCA988x Target DRAM & Baseband Channel-Dump / CFR Packing Analyzer (Workstream E5)

## 1. Executive Summary

This document defines the offline target-memory differential analysis and baseband channel-dump (`CHAN_TAB_B0/B1` / `bb_length`) complex tone-packing hypothesis evaluator for **QCA988x / AR9888 v2 ("Peregrine")** hardware (Workstream E5 of `openMAX` Physical-Boundary Phase 0).

All analysis routines and synthetic verification fixtures are implemented in:
- [`tools/qca988x/memory_diff_analyzer.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/qca988x/memory_diff_analyzer.py)
- [`artifacts/qca988x/memory_diff_fixture_report.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/qca988x/memory_diff_fixture_report.json)
- [`tests/test_qca988x_memory_diff_analyzer.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_qca988x_memory_diff_analyzer.py)

---

## 2. QCA988x Target Memory & Baseband Window Architecture (`CONFIRMED`)

From `drivers/net/wireless/ath/ath10k/pci.c` (`L01`), `drivers/net/wireless/ath/ath10k/hw.h` (`L02`), and `dl/include/AR9888/v2/extra/hw/bb_lc_reg.h` (`Q14`), the host can inspect target memory and baseband tables via Copy Engine 7 (`CE_DIAG` / `ath10k_pci_diag_read_mem`) or UTF `CMD_MEMREAD` (`42`) / `CMD_REGREAD` (`9`), subject to strict **4-byte alignment**:

| Memory / Register Window | Base Address (`Hex`) | Size / Span | Source ID | Physical Role |
| :--- | :--- | :--- | :--- | :--- |
| **`QCA988X_DRAM_ADDR`** | `0x00400000` | `0x00050000` (`320 KB`, `0x00400000..0x0044ffff`) | `L01` (`pci.c`) | Main Xtensa target DRAM holding descriptors, peer tables, rings, and dynamic buffers. |
| **`QCA988X_HOST_INTEREST_ADDRESS`** | `0x00400800` | `312 B` (`78 x uint32`) | `L02` (`hw.h`) | Root pointer table (`hi_app_host_interest`, `hi_board_data`, `hi_dbglog_config`, `hi_ACS_flags`). |
| **`QCA988x Target ROM`** | `0x00940000` | `0x00060000` (`0x00940000..0x0099ffff`) | `L01` / `Q03` | Mask ROM code region referenced by target function pointers and patch tables. |
| **`PHY_BB_CHAN_INFO_CHAN_TAB_B0`** | `0x00009b00` | `56..242 x uint32` (`CHANINFO_WORD`) | `Q14` (`bb_lc_reg.h`) | Chain 0 baseband per-subcarrier channel-estimate (`H`) table memory window. |
| **`PHY_BB_CHAN_INFO_CHAN_TAB_B1`** | `0x0000ab00` | `56..242 x uint32` (`CHANINFO_WORD`) | `Q14` (`bb_lc_reg.h`) | Chain 1 baseband per-subcarrier channel-estimate (`H`) table memory window. |
| **`PHY_BB_CHANINFO_CTRL`** | `0x0000a370` | `4 B` (`bits [3:0]`) | `Q14` (`bb_lc_reg.h`) | `CAPTURE_CHAN_INFO` (`bit 0`), `DISABLE_CHANINFOMEM` (`bit 1`), `CAPTURE_SOUNDING_PACKET` (`bit 2`), `CHANINFOMEM_S2_READ` (`bit 3`). |

---

## 3. Multi-Snapshot Differential & Packet-Correlation Classifier

Given $K \ge 2$ aligned target memory snapshots $S_0, S_1, \dots, S_{K-1}$ paired with cumulative packet/sounding counts $P_0, P_1, \dots, P_{K-1}$, [`analyze_memory_snapshots()`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/qca988x/memory_diff_analyzer.py#L148-L294) clusters modified 32-bit words (bridging gaps of $\le 4$ words) and classifies each contiguous region into one of five physical categories:

1. **`HOST_INTEREST_TABLE`**: Overlaps `0x00400800..0x00400938` (`struct host_interest`), automatically decoding `hi_app_host_interest` (`+0x00`), `hi_failure_state` (`+0x04`), `hi_board_data` (`+0x1c`), `hi_board_data_initialized` (`+0x20`), `hi_dbglog_config` (`+0x4c`), `hi_option_flag` (`+0x70`), and `hi_ACS_flags` (`+0xc4`).
2. **`MONOTONIC_COUNTER_BLOCK`**: Words with non-negative inter-snapshot deltas ($\Delta w_k \ge 0$) and strong Pearson correlation ($r \ge 0.75$) with $\Delta P_k$.
3. **`TARGET_DRAM_POINTER_RING`**: Regions containing $\ge 2$ valid 4-byte aligned target DRAM addresses (`0x00400000 <= ptr < 0x00450000`), identifying DMA/HTT/descriptor ring headers.
4. **`PACKET_CORRELATED_DESCRIPTOR_OR_CSI_BUFFER`**: Multi-dword regions ($\ge 16$ changed words) whose update activity correlates ($r \ge 0.50$) with packet/sounding bursts (`rx_ppdu_end` descriptors or copied `CHAN_TAB_B0/B1` channel dumps).
5. **`DYNAMIC_SCRATCH_REGION`**: Uncorrelated background timer/RTOS state.

---

## 4. Baseband Channel-Dump / CFR Complex Tone-Packing Hypothesis Evaluator

Because the exact bit-packing inside `PHY_BB_CHAN_INFO_CHAN_TAB_B0/B1` (`CHANINFO_WORD [31:0]`) is not documented in prose in `bb_lc_reg.h` (`Q14`), [`evaluate_channel_dump_packing_hypotheses()`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/qca988x/memory_diff_analyzer.py#L377-L458) tests four physical packing models against any captured channel-dump blob:

| Hypothesis ID | Bit Layout in 32-bit `CHANINFO_WORD` | Applicability | Physical Discriminator |
| :--- | :--- | :--- | :--- |
| **`H_10BIT_IQ_WORD32`** | `I = signed_10bit(bits[9:0])`, `Q = signed_10bit(bits[19:10])`, `reserved = bits[31:20]` | `EXACT_AR9888_PEREGRINE_CANDIDATE` | Matches Atheros 10-bit signed I/Q CSI lineage; 1 word per tone (`56` words = `224 B` for VHT20). |
| **`H_12BIT_IQ_WORD32`** | `I = signed_12bit(bits[11:0])`, `Q = signed_12bit(bits[23:12])`, `reserved = bits[31:24]` | `EXACT_AR9888_PEREGRINE_CANDIDATE` | Matches 12-bit internal FFT/equalizer precision; 1 word per tone (`56` words = `224 B` for VHT20). |
| **`H_8BIT_DUAL_TONE_WORD32`** | Two `(int8 I, int8 Q)` tones packed per 32-bit word | `LEGACY_COMPACT_CANDIDATE` | Compact 2-tone-per-dword format (`28` words = `112 B` for 56 tones). |
| **`H_EXP_MANTISSA_LATER_CFR`** | `13-bit I`, `13-bit Q`, `4-bit` shared exponent `[29:26]` | `CROSS_CHIP_LATER_QCA` | Later `ath10k`/`ath11k` (`QCA9984` / `IPQ8074`) dedicated CFR DMA format (`L05`). |

### 4.1 Composite Physical Scoring Metric

For a real wireless channel $H(f_k) = |H(f_k)| e^{j(\phi_0 - 2\pi k \Delta\tau \Delta f)}$, adjacent OFDM subcarriers exhibit:
1. **High Circular Phase-Step Coherence (`45%` weight)**:
   $$\text{Coherence} = \left| \frac{1}{N-1} \sum_{k=0}^{N-2} e^{j\,\text{wrap}(\phi_{k+1} - \phi_k)} \right| \approx 1.0$$
   Under an incorrect bit-width split (e.g., decoding 10-bit I/Q as 12-bit I/Q), the MSBs of `I` bleed into the LSBs of `Q`, scrambling $\phi_k$ and collapsing circular phase coherence.
2. **Adjacent Magnitude Smoothness (`25%` weight)**: Low mean normalized adjacent-subcarrier amplitude jump $\frac{1}{N-1}\sum ||H_{k+1}| - |H_k|| / \overline{|H|}$.
3. **Reserved-Bit Zero Ratio (`20%` weight)**: Fraction of words where upper unused bits (`[31:20]` or `[31:24]`) are zero.
4. **Canonical OFDM Subcarrier Count Match (`10%` weight)**: Exact match against `52` (L-HT20), `56` (HT20/VHT20), `108` (HT40), `114` (VHT40), `234` (VHT80), or `242` (VHT80 full).
