<!-- doc-head: STAGE486A_LTU_AD9361_FASTLOCK_AND_CAL_TABLE_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 486A — AD9361 FastLock, TX quadrature calibration and split-frequency LO

- **Receipt**: [`artifacts/autoresearch/stage486a_ltu_ad9361_fastlock_and_cal_table_re.json`](../artifacts/autoresearch/stage486a_ltu_ad9361_fastlock_and_cal_table_re.json)
- **Tool**: [`tools/re/build_stage486a_ltu_ad9361_fastlock_and_cal_table_re.py`](../tools/re/build_stage486a_ltu_ad9361_fastlock_and_cal_table_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. `eab_driver.ko` is absent — eighth confirmation

**0 files.** `ame_core.ko` (3,282,052 bytes) is the only readable target.

## 1. The three named mechanisms return zero

| Token | Hits |
| :--- | :-: |
| `fastlock`, `fast_lock` | **0** |
| `synth` | **0** |
| `quad` | **0** |
| `calib` | **0** |
| `qec` (quadrature error correction) | **0** |
| `tx_lo`, `pll` | **0** |

**`REFUTED`**: there is **no FastLock profile register set**, **no TX quadrature calibration
table**, and **no LO synthesizer vocabulary** in this module. Not one of the stage's three
mechanisms exists by name.

That is a strong negative because an AD9361 driver that programmed FastLock profiles would
necessarily name them — the profiles are indexed, and an index needs a table.

## 2. Two tokens that look like LO programming and are not

| Token | Hits | What it actually is |
| :--- | :-: | :--- |
| `rx_lo` | 2 | substring of **`tpc_rx_log`** (transmit-power control log fields) |
| `split` | 1 | substring of **`c_string_smart_split`** |

**`REFUTED`**: neither is LO programming. `rx_lo` matched inside `tpc_rx_log` and
`tpc_rx_log_idx`; `split` matched inside a string helper.

This is the **fourth** instance of the same failure mode in this series — after `LQ` inside a
base64 table (438A), `BE` inside `PROBE` (452A) and `moder` inside "modern" (460A). A short token
census is not an analysis; the context check is.

## 3. `ad9361` appears twice — in error and reset only

The RFIC is named, and **only** in two identifiers:

```
ame_ad9361_set_rf_err_skip
ame_ad9361_set_rf_reset_ongoing
```

Note that these are **string-level names, not ELF symbols** (`ad9361_symbol_count = 0`,
`ad9361_name_count = 2`). The distinction matters: a symbol is linkable and addressable; a name in
a kallsyms-style blob is only a label.

**`CONFIRMED`**: the AD9361 is present on this hardware and the driver knows about it.
**`REFUTED`**: the driver exposes any named synthesis, calibration or profile API for it. Both
names are **fault-handling** entry points — skip the error, mark the reset in progress.

An RFIC whose only named touchpoints are fault handlers is an RFIC whose normal operation is driven
somewhere else.

## 4. DCXO is the real frequency surface

`dcxo` + `tcxo` = **68 tokens**, **30 distinct symbols**:

```
ame_bbp_op_dcxo              ame_bbp_rt_keep_dcxo_sync
ame_dcxo_sync                ame_dcxo_sync_work
ame_core_NxN_dcxo_sync       bbp_rf_dcxo_adj
bbp_rf_dcxo_sync_start       bbp_rf_dcxo_sync_track
bbp_rf_dcxo_sync_adjust      bbp_rf_dcxo_sync_info_show
bbp_rf_dcxo_reset_params     bbp_rf_tcxo_cal_variation
bbp_rf_tcxo_item_expired     BBEA_track_tcxo_routine
ap_sched_track_tcxo_work     factory_bbp_track_tcxo_routine
```

**`CONFIRMED`**: a **full DCXO/TCXO discipline subsystem** exists — operate (`op_dcxo`), keep the
sync alive in real time (`rt_keep_dcxo_sync`), adjust (`sync_adjust`), start and track
(`sync_start` / `sync_track`), expose info (`sync_info_show`), reset (`reset_params`), and
calibrate variation (`tcxo_cal_variation`).

**And it tells two references apart:**

```
bbp_rf_dcxo_is_sync_by_gps
bbp_rf_dcxo_is_sync_by_tcxo
bbp_rf_dcxo_set_sync_mode      bbp_rf_dcxo_get_sync_mode
bbp_rf_dcxo_get_gps_state
```

**`CONFIRMED`**: the driver has **two sync modes** and can answer whether the oscillator is
disciplined **by GPS** or **by TCXO alone**. That closes the loop Stage 416A left open:
`ubnt_poll_host.ko` carries the GPS frame durations, and here is the consumer that disciplines the
oscillator against a GPS reference and falls back to the crystal when GPS is absent. The two stages
were looking at opposite ends of the same mechanism.

**`INFERRED`**: this is the frequency discipline that actually runs on these units. DCXO is the
digitally-controlled crystal oscillator, and a TDMA/LTE-style baseband must hold an **absolute**
frequency reference across the frame — which is a DCXO problem, not a per-packet synthesizer
problem.

If that reading holds, then FastLock profiles (a channel-agility optimisations for fast retune) are
simply **not on this product's critical path**: the LO retunes rarely, and the oscillator is
disciplined continuously instead.

## 5. What the absence implies

| Question the stage asks | Answer from the corpus |
| :--- | :--- |
| FastLock profile registers | **absent** — no `fastlock`, no profile index |
| TX quadrature calibration table | **absent** — no `quad`, no `calib`, no `qec` |
| split-frequency LO programming | **absent** — `rx_lo`/`split` are substrings |
| the RFIC is present | **CONFIRMED** — two error/reset names |
| the frequency reference is disciplined | **CONFIRMED** — 30 DCXO/TCXO symbols |

**`REFUTED`**: the stage's three mechanisms are named anywhere in `ame_core.ko`.

## 6. Why this is a useful negative

Three separate bench plans would have been wasted:

1. hunting a FastLock table that does not exist;
2. looking for a TX quadrature cal table to dump;
3. treating `tpc_rx_log` as an LO register when it is a power-control log.

The module points instead at **DCXO sync tracking** — which is the subsystem that would explain a
frequency-offset symptom, and which has a named real-time component
(`ame_bbp_rt_keep_dcxo_sync`) and an explicit variation calibration.

## 7. Gaps

- **`UNKNOWN`** — the DCXO adjustment table and its units (ppm per step).
- **`UNKNOWN`** — whether `fty_rf_dcxo_sync_track` closes the loop to the GPS 1PPS reference
  (Stage 416A found the GPS durations in `ubnt_poll_host.ko`, not here).
- **`UNKNOWN`** — whether an AD9361 transmitter-quadrature calibration exists in firmware
  (absent from this corpus, not disproven in hardware).
- **`UNKNOWN`** — the RFIC's programming path if not `ame_core.ko`; the fabric bitstream is absent.
- **`INFERRED`** — that DCXO is the operative frequency discipline. Stated as inference, not fact.
- **Not attempted** — dynamic validation, RF measurement.
