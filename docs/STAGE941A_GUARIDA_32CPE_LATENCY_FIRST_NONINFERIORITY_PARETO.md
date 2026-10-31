<!-- doc-head: Stage 941A offline NSGA-III Pareto of AQL/DWRR knobs over the Guarida panels (latency-first, capacity non-inferior); SIMULATED_MODEL_ONLY, knee gatekeeper verdict INCONCLUSIVE -->
# Stage 941A - Guarida 32-CPE Latency-First Non-Inferiority Pareto

Evidence class: `SIMULATED_MODEL_ONLY`. Attribution: external controller (offline model).
No radio, SSH or firmware was touched (`live_devices_touched: false`).

## What it does
`tools/sim/run_stage941a_guarida_32cpe_latency_first_noninferiority_pareto.py` runs pymoo
NSGA-III (seed 42, das-dennis 48 partitions, pop 52, 120 generations) over three normalised
knobs: AQL limit, DWRR quantum, airtime weight. Objectives, relative to the baseline knob set
(aql 0.80, quantum 0.50, airtime 0.50): minimise load-weighted p99 ratio, maximise
load-weighted goodput/MHz ratio.

## Panels
| Panel | CPEs | Load | Load weight |
| :--- | ---: | ---: | ---: |
| Panel1 | 3 | 0.6 | 0.063 |
| Panel2 | 22 | 1.0 | 0.769 |
| Panel3 | 6 | 0.8 | 0.168 |

Data discrepancy: the requested split (3 + 22 + 6) sums to 31, not 32. The receipt records
`cpe_count_declared: 32`, `cpe_count_by_panel_sum: 31`, `cpe_count_discrepancy: 1`. The model
uses the 31 attributed CPEs; no panel was invented for the missing one.

## Surrogate (documented, not fitted)
- p99: a larger AQL limit raises queueing delay (bufferbloat), a larger DWRR quantum adds
  head-of-line delay, a heavier airtime weight trims the tail.
- goodput/MHz: a tight AQL limit starves A-MPDU aggregation (quadratic loss), a quantum far
  from 0.5 and an airtime weight far from 0.6 cost efficiency.
- Each panel scales both effects by its own `lat_sens` / `cap_sens`; the aggregate is the
  load-weighted mean of per-panel ratios. Constants are modelling assumptions.

## Result (seed 42)
- Pareto front size: 49. Hypervolume: 1.1502 (ref point [1.5, 0.0] on [p99_ratio, -gpm_ratio]).
- Points that improve p99 by >=5% with goodput/MHz loss <=2% (the gatekeeper defaults): 2 of 49.
  - aql 0.699, quantum 0.444, airtime 0.661: p99 x0.861, goodput/MHz x0.983
  - aql 0.753, quantum 0.425, airtime 0.676: p99 x0.896, goodput/MHz x0.991
- Knee (taken over those latency-first, non-inferior points): the first one above.
  Per panel p99 ratio: P1 0.873, P2 0.859, P3 0.865.

## Gatekeeper check
`RegressionGatekeeper(objective="LATENCY_WITH_CAPACITY_NONINFERIORITY")`, `evaluate_paired`
on 6 synthetic paired A/B blocks (width 40 MHz, seeded noise 3% p99 / 1.5% goodput,
evidence_state SYNTHETIC):
- Verdict: **INCONCLUSIVE** - "Capacity non-inferiority interval not established".
- Mean p99 delta -14.5%, goodput delta -1.0%. The lower bootstrap bound of the goodput/MHz
  delta falls below the -2% non-inferiority margin, so the gate withholds a verdict.
- Recorded as returned. It was not forced to a pass; even a pass on SYNTHETIC evidence would
  be `SYNTHETIC_PASS`, never physical evidence.

## Limits
- Synthetic surrogate, not measured Guarida data; ratios are model outputs, not predictions.
- The A/B blocks are generated from the same surrogate, so they test the gate's behaviour on
  the modelled effect, not the effect itself.
- Any real use needs a bench campaign with real paired blocks and the standard holdout gate.

## Reproduce
`python tools/sim/run_stage941a_guarida_32cpe_latency_first_noninferiority_pareto.py`
then `python -m pytest tests/test_stage941a.py -q`.
Receipt: `artifacts/autoresearch/stage941a_guarida_32cpe_latency_first_noninferiority_pareto.json`
(claim `FMX-STAGE941A-GUARIDA-NONINFERIORITY`).
