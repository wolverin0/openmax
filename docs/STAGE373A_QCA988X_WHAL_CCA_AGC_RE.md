<!-- doc-head: STAGE373A_QCA988X_WHAL_CCA_AGC_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 373A — QCA988x WHAL analog CCA/AGC tables and the Xtensa SGMT payload

- **Receipt**: [`artifacts/autoresearch/stage373a_qca988x_whal_cca_agc_re.json`](../artifacts/autoresearch/stage373a_qca988x_whal_cca_agc_re.json)
- **Tool**: [`tools/re/qca988x_whal_cca_agc_register_table_re.py`](../tools/re/qca988x_whal_cca_agc_register_table_re.py)
- **Scope**: offline static. No firmware loaded, no module loaded, no radio contacted.

## 0. The container parses, and the parse is checked by tiling

`openwrt_qca988x_hw20_firmware_2_ct.bin`, **204,796 bytes**:

| Field | Value |
| :--- | :--- |
| magic | `QCA-ATH10K` |
| `version_len` | 28 |
| version | `10.1-ct-8x-__fW-022-ecad3248` |
| TLVs | **5** |
| chain end | `0x031ff9` of `0x031ffc` |
| tail pad | **3 bytes** |
| tiled | **true** |

The parse is only accepted if the chain consumes the file. It does, to within a 3-byte pad. A
parser that "finds" segments but leaves megabytes unaccounted for is wrong, and this check is what
rules that out.

| # | id | len | payload tag |
| :-: | :-: | :-: | :--- |
| 1 | 1 | 4 | — |
| 2 | 2 | 8 | — |
| 3 | 30 | 16 | — |
| 4 | **4** | **7,140** | **`SGMT`** |
| 5 | **3** | **197,537** | **`SGMT`** |

**`CONFIRMED`**: two `SGMT` segments, **204,677 bytes combined = 99.94 % of the container**. The
three control TLVs carry 28 bytes between them.

## 1. The two SGMT headers are identical except one word

Both payloads open with the same 12 bytes:

```
53 47 4d 54  01 00 00 00  00 00 98 00   <u32>
S  G  M  T   \----------- fixed -----------/
```

| Segment | bytes | u32 at payload offset 12 |
| :--- | :-: | :-: |
| id 4 | 7,140 | **148** |
| id 3 | 197,537 | **5,484** |

**`CONFIRMED`**: the prefix is a fixed 12-byte signature plus one u32.

**`UNKNOWN`**: what that u32 means. A length, a checksum or a count are all consistent; the stage
does not decide, and the receipt stores it as an uninterpreted value.

## 2. No parameter names exist in the firmware

The blob was swept for every token in the stage: `cca_thresh`, `thresh62`, `nf_cal`,
`noise_floor`, `strong_signal`, `firstep`, `cycpwr_thr1`, `cycpwr`. **Zero hits.**

**`REFUTED`**: the CCA/AGC register table cannot be located by name inside the Xtensa payload.
Firmware carries numbers; the names live on the host side. Any claim to have "found
`cca_thresh62` in the firmware" would be a fabrication.

## 3. Where the WHAL control points actually are named

`ath_hal.ko` is where the analog control surface has real function symbols:

| Image | `ath_hal.ko` bytes | WHAL tokens present |
| :--- | :-: | :--- |
| `WA.v8.7.25` | **367,456** | `cca_thresh`, `nf_cal`, `noise_floor`, `strong_signal`, `cca`, `agc` |
| `XC.v8.7.25` | **360,896** | same set |
| `XW.v6.3.6` | **503,892** | **`firstep`, `cycpwr`, `agc` only** |

Note WA and XC `ath_hal.ko` are **not** identical: 6,560 bytes apart (1.8 %), unlike `ath_dev.ko`,
which is byte-identical across the two AC images.

The named entry points, straight from the symbol table:

```
ar9300_set_cca_threshold
ar9300_is_nf_cal_done
ar9300_disable_strong_signal
ar9300_upload_noise_floor
```

**`CONFIRMED`**: four discrete analog control points exist by name. `set_cca_threshold` is the
CCA sensitivity write; `is_nf_cal_done` is the noise-floor calibration poll;
`disable_strong_signal` is the strong-signal immunity defeat; `upload_noise_floor` pushes the
computed floor into the MAC.

## 4. The ANI state is printed, and the print names the parameters

`WA/XC umac.ko` carries a debug format string that enumerates the adaptive-noise state:

```
ANI UPDATE ofdm level %d firstep %d firstep_low %d cycpwr_thr %d self_corr_low %d
```

**`CONFIRMED`**: `firstep`, `firstep_low`, `cycpwr_thr` and `self_corr_low` are the ANI
parameters, and they are emitted together in one update line. This is the closest thing in the
whole stack to a **readable CCA/AGC state vector** — five integers per channel per update.

`ath_dev.ko` adds `noise_floor=%d..%d.%03d`, a per-channel floor print with a fractional part.

## 5. XW has an INI override path the AC images do not name

The most consequential asymmetry of the stage. `XW.v6.3.6 ath_hal.ko` carries **override
messages with both the default and the INI value**:

```
%s: ** ch %d: level %d=>%d[def:%d] firstep[level]=%d ini=%d
%s: ** ch %d: level %d=>%d[def:%d] cycpwrThr1[level]=%d ini=%d
```

**`CONFIRMED`**: on the M5 line there is a per-channel, per-level **INI override** mechanism for
`firstep` and `cycpwrThr1`, and it reports the default, the requested value and the INI value side
by side.

**`CONFIRMED`**: the AC images contain no such string. They expose the four `ar9300_*` functions
instead. Two different control surfaces for the same analog quantities.

This matters directly for a `PB040-CCA-AGC-OVERRIDE` idea: the override path the stage wants is
**named and instrumented on XW**, and on WA/XC it is a direct function call. Neither path was
traced to a register write here.

## 6. What is established

| Claim | Status |
| :--- | :--- |
| container is `QCA-ATH10K` with 5 TLVs and tiles to a 3-byte pad | **CONFIRMED** |
| two `SGMT` segments hold 99.94 % of the container | **CONFIRMED** |
| both `SGMT` headers share a 12-byte prefix differing only in one u32 | **CONFIRMED** |
| CCA/AGC names exist in the firmware payload | **REFUTED** (0 hits) |
| `ar9300_set_cca_threshold` / `is_nf_cal_done` / `disable_strong_signal` / `upload_noise_floor` exist in WA/XC HAL | **CONFIRMED** |
| ANI prints `firstep` / `firstep_low` / `cycpwr_thr` / `self_corr_low` together | **CONFIRMED** |
| XW HAL has per-level `firstep` / `cycpwrThr1` INI overrides with `def:` and `ini=` | **CONFIRMED** |
| the analog register table itself | **UNKNOWN / not recovered** |
| any name → register-address mapping | **UNKNOWN / none** |

## 7. Gaps

- **`UNKNOWN`** — the numeric CCA/AGC register table. The SGMT payloads were not disassembled.
- **`UNKNOWN`** — the u32 at SGMT payload offset 12 (148 / 5,484).
- **`UNKNOWN`** — the register address written by `ar9300_set_cca_threshold`.
- **`UNKNOWN`** — whether the XW INI override accepts operator-supplied values at runtime or only
  at attach.
- **`UNKNOWN`** — the ANI tuning curve; only the state vector's shape is known.
- **Known limit** — a named function is a control point, not a table.
- **Not attempted** — Xtensa disassembly, dynamic validation.
