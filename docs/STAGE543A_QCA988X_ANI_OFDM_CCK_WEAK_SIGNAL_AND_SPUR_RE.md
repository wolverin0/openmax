<!-- doc-head: STAGE543A_QCA988X_ANI_OFDM_CCK_WEAK_SIGNAL_AND_SPUR_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 543A — ANI state machines, spur immunity, firstep and PHY-error thresholds

- **Receipt**: [`artifacts/autoresearch/stage543a_qca988x_ani_ofdm_cck_weak_signal_and_spur_re.json`](../artifacts/autoresearch/stage543a_qca988x_ani_ofdm_cck_weak_signal_and_spur_re.json)
- **Tool**: [`tools/re/build_stage543a_qca988x_ani_ofdm_cck_weak_signal_and_spur_re.py`](../tools/re/build_stage543a_qca988x_ani_ofdm_cck_weak_signal_and_spur_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Seven modules, three lines

| Module | bytes |
| :--- | :-: |
| `WA:ath_hal.ko` | 367,456 |
| `XC:ath_hal.ko` | 360,896 |
| `XW:ath_hal.ko` | 503,892 |
| `WA:ath_dev.ko` / `XC:ath_dev.ko` | 287,216 each |
| `WA:umac.ko` / `XC:umac.ko` | 2,356,432 / 2,358,768 |

## 1. ANI is a polled state machine, not a flag

Eight symbols, and they form a **complete object lifecycle**:

```
ar9300_ani_attach              ar9300_ani_detach
ar9300_ani_init_defaults       ar9300_ani_reset
ar9300_ani_control             ar9300_ani_ar_poll
ar9300_ani_get_current_state   ar9300_ani_get_current_stats
```

**`CONFIRMED`**: `ani_lifecycle_complete_of_6 = 6` — attach, defaults, reset, control, poll and
detach are **all** present, plus two read-only accessors.

The presence of `ar9300_ani_ar_poll` is the decisive detail: ANI runs on a **poll interval**, not
per packet. That is why the UMAC exposes `ani_poll_len` and `ani_listen_len` as separate knobs —
the machine listens for a window, then decides.

**`CONFIRMED`**: `ar9300_ani_get_current_state` and `_get_current_stats` exist, so the level is
**readable while running**. That is what makes ANI observable on a live radio rather than inferred
from throughput.

## 2. Spur immunity is a per-board list, not a constant

Seven spur symbols across the images:

```
ar9300_is_ani_noise_spur        ar9300_set_immunity
ar9300_get_spur_info            ar9300_set_spur_info
ar9300_eeprom_get_spur_chans_ptr
ar9300_enabledANI (via ath_hal_enabledANI)
```

**`CONFIRMED`**: `spur_chans_in_eeprom = 1`. The spur **channel list is calibration data read from
EEPROM**, not a compiled table. That has a direct consequence: two boards of the same model can
carry different spur lists, so a spur problem is **per-unit**, and re-flashing firmware does not
change it.

**`CONFIRMED`**: `ar9300_set_immunity` is the write side, `ar9300_is_ani_noise_spur` the predicate,
and `ar9300_enabledANI` the master gate.

## 3. The UMAC exposes the state and the error rate

Proc/sysctl fields in `umac.ko`:

```
ani_poll_len    ani_listen_len    ani_ofdm_level    ani_cck_level    dyntxchain
```

**`CONFIRMED`**: `ofdm_and_cck_independent = 1` — OFDM and CCK immunity levels are **separate
knobs**. A deployment can raise CCK immunity (2.4 GHz noise) without touching OFDM.

The false-alarm telemetry is a single formatted line:

```
… ofdm_phy_err_rate,%u, cck_phy_err_rate,%u … reg_ofdm_phy_error_cu,%u … max_phy_e…
```

**`CONFIRMED`**: `phy_error_rate_count = 4` — OFDM rate, CCK rate, the raw OFDM error counter and a
max field.

This is the "PHY error false-alarm threshold" the stage asks about, and its shape matters: the
driver reports a **rate**, not a verdict. The threshold that turns a rate into an immunity-level
change lives inside `ar9300_ani_control`, which was not decoded.

## 4. The real split is HAL versus UMAC, not AC versus XW

An early reading of the token counts suggested `firstep` was XW-only. The measured split is
different and more interesting:

| Variable | XW `ath_hal.ko` | AC `umac.ko` |
| :--- | :-: | :-: |
| `firstep` | **2** | **7** |
| `cycpwr` | **2** | **2** |
| `ar9300_ani_*` lifecycle | 0 | 0 (HAL-only, in WA/XC `ath_hal.ko`) |

**`CONFIRMED`**: `firstep_in_xw_hal = 1` **and** `firstep_in_ac_umac = 1`.

So the two uses are different in kind:

- in **XW `ath_hal.ko`**, `firstep[level]=%d ini=%d` is an **INI-table override** (Stage 373A) —
  the value is written at attach;
- in **AC `umac.ko`**, `firstep` is a field of the runtime ANI state vector —
  `ANI UPDATE ofdm level %d firstep %d firstep_low %d cycpwr_thr %d self_corr_low %d`.

**`UNKNOWN`**: whether the two refer to the same hardware quantity. The names match; the roles do
not, and this stage does not claim they are the same register.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| ANI has a complete 6-phase lifecycle plus 2 accessors | **CONFIRMED** (8 symbols) |
| ANI is polled, with separate poll and listen lengths | **CONFIRMED** |
| the ANI level is readable at runtime | **CONFIRMED** |
| spur immunity is driven by an EEPROM channel list | **CONFIRMED** |
| OFDM and CCK immunity levels are independent | **CONFIRMED** |
| PHY-error false alarms are reported as rates plus counters | **CONFIRMED** |
| `firstep` is XW-only | **REFUTED** (also 7 hits in AC `umac.ko`) |
| the numeric firstep / ofdm_level / spur thresholds | **UNKNOWN / not recovered** |
| the ANI transition graph | **UNKNOWN / not decoded** |

## 6. Why this matters on a bench

The ANI loop is the most likely explanation for a class of symptoms that look like "the link got
worse on its own": immunity levels rise under interference, which suppresses PHY errors but also
lowers sensitivity, and a weak station then drops. Because `ani_ofdm_level` and `ani_cck_level` are
**readable and writable**, that hypothesis is testable directly:

1. read `ani_ofdm_level` / `ani_cck_level` during a good period and a bad one;
2. if they climb, pin them and re-measure;
3. if the symptom disappears with a pinned level, ANI was the cause.

That is an actionable procedure the corpus supports. What it does **not** support is a claim about
which threshold triggered the climb.

## 7. Gaps

- **`UNKNOWN`** — the firstep, `ofdm_level` ceiling and `cck_level` ceiling values.
- **`UNKNOWN`** — the spur threshold, and the per-board spur list itself (EEPROM, not in corpus).
- **`UNKNOWN`** — the transition rule inside `ar9300_ani_control`.
- **`UNKNOWN`** — whether `firstep` in the HAL and in the UMAC are the same register.
- **`UNKNOWN`** — the poll and listen defaults; only the knob names are known.
- **Known limit** — a named lifecycle proves the machine exists, not when it steps.
- **Not attempted** — dynamic validation on a live radio.
