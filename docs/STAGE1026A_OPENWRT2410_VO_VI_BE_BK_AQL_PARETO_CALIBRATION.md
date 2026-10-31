<!-- doc-head: Stage 1026A offline NSGA-II exploration of per-AC AQL txq limits (VO/VI/BE/BK) under a deterministic airtime-queue model; SIMULATED_MODEL_ONLY, OpenWrt 24.10 and mac80211 stock are reference points, certifies nothing on hardware -->
<!-- /doc-head -->
# Stage 1026A: OpenWrt 24.10 VO/VI/BE/BK AQL Pareto exploration

Evidence class: `SIMULATED_MODEL_ONLY`.

This is a model exploration; it certifies nothing on hardware.

## What it is

A pymoo 0.6.2 NSGA-II run over the eight per-AC AQL txq limits
`[VO_low, VO_high, VI_low, VI_high, BE_low, BE_high, BK_low, BK_high]`,
each integer in 0..12000, with the constraint `low < high` per AC.
The objectives come from a closed-form deterministic airtime-queue model.
There is no device, no SSH and no ground truth. The GA does not find or certify real limits.

## Reference points (reported, not discovered)

- OpenWrt 24.10 captured: `[300,600,1000,2000,1500,3000,500,1000]`
- mac80211 stock: `[5000,12000]` on every AC

Both are evaluated with the same objective function as the GA population.
For each, the run reports whether a front point dominates it and its
normalised Euclidean distance to the nearest front point.
The front position of a reference is a statement about the model only.

## Model

Per AC, `E = 0.4*low + 0.6*high` is the standing queue airtime in microseconds.
`fill = 1-exp(-E/tau)` is the aggregation fill, with tau 300/800/2500/2500 us for VO/VI/BE/BK.
`S = 1500*exp(-E/600)` is the service inflation of an under-filled queue.
Offered airtime load `rho` is 0.05/0.25/0.55/0.20 for VO/VI/BE/BK (illustrative, unmeasured).
Hardware-queue airtime of other ACs is capped at 4000 us.

Objectives (all minimised):

1. `vo_p99_latency_ms = (E_vo + S_vo + 0.25*sum_{j!=vo} min(E_j,4000))/1000 * (1+ln(100)*rho_vo)`
2. `vi_p99_latency_ms = (E_vi + S_vi + 0.25*(min(E_be,4000)+min(E_bk,4000)) + 0.5*min(E_vo,4000))/1000 * (1+ln(100)*rho_vi)`
3. `be_goodput_neg = -min(rho_be, max(0, 1 - sum_{a in VO,VI,BK} rho_a*fill_a)) * fill_be`
4. `vi_jitter_ms = (high_vi-low_vi)/sqrt(12)/1000`

The latency terms reward small queues, while `S` and `fill` punish queues that are too small.
That tension is what produces a front. The constants are assumptions, not fitted values.

## Public API

`calibrate(seed=0, pop_size=24, n_gen=20) -> dict`, implemented in
`tools/sim/run_stage1026a_openwrt2410_vo_vi_be_bk_aql_pareto_Calibration.py`.
The Stage 1030A gate calls this exact signature.

Returned keys:

- `reference`
- `stock_reference`
- `pareto_front`: a list of `{x:[8 ints], f:[4 objective values]}`
- `reference_dominated`
- `reference_distance_to_front`
- `n_evaluations`
- `objectives`
- `model_provenance`

Extra keys carry the stock-reference metrics, the reference objective values, and the run parameters.
A fixed seed gives an identical front.

## Run

- Self-test and receipt, small run (pop 24, gen 20): `python tools/sim/run_stage1026a_openwrt2410_vo_vi_be_bk_aql_pareto_Calibration.py`
- Larger run (pop 80, gen 120): add `--full`
- Tests: `python -m pytest tools/sim/test_run_stage1026a_openwrt2410_vo_vi_be_bk_aql_pareto_Calibration.py -q`

## Receipt

`artifacts/autoresearch/stage1026a_openwrt2410_vo_vi_be_bk_aql_pareto_calibration.json`

- `status` is `CONFIRMED` and `live_devices_touched` is `false`.
- The stored front is capped at the first 40 points.
- The receipt writer reads the file back and rejects an all-NUL file or one that does not parse with `stage == "Stage 1026A"`. It retries 3 times, then raises.
- The memory claim id is `FMX-STAGE1026A-AQL-NSGA2-PARETO-CALIBRATION`. It is not ingested by this stage.

## Limits

- The front depends entirely on the assumed constants above. Changing them moves the front.
- Real AQL behaviour on the radio is not modelled. Validation needs a separate, gated on-device stage.
