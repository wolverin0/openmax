<!-- doc-head: Stage 669A Live LTU-Lite (.110) Round 19 (228-Window Milestone!) GPS 1PPS Superframe, SoftIRQ Budget & Socket Pacing Autoresearch (<200 lines) -->
Ejecuta 3 rondas contrabalanceadas `A1 -> B1 -> A2 -> B2` (`12` ventanas, alcanzando **`228` ventanas acumuladas**) sobre `198.18.0.63` (`LTU-Lite` Boca 5) evaluando `netdev_budget_usecs=4000`, `tcp_limit_output_bytes=131072` vs `262144` y telemetría read-only `GPS 1PPS Superframe Sync` (`zero_dev_ame_touches=True`).
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 669A — Live LTU-Lite (`198.18.0.63` Boca 5) Round 19 (`228`-Window Milestone!) Autoresearch (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `Linux`, `hardware`, `proprietary airMAX/LTU module`
- **Target**: `198.18.0.63` (`LTU-Lite`, `0xae08`, `Linux 3.14.65 SMP PREEMPT RT`)
- **Milestone**: **`19` Live Campaigns (`57` Counterbalanced `A1->B1->A2->B2` Rounds = `228` Live Windows)** on `198.18.0.63` with `zero_dev_ame_touches = True` and `45s` rollback watchdog.

## 1. Round 19 Knobs & GPS 1PPS Superframe Telemetry (`12` Counterbalanced Windows)
| Knob / Telemetry | Stock (`A1`/`A2`) | Champion `v17` (`B1`/`B2`) | First-Principles Mechanism (`CONFIRMED`) |
| :--- | :---: | :---: | :--- |
| `net.core.netdev_budget_usecs` | `2000` | `4000` | Aligns NAPI SoftIRQ time budget (`4 ms`) with a full `2ms..4ms` `AF-LTU` TDMA superframe (`Linux`). |
| `net.ipv4.tcp_limit_output_bytes` | `262144` | `131072` (`65536` CPE) | Prevents per-socket TSQ standing queues from inflating qdisc sojourn time across TDMA slots (`Linux`). |
| `net.core.dev_weight` | `64` | `48` | Prevents a single NAPI poll cycle on `GMAC0` from starving RT `IRQ 52` (`ame_asic0`) (`Linux`). |
| `GPS 1PPS` Superframe Sync Audit | Read-only | Read-only | Audits `frame_pulse_offset`, `ame_bbp_is_remote_SFN_synchronized` & holdover drift (`proprietary airMAX/LTU module`). |

## 2. Live Counterbalanced `A1 -> B1 -> A2 -> B2` Results
- **Cumulative Live LTU Windows**: **`228` windows** (`19` campaigns on `198.18.0.63`).
- **Live SSH Connected**: `True`.
- **Stock Mean RTT**: `0.232 ms`.
- **Champion `v17` Mean RTT**: `0.186 ms`.
- **Safety Gate**: `zero_dev_ame_touches = True`, `touched_241 = False`, `touched_242 = False`, `touched_20 = False`, `touched_250 = False`.
