<!-- doc-head: STAGE694A_LTU_EAB_DRIVER_DMA_RING_AND_ZEROCOPY_TX_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 694A — LTU EAB descriptor rings and the ARM-to-ASIC handoff

- **Receipt**: [`artifacts/autoresearch/stage694a_ltu_eab_driver_dma_ring_and_zerocopy_tx_re.json`](../artifacts/autoresearch/stage694a_ltu_eab_driver_dma_ring_and_zerocopy_tx_re.json)
- **Tool**: [`tools/re/dissect_stage694a_ltu_eab_driver_dma_ring_and_zerocopy_tx_re.py`](../tools/re/dissect_stage694a_ltu_eab_driver_dma_ring_and_zerocopy_tx_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. `eab_driver.ko` absent — thirteenth confirmation

**0 files.** The ARM side is not a separate module in this corpus. The EAB interface is **compiled
into `ame_core.ko`**, where it is the single largest symbol family: **573 tokens, 40+ distinct
symbols** (the probe caps at 40).

`ame_dev.ko` contributes 5 `eab` tokens and 4 `ring` tokens — sysfs traces only.

## 1. The descriptor interface to the ASIC

```
AME_EAB_PeakBDInterface          AME_EAB_CheckRxQBD
```

**`CONFIRMED`**: `bd_interface_named = 1`.

`BD` is the **buffer descriptor**. `PeakBDInterface` is the vendor's verb for reading the descriptor
interface, and `CheckRxQBD` is the receive-side descriptor validity check. So the ARM touches the
ASIC's descriptors through a **named interface**, not through raw MMIO pokes scattered in the code.

## 2. TX and RX queue information are read separately

```
AME_EAB_ReadTXQInfo        AME_EAB_ReadRXQInfo
```

**`CONFIRMED`**: `tx_rx_info_split = 1` — two distinct readers.

That is the key architectural fact: the ARM **polls the ASIC for queue state** rather than taking an
interrupt per descriptor. Two separate readers means the TX and RX directions have **different queue
state layouts**, not one shared structure with a direction flag.

This is consistent with Stage 460A's finding that the generic path has `ring_push` (5 hits) but
`ring_pop` only **once** — a single dequeue path serving several producers.

## 3. FIFO delivery is paired, with an extra lane

```
AME_EAB_DeliverTxFIFO        AME_EAB_DeliverTxFIFO_extra
AME_EAB_ClearallTxFIFO       AME_EAB_ClearallTxFIFO_extra
```

**`CONFIRMED`**: `fifo_pair_count = 4`, `fifo_has_extra_variant = 1`.

The `_extra` suffix appears on **both** the deliver and the clear, which is the signature of a
**second FIFO bank**: if `_extra` existed only on delivery, it would be an option on one call; because
it also has its own clear, it is a separate queue that must be drained separately.

**`CONFIRMED`**: delivery is `DeliverTxFIFO` — a **transfer of ownership** verb. That is the handoff.

## 4. The queue hierarchy matches Stage 438A's scheduler

```
AME_EAB_ActivateQueue        AME_EAB_ActivateSuperQueue
```

**`CONFIRMED`**: `super_queue_hierarchy = 1` — a **super-queue over queues**.

That is the same two-tier structure Stage 438A proved dynamically via `Top NQ CPE` / `Min SQ CPE`
with the `NtoS` and `StoN` transition counters. The EAB layer's activation primitives are the
hardware-side counterpart of that scheduler: `ActivateSuperQueue` activates the group, `ActivateQueue`
activates one member.

The other 30+ EAB symbols are checkers and clearers:

```
CheckQueueStatus   CheckQException   CheckRxFIFO   CheckL2FrameDefFIFO
CheckVList         CheckMixedCmd     CheckBeacon   CheckMem
ClearATX           ClearETX          ClearBDRateCtrlStats
AdjustFrameLength  CFTxStatus        ChkRstProg
```

**`CONFIRMED`**: the EAB layer is dominated by **validation**, not transfer. That is what a driver
does when the hardware can misbehave: it checks the queue status, the FIFO depth and the descriptor
list before and after every handoff.

## 5. `zerocopy` does not exist — and the question stays open

| Token | Hits |
| :--- | :-: |
| `zerocopy`, `zero_copy` | **0** |
| `doorbell` | **0** |
| `ame_ASIC`, `ame_asic0` | **0** |
| `cortex`, `Cortex` | **0** |
| `asic` (generic) | **1** |

**`REFUTED`**: none of the zero-copy vocabulary exists.

**`REFUTED`**: the ASIC is not named `ame_ASIC0` anywhere — the generic token `asic` appears **once**,
inside a queue-reset context.

**`REFUTED`**: the ARM core model is not named. The stage says Cortex-A7; Stage 376A established a
"dual-core ARMv7 HPS" from the SoC architecture. Cortex-A7 is **ARMv7 and therefore consistent**, but
this corpus does not name it, so `cortex_token_hits = 0`.

**The important open question:** whether the handoff is **zero-copy** (the descriptor points at ARM
memory and the ASIC DMAs from it) or **copy-based** (the FIFO write moves the bytes) is **not
decidable from these names**. `DeliverTxFIFO` is a FIFO verb, which leans toward copy — but a FIFO
can carry descriptors as easily as payloads, and the receipt says `zerocopy_tx_recovered = 0` rather
than guessing.

## 6. The ASIC reports its own capability mask

```
{"AMEX":%d, "NO_AES":%d, "NO_OFDMA":%d, "NO_RS":%d, "NO_LDPC":%d, "NO_1024QAM":%d, ...}
```

**`CONFIRMED`**: `capability_json_hits = 3` — the ASIC's feature mask is emitted as **JSON**.

`NO_LDPC`, `NO_RS` and `NO_1024QAM` are the interesting fields: they explain Stage 648A's
`ame_check_hw_NoLDPC` and its `No ldpc supported` message. The ARM does not assume the ASIC can do
LDPC — it **reads the mask**.

## 7. What is established

| Claim | Status |
| :--- | :-: |
| `eab_driver.ko` exists | **REFUTED** (0 files, 13th) |
| the EAB interface is in `ame_core.ko` | **CONFIRMED** (40+ symbols) |
| a named buffer-descriptor interface exists | **CONFIRMED** (`PeakBDInterface`) |
| TX and RX queue info are read separately | **CONFIRMED** (two readers) |
| FIFO delivery has a second lane with its own clear | **CONFIRMED** (`_extra` on both) |
| a super-queue over queues exists | **CONFIRMED** (`ActivateSuperQueue`) |
| the EAB layer is dominated by validation | **CONFIRMED** (30+ checkers) |
| the ASIC reports its capability mask as JSON | **CONFIRMED** |
| zero-copy is named | **REFUTED** (0 hits) |
| the ASIC is called `ame_ASIC0` | **REFUTED** (0 hits) |
| the ARM core is a Cortex-A7 | **UNKNOWN** (ARMv7 per 376A, cortex unnamed) |
| whether the handoff is zero-copy | **UNKNOWN / undecidable from names** |
| the BD descriptor layout | **UNKNOWN / not recovered** |

## 8. The operational reading

The EAB layer answers a specific question well: **how does the ARM know the ASIC is ready**. It does
not answer the one the stage cares about most.

**Answerable:** the ARM polls per-direction queue info, validates queue status and FIFO depth, and
activates queues through a super-queue hierarchy. A stuck TX queue is therefore detectable **before**
delivery, through `CheckQueueStatus` / `CheckRxFIFO`, not only after a timeout.

**Not answerable:** whether the bytes are copied. That requires the descriptor layout or a datapath
trace, neither of which is in the corpus. For a performance question ("where does the TX copy cost
come from"), the honest statement is that this corpus cannot rule copy-based transfer in or out.

## 9. Gaps

- **`UNKNOWN`** — whether the handoff is zero-copy or copy-based.
- **`UNKNOWN`** — the BD descriptor layout: address, length, ownership bit.
- **`UNKNOWN`** — the FIFO depth and the `_extra` lane's purpose.
- **`UNKNOWN`** — the queue-info structure returned by `ReadTXQInfo` / `ReadRXQInfo`.
- **`UNKNOWN`** — the ARM core model (ARMv7 confirmed, Cortex-A7 not named).
- **Known limit** — a `DeliverTxFIFO` name proves a transfer verb, not its mechanism.
- **Not attempted** — dynamic validation, datapath tracing, MMIO capture.
