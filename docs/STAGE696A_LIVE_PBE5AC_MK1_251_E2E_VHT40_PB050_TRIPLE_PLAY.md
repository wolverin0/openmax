<!-- doc-head: STAGE696A_LIVE_PBE5AC_MK1_251_E2E_VHT40_PB050_TRIPLE_PLAY.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 696A — Live `.241 <-> .242` End-to-End via `MK1-251` Triple-Play Stress (`PtP Champion v4`)

- **Claim Status**: `CONFIRMED`
- **Attribution**: `QCA firmware` + `ath10k` + `mac80211` + `Linux`
- **Topology**: `Windows Host PC` $\rightarrow$ `Boca 3` (`198.18.0.45` AP) $\rightarrow$ `VHT40` `PB-040/050` OTA `4addr` WDS $\rightarrow$ `198.18.0.46` STA (`MK1-251` `Boca 7`)

## 1. Live End-to-End L2/L3 WDS & Single-Stream TCP Verification (`VHT40` + `PB-040/050`)
- **`4addr` WDS Bridge**: `phy2-ap0.sta1` (`AP_WDS_IF=1`) $\leftrightarrow$ `phy2-sta0` (`STA_4ADDR=1`), `multicast_snooping=1`, and `multicast_to_unicast=1` active on both endpoints.
- **Host PC $\rightarrow$ `.241` $\rightarrow$ OTA `VHT40` $\rightarrow$ `.242` (`MK1-251` `Boca 7`) Single-Stream TCP Transfer**:
  - `4,194,304 B` transferred at **`11.18 Mbps`** (`+65.1%` over `VHT20`'s `6.77 Mbps` in `Stage 489A`).

## 2. Simultaneous Triple-Play Stress (`VoIP 64B` + `IPTV 1316B` + `4x Bulk TCP`) on `VHT40`
| Metric | `Arm A` (`VHT40` Un-tuned `aql=24000`, `fq_quantum=1514`, `0x29e00=0x136a131a`) | `Arm B` (`PtP Champion v4`: `VHT40` + `PB-040/050`, `aql=1500/2000`, `fq_quantum=300`) | Delta |
| :--- | :--- | :--- | :--- |
| **VoIP `64B` Tail `p95` RTT** | `31.219 ms` | **`22.501 ms`** | **`-27.9%` tail latency** |
| **VoIP `64B` Jitter** | `8.497 ms` | **`5.200 ms`** | **`-38.8%` jitter** |
| **IPTV `1316B` Loss** | `0.0%` | **`0.0%`** (`10/10` delivered) | **`0.0%` loss** |
| **Concurrent Bulk TCP** | `7.23 Mbps` | **`6.85 Mbps`** | Sustained under AQL bounding |
| **Post-Restore `VHT20` `1472B` Loss** | — | **`0.0%`** (`6/6` delivered, `min=2.272 ms`) | Clean `WMI_PEER_ASSOC` restore |

## 3. Artifacts & Verification
- Script: [run_stage696a_live_pbe5ac_mk1_251_e2e_vht40_pb050_triple_play.py](<repo>/tools/benchmarks/run_stage696a_live_pbe5ac_mk1_251_e2e_vht40_pb050_triple_play.py)
- Artifact: [stage696a_live_pbe5ac_mk1_251_e2e_vht40_pb050_triple_play.json](<repo>/artifacts/autoresearch/stage696a_live_pbe5ac_mk1_251_e2e_vht40_pb050_triple_play.json)
- Pytest: [test_stage696a.py](<repo>/tests/test_stage696a.py)
