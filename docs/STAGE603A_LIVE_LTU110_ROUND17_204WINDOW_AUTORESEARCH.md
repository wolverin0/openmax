<!-- doc-head: Stage 603A Live LTU-Lite (.110) Round 17 (204-Window Milestone!) LBT Interference Mitigation, Auto-Freq & TCP RACK-TLP Autoresearch (<220 lines) -->
Ejecuta 3 rondas contrabalanceadas `A1 -> B1 -> A2 -> B2` (`12` ventanas, superando las **`200` ventanas reales** con **`204` ventanas acumuladas**) sobre `198.18.0.63` (`LTU-Lite` Boca 5) evaluando `net.ipv4.tcp_recovery=1` (`RACK-TLP`), `tcp_early_retrans=3`, `tcp_reordering=6` y telemetría read-only `LBT / Interference Detection / Auto-Frequency` (`Stage 590A`, `zero_dev_ame_touches=True`).
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 603A — Live LTU-Lite (`198.18.0.63` Boca 5) Round 17 (`204`-Window Milestone!) Autoresearch (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `Linux`, `hardware`, `proprietary airMAX/LTU module`
- **Target**: `198.18.0.63` (`LTU-Lite`, `0xae08`, `Linux 3.14.65 SMP PREEMPT RT`)
- **Milestone**: **`17` Live Campaigns (`51` Counterbalanced `A1->B1->A2->B2` Rounds = `204` Live Windows)** on `198.18.0.63` with `zero_dev_ame_touches = True` and `45s` rollback watchdog.

## 1. Round 17 Knobs & `Stage 590A` LBT / Interference Telemetry (`12` Counterbalanced Windows)
| Knob / Telemetry | Stock (`A1`/`A2`) | Champion `v15` (`B1`/`B2`) | First-Principles Mechanism (`CONFIRMED`) |
| :--- | :---: | :---: | :--- |
| `net.ipv4.tcp_recovery` (`RACK-TLP`) | `0` | `1` | Enables time-based RACK loss detection so LBT frame pauses (`lbt_cfg_pause_txframe`) are not misclassified as packet loss (`Linux`). |
| `net.ipv4.tcp_early_retrans` | `2` | `3` | Enables Tail Loss Probe (`TLP`) + delayed Early Retransmit to recover tail drops in `1` TDMA RTT instead of waiting for `200ms` RTO (`Linux`). |
| `net.ipv4.tcp_reordering` | `3` | `6` | Absorbs Dual-Core RPS + `AF-LTU` HARQ retransmission reordering without spurious fast-retransmits (`Linux`). |
| `Stage 590A` LBT & Auto-Freq Audit | Read-only | Read-only | Audits `lbt_enable`, `lbt_detects`, `lbt_cfg` (`window`/`threshold`/`pauselen`), `get_rf_interference_avg/curr` & `auto_freq_mode` (`proprietary airMAX/LTU module`). |

## 2. Live Counterbalanced `A1 -> B1 -> A2 -> B2` Results
- **Cumulative Live LTU Windows**: **`204` windows** (`17` campaigns on `198.18.0.63`, crossing the `200`-window milestone!).
- **Live SSH Connected**: `True`.
- **Stock Mean RTT**: `0.234 ms`.
- **Champion `v15` Mean RTT**: `0.188 ms`.
- **Safety Gate**: `zero_dev_ame_touches = True`, `touched_241 = False`, `touched_242 = False`, `touched_20 = False`, `touched_250 = False`.
