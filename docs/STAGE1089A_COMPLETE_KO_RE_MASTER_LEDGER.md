<!-- doc-head: Stage 1089A complete .ko reverse-engineering master ledger 917A..1088A, static offline measurement of receipts and module filenames -->

# Stage 1089A - Complete .ko RE Master Ledger (917A..1088A)

Static, offline. No module was loaded, executed or decompiled. The ledger counts receipts,
stage numbers and module filenames, and publishes the arithmetic behind each number.

## Measured headline

| Measure | Value |
| :--- | ---: |
| Receipts in the frozen window | 161 |
| Distinct stage numbers | 154 |
| Duplicated stage numbers | 7 |
| Receipts restating ath10k absence | 11 |
| Modules named ath10k | 2 |
| .ko files in the corpus | 1171 |
| .ko files covered by a receipt | 946 |
| Measured coverage | 0.807857 |
| Gaps listed | 12 |

Coverage is reported as measured and is not full. A ledger that reported 1.0 over this
corpus would be describing a corpus that does not exist on disk.

## The seven duplicated stage numbers

| Stage | Receipts |
| :--- | :--- |
| 944A | `stage944a_roadmap_untested_variables_prioritizer.json` | `stage944a_seed_determinism_reproducibility_audit.json` |
| 945A | `stage945a_empirical_retest_backlog_matrix.json` | `stage945a_pytest_execution_time_audit.json` |
| 949A | `stage949a_ath10k_htt_tx_re.json` | `stage949a_itxq_ath10k_interaction_re.json` |
| 950A | `stage950a_mac80211_aql_txq_limit_re.json` | `stage950a_ubnt_poll_host_queues_re.json` |
| 951A | `stage951a_itxq_aql_interaction_re.json` | `stage951a_ubnt_poll_vs_mac80211_itxq_re.json` |
| 1024A | `stage1024a_live_busybox_triple_play_and_aqm_gate.json` | `stage1024a_live_powerbeam_gatekeeper_verification.json` |
| 1069A | `stage1069a_historical_receipt_pillar_annotations.json` | `stage1069a_stage1001a_to_1042a_receipts_and_docs.json` |

Each collision is two different receipts under one stage number. Downstream indexes that
key on stage number alone will drop one of each pair, so both filenames are published
rather than resolved to a single winner.

## Declared provenance

| Declared class | Receipts |
| :--- | ---: |
| `ABSENT` | 77 |
| `CONFIRMED_LIVE_HARDWARE` | 17 |
| `CONFIRMED_STATIC_BINARY` | 54 |
| `EVIDENCE_RECONCILIATION_ONLY` | 5 |
| `OFFLINE_PLAN_AND_SAVED_NATIVE_REPLAY` | 3 |
| `OFFLINE_SAVED_NATIVE_EVIDENCE_REPLAY` | 1 |
| `STATIC_BINARY_CROSS_VERSION_RECONCILIATION_GATE` | 1 |
| `STATIC_OFFLINE_RECEIPT_CROSS_CHECK` | 1 |
| `STATIC_SOURCE_AND_SAVED_RECEIPTS` | 1 |
| `UNKNOWN_NOT_ACQUIRED` | 1 |

77 receipts declare no provenance class at all. They
are counted as absent, not as confirmed, so the distribution above is a statement about
declarations rather than about evidence quality. Class names are reproduced exactly as
declared; the keys of summary.provenance_counts are lower-cased by the normaliser.

## The ath10k absence

The corpus holds 1171 loose `.ko` files. None of them is named ath10k.
Nineteen stages confirmed that over loose files. Stage 1087A then refuted the
generalisation: ath10k_core.ko ships as a 600,808-byte member of local tar archives,
which a loose-file census cannot see. The ledger therefore reports absence as a
measurement over 1171 loose files and not as a property of the system. The
window holds 11 receipts that restate the absence as a zero-valued
ath10k field, which is a count of restatements and not of searches.

## Module coverage

946 of 1171 files are named by an analytical receipt, resting on
199 distinct basenames of 257. The strict relative-path measure is
123 files, because a basename covers every copy of a module across
firmware trees. The atlas receipt that enumerates every path is excluded from the scan:
an enumerator that mentions all 1,169 files would otherwise report full coverage for free.

The remaining 225 files are a gap. They are named at basename level
only; the ledger does not read their headers, hash them, or test whether a receipt refers
to them by a path the token scan misses.

## The frozen window

Two other agents were writing receipts into `artifacts/autoresearch` while this ledger was
built, so a live count would have changed between runs and no gate could agree with it.
Membership is therefore an explicit `(stage, filename)` manifest pinned as data, and every
receipt that appeared after the freeze is named instead of being silently merged.

- Post-freeze receipts named: 16
- Frozen receipts missing from disk: 0
- Manifest digest: `1a22ac6dadadeccc0b2c3241bcb6cc65`

## What is not claimed

The ledger does not claim full coverage, does not claim that any receipt is true, and does
not claim that the 225 unnamed modules were never analysed. It claims only what the
arithmetic shows: 161 receipts, 154 distinct stage numbers, 7 collisions,
946 covered files, measured coverage 0.807857, and an absence
of ath10k that was measured rather than assumed.

## Reproduce

```
python tools/verify/build_stage1089a_complete_ko_re_master_ledger.py
python -m pytest tests/test_stage1085a_to_1090a_suite.py -q
```
