<!-- doc-head: Stage 1162A Wave 21 OpenCode gate 1157A..1162A, per-stage contract clauses, three named cross-stage checks, offline and collision assertions -->

# Stage 1162A - Wave 21 OpenCode Gate (1157A..1162A)

Static and offline. The gate reads six receipts, checks each stage against its contract
clause by clause, evaluates three named cross-stage checks, and asserts the wave-wide
conventions. Nothing was executed, loaded, flashed or contacted.

## Headline

| Measure | Value |
| :--- | ---: |
| Compliant | True |
| Checks run | 52 |
| Checks passed | 52 |
| Failures | 0 |
| Receipts parsed | 6 of 6 |
| Read from disk | 5 |
| ath10k fabricated offsets | 0 |
| Offline confirmed | 1 |

## Per-stage clauses

| Bucket | Run | Passed | Failed clause ids |
| :--- | ---: | ---: | :--- |
| 1157A | 10 | 10 | - |
| 1158A | 8 | 8 | - |
| 1159A | 7 | 7 | - |
| 1160A | 10 | 10 | - |
| 1161A | 7 | 7 | - |
| 1162A | 5 | 5 | - |
| wave | 2 | 2 | - |
| cross-stage | 3 | 3 | - |

The buckets reconcile with the headline: 52 checks in total, and 1162A
includes its own self-verdict, which is evaluated last.

## The three cross-stage checks

| Check | Passed |
| :--- | :--- |
| `ath10k_provenance_consistent` | True |
| `absent_versions_agree` | True |
| `wave_receipts_in_ledger` | True |

`ath10k_provenance_consistent` compares the tar member paths cited by 1157A and 1161A
after stripping any archive prefix, because two lanes may qualify the same member with
different archive paths. `absent_versions_agree` compares the absent-version labels of
1159A and 1160A against the ledger as (family, version) pairs. `wave_receipts_in_ledger`
requires the ledger to count at least the four wave receipts and to name their root.

## Receipts read

| Stage | Root | Receipt | Status | Parsed |
| :--- | :--- | :--- | :--- | :--- |
| 1157A | `artifacts/verification` | `stage1157a_ath10k_htt_txrx_airtime_re.json` | - | True |
| 1158A | `artifacts/verification` | `stage1158a_mac80211_aql_threshold_may_transmit_re.json` | - | True |
| 1159A | `artifacts/verification` | `stage1159a_uph_allow_80211_hybrid_ota_re.json` | - | True |
| 1160A | `artifacts/verification` | `stage1160a_ltu_ame_passive_safe_paths_re.json` | - | True |
| 1161A | `artifacts/verification` | `stage1161a_master_binary_re_ledger_1031a_to_1160a.json` | CONFIRMED | True |
| 1162A | `artifacts/verification` | `stage1162a_wave21_opencode_gate.json` | CONFIRMED | True |

1162A is written by this gate, so its row is declared rather than read; the suite hashes
the persisted file after the write.

## Measurements that are not asserted as equalities

- `coverage_measured` is bounded to [0, 1]. It is not required to be 1.0, and this gate
  would be reporting a fiction if it demanded that.
- `condition_confirmed` may be 0 or 1. A zero must be accompanied by a declared gap, and
  the zero is carried in the checks rather than hidden.

## Offline

`offline_confirmed = 1`. 6 of 6 receipts declare `radio_safety` static only
and a static scope, and none of them declares a live device touch. The per-receipt
evidence is carried in `offline.per_receipt` of the receipt.

## Failures

None. Every clause and every cross-stage check passed.

## Gaps

- 4 of 6 receipts declare no status field (['1157A', '1158A', '1159A', '1160A']); the gate records that rather than inventing a verdict for them
- The gate checks declared fields against the wave contract. It does not re-disassemble any module, so a symbol name reported by 1157A or 1158A is checked for presence and not for truth.
- ath10k_fabricated_offsets counts offsets that fall outside the measured byte length of the module they claim to address. An offset inside the file that addresses the wrong instruction passes this check and is not caught here.
- Coverage and condition_confirmed are measurements. The gate bounds coverage to [0, 1] and admits either value of condition_confirmed, then requires the receipt to declare a gap when the zero is real.
- Receipt fields are located by exact key, so a lane that renames a contract field is reported as a missing field rather than mapped to an approximate name.

## Reproduce

```
python tools/verify/verify_stage1162a_wave21_opencode_gate.py
python -m pytest tests/test_stage1157a_to_1162a_suite.py -q
```

