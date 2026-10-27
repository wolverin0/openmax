<!-- doc-head: STAGE563A_QCA988X_PAPRD_AND_OLPC_TX_POWER_CONTROL_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 563A — PAPRD, TPC/CTL target power and thermal calibration

- **Receipt**: [`artifacts/autoresearch/stage563a_qca988x_paprd_and_olpc_tx_power_control_re.json`](../artifacts/autoresearch/stage563a_qca988x_paprd_and_olpc_tx_power_control_re.json)
- **Tool**: [`tools/re/build_stage563a_qca988x_paprd_and_olpc_tx_power_control_re.py`](../tools/re/build_stage563a_qca988x_paprd_and_olpc_tx_power_control_re.py)
- **Scope**: offline static. No module loaded, no radio contacted, nothing transmitted.

## 0. Seven modules across three lines

| Module | bytes |
| :--- | :-: |
| `WA:ath_hal.ko` | 367,456 |
| `XC:ath_hal.ko` | 360,896 |
| `XW:ath_hal.ko` | 503,892 |
| `WA:ath_dev.ko` / `XC:ath_dev.ko` | 287,216 each |
| `WA:umac.ko` / `XC:umac.ko` | 2,356,432 / 2,358,768 |

## 1. The stage's own names do not exist: `olpc` / `clpc` return zero

| Token | Hits |
| :--- | :-: |
| `olpc`, `OLPC` | **0** |
| `clpc`, `CLPC` | **0** |
| `open_loop`, `closed_loop` | **0** |

**`REFUTED`**: there is no `OLPC` or `CLPC` identifier anywhere in the seven modules.

**This is a naming result, not an absence result.** The open/closed-loop distinction is carried by
two other families, and both are richly present:

- **`tpc`** — transmit power control: `ar9300_enable_tpc`, `ar9300_get_tpc_tables`,
  `ar9300_disp_tpc_tables`, `ath_hal_display_tpctables`, `tpc_config_get_rate_tpc`,
  `ath_net80211_enable_tpc` (**15 symbols**);
- **`ctl`** — closed-loop target: `ar9300_get_ctl_chan_nf`, `ar9300_update_loc_ctl_reg`,
  `wlan_get_ctl_by_country`, `txctl_cap`, `ol_if_spectral_get_ctl_noisefloor` (**22 symbols**).

**`CONFIRMED`**: `loop_control_count = 6`, and the six are the actual mechanism:
`enable_tpc`, `get_tpc_tables`, `get_rate_tpc`, `get_ctl_by_country`, `get_ctl_chan_nf`,
`update_loc_ctl_reg`.

A bench engineer grepping for `olpc` would conclude the stack has no open-loop power control. It
does; it is called `tpc`.

## 2. PAPRD is a seven-stage production pipeline

`paprd_pipeline_complete_of_7 = 7`. Every stage is present, in a coherent order:

| # | Stage | What it does |
| :-: | :--- | :--- |
| 1 | `ar9300_paprd_create_curve` | build the correction from the measured response |
| 2 | `ar9300_paprd_init_table` | allocate / reset the table |
| 3 | `ar9300_populate_paprd_single_table` | fill one entry |
| 4 | `ar9300_swizzle_paprd_entries` | reorder entries to the hardware layout |
| 5 | `ar9300_paprd_setup_gain_table` | per-gain-index table |
| 6 | `ar9300_set_paprd_tx_desc` | **transmit** a calibration frame |
| 7 | `ar9300_paprd_is_done` | poll for completion |

**`CONFIRMED`**: `paprd_has_transmit_path = 1`. Stage 6 is the decisive one — PAPRD is
**closed-loop around a real transmission**, not a offline table lookup. The chip sends a known
signal, measures its own PA output, and builds the inverse curve.

Two more HAL stages complete the picture:

```
ar9300_paprd_dec_tx_pwr      (reduce power during the training burst)
ar9300_enable_paprd          (master gate)
```

`ar9300_paprd_dec_tx_pwr` is a safety measure: the training transmission would otherwise go out at
full power on a live channel.

## 3. The device side owns the queue

