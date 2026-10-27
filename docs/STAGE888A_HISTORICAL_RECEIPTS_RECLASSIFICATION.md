<!-- doc-head: Stage 888A historical receipts reclassification; integrity triage flagging 338 receipts declared CONFIRMED but not physically confirmed, 40 simulated-but-CONFIRMED -->
# Stage 888A — Historical Receipts Reclassification

- **Claim Status**: `CONFIRMED` (offline reclassification)
- **Attribution**: `external controller (offline reclassification)` — no radio, no SSH
- **Artifact**: `artifacts/autoresearch/stage888a_historical_receipts_reclassification.json`
- **Tool**: `tools/verify/build_stage888a_historical_receipts_reclassification.py`
- **Source**: consumes Stage 887A classification

## 1. Class totals (1186 receipts)
| Class | Count | % |
| :--- | :--- | :--- |
| CONFIRMED_LIVE_BENCH | 131 | 11.0 |
| CONFIRMED_STATIC_BINARY | 116 | 9.8 |
| SIMULATED_MODEL_ONLY | 58 | 4.9 |
| UNKNOWN | 869 | 73.3 |
| UNREADABLE | 12 | 1.0 |

## 2. Integrity flags (the point of the audit)
- **338 receipts declare `status=CONFIRMED` but are NOT physically confirmed**
  (evidence class SIMULATED_MODEL_ONLY or UNKNOWN).
- **40 receipts are SIMULATED_MODEL_ONLY yet declare `CONFIRMED`** — the exact A08
  "synthetic looks physical" risk.

These are not necessarily wrong as models/analyses — but they must **never** be
promoted to physical confirmation or copied into a champion summary as live bench.

## 3. Reclassification rule
| Evidence class | Handling |
| :--- | :--- |
| `SIMULATED_MODEL_ONLY` | keep the receipt; relabel; never cite as live bench |
| `UNKNOWN` | requires an A10 provenance fiche before any live-bench citation |
| `CONFIRMED_STATIC_BINARY` | valid at container/byte level; runtime execution still `UNKNOWN` |
| `CONFIRMED_LIVE_BENCH` | retains physical standing pending fiche spot-checks |

## 4. What this does and does not claim
It does **not** invalidate historical measurements. It separates "we measured this on
hardware" from "a model or a synthesis produced this number", and surfaces the 338/40
receipts where the declared status over-states the evidence class. Resolving each flag
is a per-champion provenance-fiche task (A10), not an automatic status downgrade.

## 5. Reproduce
```sh
python tools/verify/build_stage887a_empirical_vs_simulated_evidence_audit.py
python tools/verify/build_stage888a_historical_receipts_reclassification.py
python -m pytest tests/test_stage885a_to_890a_suite.py -q
```
Limits: inherits Stage 887A's heuristic nature. The flag counts are a triage signal to
prioritize provenance work, not a verdict on any individual receipt's correctness.
