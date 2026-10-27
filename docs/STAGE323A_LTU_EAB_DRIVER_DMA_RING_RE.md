<!-- doc-head: STAGE323A_LTU_EAB_DRIVER_DMA_RING_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 323A — LTU EAB/DMA ring, IRQ coalescing and skb recycling

- **Receipt**: [`artifacts/autoresearch/stage323a_ltu_eab_driver_dma_ring_re.json`](../artifacts/autoresearch/stage323a_ltu_eab_driver_dma_ring_re.json)
- **Tool**: `tools/re/ltu_eab_driver_dma_ring_and_interrupt_coalesce_re.py`
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. The premise fails first

**`eab_driver.ko` does not exist.** A recursive glob for `eab*.ko` under `artifacts/` returns
**0 files**. This is the fourth independent confirmation (154A, 173A, 226A, and here).

The stage describes "LTU Beetle FPGA PCIe/AXI DMA ring descriptors" in a module that was never
shipped in the extracted rootfs. Nothing is reported for it.

## 1. What carries the DMA surface instead

`ame_core.ko` and `ame_dev.ko` in `AF-LTU.v2.4.2` — the two modules that do exist and do hold
the radio-core plumbing.

| Module | Bytes | DMA | IRQ | Coalesce | Watermark | skb |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: |
| `ame_core.ko` | 3,282,052 | **55** | **82** | 30 | 11 | 4 |
| `ame_dev.ko` | 298,760 | 21 | 14 | — | — | — |

Counts are **symbol-bucket sizes** matched by name against
`dma|desc|ring|bd_|buffer_desc`, `irq|isr|interrupt|napi`, `coalesc|mitigat|budget|poll_|timer`,
`watermark|wm_|threshold|hi_?mark|lo_?mark`, and `skb|recycle|free_|reuse|zero_?copy`.

## 2. What is and is not claimed

**`CONFIRMED`**: `ame_core.ko` carries 55 DMA-named and 82 IRQ-named defined symbols, plus 30
coalescing-shaped and 11 watermark-shaped names. That is a real, countable surface.

**Not claimed**:

- **no descriptor layout** — the ring entry size, field order and ownership bits were not
  decoded;
- **no coalescing threshold** — no numeric timer or packet-count constant was attributed to a
  coalescing register;
- **no watermark value** — the 11 watermark-named symbols were not resolved to constants;
- **no zero-copy dataflow** — the 4 skb-named symbols are a bucket, not a recycling path.

The stage asked for descriptors, timers, watermarks and recycling. What exists in the module is
**the naming**, and naming is not structure.

## 3. Why the symbol-only result is still useful

It bounds the search. If a future pass wants the DMA ring, it now knows:

- the surface is in `ame_core.ko` (55 symbols), **not** in a separate EAB driver;
- IRQ handling is 82 symbols in the same module;
- `ame_dev.ko` holds a much smaller slice (21 DMA, 14 IRQ) and is unlikely to be the ring owner.

That is a targeting result, and it is why reporting the absence of `eab_driver.ko` matters more
than reporting the presence of 55 symbols.

## 4. What would actually decode the ring

| Step | Requirement | Available? |
| :--- | :--- | :--- |
| find the ring allocation | `dma_alloc_coherent` call site + size argument | yes, symbol present |
| get the descriptor stride | the size / count division | needs the constants, not yet extracted |
| get the ownership protocol | the producer/consumer index updates | needs a write-site dataflow |
| get the coalescing threshold | the register write on the IRQ path | needs the HAL write path (blocked since 174A/197A) |

The last row is the same blocker as the knob-to-register work: without the HAL write path, no
register threshold is attributable.

## 5. Gaps

- **`UNKNOWN`** — DMA descriptor layout and ring depth.
- **`UNKNOWN`** — IRQ coalescing timers and packet-count thresholds.
- **`UNKNOWN`** — RX/TX watermark values.
- **`UNKNOWN`** — zero-copy skb recycling path.
- **`CONFIRMED ABSENT`** — `eab_driver.ko`, so any FPGA/PCIe-AXI-specific path is unreachable
  from the shipped LTU rootfs.
- **Not attempted** — dynamic validation.
