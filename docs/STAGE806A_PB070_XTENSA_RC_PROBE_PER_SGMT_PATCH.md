<!-- doc-head: STAGE806A_PB070_XTENSA_RC_PROBE_PER_SGMT_PATCH.md preserved document content -->
<!-- /doc-head -->


# Stage 806A — PB-070 Xtensa RC probe, planned per SGMT segment

- **Receipt**: [`artifacts/autoresearch/stage806a_pb070_xtensa_rc_probe_per_sgmt_patch.json`](../artifacts/autoresearch/stage806a_pb070_xtensa_rc_probe_per_sgmt_patch.json)
- **Tool**: [`tools/firmware/build_stage806a_pb070_xtensa_rc_probe_per_sgmt_patch.py`](../tools/firmware/build_stage806a_pb070_xtensa_rc_probe_per_sgmt_patch.py)
- **Scope**: offline static. **No firmware written, no flash touched**, no radio contacted.

## 0. What PB-040 established, and why it constrains this builder

The PB-040 dry run mutated one named ASCII anchor:

```
UBNT_POLL_MEM_ALLOC  ->  OMAX_POLL_MEM_ALLOC
```

a **4-byte diff** at a located anchor. That method needs two things: an **anchor string** and a
**proven load base**. This builder tests both, per segment, and refuses to emit a patch when either
is missing.

## 1. Two segments, dual-endian bases that agree

| Segment | File offset | Bytes | base (LE) | base (BE) |
| :-: | :--- | :-: | :--- | :--- |
| 4 | `0x00006c` | 7,140 | `0x00980000` | `0x00009800` |
| 3 | `0x001c58` | 197,537 | `0x00980000` | `0x00009800` |

**`CONFIRMED`**: `segments = 2`. **`CONFIRMED`**: both segments report the **same** base field, and
the two endian readings differ by a factor of 256 — **neither is corroborated**. So an address-based
patch has no defensible base, and the builder does not use one.

## 2. Anchors exist — 111 of them — and none is rate-control

| Segment | Bytes | ASCII runs ≥ 8 chars |
| :-: | :-: | :-: |
| 4 | 7,140 | **42** |
| 3 | 197,537 | **69** |
| — | — | **111 total** |

**`CONFIRMED`**: `total_ascii_runs = 111`, `segments_with_anchor = 2`.

So the segments are **not** free of long printable runs. A tool that reported "no ASCII" would be
wrong. The blockers are different:

- **`anchor_looks_like_rc`** requires `RC_`, `RATE` or `RATEFIND` in the anchor;
- every one of the 111 runs fails that test.

**`REFUTED`**: `segments_viable = 0`. There is **no rate-control anchor** in either segment, so a
rename-style probe has **no target**.

This corrects a natural but wrong expectation: the firmware is not "too stripped to contain strings".
It contains 111 of them. It simply contains none that name rate control.

## 3. The builder emits a plan, not a patch

`patch_emitted = 0`, with the per-segment record carrying:

```
segment, file_offset, bytes, load_base_le, load_base_be,
ascii_runs, anchor, anchor_found, anchor_looks_like_rc, viable, reason
```

`patch_bytes_would_be = 4` — the size a rename probe *would* touch, recorded so the plan is complete
without being executable.

**`CONFIRMED`**: `blocking_reason` is stated in the receipt rather than left implicit: *"no SGMT
segment carries a rate-control ASCII anchor, so a rename-style probe has no target"*.

A patch artifact containing an offset with no anchor would be a **fabricated offset**, and this stage
does not produce one.

## 4. What would make the plan executable

| Requirement | State |
| :--- | :--- |
| an anchor with rate-control vocabulary | **absent** (0 of 111) |
| a corroborated load base | **absent** (two readings, neither proven) |
| PB-070 readiness | **false** (unmet prerequisites, `spi_flash_write_allowed: false`) |
| operator gate | **required** |

All four are unmet simultaneously. That is why the output is a plan.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| the container has two `SGMT` segments | **CONFIRMED** |
| the two endian base readings agree on one value | **CONFIRMED** (`0x00980000` / `0x00009800`) |
| that base is corroborated by a second source | **REFUTED** (no independent check exists) |
| long ASCII runs exist in both segments | **CONFIRMED** (42 and 69) |
| any run carries rate-control vocabulary | **REFUTED** (0 viable) |
| a per-segment plan is emitted with reasons | **CONFIRMED** |
| a binary patch is emitted | **REFUTED** (`patch_emitted = 0`) |

## 6. The operational reading

The useful outcome is a **negative with a precise cause**. Two failure modes look identical from
outside — "the builder produced nothing" — and this stage separates them:

1. **not stripped**: 111 ASCII runs prove the payload is not string-free;
2. **wrong vocabulary**: zero of them are rate-control anchors.

So the next attempt should not hunt harder for strings; it should either find the rate table
numerically (Stage 805A's limit) or establish the true load base from a source outside this container.

## 7. Gaps

- **`UNKNOWN`** — the true load base; the header field is ambiguous between two readings.
- **`UNKNOWN`** — whether any rate-control routine is addressable at all from the container.
- **`UNKNOWN`** — the meaning of the 111 ASCII runs; none was classified.
- **Blocked** — PB-070 is not ready and `spi_flash_write_allowed` is false.
- **Known limit** — a plan with zero viable segments is a correct output, not a failure.
- **Not attempted** — any write, any flash operation, any dynamic validation.
