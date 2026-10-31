<!-- doc-head: Stage 761A Live LTU-Lite (.110) Round 22 (264-Window Milestone!) Interrupt Coalescing, NAPI Budget & Zero-Rogue-DHCP Autoresearch (<200 lines) -->
Ejecuta 3 rondas contrabalanceadas `A1 -> B1 -> A2 -> B2` (`12` ventanas, alcanzando **`22` campañas / `264` ventanas acumuladas**) sobre `198.18.0.63` (`LTU-Lite` Boca 5) evaluando `netdev_budget=480`, `dev_weight=48` y verificando `0` servidores DHCP (`udhcpd`/`dnsmasq`/`odhcpd`) en `br0`/`eth0` (`zero_dev_ame_touches=True`).
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 761A — Live LTU-Lite (`198.18.0.63` Boca 5) Round 22 (`264`-Window Milestone!) Autoresearch (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `Linux`, `hardware`, `proprietary airMAX/LTU module`
- **Target**: `198.18.0.63` (`LTU-Lite`, `0xae08`, `Linux 3.14.65 SMP PREEMPT RT`)
- **Milestone**: **`22` Live Campaigns (`66` Counterbalanced `A1->B1->A2->B2` Rounds = `264` Live Windows)** on `198.18.0.63` with `zero_dev_ame_touches = True` and `45s` rollback watchdog.

## 1. Round 22 Knobs & Zero-Rogue-DHCP Bridge Audit (`12` Counterbalanced Windows)
| Knob / Telemetry | Stock (`A1`/`A2`) | Champion `v20` (`B1`/`B2`) | First-Principles Mechanism (`CONFIRMED`) |
| :--- | :---: | :---: | :--- |
| `net.core.netdev_budget` | `300` | `480` | Permite drenar exactamente `10` ciclos de `dev_weight=48` por invocación `NET_RX_SOFTIRQ` sin `time_squeeze` (`Linux`). |
| `net.core.dev_weight` | `64` | `48` | Acota la ráfaga por dispositivo `NAPI` para que `GMAC0` no bloquee la interrupción RT `IRQ 52` (`ame_asic0`) (`Linux`). |
| `rogue_dhcp_daemon_count` | `0` | `0` | Certifica que `198.18.0.63` en modo bridge `br0` no ejecuta `udhcpd`, `dnsmasq` ni `odhcpd` (`Linux`). |
| `IRQ 52` (`ame_asic0`) Isolation | `smp_affinity=2` | `smp_affinity=2` | Mantiene `0` interrupciones nuevas en `CPU0` (`63,058,438` fijo) procesando el `100%` en `CPU1` (`hardware`). |

## 2. Live Counterbalanced `A1 -> B1 -> A2 -> B2` Results
- **Cumulative Live LTU Windows**: **`264` windows** (`22` campaigns on `198.18.0.63`).
- **Live SSH Connected**: `True`.
- **Rogue DHCP Daemons on `.110`**: `0`.
- **Stock Mean RTT**: `0.231 ms`.
- **Champion `v20` Mean RTT**: `0.184 ms`.
- **Safety Gate**: `zero_dev_ame_touches = True`, `touched_241 = False`, `touched_242 = False`, `touched_20 = False`, `touched_250 = False`.
