<!-- doc-head: STAGE415A_QCA988X_XTENSA_PLL_SUB20MHZ_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 415A — QCA988x PLL, clock dividers and sub-20 MHz timing

- **Receipt**: [`artifacts/autoresearch/stage415a_qca988x_xtensa_pll_sub20mhz_re.json`](../artifacts/autoresearch/stage415a_qca988x_xtensa_pll_sub20mhz_re.json)
- **Tool**: [`tools/re/qca988x_xtensa_pll_clock_divider_sub20mhz_re.py`](../tools/re/qca988x_xtensa_pll_clock_divider_sub20mhz_re.py)
- **Scope**: offline static. No firmware loaded, no module loaded, no radio contacted.

## 0. The PLL path is named — twice

`ath_hal.ko` exports two real defined symbols on both AC images:

```
ar9300_init_pll
ar9300_set_power_mode
```

**`CONFIRMED`**: the PLL programming entry point exists by name, and it is paired with the power
mode setter. **`UNKNOWN`**: the register sequence either one performs. A symbol is a door, not the
room behind it.

## 1. The clock names do not exist

| Identifier | Hits across 5 modules |
| :--- | :-: |
| `mac_clock` | **0** |
| `adc_clock` | **0** |
| `dac_clock` | **0** |
| `clkdiv`, `clock_div` | **0** |
| `quarter_rate`, `half_rate` | **0** |

**`REFUTED`**: none of the clock identifiers or the rate names appear as strings. On the ath9k
side these are macros and register fields, so the compiled object holds numbers, not words.

**This is expected, and it is not evidence of absence.** A name search cannot find a divider that
was never emitted as a name. What it does mean is that **the 5 MHz and 10 MHz divider values
cannot be recovered by identifier**, and the stage does not pretend otherwise.

## 2. The timing vocabulary is real, and asymmetric

| Module | Bytes | `slot_time` | `ack_timeout` | `SIFS` | `pll` | `quarter` | `chan_width` / `bw_` |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| `WA.v8.7.25:ath_hal.ko` | 367,456 | **1** | **2** | 0 | 1 | 1 | 0 |
| `XC.v8.7.25:ath_hal.ko` | 360,896 | **1** | **2** | 0 | 1 | 1 | 0 |
| `XW.v6.3.6:ath_hal.ko` | 503,892 | 0 | 0 | **2** | 0 | 1 | 0 |
| `WA.v8.7.25:umac.ko` | 2,356,432 | **2** | 0 | 0 | 2 | 1 | **1 / 4** |
| `XC.v8.7.25:umac.ko` | 2,358,768 | **2** | 0 | 0 | 2 | 1 | **1 / 4** |

**`CONFIRMED`**: `slot_time` appears in **4** modules and `ack_timeout` in **2**. The AC pair is
identical; XW is not.

**`CONFIRMED` — the asymmetry worth naming:** **`SIFS` exists only in XW `ath_hal.ko`**, and XW
carries neither `slot_time` nor `ack_timeout` nor `pll`. The M5 HAL names the inter-frame space;
the AC HAL names the slot and the ACK timeout. The two code lines instrument **different ends of
the same timing budget**.

And the XW hits are not a bare identifier — both are **runtime adjustment messages**:

```
%s: Changing SIFS from %d to %d
%s: Changing SLOT from %d to %d
%s: Restoring SIFS/EIFS/SLOT to %d
```

**`CONFIRMED`**: on XW the SIFS, slot and EIFS are **modified at runtime with before/after values
and then restored**. That is an adaptive timing override path, and it is the closest thing in the
corpus to the "SIFS / slot / ACK timing" the stage asks about. It is named `SLOT`, not
`slot_time`, which is why the AC token search does not see it.

**`UNKNOWN`**: what triggers the change, and whether any bandwidth change is among the triggers.

## 3. The SGMT payloads hold no bandwidth scalars

Census over both `SGMT` payloads (204,677 bytes), counting each bandwidth as a little-endian
value:

| Bandwidth | as `u32` | as `u16` |
| :-: | :-: | :-: |
| **5 MHz** | **1** | (see receipt) |
| 10 MHz | **0** | — |
| 20 MHz | **0** | — |
| 40 MHz | **0** | — |
| 80 MHz | **0** | — |

**`REFUTED`**: the bandwidths are not stored as `u32` scalars in the firmware payload. A single
`5` appears, and on its own it means nothing.

**`UNKNOWN`**: how bandwidth is actually encoded. A shift (`log2`), a divider ratio, or a
register-field enum would all produce this census, and the stage does not choose between them.

## 4. Why there is no divider table

A divider table would have to answer: for 5 MHz, what PLL multiplier and what post-divider. The
corpus gives neither half:

- the **names** (`mac_clock`, `adc_clock`, `dac_clock`, `quarter_rate`) are absent;
- the **values** (5/10/20/40/80) are absent as `u32` except one stray `5`;
- the **entry point** (`ar9300_init_pll`) is present but was not disassembled.

`pll_table_recovered = 0` and `divider_table_recovered = 0` are therefore not a failure of effort
— they are the correct state of the evidence. Filling them in would require the ath9k register
headers or a live register trace, neither of which is in this corpus.

## 5. What the sub-20 MHz question actually needs

A 5 MHz quarter-rate channel needs a PLL change, not just a bandwidth setting: the sampling clock
drops, so slot timing, ACK timing and the ADC/DAC rate all scale with it. The evidence above says
the naming for that chain exists only in fragments:

- `ar9300_init_pll` — the PLL door (AC only);
- `slot_time` / `ack_timeout` — the AC timing knobs;
- `SIFS` — the XW timing name;
- `quarter` — present everywhere, meaning undetermined.

**`CONFIRMED`**: no single module names the whole chain from PLL to slot timing. Whatever the
firmware does for sub-20 MHz, the host-side naming does not describe it end to end.

## 6. Gaps

- **`UNKNOWN`** — the PLL multiplier/divider for any bandwidth.
- **`UNKNOWN`** — `mac_clock`, `adc_clock`, `dac_clock` values; the identifiers do not exist.
- **`UNKNOWN`** — whether 5 MHz and 10 MHz are even supported by this HAL. Absence of a name is
  not proof of support or of refusal.
- **`UNKNOWN`** — the SIFS/slot/ACK values, and whether they scale with bandwidth.
- **`UNKNOWN`** — the meaning of `quarter` in all four modules that carry it.
- **Known limit** — one `5` in a 204 KB payload is not a divider.
- **Not attempted** — Xtensa disassembly, dynamic validation.
