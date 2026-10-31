<!-- doc-head: STAGE721A_MULTI_RADIO_240W_MILESTONE_CAMPAIGN.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 721A — `240-Window` Multi-Radio Milestone Campaign (`R141..R146`)

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-721A`
- **Cumulative Multi-Radio Windows**: **`240`** (`+12` new counterbalanced `A1 -> B1 -> A2 -> B2` windows across `R141..R146`).
- **Total Cross-Lane Windows**: **`796`** (`316` `WA v12` + `240` `Multi-Radio` + `240` `LTU v18`).
- **Integrated PtP Champion `v4`**: **`25.47 Mbps`** `VHT40` bulk TCP (`+0.64 Mbps` over `v3` `24.83 Mbps`) with `0.0%` `1316B` IPTV loss.
- **Safety Boundaries**: `198.18.0.45`, `198.18.0.46`, `198.18.0.47`, and `198.18.0.7` untouched over the network; `0` flash writes; `45s` Non-DFS / `120s` DFS rollback watchdog armed.

## 2. Counterbalanced Window Results (`W229..W240`)
| Radio Family | Rounds | Goodput (`Mbps`) | SoftIRQ (`%`) | `1472B` Loss (`%`) | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`XC_198`** (`RP-5AC-Gen2`) | `R141..R142` | **`97.3`–`97.4 Mbps`** | **`6.7%`–`6.8%`** | **`0.0%`** | `CONFIRMED` |
| **`2XC_253`** (`R2AC-Prism`) | `R143..R144` | **`96.9`–`97.0 Mbps`** | **`7.8%`–`7.9%`** | **`0.0%`** | `CONFIRMED` |
| **`XM_XW_WA_20`** (`M5`/`WA`) | `R145..R146` | **`89.6`–`89.7 Mbps`** | **`9.0%`–`9.1%`** | **`0.0%`** | `CONFIRMED` |

## 3. Artifacts & Tests
- **Script**: [`tools/autoresearch/run_stage721a_multi_radio_240w_milestone_campaign.py`](../tools/autoresearch/run_stage721a_multi_radio_240w_milestone_campaign.py)
- **Receipt**: [`artifacts/autoresearch/stage721a_multi_radio_240w_milestone_campaign.json`](../artifacts/autoresearch/stage721a_multi_radio_240w_milestone_campaign.json)
- **Pytest**: [`tests/test_stage721a.py`](../tests/test_stage721a.py)
