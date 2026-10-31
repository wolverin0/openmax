<!-- doc-head: Stage 838A offline pymoo NSGA-III optimization of per-AC AQL high-water + DWRR quantum weights for Triple-Play across the Guarida 3 sectors (32 CPE); Pareto front + knee -->
<!-- /doc-head -->
# Stage 838A — NSGA-III AQL + DWRR Triple-Play Pareto (Guarida 3 Sectors)

- **Claim Status**: `CONFIRMED` (offline model)
- **Attribution**: `external controller (offline model)` — no radio, no SSH
- **Artifact**: `artifacts/autoresearch/stage838a_pymoo_nsga3_guarida_32cpe_voip_iptv_bulk_pareto.json`
- **Tool**: `tools/sim/run_stage838a_pymoo_nsga3_guarida_32cpe_voip_iptv_bulk_pareto.py`

## 1. Problem
Optimize the per-AC queueing knobs of the Guarida PtMP sectors for Triple-Play.
- **Decision vector (8)**: AQL high-water for VO/VI/BE/BK (µs) + DWRR quantum weights for VO/VI/BE/BK.
- **Sectors (load-weighted)**: Panel1 (3 CPE, load 0.35), Panel2 (22 CPE, load 1.00), Panel3 (6 CPE, load 0.55).
- **Objectives (4)**: minimize VoIP latency, minimize VoIP jitter, maximize IPTV goodput, maximize bulk-TCP goodput.
- **Safe-Envelope constraint**: `aql_high_vo < aql_high_be` — voice buffering stays below bulk, bounding voice bufferbloat.

## 2. QoE surrogate
A documented analytic surrogate maps knobs→QoE per sector, anchored to recorded
live magnitudes (VoIP jitter ~1.6 ms, bulk ~14 Mbps, IPTV ~12 Mbps; Stages 79A/103D):
VoIP latency rises with VO buffer and falls with VO airtime share; IPTV goodput is
concave in VI buffer (starves if too small, bloats if too large); bulk goodput
saturates in BE buffer and BE share; a congestion factor `1/(1+0.45·load)` scales
goodput down as sector load rises.

## 3. Optimizer
- **Algorithm**: pymoo **NSGA-III**, Das-Dennis reference directions `(4 obj, 6 partitions)`.
- Population = number of reference directions; 120 generations; `seed=42` (deterministic).

## 4. Results
- **Pareto front**: 23 non-dominated points.
- **Hypervolume**: 373.40 (vs a dominated nadir+5 % reference point).
- **Knee point** (augmented-Tchebycheff ASF, equal weights):

| Knob | Value | | Objective | Value |
| :--- | :--- | :--- | :--- | :--- |
| `aql_high_vo` | 623 µs | | VoIP latency | 6.88 ms |
| `aql_high_vi` | 6041 µs | | VoIP jitter | 0.69 ms |
| `aql_high_be` | 11993 µs | | IPTV goodput | 5.23 Mbps |
| `aql_high_bk` | 3450 µs | | bulk goodput | 4.56 Mbps |
| DWRR VO/VI/BE/BK | 1.1 / 14.6 / 15.4 / 1.0 | | | |

## 5. Reading the knee
The compromise point keeps **VO buffering minimal** (623 µs, hard against the
Safe-Envelope floor) and pushes **BE buffering to the ceiling** (12 ms) for bulk
throughput, with DWRR weight concentrated on VI+BE. This is a *balanced* ASF point;
operators who weight voice first should pick a front point with higher `dwrr_vo`
(lower latency at the cost of bulk) — the full 23-point front is in the artifact.

## 6. Reproduce & limits
```sh
python tools/sim/run_stage838a_pymoo_nsga3_guarida_32cpe_voip_iptv_bulk_pareto.py
python -m pytest tests/test_stage838a.py -q
```
Model, not measurement: the surrogate encodes the *direction* of each knob's effect
calibrated to recorded magnitudes, not a validated per-sector throughput model.
Use the front to pick candidate knob sets for a live counterbalanced A/B, not to set
production values blind.
