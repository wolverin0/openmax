<!-- doc-head: STAGE460A_LTU_BEETLE_DMA_RING_AND_IRQ52_COALESCING_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 460A — Beetle `ame_asic0` coalescing, DMA rings and packet recycling

- **Receipt**: [`artifacts/autoresearch/stage460a_ltu_beetle_dma_ring_and_irq52_coalescing_re.json`](../artifacts/autoresearch/stage460a_ltu_beetle_dma_ring_and_irq52_coalescing_re.json)
- **Tool**: [`tools/re/build_stage460a_ltu_beetle_dma_ring_and_irq52_coalescing_re.py`](../tools/re/build_stage460a_ltu_beetle_dma_ring_and_irq52_coalescing_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. `eab_driver.ko` is absent — seventh confirmation

**0 files.** `ame_core.ko` (3,282,052 bytes) is the only readable target, and it is enough for the
ring and pool halves and empty for the coalescing half.

## 1. The coalescing vocabulary returns zero

| Token | Hits |
| :--- | :-: |
| `coalesc`, `coalesce` | **0** |
| `napi` | **0** |
| `irq52` | **0** |
| `dma_ring`, `desc` | **0** |
| `recycl`, `buf_pool` | **0** |
| `asic0`, `beetle` | **0** |

**`REFUTED`**: there is **no interrupt-coalescing vocabulary** in this module. No moderation
parameter, no budget, no threshold, no timer.

**`REFUTED`**: `IRQ 52` cannot be verified by name at all. An interrupt number is a **routing
constant compiled into the interrupt table**, never a string. `irq52_literal = 0`.

## 2. The two tokens that look like moderation and are not

A loose census finds two hits that a careless reading would accept:

| Token | Hits | What it actually is |
| :--- | :-: | :--- |
| `budget` | 8 | **`scheduler_budget_us`** and **`symbol_budget_us`** — scheduler timing budgets |
| `moder` | 2 | inside **"AP doesn't support modern atuo scanning"** |

**`REFUTED`**: `budget` is the **scheduler's** budget in microseconds, not an interrupt-coalescing
budget. **`REFUTED`**: `moder` is the first five letters of "modern" — the same substring failure
mode as `BE` inside `PROBE` (452A) and `LQ` inside a base64 table (438A).

`incidental_tokens = 10`, `coalescing_tokens = 0`. The distinction is the whole result.

## 3. The ring API is real and explicitly named

```
ring_init      ring_push      ring_pop
```

| Token | Hits |
| :--- | :-: |
| `ring` (total) | **41** |
| `ring_push` | **5** |
| `ring_init` | **3** |
| `ring_pop` | **1** |

**`CONFIRMED`**: a **descriptor ring** exists with the three canonical primitives — initialise,
enqueue, dequeue. That is the DMA ring the stage is looking for, under the names `ring_*` rather
than `dma_ring`.

Note the asymmetry worth recording: `ring_push` appears **5 times** and `ring_pop` **once**. A
single popleft implementation serving several producers is consistent with a shared dequeue path.

## 4. The packet pool is real

```
pkt_pool_init      pkt_pool_get      free_pkt_from_pkt_pool
```

| Token | Hits |
| :--- | :-: |
| `pkt_pool` (total) | **5** |
| `pkt_pool_init` | **1** |
| `pkt_pool_get` | **1** |

**`CONFIRMED`**: buffers are drawn from a **named pool** (`pkt_pool_get`) and returned by an
explicit **`free_pkt_from_pkt_pool`** symbol. That is packet buffer recycling by name — a get/free
pair, not a garbage collector.

**`UNKNOWN`**: whether the pool is a fixed-size array, a linked free-list, or per-queue. The names
do not say.

## 5. The interrupt surface

`irq` has **12** hits and they are **entries**, not parameters:

```
__ame_core_hook_isr_register
__ame_core_hook_hcam_isr_register
__ame_core_hook_hfe_isr_register
ame_bbp_rt_rx_isr
ame_bbp_rt_rx_isr_periodic_work
ame_bbp_isr_print_info
ame_bbp_debug_fetch_isr_symbol
Ctrl_ISR_SendPacket
ame_core_freq_jump_check_irq
ame_core_dump_airq_info
```

**`CONFIRMED`**: the ISR surface is **registration-hooked** — three `__ame_core_hook_*_isr_register`
entry points for the HCAM (MAC), HFE (fabric) and generic paths — plus a **real-time RX ISR with a
periodic work variant**.

**`CONFIRMED`**: `ame_core_dump_airq_info` is an air-queue dump, which is the closest thing here to
interrupt-queue telemetry.

**`UNKNOWN`**: which of these hooks is bound to vector 52, and whether any of them coalesces.

## 6. Completion tracking, but not recycling policy

Four messages read `Not completed yet (%u)` and `Not completed yet (%u), (%u,%u)`.

**`CONFIRMED`**: the driver tracks **outstanding descriptors** and complains when they do not
complete — that is the safety net a DMA ring needs.

**`REFUTED`**: those messages establish a **completion check**, not a **recycling policy**. There is
no timer, no threshold and no backpressure parameter attached.

## 7. What is established

| Claim | Status |
| :--- | :-: |
| `eab_driver.ko` exists | **REFUTED** (0 files, 7th) |
| an interrupt-coalescing mechanism is named | **REFUTED** (0 tokens) |
| `IRQ 52` is verifiable by name | **REFUTED** (a number, not a string) |
| `budget` is a coalescing budget | **REFUTED** (`scheduler_budget_us`) |
| `moder` indicates moderation | **REFUTED** (inside "modern") |
| a descriptor ring exists with init/push/pop | **CONFIRMED** |
| a packet pool exists with get/free | **CONFIRMED** |
| the ISR surface is registration-based | **CONFIRMED** (3 hook registers) |
| outstanding-descriptor tracking exists | **CONFIRMED** |
| a coalescing policy or parameter | **UNKNOWN / not recovered** |

## 8. The practical reading

The module has everything a DMA engine needs **except** the moderation layer the stage names:

```
ring_init -> ring_push -> [fabric] -> isr -> ring_pop -> pkt_pool_get -> free_pkt_from_pkt_pool
```

That is a complete producer/consumer loop with buffer recycling. What is missing is the part that
**decides how many completions to batch before raising an interrupt**. It may live in the fabric
bitstream (absent), in `eab_driver.ko` (absent), or it may simply not exist — this stage can only
say the module does not name it.

## 9. Gaps

- **`UNKNOWN`** — the coalescing policy, if any; no parameter exists to read.
- **`UNKNOWN`** — which ISR hook binds to vector 52.
- **`UNKNOWN`** — the pool's data structure and depth.
- **`UNKNOWN`** — the `Not completed yet` timeout, if one exists.
- **`UNKNOWN`** — whether `ring_pop` is polled or interrupt-driven.
- **Blocked** — any bitstream-level answer, until an `.rbf`/`.sof` exists.
- **Not attempted** — dynamic validation, JTAG/fabric access.