`ath_dev.ko` carries **29** paprd symbols on its own, and they are the **transmit and lifecycle**
half:

```
ath_paprd_cal            ath_paprd_send          ath_sendpaprd_single
ath_paprd_set_enable     ath_paprd_get_enable
ath_paprd_setrate        ath_paprd_getrate
ath_apply_paprd_table
ath_tx_paprd_init        ath_tx_paprd_complete
ath_tx_paprd_draintxq    ath_tx_paprd_cleanup
```

**`CONFIRMED`**: the device layer has an explicit **drain and cleanup** path around calibration.
That is what you need to stop traffic, send a training frame, and restart without corrupting the
TX queue.

## 4. Three interactions that change the answer

**Thermal and PAPRD share a path.** `ar9300_paprd_thermal_send` — `thermal_link = 1`. On this
silicon the pre-distortion curve is **temperature-dependent**, and the recalibration is triggered
through the same mechanism.

**GreenTX can skip PAPRD entirely.** `ar9300_is_skip_paprd_by_greentx` — `green_tx_skips_paprd = 1`.
A unit running GreenTX may operate with **no** pre-distortion correction at all. For an EVM or
spectral-mask question, that is the first thing to check: is PAPRD actually applied on this unit?

**Target power is per-unit.** `ar9300_set_target_power_from_eeprom` —
`target_power_from_eeprom = 1`. The target is **calibration data from EEPROM**, not a constant, so
two units of the same model can legitimately transmit different power for the same configuration.

## 5. The regulatory dimension

```
wlan_get_ctl_by_country      ctl_by_country = 1
txctl_cap                    txctl_cap = 1
tpc_config_get_rate_tpc
```

**`CONFIRMED`**: the CTL (closed-loop target) is **per-country** and there is a separate **TX power
cap**. So the transmit power actually used is the result of at least four inputs: EEPROM target,
country CTL, per-rate TPC table, and a global cap.

## 6. What is established

| Claim | Status |
| :--- | :-: |
| `olpc` / `clpc` exist as identifiers | **REFUTED** (0 hits) |
| the loop distinction is `tpc` and `ctl` | **CONFIRMED** (15 + 22 symbols, 6 controls) |
| PAPRD is a 7-stage pipeline with a transmit step | **CONFIRMED** (7/7) |
| the device layer owns drain and cleanup | **CONFIRMED** (`ath_tx_paprd_draintxq`) |
| thermal calibration shares the PAPRD path | **CONFIRMED** (`paprd_thermal_send`) |
| GreenTX can skip PAPRD | **CONFIRMED** (`is_skip_paprd_by_greentx`) |
| target power is EEPROM calibration data | **CONFIRMED** |
| CTL is per-country and there is a TX cap | **CONFIRMED** |
| the PAPRD curve coefficients | **UNKNOWN / runtime artefact** |
| the TPC per-rate tables | **UNKNOWN / not extracted** |
| the thermal compensation curve | **UNKNOWN / not recovered** |

## 7. The operational reading

For any question of the form "why is this unit's power or EVM different from that unit's", the
corpus says to check, in order:

1. **is PAPRD applied at all** (`is_skip_paprd_by_greentx`, `ath_paprd_get_enable`);
2. **what target did EEPROM supply** (`set_target_power_from_eeprom` is per-unit);
3. **what country CTL is in force** (`get_ctl_by_country` + `txctl_cap`);
4. **what the last thermal recalibration did** (`paprd_thermal_send`).

Those four differ per unit and per deployment, which is why identical hardware can measure
differently. None of the four is a constant that could be read out of the binary.

## 8. Gaps

- **`UNKNOWN`** — the PAPRD correction curve and the per-gain table contents.
- **`UNKNOWN`** — the TPC per-rate table values.
- **`UNKNOWN`** — the thermal compensation curve and its trigger threshold.
- **`UNKNOWN`** — the GreenTX skip condition.
- **`UNKNOWN`** — the CTL table per country, and the `txctl_cap` value.
- **Known limit** — a pipeline stage name proves the step exists, not what it computes.
- **Not attempted** — dynamic validation, calibration capture, EVM measurement.
