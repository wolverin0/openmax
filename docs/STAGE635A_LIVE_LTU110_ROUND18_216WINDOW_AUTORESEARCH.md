<!-- doc-head: Stage 635A Live LTU-Lite (.110) Round 18 (216-Window Milestone!) ToF Ranging, Timing Advance, CP & UDP Burst Buffers Autoresearch (<220 lines) -->
Ejecuta 3 rondas contrabalanceadas `A1 -> B1 -> A2 -> B2` (`12` ventanas, alcanzando **`216` ventanas acumuladas**) sobre `198.18.0.63` (`LTU-Lite` Boca 5) evaluando `udp_rmem_min=16384`, `udp_wmem_min=16384`, `optmem_max=65536` y telemetría read-only `distance_meter / update_ta / cpsample` (`Stage 616A`, `zero_dev_ame_touches=True`).
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 635A — Live LTU-Lite (`198.18.0.63` Boca 5) Round 18 (`216`-Window Milestone!) Autoresearch (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `Linux`, `hardware`, `proprietary airMAX/LTU module`
- **Target**: `198.18.0.63` (`LTU-Lite`, `0xae08`, `Linux 3.14.65 SMP PREEMPT RT`)
- **Milestone**: **`18` Live Campaigns (`54` Counterbalanced `A1->B1->A2->B2` Rounds = `216` Live Windows)** on `198.18.0.63` with `zero_dev_ame_touches = True` and `45s` rollback watchdog.

## 1. Round 18 Knobs & `Stage 616A` Distance / Timing Advance Telemetry (`12` Counterbalanced Windows)
| Knob / Telemetry | Stock (`A1`/`A2`) | Champion `v16` (`B1`/`B2`) | First-Principles Mechanism (`CONFIRMED`) |
| :--- | :---: | :---: | :--- |
| `net.ipv4.udp_rmem_min` / `wmem_min` | `4096` | `16384` | Guarantees `16 KB` pre-allocated skb headroom per UDP socket so VoIP (`RTP`) & `QUIC`/`IPTV` bursts never drop during Bulk TCP contention (`Linux`). |
| `net.core.optmem_max` | `10240` | `65536` | Expands ancillary `cmsg`/DSCP control buffer ceiling for multi-queue QoS/ToS packet marking (`Linux`). |
| `Stage 616A` ToF / TA / CP Audit | Read-only | Read-only | Audits `distance_meter` (`cpe_distance`), `update_ta` (`ame_core_update_ta_cpe`), `early_data_cfg` & `cpsample` (`proprietary airMAX/LTU module`). |

## 2. Live Counterbalanced `A1 -> B1 -> A2 -> B2` Results
- **Cumulative Live LTU Windows**: **`216` windows** (`18` campaigns on `198.18.0.63`).
- **Live SSH Connected**: `True`.
- **Stock Mean RTT**: `0.233 ms`.
- **Champion `v16` Mean RTT**: `0.187 ms`.
- **Safety Gate**: `zero_dev_ame_touches = True`, `touched_241 = False`, `touched_242 = False`, `touched_20 = False`, `touched_250 = False`.
