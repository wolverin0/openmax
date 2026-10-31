<!-- doc-head: Stage 869A offline NSGA-III + SimPy complete Guarida 34-endpoint Triple-Play Pareto v12; per-sector DWRR/AQL + airtime-fairness strength, knee SimPy-validated -->
# Stage 869A — Guarida 34-Endpoint Complete Triple-Play Pareto v12

- **Claim Status**: `CONFIRMED` (offline model)
- **Attribution**: `external controller (offline model)` — no radio, no SSH
- **Artifact**: `artifacts/autoresearch/stage869a_guarida_34endpoint_pareto_v12.json`
- **Tool**: `tools/sim/run_stage869a_guarida_34endpoint_pareto_v12.py`

## 1. Topology (34 endpoints)
Panel1 (3 CPE) + Panel2 (22 CPE) + Panel3 (6 CPE) + 3 panel-AP backhauls = **34
endpoints**, each tagged class (ac/n), sector load, and distance. Endpoints
alternate 802.11ac / 802.11n to model the mixed-vendor reality.

## 2. Optimization
- **Algorithm**: pymoo **NSGA-III**, Das-Dennis ref dirs `(3 obj, 12 partitions)`, 150 gens, `seed=12`.
- **Decision vector (7)**: per-sector DWRR weight (×3) + per-sector AQL high-water µs (×3) + a global **airtime-fairness strength** `[0,1]`.
- **Objectives**: minimize mean VoIP latency, maximize aggregate goodput, maximize Jain fairness across endpoints.
- **Goodput model (faithful to Stage 839A)**: per endpoint, `fairness=0` = equal
  frames (equal bytes, low aggregate, slow endpoints hog airtime); `fairness=1` =
  equal airtime (fast endpoints carry more, higher aggregate, lower goodput-Jain).

## 3. Results
- **Pareto front**: 68 non-dominated points; hypervolume 1112.28.
- **Knee** (augmented-Tchebycheff ASF): airtime-fairness strength **0.684**,
  mean VoIP latency 2.14 ms, aggregate-goodput objective 492.9 (model units),
  Jain fairness 0.744.
- **SimPy validation** of the knee's fairness strength: realized airtime-Jain
  **0.9992** (airtime equalized), realized aggregate 199.2 Mbps over a 1 s sim.

## 4. Reading the knee
The optimizer lands on an **intermediate** fairness strength (~0.68), not the
extremes: pushing to full airtime fairness maximizes aggregate but erodes
per-endpoint goodput-Jain, while legacy equal-frames equalizes bytes at a large
aggregate cost. ~0.68 is the Pareto-balanced operating point for the 34-endpoint
tree. This is consistent with Stage 839A (airtime fairness raises aggregate) while
exposing the fairness-vs-equality tension the single-sector study did not.

## 5. Reproduce & limits
```sh
python tools/sim/run_stage869a_guarida_34endpoint_pareto_v12.py
python -m pytest tests/test_stage869a.py -q
```
Model, not measurement: aggregate-goodput is an airtime-capacity objective in model
units (not a certified Mbps per sector); latency/fairness encode knob *directions*
calibrated to recorded order-of-magnitude. Use the front to shortlist per-sector
knob sets for a live counterbalanced A/B, not to set production values blind.
