<!-- doc-head: Stage 895A - the consolidated truth table covers all 333 receipts from Stage 500A to Stage 878A with sixty-six live, one hundred eighty-six static, forty-five simulation, five refuted and thirty-one undeclared, zero disagreements against the two subset stages, and zero of the seven patch gates reaching runtime -->
# Stage 895A — consolidated truth table and promotion rules

- **Receipt**: [`artifacts/autoresearch/stage895a_ko_module_claims_truth_table.json`](../artifacts/autoresearch/stage895a_ko_module_claims_truth_table.json)
- **Tool**: [`tools/verify/build_stage895a_ko_module_claims_truth_table.py`](../tools/verify/build_stage895a_ko_module_claims_truth_table.py)
- **Audit reference**: sections A09 and A10
- **Scope**: offline static. Reads receipts only.

## 0. The table

```
receipts=333 live=66 static=186 sim=45 refuted=5 undeclared=31
citable=302 tiers={binary_bytes:109, artefact_structure:168, none:56}
disagreements=0 gates=7 runtime=0 structural=1
```

| Label | Count | Share |
| :--- | :-: | :-: |
| CONFIRMED_LIVE_HARDWARE | **66** | 19.8 % |
| CONFIRMED_STATIC_BINARY | **186** | 55.9 % |
| SIMULATED_MODEL_ONLY | **45** | 13.5 % |
| REFUTED | **5** | 1.5 % |
| provenance undeclared | **31** | 9.3 % |

This stage re-classifies **every** receipt independently and then compares its labels against Stages
893A and 894A on the subset they cover.

**`CONFIRMED`**: `classifier_disagreements = 0`. Three implementations of the same five rules, written
in three files, agree on every shared receipt. If they had diverged, that would have been a defect in
the rules rather than a difference of opinion.

## 1. The three tiers

| Tier | Rows | Meaning |
| :--- | :-: | :--- |
| `binary_bytes` | **109** | scope declares offline static, or binary descriptors are present |
| `artefact_structure` | **168** | verification blocks only, no binary descriptor |
| `none` | **56** | not static: live, simulation or refuted |

**`CONFIRMED`**: the majority of the static mass, **168 of 186**, rests on **structural verification**
rather than on binary byte descriptors. That is a materially weaker tier than a hash or a symbol table,
and it is reported separately for exactly that reason.

A reader who needs byte-level provenance should filter to `binary_bytes`, which is **109** rows, not
186.

## 2. The promotion rules

| From | May be cited as | Never as |
| :--- | :--- | :--- |
| CONFIRMED_LIVE_HARDWARE | measured behaviour on the named target | a mechanism's internal design |
| CONFIRMED_STATIC_BINARY | binary content, layout, symbol or vocabulary | runtime behaviour or on-air effect |
| SIMULATED_MODEL_ONLY | a model, a scenario, a planning input | any measurement, any hardware claim |
| REFUTED | an absent name, a blocked gate, a negative result | evidence that the opposite is true |
| UNCLASSIFIED | **nothing** | anything |

The last row carries the discipline. An undeclared receipt can be cited as **nothing** until it declares
itself, and the table lists all **31** by name so that fix is actionable.

Two consequences worth stating plainly:

- **PB-040..PB-100 are proven at container level and pending execution.** They are
  `CONFIRMED_STATIC_BINARY` for their containers and **not** runtime evidence, because no `dmesg` and no
  `debugfs` witness exists in the range.
- **No champion may be cited as hardware-measured on the strength of a simulation row.** Forty-five
  receipts are model output, and they carry status words just like the binary ones.

## 3. The gate column

**`CONFIRMED`**: `gates_audited = 7`, `gates_runtime_proven = 0`,
`patches_pending_live_execution = 7`.

| Gate | Static | On target | Runtime |
| :--- | :-: | :-: | :-: |
| PB-040 | 1 | 1 | **0** |
| PB-050 | 1 | 1 | **0** |
| PB-060 | 1 | 0 | **0** |
| PB-070 | 0 | 0 | **0** |
| PB-080 | 0 | 0 | **0** |
| PB-090 | 0 | 0 | **0** |
| PB-100 | 0 | 0 | **0** |

Seven gates, three with container provenance, two present on target, **zero executing**.

## 4. What the table refuses to certify

| Claim | Status |
| :--- | :-: |
| 333 receipts are classified with one label each | **CONFIRMED** |
| the three classifiers agree | **CONFIRMED** (0 disagreements) |
| 109 receipts carry byte-level provenance | **CONFIRMED** |
| any gate reaches runtime | **REFUTED** (0 of 7) |
| a simulation row may be cited as a measurement | **REFUTED** (rule 3) |
| an undeclared receipt may be cited at all | **REFUTED** (rule 5) |
| a static finding is necessarily correct | **REFUTED** |

## 5. The operational reading

1. **Cite by label, never by status word.** `status: CONFIRMED` appears on simulations and on binary
   analyses alike.
2. **Prefer the narrow tier.** 109 rows are byte-level; 186 are labelled static. The difference is 77
   rows of structural verification, and conflating them overstates the corpus.
3. **Keep the gate phrasing exact**: container-proven and pending on target, seven of seven.

## 6. Gaps

- **`UNKNOWN`** — correctness of any individual finding; the table classifies provenance only.
- **`UNKNOWN`** — whether the 31 undeclared receipts are static or documentary.
- **Blocked** — runtime for all seven gates, absent witness.
- **Known limit** — three classifiers agreeing does not make the rules complete, only consistent.
- **Not attempted** — any dynamic validation.
