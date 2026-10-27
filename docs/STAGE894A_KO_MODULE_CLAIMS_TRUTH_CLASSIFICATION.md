<!-- doc-head: Stage 894A - of the 258 kernel-module receipts fourteen modules are tracked and eight carry live evidence, with only ath_hal and ath_spectral at zero live receipts, while ubnt_poll_host shows ten live against forty-two static and twenty receipts declare no provenance at all -->
# Stage 894A — kernel-module claims truth classification

- **Receipt**: [`artifacts/autoresearch/stage894a_ko_module_claims_truth_classification.json`](../artifacts/autoresearch/stage894a_ko_module_claims_truth_classification.json)
- **Tool**: [`tools/re/dissect_stage894a_ko_module_claims_truth_classification.py`](../tools/re/dissect_stage894a_ko_module_claims_truth_classification.py)
- **Audit reference**: sections A09 and A10
- **Scope**: offline static. Reads receipts only. No module loaded, no radio contacted.

## 0. The counts

```
receipts=258 modules=14 with_live=8 live=42 static=163 sim=31 refuted=2 undeclared=20
```

| Label | Count |
| :--- | :-: |
| CONFIRMED_LIVE_HARDWARE | **42** |
| CONFIRMED_STATIC_BINARY | **163** |
| SIMULATED_MODEL_ONLY | **31** |
| REFUTED | **2** |
| provenance undeclared | **20** |

The same five rules as Stage 893A, applied to the module subset, plus a per-module distribution.

## 1. Per module

| Module | Receipts | live | static | sim | live fraction |
| :--- | :-: | :-: | :-: | :-: | :-: |
| `ath10k` | 172 | 39 | 96 | 22 | 0.2267 |
| `mac80211` | 157 | 38 | 92 | 18 | 0.2420 |
| `umac` | 83 | 25 | 51 | 6 | 0.3012 |
| `ame_core` | 74 | 8 | 54 | 8 | 0.1081 |
| `ubnt_poll_host` | 68 | 10 | 42 | 11 | 0.1471 |
| `ath_dev` | 56 | 10 | 37 | 7 | 0.1786 |
| `eab_driver` | 45 | 10 | 29 | 5 | 0.2222 |
| `ame_dev` | 28 | 1 | 23 | 1 | 0.0357 |
| **`ath_hal`** | 11 | **0** | 9 | 1 | **0.0** |
| **`ath_spectral`** | 5 | **0** | 5 | 0 | **0.0** |

**`CONFIRMED`**: `modules_with_live_evidence = 8` of 14.

Only **two** modules have zero live receipts, and both are small ones: `ath_hal` with 11 and
`ath_spectral` with 5. The claim "the busy modules were never measured" would be **false**.

## 2. The correction this table forced on its own first draft

My first draft of this document asserted that `ubnt_poll_host` and `ath_dev` had **zero** live receipts,
and that every claim about them was therefore static. That was **`REFUTED`** by the final run: both show
**10** live receipts, at fractions 0.1471 and 0.1786.

The cause was a rule change, not a corpus change. Widening R1 to recognise live campaign counters
(`*windows*`) and declared `hardware_pair` values converted **25 receipts** from static to live, which
moved four modules off zero at once.

The lesson is worth keeping: **a per-module table is only valid for the rule set that produced it.** The
document was rewritten after the rule was finalised, and the numbers here match the receipt.

## 3. Why a per-module fraction is not a per-claim provenance

**`REFUTED`**: a live fraction of 0.2267 for `ath10k` does **not** mean 22.67 % of ath10k claims are
live. It means 22.67 % of the **receipts that mention ath10k** are live. A single live receipt that
mentions a module in passing counts fully, and a static receipt that draws forty conclusions counts once.

The fraction is a **corpus shape**, not a claim-level confidence. Using it as a weight would be a
category error.

## 4. The residual

**`CONFIRMED`**: `provenance_undeclared = 20`, listed by name in the receipt.

These receipts mention a module and declare no live marker, no simulation marker, no binary descriptor
and no verification block. They are citable as **nothing**, which is the point.

`fail_closed = 1` asserts structural completeness: 258 rows, one label each, tallies summing.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| 258 module receipts fall in Stage 500A..878A | **CONFIRMED** |
| 14 modules are tracked | **CONFIRMED** |
| 8 modules carry live evidence | **CONFIRMED** |
| `ath_hal` has zero live receipts | **CONFIRMED** (0 of 11) |
| `ath_spectral` has zero live receipts | **CONFIRMED** (0 of 5) |
| `ubnt_poll_host` has zero live receipts | **REFUTED** (10 of 68) |
| `ath_dev` has zero live receipts | **REFUTED** (10 of 56) |
| 20 receipts declare no provenance | **CONFIRMED**, listed by name |
| a live fraction is a claim-level confidence | **REFUTED** |

## 6. The operational reading

1. **Separate static from live per module before quoting.** `ame_dev` at 0.0357 and `ubnt_poll_host` at
   0.1471 are mostly static, and a sentence presenting their findings as measurements is a provenance
   error.
2. **Do not weight findings by the fraction.** It describes the corpus, not the claim.
3. **Check the fraction against the rule set that produced it.** This stage's own draft failed that test
   and the table here is the corrected version.

## 7. Gaps

- **`UNKNOWN`** — whether the 20 undeclared receipts are static or documentary.
- **`UNKNOWN`** — correctness of any individual module claim.
- **Known limit** — attribution comes from string presence, so a receipt that mentions a module only as
  a counter-example is still counted against it.
- **Known limit** — the live fraction moves with the rule set, as section 2 documents.
- **Not attempted** — loading any module, any dynamic validation.
