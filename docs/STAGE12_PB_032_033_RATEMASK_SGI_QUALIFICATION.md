<!-- doc-head: STAGE12_PB_032_033_RATEMASK_SGI_QUALIFICATION.md preserved document content -->
<!-- /doc-head -->

# Stage 12 — PB-032 & PB-033 Qualification: QCA988x Per-Peer Rate-Mask Latency Curve & Short-GI / RTS-CTS Micro-Regime Solver

**Task ID**: `T-PB-GEM1-17`  
**Status**: `SILICON_ANCHORED_QUALIFICATION_COMPLETE` (`automatic_execution_allowed = False`)  
**Implementation**: [`controller/pb_032_033_ratemask_sgi_solver.py`](../controller/pb_032_033_ratemask_sgi_solver.py)  
**Artifact Report**: [`artifacts/qca988x/pb_032_033_ratemask_sgi_qualification_20261024.json`](../artifacts/qca988x/pb_032_033_ratemask_sgi_qualification_20261024.json)

---

## 1. Gate PB-032: Per-Peer Rate-Mask Update Latency vs. Target 4-Series MRR

Anchored to live `LAP-120` silicon measurements ([`pb_021_031_050_live_lap120_silicon_qualification_20261024.json`](../artifacts/qca988x/pb_021_031_050_live_lap120_silicon_qualification_20261024.json)) and `umac.ko` / `athwlan` disassembly ([`pb_010_wmi_htt_strip_map.json`](../artifacts/qca988x/pb_010_wmi_htt_strip_map.json)):

| Mechanism | Control Hook | Apply Latency (`p50` / `p99`) | Minimum Safe Control Epoch | Role in FuturaMAX |
| :--- | :--- | :---: | :---: | :--- |
| **Host `nl80211_set_tx_bitrate_mask`** | `WMI_PEER_ASSOC_CMD` (`PCIe MMIO p50=197.08us` + HTT drain) | `1450 us` / `4200 us` | `>= 200 ms` | **Slow/Medium-Loop MCS Ceiling Controller** (prevents optimistic MCS 8/9 flapping at `6..14 km`) |
| **Target `0x9044` 4-Series MRR** | `WMI_PEER_RATE_RETRY_SCHED_CMDID` (`IRAM 0x00980e1c`) + PCU | `14.0 us` / `29.0 us` | `0.05 ms` (Sub-PPDU) | **Hardware Per-TXOP Retry Fallback** (`Series 0 -> 1 -> 2 -> 3` in `1232` cycles at `88.000 MHz`) |

---

## 2. Gate PB-033: Silicon-Exact `88.000 MHz` SGI, LDPC, A-MPDU & RTS/CTS Micro-Regime Solver

1. **Exact `88.000 MHz` Silicon Slot & ACK/CTS Timeout Equations**:
   - Verified across `coverage_class = 0..31` on `LAP-120` (`0x21070`, `0x21030`, `0x28014`):
     $$\text{SIFS} = 1232\text{ cycles} = 14.000\ \mu\text{s}$$
     $$\text{Slot}(c) = 792 + 264c\text{ cycles} = (9 + 3c)\ \mu\text{s}$$
     $$\text{ACK/CTS Timeout}(c) = 2640 + 264c\text{ cycles} = (30 + 3c)\ \mu\text{s}$$
2. **Short-GI (`400 ns`) vs. Long-GI (`800 ns`) Crossover Law**:
   - Enable `SGI (400 ns)` ONLY when `delay_spread_rms_ns <= 95 ns` AND `distance_km <= 6.0 km` AND `cinr_db >= 24.0 dB`. Above `95 ns` RMS delay spread or `>6.0 km`, forcing `LGI (800 ns)` eliminates inter-symbol interference (ISI) tail loss.
3. **HTT A-MPDU Depth (`16 / 32 / 64`) & Dynamic RTS/CTS Hysteresis**:
   - Live silicon readback confirmed `htt_max_amsdu_ampdu` switches cleanly between `3 16`, `3 32`, and `3 64`.
   - Keeps `rts=2347` (`off`) when `active_ul_cpes == 1` and `mac_retry_rate_pct < 4.0%`, avoiding the `6.9%..11.2%` RTS/CTS handshake tax across `1..14 km`, and switches to `rts=256` whenever `active_ul_cpes >= 2` or `mac_retry_rate_pct >= 4.0%`.

---

## 3. Verification

```powershell
pytest tests/test_pb_032_033_ratemask_sgi_solver.py -v
```
