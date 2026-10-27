<!-- doc-head: Stage 887A offline classifier of all 1186 autoresearch receipts into CONFIRMED_LIVE_BENCH / CONFIRMED_STATIC_BINARY / SIMULATED_MODEL_ONLY / UNKNOWN with transparent heuristics -->
# Stage 887A — Empirical vs Simulated Evidence Audit

- **Claim Status**: `CONFIRMED` (offline classifier)
- **Attribution**: `external controller (offline classifier)` — no radio, no SSH
- **Artifact**: `artifacts/autoresearch/stage887a_empirical_vs_simulated_evidence_audit.json`
- **Tool**: `tools/verify/build_stage887a_empirical_vs_simulated_evidence_audit.py`
- **Evidence class**: `SIMULATED_MODEL_ONLY` (it is itself an offline analysis)

## 1. Purpose
Operationalizes audit A08/A10: every receipt in `artifacts/autoresearch/*.json` is
tagged with an evidence class so a downstream summary cannot mistake a model or an
unlabelled synthesis for a physical measurement.

## 2. Transparent heuristics
| Class | Rule |
| :--- | :--- |
| `CONFIRMED_LIVE_BENCH` | measurement series (`windows`/`*_rounds`) or `live`-named + ping/goodput metrics or device IPs + hardware attribution, not flagged offline |
| `CONFIRMED_STATIC_BINARY` | SGMT/xtensa/patch binary analysis (hashes, patches), no device execution |
| `SIMULATED_MODEL_ONLY` | SimPy/pymoo/analytic or offline-model marker or `live_devices_touched=False` model |
| `UNKNOWN` | ambiguous or insufficient signal (synthesis/plan/RE/unlabelled) |

These are deliberately conservative; this is a **first-pass triage, not a
per-champion provenance fiche** (that remains A10's separate requirement).

## 3. Results (1186 receipts scanned)
| Class | Count | % |
| :--- | :--- | :--- |
| CONFIRMED_LIVE_BENCH | 131 | 11.0 |
| CONFIRMED_STATIC_BINARY | 116 | 9.8 |
| SIMULATED_MODEL_ONLY | 58 | 4.9 |
| UNKNOWN | 869 | 73.3 |
| UNREADABLE (NUL/parse) | 12 | 1.0 |

## 4. Reading the result
Only ~11 % of receipts carry a clear live-hardware benchmark signature; ~73 % are
synthesis/plan/RE or otherwise unlabelled and cannot be cited as physical evidence
without a provenance fiche. This is the quantified form of the audit's core concern:
the window *count* is not the evidence — the *genealogy* is. The downstream
reclassification (Stage 888A) turns this into integrity flags.

## 5. Reproduce & limits
```sh
python tools/verify/build_stage887a_empirical_vs_simulated_evidence_audit.py
python -m pytest tests/test_stage885a_to_890a_suite.py -q
```
Heuristic, not authoritative: a receipt's class reflects its own self-description,
which the audit warns can be optimistic. UNKNOWN is an honest "needs a fiche", not a
failure. The 12 UNREADABLE receipts are filesystem-corrupted (all-NUL) inputs.
