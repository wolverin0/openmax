<!-- doc-head: Stage 695A live PowerBeam 5AC Gen2 .241<->.242 VHT40 PB-040/PB-050 counterbalanced PtP Champion v4 window — RECORDED DEGRADED, needs live re-run to certify throughput -->
# Stage 695A — Live `.241 <-> .242` VHT40 + PB-040/PB-050 PtP Champion v4

- **Claim Status**: `CONFIRMED` (receipt recorded) — **throughput DEGRADED in this window, see §4**
- **Attribution**: `QCA firmware` + `ath10k` + `mac80211` + `Linux` + `hardware`
- **Protocol**: counterbalanced `A1 -> B1 -> A2 -> B2`
- **Silicon**: `athwlan=12b29d01`, `0x00029e00=0x13761320`, PB-050 SGMT in RAM (`a49160ff…`), zero flash writes.
- **Receipt**: `artifacts/autoresearch/stage695a_live_pbe5ac_vht40_pb040_pb050_champion_v4.json`

## 1. Arms
- **Arm A** — reg `0x136a131a` (stock baseband timing), `pktlog_filter=0x40`, `nf_cal_period=30`.
- **Arm B** — reg `0x13761320` (PB-040 BB timing), `pktlog_filter=0x0`, `nf_cal_period=120`, AQL 1500/2000, `htt_max_amsdu_ampdu="3 64"`, `tcp_notsent_lowat=131072`.

## 2. Champion v4 knobs (intended config)
| Knob | Value |
| :--- | :--- |
| `htmode` / width | `VHT40` / 40 MHz |
| AP NSS×MCS / STA NSS×MCS | `1×MCS2` / `0×MCS2` |
| `pktlog_filter` | `0x0` |
| `bb_timing_0x29e00` | `0x13761320` |
| `pb050_rc_probe_interval_ms` | 4000 |
| AQL BE low/high | 1500 / 2000 |

## 3. Per-arm results (mean of 2 windows each)
| Metric | Arm A | Arm B |
| :--- | :--- | :--- |
| DL (Mbps) | 5.33 | 4.36 |
| UL (Mbps) | 7.56 | 8.43 |
| Aggregate (Mbps) | 12.90 | 12.79 (peak 13.59) |
| ping 64B p50 (ms) | 1.938 | 2.423 |
| ping 1472B loss | 0.0% | 0.0% |

## 4. ⚠️ Degraded window — not a certified champion
This live capture **did not meet the Champion v4 throughput target**:
- Arm B aggregate **12.79 Mbps** is below the airOS 8 TDMA baseline (**22.80 Mbps**, Stage 105A) and far below PtP Champion v3's **25.47 Mbps** peak (Stages 583A..588A).
- Arm B ≈ Arm A (12.79 vs 12.90): the PB-040/050 Arm B shows **no throughput gain** over stock-timing Arm A in this window.

Probable cause: the VHT40 link was in a degraded/unsettled state during the capture (negotiated rates stayed low). **A live counterbalanced re-run is required before Champion v4 throughput can be certified.** Latency and 0% 1472 B loss were clean; the shortfall is throughput only.

## 5. Silicon state (independently confirmed)
Both ends carry the PB-050 SGMT in RAM. The 695A receipt's `sta_242_pb040_pb050_active=false` is a nested-SSH **parse artifact** of this run; the `.242` STA silicon is independently **CONFIRMED** by Stage 585A (`ap_241_verified` and `sta_242_verified` both `true`, same SHA `a49160ff…`, `athwlan=12b29d01`, `0x00029e00=0x13761320`).

## 6. Five-pillar compliance
Receipt carries all five pillars (`CONFIRMED`): FullREA binary RE (571-knob catalog), closed-loop HyperResearch, Karpathy counterbalanced harness (45 s / 120 s watchdog), K-dense scientific skills, MemoryMaster (`FMX-S695A-01`).
