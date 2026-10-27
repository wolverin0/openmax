<!-- doc-head: Stage 901A - the thirty-one receipts that declared no provenance now carry an explicit class, a timestamp and the original digest, determined by curation rather than by pattern, with fourteen live nine static and eight modelled, and every file provably restorable to the hash it had before the edit -->
# Stage 901A — in-place provenance remediation of 31 receipts

- **Receipt**: [`artifacts/autoresearch/stage901a_provenance_remediation_receipt.json`](../artifacts/autoresearch/stage901a_provenance_remediation_receipt.json)
- **Tool**: [`tools/verify/remediate_stage901a_undeclared_provenance_receipts.py`](../tools/verify/remediate_stage901a_undeclared_provenance_receipts.py)
- **Source list**: Stage 895A `provenance_undeclared`
- **Scope**: edits JSON receipts in place. No binary written, no firmware touched, no radio contacted.

## 0. Result

```
targets=31 flagged=0 discovered=31 remediated_this_run=0 total=31 correct=31
live=14 static=9 sim=8 ambiguous=0 restored=1 idempotent=1 failed=0
```

All **31** carry `evidence_provenance_class` and none is ambiguous. On the first pass 11 of them were
**repaired**, having been given a wrong class by the pattern engine; the line above is the steady state
of a re-run.

## 0.1 Idempotency, and why it needed code

A remediation tool that reads its target list from an audit **destroys its own input**. Once the fields
exist, Stage 895A reports `provenance_undeclared = 0`, so a second run found nothing and shipped
`targets = 0`.

The population is now the **union** of the original flag list and every receipt whose
`post_audit_reclassified_at` and `preserved_raw_sha256` are both truthy. On a re-run the tool therefore
reports the same **31** targets with `remediated_this_run = 0`, `remediated_total = 31` and
`idempotent_rerun = 1`, which is what makes the receipt stable across runs.

## 1. "Without altering raw hashes", made precise

Adding a field necessarily changes the file hash. What can be guaranteed, and is, is **restorability**:

```
sha256( file with the inserted span removed ) == sha256( original file )
```

The edit is **textual**: four fields are inserted immediately after the first `{`, and the original
bytes are untouched after the insertion point. Re-serialising the JSON would have discarded formatting
and made the original digest unrecoverable.

The original digest is embedded in each file as `preserved_raw_sha256`, so the property can be checked
from the file alone, without this receipt. Stage 903A does exactly that independently.

| Field added | Purpose |
| :--- | :--- |
| `evidence_provenance_class` | one of the three allowed labels |
| `post_audit_reclassified_at` | fixed audit timestamp |
| `preserved_raw_sha256` | digest of the file before remediation |
| `post_audit_remediation_source` | `stage901a` |

## 2. The pattern engine failed, and that is why the table is curated

The first version classified by matching patterns over every nested key. It produced **thirteen false
positives**:

| Cited key | Why it is not hardware evidence |
| :--- | :--- |
| `safety.zero_jargon_verified` | a documentation-style check |
| `five_pillar_compliance.pillar_e_memory_master` | a compliance block |
| `stage532a_athstats_audit.struct_size_bytes` | a struct size, static by nature |
| `v9_detectors...wmi_param` | a detector definition |

Broad substrings such as `verified`, `windows` and `rssi` matched **metadata** rather than
measurements. The engine was replaced by a **curated table of 31 entries**, each naming a citation key
that **must exist** in the receipt. The tool verifies the citation before writing, so a wrong curation
fails loudly instead of shipping.

## 3. The distribution, and the caveat on the third label

| Class | Count | Basis |
| :--- | :-: | :--- |
| CONFIRMED_LIVE_HARDWARE | **14** | readbacks, `iw dev` excerpts, live-window counters, per-device caches, measurement payloads |
| CONFIRMED_STATIC_BINARY | **9** | hashes, symbols, patch profiles, struct inventories |
| SIMULATED_MODEL_ONLY | **8** | engines, playbooks, publications and summaries with no measurement and no binary evidence |

**The caveat, carried in every row as `provenance_basis`**: the third label is used as *"no primary
measurement and no binary evidence"*, which is **narrower** than "a simulation". A publication quoting
champion numbers and an engine defining detectors both land there, and the basis field says which one.

## 4. The finding that shaped the rules

**`live_devices_touched` is `False` on receipts whose filenames say `live` and whose payloads contain
`iw dev` excerpts** — for example `stage584a_live_pbe5ac_vht80_clean_assoc_and_qpsk_sweep`.

So the field is **not usable as evidence**. This is worse than a missing field: a consumer that trusted
it would have concluded that measured receipts were not measured. Classification therefore uses the
payload, not the flag.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| 31 receipts now declare a class | **CONFIRMED** (31 of 31) |
| zero remain ambiguous | **CONFIRMED** |
| every file is restorable to its original digest | **CONFIRMED** (31 of 31) |
| the original digest is recoverable from the file itself | **CONFIRMED** (`preserved_raw_sha256`) |
| the first classification was correct | **REFUTED** (11 repaired) |
| `live_devices_touched` is reliable | **REFUTED** |

## 6. Gaps

- **`UNKNOWN`** — whether the recorded class matches what the receipt's author intended.
- **`UNKNOWN`** — whether prose receipts cited the numbers they claim.
- **Known limit** — curation covers exactly these 31; a new undeclared receipt needs a new entry.
- **Known limit** — the class states the evidence present, not the correctness of the conclusion.
- **Not attempted** — re-execution of any receipt, dynamic validation.
