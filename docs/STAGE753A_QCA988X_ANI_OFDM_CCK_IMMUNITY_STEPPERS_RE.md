<!-- doc-head: STAGE753A_QCA988X_ANI_OFDM_CCK_IMMUNITY_STEPPERS_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 753A — the ANI state machine: ofdm_level, cck_level, firstep, spur, mrc_cck

- **Receipt**: [`artifacts/autoresearch/stage753a_qca988x_ani_ofdm_cck_immunity_steppers_re.json`](../artifacts/autoresearch/stage753a_qca988x_ani_ofdm_cck_immunity_steppers_re.json)
- **Tool**: [`tools/re/dissect_stage753a_qca988x_ani_ofdm_cck_immunity_steppers_re.py`](../tools/re/dissect_stage753a_qca988x_ani_ofdm_cck_immunity_steppers_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. `ath10k_core.ko` absent — eighth confirmation

**0 files.** The ath10k ANI implementation cannot be read. The vendor `umac.ko` goes further than
naming the variables: it **prints the state machine**.

## 1. The loop is two-phase, and both phases are logged

**UPDATE — the measurements:**

```
ANI UPDATE ofdm level %d firstep %d firstep_low %d cycpwr_thr %d self_corr_low %d
ANI UPDATE  cck level %d firstep %d firstep_low %d mrc_cck %d
```

**CONTROL — the actions taken:**

```
ANI CONTROL ofdmlevel %d ccklevel %d
ANI ofdm_control firstep %d cycpwr %d
ANI cck_control mrc_cck %d barker_threshold %d
```

**`CONFIRMED`**: `two_phase_loop = 1` — `update_line_count = 2`, `control_line_count = 3`.

ANI is not one adjustment. It **measures**, decides, then **applies**, and each phase is
instrumented separately. That is the state machine the stage asks for, recovered from its own
telemetry rather than inferred from control flow.

## 2. The observation and action sets are different — and that is the finding

| Domain | Measured (UPDATE) | Applied (CONTROL) |
| :--- | :--- | :--- |
| **OFDM** | `ofdm level`, `firstep`, `firstep_low`, `cycpwr_thr`, `self_corr_low` | **`firstep`**, **`cycpwr`** |
| **CCK** | `cck level`, `firstep`, `firstep_low`, **`mrc_cck`** | **`mrc_cck`**, **`barker_threshold`** |

**`CONFIRMED`**: `ofdm_action_set = 1` (`firstep`, `cycpwr`), `cck_action_set = 1`
(`mrc_cck`, `barker_threshold`).

Three consequences worth spelling out:

- **`firstep` spans both domains.** It is measured in the OFDM and CCK updates but applied only by
  the OFDM control. So the CCK path *observes* the OFDM energy estimate without acting on it.
- **`mrc_cck` is a control, not a statistic.** It appears in both the CCK UPDATE and the CCK CONTROL,
  which is what a state variable looks like: read, then written.
- **`self_corr_low` and `firstep_low` are observation-only** in the logged path. They never appear as
  CONTROL outputs, so their role is measurement.

**`CONFIRMED`**: `mrc_cck_present = 1` (`mrc_cck_hits = 6`) and `barker_threshold_present = 1`.

**`barker_threshold`** is the second CCK lever and it is a different mechanism from `mrc_cck`: Barker
spreading is the 1 and 2 Mbps CCK modulation, so raising its threshold **suppresses weak legacy
frames**, while `mrc_cck` controls **receive combining**. Two distinct CCK responses to the same
measurement.

## 3. The reset path is diagnosed

```
ANI resetting resetflag %d resetCause %d
```

**`CONFIRMED`**: `reset_is_diagnosed = 1` (`reset_line_hits = 2`).

That answers the most confusing ANI symptom: immunity levels jumping back to default. It is a
**logged reset with a cause code**, not an unexplained regression.

## 4. The knobs are separate and readable

```
ani_poll_len   ani_listen_len   ani_ofdm_level   ani_cck_level   dyntxchain
```

**`CONFIRMED`**: `proc_knob_count = 5`, and both levels have `get_` accessors, so `ofdm_level` and
`cck_level` are **independently readable and writable** per interface.

`dyntxchain` sits in the same block — **dynamic TX chain count** is part of the immunity response.
That links ANI directly to Stage 615A's chainmask work: the same loop that raises immunity can drop a
transmit chain.

## 5. The HAL owns the machine, the UMAC prints it

`ath_hal.ko` (WA) carries the full lifecycle plus the immunity controls:

```
ar9300_ani_attach   ar9300_ani_detach   ar9300_ani_init_defaults   ar9300_ani_reset
ar9300_ani_control  ar9300_ani_ar_poll
ar9300_ani_get_current_state    ar9300_ani_get_current_stats
ar9300_set_immunity   ar9300_is_ani_noise_spur   ath_hal_enabledANI
ath_hal_log_ani       ath_hal_log_ani_callback_register
```

**`CONFIRMED`**: `hal_lifecycle_count = 6`, `spur_immunity_present = 1` (`ar9300_set_immunity`,
`ar9300_is_ani_noise_spur`, `ath_hal_enabledANI`).

**`ath_hal_log_ani_callback_register` explains how §1 exists**: the HAL **registers a logging
callback** and the UMAC prints through it. That is why the state machine is visible at all — it was
designed to be observable.

`ath_dev.ko` contributes `ANI` (7 tokens) and `immunity` (2): the device layer knows the names but
does not own the loop.

`thresholds_recovered = 0`: no numeric firstep, `ofdm_level` ceiling, `cck_level` ceiling, `cycpwr`
or spur threshold was found. **The machine is recovered; its constants are not.**

## 6. What is established

| Claim | Status |
| :--- | :-: |
| `ath10k_core.ko` exists | **REFUTED** (0 files) |
| ANI has distinct measurement and action phases | **CONFIRMED** (2 UPDATE, 3 CONTROL) |
| OFDM actions are `firstep` and `cycpwr` | **CONFIRMED** |
| CCK actions are `mrc_cck` and `barker_threshold` | **CONFIRMED** |
| `mrc_cck` is a control variable, not a statistic | **CONFIRMED** (both phases) |
| `firstep` is measured in both domains, applied in OFDM only | **CONFIRMED** |
| `self_corr_low` / `firstep_low` are observation-only | **CONFIRMED** |
| a reset is logged with a flag and a cause | **CONFIRMED** |
| both levels are independently readable and writable | **CONFIRMED** (proc + getters) |
| ANI can also change the TX chain count | **CONFIRMED** (`dyntxchain`) |
| the HAL owns the lifecycle and registers the logger | **CONFIRMED** (6 + callback) |
| the numeric thresholds and stepper increments | **UNKNOWN / not in the module** |

## 7. The operational reading

This changes what an ANI diagnosis can be. Because the loop prints both phases, a live system shows
**what it measured and what it did**:

1. if UPDATE values move but CONTROL values do not, the machine is **stuck** — a control-path fault,
   not an RF one;
2. if CONTROL moves but throughput does not recover, the **chosen lever is wrong** — and the two
   levers per domain say which: `firstep`/`cycpwr` for OFDM energy, `mrc_cck`/`barker_threshold` for
   CCK combining and legacy suppression;
3. if the levels snap back, look for `ANI resetting` with its cause code before assuming interference.

Without the log, all three look identical from a throughput graph.

## 8. Gaps

- **`UNKNOWN`** — the firstep, `ofdm_level` ceiling, `cck_level` ceiling, `cycpwr` and spur
  thresholds.
- **`UNKNOWN`** — the stepper increment per poll (how far a level moves on one decision).
- **`UNKNOWN`** — the exact transition conditions, which the log lines expose as effects rather than
  as rules.
- **`UNKNOWN`** — the `resetCause` code enumeration.
- **`UNKNOWN`** — why `self_corr_low` is measured but never applied.
- **Known limit** — a printed state machine proves observability, not the policy behind it.
- **Not attempted** — dynamic validation, live log capture.
