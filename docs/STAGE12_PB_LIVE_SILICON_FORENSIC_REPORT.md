<!-- doc-head: STAGE12_PB_LIVE_SILICON_FORENSIC_REPORT.md preserved document content -->
<!-- /doc-head -->

# Stage 12: Live PB-021 / PB-031 / PB-050 QCA988x Silicon Measurement & Calibration-Table Forensic Report

## 1. Executive Summary

This report documents the bit-exact forensic analysis of live QCA988x (`AR9888 v2.0`, PCI `0000:00:00.0`) register captures from `LAP-120` (`OpenWrt 24.10.3 r28872-daca7c049b`, Linux `6.6.110 mips`), implemented in [`analysis/pb_live_silicon_forensic_analyzer.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/analysis/pb_live_silicon_forensic_analyzer.py) and stored in [`artifacts/qca988x/pb_live_silicon_forensic_report_20261024.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/qca988x/pb_live_silicon_forensic_report_20261024.json) (`forensic_report_sha256: d7c48e144ed6d7af38372bff531bc82d45c5604a2e20c26e3625bd9eb2e81623`).

---

## 2. `PB-050`: 88.000 MHz MAC Core Clock & Host PCIe MMIO Jitter Boundary

Live MMIO readback across `coverage_class = {0, 2, 6, 13, 20, 26, 31}` (`0 km` to `14 km`) confirms with **zero cycle error (`formula_bit_exact_across_all_classes = True`)**:

$$\text{SIFS}_{0\text{x}21030} = 1232\text{ cycles} = 14.000\ \mu\text{s}, \quad \text{EIFS}_{0\text{x}210\text{b}0} = 8096\text{ cycles} = 92.000\ \mu\text{s}$$

$$\text{Slot}_{0\text{x}21070}(c) = 792 + 264c = 88(9 + 3c)\text{ cycles}, \quad \text{ACK/CTS Timeout}_{0\text{x}28014}(c) = 2640 + 264c = 88(30 + 3c)\text{ cycles}$$

### Paired $N=160$ Clock & MMIO Syscall Jitter Benchmark
- **Silicon PCU Cycle Counter (`0x280f8`) vs `TSF2_L32` (`0x28120`)**: Mean `87.9815 cycles/us`, Median `87.9996 cycles/us` (`-4.55 ppm` median drift relative to `88.0000 MHz`).
- **Single PCIe MMIO Syscall Latency**: `p50 = 197.08 us`, `p95 = 531.72 us`, `p99 = 588.24 us`.
- **Host vs Target Midpoint Jitter**: `p50 = 6.46 us`, `p95 = 737.04 us`, `p99 = 813.82 us`.
- **Architectural Implication (`CONFIRMED`)**: Because host debugfs/PCIe MMIO readback exhibits `p99 = 813.82 us > 50 us`, sub-`50 us` fine slot TDMA cannot be driven from host MMIO polling alone; host-enforced `hMAC` airtime epochs must use $\ge 1000\ \mu\text{s}$ (`1.0 ms`) epochs while sub-`50 us` slot synchronization requires target-resident or WMI beacon/TSF timer anchoring.

---

## 3. `PB-021`: Baseband `CHANINFO` & Dual-Chain Calibration Banks (`0x29b00` / `0x2ab00`)

- `PHY_BB_CHANINFO_CTRL (0x2a370)` reads `0x000004c8` (`CAPTURE_CHAN_INFO=0`, `CHANINFOMEM_S2_READ=1`, `CHANINFO_20MHZ_SUBBAND=3`).
- `PHY_BB_CHANINFO_GAIN_DIFF (0x2a380)` reads `0x01ffdff7` (`low16 = -8201`, `high16 = +511`).
- Both 16-word calibration tables (`0x29b00..0x29b3c` on Chain 0 and `0x2ab00..0x2ab3c` on Chain 1) contain **16/16 non-zero words** structured as 5 subband calibration triplets `(primary_gain, secondary_gain, signed_phase_slope)` plus tail word (`0x29b3c = 0x038f`, `0x2ab3c = 0x04b0`), with a mean inter-chain secondary gain differential of `1.869 dB`.

---

## 4. `PB-031`: `PHY_BB_LDPC_CNTL1/2` & HTT A-MPDU Depth Authority

- `PHY_BB_LDPC_CNTL1 (0x29c04) = 0xffffff55`, `PHY_BB_LDPC_CNTL2 (0x29c08) = 0x0320ff55` (`ldpc_decoder_budget = 800 cycles = 9.091 us` at `88 MHz`).
- Live `htt_max_amsdu_ampdu` writes for A-MPDU depths `16`, `32`, and `64` read back `3 16`, `3 32`, and `3 64` cleanly, and exact baseline restoration (`coverage_class=0`, `htt_max_amsdu_ampdu="3 64"`) is verified.

---

## 5. Verification

```powershell
python analysis/pb_live_silicon_forensic_analyzer.py
python -m pytest tests/test_pb_live_silicon_forensic_analyzer.py -v
```
