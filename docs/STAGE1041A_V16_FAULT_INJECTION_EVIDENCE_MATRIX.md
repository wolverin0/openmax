<!-- doc-head: Stage 1041A fault-injection evidence matrix {scenario, expected, observed, pass} for the v16 kits -->
<!-- /doc-head -->
# Stage 1041A: v16 fault-injection evidence matrix

Derived from the junit result of `tests/test_stage1039a_v16_busybox_restricted_path_harness.py`
(builder: `tools/verify/build_stage1039a_to_1041a_v16_adversarial_receipts.py`).

## Matrix rows (per kit where applicable)
| Scenario | Expected |
| :--- | :--- |
| poison trap self-check | `stat`/`tc` exit 127 and marker written |
| `--dry-run` | exit 0, no writes |
| `--apply` | exit 0, snapshot, 4 AC writes, persistence |
| `--verify` champion / stock | 0 / non-zero |
| `--rollback` then `--verify` | stock restored, verify non-zero |
| FAULT snapshot removed, `--rollback` | non-zero |
| FAULT read-only AQL, `--apply` | non-zero |
| PBE watchdog (`operstate=down`, 2 s) | auto-rollback, non-zero |

## Invariant
The poison marker is empty after every successful run (kit never invoked
`stat tc timeout seq usleep iperf3 python python3`). Recorded in `poison_marker_empty_invariant`.

## Result semantics
`pass` is `true` (passed), `false` (deviation) or `null` (skipped; for example the read-only case on
Windows where chmod is not enforced). Receipt: `artifacts/autoresearch/stage1041a_v16_fault_injection_evidence_matrix.json`.
