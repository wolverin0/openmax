<!-- doc-head: Stage 840A offline WISP executive KPI dashboard summary; multipliers & percentages distilled from the 699A ledger + 837A/838A/839A offline sims -->
<!-- /doc-head -->
# Stage 840A — WISP Executive KPI Dashboard Summary

- **Claim Status**: `CONFIRMED` (offline summary)
- **Attribution**: `external controller (offline summary)` — no radio, no SSH
- **Artifact**: `artifacts/autoresearch/stage840a_wisp_executive_kpi_dashboard_summary.json`
- **Tool**: `tools/observability/build_stage840a_wisp_executive_kpi_dashboard_summary.py`
- **Sources**: 699A ledger · 837A fade model · 838A Pareto · 839A airtime fairness

## 1. Headline KPIs
- **PtP Champion v3 = 2.27× untuned OpenWrt** (24.18 vs 10.64 Mbps aggregate).
- **Airtime fairness = +18.55 % aggregate** in mixed ac/n sectors (offline model).
- **VHT40 extends stressed-link range to 10 km** vs VHT80's 6 km.

## 2. PtP throughput evolution
| Generation | Aggregate (Mbps) | Note |
| :--- | :--- | :--- |
| Baseline — stock airOS 8 TDMA | 22.80 | reference |
| Baseline — untuned OpenWrt | 10.64 | floor |
| **PtP Champion v3** | **24.18** | 2.27× untuned, +6.05 % vs airOS 8 |
| PtP Champion v4 (695A window) | 12.79 | ⚠️ `DEGRADED_WINDOW_NEEDS_LIVE_RERUN` |

v4's recorded window underperformed v3; the dashboard flags it rather than
reporting it as a champion. **v3 remains the throughput reference.**

## 3. Range / width planning (837A)
- Nominal (well-aligned): both widths stable to 15 km.
- Stressed: VHT40 stable to 10 km, VHT80 to 6 km (VHT80 +3.01 dB noise penalty).
- Rule: **VHT80 for short/clean hops; VHT40 to extend range or under margin uncertainty.**

## 4. Triple-Play knee (838A) & fairness (839A)
- NSGA-III Pareto front of 23 points; knee balances VoIP latency/jitter against
  IPTV/bulk goodput under the Safe-Envelope constraint.
- Airtime fairness recovers +13–22 % aggregate (mean +18.55 %) and equalizes
  airtime (Jain ≈ 1.0) vs legacy equal-TXOP.

## 5. Reproduce & limits
```sh
python tools/observability/build_stage840a_wisp_executive_kpi_dashboard_summary.py
python -m pytest tests/test_stage840a.py -q
```
This is arithmetic over existing receipts — it introduces no new measurement. The
offline-model KPIs (range, fairness, Pareto) carry their own model caveats from
Stages 837A–839A; the live KPIs inherit the 695A degraded-window caveat.
