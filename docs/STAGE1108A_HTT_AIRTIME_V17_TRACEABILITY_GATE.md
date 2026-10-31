<!-- doc-head: Stage 1108A gates the HTT airtime and v17 kit traceability wave 1103A..1108A, deriving coverage and invalid-write counts as measurements while holding fabricated ath10k offsets at zero; CONFIRMED_STATIC_BINARY, static only -->
<!-- /doc-head -->
# Stage 1108A - HTT airtime and v17 kit traceability gate

Evidence class: `CONFIRMED_STATIC_BINARY`. `radio_safety: static only`.

- **Receipt**: [`artifacts/autoresearch/stage1108a_htt_airtime_v17_traceability_gate.json`](../artifacts/autoresearch/stage1108a_htt_airtime_v17_traceability_gate.json)
- **Tool**: [`tools/verify/verify_stage1108a_htt_airtime_v17_traceability_gate.py`](../tools/verify/verify_stage1108a_htt_airtime_v17_traceability_gate.py)
- **Headline**: `compliant=true checks=16/16 cross=3/3 ath10k_present_claims=3 ath10k_fabricated_offsets=0`

## What this gate refuses to demand

Two figures are measurements, not targets. `coverage_measured` is accepted anywhere in `[0, 1]`
and `invalid_writes` is accepted at any value, because a corpus that traced perfectly and a kit
that never wrote a bad line would be the fiction the previous wave already disproved.

The write arithmetic is a separate question and is reported separately:

- Stipulated identity: `valid_writes + invalid_writes + unknown_writes == writes_total`
- `two_term_holds` = False
- `unknown_published` = True
- Published partition: 18 valid + 0 invalid + 2 unknown = 20 against writes_total 20

Stage1171A requires the exact three-way partition. `two_term_holds` remains a historical diagnostic;
unknown writes remain unknown and are never folded into valid or invalid counts.

One figure is a target and stays one: `ath10k_fabricated_offsets` is 0. A fabricated offset is a
false claim rather than corpus dirt, so every offset in 1103A is checked against the real
`ath10k_core.ko` bytes from the tar member named in `EXTRACTION.json`.

## Checks

| check | verdict | detail |
| :--- | :--- | :--- |
| `receipt_1103a_contract` | PASS | core and pci present, sizes match the extracted files, provenance names a tar source, offsets recovered is positive |
| `receipt_1104a_contract` | PASS | mac80211 present with non-empty format_strings and handler_offsets |
| `receipt_1105a_contract` | PASS | two kits, writes_total positive, valid plus invalid plus unknown equals total, evidence names1031A |
| `writes_sum_closes_1105a` | PASS | the published write partition closes the total: 18 valid + 0 invalid + 2 unknown = 20 against writes_total 20 |
| `receipt_1106a_contract` | PASS | files_scanned positive, exact three-way path census closes; IPTV flag is boolean |
| `path_census_closes_1106a` | PASS | the published path-form census closes: 5 valid + 0 invalid + 1 unknown = 6 against 6 unique paths |
| `receipt_1107a_contract` | PASS | at least four receipts found, coverage inside [0, 1], sweep scope declares the tar members |
| `matrix_arithmetic_not_normalised` | PASS | traced plus untraced equals matrix_rows and coverage equals traced over rows |
| `ath10k_provenance_consistent` | PASS | all three cite the same ath10k_core tar member lib/modules/6.6.110/ath10k_core.ko |
| `v17_kits_cite_proven_formats` | PASS | 5 cited format literal(s) are all present among 16 proven literals |
| `matrix_covers_this_wave` | PASS | stages_in_matrix carries 76 stage numbers and covers 1103A..1106A |
| `ath10k_absence_claims_are_scoped` | PASS | 0 ath10k absence claim(s) found, each either tar-scoped or scoped to another kernel object |
| `ath10k_present_positively_claimed` | PASS | 3 positive ath10k attributions, 2 of them in 1103A |
| `ath10k_offsets_not_fabricated` | PASS | 61 offset(s) published by 1103A, 9 self-verified by a display or byte witness, 52 carried no witness, 0 contradicted the module bytes or their own dis |
| `receipt_1108a_contract` | PASS | structural fields present, cross-check names exact, fabricated offsets 0 |
| `docs_shape_1103a_to_1107a` | PASS | upstream docs under 180 lines, one doc-head each, no exclamation mark in prose |

