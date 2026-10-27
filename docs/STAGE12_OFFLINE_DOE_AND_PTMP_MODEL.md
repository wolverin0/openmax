<!-- doc-head: Offline DOE, pymoo proposals and bounded SimPy model methodology -->
Frozen13 single-link treatment windows calibrate exploratory models, not causal wireless gains.
DOE and NSGA-II/III remain disconnected from every device and mutable bench policy.
SimPy emits384 scenarios/1152replications with explicit vendor/RTS/TXOP assumptions.
Held-out tail errors and unmodeled controls are retained; no physical prediction acceptance.
<!-- /doc-head -->

# Stage12 — offline DOE, surrogate and PtMP model

Waves B/C implement reproducible numerical studies using the real saved R1/R2 measurements as reported inputs. They neither reacquire data nor execute a radio/bench command. R1 contains8 treatment windows and R2 contains5, each with2 receiver repetitions and6 RTT samples. The original master summaries disagree with several values; the [frozen manifest](../artifacts/autoresearch/waves_abcd_20261024/inputs_manifest.json) and [causal audit](STAGE12_AUTORESEARCH_STATISTICAL_AND_CAUSAL_AUDIT.md) preserve that distinction.

Runtime versions: Python3.12.4, NumPy1.26.4, SciPy1.17.1, pymoo0.6.2 and SimPy4.1.2. [Environment provenance](../artifacts/autoresearch/waves_abcd_20261024/environment.json) records the actual host metadata. Libraries were initially unavailable; the failed offline cache-resolution attempt and blocked-state tests remain history. Native optimizations and simulations subsequently ran with the actual locally available libraries, without a substitute engine or an online install by this task.

## DOE and coverage

[Optimizer source](../orchestration/autoresearch/fmx_doe_and_pymoo_optimizer.py) inventories every original248 catalog entry and the expanded571-entry catalog. Excluded controls remain excluded; controls without empirical responses remain unmodeled. Static extraction does not supply a response coefficient or a physically approved range.

The measured model uses six factors: coupled AQL low/high/threshold, raw CT7 threshold, CT10 RIFS, FQ quantum, HTT A-MSDU and HTT A-MPDU. They map to eight stored fields and six catalog identities. CT7 is a raw firmware threshold, not a proved normalized percentage. In particular CT6 is MAX_TXPOWER and never substituted for Dynamic BW RTS.

The finite model grid contains360 combinations. Model bounds are not device-safe RAM ranges. AQL levels map to high=2low and threshold=4low except the observed stock5000/12000/24000 package. Thus the study cannot estimate isolated low/high/threshold effects. Some proposed levels/combinations are interpolations not observed treatments; distance to training and missing physical qualification remain explicit.

The regular half fraction has32 rows and defining relation I=product(all6 coded factors), resolutionVI. Endpoint coding and all main/two-way aliases are reported; no claim of estimating all571 effects is made. The seeded greedy D-design selects14 unique runs with main-effect matrix rank7, randomized order and determinant history. It is a D-optimal approximation over the stated finite set, not a global optimality certificate. No independent physical repetitions are implied by rows in either design.

## Surrogate and NSGA-II/III

The RBF ridge surrogate uses fixed engineering feature scales, length-scale0.5, ridge0.1 and a round nuisance axis. Round means are learned inside each training fold and residuals are modeled around them. The entire policy tuple is excluded across both rounds for each held-out assessment. It is not a chronological holdout, a randomization scheme or a resolution of the round/environment confounder.

The initial zero-centered model performed poorly and is preserved in the independent review. Centering prevents unobserved settings from shrinking toward fictitious zero throughput/latency. Final leave-policy-out RMSE is approximately9.06 Mbps,8.96 ms p95 and9.50 ms p99; corresponding round-mean baseline errors are10.73 Mbps,9.48 ms and10.05 ms. This small retrospective advantage is not independent physical validation or calibrated uncertainty coverage.

Both native pymoo algorithms optimize negative goodput/100, p95/20 and p99/20, with integer level indices, rounding repair, population32,20 generations and seed20261024. A normalized feature-distance constraint≤0.75 limits unsupported model extrapolation. NSGA-III uses declared reference directions. Results are rechecked for integer validity, finite predictions, model support and nondominance; no least-infeasible solution is called feasible. Model feasibility does not imply hardware feasibility. The resulting frontier is an approximation, without global optimality or gain claims.

[Candidate batches](../artifacts/autoresearch/waves_abcd_20261024/doe_pymoo_candidate_batches_20261024.json) preserve designs, original/expanded catalog dispositions, source hashes, software versions, validation errors and both algorithm outputs. Every proposal has `automatic_execution_allowed=false` and `physical_safety_qualified=false`. No shell commands or actuator integration is generated.

