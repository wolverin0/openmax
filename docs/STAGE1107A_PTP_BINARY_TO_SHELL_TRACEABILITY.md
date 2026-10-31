<!-- doc-head: Stage 1107A builds the PtP binary-to-shell traceability matrix across 1031A..1106A, sourcing ath10k from the tar members in EXTRACTION.json rather than a loose-.ko sweep, and reporting coverage as a measurement; CONFIRMED_STATIC_BINARY, static only -->
<!-- /doc-head -->
# Stage 1107A - PtP binary-to-shell traceability matrix

Evidence class: `CONFIRMED_STATIC_BINARY`. `radio_safety: static only`.
Scope: static only; offline correlation of the 1103A..1106A receipts with the 1031A and 1059A supporting receipts, the v17 kit script text and the ath10k tar extraction manifest, no module loaded, no kit executed, no radio contacted

- **Receipt**: [`artifacts/autoresearch/stage1107a_ptp_binary_to_shell_traceability.json`](../artifacts/autoresearch/stage1107a_ptp_binary_to_shell_traceability.json)
- **Tool**: [`tools/verify/build_stage1107a_ptp_binary_to_shell_traceability.py`](../tools/verify/build_stage1107a_ptp_binary_to_shell_traceability.py)

## Question

A debugfs write literal found inside a kernel object proves a parser exists. It does not prove the
kit writes it. This stage measures the gap: for every artefact a binary dissection recovered, is the
same token present in the shell layer that is permitted to write it.

## Sweep scope, stated before any absence

tar-inclusive and loose-file inclusive: artifacts/firmware_re_ath10k_tar/EXTRACTION.json members taken from artifacts/verification/stage117a_build/stock.tar (./lib/modules/6.6.110/ath10k_core.ko, ./lib/modules/6.6.110/ath10k_pci.ko, ./lib/firmware/ath10k/QCA988X/hw2.0/board.bin), every artifacts/autoresearch/stageNNNNa_*.json receipt in 1031..1106, every firmware/openwrt/**/fmx_*_v17_*kit.sh script, and every docs/STAGE*.md stage doc. No absence claim in this receipt rests on a loose-.ko-only sweep, because the earlier loose-.ko-only sweep reported ath10k absent while 72 copies sat inside tars

## Matrix

| stage span | stages | receipts found | receipts expected | missing receipts |
| :--- | :--- | :--- | :--- | :--- |
| 1031A..1106A | 76 | 76 | 76 | none |

| family | rows | traced |
| :--- | :--- | :--- |
| `ath10k_offset` | 56 | 0 |
| `dictionary_write_syntax` | 8 | 5 |
| `kit_write` | 10 | 7 |
| `mac80211_format` | 4 | 0 |
| `mac80211_handler` | 3 | 0 |
| `sysfs_path` | 6 | 0 |

`matrix_rows` = 87, `traced_binary_to_shell` = 12,
`coverage_measured` = 0.137931.

The coverage figure is `traced / matrix_rows` and is a measurement, not a target. This stage does
not require the corpus to trace cleanly, and it does not require any kit to be flawless.

### Traced rows, first 12

| row | family | binary token | traced |
| :--- | :--- | :--- | :--- |
| `1059A:dictionary:aql_txq_limit:%u %u %u` | `dictionary_write_syntax` | `%u %u %u` | 1 |
| `1059A:dictionary:aql_txq_limit:mcast %u` | `dictionary_write_syntax` | `mcast %u` | 1 |
| `1059A:dictionary:aqm:fq_limit %u` | `dictionary_write_syntax` | `fq_limit %u` | 1 |
| `1059A:dictionary:aqm:fq_memory_limit %u` | `dictionary_write_syntax` | `fq_memory_limit %u` | 1 |
| `1059A:dictionary:aqm:fq_quantum %u` | `dictionary_write_syntax` | `fq_quantum %u` | 1 |
| `1105A:kit_write:aql_txq_limit:0 500 1000` | `kit_write` | `0 500 1000` | 1 |
| `1105A:kit_write:aql_txq_limit:1 1500 3000` | `kit_write` | `1 1500 3000` | 1 |
| `1105A:kit_write:aql_txq_limit:2 3000 6000` | `kit_write` | `2 3000 6000` | 1 |
| `1105A:kit_write:aql_txq_limit:3 1500 3000` | `kit_write` | `3 1500 3000` | 1 |
| `1105A:kit_write:aqm:fq_limit 2048` | `kit_write` | `fq_limit 2048` | 1 |
| `1105A:kit_write:aqm:fq_memory_limit 4194304` | `kit_write` | `fq_memory_limit 4194304` | 1 |
| `1105A:kit_write:aqm:fq_quantum 1514` | `kit_write` | `fq_quantum 1514` | 1 |

