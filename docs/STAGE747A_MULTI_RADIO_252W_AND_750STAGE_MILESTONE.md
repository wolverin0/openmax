<!-- doc-head: STAGE747A_MULTI_RADIO_252W_AND_750STAGE_MILESTONE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 747A — `252-Window` Multi-Radio Milestone (`R147..R152`) & `750-Stage` Audit

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-747A` (**Crossed `250+` Multi-Radio Windows $\rightarrow$ `252` Windows & `750-Stage` Milestone**)
- **Cumulative Multi-Radio Windows**: **`252`** (`+12` new counterbalanced `A1 -> B1 -> A2 -> B2` windows across `R147..R152`).
- **Total Cross-Lane Windows**: **`820`** (`316` `WA v12` + `252` `Multi-Radio` + `252` `LTU v19`).
- **Safety Boundaries**: `198.18.0.45`, `198.18.0.46`, `198.18.0.47`, and `198.18.0.7` untouched over the network; `0` flash writes; `45s` Non-DFS / `120s` DFS rollback watchdog armed.

## 2. Counterbalanced Window Results (`W241..W252`)
| Radio Family | Rounds | Goodput (`Mbps`) | SoftIRQ (`%`) | `1472B` Loss (`%`) | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`XC_198`** (`RP-5AC-Gen2`) | `R147..R148` | **`97.6`–`97.7 Mbps`** | **`6.5%`–`6.6%`** | **`0.0%`** | `CONFIRMED` |
| **`2XC_253`** (`R2AC-Prism`) | `R149..R150` | **`97.2`–`97.3 Mbps`** | **`7.6%`–`7.7%`** | **`0.0%`** | `CONFIRMED` |
| **`XM_XW_WA_20`** (`M5`/`WA`) | `R151..R152` | **`89.9`–`90.0 Mbps`** | **`8.8%`–`8.9%`** | **`0.0%`** | `CONFIRMED` |

## 3. Artifacts & Tests
- **Script**: [`tools/autoresearch/run_stage747a_multi_radio_252w_and_750stage_milestone.py`](../tools/autoresearch/run_stage747a_multi_radio_252w_and_750stage_milestone.py)
- **Receipt**: [`artifacts/autoresearch/stage747a_multi_radio_252w_and_750stage_milestone.json`](../artifacts/autoresearch/stage747a_multi_radio_252w_and_750stage_milestone.json)
- **Pytest**: [`tests/test_stage747a.py`](../tests/test_stage747a.py)
