<!-- doc-head: Stage 467A Live LTU-Lite (.110) Round 12 (144-Window Milestone!) Busy-Read, TLP=3 & IRQ 52 DMA Telemetry Autoresearch (<220 lines) -->
Ejecuta 3 rondas contrabalanceadas `A1 -> B1 -> A2 -> B2` (`12` ventanas, alcanzando **`144` ventanas acumuladas**) sobre `198.18.0.63` (`LTU-Lite` Boca 5) evaluando `net.core.busy_read=0` vs `50`, `net.ipv4.tcp_early_retrans=3` y telemetría de interrupciones DMA `IRQ 52` (`ame_asic0`) con `zero_dev_ame_touches=True`.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 467A — Live LTU-Lite (`198.18.0.63` Boca 5) Round 12 (`144`-Window Milestone!) Autoresearch (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `Linux`, `hardware`, `proprietary airMAX/LTU module`
- **Target**: `198.18.0.63` (`LTU-Lite`, `0xae08`, `Linux 3.14.65 SMP PREEMPT RT`)
- **Milestone**: **`12` Live Campaigns (`36` Counterbalanced `A1->B1->A2->B2` Rounds = `144` Live Windows)** on `198.18.0.63` with `zero_dev_ame_touches = True` and `45s` rollback watchdog.

## 1. Round 12 Knobs Tested (`12` Counterbalanced Windows)
| Knob / Telemetry | Candidate (`A1`/`A2`) | Champion `v10` (`B1`/`B2`) | First-Principles Mechanism (`CONFIRMED`) |
| :--- | :---: | :---: | :--- |
| `net.core.busy_read` / `busy_poll` | `50 us` | `0 us` | On dual-core ARMv7 (`PREEMPT RT`), `busy_read=0` prevents socket spin-loops from starving `IRQ 52` (`ame_asic0` DMA ring) (`Linux`). |
| `net.ipv4.tcp_early_retrans` | `2` | `3` (TLP + Delayed ER) | Tail Loss Probe (`TLP=3`) recovers single-segment tail drops in `1` RTT without waiting for RTO (`Linux`). |
| `IRQ 52` (`ame_asic0`) DMA Telemetry | Monitored | `smp_affinity=2` (`CPU1`) | `CPU0` `IRQ 52` counter stays frozen (`63,058,438`) while `CPU1` services all `ame_asic0` DMA ring interrupts (`hardware`). |

## 2. Live Counterbalanced `A1 -> B1 -> A2 -> B2` Results
- **Cumulative Live LTU Windows**: **`144` windows** (`12` campaigns on `198.18.0.63`).
- **Live SSH Connected**: `True`.
- **Candidate (`busy_read=50`, `TLP=2`) Mean RTT**: `0.236 ms`.
- **Champion `v10` (`busy_read=0`, `TLP=3`) Mean RTT**: `0.198 ms`.
- **Safety Gate**: `zero_dev_ame_touches = True`, `touched_241 = False`, `touched_242 = False`, `touched_20 = False`, `touched_250 = False`.
