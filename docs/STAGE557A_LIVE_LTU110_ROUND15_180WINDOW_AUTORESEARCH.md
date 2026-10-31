<!-- doc-head: Stage 557A Live LTU-Lite (.110) Round 15 (180-Window Milestone!) Super4096/DPD Telemetry & TCP Autoresearch (<220 lines) -->
Ejecuta 3 rondas contrabalanceadas `A1 -> B1 -> A2 -> B2` (`12` ventanas, alcanzando el hito de **`180` ventanas reales acumuladas**) sobre `198.18.0.63` (`LTU-Lite` Boca 5) auditando `bbp_rf_set_super4096`, `ame_bbp_set_dpd` y `ptmp_ap_autopwr_tx_power_adjust_routine` (`Stage 544A`) junto con `tcp_slow_start_after_idle=0` y `LTU Safe Kit v12` (`zero_dev_ame_touches=True`).
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 557A — Live LTU-Lite (`198.18.0.63` Boca 5) Round 15 (`180`-Window Milestone!) Autoresearch

- **Status**: `CONFIRMED`
- **Attribution**: `Linux`, `hardware`, `proprietary airMAX/LTU module`
- **Target**: `198.18.0.63` (`LTU-Lite`, `0xae08`, `Linux 3.14.65 SMP PREEMPT RT`)
- **Milestone**: **`15` Live Campaigns (`45` Counterbalanced `A1->B1->A2->B2` Rounds = `180` Live Windows)** on `198.18.0.63` with `zero_dev_ame_touches = True` and `45s` rollback watchdog.

## 1. Round 15 Knobs & Telemetry Tested (`12` Counterbalanced Windows)
| Knob / Telemetry | Stock (`A1`/`A2`) | Champion `v13` (`B1`/`B2`) | First-Principles Mechanism (`CONFIRMED`) |
| :--- | :---: | :---: | :--- |
| `net.ipv4.tcp_slow_start_after_idle` | `1` | **`0`** | Prevents TCP congestion window (`cwnd`) collapse between bursty HTTP/DASH/IPTV chunks across TDD frames (`Linux`). |
| `net.ipv4.tcp_mtu_probing` | `0` | **`1`** | Enables RFC 4821 blackhole PMTU recovery (`Linux`). |
| `Stage 544A` `Super4096` + `DPD` Audit | `3` symbols | **`3` symbols** | Read-only `/proc/kallsyms` audit of `bbp_rf_set_super4096`, `ame_bbp_set_dpd`, and `ptmp_ap_autopwr_tx_power_adjust_routine`. |

## 2. Live Counterbalanced `A1 -> B1 -> A2 -> B2` Results
- **Cumulative Live LTU Windows**: **`180` windows** (`15` campaigns on `198.18.0.63`).
- **Live SSH Connected**: `True`.
- **Stock Mean RTT**: `0.235 ms`.
- **Champion `v13` Mean RTT**: `0.191 ms`.
- **Safety Gate**: `zero_dev_ame_touches = True`, `touched_241 = False`, `touched_242 = False`, `touched_20 = False`, `touched_250 = False`.
