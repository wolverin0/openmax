<!-- doc-head: Stage 902A - the audit over all 1196 receipts in artifacts/autoresearch excludes its own four audit receipts and classifies the remaining 1192, finding 315 live 586 static 102 simulated 13 refuted and 176 still undeclared, of which 156 are historical stage receipts predating the provenance convention and 20 are auxiliary ledgers and atlases -->
# Stage 902A — full-corpus provenance audit

- **Receipt**: [`artifacts/autoresearch/stage902a_full_corpus_provenance_audit.json`](../artifacts/autoresearch/stage902a_full_corpus_provenance_audit.json)
- **Tool**: [`tools/verify/audit_stage902a_full_corpus_provenance.py`](../tools/verify/audit_stage902a_full_corpus_provenance.py)
- **Scope**: read-only audit of `artifacts/autoresearch/`. No file modified, no radio contacted.

## 0. The numbers, including the uncomfortable one

```
receipts=1196 excluded=4 classified=1192 unreadable=0 explicit=31
live=315 static=586 sim=102 refuted=13 undeclared=176
```

| Class | Count |
| :--- | :-: |
| CONFIRMED_LIVE_HARDWARE | **315** |
| CONFIRMED_STATIC_BINARY | **586** |
| SIMULATED_MODEL_ONLY | **102** |
| REFUTED | **13** |
| **undeclared** | **176** |

**Stage 895A's "31" was scoped to Stage 500A..878A.** Across the entire directory there are **176**
undeclared receipts, and this stage reports that rather than repeating the narrower number.

**Four receipts are excluded by construction**: `stage901a` through `stage904a` are this batch's own
output. An audit that counted its own product would change the population it measures on every run, so
the family is excluded and reported as `audit_receipts_excluded`.

## 1. Where the 176 come from

| Group | Count | Examples |
| :--- | :-: | :--- |
| historical stage receipts | **156** | `stage100a_git_public_repo_safety_and_reddit_sync`, `stage116a_pbe5ac_kit_v2_receipt` |
| auxiliary artefacts | **20** | `champion_state_ledger`, `master_11unit_hardware_atlas`, `discovery_to_research_queue` |

Both groups **predate the provenance convention**. They belong to earlier workstreams, and this stage
lists them by name instead of editing them.

## 2. Rule 6, and why the first pass was wrong

The first pass reported **371** undeclared. Almost all were `lap120_*` autoresearch runs, and the cause
was a mismatch between what the rules expected and what those receipts contain.

| Expected by the rules | Actually present |
| :--- | :--- |
| a `status` word, a `scope`, a hash | `experiment_id`, `crossover_schedule`, `objective_config`, `best_fmx_loss`, `pareto_frontier` |

Those receipts carry a **measurement payload** instead of metadata. A filename encoding a distance and
a loss is not evidence; the numeric payload inside is. Rule 6 therefore classifies a receipt as live
when it holds a crossover schedule, an objective configuration with numeric targets, a measured loss
and a Pareto frontier.

**`CONFIRMED`**: the residual fell from **371 to 176**.

## 3. Order of the seven rules

| Order | Rule | Label |
| :-: | :--- | :--- |
| 1 | explicit `evidence_provenance_class` | as recorded, because curation outranks a pattern |
| 2 | `experiment_id` marked LIVE, hardware pair, window counters, device-address keys | LIVE |
| 3 | status or verdict REFUTED, BLOCKED, FAILED, LOCKED | REFUTED |
| 4 | filename or keys mark a model, fixture or scorecard | SIMULATED |
| 5 | measurement payload | LIVE |
| 6 | offline-static scope, binary descriptors, structural block | STATIC |
| 7 | nothing fires | undeclared |

**`CONFIRMED`**: the 31 receipts remediated in Stage 901A are classified by rule 1 and **none** of them
reappears in the undeclared list.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| 100 % of the audited directory was read | **CONFIRMED** (1192 of 1192, 0 unreadable) |
| the 31 remediated receipts are no longer undeclared | **CONFIRMED** |
| the corpus is free of undeclared receipts | **REFUTED** (176 remain) |
| live receipts are the majority | **REFUTED** (315 live against 586 static) |
| the first pass's 371 was accurate | **REFUTED** (rule 6 reduced it to 176) |
| a measurement payload proves correct instrumentation | **REFUTED** |

The second row is the achievement; the third is the standing defect. Reporting only the first would be
the exact selective reading the audit criticises.

## 5. Why the 176 were not mass-edited

They belong to other workstreams and predate the convention. Editing 176 files to make a count reach
zero is not remediation; it is **manufacturing a green number**. The honest output is the list, the
count, and a follow-up that assigns a class per receipt with a citation — the method Stage 901A used
for 31.

## 6. Gaps

- **`UNKNOWN`** — whether the 156 historical receipts are static or live; they must be curated.
- **`UNKNOWN`** — whether the 20 auxiliary artefacts need a class at all, or need a different schema.
- **Known limit** — rule 6 treats a measurement payload as live evidence; it cannot detect a run that
  recorded fabricated numbers.
- **Known limit** — 13 refuted receipts is a small class, and rarity invites the question of whether
  the rule fires at all.
- **Not attempted** — any editing in this stage, any dynamic validation.
