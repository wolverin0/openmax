<!-- doc-head: STAGE438A_LTU_AME_CORE_POLL_SCHEDULER_AND_SLOT_ALLOC_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 438A — the LTU poll-list scheduler and its CPE classes

- **Receipt**: [`artifacts/autoresearch/stage438a_ltu_ame_core_poll_scheduler_and_slot_alloc_re.json`](../artifacts/autoresearch/stage438a_ltu_ame_core_poll_scheduler_and_slot_alloc_re.json)
- **Tool**: [`tools/re/build_stage438a_ltu_ame_core_poll_scheduler_and_slot_alloc_re.py`](../tools/re/build_stage438a_ltu_ame_core_poll_scheduler_and_slot_alloc_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. `eab_driver.ko` is absent — sixth confirmation

**0 files.** The entire scheduler lives in `ame_core.ko` (3,282,052 bytes). Every stage that names
`eab_driver.ko` hits the same wall, and this one records it rather than working around it.

## 1. The stage's label is wrong; its mechanism is right

The stage asks to compare a **Short-Queue `SQ ≤ 16` CPE** path against a **Long-Queue `LQ > 16`
CPE** path. The module does have a two-class CPE split — but it is called **N and S**, and the
words "short" and "long" are not used for it.

| Token | Total | Format-string contexts |
| :--- | :-: | :-: |
| **`SQ`** | **6** | **6** |
| `NQ` | 1 | — |
| `SWQ` | 3 | — |
| **`LQ`** | **20** | **0** |
| `long_queue` | 0 | — |
| `short_queue` | 0 | — |

**`CONFIRMED`**: `SQ` is real — every one of its 6 hits sits inside a genuine log format string.

**`REFUTED`**: `LQ` is **not a token**. Its 20 occurrences carry **zero** format-string context.
Four of them are printable, and that is the trap worth naming: they sit inside a base64-style
lookup table (`BINSXZ?FKPVW=CINTU<BHMST:AFLQR8@…`), which is printable ASCII but is not a
diagnostic. A printable-ratio classifier would have called them hits; a format-string classifier
does not.

**`REFUTED`**: `short_queue` and `long_queue` do not exist. The 22 `short` hits are all
`parmtype=…:short` / `ushort` type declarations in the tunable metadata, not a queue name.

## 2. What the `SQ` strings actually say

```
--- SFN[%x] ---
Top NQ CPE(%d) [%d.%d] (NtoS=%d)
Min SQ CPE(%d) [%d.%d] (StoN=%d)
SQ-CPE(%d)[%d.%d]
[d] TA %d, ID %d, QID %d, numQ %d, numSQ %d, macAddr …
cpeID %d, startQ %d, numQ %d numSQ %d
```

**`CONFIRMED`** — and this is the stage's real finding — the module names a **two-class CPE
scheduler** with explicit **promotion and demotion counters**:

| Element | Meaning (from the string) |
| :--- | :--- |
| `Top NQ CPE` | the best CPE in class **N** |
| `Min SQ CPE` | the worst CPE in class **S** |
| **`NtoS`** | count of transitions **N → S** |
| **`StoN`** | count of transitions **S → N** |
| `numQ`, `numSQ` | per-CPE queue counts |
| `SFN[%x]` | a superframe number |

**`CONFIRMED`**: `NtoS` and `StoN` both exist (1 each) inside format strings. **The class split is
dynamic** — that is exactly the "dynamic slot allocation" behaviour the stage is looking for, and
it is proven by the presence of transition counters rather than inferred from a name.

The selection rule the strings imply: **promote the top of N, demote the bottom of S**. That is the
classic two-tier scheduling policy, and it is the strongest statement the corpus supports.

## 3. Polling and the scheduler surface

| Finding | Value |
| :--- | :--- |
| `poll` tokens | **2** — `enter polling mode`, `Q#%u is active…` |
| `sched` tokens | **297** |
| `ofdma` / `OFDMA` | **88** combined |
| `slot` tokens | 41 |
| scheduler symbols | **40 matched** |

Representative symbols:

```
AME_HSM_add_sched_result
AME_HSM_submit_sched_result
AME_SchedAutoMCS
AME_SchedCheckActiveCPE
ame_core_put_last_scheduler_result
scheduler_result_emit
ame_core_log_sched_dump
core_task_frm_run / core_task_hi_run
```

**`CONFIRMED`**: the scheduler is a **submit-result / emit** pipeline (`add_sched_result`,
`submit_sched_result`, `put_last_scheduler_result`, `scheduler_result_emit`) with an activity check
(`AME_SchedCheckActiveCPE`) and an auto-MCS policy (`AME_SchedAutoMCS`).

## 4. The 16-CPE threshold is not there

`threshold_16_present = 0`. The integer 16 appears 40 times in the module, but in unrelated
contexts (array bounds, shifts, bit widths). **`REFUTED`**: no `SQ ≤ 16` boundary exists as a
recoverable constant, and no `16` sits near any `SQ`/`NQ` string.

## 5. Slot allocation is mixed with crypto

`slot` has 41 hits, and they are **not one thing**:

- `match on slot idx %X` / `slot on idx …` — scheduler key slots;
- `wait_for_aes_slots` / `ame_bbp_set_aes_key` — **crypto keystore slots**;
- `ame_bbp_set_Param_mimo`, `ame_bbp_set_Param_mcs` — BBP parameter setters that happen to be
  adjacent.

**`REFUTED`**: there is no single "slot allocator" to isolate. The word is overloaded across
scheduling and AES key storage, and merging them would be a false positive.

## 6. What is established

| Claim | Status |
| :--- | :-: |
| `eab_driver.ko` exists | **REFUTED** (0 files) |
| a Short-Queue `SQ` class exists | **CONFIRMED** (6 format strings) |
| a Long-Queue `LQ` class exists | **REFUTED** (20 tokens, 0 format strings) |
| `long_queue` / `short_queue` exist | **REFUTED** (0 hits) |
| the two classes are **N** and **S** | **CONFIRMED** (`Top NQ CPE`, `Min SQ CPE`) |
| the split is dynamic, with N→S and S→N counters | **CONFIRMED** (`NtoS`, `StoN`) |
| a `≤ 16` CPE threshold exists | **REFUTED** |
| polling mode is entered and queues go active | **CONFIRMED** |
| a submit/emit scheduler pipeline exists | **CONFIRMED** (40 symbols) |
| slot allocation is one isolatable subsystem | **REFUTED** (mixed with AES slots) |

## 7. Gaps

- **`UNKNOWN`** — the rule that triggers `NtoS` / `StoN`; only the counters are visible.
- **`UNKNOWN`** — the actual capacity limit of class `S`; 16 is not in the binary.
- **`UNKNOWN`** — the `SFN` superframe structure and the slot map within it.
- **`UNKNOWN`** — the OFDMA/TDD split: 88 OFDMA tokens, but no down/up duration pair was bound.
- **`UNKNOWN`** — what `SWQ` means (`SWQ_Record Not Support`); the acronym is undefined here.
- **Known limit** — a counter proves a transition happens, not what governs it.
- **Not attempted** — dynamic validation.
