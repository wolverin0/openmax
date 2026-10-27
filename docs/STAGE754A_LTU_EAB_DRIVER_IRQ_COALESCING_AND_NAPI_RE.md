<!-- doc-head: STAGE754A_LTU_EAB_DRIVER_IRQ_COALESCING_AND_NAPI_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 754A — GIC 52, IRQ coalescing and the NAPI poll budget

- **Receipt**: [`artifacts/autoresearch/stage754a_ltu_eab_driver_irq_coalescing_and_napi_re.json`](../artifacts/autoresearch/stage754a_ltu_eab_driver_irq_coalescing_and_napi_re.json)
- **Tool**: [`tools/re/dissect_stage754a_ltu_eab_driver_irq_coalescing_and_napi_re.py`](../tools/re/dissect_stage754a_ltu_eab_driver_irq_coalescing_and_napi_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. `eab_driver.ko` absent — fourteenth confirmation

**0 files.** Readable targets: `ame_core.ko` (3,282,052 bytes) and `ame_dev.ko` (298,760 bytes).

The stage asks for three mechanisms. **All three fail**, and each failure is informative.

## 1. NAPI does not exist

| Token | Hits |
| :--- | :-: |
| `napi`, `NAPI` | **0** |

**`REFUTED`**: `napi_absent = 1`.

NAPI is a **Linux networking** API — a poll budget for a netdev driver. This is **not a netdev
driver**: it is a baseband/TDMA driver with its own scheduling layer. There is no poll budget to
recover because there is no NAPI.

## 2. Coalescing does not exist either — second independent confirmation

| Token | Hits |
| :--- | :-: |
| `coalesc`, `COALESC` | **0** |

**`REFUTED`**: `coalescing_absent = 1`.

Stage 460A measured the same zero and concluded the module does not name a moderation layer. This
stage re-measures it on the same modules from a different prompt and gets the same answer — which is
the useful part: the negative is **reproducible**, not a one-off miss.

## 3. `gic` is inside `vermagic`

The single `gic` hit in each module is:

```
vermagic=3.14.65 SMP preempt mod_unload ARMv7 p2v8
```

**`REFUTED`**: `gic_is_vermagic = 1` (`gic_token_hits = 2`, `vermagic_hits = 2`).

The **Generic Interrupt Controller is not named** anywhere. The token matched the module's
compatibility string. This is the tenth substring trap of the series and the second in two stages,
right after `compensat` in Stage 728A.

## 4. `budget` is the scheduler's, not the poll loop's

All 8 hits are:

```
checkpoint1 %u checkpoint2 %u checkpoint3 %u scheduler_budget_us:%u symbol_budget_us:%u
```

**`REFUTED`**: `budget_is_scheduler = 1` (`sched_budget_hits = 2`).

That is a **TDMA scheduling budget in microseconds**, with three checkpoints before it — a timing
instrument for the frame scheduler, not a NAPI poll weight. Stage 460A reached the same conclusion.

## 5. `poll` means polling mode

Both hits are `enter polling mode` and `Q#%u is active` — the strings Stage 438A first found.

**`REFUTED`**: `poll_is_polling_mode = 1`. This is the **TDMA poll-list** mechanism for CPE
scheduling, not NAPI polling.

## 6. What the interrupt surface actually is

```
ptmp_sched_irq_entry        ptp_sched_irq_entry
ame_core_freq_jump_check_irq       ame_core_dump_airq_info
ame_core_airQexcptHandler   monitor_airQueue_routine   monitor_airQueue_work
Sched_update_budget_by_QId
```

**`CONFIRMED`**: `sched_irq_count = 2`, `ptmp_ptp_split = 1`, `airq_exception_handler = 1`.

The interrupt entries are **scheduler-scoped**: one for **PtMP** (multipoint, the AP case) and one
for **PtP** (point-to-point, the backhaul case). Beside them sit a **frequency-jump check** and an
**air-queue monitor** with its own exception handler and worker.

**This is the architectural answer to the stage's question.** The interrupt is not a
packet-completion vector that needs moderation — it is a **scheduling tick**. And a tick-driven
design does not coalesce, because coalescing a tick delays the schedule. Instead it **budgets** the
work done per tick, which is precisely what `scheduler_budget_us` measures.

So the absence of coalescing and NAPI is not a gap in the driver. It is the **consequence of the
architecture**: a TDMA baseband cannot batch interrupts without violating its own timing.

## 7. `IRQ 52` cannot be verified by name

**`REFUTED`**: `irq52_literal = 0`.

An interrupt number is a **routing constant compiled into the interrupt table**, never a string. So
the specific vector claim is unverifiable from the module — only the ISR names that exist can be
examined, and they say the vectors are scheduler-scoped, not numbered in text.

## 8. What is established

| Claim | Status |
| :--- | :-: |
| `eab_driver.ko` exists | **REFUTED** (0 files, 14th) |
| a NAPI poll budget exists | **REFUTED** (0 hits) |
| an IRQ coalescing parameter exists | **REFUTED** (0 hits, 2nd confirmation) |
| `gic` names the Generic Interrupt Controller here | **REFUTED** (`vermagic`) |
| `budget` is a poll budget | **REFUTED** (`scheduler_budget_us`) |
| `poll` is NAPI polling | **REFUTED** (`enter polling mode`) |
| IRQ 52 is verifiable by name | **REFUTED** (a routing constant) |
| the interrupt entries are scheduler-scoped, PtMP and PtP split | **CONFIRMED** |
| a frequency-jump check IRQ exists | **CONFIRMED** |
| an air-queue monitor with an exception handler exists | **CONFIRMED** |
| the per-tick work is bounded by a microsecond budget | **CONFIRMED** |
| the GIC vector-to-source map | **UNKNOWN / not in the module** |

## 9. The operational reading

The absence of coalescing is not a defect to work around — it tells you **where to look** when
interrupt load is the symptom:

1. the work per tick is bounded by `scheduler_budget_us`; if that budget is exhausted at the three
   checkpoints, the scheduler is **behind**, not the interrupt controller;
2. `ame_core_airQexcptHandler` firing means the **air queue** overflowed — a queue-depth or
   scheduling problem, not a moderation problem;
3. `freq_jump_check_irq` firing points at **frequency agility**, the `autofa` mechanism Stage 616A
   found, not at packet load.

Coalescing would not help any of the three, because none of them is a per-packet interrupt.

## 10. Gaps

- **`UNKNOWN`** — the GIC vector map; IRQ 52 is a number in a table, not a symbol.
- **`UNKNOWN`** — the `scheduler_budget_us` default value and what the three checkpoints measure.
- **`UNKNOWN`** — the air-queue exception conditions.
- **`UNKNOWN`** — whether any moderation exists in the fabric bitstream (absent from the corpus).
- **`UNKNOWN`** — how the PtMP and PtP IRQ entries are selected at runtime.
- **Known limit** — an absent API in a module that is not a netdev driver is expected, not a defect.
- **Not attempted** — dynamic validation, interrupt-load measurement.
