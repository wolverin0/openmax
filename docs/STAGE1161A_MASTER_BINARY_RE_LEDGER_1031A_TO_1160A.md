<!-- doc-head: Stage 1161A master binary RE ledger 1031A..1160A, static offline census of both receipt roots with measured stage coverage and recorded corpus facts -->

# Stage 1161A - Master Binary RE Ledger (1031A..1160A)

Static and offline. No module was loaded, executed or decompiled, and no radio was
contacted. The ledger counts receipts, stage numbers, declared provenance classes and
binary filenames, and publishes the arithmetic behind every number.

## Measured headline

| Measure | Value |
| :--- | ---: |
| Stage numbers in scope | 130 |
| Stages carrying a receipt | 123 |
| Stages missing a receipt | 7 |
| Matrix rows | 130 |
| Distinct binary artefacts cited | 61 |
| Measured stage coverage | 0.946154 |
| Gaps listed | 11 |
| Declares full coverage | False |

Coverage is a measurement and it is below 1.0. Wave 18 never ran, so a ledger that
printed 1.0 over this window would be describing a window that does not exist.

## Where the receipts live

| Root | In-window files | In-window stages | Auxiliary files |
| :--- | ---: | ---: | ---: |
| `artifacts/verification` | 21 | 21 | 0 |
| `artifacts/autoresearch` | 105 | 102 | 2 |

The two roots are both scanned and every matrix row carries the root it was read from.
A stage that appeared in both roots would be read from `artifacts/verification` first,
because that is where the late stages of this wave wrote.

The table counts stage files inside the window, not JSON files in the directory. A raw
directory count would move every time a neighbouring lane wrote a receipt for a stage
outside 1031..1160, and a ledger whose bytes move whenever a neighbour writes is a ledger
that no gate can agree with.

## The four wave receipts

| Stage | Root | Receipt | Bytes | Parsed |
| :--- | :--- | :--- | ---: | :--- |
| 1157A | `artifacts/verification` | `stage1157a_ath10k_htt_txrx_airtime_re.json` | 67179 | True |
| 1158A | `artifacts/verification` | `stage1158a_mac80211_aql_threshold_may_transmit_re.json` | 83428 | True |
| 1159A | `artifacts/verification` | `stage1159a_uph_allow_80211_hybrid_ota_re.json` | 109096 | True |
| 1160A | `artifacts/verification` | `stage1160a_ltu_ame_passive_safe_paths_re.json` | 328872 | True |

## ath10k provenance

`ath10k_core.ko` is a 600808-byte tar member at `./lib/modules/6.6.110/ath10k_core.ko` and `ath10k_pci.ko`
is a 56648-byte tar member at `./lib/modules/6.6.110/ath10k_pci.ko`. Each exists in
72 copies inside the local tar corpus, and neither exists as a loose
file. The extracted copies are re-measured here rather than trusted:

- core on disk: 600808 B, sha256 `d7f2d1ac07a6c91f`
- pci on disk: 56648 B, sha256 `11bc8d7a4ee1f98c`
- recorded sizes agree with the copies on disk: True

The size and copy counts are recorded from the 1157A..1160A lane, not re-derived. Only
the extracted bytes are re-measured, so this ledger corroborates two numbers and carries
the rest as a citation.

## Corpus facts recorded, not re-derived

| Fact | Value | Source |
| :--- | :--- | :--- |
| ath10k_core.ko exists as a tar member | bytes=600808, copies=72, member=./lib/modules/6.6.110/ath10k_core.ko | wave 1157A..1160A lane |
| ath10k_pci.ko exists as a tar member | bytes=56648, copies=72, member=./lib/modules/6.6.110/ath10k_pci.ko | wave 1157A..1160A lane |
| eab_driver.ko is absent from the corpus | loose=0, tar_members=0, tars_searched=114 | wave 1157A..1160A lane |
| LTU 2.3.1 is absent | absent=LTU 2.3.1, present=LTU 2.4.2 | wave 1157A..1160A lane |
| airOS 8.7.15 is absent | absent=airOS 8.7.15, present=['8.7.11', '8.7.25'] | wave 1157A..1160A lane |
| airOS 8.7.11 contributes 4 modules | modules=4 | wave 1157A..1160A lane |
| airOS 8.7.25 contributes full trees | trees=full | wave 1157A..1160A lane |

## Version inventory

- available labels: `["airOS 8.7.11", "airOS 8.7.25", "LTU 2.4.2"]`
- absent labels: `["airOS 8.7.15", "LTU 2.3.1"]`
- available as an object, keys lower-cased by the normaliser: `{"airos": ["8.7.11", "8.7.25"], "ltu": ["2.4.2"]}`

Absence here is label absence. A vendor build carrying the same version under a
different directory name would not be seen by this census.

## Coverage

`coverage_measured = 123 / 130 = 0.946154`, computed only as `stages carrying a receipt / stage numbers in 1031..1160`.
The 7 missing stages are `["1139A", "1140A", "1141A", "1142A", "1143A", "1144A", "1155A"]`.
Wave 18 never ran, and 1155A is a Spanish decision summary with a doc and no receipt.
Both facts are gaps in this ledger and neither is repaired by rounding.

## Gaps

- coverage_measured is stage coverage, the ratio of stages in 1031..1160 that carry a receipt. It is not coverage of the binary surface, not coverage of the 571-knob catalog, and not a statement that any receipt is true.
- A receipt that exists and cannot be parsed is counted as found and named as unreadable. The ledger fails closed on its own arithmetic, not on a foreign lane's JSON defect.
- Provenance counts read whatever evidence_provenance_class a receipt declares. The ledger does not re-audit those declarations, so a receipt that overstates its class is carried at the class it claims.
- The ath10k sizes and the 72-copies-per-module count are recorded from the 1157A..1160A lane rather than re-derived here. Only the extracted copy on disk is re-measured, and only its byte length and sha256 are corroborated.
- eab_driver.ko absence is measured over loose files and 114 tar archives. It is not evidence about squashfs images, firmware containers, or any tree that those 114 archives do not contain.
- airOS 8.7.15 and LTU 2.3.1 are absent as labels. A vendor build carrying the same version under a different directory name would not be seen by a label census.
- Auxiliary receipts whose filename begins with an underscore are listed but excluded from canonical selection, because they are before-snapshots and not stage verdicts.
- No stage in this window read a live radio. Every row is static, and the ledger neither confirms nor denies any field measurement recorded elsewhere in the repository.
- Stage coverage arithmetic: 123 stages carry a receipt of 130 in scope, so coverage_measured is 0.946154 and 7 stages are missing (['1139A', '1140A', '1141A', '1142A', '1143A', '1144A', '1155A']).
- 0 in-window receipts could not be parsed and are named rather than treated as evidence ([]).
- Wave receipt roots: [('1157A', 'artifacts/verification'), ('1158A', 'artifacts/verification'), ('1159A', 'artifacts/verification'), ('1160A', 'artifacts/verification')] - a stage that appears in both roots would be read from artifacts/verification first.

## What is not claimed

The ledger does not claim full coverage, does not claim that any receipt is true, and
does not claim that the missing stages have no analysis elsewhere. It claims only what
the arithmetic shows: 123 of 130 stages carry a receipt, 61 distinct binary artefacts are cited, and
the ath10k members are cited by tar path with their measured sizes.

## Reproduce

```
python tools/verify/verify_all_opencode_binary_re_stages_1031a_to_1160a.py
python -m pytest tests/test_stage1157a_to_1162a_suite.py -q
```

