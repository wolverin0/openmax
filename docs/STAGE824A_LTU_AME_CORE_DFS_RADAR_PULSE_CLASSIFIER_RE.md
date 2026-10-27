<!-- doc-head: STAGE824A_LTU_AME_CORE_DFS_RADAR_PULSE_CLASSIFIER_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 824A — LTU Beetle DFS pulse classifier, PW/PRI filters and LNA immunity

- **Receipt**: [`artifacts/autoresearch/stage824a_ltu_ame_core_dfs_radar_pulse_classifier_re.json`](../artifacts/autoresearch/stage824a_ltu_ame_core_dfs_radar_pulse_classifier_re.json)
- **Tool**: [`tools/re/dissect_stage824a_ltu_ame_core_dfs_radar_pulse_classifier_re.py`](../tools/re/dissect_stage824a_ltu_ame_core_dfs_radar_pulse_classifier_re.py)
- **Scope**: offline static. No module loaded, no radio contacted, nothing transmitted.

## 0. The stage names the wrong two modules

| Module | Bytes | `pulse` | `dfs`/`DFS` | `pri`/`PRI` |
| :--- | :-: | :-: | :-: | :-: |
| `ame_core.ko` | 3,282,052 | 22 | 24 / 34 | 65 |
| `ame_dev.ko` | 298,760 | 6 | 6 | 18 |
| **`ame_dfs.ko`** | **141,472** | **82** | **192 / 64** | **29 / 18** |

**`CONFIRMED`**: `classifier_in_dfs_module = 1`. The radar classifier is in **`ame_dfs.ko`** — a
141 KB module the stage does not name — where `pulse` density is **82 against 22** in `ame_core.ko`.

That is a location correction, and it matters: `ame_core.ko` is 23× larger and would have absorbed the
search, while the mechanism sits in the module named after it.

## 1. The classifier surface, three named entry points

```
DFSdetect              DFSChanActivity          DFS_heavy_env_det
```

**`CONFIRMED`**: `classifier_symbol_count = 3`, `heavy_env_detector = 1`, `channel_activity = 1`.

**`DFS_heavy_env_det` is the name that answers the stage's actual question.** Before classifying
pulses, the module decides whether the **RF environment is so busy that pre-classification filtering
would be unreliable**. That is precisely the guard a co-located tower needs: when the environment is
heavy, a naive pulse count produces false verdicts.

**`DFSChanActivity` separate from `DFSdetect`** means the module can report "this channel is active
but not radar" — the distinction that prevents busy channels from being flagged as radar.

The lifecycle is complete: `ame_dfs_init`/`_deinit`/`_isr`/`_ioctl`/`_reset`,
`ame_start_ep_dfs`/`ame_stop_ep_dfs` (**7 symbols**), with a ubus surface
(`dfsdetect`, `dfs_irq_ctl`, `startdfs`, `dfs_hit_monitor_mode_get`).

## 2. The pulse filter is a selector, and it reports occupancy

The module's own log line carries three fields:

```
%s.tot hits %u, pulse percent/max %d/%u
%s.pulseFilteringModule             %d
%s.target_pwr : %d
```

**`CONFIRMED`**: `filter_is_selectable = 1`, `pulse_percent_max_reported = 1`.

| Field | Meaning |
| :--- | :--- |
| **`tot hits`** | pulses seen |
| **`pulse percent/max`** | **occupancy percentage** and the **maximum** reading |
| **`pulseFilteringModule`** | **which filter** is active |

`pulseFilteringModule` is a **selector**, not a boolean. The module can run different pulse filters —
the same design Stage 727A found on the AC side, where `ath_dfs.ko` carries **five** PHYERR
processors, four named after Atheros silicon generations.

**`CONFIRMED`**: `target_pwr : %d` is printed **beside** the pulse statistics. Transmit power and
radar detection are reported together, which is exactly where an LNA-saturation false trigger would
originate.

## 3. LNA saturation is not named — and the stage asks about it

| Token | Hits |
| :--- | :-: |
| `lna`, `LNA` | **0** |
| `satur` | **1** (in `ame_core.ko`, not in `ame_dfs.ko`) |

**`REFUTED`**: `lna_saturation_named = 0`.

The single `satur` hit is in `ame_core.ko` and **not in the DFS path**. So the specific hypothesis —
false DFS triggers from LNA saturation on co-located towers — is **not named in the binary**.

What exists is the **general** immunity machinery, and it is plausible but unproven:

- `DFS_heavy_env_det` rejects verdicts in a busy environment;
- `pulseFilteringModule` allows the filter to change;
- `pulse percent/max` thresholds occupancy;
- `target_pwr` is logged alongside, tying detection to the transmit state.

A saturated LNA produces a wide, strong pulse that the percent/max filter and the heavy-environment
detector would both plausibly reject — **but the corpus does not say so**, and this stage does not
claim it. `lna_saturation_immunity_recovered = 0`.

## 4. The PW/PRI tables are not in the strings

**`REFUTED`**: `pw_pri_table_recovered = 0`.

`pri` has 29 hits and `PRI` 18 in `ame_dfs.ko`, and `pulse` 82 — the vocabulary is dense — but **no
pulse-width or PRI threshold table** appears. The thresholds are numeric data in code, and none was
extracted.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| the classifier is in `ame_core.ko` / `ame_dev.ko` | **REFUTED** (it is `ame_dfs.ko`) |
| a heavy-environment detector exists | **CONFIRMED** (`DFS_heavy_env_det`) |
| channel activity is separate from the detect verdict | **CONFIRMED** (`DFSChanActivity`) |
| the pulse filter is selectable | **CONFIRMED** (`pulseFilteringModule`) |
| pulse occupancy is reported as percent and max | **CONFIRMED** |
| a hit counter and a ubus control surface exist | **CONFIRMED** |
| `target_pwr` is reported beside the pulse stats | **CONFIRMED** |
| LNA saturation is named | **REFUTED** (0 hits) |
| a PW/PRI threshold table exists in text | **REFUTED** |
| which filter is chosen, and when | **UNKNOWN / not decoded** |
| the heavy-environment criterion | **UNKNOWN / not decoded** |

## 6. The operational reading

For a co-located-tower false-DFS problem, this stage gives three **observable** handles and one
honest gap:

1. **`tot hits`** climbing while **`pulse percent/max`** stays low points at many weak events, not a
   radar;
2. **`pulseFilteringModule`** differing between two APs means they are **not running the same
   filter**, so their verdicts are not comparable;
3. **`DFS_heavy_env_det`** declaring a heavy environment means the module itself considers
   classification unreliable at that moment.

What cannot be read is an **LNA-saturation flag**, because none is named. If a deployment needs to
prove saturation-induced false DFS, it must measure the LNA state externally — the module will not
tell you.

## 7. Gaps

- **`UNKNOWN`** — which `pulseFilteringModule` values exist and what each one does.
- **`UNKNOWN`** — the `DFS_heavy_env_det` criterion and its thresholds.
- **`UNKNOWN`** — the pulse-width and PRI tables.
- **`UNKNOWN`** — the `pulse percent/max` thresholds that produce a verdict.
- **`UNKNOWN`** — how `target_pwr` couples into detection.
- **Known limit** — a named guard proves the guard exists, not what it rejects.
- **Not attempted** — dynamic validation, radar injection, LNA measurement.
