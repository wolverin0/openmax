<!-- doc-head: Stage 893A - of the 143 Xtensa receipts from Stage 500A to Stage 878A twenty-five declare live hardware evidence, eighty-seven static binary evidence, thirteen simulation, five a negative verdict, and thirteen declare no provenance at all and are listed by name and never citable -->
# Stage 893A — Xtensa findings truth classification

- **Receipt**: [`artifacts/autoresearch/stage893a_xtensa_findings_truth_classification.json`](../artifacts/autoresearch/stage893a_xtensa_findings_truth_classification.json)
- **Tool**: [`tools/re/dissect_stage893a_xtensa_findings_truth_classification.py`](../tools/re/dissect_stage893a_xtensa_findings_truth_classification.py)
- **Audit reference**: sections A09 and A10
- **Scope**: offline static. Reads receipts only.

## 0. The counts

```
classified=143 live=25 static=87 sim=13 refuted=5 undeclared=13 fail_closed=1
```

| Label | Count | Share |
| :--- | :-: | :-: |
| CONFIRMED_LIVE_HARDWARE | **25** | 17.5 % |
| CONFIRMED_STATIC_BINARY | **87** | 60.8 % |
| SIMULATED_MODEL_ONLY | **13** | 9.1 % |
| REFUTED | **5** | 3.5 % |
| provenance undeclared | **13** | 9.1 % |

## 1. The five rules, in order

| Order | Rule | Label |
| :-: | :--- | :--- |
| 1 | explicit live markers | CONFIRMED_LIVE_HARDWARE |
| 2 | status contains REFUTED, BLOCKED, FAILED, LOCKED | REFUTED |
| 3 | filename or keys mark a simulation or fixture | SIMULATED_MODEL_ONLY |
| 4 | static scope, binary descriptors, or structural verification | CONFIRMED_STATIC_BINARY |
| 5 | nothing fires | **undeclared**, listed by name |

The order encodes one deliberate choice: **hardware evidence outranks everything else**. A receipt that
touched a radio keeps the live label even when its conclusion is negative, because the provenance of the
measurement is what a downstream consumer needs.

## 2. The residual is the honest part

Thirteen receipts declare **no provenance at all**: no live marker, no simulation marker, no binary
descriptor, no structural verification block.

The temptation is to file them under CONFIRMED_STATIC_BINARY because they are clearly not hardware.
**`REFUTED`**: that would be the exact error the audit condemns — promoting an artefact by inference
from its filename.

So they are listed **by name** in the receipt and can be cited as **nothing**. `fail_closed = 1` asserts
**structural completeness** — every receipt carries exactly one label and the tallies sum to the total —
not that every receipt declared itself.

That distinction matters. A gate that forced these thirteen into a category would report a clean table
and hide a real defect, which is worse than reporting the defect.

## 3. Where the rules were too narrow, and what fixed them

The first run left **89 of 143** undeclared. Three real signal families were missing, and each was
added only after inspecting the receipts it was meant to catch:

| Signal found | Example | Rule |
| :--- | :--- | :--- |
| live campaign counters rather than booleans | `cumulative_wa_rf_windows_r1_to_r52` | R1 on any `*windows*` integer above zero |
| binary descriptors not named `sha256` | `uci_defaults_champion_sha256`, `held_vendor_static_proof` | R4 on any key containing sha256, bytes, symbol, offset, address, segment, hash, module, package, firmware or elf |
| structural verification blocks | `artifact_checks`, `claims_synced_count`, `repo_5pillar_gate_result` | R4s, recorded as tier `artefact_structure` |

**`CONFIRMED`**: the residual fell from 89 to 13 through evidence, not through loosening the definition
of static.

## 4. Evidence tiers

Calling a receipt "static binary" covers two different strengths, so every row carries a tier:

| Tier | Rows | Meaning |
| :--- | :-: | :--- |
| `binary_bytes` | — | scope declares offline static, or binary descriptors are present |
| `artefact_structure` | — | verification blocks only, no binary descriptor |
| `none` | — | not static (live, simulation or refuted) |

Per-tier counts live in the receipt. The tier is orthogonal to the label: a live receipt can still show
`binary_bytes` because it also carries hashes.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| 143 Xtensa receipts fall in Stage 500A..878A | **CONFIRMED** |
| 25 declare live hardware evidence | **CONFIRMED** (17.5 %) |
| 87 declare static binary evidence | **CONFIRMED** (60.8 %) |
| 13 are simulation or model output | **CONFIRMED** |
| 13 declare no provenance | **CONFIRMED**, listed by name |
| every receipt carries exactly one label | **CONFIRMED** (`fail_closed = 1`) |
| a label proves the conclusion correct | **REFUTED** |

## 6. The operational reading

1. **Only 17.5 % of the Xtensa corpus has hardware provenance.** Any summary that presents Xtensa
   findings as a block inherits the static majority's limits.
2. **Simulation receipts carry `status: CONFIRMED`** just like binary ones, so the status word is not a
   provenance label. That is the single most reusable finding of this stage.
3. **The thirteen undeclared receipts are a defect list**, not a category. Each should be fixed at
   source by declaring scope, and until then it may be cited as nothing.

## 7. Gaps

- **`UNKNOWN`** — the correctness of any individual finding.
- **`UNKNOWN`** — whether the 13 undeclared receipts are static or documentary.
- **Known limit** — filename matching can attribute a receipt that only mentions a token in passing.
- **Not attempted** — re-execution of any receipt, dynamic validation.
