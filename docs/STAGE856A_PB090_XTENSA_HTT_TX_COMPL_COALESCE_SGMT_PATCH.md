<!-- doc-head: Stage 856A - PB-090 coalescence is not buildable because the delimited uppercase transfer anchors return zero in the container and in all seven kit images, so the builder emits a plan with patch_emitted zero and the hexa-patch stands at three of six gates blocked by one policy decision and two missing anchors -->
<!-- /doc-head -->
# Stage 856A — PB-090 HTT TX-completion coalescence and the hexa-patch manifest

- **Receipt**: [`artifacts/autoresearch/stage856a_pb090_xtensa_htt_tx_compl_coalesce_sgmt_patch.json`](../artifacts/autoresearch/stage856a_pb090_xtensa_htt_tx_compl_coalesce_sgmt_patch.json)
- **Tool**: [`tools/firmware/build_stage856a_pb090_xtensa_htt_tx_compl_coalesce_sgmt_patch.py`](../tools/firmware/build_stage856a_pb090_xtensa_htt_tx_compl_coalesce_sgmt_patch.py)
- **Scope**: offline static. No firmware written, no flash touched, no radio contacted.

## 0. A false positive I had to remove from my own tool

The first run reported **`images_with_anchor = 6`** of 7. That was wrong.

My anchor set was `htt`, `TX_COMPL`, `t2h`, `ring`, counted as **case-sensitive substrings**. The
problem is `ring`: it occurs inside ordinary printable ASCII — `string`, `during`, `monitoring` — and
`htt` can occur inside other words too. Six of seven payloads matched on that basis.

The predicate was tightened to **delimited uppercase tokens**:

```
(?<![A-Za-z0-9])HTT_      TX_COMPL
(?<![A-Za-z0-9])T2H[_A-Z]      (?<![A-Za-z0-9])RING_
```

**`REFUTED` after the fix**: `images_with_anchor = 0`.

This is the twelfth substring trap of the series and the **second one I authored**. It is recorded
rather than silently corrected, because `ring` is precisely the kind of short English word that looks
like a firmware token and is not.

## 1. PB-090 is not buildable

A coalescence patch needs a **per-completion boundary** to coalesce. The probes say:

| Probe | Container | 7 kit images |
| :--- | :-: | :-: |
| `HTT_` (delimited) | 0 | 0 |
| `TX_COMPL` | 0 | 0 |
| `T2H_` (delimited) | 0 | 0 |
| `RING_` (delimited) | 0 | 0 |

**`CONFIRMED`**: `container_anchor_present = 0`, `images_with_anchor = 0`, across **4** anchors and
**7** images — 1,214 long ASCII runs inspected between them.

**`REFUTED`**: `patch_emitted = 0`. The builder emits:

1. per-image size, SHA-256, `SGMT` tag count, ASCII-run census and the four anchor results;
2. the container probe with the same predicate;
3. the hexa-patch manifest with a **stated reason per gate**.

## 2. The hexa-patch stands at 3 of 6

| Gate | State | Reason |
| :--- | :---: | :--- |
| **PB-040** | applied | anchored rename, 4-byte diff, 3 roles measured |
| **PB-050** | applied | kit-badged, live silicon qualification on record |
| **PB-060** | applied | kit-badged, autonomous-search pilot on record |
| **PB-070** | **missing** | policy-locked (`LOCKED_CONCENTRATE_ON_MAC_AND_POLICY`) |
| **PB-080** | **missing** | no queue anchor in any container or kit image |
| **PB-090** | **missing** | no transfer anchor in any container or kit image |

**`CONFIRMED`**: `hexa_complete = 3`, `hexa_missing = 3`, `hexa_completion_fraction = 0.5`.

Note the arithmetic against Stage 833A: there the **penta**-patch was 3 of 5 and PB-090 did not exist.
Adding a sixth gate with the same two blockers lowers the fraction from `0.6` to `0.5` while the
number of applied gates stays at **3**. A completion fraction can fall without any regression, and a
reader comparing the two stages should compare the **count**, not the fraction.

## 3. Three gates fail for three different reasons

**`CONFIRMED`**: `blocked_by_policy = 1`, `blocked_by_anchor = 2`.

1. **PB-070 — policy.** The verdict is `LOCKED_CONCENTRATE_ON_MAC_AND_POLICY`. This is a **decision**
   already taken, not missing evidence. More analysis does not move it.
2. **PB-080 — evidence.** No queue vocabulary exists in the container (Stage 832A) or in the seven
   payloads (Stage 833A).
3. **PB-090 — evidence.** No transfer vocabulary exists, measured twice: in the container by Stage 855A
   and in the payloads here.

Conflating the three would misdirect the work. One needs an operator decision; two need evidence that
the corpus does not contain at any address.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| the 7 kit images exist | **CONFIRMED** (Stage 833A) |
| any image carries a delimited transfer anchor | **REFUTED** (0 of 7) |
| the container carries one | **REFUTED** (0 of 4 probes) |
| the first run's 6-of-7 result was right | **REFUTED** (`ring` inside `string`) |
| PB-040, PB-050, PB-060 are applied | **CONFIRMED** (from receipts and kit filenames) |
| PB-070 is policy-locked | **CONFIRMED** (verdict string on record) |
| PB-080 and PB-090 lack anchors | **CONFIRMED** (independent measurements) |
| a PB-090 patch was emitted | **REFUTED** (`patch_emitted = 0`) |

## 5. The operational reading

For anyone who wants PB-090, the order of work is fixed by the cascade:

1. **PB-070 first** — it is policy-locked, so it needs a decision, and everything after it is
   unreachable while it stays locked;
2. **PB-080 and PB-090 next** — both need an anchor that does not exist, so they need either a
   disassembly or a dynamic observation, neither of which is available offline;
3. **do not** spend effort on a PB-090 payload before PB-070 moves, since the gate cannot be reached.

The manifest is intentionally a **plan with zero bytes written**. Three applied gates, three missing,
and each missing gate carries the reason it is missing.

## 6. Gaps

- **`UNKNOWN`** — whether the kit filename badges correspond to verified in-payload changes.
- **`UNKNOWN`** — any coalescence boundary, since no completion ring is identifiable.
- **Blocked** — PB-070 policy, PB-080 anchor, PB-090 anchor.
- **Known limit** — a plan over 7 real images is still not a patch.
- **Not attempted** — any write, any flash operation, any dynamic validation.
