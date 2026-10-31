<!-- doc-head: Stage 834A - ATPC is not spelled atpc on LTU where the mechanism is autopwr with 48 hits and a named algorithm plus a per-MCS power adjustment, EVM is measured four ways but no target EVM in dB exists because the requirement is derived from BLER and MCS selection rather than stored as a threshold -->
<!-- /doc-head -->
# Stage 834A — LTU ATPC closed loop and the EVM target for 4096-QAM

- **Receipt**: [`artifacts/autoresearch/stage834a_ltu_ame_core_ul_power_control_and_target_evm_re.json`](../artifacts/autoresearch/stage834a_ltu_ame_core_ul_power_control_and_target_evm_re.json)
- **Tool**: [`tools/re/dissect_stage834a_ltu_ame_core_ul_power_control_and_target_evm_re.py`](../tools/re/dissect_stage834a_ltu_ame_core_ul_power_control_and_target_evm_re.py)
- **Scope**: offline static. No module loaded, no radio contacted, nothing transmitted.

## 0. One mechanism, two spellings across the two lines

| Token | `ame_core.ko` + `ame_dev.ko` |
| :--- | :-: |
| `atpc` | **0** |
| `ATPC` | **0** |
| **`autopwr`** | **48** |
| `auto_pwr` | 8 |
| `ptmp_ap_autopwr` | 6 |

**`REFUTED`**: `atpc_name_absent = 1` on LTU.

Stage 831A found the **AC** side uses `atpc_*` (`atpc_target_rssi`, `atpc_max_power`,
`atpc_min_power`). The **LTU** side uses `autopwr`. Same mechanism, two names, two lines.

**A single-name search misses one full product line.** That is the practical consequence, and it is
the kind of defect that makes an audit conclude "this feature does not exist on LTU".

## 1. The closed loop is a named algorithm, not a heuristic

```
autopwr_reset          auto_pwr_init_handlr      auto_pwr_run_handlr
autopwr_algo           auto_pwr_adjust_pwr_by_mcs
```

**`CONFIRMED`**: `algo_named = 1`, `run_handler = 1`, `per_mcs_adjust_named = 1`.

Three of those names carry the whole design:

| Symbol | Role |
| :--- | :--- |
| `autopwr_algo` | the **algorithm object** |
| `auto_pwr_run_handlr` | the **periodic handler** that drives it |
| **`auto_pwr_adjust_pwr_by_mcs`** | power adjusted **per MCS** |

**`auto_pwr_adjust_pwr_by_mcs` is the decisive name.** 4096-QAM needs the highest MCS backed off
harder than a low one — the module states that directly rather than applying one global backoff.

## 2. EVM is measured four ways; the target does not exist

```
bbp_mrx_evm_get_mode_and_result    bbp_mrx_evm_set
ame_bbp_get_evm_dump               bbp_mrx_evm_print
```

**`CONFIRMED`**: `evm_measurement_count = 4` — EVM is captured, stored, dumped and printed.

**`REFUTED`**: `target_evm` returns **0**, and `evm_target` does not exist either.
`target_evm_absent = 1`.

So the **EVM requirement in dB is not in the module**. The measurement side is complete; the
requirement side is absent.

**The reason is structural, and §3 explains it.**

## 3. 4096-QAM is gated and the target is derived

```
check_4096mimo_ofdm      choose_mcsTPindex_ofdm      autoMCS_updateDL
callhome_bler_log
```

**`CONFIRMED`**: `qam_gate_named = 1`, `mcs_selector_named = 1`.

The loop is:

```
measure EVM + BLER  ->  choose MCS  ->  adjust power per MCS
```

**No fixed dB threshold is needed** because the target is **derived** from the BLER feedback and the
MCS choice. That is why `target_evm` is absent: it is not a constant in this design, it is an
**emergent consequence** of the closed loop.

That reframes the stage's question. Asking "what is the target EVM for 4096-QAM" presumes a stored
threshold; the module instead says "hold the MCS, and let BLER drive the backoff".

## 4. What is established

| Claim | Status |
| :--- | :-: |
| ATPC is called `atpc` on LTU | **REFUTED** (0) |
| it is called `autopwr` on LTU | **CONFIRMED** (48) |
| the AC line uses `atpc_*` | **CONFIRMED** (831A) |
| a named algorithm object exists | **CONFIRMED** (`autopwr_algo`) |
| power is adjusted per MCS | **CONFIRMED** (`auto_pwr_adjust_pwr_by_mcs`) |
| EVM is measured and dumped | **CONFIRMED** (4 symbols) |
| a target EVM in dB exists | **REFUTED** (0) |
| 4096-QAM has an eligibility gate and an MCS selector | **CONFIRMED** |
| the per-MCS gain matrix | **UNKNOWN / not recovered** |
| the LNA-saturation backoff rule | **UNKNOWN / not in the module** |

## 5. The operational reading

For "hold 4096-QAM 12x without saturating the AP LNA", the module offers a **loop, not a number**:

1. `check_4096mimo_ofdm` says whether the mode is eligible;
2. `choose_mcsTPindex_ofdm` picks the MCS;
3. `auto_pwr_adjust_pwr_by_mcs` backs the power off **for that MCS**;
4. `callhome_bler_log` feeds the error rate back.

What it will not give you is a target EVM to hold. A bench that sets one would be **inventing a
constant the design does not use**.

## 6. Gaps

- **`UNKNOWN`** — the per-MCS backoff matrix and its step size.
- **`UNKNOWN`** — whether a target EVM exists in firmware (the host has none).
- **`UNKNOWN`** — the BLER threshold that triggers a step.
- **`UNKNOWN`** — how LNA saturation is detected, if at all (Stage 824A: `lna` = 0).
- **Known limit** — a named loop proves the loop exists, not its gain.
- **Not attempted** — dynamic validation, EVM measurement on air.
