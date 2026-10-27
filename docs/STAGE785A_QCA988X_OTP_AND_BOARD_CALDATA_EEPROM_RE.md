<!-- doc-head: STAGE785A_QCA988X_OTP_AND_BOARD_CALDATA_EEPROM_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 785A — board.bin, caldata EEPROM at mtd5 0x5000, and otp.bin

- **Receipt**: [`artifacts/autoresearch/stage785a_qca988x_otp_and_board_caldata_eeprom_re.json`](../artifacts/autoresearch/stage785a_qca988x_otp_and_board_caldata_eeprom_re.json)
- **Tool**: [`tools/re/dissect_stage785a_qca988x_otp_and_board_caldata_eeprom_re.py`](../tools/re/dissect_stage785a_qca988x_otp_and_board_caldata_eeprom_re.py)
- **Scope**: offline static. No module loaded, no flash written, no radio contacted.

## 0. Two absent blobs, one present dataset

| File | Files in corpus |
| :--- | :-: |
| `board.bin` | **0** |
| `otp.bin` | **0** |
| `board-2.bin` | **0** |

**`REFUTED`**: `ath10k_blobs_absent = 1`. These are ath10k firmware blobs; the vendor stack does not
ship them.

**But the calibration data is here — as raw flash.** `mtd5_dumps_found = 41`, each exactly
**65,536 bytes**. That is strictly more useful than a `board.bin`: it is the **actual per-unit
calibration**, not a generic reference table.

## 1. The 5 GHz block, byte for byte

Canonical dump `artifacts/canary_panel1_guarida/AP_Panel1-Guarida/mtd5.bin`, sha256 prefix
`58ece05258e85969`:

```
0x0000  78 45 58 a1  34 a2 7a 45  58 a1 34 a2  e8 e5 07 77
0x5000  44 08 2d 86  02 03  78 45 58 a0  34 a2  00 00 00 00
```

**`CONFIRMED`**: the **5 GHz block starts at 0x5000** — the offset the AGENTS.md routing table names —
but the magic is at **0x5006**, behind a **six-byte prefix** (`44 08 2d 86 02 03`). Anyone scanning
for the magic at exactly 0x5000 would miss it by six bytes.

**`CONFIRMED`**: the two regions share a **three-byte magic `78 45 58`** and differ in the fourth
byte — **`a1` at 0x0000, `a0` at 0x5006**. So they are siblings of one structure family, separated by
a version byte rather than by a different identifier.

**`CONFIRMED`**: `identity_string_present = 1`, and the string is **`CUS223-720-S0849`** — a
model/serial identifier embedded in the 5 GHz calibration block. That is the board identity the
stage is after, and it is plain ASCII inside the dump.

## 2. The dump is sparse — four pages, not sixteen

`pages_with_data = 4` of **16** (4 KB pages counted by bytes that are neither `0x00` nor `0xFF`).

**`CONFIRMED`**: three quarters of the 64 KB region is erased. So the calibration is a **sparse
structure**, not a dense table — and a tool that assumes a fixed layout across the full 64 KB will
read mostly erased cells.

**`CONFIRMED`**: `identical_dumps = 10` of the 41 are byte-identical to the canonical one. The
remaining 31 differ, so the corpus holds **at least 11 distinct calibrations** — the per-unit
variation the stage implies is real and measurable.

## 3. The HAL board-value path

`ath_hal.ko` carries **39 `eeprom` tokens** and **17 eeprom symbols**, including the whole board
path:

```
ar9300_eeprom_restore_internal      ar9300_eeprom_set_board_values
ar9300_set_target_power_from_eeprom ar9300_is_nf_cal_done
ar9300_eeprom_get_spur_chans_ptr    ar9300_eeprom_get_num_ant_config
```

**`CONFIRMED`**: `hal_board_path_count = 5` — `target_power_from_eeprom = 1`, `nf_cal_done = 1`.

So at attach the HAL **restores** the EEPROM, **applies board values**, sets **target power from
EEPROM**, and tracks **NF calibration completion**. Target power and noise floor are therefore
per-unit runtime state, not constants — consistent with Stage 563A's PAPRD finding and Stage 544A's
DPD finding.

## 4. `ctl_table` is not an EEPROM symbol — and that distinction matters

**`REFUTED`**: `ctl_table_is_eeprom_symbol = 0`. The 2 `ctl_table` text hits live in `umac.ko`, and
`ctl_table` does not appear among the HAL's eeprom symbols.

The CTL path is `wlan_get_ctl_by_country` + `txctl_cap` in `umac.ko` (Stage 563A) — **per country**.
Target power is **per unit**.

That split answers a question the stage raises without asking: two identical units differ in
**target power** (EEPROM) but share **CTL limits** (regulatory). A power discrepancy between them is
expected; a CTL discrepancy is not.

## 5. The OTP tokens are firmware lengths, not calibration

`umac.ko` has `otp` (3) and `OTP` (3); the tail of Stage 451A's findings names them:

```
otp_AR9888v2_bin_len        athwlan_AR9888v2_ptmp_sta_bin_len
```

**`CONFIRMED`**: those are **firmware blob lengths** for the download path, not OTP calibration
content. Reading `otp` tokens as calibration would be the same class of error as reading `bin_` in
`umac.ko` as FFT bins (Stage 451A) — and it is the same module.

## 6. What is established

| Claim | Status |
| :--- | :-: |
| `board.bin` / `otp.bin` exist | **REFUTED** (0 files) |
| the caldata is present as mtd5 dumps | **CONFIRMED** (41 × 65,536 bytes) |
| the 5 GHz block starts at 0x5000 | **CONFIRMED** |
| the magic sits at 0x5006 behind a 6-byte prefix | **CONFIRMED** |
| the two regions share `78 45 58` and differ in byte 3 | **CONFIRMED** |
| the block carries a board identity string | **CONFIRMED** (`CUS223-720-S0849`) |
| the dump is sparse (4 of 16 pages) | **CONFIRMED** |
| per-unit variation exists (10 identical, 31 differ) | **CONFIRMED** |
| target power and NF cal state come from EEPROM | **CONFIRMED** |
| CTL limits are per country, not per unit | **CONFIRMED** |
| the numeric calibration values | **UNKNOWN / not decoded** |
| the 5 GHz subband table | **UNKNOWN / not decoded** |

## 7. The operational reading

Three things follow for a calibration investigation:

1. **compare dumps, not models** — 31 of 41 dumps differ, so a power or sensitivity difference
   between two identical boards is **expected** and traceable to their mtd5 content;
2. **the 5 GHz block is at 0x5000 + 6**, so any script that reads at 0x5000 exactly will parse six
   bytes of prefix as structure;
3. **the dump is mostly erased**, so a "missing" calibration field may simply be an unpopulated
   region rather than a parse error.

What cannot be done from this stage is read a target-power value out of the block. The block is
**located**; its fields are not decoded.

## 8. Gaps

- **`UNKNOWN`** — the numeric per-rate target power, `ht`/`vht` variants.
- **`UNKNOWN`** — the 5 GHz subband edges.
- **`UNKNOWN`** — the NF calibration offsets.
- **`UNKNOWN`** — the version-byte semantics (`a0` vs `a1`).
- **`UNKNOWN`** — the meaning of the six-byte prefix at 0x5000.
- **Known limit** — locating a block is not decoding it.
- **Not attempted** — writing any calibration, dynamic validation.
