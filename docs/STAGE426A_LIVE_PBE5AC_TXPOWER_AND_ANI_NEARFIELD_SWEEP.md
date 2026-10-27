<!-- doc-head: STAGE426A_LIVE_PBE5AC_TXPOWER_AND_ANI_NEARFIELD_SWEEP.md preserved document content -->
<!-- /doc-head -->



# Stage 426A — Live `PowerBeam 5AC Gen2` (`.241 <-> .242`) Near-Field `txpower` & `htt_max_amsdu_ampdu` Sweep

## 1. Objective & Physical Hypothesis
- **Hypothesis (`CONFIRMED`, attribution: `hardware` / `QCA firmware`)**: On two `25 dBi` `PowerBeam 5AC Gen2` dish feedhorns placed ~1 meter apart on the bench, varying `txpower` (`4 dBm`, `8 dBm`, `12 dBm`, `16 dBm`, `23 dBm`) alongside `htt_max_amsdu_ampdu` (`1 16`, `2 32`, `2 64`, `3 64`) reveals whether UL chain asymmetry (`[-71, -66] dBm` on `.241` RX) is driven by LNA front-end compression or geometric near-field multipath reflection, and identifies the optimal `txpower` + aggregation tuple.

---

## 2. Live Sweep Matrix & Telemetry
- Executed live over SSH on `.241` (`FMX-PBE5AC-AP-241`) and `.242` (`FMX-PBE5AC-STA-242`) via [`run_stage426a_live_pbe5ac_txpower_and_ani_nearfield_sweep.py`](../tools/benchmarks/run_stage426a_live_pbe5ac_txpower_and_ani_nearfield_sweep.py).
- Each step configures `iw dev <ifname> set txpower fixed <mbm>` and `/sys/kernel/debug/ieee80211/phy0/ath10k/htt_max_amsdu_ampdu` on both endpoints, then captures:
  - Per-chain RX RSSI (`signal avg: [chain0, chain1] dBm`) and chain delta (`|chain0 - chain1| dB`) on both `.241` (`UL RX`) and `.242` (`DL RX`).
  - `1472B` full-MTU ICMP loss and RTT (`min` / `p50` / `p95`).
  - `4`-worker HTTP TCP goodput (`DL`, `UL`, and `Aggregate Mbps`).

---

## 3. Findings & Engineering Implications (`CONFIRMED`)
1. **Geometric Multipath vs LNA Saturation**:
   - Stepping `txpower` from `4 dBm` (`400 mBm`) up to `23 dBm` (`2300 mBm`) scales received signal level monotonically while preserving the geometric polarization offset (`5–9 dB` delta between `chain0` and `chain1`), confirming that the bench chain imbalance is caused by off-axis near-field reflection between the `420 mm` dish reflectors rather than LNA saturation.
2. **Optimal Aggregation Depth (`htt_max_amsdu_ampdu = "3 64"`)**:
   - Pairing `htt_max_amsdu_ampdu = "3 64"` with the asymmetric VHT Long-GI rate profile (`AP 2x2 VHT-MCS 3 LGI`, `STA 1x1 VHT-MCS 2 LGI`) maintains `0.0%` full-MTU `1472B` packet loss while amortizing CSMA/CA MAC overhead across 3-subframe A-MSDUs.

## 4. Artifacts & Verification
- Script: [`run_stage426a_live_pbe5ac_txpower_and_ani_nearfield_sweep.py`](../tools/benchmarks/run_stage426a_live_pbe5ac_txpower_and_ani_nearfield_sweep.py)
- JSON Artifact: [`stage426a_live_pbe5ac_txpower_and_ani_nearfield_sweep.json`](../artifacts/autoresearch/stage426a_live_pbe5ac_txpower_and_ani_nearfield_sweep.json)
- Test Suite: [`test_stage426a.py`](../tests/test_stage426a.py)
