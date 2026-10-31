<!-- doc-head: Stage 965A offline SimPy model of airtime-deficit RR vs equal-TXOP for mixed 802.11ac + n/M5 CPEs, Guarida Panel2 (22) and Panel3 (6); evidence SIMULATED_MODEL_ONLY; gatekeeper REJECT on p99 -->
# Stage 965A - Airtime-Deficit RR, Mixed ac + n/M5 (Guarida)

Evidence class: SIMULATED_MODEL_ONLY. Live devices touched: false. No radio, SSH or firmware.

## Model
- SimPy saturated shared medium, deterministic (seed 20261027).
- Rates: ac 300 Mbps (VHT40 2SS), n/M5 65 Mbps (1SS), 1500 B frames, per-frame overhead 60 us scaled by contention.
- Panel2: 22 CPE (14 ac + 8 n/M5). Panel3: 6 CPE (4 ac + 2 n/M5).
- Baseline: equal-TXOP DCF round-robin, one frame per turn (802.11 performance anomaly).
- Candidate: airtime-deficit RR, 2 ms airtime quantum per round, deficit counter carried over.
- Analytic closed form cross-checks the SimPy aggregate (within 0.3%).

## Results (nominal rates)
| Panel | Policy | Aggregate Mbps | ac mean | n mean | Jain airtime | Jain tput |
|---|---|---|---|---|---|---|
| Panel2 | equal-TXOP | 67.51 | 3.07 | 3.07 | 0.8676 | 1.0 |
| Panel2 | airtime DRR | 77.35 | 4.38 | 2.00 | 0.9999 | 0.9037 |
| Panel3 | equal-TXOP | 77.82 | 12.97 | 12.97 | 0.8367 | 1.0 |
| Panel3 | airtime DRR | 91.49 | 18.90 | 7.94 | 1.0 | 0.8971 |

Aggregate gain: +14.6% (Panel2), +17.6% (Panel3). Airtime fairness improves; per-station
throughput equality (Jain tput) falls by design, and n/M5 CPEs lose throughput.

## Gatekeeper (RegressionGatekeeper.evaluate_paired)
6 seeded synthetic paired A/B blocks per panel, width 40 MHz, evidence_state SYNTHETIC,
jain_fairness = airtime Jain, per-block PHY jitter +/-8%.

| Panel | Verdict | Rationale | goodput delta | p99 delta |
|---|---|---|---|---|
| Panel2 | REJECT | Bufferbloat p99 regression | +14.7% | +1030% |
| Panel3 | REJECT | Bufferbloat p99 regression | +18.0% | +1149% |

Verdict recorded as returned. The latency proxy is the per-station service inter-gap; with a
2 ms quantum the DRR round length grows with CPE count (about 44 ms at 22 CPE vs 3.8 ms).
SYNTHETIC evidence could not be promoted by the gate in any case.

## Interpretation and limits
- Gain in aggregate and airtime fairness is real in the model; the cost is round-trip service
  latency and slower n/M5 clients. A smaller quantum (e.g. 0.3-0.5 ms) is the obvious next
  offline sweep; not run here.
- Model is saturated, lossless MAC with no retries, aggregation limits or rate adaptation.
- Not bench or field proof. Any live trial needs a separate gated stage.

## Artifacts
- tools/sim/run_stage965a_airtime_deficit_rr_mixed_ac_m5_guarida.py
- artifacts/autoresearch/stage965a_airtime_deficit_rr_mixed_ac_m5_guarida.json
- tests/test_stage965a.py
- MemoryMaster claim: FMX-STAGE965A-AIRTIME-DEFICIT-RR
