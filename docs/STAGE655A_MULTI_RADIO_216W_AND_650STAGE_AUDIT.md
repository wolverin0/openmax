<!-- doc-head: STAGE655A_MULTI_RADIO_216W_AND_650STAGE_AUDIT.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 655A — `650-Stage` Milestone Audit & `216-Window` Multi-Radio Milestone (`R129..R134`)

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-655A` (**`650-Stage` Project Milestone & `216` Multi-Radio Windows**)
- **Cumulative Multi-Radio Windows**: **`216`** (`+12` new counterbalanced `A1 -> B1 -> A2 -> B2` windows across `R129..R134`).
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `proprietary airMAX/LTU module`, `hardware`.
- **Safety Boundaries**: `198.18.0.45`, `198.18.0.46`, `198.18.0.47`, and `198.18.0.7` untouched over the network; `0` flash writes; `45s` Non-DFS / `120s` DFS rollback watchdog armed.

## 2. Cross-Fleet Telemetry Consolidation (`Stages 1A..655A`)
| Lane / Family | Cumulative Windows | Active Champion | Headline Verified Metric |
| :--- | :--- | :--- | :--- |
| **`WA` (`AR9342` + `QCA9882`)** | `252` | `WA Champion v11` / `PtP v3` | `24.83 Mbps` `VHT40`, `0.0%` `1316B` IPTV loss, `19.36h` `.84` 0-disconnect soak |
| **`Multi-Radio` (`XC`/`2XC`/`XW`/`XM`)** | **`216`** | `Cross-Fleet v54.0` | `96.8 Mbps` (`XC .198`), `96.4 Mbps` (`2XC .253`), `89.1 Mbps` (`XM/XW .20`), `0.0%` `1472B` loss |
| **`AF-LTU` (`Beetle` + `ame_ASIC0`)** | `216` | `LTU Champion v16` | `78.4%` `4096-QAM` (`12X`) residence, `576.4 Mbps`, `-42.6 dB` UL EVM |

## 3. Artifacts & Tests
- **Script**: [`tools/autoresearch/run_stage655a_multi_radio_216w_and_650stage_audit.py`](../tools/autoresearch/run_stage655a_multi_radio_216w_and_650stage_audit.py)
- **Receipt**: [`artifacts/autoresearch/stage655a_multi_radio_216w_and_650stage_audit.json`](../artifacts/autoresearch/stage655a_multi_radio_216w_and_650stage_audit.json)
- **Pytest**: [`tests/test_stage655a.py`](../tests/test_stage655a.py)
