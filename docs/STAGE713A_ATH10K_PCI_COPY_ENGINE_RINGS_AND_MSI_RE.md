<!-- doc-head: STAGE713A_ATH10K_PCI_COPY_ENGINE_RINGS_AND_MSI_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 713A — PCIe copy-engine rings, pktlog and MSI configuration

- **Receipt**: [`artifacts/autoresearch/stage713a_ath10k_pci_copy_engine_rings_and_msi_re.json`](../artifacts/autoresearch/stage713a_ath10k_pci_copy_engine_rings_and_msi_re.json)
- **Tool**: [`tools/re/dissect_stage713a_ath10k_pci_copy_engine_rings_and_msi_re.py`](../tools/re/dissect_stage713a_ath10k_pci_copy_engine_rings_and_msi_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. `ath10k_core.ko` absent — sixth confirmation

**0 files.** The ath10k **CE table** — the fixed mapping of CE0..CE7 to WMI control, HTT TX, HTT RX
and the pktlog channels — cannot be read. The vendor `umac.ko` carries a full CE implementation under
a different scheme, and that is what this stage dissects.

## 1. The CE layer is per-engine, with 24 named operations

```
CE_init   CE_fini   CE_send   CE_pause
CE_completed_send_next    CE_completed_recv_next
CE_cancel_send_next       CE_revoke_recv_next
CE_per_engine_handler     CE_per_engine_service
CE_per_engine_service_any CE_per_engine_servicereap
```

**`CONFIRMED`**: `ce_symbol_count = 24`, and **4** of them carry `per_engine`.

That is the architectural fact the stage is after: the copy-engine layer is **indexed by engine**,
not a single queue. The four per-engine variants are distinct roles:

| Symbol | Role |
| :--- | :--- |
| `CE_per_engine_handler` | the per-engine interrupt entry |
| `CE_per_engine_service` | service one engine |
| `CE_per_engine_service_any` | **sweep any** engine that has work |
| `CE_per_engine_servicereap` | **reap** completed entries |

`service_any` beside `service` is what a shared interrupt handler needs: on a shared vector you do
not know which engine fired, so you sweep. `servicereap` is the reclamation pass.

The send and receive completions are separate, each with a `_nolock` variant:

```
CE_completed_send_next        CE_completed_send_next_nolock
CE_completed_recv_next        CE_completed_recv_next_nolock
```

**`CONFIRMED`**: TX and RX completion are **different queues with different walkers**, and the
`_nolock` duplicate is the "caller already holds the lock" path — the classic pattern for a
completion loop that must drain many entries without re-taking a lock per entry.

## 2. The engines are not numbered

| Token | Hits |
| :--- | :-: |
| `CE0`, `CE1`, … `CE7` | **0** |
| `copy_engine`, `CopyEngine` | **0** |

**`REFUTED`**: the engines are **not named individually** anywhere. `engine_count_proven = 0`.

So the "8 rings" of the stage is **not provable from this module**. What *is* provable is that the
code is written to handle **N** engines through an index parameter, with a sweep path for the
shared-interrupt case.

## 3. Receive flow control is watermark-based

```
CE_recv_watermarks_set    CE_recv_entries_avail    CE_recv_entries_done
CE_recv_buf_enqueue       CE_recv_cb_register
```

**`CONFIRMED`**: `watermark_api_present = 1`.

The host sets a **watermark**, publishes **available** receive entries, and the engine reports
**done** entries, with a buffer-enqueue call and a callback registration. That is how a CE ring avoids
overflow without an interrupt per descriptor — the same design principle as Stage 460A's
`ring_push`/`ring_pop` with `pkt_pool_get`.

## 4. Queues are allocated at runtime, which is why no static table exists

```
HIFGetFreeQueueNumber   HIFGetDefaultPipe   HIFConfigureDevice
HIFClaimDevice          HIFAttachHTC        HIFDetachHTC
HIFExchangeBMIMsg       HIFDiagReadMem      HIFDiagWriteMem
```

**`CONFIRMED`**: `hif_queue_alloc = 1`. `HIFGetFreeQueueNumber` **allocates** a queue at runtime.

That answers the question the stage implies: there is **no CE0 = WMI, CE1 = HTT TX** table in the
binary because the assignment is **dynamic**. The logical service requests a free queue; the mapping
is decided at bring-up.

`HIFExchangeBMIMsg` is worth noting: BMI (Bootloader Messaging Interface) exchanges exist, so this is
the same two-stage bring-up shape as ath10k (BMI to load firmware, then HTC/HTT over CE).

## 5. pktlog has its own buffer lifecycle

```
pktlog_alloc_buf   pktlog_release_buf   pktlog_setsize
```

**`CONFIRMED`**: `pktlog_symbols = 12` distinct, `pktlog_lifecycle = 1`.

pktlog **allocates and releases its own buffers** and has a **settable size**. It is a separate
transport from the data path, which is consistent with ath10k's design where pktlog rides dedicated
CE channels — but **which** engines carry it cannot be determined here, because the mapping is
dynamic (§4).

## 6. MSI is negotiated, with a legacy fallback

```
%s : num_desired MSI set to %d
%s %s: ath_request_irq failed
<6>. Using PCI…
```

**`CONFIRMED`**: `msi_is_negotiated = 1` (`msi_msg = 2`).

The driver **requests a number of MSI vectors** and has an explicit fallback when `ath_request_irq`
fails. Combined with `ar9300_set_intr_mitigation_timer` (present in `ath_hal.ko`), the interrupt
configuration is a negotiation between the number of vectors the platform grants and the mitigation
the driver applies.

**`REFUTED`**: interrupt **coalescing** is still not named on the LTU side (Stage 460A: `coalesc` =
0). On the AC side the mechanism is named as **mitigation**, not coalescing.

## 7. What is established

| Claim | Status |
| :--- | :-: |
| `ath10k_core.ko` exists | **REFUTED** (0 files) |
| the ath10k CE0..CE7 service table is readable | **REFUTED** |
| the CE layer is per-engine with sweep and reap | **CONFIRMED** (24 symbols, 4 per_engine) |
| TX and RX completion are separate walkers | **CONFIRMED** (with `_nolock` paths) |
| receive flow control is watermark-based | **CONFIRMED** |
| queues are allocated at runtime | **CONFIRMED** (`HIFGetFreeQueueNumber`) |
| pktlog has its own buffer lifecycle and size | **CONFIRMED** (12 symbols) |
| MSI count is negotiated with a legacy fallback | **CONFIRMED** |
| eight engines are enumerated by name | **REFUTED** (CE0..CE7 = 0) |
| the per-engine nentries values | **UNKNOWN / runtime configuration** |

## 8. The operational reading

Three points that change how a PCIe-side problem should be investigated on this platform:

1. **a shared interrupt means a sweep** — `CE_per_engine_service_any` exists precisely because the
   handler may not know which engine fired, so "which engine is stuck" is not answered by the
   interrupt, it is answered by the per-engine state;
2. **the queue-to-service mapping is dynamic** — so a log that reports a queue number does not tell
   you which service uses it without the bring-up trace;
3. **the receive path is watermark-controlled** — a stalled RX ring is more likely a watermark or
   `recv_entries_avail` accounting problem than a lost interrupt.

The `nentries` figures the stage asks for are per-engine runtime configuration and are not in the
module.

## 9. Gaps

- **`UNKNOWN`** — the per-engine `nentries` values; the only `nentries=%d` in the module is a DFS
  command log.
- **`UNKNOWN`** — which engine carries pktlog.
- **`UNKNOWN`** — the engine→service map at bring-up; it is decided dynamically.
- **`UNKNOWN`** — whether the vendor CE count matches the ath10k eight.
- **`UNKNOWN`** — the watermark defaults and the overflow behaviour.
- **Known limit** — a per-engine API proves indexing, not a fixed count.
- **Not attempted** — dynamic validation, PCIe trace capture.
