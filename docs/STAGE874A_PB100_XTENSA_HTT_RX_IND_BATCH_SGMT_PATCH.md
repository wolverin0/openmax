<!-- doc-head: Stage 874A - PB-100 is not buildable because five delimited receive anchors return zero in the container and in all seven kit images, and the combined virtual-address collision check is verifiable for exactly one gate of seven since only PB-040 records per-role mutation addresses which are mutually consistent and 32 bytes apart -->
# Stage 874A — PB-100 RX indication batching and the combo VA-collision check

- **Receipt**: [`artifacts/autoresearch/stage874a_pb100_xtensa_htt_rx_ind_batch_sgmt_patch.json`](../artifacts/autoresearch/stage874a_pb100_xtensa_htt_rx_ind_batch_sgmt_patch.json)
- **Tool**: [`tools/firmware/build_stage874a_pb100_xtensa_htt_rx_ind_batch_sgmt_patch.py`](../tools/firmware/build_stage874a_pb100_xtensa_htt_rx_ind_batch_sgmt_patch.py)
- **Scope**: offline static. No firmware written, no flash touched, no radio contacted.

## 0. PB-100 is not buildable

Batching RX indications needs the indication path. Five **delimited uppercase** anchors were probed —
the same discipline Stage 856A adopted after `ring` matched `string`:

```
HTT_     RX_IND     RX_FRAG     T2H_     RING_
```

| Probe scope | Result |
| :--- | :-: |
| container (204,796 B) | **0 of 5** |
| 7 kit images (1,214 long ASCII runs) | **0 of 5** |

**`CONFIRMED`**: `container_anchor_present = 0`, `images_with_anchor = 0`, `patch_emitted = 0`.

So PB-100 is emitted as a **plan with zero bytes written**, and the reason is stated in the receipt.

## 1. The collision check is the useful half, and it is partial

The combo spans **seven** gates: PB-040, PB-050, PB-060, PB-070, PB-080, PB-090, PB-100.

Virtual addresses exist for **one** of them. Only PB-040 recorded per-role mutation addresses:

| Role | Segment base | Offset | Virtual address | Base plus offset |
| :--- | :--- | :-: | :--- | :--- |
| `ptmp_sta` | `0x0040b000` | 4988 | `0x0040c37c` | **matches** |
| `ptmp_ap` | `0x0040b000` | 5020 | `0x0040c39c` | **matches** |
| `ptp` | `0x0040b000` | 5216 | `0x0040c460` | **matches** |

**`CONFIRMED`**: `offset_base_consistent = 1` — each virtual address minus the segment base equals its
recorded offset, exactly, for all three roles. That is an internal consistency check the receipt passes.

**`CONFIRMED`**: `va_collisions = 0`, `minimum_gap_bytes = 32`.

The closest pair is `ptmp_sta` at `0x0040c37c` and `ptmp_ap` at `0x0040c39c`: **32 bytes** apart, against
**4-byte** mutations. With 4-byte writes, 32 bytes of separation is eight times the mutation width, so
those two cannot overlap.

## 2. The honest scope of the non-collision claim

**`REFUTED`**: `combo_va_verified = 0`, `combo_va_verified_fraction = 0.1429`.

| Measure | Value |
| :--- | :-: |
| gates in the combo | **7** |
| gates with a recorded virtual address | **1** |
| gates without one | **6** |
| verified fraction | **0.1429** |

Six gates carry **no address at all**, so their non-collision with PB-040 **cannot be checked**. A
verdict of "the combo does not collide" would therefore be a claim about six gates nobody has addresses
for.

That is the deliverable of this half of the stage: the combination is **non-colliding where measurable**
and **unproven everywhere else**, and the two statements are not the same.

## 3. Why the recorded addresses still carry a caveat

Even the three measured addresses inherit the base ambiguity of Stage 855A: the segment base field reads
`0x00980000` little-endian and `0x00009800` big-endian. Here the **relative** structure is what matters —
base plus offset equals address for all three roles — and that relation holds **regardless of which
reading is used**, because it is tested within one reading at a time.

So the offset consistency is robust; the **absolute** addresses are not, and nothing in this stage
resolves them.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| PB-100 has a delimited receive anchor in the container | **REFUTED** (0 of 5) |
| it has one in any of the 7 kit images | **REFUTED** (0 of 5) |
| a PB-100 patch was emitted | **REFUTED** (`patch_emitted = 0`) |
| PB-040's addresses equal base plus offset | **CONFIRMED** (3 of 3) |
| the three PB-040 mutations collide | **REFUTED** (`va_collisions = 0`) |
| the minimum separation is 32 bytes | **CONFIRMED** |
| the seven-gate combo is collision-free | **UNKNOWN for 6 gates** |
| the absolute addresses are resolved | **REFUTED** (base ambiguity inherited) |

## 5. The operational reading

1. **PB-100 cannot be placed** — no anchor, and the byte-level route is closed (Stage 873A).
2. **The collision verdict is not a combo verdict** — it covers PB-040 only, and that limitation is
   recorded in the receipt as a fraction rather than a footnote.
3. **Before any combo claim**, the other six gates need addresses. Until then the only defensible
   phrasing is "no collision where measured".

That third point is the one that survives this stage. A collision check is only as wide as the address
set behind it, and here that set is three entries deep.

## 6. Gaps

- **`UNKNOWN`** — the virtual addresses of six of the seven gates.
- **`UNKNOWN`** — the segment load base, inherited from Stage 855A.
- **Blocked** — PB-100 anchor, and combo coverage for six gates.
- **Known limit** — a plan over 7 real images is still not a patch.
- **Not attempted** — any write, any flash operation, any dynamic validation.