### Untraced

75 rows, first ten: `1103A:ce_ring_symbols:_0`, `1103A:ce_ring_symbols:_1`, `1103A:ce_ring_symbols:_21`, `1103A:ce_ring_symbols:_22`, `1103A:ce_ring_symbols:_23`, `1103A:ce_ring_symbols:_24`, `1103A:ce_ring_symbols:_25`, `1103A:ce_ring_symbols:_26`, `1103A:ce_ring_symbols:_27`, `1103A:ce_ring_symbols:_28`

## Wave fields consumed

| stage | field | value |
| :--- | :--- | :--- |
| 1103A | `core_bytes` | 600808 |
| 1103A | `pci_bytes` | 56648 |
| 1103A | `offsets_recovered` | 56 |
| 1104A | `format_strings` | 4 |
| 1104A | `handler_offsets` | 5 |
| 1105A | `writes_total` | 20 |
| 1105A | `valid_writes` / `invalid_writes` | 18 / 0 |
| 1105A | `evidence_stage` | 1031A (CONFIRMED_STATIC_BINARY, mac80211.ko relocation and rodata analysis); 1104A present at generation time and cited for its handler inventory of airtime_flags, aql_enable and aql_pending, which these kits do not write |
| 1106A | `unique_paths` | 6 |
| 1106A | `path_form_valid` | 5 |
| 1106A | `iptv_1316b_attributable` | 1 |

## ath10k provenance

tar_member:./lib/modules/6.6.110/ath10k_core.ko (600808 B, sha256 d7f2d1ac07a6c91fe4284eac37bbe92e822b276a59928946ff86cb9da00ddf84) and tar_member:./lib/modules/6.6.110/ath10k_pci.ko (56648 B, sha256 11bc8d7a4ee1f98c8d72b68f5bb43150bd36186ceed78e5f4400fb3cab26cd66) extracted from stock.tar into artifacts/firmware_re_ath10k_tar/ per artifacts/firmware_re_ath10k_tar/EXTRACTION.json

Stage 1056A reported `ath10k_core_present: 0` after scanning 1,169 loose `.ko` files. That sweep
scope is the defect this matrix must not repeat: 72 ath10k copies were later found inside tar
members. No row here asserts ath10k absence, and the rows that exist cite the tar member path.

## Gaps

- The matrix is assembled from receipt fields, not by re-running the dissections. A wrong offset or a wrong format literal that 1103A and 1104A report consistently is carried into the matrix unchanged; only the arithmetic and the citations are re-checked here.
- A row is traced when the binary-side token is found in the shell layer. Absence of a token is measured as untraced, which is not proof that no shell line writes that knob: the kits may reach the same value through a variable, a loop or a helper whose text never repeats the literal.
- 1105A and 1106A row extraction is schema-tolerant. The builder looks for dicts that carry both a target-shaped key and a syntax-shaped key, and for a unique_paths list. A wave receipt that stores its writes under unrecognised key names contributes fewer rows, so matrix_rows is a lower bound on the traceable population rather than a census.
- Format-literal traces use exact normalised string equality, never substring search. Two conversions such as %u and %u\n are short enough that substring matching would report a trace for almost any script. The strict rule under-reports traces, which is the safe direction, and it never invents one.
- A conversion literal that reappears in a kit is a token match, not proof that the kit writes the debugfs node that owns the literal. The dictionary_write_syntax family is the only family that binds a literal to a file the script actually names, and it is reported separately for that reason.
- ath10k offsets are attributed from artifacts/firmware_re_ath10k_tar/EXTRACTION.json and the 1103A receipt. This stage does not re-dissect the module and does not prove that any offset is a live HTT handler; a recovered offset is a static address claim only.
- The four stages 1044A..1047A are live bench stages whose receipts live outside artifacts/autoresearch. They are counted in stages_in_matrix because the span includes them, and they are named in receipts_missing because no receipt file of that shape exists here.
- No dynamic validation: no module was loaded, no debugfs node was opened, no kit was executed, no radio or host was contacted.

## Claim boundary

The matrix records which binary-side tokens reappear in the shell layer. It does not prove that any
kit line is correct, that any value is safe, or that any traced write reaches a radio. No module was
loaded, no kit was run, no device was contacted.
