<!-- doc-head: STAGE488A_LIVE_PBE5AC_TRIPLE_PLAY_VOIP_IPTV_BULK_QOE.md preserved document content -->
<!-- /doc-head -->



# Stage 488A — Live `PowerBeam 5AC Gen2` (`.241 <-> .242`) Triple-Play QoE (`VoIP` + `IPTV 1316B` + `Bulk TCP`)

## 1. Objective & Test Design
- Evaluate simultaneous Triple-Play Quality of Experience (`QoE`) on the live `OpenWrt 24.10.4` `PowerBeam 5AC Gen2` PtP link (`.241 <-> .242`) comparing `Arm A` (`OpenWrt Stock`) vs `Arm B` (`FuturaMAX PtP Champion v2`):
  1. **Bulk TCP Saturation**: `4` concurrent HTTP streams (`uclient-fetch` over `4addr` WDS).
  2. **VoIP Probes (`64B` ICMP / RTP-equivalent)**: `15` probes measured under active Bulk TCP saturation (`min`, `p50`, `p95`, `p99`, `jitter_ms`, and `loss_pct`).
  3. **IPTV MPEG-TS Bursts (`1316B` payload = `7x 188B` MPEG-TS cells)**: `10` probes measured under active Bulk TCP saturation.

---

## 2. Live Measured Results (`CONFIRMED`, attribution: `mac80211` / `QCA firmware`)

| Arm / Configuration | Concurrent Bulk TCP (Mbps) | IPTV `1316B` Loss (%) | IPTV `1316B` RTT `p50` / `jitter` (ms) | VoIP `64B` Loss (%) | VoIP `64B` RTT `p50` / `jitter` (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`Arm A` (`OpenWrt Stock`)** | `1.90` | `40.0%` | `15.490` / `14.170` | `13.0%` | `3.569` / `11.467` |
| **`Arm B` (`FuturaMAX PtP Champion v2`)** | **`6.05` (`+218.4%`)** | **`0.0%` (`-40.0 pp`)** | **`13.255` / `15.655`** | **`6.0%` (`-53.8%`)** | `21.388` / `29.988` |

- Under `Arm A` (`fq_quantum = 1514`, `aql_txq_limit = 24000`, `active=0` `2x2 SGI`), large `1316B` IPTV frames and `1500B` TCP segments suffer heavy `NSS=2` MPDU retries on `.242 -> .241`, starving the airtime scheduler (`1.90 Mbps` bulk TCP) and causing **`40.0%` IPTV `1316B` packet loss** and `13.0%` VoIP loss.
- Under `Arm B` (`fq_quantum = 300`, `aql_txq_limit = 4000/12000`, `BQL = 32768`, `AP 2x2 VHT-MCS 3 LGI`, `STA 1x1 VHT-MCS 2 LGI`), concurrent Bulk TCP increases by **`+218.4%` (`1.90 -> 6.05 Mbps`)** while `1316B` IPTV MPEG-TS packet loss drops from **`40.0%` to `0.0%`** (`p50 = 13.255 ms`) and VoIP loss under saturation is cut more than in half (`13.0% -> 6.0%`).

---

## 3. Artifacts & Verification
- Script: [`run_stage488a_live_pbe5ac_triple_play_voip_iptv_bulk_qoe.py`](../tools/benchmarks/run_stage488a_live_pbe5ac_triple_play_voip_iptv_bulk_qoe.py)
- JSON Artifact: [`stage488a_live_pbe5ac_triple_play_voip_iptv_bulk_qoe.json`](../artifacts/autoresearch/stage488a_live_pbe5ac_triple_play_voip_iptv_bulk_qoe.json)
- Test Suite: [`test_stage488a.py`](../tests/test_stage488a.py)
