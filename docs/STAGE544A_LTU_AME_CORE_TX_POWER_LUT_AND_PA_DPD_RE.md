<!-- doc-head: STAGE544A_LTU_AME_CORE_TX_POWER_LUT_AND_PA_DPD_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 544A — LTU TX power LUT, PA pre-distortion and 4096-QAM EVM

- **Receipt**: [`artifacts/autoresearch/stage544a_ltu_ame_core_tx_power_lut_and_pa_dpd_re.json`](../artifacts/autoresearch/stage544a_ltu_ame_core_tx_power_lut_and_pa_dpd_re.json)
- **Tool**: [`tools/re/build_stage544a_ltu_ame_core_tx_power_lut_and_pa_dpd_re.py`](../tools/re/build_stage544a_ltu_ame_core_tx_power_lut_and_pa_dpd_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. `eab_driver.ko` absent — ninth confirmation

**0 files.** Two targets remain: `ame_core.ko` (3,282,052 bytes) and `ame_dev.ko` (298,760 bytes).

## 1. The TX power LUT is a conversion pair, not a table

```
bbp_util_calculate_tx_power_by_attenuation
bbp_util_calculate_tx_attenuation_by_power
```

**`CONFIRMED`**: `conversion_pair_named = 1` — the two directions both exist. That is the important
shape: power and attenuation are **mutually convertible**, which means the "LUT" is a **function**,
not a dumped array. A function implies the curve is computed from calibration coefficients at
runtime.

Supporting callers:

```
ame_bbp_get_txpower          ame_bbp_get_desired_txpower
ame_bbp_op_rf_tune_txpower   ame_bbp_op_rf_force_txpower
ame_bbp_op_set_rxTopA_txPower   ame_bbp_op_get_rxTopA_txPower
```

**`CONFIRMED`**: 17 TX-power symbols, including a **forced** variant
(`rf_force_txpower`) beside the tuning one — so a fixed power can be pinned, which is exactly what
a calibration bench needs.

**`UNKNOWN`**: the coefficients. They are per-unit calibration data and are not in the module.

## 2. DPD is a variable-length blob with a sysfs interface

```
ame_bbp_set_dpd      ame_bbp_get_dpd      ame_bbp_set_pa
dpd_load             dpd_show             dpd_store
```

**`CONFIRMED`**: `dpd_sysfs_interface = [dpd_load, dpd_show, dpd_store]` — a full **load / read /
write** triple. The DPD table is not compiled in; it is **supplied at runtime** through sysfs.

**`CONFIRMED`**: `dpd_table_is_variable_length = 1`. The module logs:

```
Incorrect dpd(tx) size (%d)!=(%d)
```

A size comparison against an expected length means the payload is **length-validated data**, not a
fixed struct. That is decisive for how to treat it: the DPD coefficients are an artefact you obtain
per unit, not a constant you read out of the binary.

**`CONFIRMED`**: `ame_bbp_set_pa` sits beside `ame_bbp_set_dpd`, so PA and DPD are set as a pair —
pre-distortion is meaningless without the operating point.

## 3. EVM is an instrumentation family, not a single field

```
ame_bbp_op_evm              ame_bbp_op_evm_mcs_map
ame_bbp_op_evm_peek_symbols ame_bbp_evm_get_cfg
ame_bbp_evm_set_r           ame_bbp_get_evm_dump
__bbp_mrx_evm_next
```

**`CONFIRMED`**: 23 EVM symbols. Three details matter:

- **`_mcs_map`** — EVM is measured **per MCS**, not as one aggregate number;
- **`_peek_symbols`** — the measurement reaches into **individual OFDM symbols**;
- **`_get_cfg` / `_set_r`** — there is a configuration and a result register, i.e. a real measurement
  loop.

That is the machinery a 4096-QAM EVM requirement would need, and it is present.

## 4. 4096-QAM is named, its threshold is not

```
bbp_rf_set_super4096        check_4096mimo_ofdm        choose_mcsTPindex_ofdm
```

**`CONFIRMED`**: `super4096` is an explicit RF setter, and `check_4096mimo_ofdm` gates it. The word
"super" is the vendor's own label for the 4096-QAM mode.

**`UNKNOWN`**: `evm_backoff_db_recovered = 0`. No EVM-to-backoff dB mapping was found. The stage
asks for "4096-QAM TX EVM backoff symbols"; the symbols that exist are the **measurement** side
(`op_evm_mcs_map`, `peek_symbols`), and the **backoff decision** is not among them.

## 5. The disambiguation that had to be made: `backoff` is not TX backoff

`backoff` has **25 hits** in `ame_core.ko`, and every one is:

```
cz_cross_frame_backoff_enable
cz_cross_frame_backoff_grouping_num
```

**`REFUTED`**: this is a **cross-frame grouping** scheduler knob, not a power or EVM backoff. The
two meanings share a word and nothing else. Counting these as "TX EVM backoff" would have produced
a completely false positive — the fifth instance of this failure mode in the series (after `LQ`,
`BE`, `moder` and `rx_lo`).

`backoff_is_crossframe_modules = 1`.

## 6. Calibration runs over ubus

In `ame_dev.ko`:

```
calibrate        callback_func_call_sync_calibrate
set_rfic_txgain / get_rfic_txgain   (ubus handlers)
obs_txgain_store / obs_txgain_show
```

**`CONFIRMED`**: calibration is a **ubus RPC**, exposed through
`__ksymtab_ubus_func_register_*` — so an external process triggers it, not an internal timer. The
`rfic_txgain` set/get pair is the RFIC-side gain control, and `obs_txgain` is its observation
counterpart.

## 7. What is established

| Claim | Status |
| :--- | :-: |
| `eab_driver.ko` exists | **REFUTED** (0 files, 9th) |
| TX power and attenuation are mutually convertible | **CONFIRMED** (both directions) |
| a forced-TX-power path exists | **CONFIRMED** (`rf_force_txpower`) |
| the DPD table is supplied at runtime with a length check | **CONFIRMED** (`dpd_store`, size log) |
| PA and DPD are set as a pair | **CONFIRMED** (`set_pa` beside `set_dpd`) |
| EVM is measured per MCS, down to symbols | **CONFIRMED** (`_mcs_map`, `_peek_symbols`) |
| 4096-QAM has an explicit RF setter and a check | **CONFIRMED** (`set_super4096`) |
| `backoff` means TX/EVM backoff here | **REFUTED** (`cz_cross_frame_backoff_*`) |
| calibration is externally triggered | **CONFIRMED** (ubus) |
| the LUT coefficients | **UNKNOWN / per-unit calibration data** |
| the DPD coefficients | **UNKNOWN / runtime payload** |
| the EVM backoff dB curve | **UNKNOWN / not present** |

## 8. The operational consequence

Three of the four things the stage asks for are **runtime payloads**, not constants:

- the TX power LUT is a **function of calibration coefficients**;
- the DPD table is **loaded through sysfs** and length-checked;
- the EVM measurement is **live telemetry**.

So "dissecting the LUT" by reading the binary cannot succeed, and this stage says so instead of
producing a fake table. What a bench can do is concrete: dump the current DPD via `dpd_show`, read
`ame_bbp_get_txpower` against `_get_desired_txpower`, and collect `op_evm_mcs_map` at the MCS
under test.

## 9. Gaps

- **`UNKNOWN`** — the TX-power/attenuation curve and its coefficients.
- **`UNKNOWN`** — the DPD payload format beyond the length check.
- **`UNKNOWN`** — the EVM requirement per MCS, and any backoff derived from it.
- **`UNKNOWN`** — what `check_4096mimo_ofdm` gates on.
- **`UNKNOWN`** — the calibration trigger conditions and duration.
- **Known limit** — a named API proves the hook exists, not the numbers behind it.
- **Not attempted** — dynamic validation, RF measurement, DPD capture.
