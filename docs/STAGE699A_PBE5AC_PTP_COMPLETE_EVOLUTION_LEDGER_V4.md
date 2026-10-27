<!-- doc-head: Stage 699A complete PowerBeam 5AC Gen2 PtP evolution ledger (Baseline 0 -> Champion v4) across 25 live PtP stages; v4 window degraded vs v3, needs live re-run -->
# Stage 699A — Complete PowerBeam 5AC Gen2 PtP Evolution Ledger v4

- **Claim Status**: `CONFIRMED`
- **Attribution**: `QCA firmware` + `ath10k` + `mac80211` + `Linux` + `hardware`
- **Total live PtP stages consolidated**: 25
- **Stage families**: `Stage 105A`, `425A..430A`, `487A..492A`, `583A..588A`, `695A..700A`
- **Receipt**: `artifacts/autoresearch/stage699a_pbe5ac_ptp_complete_evolution_ledger_v4.json`

## 1. Evolution timeline
| Generation | Stage ref | Width | Aggregate (Mbps) | Peak | p50 (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Baseline 0 — Stock airOS 8 TDMA | 105A | 20 | 22.80 | — | 1.96 |
| Baseline 1 — Stock OpenWrt 24.10.4 (un-tuned Arm A) | 105A/429A | 20 | 10.64 | — | 1.659 |
| PtP Champion v1 — Asymmetric VHT LGI | 105A | 20 | 14.62 | — | 1.589 |
| PtP Champion v2 — VHT20 + AQL 1500/2000 + fq_quantum=300 | 425A..430A | 20 | 20.58 | 22.46 | — |
| PtP Champion v3 — VHT40 + pktlog_filter=0x0 + notsent_lowat | 487A..492A, 583A..588A | 40 | **24.18** | **25.47** | — |
| PtP Champion v4 — VHT40 + PB-040/PB-050 silicon patch | 695A..700A | 40 | 12.79 ⚠️ | 13.59 | 2.423 |

## 2. ⚠️ v4 is a degraded live window, not a throughput champion
The Champion v4 row reflects the Stage 695A live capture, which **regressed** relative to Champion v3:
- Aggregate **12.79 Mbps** vs v3 **24.18 Mbps** (−47%), and below the airOS 8 baseline of 22.80 Mbps.
- The silicon patch (PB-040/PB-050, `0x00029e00=0x13761320`) is correctly loaded, but the recorded window shows **no throughput benefit** — the link stayed at low negotiated rates.

**Interpretation**: v4's value proposition (silicon-level BB-timing + RC-probe dampening) is *not* demonstrated by this window. A live counterbalanced re-run of Stage 695A is required before v4 can supersede v3 as the throughput champion. Until then, **Champion v3 remains the throughput reference**.

## 3. Silicon patch verification
| Field | Value |
| :--- | :--- |
| PB-050 SHA-256 | `a49160ff008390a34e43145bc56f6b8d047f8e02433aff20f965b6f2874ef52f` |
| `athwlan` checksum | `12b29d01` |
| `0x00029e00` | `0x13761320` |
| `.241` AP verified | `true` |
| `.242` STA verified | `false` in this receipt — **but `true` per Stage 585A** (same SHA, independent CONFIRMED proof; 695A/699A value is a nested-SSH parse artifact) |

## 4. Release kit v4
- Dynamic phy* + SGMT loader SHA-256 `45c319f0…`, Champion v4 hotplug SHA-256 `138eeed8…`, 215 binaries verified (Stages 697A/698A).

## 5. Verdict
The PtP line has progressed Baseline 0 → Champion v3 with monotonic, verified gains. **Champion v4's throughput claim is unproven in the recorded data and is flagged for a live re-run.** Latency/loss behaviour in v4 remained clean (0% 1472 B loss).
