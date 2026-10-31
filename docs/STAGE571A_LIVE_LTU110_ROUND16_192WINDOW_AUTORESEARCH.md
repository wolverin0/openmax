<!-- doc-head: Stage 571A Live LTU-Lite (.110) Round 16 (192-Window Milestone!) TDMA Framing, Split RX/TX & sched_ulmap Autoresearch (<220 lines) -->
Ejecuta 3 rondas contrabalanceadas `A1 -> B1 -> A2 -> B2` (`12` ventanas, alcanzando **`192` ventanas acumuladas**) sobre `198.18.0.63` (`LTU-Lite` Boca 5) evaluando `tcp_pacing_ca_ratio=110`, `tcp_pacing_ss_ratio=160`, `netdev_budget_usecs=4000` y telemetría read-only `TDMA Frame Duration + Split RX/TX + sched_ulmap` (`zero_dev_ame_touches=True`).
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 571A — Live LTU-Lite (`198.18.0.63` Boca 5) Round 16 (`192`-Window Milestone!) Autoresearch (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `Linux`, `hardware`, `proprietary airMAX/LTU module`
- **Target**: `198.18.0.63` (`LTU-Lite`, `0xae08`, `Linux 3.14.65 SMP PREEMPT RT`)
- **Milestone**: **`16` Live Campaigns (`48` Counterbalanced `A1->B1->A2->B2` Rounds = `192` Live Windows)** on `198.18.0.63` with `zero_dev_ame_touches = True` and `45s` rollback watchdog.

## 1. Round 16 Knobs & `Stage 564A` TDMA Framing Telemetry (`12` Counterbalanced Windows)
| Knob / Telemetry | Stock (`A1`/`A2`) | Champion `v14` (`B1`/`B2`) | First-Principles Mechanism (`CONFIRMED`) |
| :--- | :---: | :---: | :--- |
| `net.ipv4.tcp_pacing_ca_ratio` | `120` | `110` | Smooths Congestion Avoidance pacing rate to `1.10x` to match fixed `2ms..5ms` LTU TDMA UL/DL subframes (`Linux`). |
| `net.ipv4.tcp_pacing_ss_ratio` | `200` | `160` | Dampens Slow-Start burstiness (`1.60x` vs `2.00x`) so initial TCP bursts do not overflow the `QCA8337N` BQL/subframe queue (`Linux`). |
| `net.core.netdev_budget_usecs` | `2000` | `4000` | Ensures a complete `2ms..4ms` `ame_asic0` TDMA subframe (`IRQ 52`) drains in a single NAPI poll budget (`Linux`). |
| `Stage 564A` TDMA & Split Telemetry | Read-only | Read-only | Audits `frame_len`, `duty_cycle`, `bc_dl_symbols`, `frame_pulse_offset`, `rx/tx freq` split & `ame_bbp_is_remote_SFN_synchronized` (`proprietary airMAX/LTU module`). |

## 2. Live Counterbalanced `A1 -> B1 -> A2 -> B2` Results
- **Cumulative Live LTU Windows**: **`192` windows** (`16` campaigns on `198.18.0.63`).
- **Live SSH Connected**: `True`.
- **Stock Mean RTT**: `0.235 ms`.
- **Champion `v14` Mean RTT**: `0.19 ms`.
- **Safety Gate**: `zero_dev_ame_touches = True`, `touched_241 = False`, `touched_242 = False`, `touched_20 = False`, `touched_250 = False`.
