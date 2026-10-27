<!-- doc-head: Stage 903A - all thirty-one remediated receipts verify independently, each one restorable to its pre-edit digest by removing the inserted span, with fourteen live nine static and eight modelled agreeing exactly with the remediation receipt -->
# Stage 903A — restoration registry

- **Receipt**: [`artifacts/autoresearch/stage903a_provenance_restoration_registry.json`](../artifacts/autoresearch/stage903a_provenance_restoration_registry.json)
- **Tool**: [`tools/verify/verify_stage903a_provenance_restoration_registry.py`](../tools/verify/verify_stage903a_provenance_restoration_registry.py)
- **Scope**: read-only verification of the receipts remediated by Stage 901A.

## 0. Result

```
receipts=31 verified=31 restored=31 class_valid=31
live=14 static=9 sim=8 all_restored=1
```

All **31** pass every check, and the class counts agree **exactly** with Stage 901A: 14 live, 9 static,
8 modelled.

## 1. The verification is independent of Stage 901A

The check re-derives everything from the file itself:

1. read the file;
2. find the inserted span, from `evidence_provenance_class` to `post_audit_remediation_source`;
3. remove it;
4. hash the remainder;
5. compare with `preserved_raw_sha256`, **stored inside the file**.

**`CONFIRMED`**: `restoration_verified = 31 / 31`.

Because the expected digest lives in the file, the claim survives the loss of the Stage 901A receipt, of
this registry, and of the tool. A reader with one file can check it with a text editor and `sha256sum`.

## 2. What the registry records per receipt

| Field | Meaning |
| :--- | :--- |
| `observed_class` | the class written into the file |
| `class_valid` | it is one of the three declared labels |
| `preserved_present` | the original digest is stored |
| `recomputed_original_sha256` | hash of the file minus the inserted span |
| `restoration_verified` | that hash equals the stored digest |
| `inserted_field_count` | how many of the four fields are present |
| `citation` | the key that justified the class |
| `provenance_basis` | why that key counts as evidence |

**`CONFIRMED`**: `inserted_field_count = 4` for all 31 — no partial write, no truncated insertion.

## 3. Why a registry instead of a boolean

A single `restored: true` would say nothing about **which** file failed when one does. The registry
carries one row per receipt with the recomputed digest, so a future edit to any of the 31 shows up as a
specific row whose two hashes diverge, not as a global false.

That is also the failure mode worth naming: **editing a remediated receipt invalidates its restoration
record**, because the stored digest describes the file as it was at remediation time. Any later change
must either re-run Stage 901A or record that the restoration guarantee no longer applies.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| all 31 carry the four fields | **CONFIRMED** |
| all 31 restore to their original digest | **CONFIRMED** (31 of 31) |
| all 31 carry a valid class | **CONFIRMED** |
| the class counts match Stage 901A | **CONFIRMED** (14 / 9 / 8) |
| restoration proves the file was correct before remediation | **REFUTED** |

## 5. Gaps

- **`UNKNOWN`** — whether the pre-remediation content was itself correct.
- **`UNKNOWN`** — whether any of the 31 was edited after remediation; the registry would show it, but
  this run found none.
- **Known limit** — the registry covers exactly 31 receipts, not the 176 still undeclared.
- **Not attempted** — re-execution of any receipt, dynamic validation.
