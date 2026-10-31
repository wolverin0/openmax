<!-- doc-head: Stage 1193A wave 26 OpenCode gate 1188A..1193A, per-stage contract clauses, three named cross-stage checks, offline and collision assertions -->

# Stage 1193A - Wave 26 OpenCode Gate (1188A..1193A)

Static and offline. The gate reads six receipts, checks each stage against its contract
clause by clause, evaluates three named cross-stage checks, and asserts the wave-wide
conventions. Nothing was executed, loaded, flashed or contacted.

## Headline

| Measure | Value |
| :--- | ---: |
| Compliant | True |
| Checks run | 69 |
| Checks passed | 69 |
| Failures | 0 |
| Receipts parsed | 5 of 6 |
| Fabricated offsets | 0 |
| Offline confirmed | 1 |

## Per-stage clauses

| Bucket | Run | Passed | Failed clause ids |
| :--- | ---: | ---: | :--- |
| 1188A | 9 | 9 | - |
| 1189A | 10 | 10 | - |
| 1190A | 9 | 9 | - |
| 1191A | 11 | 11 | - |
| 1192A | 13 | 13 | - |
| 1193A | 11 | 11 | - |
| wave | 3 | 3 | - |
| cross-stage | 3 | 3 | - |

The buckets reconcile with the headline: 69 checks in total, and
1193A includes its own self-verdict, which is evaluated last.

## The three cross-stage checks

| Check | Passed |
| :--- | :--- |
| `ath10k_provenance_consistent` | True |
| `absent_versions_agree` | True |
| `signatures_cover_this_wave` | True |

`ath10k_provenance_consistent` requires 1189A and 1192A to cite the same ath10k_core tar
member, compared after stripping any archive prefix, because two lanes may qualify the
same member with different archive paths. `absent_versions_agree` requires the three eab
counters declared by 1191A to reappear with the same zeros in 1192A, and the absent
version label to appear as a (family, version) pair. `signatures_cover_this_wave` requires
the matrix to name all four source stages.

## Receipts read

| Stage | Receipt | Status | Parsed |
| :--- | :--- | :--- | :--- |
| 1188A | `stage1188a_uph_umac_airview_acs_re.json` | - | True |
| 1189A | `stage1189a_ath10k_survey_spectral_re.json` | - | True |
| 1190A | `stage1190a_uph_ptmp_rate_collapse_re.json` | - | True |
| 1191A | `stage1191a_ltu_modulation_atpc_re.json` | - | True |
| 1192A | `stage1192a_binary_re_to_field_symptom_signatures.json` | CONFIRMED | True |
| 1193A | `stage1193a_wave26_opencode_gate.json` | CONFIRMED | True |

1193A is written by this gate, so its row is declared rather than read; the suite hashes
the persisted file after the write.

## Measurements that are not pinned

- `coverage_measured` is bounded to [0, 1]. It is not required to be 1.0, and demanding
  that would report a fiction: the matrix publishes the gaps that keep it below 1.
- `hypotheses_supported` is bounded by `hypotheses_total`. Equality is not required.
- `offsets_recovered` must be positive. No magnitude is asserted, because the count is
  a measurement of what the disassembly actually yielded.

## Offline

`offline_confirmed = 1`. 6 of 6 receipts declare `radio_safety` static only and
a static scope, and none of them declares a live device touch. The per-receipt evidence
is carried in `offline.per_receipt`.

## Failures

None. Every clause and every cross-stage check passed.

## Gaps

- The gate checks declared fields against the wave contract. It does not re-disassemble any module, so a symbol name a lane reports is checked for presence, not for truth.
- fabricated_offsets counts offsets outside the measured byte length of the module they claim to address. An offset inside the file that addresses the wrong instruction passes this check and is not caught here.
- coverage_measured is bounded to [0, 1] and hypotheses_supported is bounded by hypotheses_total. Neither is pinned: both are measurements and previous waves proved the gaps are real.
- Contract fields are located by exact key, so a lane that renames a field is reported as a missing field rather than mapped to an approximate name.

## Reproduce

```
python tools/verify/verify_stage1193a_wave26_opencode_gate.py
python -m pytest tests/test_stage1188a_to_1193a_suite.py -q
```

