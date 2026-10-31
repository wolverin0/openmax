<!-- doc-head: Stage 833A - all seven SGMT kit images exist as raw payloads with 1214 long ASCII runs between them, none carries a delimited queue anchor once the case-insensitive false positive is removed, so the Penta-Patch stands at three of five gates with PB-070 blocked by readiness and PB-080 by the absence of any anchor -->
<!-- /doc-head -->
# Stage 833A — PB-080 surgical patch plan and the Penta-Patch across 7 SGMT images

- **Receipt**: [`artifacts/autoresearch/stage833a_pb080_xtensa_peer_tid_qdepth_sgmt_patch.json`](../artifacts/autoresearch/stage833a_pb080_xtensa_peer_tid_qdepth_sgmt_patch.json)
- **Tool**: [`tools/firmware/build_stage833a_pb080_xtensa_peer_tid_qdepth_sgmt_patch.py`](../tools/firmware/build_stage833a_pb080_xtensa_peer_tid_qdepth_sgmt_patch.py)
- **Scope**: offline static. **No firmware written, no flash touched**, no radio contacted.

## 0. The 7 images are real

**`CONFIRMED`**: `images_found = 7` under `artifacts/autoresearch/kits/stage817a/`:

| Image | Bytes | ASCII runs |
| :--- | :-: | :-: |
| `OpenWrt_10.1.467-ct_IE3_pb040_pb050_pb060.sgmt.bin` | 200,943 | 71 |
| `WA.v8.7.25_ptmp_ap_pb040_pb050_pb060.sgmt.bin` | 255,669 | 196 |
| `WA.v8.7.25_ptmp_sta_pb040_pb050_pb060.sgmt.bin` | 237,993 | 201 |
| `WA.v8.7.25_ptp_pb040_pb050_pb060.sgmt.bin` | 218,498 | 174 |
| `XC.v8.7.25_ptmp_ap_pb040_pb050_pb060.sgmt.bin` | 256,559 | 197 |
| `XC.v8.7.25_ptmp_sta_pb040_pb050_pb060.sgmt.bin` | 238,872 | 201 |
| `XC.v8.7.25_ptp_pb040_pb050_pb060.sgmt.bin` | 219,367 | 174 |

Each begins with the `SGMT` tag, `01 00 00 00`, `00 00 98 00` — they are **raw SGMT payloads**, not
`QCA-ATH10K` containers. **1,214** long ASCII runs between them.

## 1. The false positive I had to remove from my own tool

The first run reported **`pb080_viable_images = 6`** of 7. That was wrong, and the cause was in my
own predicate:

```
re.search(r"TID|QDEPTH|QUEUE|PEER", s, re.I)
```

**Case-insensitive `TID` matches `identity`, `entity`, `identify`.** Any firmware with a debug string
containing "identity" would have been declared a viable PB-080 target. Six of seven images passed on
that basis.

The predicate was tightened to a **delimited uppercase token**:

```
WAL_PEER_TID | PEER_TID | QDEPTH | _TID_ | _TID\b
```

**`REFUTED` after the fix**: `pb080_viable_images = 0`.

This is the eleventh substring trap of the series, and the first one **I authored**. It is recorded
here rather than silently corrected, because the same mistake would recur in any tool that greps
short uppercase tokens case-insensitively.

## 2. The Penta-Patch stands at 3 of 5

| Gate | Baked into | State |
| :--- | :-: | :--- |
| **PB-040** | 7 / 7 | **complete** |
| **PB-050** | 7 / 7 | **complete** |
| **PB-060** | 7 / 7 | **complete** |
| **PB-070** | 0 / 7 | **missing** — blocked by readiness (Stage 809A) |
| **PB-080** | 0 / 7 | **missing** — blocked by no anchor (Stage 832A) |

**`CONFIRMED`**: `penta_complete = 3`, `penta_missing = 2`, `penta_completion_fraction = 0.6`.

The two missing gates fail for **different reasons**, and conflating them would misdirect the work:

- **PB-070** fails on **gate readiness** — its prerequisites are unmet and
  `spi_flash_write_allowed` is false. It is a permissions problem.
- **PB-080** fails on **anchor absence** — there is no queue vocabulary in any image. It is an
  evidence problem.

## 3. What the builder emits

`patch_emitted = 0`, `penta_patch_emitted = 0`, with the reason stated:

> *"no image carries a TID/QUEUE/PEER anchor, so PB-080 has no target; PB-070 is additionally blocked
> by gate readiness"*

Per image it records size, SHA-256, `SGMT` tag count, ASCII-run census, both anchors (rate-control and
queue), viability, and which gates appear in the filename.

**`CONFIRMED`**: the manifest is derived from **kit filenames**, which states **intent** rather than
proven content. A file named `..._pb040_pb050_pb060...` asserts those three gates were applied; this
stage does not independently verify each one inside the payload.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| the 7 SGMT images exist | **CONFIRMED** |
| they are raw SGMT payloads, not containers | **CONFIRMED** |
| long ASCII runs are abundant (1,214) | **CONFIRMED** |
| any image carries a delimited queue anchor | **REFUTED** (0 of 7) |
| the first run's 6-of-7 result was correct | **REFUTED** (case-insensitive false positive) |
| PB-040/050/060 are baked into all 7 | **CONFIRMED** (from filenames) |
| PB-070 and PB-080 are baked into any | **REFUTED** (0 of 7) |
| a PB-080 patch was emitted | **REFUTED** (`patch_emitted = 0`) |

## 5. The operational reading

The Penta-Patch is **60 % real and 40 % blocked**, and the blockers are of different kinds:

1. **PB-070 needs a gate opened**, not more analysis — Stage 809A recorded its unmet prerequisites;
2. **PB-080 needs an anchor that does not exist** in the corpus, so no amount of tooling resolves it.

The 7 images are a **valid base** for a future Penta-Patch: three gates are already applied and the
payloads are byte-identified by SHA-256. What is missing is one permission and one piece of evidence.

## 6. Gaps

- **`UNKNOWN`** — whether the filename badges correspond to verified in-payload changes.
- **`UNKNOWN`** — the load base of a raw SGMT payload, since it carries no container header.
- **Blocked** — PB-070 readiness and PB-080 anchor, both absent.
- **Known limit** — a plan over 7 real images is still not a patch.
- **Not attempted** — any write, any flash operation, any dynamic validation.
