<!-- doc-head: STAGE590A_LTU_AME_CORE_INTERFERENCE_MITIGATION_AND_AUTO_CHANNEL_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 590A — LTU Listen-Before-Talk, interference detection and auto-frequency hooks

- **Receipt**: [`artifacts/autoresearch/stage590a_ltu_ame_core_interference_mitigation_and_auto_channel_re.json`](../artifacts/autoresearch/stage590a_ltu_ame_core_interference_mitigation_and_auto_channel_re.json)
- **Tool**: [`tools/re/build_stage590a_ltu_ame_core_interference_mitigation_and_auto_channel_re.py`](../tools/re/build_stage590a_ltu_ame_core_interference_mitigation_and_auto_channel_re.py)
- **Scope**: offline static. No module loaded, no radio contacted, nothing transmitted.

## 0. Two modules

`ame_core.ko` (3,282,052 bytes) and `ame_dev.ko` (298,760 bytes). `eab_driver.ko` is absent for the
eleventh time, but this stage does not need it — everything below is in the two modules that exist.

## 1. "Mitigation" is the word that is not there

| Token | Hits |
| :--- | :-: |
| `mitigat` | **0** |

**`REFUTED`**: the word "mitigation" appears in neither module.

**This is a naming result, not an absence result.** The mechanism is implemented as three separate
things, all richly named: **detection**, **Listen-Before-Talk**, and **auto-frequency**. This stage
reports them under those names instead of inventing a mitigation module.

## 2. LBT is a complete API, not a flag

**24 symbols.** The control set:

```
ame_core_lbt_init          ame_core_lbt_enable        ame_core_lbt_is_enable
ame_core_lbt_set_cfg       ame_core_lbt_get_cfg       ame_core_is_lbt_required
```

`lbt_api_count = 6`. Note `is_lbt_required` — a **separate predicate** from `is_enable`, which means
LBT can be enabled yet not required for a given transmit.

Four configurable parameters:

| Parameter | What it implies |
| :--- | :--- |
| `lbt_cfg_listen_window` | LBT listens for a **window**, so deferral is time-bounded |
| `lbt_cfg_pause_txframe` | LBT can **pause the TX frame** |
| `lbt_cfg_threshold` | the energy threshold for "busy" |
| `lbt_cfg_reset` | clear the state |

**`CONFIRMED`**: `lbt_has_listen_window = 1` and `lbt_has_pause_txframe = 1`.

`lbt_cfg_pause_txframe` is the important one: LBT is **integrated with the TDMA frame scheduler** of
Stage 564A, not layered above it. A listen-before-talk decision that can pause a TX frame is making
a decision *inside* the frame, which is what a TDD radio requires.

Two detection counters:

```
ame_core_lbt_incr_detect_cnt     ame_core_lbt_get_detect_cnt
```

**`CONFIRMED`**: `lbt_has_detect_counter = 1`. Detections are **counted**, so an operator can see
whether LBT is firing rather than inferring it from degraded throughput.

## 3. The sysfs group is one show with three stores

| Prefix | show | store |
| :--- | :-: | :-: |
| `lbt_cfg` | **1** | **3** (`_window_store`, `_threshold_store`, `_pauselen_store`) |
| `lbt_detects` | 1 | 1 |
| `lbt_enable` | 1 | 1 |
| `lbt_reset` | 1 | 1 |

**`CONFIRMED`**: `sysfs_pair_count = 3` complete pairs, plus `lbt_cfg` as a **single aggregate read
with three parameterised writes**.

That asymmetry is deliberate and worth recording: you can read the whole LBT configuration in one
sysfs read, but you must write each parameter separately. A naive "show/store pair" check would
report `lbt_cfg` as broken. It is not — it is a **different shape**.

`lbt_cfg_store_variants = [pauselen, threshold, window]`.

## 4. Interference detection is its own subsystem

