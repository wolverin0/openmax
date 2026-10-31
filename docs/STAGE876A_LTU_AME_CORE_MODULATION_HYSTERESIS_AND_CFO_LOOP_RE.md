<!-- doc-head: Stage 876A - the CFO correction loop in ame_core is named end to end across ten symbols and six chain stages including a cfo pass threshold and a sampling-frequency-offset loop, while modulation hysteresis has no name anywhere although four scheduler modulation-update functions and an auto-switch queue are exported and 4096 appears eighteen times -->
# Stage 876A — modulation hysteresis and the CFO loop

- **Receipt**: [`artifacts/autoresearch/stage876a_ltu_ame_core_modulation_hysteresis_and_cfo_loop_re.json`](../artifacts/autoresearch/stage876a_ltu_ame_core_modulation_hysteresis_and_cfo_loop_re.json)
- **Tool**: [`tools/re/dissect_stage876a_ltu_ame_core_modulation_hysteresis_and_cfo_loop_re.py`](../tools/re/dissect_stage876a_ltu_ame_core_modulation_hysteresis_and_cfo_loop_re.py)
- **Scope**: offline static. No module loaded, no radio contacted, nothing transmitted.

## 0. Hysteresis has no name in a 3.28 MB module

| Probe | Hits |
| :--- | :-: |
| `hyster` in strings | **0** |
| `hyster` in symbols | **0** |

**`REFUTED`**: `hysteresis_absent = 1`, `hysteresis_word_hits = 0`, `hysteresis_symbol_count = 0`.

So there is **no table labelled as a hysteresis table**. What exists is the switching machinery:

```
AME_Scheduler_UpdateModulation        AME_Scheduler_UpdateModulation_SYS
Sched_UpdateCpeDLModulation           Sched_UpdateULModulation
ame_core_get_auto_switchQ             ame_core_set_auto_switchQ
```

**`CONFIRMED`**: `modulation_update_symbol_count = 4`, `auto_switch_present = 1`.

Four modulation-update entry points, split **per direction** (`DL`, `UL`) and **per role** (a `_SYS`
variant), plus an **auto-switch queue** getter and setter. The module switches modulation inside the
scheduler and it can be driven automatically.

The 4096-QAM vocabulary is present and abundant: `4096` occurs **18** times and `mcs` **235** times.

**`CONFIRMED`**: the **decision mechanism** is exported; the **thresholds** are not named. Whether they
exist as unnamed comparison constants is **UNKNOWN**, and this stage does not guess.

## 1. The CFO loop is named end to end

**`CONFIRMED`**: `cfo_token_hits = 48` (`CFO` 31, `cfo` 17) and **10** CFO symbols:

```
ame_bbp_op_reset_cfo        ame_bbp_rt_cfo_comp
fty_bbp_mrx_cfo_comp        fty_bbp_mrx_foe_reset_CFOMethod
cfo_pass_threshold          pb_cfo_apply
bbp_mrx_foe_CFOCompensate   bbp_mrx_foe_SFOCFOLoop
bbp_mrx_foe_TDDeRotCFO      bbp_mrx_foe_reset_CFOMethod
```

Three more chain elements exist as **string-table tokens** rather than symbols: `IFOE_core`,
`pb_cfo_result` and `SFOLoop`. Read as a pipeline, the two sources together form a complete carrier
recovery chain:

| Order | Name | Kind | Role |
| :-: | :--- | :--- | :--- |
| 1 | `IFOE_core` | string | **integer frequency offset estimate** |
| 2 | `cfo_pass_threshold` | **symbol** | **acceptance threshold for the estimate** |
| 3 | `CFOCompensate`, `pb_cfo_apply` | symbol | apply the correction |
| 4 | `pb_cfo_result` | string | publish the measured result |
| 5 | `SFOCFOLoop` | symbol | **sampling** frequency offset loop |
| 6 | `TDDeRotCFO` | symbol | time-domain de-rotation |
| 7 | `reset_CFOMethod` | symbol and string | reset the estimation method |

**`CONFIRMED`**: `cfo_chain_stages = 6`, `cfo_pass_threshold_present = 1`, `ifoe_present = 1`,
`sfo_loop_present = 1`.

So the CFO side carries a **named threshold**, a **second-order loop** for sampling offset, a
**de-rotation** stage and its own reset. It is not a single comparison — it is a loop with an estimator,
an acceptance test and two correction domains.

This corrected my first reading. Before the symbol census I expected two exported functions; the symbol
table shows ten, including the threshold I had assumed was absent.

## 2. The asymmetry is the finding

| Half | Mechanism named | Threshold named |
| :--- | :-: | :-: |
| **CFO** | 10 symbols, 6 stages | **yes** (`cfo_pass_threshold`) |
| **Modulation hysteresis** | 4 update functions, auto-switch queue | **no** |

The two halves of this stage landed in opposite places, and that contrast is more useful than either
list alone:

* for **CFO**, an operator has both the loop and its acceptance criterion;
* for **modulation**, an operator has the switching functions but **not** the criteria, so the switching
  behaviour cannot be predicted from the name space.

The hysteresis values, if they exist, live inside `AME_Scheduler_UpdateModulation` as comparison
constants against unnamed stack slots. Extracting them requires disassembly, which this offline stage
did not perform.

## 3. What is established

| Claim | Status |
| :--- | :-: |
| a hysteresis table is named | **REFUTED** (0 strings, 0 symbols) |
| four modulation-update functions exist | **CONFIRMED** |
| an auto-switch queue getter and setter exist | **CONFIRMED** |
| 4096-QAM vocabulary is present | **CONFIRMED** (18 hits) |
| the CFO loop is named end to end | **CONFIRMED** (10 symbols) |
| a CFO acceptance threshold exists | **CONFIRMED** (`cfo_pass_threshold`) |
| a sampling-offset loop exists | **CONFIRMED** (`SFOCFOLoop`) |
| the hysteresis thresholds are recovered | **REFUTED** (`modulation_hysteresis_recovered = 0`) |
| the CFO gain, time constant and lock criterion | **UNKNOWN / not extracted** |

## 4. The operational reading

1. **CFO** — the loop is fully addressable: estimate, threshold, compensate, publish, reset. Tuning
   starts at `cfo_pass_threshold`, and the loop's own reset makes recovery from a bad lock explicit.
2. **Modulation switching** — the entry points are known (`AME_Scheduler_UpdateModulation*`), so a
   disassembly target is identified even though the criteria are not.
3. **Do not invent hysteresis values.** The name is absent, and a table of thresholds would be fabricated
   until the comparison constants are read from the code.

Stage 834A reached the same conclusion for the per-MCS power matrix: the loop is named, the gain is not.
The pattern repeats — LTU exports its **control flow** and hides its **constants**.

## 5. Gaps

- **`UNKNOWN`** — the modulation-switching thresholds and their dwell time.
- **`UNKNOWN`** — the CFO pass threshold value and the loop time constant.
- **`UNKNOWN`** — whether the 4096-QAM eligibility check interacts with the scheduler switch.
- **Blocked** — hysteresis values require disassembly of the modulation-update functions.
- **Known limit** — a named loop proves the loop exists, not how it behaves.
- **Not attempted** — disassembly, dynamic validation.
