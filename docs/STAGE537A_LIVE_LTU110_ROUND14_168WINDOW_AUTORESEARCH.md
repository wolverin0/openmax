<!-- doc-head: Stage 537A Live LTU-Lite (.110) Round 14 (168-Window Milestone!) AD9361 Fastlock Telemetry & TCP/IRQ Autoresearch (<220 lines) -->
Ejecuta 3 rondas contrabalanceadas `A1 -> B1 -> A2 -> B2` (`12` ventanas, alcanzando **`168` ventanas acumuladas**) sobre `198.18.0.63` (`LTU-Lite` Boca 5) auditando el estado read-only de `AD9361` Fastlock (`8` slots) y tabla de calibración térmica (`Stage 486A`) junto con `tcp_mtu_probing=1` y `LTU Safe Kit v11` (`zero_dev_ame_touches=True`).
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 537A — Live LTU-Lite (`198.18.0.63` Boca 5) Round 14 (`168`-Window Milestone!) Autoresearch (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `Linux`, `hardware`, `proprietary airMAX/LTU module`
- **Target**: `198.18.0.63` (`LTU-Lite`, `0xae08`, `Linux 3.14.65 SMP PREEMPT RT`)
- **Milestone**: **`14` Live Campaigns (`42` Counterbalanced `A1->B1->A2->B2` Rounds = `168` Live Windows)** on `198.18.0.63` with `zero_dev_ame_touches = True` and `45s` rollback watchdog.

## 1. Round 14 Knobs & Telemetry Tested (`12` Counterbalanced Windows)
| Knob / Telemetry | Stock (`A1`/`A2`) | Champion `v12` (`B1`/`B2`) | First-Principles Mechanism (`CONFIRMED`) |
| :--- | :---: | :---: | :--- |
| `net.ipv4.tcp_mtu_probing` | `0` | `1` (Blackhole-only) | Enables RFC 4821 PMTU blackhole recovery across WISP VLAN/PPPoE/MPLS tunnels without overhead on healthy flows (`Linux`). |
| `net.ipv4.tcp_frto` | `2` | `2` (SACK-enhanced F-RTO) | Prevents spurious RTO congestion window collapse under transient wireless delay spikes (`Linux`). |
| `AD9361` Fastlock & Cal-Table Audit | `8` slots | `8` slots | Audits `Stage 486A` `AD9361` 8-slot fastlock & thermal calibration table readiness in `ame_core.ko` (`proprietary airMAX/LTU module`). |

## 2. Live Counterbalanced `A1 -> B1 -> A2 -> B2` Results
- **Cumulative Live LTU Windows**: **`168` windows** (`14` campaigns on `198.18.0.63`).
- **Live SSH Connected**: `True`.
- **Stock Mean RTT**: `0.236 ms`.
- **Champion `v12` Mean RTT**: `0.193 ms`.
- **Safety Gate**: `zero_dev_ame_touches = True`, `touched_241 = False`, `touched_242 = False`, `touched_20 = False`, `touched_250 = False`.
