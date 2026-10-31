<!-- doc-head: Stage 977A offline Sidak x sign-flip permutation power curves and MDE per n in {6,8,12,16}; at family size 500 MDE is unreachable for n<=12 (audit A07) and 2.0 SD at n=16 -->
# Stage 977A - Sidak x Permutation Power Curve and MDE Calculator

Evidence class: `SIMULATED_MODEL_ONLY`. 100% offline; no radios, SSH or firmware touched.

## Method
- Paired deltas ~ Normal(mean=d, sd=1), n blocks in {6, 8, 12, 16}; d in 0.0..3.0 step 0.25.
- 400 Monte Carlo trials per (n, d) cell, seed 20261027 (numpy default_rng).
- Test: two-sided sign-flip permutation test; reject if `p <= compute_adjusted_alpha(0.05, m)`.
- Single-step Sidak from `analysis.regression_gate.gatekeeper.compute_adjusted_alpha`.
- MDE(n) = smallest grid d with power >= 0.80; `None` = unreachable within d <= 3.0 SD.

## Implementation note (deviation from brief)
`paired_sign_flip_p_value` enumerates exactly for n <= 16 (`max_exact_blocks=16`) and ignores
`n_permutations` there, so 65536 permutations is the exact 2^16 enumeration for n=16 and
the resolution floor is `2/2^n` for every n in the set (not `1/(perm+1)`). Running the
gatekeeper in pure Python per trial is too slow, so the script uses a vectorised exact
enumeration with the same rule; it is cross-checked against the gatekeeper on 12 samples
(max abs difference 0.0).

## Results: MDE (per-block SD units)
| n | min_p (2/2^n) | m=1 (alpha 0.05) | m=500 (alpha 1.026e-4) |
|---|---------------|------------------|------------------------|
| 6 | 3.125e-02 | 2.0 | None (min_p > alpha) |
| 8 | 7.812e-03 | 1.25 | None (min_p > alpha) |
| 12 | 4.883e-04 | 1.0 | None (min_p > alpha) |
| 16 | 3.052e-05 | 1.0 | 2.0 |

## Findings
- At m=500 the adjusted alpha (~1.03e-4) is below the resolution floor for n=6, 8 and 12:
  rejection is mathematically impossible, power is exactly 0 at every d. This is audit A07.
- At n=16 the floor (3.05e-5) is just under alpha, so rejection is possible but needs an
  effect of about 2 SD (power 0.78 at 1.75, 0.93 at 2.0 on the grid; MDE grid value 2.0).
- Even at m=1, n=6 needs ~2 SD; n=12 and n=16 detect ~1 SD.
- d=0.0 rows give the empirical type-I rate (about 0.03-0.06 at m=1, 0.00 at m=500).
- Grid resolution is 0.25 SD and MC error at 400 trials is about +/-0.025 near power 0.8,
  so MDE values are grid upper bounds, not interpolated estimates.

## Artifacts
- `tools/sim/run_stage977a_sidak_permutation_power_curve_and_mde_calculator.py`
- `artifacts/autoresearch/stage977a_sidak_permutation_power_curve_and_mde_calculator.json`
- `tests/test_stage977a.py`

MemoryMaster claim: `FMX-STAGE977A-MDE-POWER-CURVE`.
