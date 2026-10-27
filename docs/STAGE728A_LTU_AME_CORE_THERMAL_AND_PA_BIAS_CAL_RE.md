<!-- doc-head: STAGE728A_LTU_AME_CORE_THERMAL_AND_PA_BIAS_CAL_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 728A — thermal calibration, PA temperature compensation and TX gain control

- **Receipt**: [`artifacts/autoresearch/stage728a_ltu_ame_core_thermal_and_pa_bias_cal_re.json`](../artifacts/autoresearch/stage728a_ltu_ame_core_thermal_and_pa_bias_cal_re.json)
- **Tool**: [`tools/re/dissect_stage728a_ltu_ame_core_thermal_and_pa_bias_cal_re.py`](../tools/re/dissect_stage728a_ltu_ame_core_thermal_and_pa_bias_cal_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. The stage's vocabulary does not exist

| Token | Hits |
| :--- | :-: |
| `thermal`, `THERMAL` | **0** |
| `pa_bias`, `bias`, `BIAS` | **0** |

**`REFUTED`**: `thermal_word_absent = 1` and `pa_bias_absent = 1`.

This is a naming result, not an absence result. The mechanism is present under **two other words**:

| Token | Hits |
| :--- | :-: |
| `temp`, `TEMP`, `temperature` | **5** |
| `txgain`, `tx_gain` | **34** |

So the compensation exists; it is described as **temperature** acting on **tx_gain**.

## 1. Two temperature readers

```
bbp_rf_get_temperature      fty_rf_get_temperature
```

**`CONFIRMED`**: `temperature_reader_count = 2`, `two_temperature_paths = 1`.

The split is meaningful: `bbp_rf_*` is the **operational** path used at runtime; `fty_rf_*` is the
**factory** test path. Two readers for one sensor is what you build when factory calibration and
field operation must be able to disagree — the factory value is the reference, the operational value
is the live one.

## 2. TX gain has a five-symbol control surface, with a staged update

```
ame_bbp_get_tx_gain        ame_bbp_set_tx_gain
bbp_rf_fetch_tx_gain       bbp_rf_apply_tx_gain
ame_bbp_obs_set_txgain
```

**`CONFIRMED`**: `tx_gain_control_count = 5` (`txgain_tokens = 34`), and
`fetch_apply_split = 1`.

**`fetch` and `apply` are separate verbs.** That is the signature of a **staged** update: read the
current gain, compute a correction, then apply it. A single `set` would be enough for a static
configuration; the split exists because something is **recomputing** the value — and the only
candidate in this module is temperature.

`ame_bbp_obs_set_txgain` is the observation-mode variant, so gain can be forced for measurement
without changing the operating point.

## 3. The autotune loop is named, and it has a step size

```
fty_rf_autotune_txgain      fty_rf_adjust_step_txgain
```

**`CONFIRMED`**: `autotune_present = 1`, `autotune_has_step = 1`.

`adjust_step_txgain` is the **step** of the autotune. A stepping controller — rather than a
one-shot set — is exactly right for thermal drift, which is **slow and monotonic**. You walk the gain
toward the target in increments and re-measure, instead of jumping and overshooting.

This is the strongest structural finding of the stage: the module contains a **closed-loop gain
correction with an explicit step parameter**, which is what "PA temperature compensation" means in
practice.

## 4. Power calibration compensation is separate from airtime compensation

`compensat` has 2 hits:

```
sched_airtime_compensate_by_l2bps       <- airtime scheduling
bbp_ulpwr_fftpwr_cal_compensate         <- power calibration
```

**`REFUTED`**: `compensate_is_airtime = 1` — one of the two is **airtime scheduling**, not thermal
compensation. Reading `compensat` as one mechanism would merge a scheduler with a calibration routine.

**`CONFIRMED`**: `power_cal_compensate = 1` — `bbp_ulpwr_fftpwr_cal_compensate` is the real power
compensation, and the `ulpwr` / `fftpwr` prefix means it handles **uplink power** and **full-frame
power** separately. Those are measured differently, so they are compensated differently.

## 5. A temperature buffer exists in the EAB layer

```
AME_EAB_GetLoopbackTempBuf
```

**`CONFIRMED`**: `loopback_temp_buf = 1`.

The EAB layer (Stage 694A's descriptor interface) provides a **loopback temperature buffer**. That
means calibration can capture temperature samples **through the ASIC loopback path** rather than
polling a sensor register — the same loopback used to characterise the transmit chain.

## 6. Calibration is triggered from outside

`ame_dev.ko` exposes, over ubus:

```
calibrate        callback_func_call_sync_calibrate
set_rfic_txgain  get_rfic_txgain
obs_txgain_show  obs_txgain_store
```

**`CONFIRMED`**: `ubus_calibration = 1`, `ubus_hooks = [calibrate, set_rfic_txgain, get_rfic_txgain]`.

Nothing here runs on an internal timer. Calibration and RFIC gain are **externally driven** — the same
architecture Stage 544A found for DPD loading. A field unit's thermal state is therefore the result of
whatever the managing process scheduled, not of a fixed internal loop.

## 7. What is established

| Claim | Status |
| :--- | :-: |
| `thermal` / `pa_bias` / `bias` exist as identifiers | **REFUTED** (0 hits) |
| temperature is read on both an operational and a factory path | **CONFIRMED** (2 readers) |
| TX gain has get/set plus fetch/apply | **CONFIRMED** (5 symbols, staged) |
| an autotune loop with an explicit step exists | **CONFIRMED** |
| power calibration compensates uplink and full-frame separately | **CONFIRMED** |
| a loopback temperature buffer exists in the EAB layer | **CONFIRMED** |
| calibration is externally triggered over ubus | **CONFIRMED** |
| `compensat` is ambiguous (airtime vs calibration) | **CONFIRMED** |
| the temperature-to-gain curve | **UNKNOWN / not in the module** |
| the PA bias value and coefficient | **UNKNOWN / not found** |

## 8. The operational reading

The mechanism is **closed-loop and stepping**, and that shapes how a thermal symptom should be
investigated:

1. read temperature on the operational path (`bbp_rf_get_temperature`) and on the factory path
   (`fty_rf_get_temperature`) — if they diverge, the sensor or the calibration reference is the fault,
   not the PA;
2. watch `txgain` while temperature moves — `fetch`/`apply` means the value is recomputed, so the gain
   should track;
3. if the gain **steps** in a sawtooth rather than settling, the step size (`adjust_step_txgain`) is
   too coarse — that is a tuning problem, not a hardware fault.

What cannot be answered is the **target curve**: how much gain should move per degree. Both ends are
named; the mapping is not in the module.

## 9. Gaps

- **`UNKNOWN`** — the temperature-to-gain mapping and its coefficient.
- **`UNKNOWN`** — the autotune step size and its convergence criterion.
- **`UNKNOWN`** — the PA bias value, its temperature coefficient, and whether it is even adjusted.
- **`UNKNOWN`** — what the EAB loopback temperature buffer contains (samples, average, or a single
  reading).
- **`UNKNOWN`** — the ubus caller's schedule for calibration.
- **Known limit** — a stepped autotune proves a loop exists, not what it converges to.
- **Not attempted** — dynamic validation, thermal chamber characterisation.
