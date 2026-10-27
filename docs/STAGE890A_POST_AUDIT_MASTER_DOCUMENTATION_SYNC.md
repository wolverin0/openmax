<!-- doc-head: Stage 890A post-audit master documentation sync & consolidated gate for 885A-890A; master docs carry the honest live-vs-simulated classification, fail-closed gate -->
# Stage 890A — Post-Audit Master Documentation Sync & Gate

- **Claim Status**: `CONFIRMED` (offline gate)
- **Attribution**: `external controller (offline gate)` — no radio, no SSH
- **Artifact**: `artifacts/autoresearch/stage890a_post_audit_master_documentation_sync.json`
- **Tool**: `tools/verify/verify_stage890a_post_audit_live_and_docs_gate.py`
- **Evidence class**: `DOCUMENTATION_SYNC_GATE`

## 1. What it closes
The post-audit remediation set (Stages 885A–889A) plus the master-doc sync. It is the
single fail-closed gate for the ChatGPT audit response delivered in the offline role.

## 2. Gate checks
- **885A–889A receipts**: exist, `status=CONFIRMED`, `live_devices_touched=False`,
  5-pillar compliant, not NUL-corrupt.
- **Stage docs 885A–890A**: exist, < 180 lines, open with a `<!-- doc-head:`.
- **Master docs**: both `MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md` and
  `CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md` carry the
  "Post-Audit Evidence Classification" section and stay ≤ 250 lines.

## 3. Master-doc sync (the honest classification)
Both master docs now record, as first-class content:
- The evidence-class split of all 1186 receipts: 131 `CONFIRMED_LIVE_BENCH`,
  116 `CONFIRMED_STATIC_BINARY`, 58 `SIMULATED_MODEL_ONLY`, 869 `UNKNOWN`, 12 `UNREADABLE`.
- The integrity flags: **338** receipts declared `CONFIRMED` without physical
  confirmation; **40** simulated-but-declared-`CONFIRMED`.
- The rule that simulated/unknown results must never be promoted to live-hardware
  evidence without an A10 provenance fiche.

## 4. Remediation map (audit → stage)
| Audit finding | Remediation stage |
| :--- | :--- |
| A01/A02 fail-open kit + fq_codel token | 885A field-kit hardening |
| A03 A/A control + hold-out identity | 886A protocol + self-tests |
| A08/A10 empirical vs simulated | 887A classifier · 888A reclassification |
| A07/A06 power & pre-registration | 889A power/hold-out protocol |

## 5. Reproduce
```sh
python tools/verify/build_stage885a_post_audit_field_kits_hardening.py
python tools/verify/build_stage886a_post_audit_aa_control_protocol.py
python tools/verify/build_stage887a_empirical_vs_simulated_evidence_audit.py
python tools/verify/build_stage888a_historical_receipts_reclassification.py
python tools/verify/build_stage889a_statistical_power_and_holdout_protocol.py
python tools/verify/verify_stage890a_post_audit_live_and_docs_gate.py
python -m pytest tests/test_stage885a_to_890a_suite.py -q
```

## 6. Scope & limits
Offline only. The live evaluator/gatekeeper/patcher files cited by the audit are owned
by another lane and were not edited here (A03/A05/A09 remediations into those modules
are separate, lane-owned changes). This stage delivers the protocols, classifiers, and
hardened kit files, and makes the honest classification canonical in the master docs.
