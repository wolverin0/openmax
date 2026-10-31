<!-- doc-head: Stage 927A - the PowerBeam 241 and 242 backups both exist at 65536 bytes, come from different partitions mtd7 and mtd5 so identity is the wrong test, and their ART blocks differ by exactly six bytes at 0x1000 and four bytes at 0x5000 with both blocks present on both sides -->
# Stage 927A — PowerBeam `.241` and `.242` caldata comparison

- **Receipt**: [`artifacts/autoresearch/stage927a_powerbeam_241_242_caldata_comparison.json`](../artifacts/autoresearch/stage927a_powerbeam_241_242_caldata_comparison.json)
- **Tool**: [`tools/re/dissect_stage927a_powerbeam_241_242_caldata_comparison.py`](../tools/re/dissect_stage927a_powerbeam_241_242_caldata_comparison.py)
- **Scope**: read-only comparison of two backup files. No radio contacted.

## 0. Both sides exist, and they are not the same partition

```
241  stage105a_backups/241_mtd_backups/mtd7_art.bin                     65,536 B
242  stage105a_backups/242_Stock_airOS8_WA.v8.7.11/mtd5_EEPROM.bin      65,536 B
```

**`CONFIRMED`**: `sides_present = 2`, `partition_mismatch = 1`.

One is `mtd7`, the other `mtd5`. **A byte-for-byte identity test between them would be meaningless**, and
that is the first thing worth saying: the two names refer to different partitions on two different
images, so "identical" was never the right question.

## 1. The comparison that is meaningful

| Block | Offset | Differing bytes |
| :--- | :--- | :-: |
| 2.4 GHz ART | `0x1000` | **6** |
| 5 GHz ART | `0x5000` | **4** |

**`CONFIRMED`**: `block_24_identical = 0`, `block_5_identical = 0`, with **6** and **4** bytes differing
respectively.

A ten-byte total difference across two calibration blocks is the signature of **per-radio trimming** —
MAC address, power offsets, or a calibration delta — not of two unrelated layouts. Two images from
different hardware would differ across hundreds of bytes.

**`CONFIRMED`**: `both_blocks_present = 1` — both blocks are non-zero on both sides, so neither file is a
failed read.

## 2. The board-header rule does not apply here either

Stage 926A refuted the 2,116-byte header invariant at `0x1000` across fifty dumps. This stage checks the
same two files and reaches the same result: `board_header_241 = 0`, `board_header_242 = 0`.

That is a **second independent refutation** of the same assumption, and it is worth recording as such:
the invariant is not a property of the `mtd5` / `mtd7` ART partition on this platform.

## 3. What the backup is, and what it is not

The `242` file sits in a directory named `242_Stock_airOS8_WA.v8.7.11`. **`CONFIRMED`**: it is a **stock**
image, not a capture of the patched state. So this comparison characterises two radios' factory
calibration; it says nothing about whether a patch altered calibration, and a later stage must not read
it that way.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| both backups exist | **CONFIRMED** (65,536 B each) |
| they come from the same partition | **REFUTED** (`mtd7` against `mtd5`) |
| their ART blocks are byte-identical | **REFUTED** (6 and 4 bytes differ) |
| both blocks are present on both sides | **CONFIRMED** |
| the difference looks like a layout mismatch | **REFUTED** (10 bytes total) |
| the `242` file shows the patched state | **REFUTED** (stock upgrade image) |
| the 2,116-byte header rule applies at `0x1000` | **REFUTED** (both sides fail it) |
| the cause of the 10 bytes | **UNKNOWN** |

## 5. The operational reading

1. **Compare structure, not whole files**, when the partitions differ. The `mtd7`/`mtd5` mismatch makes a
   digest equality test vacuous, and the tool reports `partition_mismatch` precisely so that nobody runs
   one.
2. **Ten differing bytes is a small, specific lead.** MAC and per-radio trim are the plausible causes;
   this stage does not claim which, because it did not isolate the offsets' semantics.
3. **Do not treat `242` as post-patch evidence.** It is a stock image by directory name and by content,
   and the receipt records that.

## 6. Gaps

- **`UNKNOWN`** — what the 6 and 4 differing bytes encode.
- **`UNKNOWN`** — whether `mtd7` on the `241` device holds the same structure as `mtd5` on a stock image.
- **Blocked** — no post-patch capture of either radio exists in the corpus.
- **Known limit** — a small difference is consistent with trimming and does not prove it.
- **Not attempted** — reading either radio, any dynamic validation.
