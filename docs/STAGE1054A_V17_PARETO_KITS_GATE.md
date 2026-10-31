<!-- doc-head: Stage 1054A offline fail-closed gate + consolidated suite for the v17 Pareto BusyBox kits and the 1053A OTA PtP runbook (1049A..1053A); no live devices. -->
<!-- /doc-head -->
# Stage 1054A - v17 Pareto kits gate

Fail-closed, offline. Exits with `SystemExit(1)` on any failure. Writes
`artifacts/autoresearch/stage1054a_v17_pareto_kits_gate_receipt.json` (retry 3x on all-NUL).

Gate: `tools/verify/verify_stage1054a_v17_pareto_kits_gate.py`
Suite: `tests/test_stage1049a_to_1054a_suite.py`

Artifacts are located by stage-number glob (`stage1049a_*.json`, `STAGE1049A_*.md`,
`fmx_wa_v17*.sh`, `fmx_pbe5ac_v17*.sh`); exactly one match each is required.

## Checks

1. Receipts 1049A..1053A exist, not all-NUL, status CONFIRMED, `live_devices_touched` False,
   pass `audit_stage_receipt_5pillars`.
2. Docs 1049A..1054A exist, under 180 lines, line 1 starts with `<!-- doc-head:`.
3. Both v17 kits exist, no CR bytes, `sh -n` clean (skip recorded if no `sh`).
4. Bashism grep (non-comment lines): `[[`, `function `, `declare `, `local -`, `=(`, `$'`,
   `==` inside `[ ]` - none allowed.
5. 1025A `audit_text` on each kit: 0 findings; `|| true` / `|| :` count 0.
6. `--dry-run` of each kit under a fake `--root` (with `FMX_WRITE_TRACE`): plan references
   `aql_txq_limit`, `aql_threshold`, `aqm`, `tcp_notsent_lowat`, `default_qdisc`; 4 AQL
   `idx low high` lines (idx 0..3); 3 `fq_xxx N` aqm writes; the u32 and two scalars.
7. `python -m pytest tests/test_stage1051a_v17_pareto_busybox_restricted_path_harness.py -q`
   returns 0 (a skip counts as pass and is recorded).
8. The 1052A receipt records 0 findings for both kits; the 1053A receipt records
   `execution_status` `RUNBOOK_NOT_EXECUTED`.

## Honesty notes

- The gate proves offline kit hygiene and plan shape only. It does not prove any on-air gain.
- The runbook (`docs/STAGE1053A_PRODUCTION_PTP_OTA_ROLLOUT_RUNBOOK.md`) is NOT executed.
  PowerBeam is `NOT_READY`; LiteBeam is `NO_EVIDENCE` (Stage 1009A).
- The orchestrator runs the final gate and suite at phase close.

## Receipt

Claim id `FMX-STAGE1054A-V17-PARETO-KITS-GATE`; status CONFIRMED iff `all_gates_passed`.
