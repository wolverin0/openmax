<!-- doc-head: STAGE499A_QCA988X_DFS_RADAR_PULSE_DETECTOR_AND_CAC_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 499A — DFS radar discrimination, false-radar immunity and CAC

- **Receipt**: [`artifacts/autoresearch/stage499a_qca988x_dfs_radar_pulse_detector_and_cac_re.json`](../artifacts/autoresearch/stage499a_qca988x_dfs_radar_pulse_detector_and_cac_re.json)
- **Tool**: [`tools/re/build_stage499a_qca988x_dfs_radar_pulse_detector_and_cac_re.py`](../tools/re/build_stage499a_qca988x_dfs_radar_pulse_detector_and_cac_re.py)
- **Scope**: offline static. No firmware loaded, no module loaded, no radio contacted, nothing transmitted.

## 0. Five `ath_dfs.ko` variants, no firmware

| Image | `ath_dfs.ko` bytes |
| :--- | :-: |
| `WA.v8.7.25` | 203,796 |
| `XC.v8.7.25` | 203,796 |
| `XC.v8.7.4cs` | 199,932 |
| `XW.v6.1.4` | 191,100 |
| `XW.v6.3.6` | 176,248 |

`firmware-2.bin` **0**, `firmware-5.bin` **0**. Sixth time in this series. Every figure below is from
the kernel module.

## 1. Four independent discriminator families — not one

The stage asks for "a pulse width / PRI / chirp discriminator". The module has **four**:

| Family | Symbols | Hits in WA |
| :--- | :--- | :-: |
| **bin5** | `dfs_bin5_check`, `dfs_bin5_check_pulse`, `dfs_bin5_addpulse` | **9** |
| **bin / fixed-pattern** | `dfs_bin_check`, `dfs_bin_fixedpattern_check`, `dfs_bin_pri_check`, `dfs_bin_resolution` | **5** |
| **chirp** | `dfs_check_chirping`, `dfs_check_chirping_merlin`, `DFS_chirp_protect` | **2** |
| **PRI blacklist** | `PRI_black_list`, `PRI_black_list_delta`, `DFS_check_PRI_blakc_list` | **3** |

**`CONFIRMED`**: `discriminator_family_count = 4`. Radar detection is a **committee of independent
tests**, not a single threshold. That is the correct architecture for DFS — each family catches a
different pulse shape, and the verdict is combined.

**`CONFIRMED`**: the resolution is computed, not hard-coded —
`dfs_get_bin_resolution_dhz`, plus `dfs_get_base_dfs_filter_threshold` and
`dfs_get_adjusted_filter_threshold`, so the filter floor is **adjusted per channel bandwidth**.

## 2. The chirp test is per-chip

`chirp_is_per_chip = 1`. The name `dfs_check_chirping_merlin` is real (it lives in the name table,
not `.symtab` — the same string-vs-symbol distinction as `ad9361` in 486A and `ring_*` in 460A).

**`CONFIRMED`**: Merlin is the AR93xx generation, so the chirp discriminator is **chip-specific**.
A generic chirp test did not ship; the vendor specialised it per radio generation. On a QCA988x the
generic path plus the Pulse/`FF` counters (`DFS_pulse_cntr_FF`, `DFS_pulse_stream_stats`) do the
work.

## 3. A third vendor typo: `blakc`

```
DFS_check_PRI_blakc_list          <-- "blakc", not "black"
PRI_black_list
PRI_black_list_delta
```

**`CONFIRMED`**: the checker is misspelled. A `grep -r black_list` finds the two lists and
**misses the checker** — the same trap as `ath_net80211_reset_pasued_tid` in Stage 459A.

`pri_blacklist_typo = 1`.

The `_delta` companion is worth noting: the blacklist stores an **offset**, not an absolute PRI, so
the same list survives a clock-domain change.

## 4. False-radar immunity is a real, tunable surface

| Knob | Runtime message |
| :--- | :--- |
| `DFS_SET_FALSE_RSSI_THRESHOLD` | `false RSSI threshold now = %d` |
| `DFS_SET_FILTER_RSSI_OFFSET` | `RSSI filter offset is now %d` |
| `DFS_SET_PRI_MULTIPLIER` | `DFS PRI multiplier is now / override is now %d` |
| `DFS_SET_MUTE_TIME` | mute window |

And the decision itself:

```
setting false_detect to TRUE. rssi=%d thresh=%d rsfr->peak_m…
```

