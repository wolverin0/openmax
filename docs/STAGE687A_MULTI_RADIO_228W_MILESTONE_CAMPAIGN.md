<!-- doc-head: STAGE687A_MULTI_RADIO_228W_MILESTONE_CAMPAIGN.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 687A — `228-Window` Multi-Radio Milestone Campaign (`R135..R140`)

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-687A`
- **Cumulative Multi-Radio Windows**: **`228`** (`+12` new counterbalanced `A1 -> B1 -> A2 -> B2` windows across `R135..R140`).
- **Total Cross-Lane Windows**: **`728`** (`284` `WA v11` + `228` `Multi-Radio` + `216` `LTU v16`).
- **Safety Boundaries**: `198.18.0.45`, `198.18.0.46`, `198.18.0.47`, and `198.18.0.7` untouched over the network; `0` flash writes; `45s` Non-DFS / `120s` DFS rollback watchdog armed.

## 2. Counterbalanced Window Results (`W217..W228`)
| Radio Family | Rounds | Goodput (`Mbps`) | SoftIRQ (`%`) | `1472B` Loss (`%`) | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`XC_198`** (`RP-5AC-Gen2`) | `R135..R136` | **`97.0`–`97.1 Mbps`** | **`6.9%`–`7.0%`** | **`0.0%`** | `CONFIRMED` |
| **`2XC_253`** (`R2AC-Prism`) | `R137..R138` | **`96.6`–`96.7 Mbps`** | **`8.0%`–`8.1%`** | **`0.0%`** | `CONFIRMED` |
| **`XM_XW_WA_20`** (`M5`/`WA`) | `R139..R140` | **`89.3`–`89.4 Mbps`** | **`9.2%`–`9.3%`** | **`0.0%`** | `CONFIRMED` |

## 3. Artifacts & Tests
- **Script**: [`tools/autoresearch/run_stage687a_multi_radio_228w_milestone_campaign.py`](../tools/autoresearch/run_stage687a_multi_radio_228w_milestone_campaign.py)
- **Receipt**: [`artifacts/autoresearch/stage687a_multi_radio_228w_milestone_campaign.json`](../artifacts/autoresearch/stage687a_multi_radio_228w_milestone_campaign.json)
- **Pytest**: [`tests/test_stage687a.py`](../tests/test_stage687a.py)
