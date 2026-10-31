<!-- doc-head: Stage 1125A operator monitoring and abort-criteria guide for the production PtP canary (prepare-only, offline) -->
Prepare-only. No device was touched; nothing here is a readiness claim.
<!-- /doc-head -->

# Stage 1125A - PtP production canary monitoring and abort criteria

Owner: Codex #1 (live lane). Receipt: `artifacts/autoresearch/stage1125a_ptp_production_canary_monitoring_and_abort_criteria.json` with `execution_status` `MONITORING_DOC_ONLY`.

## Tools the operator uses

| Tool | Source stage | Role |
|---|---|---|
| Canary monitor (`build_plan` / `evaluate`) | `docs/STAGE1121A_*.md` | `build_plan` emits the read-only sampling plan; `evaluate` classifies the saved samples |
| Fault-matrix self-test | `tests/test_stage1122a_ptp_canary_monitor_fault_matrix.py` | Proves each verdict fires on its fault, offline |
| One-shot health dump | `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_ptp_v17_one_shot_health_dump.sh` | Single read-only snapshot for the operator, Stage 1123A |
| Restricted-path test | `tests/test_stage1124a_health_dump_restricted_path.py` | Proves the dump stays inside its allowed paths |
| Watchdog v17 | `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_ptp_rollback_watchdog_v17.sh` | Automatic rollback on the device |

## Verdict ladder

`evaluate` returns one verdict per sample window. Only the first one below is an abort.

| Verdict | Meaning | Operator action |
|---|---|---|
| `ROLLBACK_REQUIRED` | An abort threshold is crossed | Abort the canary and roll back (see below) |
| `DEGRADED` | Link is impaired but not an abort | Keep watching; do not roll back for this alone |
| Healthy | All sampled metrics inside bounds | Continue the window |

## Abort criteria (ROLLBACK_REQUIRED)

Any single one is sufficient.

| Metric | Abort threshold |
|---|---|
| Packet loss | `loss_pct` greater than 2% |
| Latency tail | p99 greater than 40 ms |
| Chain imbalance | greater than 6 dB between chains |

Do not average away a breach. A threshold crossed in one window is an abort.

## DFS radar CAC is DEGRADED, not an abort

A radar hit on a DFS channel starts a Channel Availability Check. The wait is a regulatory requirement, so the monitor reports `DEGRADED`. Do not roll back on it. The watchdog uses its 120 s window for DFS so the CAC wait is not mistaken for failure.

## Watchdog v17 auto-rollback

`fmx_ptp_rollback_watchdog_v17.sh` runs on the device with a 45 s window, or 120 s with `--dfs`. If the link is not confirmed inside the window it rolls back by itself, without the operator. The operator abort above is the manual path and is not a substitute for the watchdog.

## One-shot health dump

Run the Stage 1123A script once when a verdict is unclear or after a rollback. It is a single read-only snapshot; save the output next to the monitor samples. It is not a continuous monitor.

## Standing open decisions

| Decision | State |
|---|---|
| `aql_threshold` 24000 versus 12000 | Open. Not resolved by this guide; the operator decides before widening the canary |
| LiteBeam | `NO_EVIDENCE`. No LiteBeam result exists; do not extrapolate from PowerBeam |
| v17 persistence | Runtime-only. A reboot discards it; nothing is written to flash |

## Boundaries

- This stage ran no SSH and touched no device (`live_devices_touched` is `false`).
- No value in the receipt is a readiness claim. Acceptance needs live evidence from Codex #1.
- Gate: `tools/verify/verify_stage1126a_wave15_claude_gate.py`.
