<!-- doc-head: Stage 944A runs four offline generators twice and compares receipt sha256 (timestamp excluded) to measure seed determinism -->
# Stage 944A - Seed-Determinism Reproducibility Audit

- **Claim Status**: `CONFIRMED` (offline audit)
- **Attribution**: `external controller (offline audit)`; no radio, no SSH
- **Artifact**: `artifacts/autoresearch/stage944a_seed_determinism_reproducibility_audit.json`
- **Tool**: `tools/verify/build_stage944a_seed_determinism_reproducibility_audit.py`
- **Evidence class**: `DETERMINISM_AUDIT`

## Method
Each generator is run twice. The emitted JSON receipt is loaded, the `timestamp`
key is popped, and the canonical `json.dumps(sort_keys=True)` is sha256-hashed.
Stable means both hashes match. Original artifact bytes are restored afterwards.

## Result
- Deterministic fraction: **1.00** (4/4)

| Generator | Stable |
| :--- | :--- |
| `run_stage837a_simpy_ptp_vht40_vs_vht80_thermal_and_rain_fade_model.py` | True |
| `run_stage838a_pymoo_nsga3_guarida_32cpe_voip_iptv_bulk_pareto.py` | True |
| `run_stage839a_simpy_mixed_ac_and_m5_airtime_fairness_scheduler.py` | True |
| `build_stage889a_statistical_power_and_holdout_protocol.py` | True |

## Reproduce
```sh
python tools/verify/build_stage944a_seed_determinism_reproducibility_audit.py
python -m pytest tests/test_stage944a.py -q
```
Limit: only the listed generators are covered; other receipts may embed
non-timestamp volatile fields.
