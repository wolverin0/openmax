<!-- doc-head: STAGE616A_LTU_AME_CORE_RANGING_TOF_AND_TIMING_ADVANCE_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 616A — LTU ranging: distance, cpe_distance, timing advance and CP alignment

- **Receipt**: [`artifacts/autoresearch/stage616a_ltu_ame_core_ranging_tof_and_timing_advance_re.json`](../artifacts/autoresearch/stage616a_ltu_ame_core_ranging_tof_and_timing_advance_re.json)
- **Tool**: [`tools/re/build_stage616a_ltu_ame_core_ranging_tof_and_timing_advance_re.py`](../tools/re/build_stage616a_ltu_ame_core_ranging_tof_and_timing_advance_re.py)
- **Scope**: offline static. No module loaded, no radio contacted, nothing transmitted.

## 0. Two modules

`ame_core.ko` (3,282,052 bytes) and `ame_dev.ko` (298,760 bytes).

## 1. `tof` is `autofa` — the most consequential trap of the series

The stage asks for **Time-of-Flight ranging**. `tof` has **29 hits**, which looks like a strong
positive. It is not.

**Every hit sits inside `autofa`** — **auto-frequency acquisition**:

```
autofa_create_scanning_list   autofa_scan_next      autofa_get_result
autofa_run_config             autofa_set_speed      autofa_stop
autofa_get_config             autofa_get_paused     autofa_set_paused
autofa_get_scan_mode          autofa_set_scan_mode  autofa_force_freq
autofa_force_idx              autofa_get_avg_freq_range
```

**`CONFIRMED`**: `tof_is_autofa = 1`, and **15 distinct `autofa_*` symbols** carry the bytes.

**`REFUTED`**: there is **no Time-of-Flight ranging**. The corroborating tokens are all zero:

| Token | Hits |
| :--- | :-: |
| `ranging` | **0** |
| `rtt` | **0** |
| `round_trip` | **0** |

`tof_ranging_recovered = 0`.

This is the eighth substring trap of the series and the worst one yet, because `tof` is **exactly**
the acronym the stage looks for, and 29 hits is enough to convince a careless reader. The
disambiguator is context: every window contains `autofa`.

## 2. `cpe_distance` is real — distance is measured

Unlike ToF, this is a genuine positive:

```
cpe_distance                       (explicit symbol)
ame_core_get_distance_meter        (accessor)
distance_meter_show / _store       (sysfs pair, in ame_dev.ko)
```

**`CONFIRMED`**: `distance_measurement_present = 1` and `distance_sysfs_pairs = 1`.

So a per-CPE distance value **is computed, held, and exposed** — readable and writable through sysfs.
The units are in the name (`distance_meter`), and the earlier Stage 388A context showed it beside
`ptmp_ap_autopwr_tx_power_adjust_routine`, which ties distance to **automatic TX power adjustment**.

**`UNKNOWN`**: how the distance is measured. No `rtt`, no `round_trip`, no timestamp-difference
mechanism is named. It could be derived from timing advance, from RSSI, or from a ranging exchange
that is not named here — the corpus does not say, and this stage does not guess.

## 3. `timing_adv` does not exist

| Token | Hits |
| :--- | :-: |
| **`timing_adv`** | **0** |
| `ta_` | **65** |

**`REFUTED`**: there is no timing-advance identifier. The 65 `ta_` hits are **substring noise** from
`data_`, `sta_`, `delta_` and similar names — the same failure mode as `bf_` in Stage 615A, one
stage earlier.

`ta_mechanism_recovered = 0`.

That is a notable gap for a TDD PtMP system: timing advance is how a CPE aligns its uplink burst to
the AP's schedule, and Stage 564A found the UL symbol assignment record without finding any
adjustment term. Either the adjustment uses a different name, or it is computed from the distance
value in §2.

## 4. `cpsample` is the CP length, not an alignment offset

| Token | Hits |
| :--- | :-: |
| `cpsample` | **2** |
| `cp_align` | **0** |
| `cyclic` | **0** |

