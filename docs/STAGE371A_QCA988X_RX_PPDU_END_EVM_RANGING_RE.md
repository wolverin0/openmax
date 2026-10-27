<!-- doc-head: STAGE371A_QCA988X_RX_PPDU_END_EVM_RANGING_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 371A — QCA988x `rx_ppdu_end` descriptor, EVM per stream and ranging

- **Receipt**: [`artifacts/autoresearch/stage371a_qca988x_rx_ppdu_end_evm_ranging_re.json`](../artifacts/autoresearch/stage371a_qca988x_rx_ppdu_end_evm_ranging_re.json)
- **Tool**: [`tools/re/qca988x_rx_ppdu_end_84byte_evm_ranging_re.py`](../tools/re/qca988x_rx_ppdu_end_84byte_evm_ranging_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Two premises fail before the analysis starts

**`ath10k_core.ko` does not exist.** A recursive glob for `ath10k*.ko` under `artifacts/`
returns **0 files**. The airOS 8 AC images ship the **vendor** stack (`umac.ko` + `ath_dev.ko`),
not mainline `ath10k`.

**The descriptor field names are absent.** Exact-string counts in `umac.ko`:

| Field | `umac.ko` | `ath_dev.ko` |
| :--- | :-: | :-: |
| `rx_ppdu_end` | **0** | 0 |
| `evm_p0` | **0** | 0 |
| `evm_p15` | **0** | 0 |
| `locationing_timestamp` | **0** | 0 |
| `ppdu_end` | **0** | 0 |
| **`htt_rx_amsdu_pop`** | **4** | 0 |

**`CONFIRMED`**: the 84-byte `rx_ppdu_end_qca988x` structure with `evm_p0..evm_p15` is a
**mainline ath10k** layout. It is not named in these binaries. Nothing is reported as if it were.

## 1. What is real

**`htt_rx_amsdu_pop` is present in `umac.ko`, 4 raw hits in each image.** That is the function
the task names as the place where `skb_pull` discards the descriptor.

So the **discard path exists**; what does not exist under the expected name is the descriptor it
discards. Those are separable claims and the receipt keeps them separate.

`ath_dev.ko` has neither.

## 2. Geometry constants

The tool looked for the descriptor geometry as immediates inside the pop function:
84 (size), 72 (dword 18 byte offset), 19 / 21 (dword counts), 16 (EVM pairs).

**Result: `{}` — none of those constants appear** in the `htt_rx_amsdu_pop` functions of either
image.

That is consistent with the absence of the descriptor: if the structure were consumed there, at
least one of its size or offset constants would be materialised. It is not.

## 3. The ranging arithmetic — the one thing that checks out

The task states 80 MHz sampling gives 12.5 ns, and 12.5 ns gives 1.87 m.

| Quantity | Value |
| :--- | :--- |
| Sample interval at 80 MHz | **12.5 ns** |
| Round-trip metres per ns (`c/2`) | 0.149896 |
| **Round-trip resolution** | **1.8737 m** |

**`CONFIRMED`**: the arithmetic is right. 12.5 ns × 0.1499 m/ns = **1.874 m**, which is the
1.87 m in the task.

**`UNKNOWN`**: whether any field in this stack actually timestamps at that resolution. A correct
constant is not evidence of a working ranging path — it is evidence that the physics was
computed correctly.

## 4. Why this matters

The task described a genuinely interesting capability: per-spatial-stream EVM in dwords 0..15 and
an 80 MHz locationing timestamp in dword 18, discarded by `skb_pull`. If that were present in the
vendor stack, it would be a signal-quality and ranging datapoint nobody currently extracts.

It is **not present under those names**. Three possibilities remain, and none is claimed:

1. the vendor stack carries an equivalent descriptor with **different field names**;
2. the vendor stack discards it earlier, before the pop function;
3. the capability is ath10k-only and never shipped in airOS 8.

Distinguishing them needs a scan of the pop function's actual `skb_pull` argument, which this
stage does not do.

## 5. Gaps

- **`UNKNOWN`** — whether a differently-named equivalent descriptor exists.
- **`UNKNOWN`** — the `skb_pull` length actually used in `htt_rx_amsdu_pop`.
- **`UNKNOWN`** — whether any timestamp field exists at all.
- **`CONFIRMED ABSENT`** — `ath10k_core.ko` and the ath10k field names.
- **Not attempted** — dynamic validation.
