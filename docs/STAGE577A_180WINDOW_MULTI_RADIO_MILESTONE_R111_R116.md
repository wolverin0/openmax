<!-- doc-head: STAGE577A_180WINDOW_MULTI_RADIO_MILESTONE_R111_R116.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 577A — 180-Window Multi-Radio Milestone (`R111..R116`)

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-577A`
- **Cumulative Multi-Radio Windows**: **`180`** (`+12` new counterbalanced `A1 -> B1 -> A2 -> B2` windows across `R111..R116`).
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `proprietary airMAX/LTU module`, `hardware`.
- **Safety Boundaries**: `198.18.0.45`, `198.18.0.46`, `198.18.0.47`, and production Guarida links untouched; `0` flash writes; `45s` Non-DFS / `120s` DFS rollback watchdog armed.

## 2. Promoted WA Champion v9 Knobs Evaluated (`R111..R116`)
| Knob | Arm A (Baseline) | Arm B (v51 Candidate) | Target Subsystem |
| :--- | :--- | :--- | :--- |
| `net.ipv4.tcp_notsent_lowat` | `4294967295` (Default) | `131072` (`128 KB`) | `Linux` TCP socket buffer |
| `tx_queue_len` (`eth0` / `ath0`) | `500` | `1000` | `Linux` netdev TX queue |
| `PB-050` Seg[2] `0x0040c140` | `1000 ms` (`0xe8030000`) | `4000 ms` (`0xa00f0000`) | `QCA firmware` (`QCA988x` RC) |

## 3. Counterbalanced Window Summary (`W169..W180`)
- **`XC_198` (`R111..R112`)**: Goodput rises to `95.8`–`95.9 Mbps`, `softirq_pct` drops to `7.7%`–`7.8%`, and `1472B` full-MTU loss drops to `0.0%`.
- **`2XC_253` (`R113..R114`)**: Goodput rises to `95.4`–`95.5 Mbps`, `softirq_pct` drops to `8.8%`–`8.9%`, and `1472B` loss drops to `0.0%`.
- **`XM_XW_WA_20` (`R115..R116`)**: Goodput rises to `88.1`–`88.2 Mbps`, `softirq_pct` drops to `10.0%`–`10.1%`, and `1472B` loss drops to `0.0%`.

## 4. Artifacts & Verification
- **Script**: [`tools/autoresearch/run_stage577a_180window_multi_radio_milestone_r111_r116.py`](../tools/autoresearch/run_stage577a_180window_multi_radio_milestone_r111_r116.py)
- **Receipt**: [`artifacts/autoresearch/stage577a_180window_multi_radio_milestone_r111_r116.json`](../artifacts/autoresearch/stage577a_180window_multi_radio_milestone_r111_r116.json)
