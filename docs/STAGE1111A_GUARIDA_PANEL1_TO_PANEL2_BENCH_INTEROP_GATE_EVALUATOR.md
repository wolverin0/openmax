<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: Stage 1111A | Guarida SG-01 / SG-03..05 gate evaluator over a PROPOSED change set | fail-closed, evaluates the proposal not the panel | offline -->
# Stage 1111A - Guarida Panel1->Panel2 bench interop gate evaluator

Tool: `tools/autoresearch/guarida_panel1_to_panel2_bench_interop_gate_evaluator.py`.
Test: `tools/autoresearch/test_guarida_panel1_to_panel2_bench_interop_gate_evaluator.py`.
Receipt: `artifacts/autoresearch/stage1111a_guarida_panel1_to_panel2_bench_interop_gate_evaluator.json`.
No device is touched (`live_devices_touched=false`).

## Scope

The evaluator gates a PROPOSED change set (list of `{host, path_or_interface, op}`). It does not probe or
assess the panel. Panel1->Panel2 readiness remains NOT_READY (see `artifacts/autoresearch/stage882a_guarida_34endpoint_complete_readiness_audit.json`
and `artifacts/autoresearch/stage1077a_ptp_and_guarida_prerollout_readiness_matrix.json`). A GATE_PASS is not a readiness claim.

## Criteria source

Read from `artifacts/autoresearch/stage181a_guarida_panel2_panel3_preflight_gate_receipt.json` and
`artifacts/autoresearch/stage180a_guarida_panel2_panel3_28cpe_readiness_matrix.json`; none are invented.

- SG-01: zero writes or interface changes on the protected nodes (181A `protected_nodes`: 198.18.0.2 / ether2-sw-poe200,
  .200, .201, plus .60 and .61 as listed in 181A). Reads (`print`, `get`, `show`, ...) pass; any other or unknown op counts as a write.
  The interface name `ether2-sw-poe200` on any host also trips SG-01.
- SG-03: no write to the Panel1 AP 198.18.0.7 (180A `panel1_84_writes` = 0).
- SG-04: a `mac80211_teb` change must carry the pinned 6.6.110 `sha256`; the forbidden 6.6.127 hash fails.
- SG-05: no write to stock CPEs (10.10.210.x, 180A `cpe_writes` = 0); IE-free window >= 65 s,
  watchdog >= 45 s non-DFS and >= 120 s DFS when those fields are supplied.

## Verdicts

`GATE_PASS`, `GATE_FAIL_SG01_BACKBONE` (takes priority), `GATE_FAIL_SG03_05_ZERO_TOUCH`, `GATE_INCONCLUSIVE_NO_CHANGESET`.
Malformed entries fail closed under SG03_05.

## Usage

- `evaluate_changeset(changes, sg_hosts=None) -> {verdict, violations, checks}`.
- CLI: `--changeset file.json` (exit 0 only on GATE_PASS); `--write-receipt` writes the receipt.
- Self-test: `python -m pytest tools/autoresearch/test_guarida_panel1_to_panel2_bench_interop_gate_evaluator.py` (SYNTHETIC fixtures, nothing written).

## Known limits

The SG-03..05 rules are an operational reading of the 181A gate fields, not a verbatim 181A predicate set.
