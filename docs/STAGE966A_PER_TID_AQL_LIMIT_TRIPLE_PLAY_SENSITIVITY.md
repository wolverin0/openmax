<!-- doc-head: Stage 966A offline per-TID (VO/VI/BE/BK) AQL limit sensitivity for Triple-Play QoE plus synthetic A/A negative control; SIMULATED_MODEL_ONLY, no device touched -->
# Stage 966A - Per-TID AQL limit Triple-Play sensitivity

Status: CONFIRMED (offline). Evidence class: `SIMULATED_MODEL_ONLY`. Live devices touched: none.

## What it does
- Analytic queueing model of per-AC AQL high-water limits (KB of in-flight airtime-queue bytes).
- Grid: VO {4,8,12,24}, VI {8,16,24,48}, BE {12,24,48,96}, BK {6,12,24,48} = 256 configs.
- Baseline: VO 12, VI 24, BE 24, BK 12.
- Per config: VoIP p99 and jitter (64 B), IPTV jitter and loss (1316 B), TCP bulk goodput.
- Sensitivity two ways: one-at-a-time (% change per ln(limit) around baseline) and grid-marginal
  (range of per-level mean, % of baseline).

## Findings (model-relative, not absolute QoE)
- BE limit dominates VoIP p99/jitter, IPTV jitter and bulk goodput: low-priority in-flight bytes
  head-of-line block the higher ACs, while a small BE limit starves A-MPDU depth.
  This is a real latency vs throughput trade on a single knob.
- VI limit dominates IPTV loss (tail drop once the limit cannot hold a GOP burst, ~21 KB) and is
  second for IPTV jitter.
- BK has a modest effect on latency (18-30 %) and bulk goodput (~7 %).
- VO limit has the smallest effect (<10 % on VoIP p99); below ~8 KB it adds contention delay.
- IPTV loss marginal % is huge only because the baseline loss is near zero (0.04 %).

## A/A negative control
- Same config (baseline) on both arms, 6 seeded paired blocks, 4 % multiplicative noise,
  `RegressionGatekeeper.evaluate_paired` (objective CAPACITY_WITH_QOE_CONSTRAINTS, alpha 0.05).
- Verdict: REJECT (not PROMOTE / KEEP_FOR_REPLICATION / SYNTHETIC_PASS), so no win fabricated.
- 200 further seeded repeats: 2 wins (1.0 %), within alpha.

## Limits
- Coupling constants are assumptions; use only to rank sensitivities and to choose bench sweeps.
- No firmware change is proposed or authorised by this stage.

## Files
- `tools/sim/run_stage966a_per_tid_aql_limit_triple_play_sensitivity.py`
- `artifacts/autoresearch/stage966a_per_tid_aql_limit_triple_play_sensitivity.json`
- `tests/test_stage966a.py`
- MemoryMaster claim: `FMX-STAGE966A-PER-TID-AQL-SENSITIVITY` (FMX-S966A-01)