```
ame_core_interference_det_init      ame_core_interference_det_deinit
ame_core_get_rf_interference_avg    ame_core_get_rf_interference_curr
ame_rf_interference_det_fn
```

**`CONFIRMED`**: `interference_detection_named = 1`, four controls. Two of them are **measurements**
— average and current RF interference — which means the interference level is a **readable
quantity**, not just an internal flag.

The RX-power trigger is visible in a log string:

```
RX_POWER_HIGH_INTERF_S…
```

**`CONFIRMED`**: high RX power is one of the interference triggers. That matters for co-located
sectors: a neighbouring transmitter raising your RX power is exactly the case where LBT defers to a
signal that is not actually on your channel.

## 5. Auto-frequency has seven configuration keys

From `ame_dev.ko`:

```
prefer_work_txfreq      prefer_work_rxfreq
freq_list_enabled       auto_freq_list        auto_freq_mode
smart_scan              reg_obey
```

plus `ame_freq_list` in the core.

**`CONFIRMED`**: `auto_channel_key_count = 7`, `auto_channel_hooks_named = 1`.

Three details:

- **`prefer_work_txfreq` / `prefer_work_rxfreq`** are **separate**, consistent with the split TX/RX
  frequency found in Stage 564A. The auto-channel logic can prefer different frequencies per
  direction.
- **`reg_obey`** — regulatory compliance is a **configurable flag**, which means auto-frequency can
  be constrained to a regulatory set.
- **`auto_freq_mode`** and **`smart_scan`** are mode selectors, not just enables.

**`UNKNOWN`**: which mode does what, and what metric drives selection.

## 6. What is established

| Claim | Status |
| :--- | :-: |
| "mitigation" exists as a token | **REFUTED** (0 hits) |
| LBT has a full init/enable/config/required API | **CONFIRMED** (6 controls) |
| LBT has a bounded listen window | **CONFIRMED** (`lbt_cfg_listen_window`) |
| LBT can pause the TX frame | **CONFIRMED** (`lbt_cfg_pause_txframe`) |
| LBT detections are counted | **CONFIRMED** (incr + get counters) |
| the sysfs group is 3 pairs plus 1 show / 3 stores | **CONFIRMED** |
| interference is readable as average and current RF level | **CONFIRMED** |
| high RX power is an interference trigger | **CONFIRMED** (`RX_POWER_HIGH_INTERF_S`) |
| auto-channel has seven keys with separate TX/RX preferences | **CONFIRMED** |
| the LBT threshold and window values | **UNKNOWN / runtime data** |
| the auto-channel selection policy | **UNKNOWN / not recovered** |
| a spectral-scan hook by that name in these modules | **REFUTED** (see Stage 327A for the AC side) |

## 7. The operational reading

The three mechanisms form a chain, and reading them separately is the useful part:

1. **detection** tells you the RF environment is bad (`get_rf_interference_avg` / `_curr`, high-RX
   trigger);
2. **LBT** tells you the radio is deferring (`get_detect_cnt` climbing, `pause_txframe` firing);
3. **auto-frequency** is what can actually move you (`auto_freq_mode`, `freq_list_enabled`).

A park seeing low throughput on a co-located sector can distinguish the three: if `lbt_detects`
climbs while `get_rf_interference_avg` is flat, LBT is reacting to a neighbour's energy rather than
real channel occupancy. That is a testable diagnosis the corpus supports.

## 8. Gaps

- **`UNKNOWN`** — the LBT threshold, listen-window and pause-frame values.
- **`UNKNOWN`** — what `auto_freq_mode` selects and what metric drives it.
- **`UNKNOWN`** — whether `smart_scan` differs from `auto_freq_list` in policy or only in cadence.
- **`UNKNOWN`** — how `reg_obey` constrains the candidate set.
- **`UNKNOWN`** — the decision that consumes `get_rf_interference_avg`.
- **Known limit** — a named API proves the hook exists, not the numbers behind it.
- **Not attempted** — dynamic validation, on-air deferral measurement.