`checks_run` = 16, `checks_passed` = 16.

## Cross-stage checks

| check | verdict | detail |
| :--- | :--- | :--- |
| `ath10k_provenance_consistent` | PASS | all three cite the same ath10k_core tar member lib/modules/6.6.110/ath10k_core.ko |
| `v17_kits_cite_proven_formats` | PASS | 5 cited format literal(s) are all present among 16 proven literals |
| `matrix_covers_this_wave` | PASS | stages_in_matrix carries 76 stage numbers and covers 1103A..1106A |

## Provenance invariants, all six receipts

`receipts_graded` = 6, `radio_safety_static_only` =
6, `scope_names_static` = 6,
`gaps_non_empty` = 6, `provenance_class_present` =
6, `case_collisions` = 0.

## ath10k presence and absence

`ath10k_present_claims` = 3,
`ath10k_absence_claims` = 0,
`ath10k_offsets_verified` = 9,
`ath10k_offsets_unverifiable` = 52.

Stage 1056A reported `ath10k_core_present: 0` after scanning 1,169 loose `.ko` files. The module
was not missing; the sweep was. Seventy-two ath10k copies were later found inside tar members, and
`EXTRACTION.json` recovers two of them for this wave. An ath10k absence assertion is therefore
graded against the sweep scope that accompanies it, never on its own.

| stage | absence field | scope names tar | scoped to another object |
| :--- | :--- | :--- | :--- |
| none | none | 0 | 0 |

## Failures

- none

## Gaps

- The gate checks schema, arithmetic, citations and mutual agreement of six receipts. It does not re-run the dissections, so a wrong offset reported consistently by two stages would pass the cross-check and only the byte-witness clause would catch it, and only when a witness exists.
- ath10k offset fabrication is decided against artifacts/firmware_re_ath10k_tar/ath10k_core.ko. An offset claimed by 1103A that is not present in that file is out of scope of this gate, so an offset with no byte witness is counted as unverifiable rather than fabricated. The unverifiable count is published so the difference is visible.
- ath10k_provenance_consistent compares the member identity each receipt cites, not the full sentence. Three receipts that all name ath10k_core.ko and all declare tar provenance pass even when their prose differs, and the canonical form each one produced is recorded so the comparison can be audited rather than trusted.
- v17_kits_cite_proven_formats can pass vacuously when 1105A cites no conversion literal at all. That case is flagged as vacuous in the cross-check detail instead of being reported as a strong result, and the flag is part of the published receipt.
- invalid_writes is not required to be 0. A kit that writes nothing valid and a kit that writes nothing at all are distinguished only by the arithmetic identity and by writes_total, which is why writes_total must be positive.
- The stipulated write identity is valid plus invalid equals writes_total. When a receipt also publishes an unknown_writes bucket, the gate still grades the stipulated two-term form as a hard clause and separately reports whether the three-term partition closes. Folding unknown writes into valid or invalid would make the two-term form balance by restating a measurement, which this gate refuses to do.
- coverage_measured is not required to be 1. The gate enforces that the published figure equals traced over rows, so the number cannot be rounded or restated, and it enforces the range. It does not enforce a floor.
- Documentation is checked for shape only: line count, exactly one doc-head on line one, and no exclamation mark. Prose truth is not machine-checked.
- No dynamic validation: no module was loaded, no kit was executed, no radio or host was contacted.

## Claim boundary

The gate grades schema, arithmetic, citation agreement and byte-witnessed offsets inside one
extracted module. It does not re-dissect any kernel object, does not prove any kit line correct, and
does not prove any value safe. No module was loaded, no kit was run, no device was contacted.