**`CONFIRMED`**: `cpsample` exists in `ame_dev.ko` — Stage 388A already identified it as the cyclic
prefix parameter, sitting in the frame descriptor beside `duty_cycle`, `frame_len`, `dl_symbols`,
`ul_symbols` and `gap0`.

**`REFUTED`**: there is no `cp_align` and no `cyclic` token. So the CP is **configured as a length**,
not **aligned by an offset**. The alignment Stage 564A found is `frame_pulse_offset`, which is a
frame-start offset, not a CP offset.

`cp_alignment_offset_recovered = 0`.

## 5. The bonus: `autofa` is a whole subsystem

The trap uncovered something real. 15 symbols cover:

- **scan list construction** (`create_scanning_list`) and **stepping** (`scan_next`);
- **result retrieval** (`get_result`) and **average frequency range** (`get_avg_freq_range`);
- **configuration** (`get_config`, `run_config`, `set_scan_mode`, `get_scan_mode`);
- **speed control** (`set_speed`) and **pause** (`get_paused`, `set_paused`);
- **forced frequency** (`force_freq`, `force_frequency`, `force_idx`, `force_idx_end`,
  `force_in_dl`);
- **stop** (`autofa_stop`).

**`CONFIRMED`**: this is materially more than the "auto-frequency hooks" Stage 590A recorded from the
sysfs side. `force_in_dl` is the notable one: acquisition can be **forced from the downlink**, which
is what a CPE scanning on instruction from its AP looks like.

A naming note worth keeping: **15 of these are ELF symbols**, while `autofa_create_scanning_list`
and `autofa_scan_next` appear only as **string-level names** — the same symbol-versus-name
distinction as `ad9361` in Stage 486A and `dfs_check_chirping_merlin` in Stage 499A. Both are real
identifiers; only one of the two kinds is linkable.

## 6. What is established

| Claim | Status |
| :--- | :-: |
| `tof` means Time-of-Flight here | **REFUTED** (all 29 inside `autofa`) |
| a ToF ranging mechanism exists | **REFUTED** (`ranging`/`rtt`/`round_trip` all 0) |
| a per-CPE distance is computed and exposed | **CONFIRMED** (`cpe_distance`, sysfs pair) |
| `timing_adv` exists as an identifier | **REFUTED** (0 hits) |
| the `ta_` count is timing advance | **REFUTED** (substring noise) |
| `cpsample` is the CP length parameter | **CONFIRMED** |
| a CP alignment offset is named | **REFUTED** (`cp_align`, `cyclic` = 0) |
| an auto-frequency acquisition subsystem exists | **CONFIRMED** (15 `autofa_*` symbols) |
| the distance measurement source | **UNKNOWN / not named** |
| the timing-advance mechanism | **UNKNOWN / not found** |

## 7. The operational reading

Three things are separately true, and mixing them is the error this stage avoids:

1. **a distance value exists** and is exposed in metres through sysfs — that is usable today;
2. **timing advance is not named**, so uplink alignment cannot be audited from the binary;
3. **ToF ranging does not exist here**, despite 29 `tof` hits — the hits are channel scanning.

For a park trying to explain a distance-scaled behaviour (Stage 388A showed `distance_meter` beside
the auto-power routine), the distance knob is the handle. For an uplink-alignment question, the
corpus offers nothing named, and a bench would have to measure the effect rather than read it.

## 8. Gaps

- **`UNKNOWN`** — how `cpe_distance` is measured, and whether it is GPS-assisted.
- **`UNKNOWN`** — the range and units validation of `distance_meter` beyond the name.
- **`UNKNOWN`** — the timing-advance mechanism, under whatever name it actually uses.
- **`UNKNOWN`** — whether `frame_pulse_offset` (Stage 564A) serves as the CP/uplink alignment.
- **`UNKNOWN`** — the `autofa` selection metric and the `force_in_dl` trigger.
- **Known limit** — a distance value proves measurement exists, not how it is made.
- **Not attempted** — dynamic validation, ranging measurement.
