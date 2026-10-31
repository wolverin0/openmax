<!-- doc-head: Stage 926A - fifty caldata dumps of 65536 bytes collapse to ten unique digests with both ART blocks present everywhere, no .20 dump exists, board.bin does not exist as a file, and the 2116 plus XOR header invariant is refuted at offset 0x1000 where the first word reads 514 instead -->
# Stage 926A — caldata and board-data audit

- **Receipt**: [`artifacts/autoresearch/stage926a_wa_caldata_and_board_bin_audit.json`](../artifacts/autoresearch/stage926a_wa_caldata_and_board_bin_audit.json)
- **Tool**: [`tools/re/dissect_stage926a_wa_caldata_and_board_bin_audit.py`](../tools/re/dissect_stage926a_wa_caldata_and_board_bin_audit.py)
- **Scope**: read-only. No dump modified, no radio contacted.

## 0. The class, measured

```
dumps = 50   unique digests = 10   both ART blocks = 50
device .20 = 0   board.bin = 0   ambiguous = 0
```

**`REFUTED`**: `device_20_dumps = 0`. There is **no `.20` caldata dump** in this corpus. The stage names
a device whose calibration was never captured here.

My first version of the detector reported **42** `.20` dumps; that was a substring defect, because `_20`
matches the date fragment in names like `backup_20261019`. Tightening the pattern to `.20` followed by a
non-digit gives the true count, which is **zero**.

**`REFUTED`**: `board_bin_files = 0`. Neither `board.bin` nor `board-2.bin` exists as a file.

## 1. What the fifty dumps actually are

All fifty are **65,536 bytes**, matching the `mtd5` caldata partition on these boards, and they collapse
to **10 unique digests** — the same backup copied into several evidence directories.

| Property | Result |
| :--- | :-: |
| size exactly 65,536 | **50 / 50** |
| unique digests | **10** |
| 2.4 GHz block at `0x1000` non-zero | **50 / 50** |
| 5 GHz block at `0x5000` non-zero | **50 / 50** |
| both blocks present | **50 / 50** |
| ambiguous dumps | **0** |

**`CONFIRMED`**: no dump is a zeroed or malformed read. Whatever else is in dispute, the calibration
data is present in every artefact of this class.

## 2. The board-header invariant is refuted here

The loader-side rule is a **2,116-byte** board-data header whose first 16-bit word equals **2116** and
whose 16-bit XOR equals **0xFFFF**. The tool applies it at `0x1000`.

**`REFUTED`**: `board_header_valid_24 = 0` — **zero** of fifty dumps satisfy it, and the observed first
word is **514**.

That is a useful result rather than a failure. It says the 2,116-byte header invariant belongs to board
data **inside the firmware container** (`otp_AR9888v2_bin` and similar), **not** to the `mtd5` ART
partition at offset `0x1000`. Applying it there was my error, and the measurement corrects it.

So the check is retained in the tool as a **refutation**, not as a validator: it documents that this
invariant does not describe caldata, which prevents a future stage from "fixing" the dumps to satisfy a
rule that never applied to them.

## 3. What is established

| Claim | Status |
| :--- | :-: |
| a `.20` caldata dump exists here | **REFUTED** (0) |
| `board.bin` / `board-2.bin` exist as files | **REFUTED** (0) |
| the dump class is 50 files of 65,536 bytes | **CONFIRMED** |
| they reduce to 10 unique digests | **CONFIRMED** |
| both ART blocks are present in every dump | **CONFIRMED** (50 of 50) |
| the 2,116-byte header rule holds at `0x1000` | **REFUTED** (first word 514) |
| device attribution is reliable | **UNKNOWN** — it comes from the directory path |

## 4. The operational reading

1. **Ten unique dumps, not fifty.** Treating each path as an independent sample would overstate the
   evidence fivefold.
2. **Calibration is present everywhere**, so a zeroed-ART failure mode is not what is wrong with this
   corpus; the gaps are attribution and the missing devices, not the data.
3. **Do not apply the board-data checksum to `mtd5`.** It is the wrong partition for that rule, and this
   stage proves it on fifty files.

## 5. Gaps

- **`UNKNOWN`** — the true owner of each unique digest; paths are the only attribution available.
- **`UNKNOWN`** — the structure of the 2,116-byte header's actual home inside the firmware.
- **Blocked** — no `.20` dump and no `board.bin` file exist to complete the stage as titled.
- **Known limit** — a non-zero ART block is not proof of a valid calibration, only of content.
- **Not attempted** — reading any device, any dynamic validation.
