<!-- doc-head: STAGE667A_ATH10K_HTT_TX_DESC_AND_COMP_RING_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 667A — HTT TX descriptor path and the T2H completion ring

- **Receipt**: [`artifacts/autoresearch/stage667a_ath10k_htt_tx_desc_and_comp_ring_re.json`](../artifacts/autoresearch/stage667a_ath10k_htt_tx_desc_and_comp_ring_re.json)
- **Tool**: [`tools/re/dissect_stage667a_ath10k_htt_tx_desc_and_comp_ring_re.py`](../tools/re/dissect_stage667a_ath10k_htt_tx_desc_and_comp_ring_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. `ath10k_core.ko` is not in this corpus

**0 files.** Stages 371A, 395A, 423A and 437A all hit the same wall. So:

| ath10k name | Available |
| :--- | :-: |
| `ath10k_htt_tx_32` | **no** |
| `HTT_T2H_MSG_TYPE_TX_COMPL_IND` | **no** |
| `frag_desc` | **no** |

The **vendor** HTT path is in `umac.ko`, and it is fully named. This stage dissects that instead and
states plainly which ath10k claims it cannot make.

## 1. The descriptor lifecycle is complete: 4 of 4

```
htt_tx_attach        htt_tx_detach
htt_tx_desc_alloc    htt_tx_desc_free
```

**`CONFIRMED`**: `desc_lifecycle_complete = 1` (`desc_lifecycle_count = 4`).

That is the whole object lifecycle — a descriptor is allocated from the pool, used, and returned. The
pool is per-transport, created at attach and destroyed at detach.

Two **state flags** sit on the descriptor:

```
htt_tx_desc_flag_batch_more      htt_tx_desc_flag_postponed
```

**`CONFIRMED`**: `desc_flag_count = 2`. These are the interesting part of the design:

- **`batch_more`** — this descriptor is not the last in a batch, so the target should expect more
  before acting. That is **transmit aggregation expressed as a descriptor flag**, not as a separate
  API.
- **`postponed`** — the descriptor is parked, to be submitted later. That is what a scheduler needs
  when a frame must wait for its slot.

Both are per-descriptor bits, so a single ring can carry a mixed stream of immediate, batched and
deferred frames. That is materially more flexible than a queue-level aggregation setting.

## 2. The completion path

```
htt_tx_compl_desc_id         htt_t2h_msg_handler
htt_t2h_lp_msg_handler       ol_tx_completion_handler
```

**`CONFIRMED`**: `completion_symbol_count = 4`, and all four of the ones that matter are present:

| Symbol | Role |
| :--- | :--- |
| `htt_tx_compl_desc_id` | names the **completion descriptor** that drives the ring |
| `htt_t2h_msg_handler` | the **T2H consumer** — the ring's message handler |
| `htt_t2h_lp_msg_handler` | the **low-priority** T2H handler |
| `ol_tx_completion_handler` | the **OS-side** completion that releases the buffer |

**`CONFIRMED`**: `t2h_lp_handler_present = 1`. The existence of a **separate low-priority handler**
is the design detail worth naming: T2H traffic is split by priority, so completion processing cannot
be starved by a burst of data-bearing T2H messages. In a TX-completion-driven buffer-recycling loop,
that split is what keeps the ring drained under load.

**`CONFIRMED`**: `os_completion_present = 1`. `ol_tx_completion_handler` is the point where the
buffer is handed back — the sk_buff release the stage asks about, in vendor naming.

The T2H side also carries diagnostics (`htt_t2h_stats_print`, `htt_t2h_dbg_stats_hdr_parse`,
`htt_t2h_tx_ppdu_log_print`), so the ring's behaviour is observable.

## 3. Two ath10k concepts are genuinely absent

| Token | Hits across 4 modules |
| :--- | :-: |
| `frag_desc` | **0** |
| `aql`, `AQL` | **0** |
| `bql`, `BQL` | **0** |
| `TX_COMPL_IND` | **0** |

**`REFUTED`**: `ath10k_only_token_hits = 0`. No `frag_desc`, and **no AQL/BQL anywhere**.

This is not a renaming. AQL (Airtime Queue Limits) and BQL (Byte Queue Limits) are **mainline
mac80211** mechanisms that pace the stack by airtime and bytes. The vendor stack does not use them —
it has its own TDMA scheduler in `ubnt_poll_host.ko` (Stages 374A, 416A, 452A, 589A).

So the feedback loop the stage describes — TX completion feeding AQL/BQL — **has no vendor
equivalent**. The completion still frees buffers, but nothing paces the queue by airtime.

## 4. `peer_id` and `vdev_id` exist but only as traces

| Token | Hits |
| :--- | :-: |
| `peer_id` | **2** |
| `vdev_id` | **2** |

**`INFERRED`**: the HTT TX descriptor carries both fields, because both names appear. **`UNKNOWN`**:
their offsets and widths. Two hits each is enough to prove the vocabulary, not to lay out a struct.

`tx_desc_layout_recovered = 0`.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| `ath10k_core.ko` exists | **REFUTED** (0 files) |
| `ath10k_htt_tx_32` / `frag_desc` are readable | **REFUTED** |
| the vendor descriptor lifecycle is complete | **CONFIRMED** (4/4) |
| aggregation is a per-descriptor flag (`batch_more`) | **CONFIRMED** |
| deferral is a per-descriptor flag (`postponed`) | **CONFIRMED** |
| a completion descriptor id exists | **CONFIRMED** (`htt_tx_compl_desc_id`) |
| T2H is split into normal and low-priority handlers | **CONFIRMED** |
| the OS-side completion releases the buffer | **CONFIRMED** (`ol_tx_completion_handler`) |
| AQL / BQL exist in this stack | **REFUTED** (0 hits) |
| `peer_id` / `vdev_id` are descriptor fields | **INFERRED** (present, unlocated) |
| the 32-bit descriptor layout | **UNKNOWN / not recovered** |

## 6. The operational reading

Three things follow for a bench:

1. **aggregation and deferral are per-frame**, so a mixed workload (voice plus bulk) can share one
   ring without a queue-wide policy decision;
2. **completion processing has a priority split**, so a stalled TX ring is more likely a scheduler
   problem than a completion-starvation problem;
3. **there is no AQL/BQL pacing**, so queue depth is governed by the TDMA scheduler and the ring
   depth (`htt_rx_ring_elems` for RX, Stage 647A), not by airtime accounting.

That third point is the one that changes how a latency investigation should be framed on this
platform.

## 7. Gaps

- **`UNKNOWN`** — the 32-bit HTT TX descriptor field layout (peer_id/tid/vdev_id offsets).
- **`UNKNOWN`** — the completion ring depth and descriptor stride.
- **`UNKNOWN`** — how `batch_more` translates into target-side aggregation timing.
- **`UNKNOWN`** — what `postponed` waits for.
- **`UNKNOWN`** — the `tid` field: `tid` as a token was not isolated in this pass.
- **Known limit** — a named handler proves the ring exists, not its geometry.
- **Not attempted** — dynamic validation, on-air TX ring capture.