**`CONFIRMED`**: false-radar rejection is **RSSI-gated** — a detection below the false-RSSI
threshold is discarded. **`CONFIRMED`**: the threshold, the filter offset and the PRI multiplier are
all **operator-overridable at runtime** (3 of 5 images expose the false-RSSI knob, all 5 expose the
PRI multiplier).

That is exactly the "false-radar immunity filter" the stage asks about, and it is a **tunable**, not
a fixed constant — which means a park suffering spurious DFS events has knobs to try.

## 5. CAC: a millisecond override, not a 60/600 constant

| Knob | Message | Images |
| :--- | :--- | :-: |
| `DFS_SET_CAC_TIME_OVERRIDE_MS` | `cac time override = %d se…` | **5 / 5** |
| `DFS_SET_IGNORE_CAC` | `ignore cac = %d` | 3 / 5 |

**`CONFIRMED`**: the CAC duration is expressed in **milliseconds** and is **overridable**.

**`REFUTED`**: neither `60` nor `600` is recoverable as a CAC constant.
`cac_600_literals = 0` across all five images. The 23 byte-pair hits for `60` are worthless as
evidence — that pair matches any decimal text in the module.

So the "60 s / 600 s state machine" is **not** two literals in the binary. It is a delay computed
from the channel's DFS band plus the override — and the computation was not decoded.
`cac_constant_recovered = 0`.

## 6. The asymmetry that matters most: XW has no bin detectors

| Image | bin5 | bin | chirp | PRI blacklist |
| :--- | :-: | :-: | :-: | :-: |
| `WA.v8.7.25` | **9** | **5** | 2 | 3 |
| `XC.v8.7.25` | **9** | **5** | 2 | 3 |
| `XC.v8.7.4cs` | **9** | **5** | 2 | 3 |
| `XW.v6.1.4` | **0** | **0** | **0** | **0** |
| `XW.v6.3.6` | **0** | **0** | 1 | 3 |

**`CONFIRMED`**: the **bin5 and bin/fixed-pattern detectors exist only in the AC images.** Neither
M5 image carries them at all, and XW 6.1.4 carries **no** discriminator family whatsoever — not even
the PRI blacklist.

Two readings, and this stage does not choose between them:

1. on the M5 line the bin detectors live in a **different module** (or in firmware), and
   `ath_dfs.ko` there is a thinner shim;
2. the M5 line genuinely relies on fewer discriminator families and leans on the PRI blacklist plus
   the spectral/`phyerr` path.

Either way, **an M5 radio and an AC radio do not run the same radar detection code**, and a
compliance question answered on one line does not transfer to the other. That is a bench-relevant
fact, not a curiosity.

## 7. What is established

| Claim | Status |
| :--- | :-: |
| `firmware-2.bin` / `firmware-5.bin` exist | **REFUTED** (0 files) |
| there are four independent discriminator families | **CONFIRMED** |
| the chirp test is per-chip (`_merlin`) | **CONFIRMED** |
| the PRI checker is misspelled `blakc` | **CONFIRMED** |
| false-radar rejection is RSSI-gated and tunable | **CONFIRMED** |
| the false-RSSI / filter-offset / PRI-multiplier knobs exist | **CONFIRMED** |
| CAC is a millisecond override | **CONFIRMED** |
| the 60 s / 600 s durations exist as literals | **REFUTED** |
| bin5 / bin detectors exist on XW | **REFUTED** (0 in both M5 images) |
| the pulse-width and PRI threshold tables | **UNKNOWN / not extracted** |
| the CAC duration computation | **UNKNOWN / not decoded** |

## 8. Gaps

- **`UNKNOWN`** — the pulse-width bins and their edges; `dfs_get_bin_resolution_dhz` computes a
  resolution but the table was not read.
- **`UNKNOWN`** — the PRI multiplier's default and range.
- **`UNKNOWN`** — how the four families are combined into a verdict (any-of? quorum? per-family
  confidence?).
- **`UNKNOWN`** — the false-RSSI threshold's default value; the message prints it at runtime only.
- **`UNKNOWN`** — the CAC computation, and whether the 600 s case is derived from a channel list.
- **`UNKNOWN`** — what replaced the bin detectors on XW.
- **Known limit** — a symbol name proves a test exists, not that it fires.
- **Not attempted** — dynamic validation, on-air radar injection.
