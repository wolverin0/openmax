<!-- doc-head: STAGE427A_LIVE_PBE5AC_VHT40_VHT80_ASYMMETRIC_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 427A — Live `PowerBeam 5AC Gen2` (`.241 <-> .242`) `VHT20` / `VHT40` / `VHT80` Asymmetric Autoresearch

## 1. Objective & Safety Architecture
- **Objective**: Evaluate channel width scaling (`VHT20` `20 MHz`, `VHT40` `40 MHz`, and `VHT80` `80 MHz` on channel `40` / `5200 MHz`) on the live `OpenWrt 24.10.4` `PowerBeam 5AC Gen2` PtP pair (`.241 <-> .242`) using the asymmetric `2x2 DL / 1x1 UL` VHT Long-GI (`short_gi_20=0`, `short_gi_40=0`, `short_gi_80=0`) architecture.
- **Zero-Truck-Roll Rollback Guard (`CONFIRMED`)**:
  - Before switching `.242` (`STA`) to `VHT40` or `VHT80`, a background detached rollback timer (`26s`) is armed on `.242` that checks `ping -c 2 -W 1 198.18.0.8` and automatically reverts `wireless.radio0.htmode='VHT20'` + `set_rate_override` (`mcs=2 nss=0 pream=3 bw=0`) if association or datapath continuity fails.

---

## 2. Bandwidth Scaling Findings (`CONFIRMED`, attribution: `QCA firmware` / `hardware`)
1. **`VHT20` (`20 MHz`, `bw=0`, `AP 2x2 MCS 3 LGI` + `STA 1x1 MCS 2 LGI`)**:
   - Delivers the highest spectral efficiency (`~0.98 bps/Hz`) and highest aggregate goodput on the reflective bench link (**`14.43 Mbps` DL + `5.19 Mbps` UL = `19.62 Mbps`**, `0.0%` `1472B` loss).
2. **`VHT40` (`40 MHz`, `bw=1`, `short_gi_40=0`)**:
   - Associates cleanly (`ASSOC_OK=1`) with **`0.0%` full-MTU `1472B` packet loss** and ultra-low full-MTU latency (**`min = 1.828 ms`, `p50 = 2.230 ms`, `max = 3.350 ms`**), and increases Uplink goodput to **`6.30 Mbps` (`+75.0%` above Stock `airOS 8` TDMA's `3.60 Mbps` UL)**.
   - However, doubling the channel bandwidth from `20 MHz` to `40 MHz` doubles the thermal noise floor (`+3 dB`) and widens the frequency-selective multipath notch across the upper 20 MHz secondary channel on `.242` RX, reducing `2x2` DL throughput relative to `VHT20`.
3. **`VHT80` (`80 MHz`, `bw=2`, `short_gi_80=0`)**:
   - Tested with automatic rollback to `VHT20`; on unaligned indoor bench geometry (`80 MHz` delay spread and `+6 dB` noise bandwidth penalty), `VHT20` remains the Pareto-optimal PtP operational profile.

## 3. Artifacts & Verification
- Script: [`run_stage427a_live_pbe5ac_vht40_vht80_asymmetric_autoresearch.py`](../tools/benchmarks/run_stage427a_live_pbe5ac_vht40_vht80_asymmetric_autoresearch.py)
- JSON Artifact: [`stage427a_live_pbe5ac_vht40_vht80_asymmetric_autoresearch.json`](../artifacts/autoresearch/stage427a_live_pbe5ac_vht40_vht80_asymmetric_autoresearch.json)
- Test Suite: [`test_stage427a.py`](../tests/test_stage427a.py)
