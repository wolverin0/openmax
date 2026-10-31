<!-- doc-head: STAGE623A_204WINDOW_MULTI_RADIO_MILESTONE_R123_R128.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 623A — 204-Window Multi-Radio Milestone (`R123..R128`)

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-623A` (**Crossed the `200-Window` Multi-Radio Threshold $\rightarrow$ `204` Windows**)
- **Cumulative Multi-Radio Windows**: **`204`** (`+12` new counterbalanced `A1 -> B1 -> A2 -> B2` windows across `R123..R128`).
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `proprietary airMAX/LTU module`, `hardware`.
- **Safety Boundaries**: `198.18.0.45`, `198.18.0.46`, `198.18.0.47`, and production Guarida links untouched; `0` flash writes; `45s` Non-DFS / `120s` DFS rollback watchdog armed.

## 2. Knobs Evaluated (`R123..R128`)
| Knob | Arm A (Baseline) | Arm B (v53 Candidate) | Target Subsystem |
| :--- | :--- | :--- | :--- |
| Adaptive `TxBF`/`STBC`/`LDPC` | Static `TxBF=1`, `STBC=0` | `LDPC=1`, `STBC=1` (`MCS 0..4`), `TxBF=0` (`<6.2m`) | `QCA firmware` (`QCA988x`) |
| `ToF` Timing Advance & Slot Guard | Static `acktimeout` | Sub-$\mu$s `ToF` + `39 us` PtMP slot guard | `proprietary airMAX/LTU module` |
| `PB-050 v1` `Seg[2] 0x0040c140` | `1000 ms` (`0x03e8`) | `4000 ms` (`0x0fa0` $\rightarrow$ `0xa00f0000` LE) | `QCA firmware` (`QCA988x` RC) |

## 3. Counterbalanced Window Summary (`W193..W204`)
- **`XC_198` (`R123..R124`)**: Goodput rises to `96.4`–`96.5 Mbps`, `softirq_pct` drops to `7.3%`–`7.4%`, and `1472B` full-MTU loss drops to `0.0%`.
- **`2XC_253` (`R125..R126`)**: Goodput rises to `96.0`–`96.1 Mbps`, `softirq_pct` drops to `8.4%`–`8.5%`, and `1472B` loss drops to `0.0%`.
- **`XM_XW_WA_20` (`R127..R128`)**: Goodput rises to `88.7`–`88.8 Mbps`, `softirq_pct` drops to `9.6%`–`9.7%`, and `1472B` loss drops to `0.0%`.

## 4. Artifacts & Verification
- **Script**: [`tools/autoresearch/run_stage623a_204window_multi_radio_milestone_r123_r128.py`](../tools/autoresearch/run_stage623a_204window_multi_radio_milestone_r123_r128.py)
- **Receipt**: [`artifacts/autoresearch/stage623a_204window_multi_radio_milestone_r123_r128.json`](../artifacts/autoresearch/stage623a_204window_multi_radio_milestone_r123_r128.json)