## SimPy conceptual model

[Simulator source](../tools/sim/fmx_simpy_ptmp_aql_rc_sim.py) uses native SimPy processes for arrivals and a single shared round-robin airtime server. Pending airtime includes the in-flight packet. Admission uses per-CPE high/low limits and a global threshold; finite queue/admission rejection is explicit. TXOP controls a soft batch duration ending after a packet completes. Packets, simulated time and processed events all have fixed caps; an exceeded cap raises an error, never a completed result.

Per-round local interpolation of the saved eight-field policies supplies phenomenological capacity and an unexplained latency component. RC changes that calibrated response; it does not emulate the proprietary firmware's MCS state machine or establish an isolated RC effect. RIFS is fixed0 in scenario queries and retained as a distance feature in the input policies. R1 and R2 are separate contexts; their throughput drift is not averaged away.

The following are **scenario assumptions**, not measured vendor/RF coefficients:

- WA/XC service efficiency1 and SXT/LBM5 efficiency0.5. No multivendor loaded curves calibrated these values.
- Collision probability0.1 and conceptual RTS collision multiplier0.5. There are no hidden-node traces or measured DynamicBW/RTS treatment effects here.
- WMM TXOP is a conceptual batch duration0/1500/4000 µs, with no claim that a specific hardware/driver setter produces it.
- Open-loop offered load120 Mbps,1500-byte packets,0.5 s horizon and0.1 s warm-up. TCP feedback, exact offered-load traces, management traffic, RF topology and PHY/MCS transitions are absent.

The model therefore tests sensitivity of a declared queue system. It does not simulate the complete airMAX scheduler or establish that this hardware can implement an optimized PtMP MAC.

## Prediction dataset and diagnostics

[Predictions](../artifacts/autoresearch/simpy_ptmp_predictions_20261024.json) cover2 round contexts×16 CPE counts×3 AQL profiles×4 RC/RTS/TXOP profiles=384 scenarios, each with3 independent stochastic replications. Vendor classes cycle WA/XC/SXT/LBM5 as CPE count grows. Replication seed is20261024+1009i; arrival and collision streams use separate offsets. Common seeds across scenarios support numerical comparison, not independent physical replication.

Throughput counts departures in [warmup,horizon); RTT uses admitted post-warmup arrivals completed before the horizon plus the phenomenological delay. Incomplete packets remain explicit. `window_counts` is a flow summary with entry/departure windows, not a conserved cohort; only the complete-run conservation identity includes all rejected, delivered, collision-lost and unfinished packets. Completed latency is censored at the horizon. The three-replication Student-t intervals quantify Monte Carlo variation conditional on the model, excluding model/parameter/transport uncertainty.

The [native curve comparison](../artifacts/autoresearch/waves_abcd_20261024/simpy_curve_comparison.json) includes six compatible measured treatments, each evaluated in-sample and with the whole policy held out across rounds; seven other treatments have unmodeled RIFS/FQ/HTT states and are explicitly excluded from matched comparisons. In-sample RMSE is4.48 Mbps/6.91 ms/7.87 ms; held-out RMSE is8.97 Mbps/14.88 ms/15.92 ms for goodput/p95/p99. These errors and the mismatch between six measured ping RTTs and simulated packet completion latency prevent a physical accuracy claim. No acceptance threshold was invented after observing these errors.

## Reproduction and verification

From the repository root, with the recorded local libraries available:

```powershell
python -B -m orchestration.autoresearch.fmx_doe_and_pymoo_optimizer
python -B -m tools.sim.fmx_simpy_ptmp_aql_rc_sim
python -B artifacts/autoresearch/waves_abcd_20261024/validate_simpy_curves.py
python -B -m analysis.statistics.fmx_autoresearch_statistical_audit --write-report
```

Generated outputs are fenced to owned wave artifacts and the named simulator dataset. Frozen inputs, original live receipts, device names/ADS and external destinations are rejected. The unit suites check DOE rank/aliases, leakage, numerical bounds, native optimization reproducibility/nondominance, native simulation conservation/caps/seed reproducibility and statistical formulas. Independent reviews preserve earlier failures and later repairs. These are software/numerical verification, not physical experiment acceptance.

The local experimental-design, pymoo, hypothesis-generation, SimPy, statistical-analysis/power and aeon skills informed these boundaries. Aeon fitting is not justified by six sparse pings; no unsupported time-series classifier was added. The locally declared Scientific Agent Skills reference is recorded in the statistical report without an online bibliography lookup.
