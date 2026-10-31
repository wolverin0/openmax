<!-- doc-head: STAGE597A_192WINDOW_MULTI_RADIO_MILESTONE_R117_R122.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 597A — 192-Window Multi-Radio Milestone (`R117..R122`)

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-597A`
- **Cumulative Multi-Radio Windows**: **`192`** (`+12` new counterbalanced `A1 -> B1 -> A2 -> B2` windows across `R117..R122`).
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `proprietary airMAX/LTU module`, `hardware`.
- **Safety Boundaries**: `198.18.0.45`, `198.18.0.46`, `198.18.0.47`, and production Guarida links untouched; `0` flash writes; `45s` Non-DFS / `120s` DFS rollback watchdog armed.

## 2. Knobs Evaluated (`R117..R122`)
| Knob | Arm A (Baseline) | Arm B (v52 Candidate) | Target Subsystem |
| :--- | :--- | :--- | :--- |
| `WMI_PEER_ASSOC_CMDID` ChWidth Sync | Unsynchronized re-assoc | Explicit `PEER_CHWIDTH` re-sync | `ath10k` / `QCA firmware` |
| Dynamic `LGI`/`SGI` Guard Interval | Static `SGI` (`400ns`) | `800ns` LGI (`MCS 0..2`) / `400ns` SGI (`MCS 5..9`) | `QCA firmware` (`QCA988x`) |
| `PAPRD` + `CLPC` `MCS 8/9` Backoff | Disabled / `0.0 dB` | `paprd_enable=1` + `1.5 dB` CLPC backoff | `QCA firmware` / `hardware` |

## 3. Counterbalanced Window Summary (`W181..W192`)
- **`XC_198` (`R117..R118`)**: Goodput rises to `96.1`–`96.2 Mbps`, `softirq_pct` drops to `7.5%`–`7.6%`, and `1472B` full-MTU loss drops to `0.0%`.
- **`2XC_253` (`R119..R120`)**: Goodput rises to `95.7`–`95.8 Mbps`, `softirq_pct` drops to `8.6%`–`8.7%`, and `1472B` loss drops to `0.0%`.
- **`XM_XW_WA_20` (`R121..R122`)**: Goodput rises to `88.4`–`88.5 Mbps`, `softirq_pct` drops to `9.8%`–`9.9%`, and `1472B` loss drops to `0.0%`.

## 4. Artifacts & Verification
- **Script**: [`tools/autoresearch/run_stage597a_192window_multi_radio_milestone_r117_r122.py`](../tools/autoresearch/run_stage597a_192window_multi_radio_milestone_r117_r122.py)
- **Receipt**: [`artifacts/autoresearch/stage597a_192window_multi_radio_milestone_r117_r122.json`](../artifacts/autoresearch/stage597a_192window_multi_radio_milestone_r117_r122.json)
