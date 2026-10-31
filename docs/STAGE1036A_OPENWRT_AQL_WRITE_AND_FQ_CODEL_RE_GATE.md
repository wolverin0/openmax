<!-- doc-head: Stage 1036A | static-only consumer gate for the OpenWrt AQL write and fq_codel RE chain 1031A..1036A | status CONFIRMED when the contract and three cross checks hold | live_devices_touched false -->
<!-- /doc-head -->
# Stage 1036A - OpenWrt AQL Write and fq_codel RE Gate

Offline, fail-closed consumer gate for the five upstream receipts and the six
stage docs of the chain 1031A..1036A. Nothing here contacts a radio, an AP, a
CPE or an OpenWrt host. No upstream binary, kernel tree or symbol table is
re-read: the gate consumes what the upstream receipts declare and tests that
those declarations are complete, internally consistent and mutually compatible.

The gate measures. It does not require that AQL write support be found, that a
format syntax be confirmable, or that any fq_codel default match. A stage that
claims a syntax or a default without the evidence field that backs it fails.

## Files

- Gate: `tools/verify/verify_stage1036a_openwrt_aql_write_and_fq_codel_re_gate.py`
- Suite: `tests/test_stage1031a_to_1036a_suite.py`
- Receipt: `artifacts/autoresearch/stage1036a_openwrt_aql_write_and_fq_codel_re_gate.json`
- Upstream receipts: `artifacts/autoresearch/stage103{1,2,3,4,5}a_*.json`
- Upstream docs: `docs/STAGE103{1,2,3,4,5}A_*.md`

A receipt is resolved by glob and then by its own declared stage. The chain uses
two declaration sites: `meta.stage` for 1031A..1033A and a top level `stage` for
1034A..1035A. Both are accepted and the declaring field is recorded per stage in
the gate receipt, so the split stays visible instead of being smoothed over. Two
candidates declaring the same stage is a failure, not a preference. A doc is
resolved by glob and must be unique.

## Contract, per receipt `summary`

| Stage | Required |
| :--- | :--- |
| 1031A | `openwrt_label_verified == 0`; `aql_read_symbol == 0`; `aql_write_symbol == 0`; `sscanf_hits >= 0`; `scnprintf_hits >= 0`; `aql_field_names` non-empty; `syntax_confirmed` in (0, 1); `syntax_confirmed == 1` requires non-empty `format_strings`; `stage955a_contains_expected` in (0, 1) |
| 1032A | `airtime_check_is_symbol` in (True, False, 0, 1); `aqm_token_hits >= 0`; `aqm_fields` and `aql_fields` are lists; `evidence_grade` non-empty |
| 1033A | `layers_total >= 2`; `boundary_documented == 1`; `syntax_confirmed` in (0, 1) and equal to 1031A by the `syntax_agrees` cross check |
| 1034A | `fq_init_present == 0`; `fq_tin_dequeue_present == 0`; `codel_should_drop_present == 0`; `fq_knob_names` non-empty; `0 <= matches_expected <= 3`; `matches_expected` equals the count of non-null `found_defaults` entries that equal `expected_defaults`; `stage955a_contains_expected` in (0, 1) |
| 1035A | `codel_symbols_present == 0`; `divergence_count >= 0`; `mac80211_defaults` and `classic_fq_codel_defaults` are objects; `boundary_documented == 1` |

Two evidence rules make the table stricter than a type check.

1. `syntax_confirmed == 1` with no format evidence is rejected. `format_strings`
   may hold strings or call-site objects; either way at least one extracted text
   must contain a printf conversion such as `%u`, because a symbol name alone is
   not a format syntax. This catches a stage that infers `sscanf` syntax from a
   function name.
2. `matches_expected` is recomputed from the receipt's own tables. A count that
   disagrees with `found_defaults` and `expected_defaults` fails, so a default
   may not be asserted in prose while the evidence table is empty. A count of 3
   is never required; 0, 1, 2 and 3 all pass when the arithmetic agrees.

The gate deliberately does not assert `matches_expected == 3` and does not
assert that syntax is confirmed. Both are measurements, not obligations.

## The three cross-stage checks

| Name | Rule |
| :--- | :--- |
| `fq_names_absent_agrees` | Every fq/codel `*_present` flag reported by 1034A and 1035A is zero, and each stage reports at least one such flag |
| `syntax_agrees` | 1031A `syntax_confirmed` equals 1033A `syntax_confirmed`, both in (0, 1) |
| `version_label_agrees` | 1031A `openwrt_label_verified == 0` and 1031A `vermagic` equals 1034A `vermagic`, both non-empty |

Vermagic is read from `summary.vermagic`, then `meta.vermagic`, then
`meta.target_binary.vermagic`, and compared on stripped strings. 1031A records
it in the summary; 1034A records it under `meta.target_binary` with a trailing
space, so a raw string compare would fail on whitespace alone rather than on a
different kernel version.

The receipt records exactly these three names under `cross_checks`; the suite
asserts the key set and the count of three, so a fourth silent check cannot be
added without a documentation change.

## Provenance invariants, all six receipts

Every receipt, including this gate's own, must carry `meta.radio_safety` equal
to `static only`, a `scope` string containing `static`, a non-empty `gaps` list
of non-blank strings, and a non-empty `evidence_provenance_class`. The whole
document is walked for keys that collide case-insensitively; one collision fails
the stage. The gate's own payload is rebuilt through `decase()`, which refuses a
collision before serialisation instead of silently keeping the last key.

## Determinism

No wall-clock value is written. The receipt carries
`inputs_digest_sha256` over the five upstream receipt bytes and the six doc
bytes, so a rerun on unchanged inputs is byte-identical. The suite runs each of
the six scripts twice and compares receipt bytes. Receipt writes retry three
times against all-NUL corruption.

## Refusals

- A missing, unparseable, all-NUL or ambiguous upstream receipt fails the gate.
- A receipt whose `meta.stage` names another stage fails.
- A doc at 180 lines or more, or with a doc-head not at line 1, fails.
- A default or syntax claim without its evidence field fails that stage.
- The gate never infers a symbol from a name, and never upgrades a measurement
  into a confirmation.

## Gaps

- No live validation. Every conclusion rests on static receipts and source text.
- The five upstream receipts are authored concurrently by other agents. This gate
  checks schema, arithmetic and mutual agreement, not the truth of their scans.
- `expected_defaults` is taken as given. A wrong expectation table would make a
  matching count look correct, so the count is evidence of consistency only.
- Determinism is demonstrated on one interpreter and platform, not across both.

## Running

```text
python tools/verify/verify_stage1036a_openwrt_aql_write_and_fq_codel_re_gate.py
python -m pytest tests/test_stage1031a_to_1036a_suite.py -q
```

The gate exits non-zero and writes a FAILED receipt with the failure list when
any clause above is unmet. A green gate means the chain is consistent, not that
the radio behaviour is proven.
