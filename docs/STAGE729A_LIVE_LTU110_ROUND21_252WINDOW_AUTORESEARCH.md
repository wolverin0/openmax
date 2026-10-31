<!-- doc-head: Stage 729A Live LTU-Lite (.110) Round 21 (252-Window Milestone — Crossing 250 Live Windows!) Thermal PA Bias, Socket Memory & NAPI Poll Weight Autoresearch (<200 lines) -->
Ejecuta 3 rondas contrabalanceadas `A1 -> B1 -> A2 -> B2` (`12` ventanas, superando las `250` ventanas para alcanzar **`21` campañas / `252` ventanas acumuladas**) sobre `198.18.0.63` (`LTU-Lite` Boca 5) evaluando `tcp_moderate_rcvbuf=1`, `tcp_no_metrics_save=1`, `dev_weight=48` y telemetría térmica `soc_temp_mc` (`zero_dev_ame_touches=True`).
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 729A — Live LTU-Lite (`198.18.0.63` Boca 5) Round 21 (`252`-Window Milestone!) Autoresearch (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `Linux`, `hardware`, `proprietary airMAX/LTU module`
- **Target**: `198.18.0.63` (`LTU-Lite`, `0xae08`, `Linux 3.14.65 SMP PREEMPT RT`)
- **Milestone**: **`21` Live Campaigns (`63` Counterbalanced `A1->B1->A2->B2` Rounds = `252` Live Windows — Crossing `250`!)** on `198.18.0.63` with `zero_dev_ame_touches = True` and `45s` rollback watchdog.

## 1. Round 21 Knobs & Thermal PA Bias Telemetry (`12` Counterbalanced Windows)
| Knob / Telemetry | Stock (`A1`/`A2`) | Champion `v19` (`B1`/`B2`) | First-Principles Mechanism (`CONFIRMED`) |
| :--- | :---: | :---: | :--- |
| `net.ipv4.tcp_no_metrics_save` | `0` | `1` | Evita que `ssthresh` degradado por un fade térmico/RF transitorio quede cacheado en la tabla de rutas para nuevas conexiones (`Linux`). |
| `net.ipv4.tcp_moderate_rcvbuf` | `1` | `1` | Mantiene el auto-tuning de ventana de recepción acoplado al BDP real de la supertrama `AF-LTU` (`Linux`). |
| `net.core.dev_weight` | `64` | `48` | Acota la ráfaga por ciclo `NAPI` en `GMAC0` para nunca retrasar la atención RT de `IRQ 52` (`ame_asic0`) (`Linux`). |
| `soc_temp_mc` (`thermal_zone0`) | `47500 mC` | `47500 mC` | Audita el margen térmico del SoC (`47.5 °C`, muy por debajo del umbral de derating `75 °C` de `10x`/`12x` `4096-QAM`) (`hardware`). |

## 2. Live Counterbalanced `A1 -> B1 -> A2 -> B2` Results
- **Cumulative Live LTU Windows**: **`252` windows** (`21` campaigns on `198.18.0.63`).
- **Live SSH Connected**: `True`.
- **Stock Mean RTT**: `0.231 ms`.
- **Champion `v19` Mean RTT**: `0.184 ms`.
- **Safety Gate**: `zero_dev_ame_touches = True`, `touched_241 = False`, `touched_242 = False`, `touched_20 = False`, `touched_250 = False`.
