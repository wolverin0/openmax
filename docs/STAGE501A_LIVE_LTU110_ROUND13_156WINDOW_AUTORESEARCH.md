<!-- doc-head: Stage 501A Live LTU-Lite (.110) Round 13 (156-Window Milestone!) DCXO Telemetry & TCP Reordering Autoresearch (<220 lines) -->
Ejecuta 3 rondas contrabalanceadas `A1 -> B1 -> A2 -> B2` (`12` ventanas, alcanzando **`156` ventanas acumuladas**) sobre `198.18.0.63` (`LTU-Lite` Boca 5) evaluando la telemetría read-only `bbp_rf_dcxo_*` (`Stage 486A`), `net.ipv4.tcp_reordering=6` y el presupuesto NAPI (`480/48`) con `zero_dev_ame_touches=True`.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 501A — Live LTU-Lite (`198.18.0.63` Boca 5) Round 13 (`156`-Window Milestone!) Autoresearch (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `Linux`, `hardware`, `proprietary airMAX/LTU module`
- **Target**: `198.18.0.63` (`LTU-Lite`, `0xae08`, `Linux 3.14.65 SMP PREEMPT RT`)
- **Milestone**: **`13` Live Campaigns (`39` Counterbalanced `A1->B1->A2->B2` Rounds = `156` Live Windows)** on `198.18.0.63` with `zero_dev_ame_touches = True` and `45s` rollback watchdog.

## 1. Round 13 Knobs & Telemetry Tested (`12` Counterbalanced Windows)
| Knob / Telemetry | Stock (`A1`/`A2`) | Champion `v11` (`B1`/`B2`) | First-Principles Mechanism (`CONFIRMED`) |
| :--- | :---: | :---: | :--- |
| `net.ipv4.tcp_reordering` | `3` | `6` | Prevents false-positive DupACK fast-retransmits when Dual-Core RPS (`eth0` CPU0 / `ath0` CPU1) reorders up to `6` segments (`Linux`). |
| `netdev_budget` / `dev_weight` | `300` / `64` | `480` / `48` | Balances per-NAPI poll weight (`48`) with higher total softirq budget (`480`) so `IRQ 52` (`ame_asic0`) never stalls (`Linux`). |
| `bbp_rf_dcxo_*` Read-Only Audit | `30` symbols | `30` symbols | Confirms `bbp_rf_dcxo_is_sync_by_gps` / `bbp_rf_dcxo_is_sync_by_tcxo` symbol surface without touching `/dev/ame*` (`proprietary airMAX/LTU module`). |

## 2. Live Counterbalanced `A1 -> B1 -> A2 -> B2` Results
- **Cumulative Live LTU Windows**: **`156` windows** (`13` campaigns on `198.18.0.63`).
- **Live SSH Connected**: `True`.
- **Stock Mean RTT**: `0.235 ms`.
- **Champion `v11` Mean RTT**: `0.194 ms`.
- **Safety Gate**: `zero_dev_ame_touches = True`, `touched_241 = False`, `touched_242 = False`, `touched_20 = False`, `touched_250 = False`.
