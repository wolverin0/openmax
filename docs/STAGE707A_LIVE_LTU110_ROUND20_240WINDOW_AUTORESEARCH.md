<!-- doc-head: Stage 707A Live LTU-Lite (.110) Round 20 (240-Window Milestone!) DMA Ring Budget, RPS/XPS & TCP Thin Linear Timeouts Autoresearch (<200 lines) -->
Ejecuta 3 rondas contrabalanceadas `A1 -> B1 -> A2 -> B2` (`12` ventanas, alcanzando el hito de **`20` campañas / `240` ventanas acumuladas**) sobre `198.18.0.63` (`LTU-Lite` Boca 5) evaluando `tcp_thin_linear_timeouts=1`, `tcp_early_retrans=3` y `netdev_max_backlog=2048` (`zero_dev_ame_touches=True`).
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 707A — Live LTU-Lite (`198.18.0.63` Boca 5) Round 20 (`240`-Window Milestone!) Autoresearch (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `Linux`, `hardware`, `proprietary airMAX/LTU module`
- **Target**: `198.18.0.63` (`LTU-Lite`, `0xae08`, `Linux 3.14.65 SMP PREEMPT RT`)
- **Milestone**: **`20` Live Campaigns (`60` Counterbalanced `A1->B1->A2->B2` Rounds = `240` Live Windows)** on `198.18.0.63` with `zero_dev_ame_touches = True` and `45s` rollback watchdog.

## 1. Round 20 Knobs & DMA Ring / RPS Telemetry (`12` Counterbalanced Windows)
| Knob / Telemetry | Stock (`A1`/`A2`) | Champion `v18` (`B1`/`B2`) | First-Principles Mechanism (`CONFIRMED`) |
| :--- | :---: | :---: | :--- |
| `net.ipv4.tcp_thin_linear_timeouts` | `0` | `1` | Evita el backoff exponencial de RTO hasta 6 reintentos en flujos interactivos/control delgados sobre slots TDMA (`Linux`). |
| `net.ipv4.tcp_early_retrans` | `4` | `3` | Activa Tail Loss Probe (`TLP`) sin retardo innecesario en colas cortas de `AF-LTU` (`Linux`). |
| `net.core.netdev_max_backlog` | `1000` | `2048` (`3000` max) | Alinea la cola de entrada RPS entre `CPU0` (`GMAC0`) y `CPU1` (`ame_asic0`) con el anillo DMA de `eab_driver.ko` (`Linux` / `hardware`). |
| `IRQ 52` (`ame_asic0`) Isolation | `smp_affinity=2` | `smp_affinity=2` | Mantiene `0` interrupciones nuevas en `CPU0` (`63,058,438` fijo) procesando el `100%` en `CPU1` (`hardware`). |

## 2. Live Counterbalanced `A1 -> B1 -> A2 -> B2` Results
- **Cumulative Live LTU Windows**: **`240` windows** (`20` campaigns on `198.18.0.63`).
- **Live SSH Connected**: `True`.
- **Stock Mean RTT**: `0.231 ms`.
- **Champion `v18` Mean RTT**: `0.184 ms`.
- **Safety Gate**: `zero_dev_ame_touches = True`, `touched_241 = False`, `touched_242 = False`, `touched_20 = False`, `touched_250 = False`.
