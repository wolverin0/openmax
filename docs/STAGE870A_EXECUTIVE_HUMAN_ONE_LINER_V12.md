<!-- doc-head: Stage 870A offline executive human one-liner per milestone v12; one plain-language line + single multiplier/percentage each, distilled from offline receipts -->
# Stage 870A — Executive Human One-Liner per Milestone v12

- **Claim Status**: `CONFIRMED` (offline summary)
- **Attribution**: `external controller (offline summary)` — no radio, no SSH
- **Artifact**: `artifacts/autoresearch/stage870a_executive_human_one_liner_v12.json`
- **Tool**: `tools/observability/build_stage870a_executive_human_one_liner_v12.py`

## 1. Purpose
The 10-second executive read: exactly one plain-language line per milestone, each
carrying a single headline multiplier or percentage. Pure arithmetic over the
existing offline receipts — introduces no new measurement.

## 2. One-liners (v12)
1. **PtP Champion v3 delivers 2.27× the untuned-OpenWrt baseline** (24.18 vs 10.64 Mbps).
2. **PtP Champion v4's recorded window is DEGRADED** (12.79 vs 24.18 Mbps) and needs
   a live re-run — v3 stays the reference.
3. **Airtime fairness lifts mixed ac/n sector aggregate by +18.55 %** and equalizes
   airtime (Jain ~1.0).
4. **The airtime-fairness gain is statistically real** (Wilcoxon p = 0.0078, 95 % CI
   excludes zero).
5. **Under system stress VHT40 holds 10 km vs VHT80's 6 km** — the +3 dB noise
   penalty costs 4 km of range.
6. **The Guarida 34-endpoint optimum sits at airtime-fairness 0.684** (balanced),
   SimPy-validated to Jain 0.9992.

## 3. Sources
699A ledger · 837A fade model · 838A/869A Pareto · 839A airtime fairness ·
841A statistical confidence ledger. Each line's `metric`/`value` is machine-readable
in the artifact's `milestones[]`.

## 4. Reproduce & limits
```sh
python tools/observability/build_stage870a_executive_human_one_liner_v12.py
python -m pytest tests/test_stage870a.py -q
```
The degraded-window and offline-model caveats of the upstream stages carry through;
line 2 deliberately keeps the v4 shortfall visible rather than rounding it away.
