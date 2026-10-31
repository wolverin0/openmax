<!-- doc-head: Stage 841A offline statistical confidence ledger; percentile bootstrap 95% CI + Wilcoxon signed-rank over pooled window metrics from 695A/837A/839A receipts -->
<!-- /doc-head -->
# Stage 841A — Statistical Confidence Ledger (Bootstrap + Wilcoxon)

- **Claim Status**: `CONFIRMED` (offline statistics)
- **Attribution**: `external controller (offline statistics)` — no radio, no SSH
- **Artifact**: `artifacts/autoresearch/stage841a_1020window_statistical_confidence_ledger.json`
- **Tool**: `tools/verify/build_stage841a_1020window_statistical_confidence_ledger.py`

## 1. Method
Each comparison gets a **percentile bootstrap 95 % CI** on the mean difference
(10 000 resamples, `seed=20261027`, deterministic) plus, for paired samples of
n ≥ 6, a **Wilcoxon signed-rank** test. A CI that excludes zero marks a difference
resolvable at 95 % confidence. Pooled window count is reported honestly (38); the
filename's "1020" is nominal, not a claimed sample size.

## 2. Ledger
| Comparison | mean Δ (b−a) | bootstrap CI95 | excl. 0 | Wilcoxon p |
| :--- | :--- | :--- | :--- | :--- |
| 839A airtime-fair − equal-TXOP agg (Mbps) | +12.08 | [10.32, 13.68] | **yes** | **0.0078** |
| 837A stressed VHT40 − VHT80 MCS stability (%) | +22.38 | [0.00, 55.19] | no | 0.25 |
| 695A live arm B − arm A agg (Mbps) [small-n] | −0.12 | [−1.20, 0.97] | no | n/a (n<6) |

## 3. Reading the ledger
- **Airtime fairness is statistically solid**: +12.08 Mbps mean uplift, CI well
  clear of zero, Wilcoxon p = 0.0078 → the +18.55 % headline (Stage 839A) is not
  noise.
- **VHT40's stressed-range advantage is directionally large (+22 % stability) but
  not statistically resolvable** across only 9 distances: the effect is bimodal
  (0 % vs 100 % stability per distance), so the CI spans zero and Wilcoxon p = 0.25.
  Honest verdict: *promising, under-powered* — more distance granularity needed to
  claim significance.
- **695A arm A vs arm B is a null at n = 2 per arm**: the PB-040/050 Arm B shows no
  resolvable aggregate difference vs stock-timing Arm A in this degraded window —
  consistent with the 695A degraded-window flag (Stages 695A/699A).

## 4. Reproduce & limits
```sh
python tools/verify/build_stage841a_1020window_statistical_confidence_ledger.py
python -m pytest tests/test_stage841a.py -q
```
Non-significant comparisons are reported as such, not hidden. The offline-sim
inputs carry their own model caveats (Stages 837A/839A); the ledger quantifies
uncertainty in those populations, it does not validate the models against hardware.
