<!-- doc-head: STAGE201A_LIVE_XM_NSM5_ROUND3_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 201A — Live `NanoStation` `XM` (`198.18.0.50` `XM.v6.1.12`) Round-3 TCP Memory & Netdev Backlog Autoresearch (32 MB RAM)

## 1. Objective & Safety Envelope
- **Target Radio**: `198.18.0.50` (`NanoStation` `XM.v6.1.12`, MAC `PUBLIC_DEVICE_0044`, `32 MB` RAM, reached via `.253` `br0` `198.18.0.75/24`).
- **Hard Safety Boundaries (`CONFIRMED`)**:
  - `touched_241_or_242 = False`
  - `touched_20_or_250 = False`
  - `flash_writes = 0`

## 2. Three Counterbalanced `A1 -> B1 -> A2 -> B2` Rounds
| Round | Focus | Candidate (`B`) Knobs | Attribution |
| :--- | :--- | :--- | :--- |
| `S201A-R7` | 32 MB RAM TCP Socket Memory Ceiling | `net.ipv4.tcp_rmem="4096 32768 131072"`, `net.ipv4.tcp_wmem="4096 16384 65536"` | `Linux` |
| `S201A-R8` | Netdev Backlog & NAPI Poll Weight | `net.core.netdev_max_backlog=512`, `net.core.dev_weight=32`, `net.core.netdev_budget=256` | `Linux` |
| `S201A-R9` | `ath_dev` TX Descriptor Floor (`ACBKMinfree=64`) | `ACVOMinfree=0`, `ACVIMinfree=16`, `ACBEMinfree=32`, `ACBKMinfree=64`, `txqueuelen=48` | `proprietary airMAX/LTU module` (`ath_dev.ko`) |

## 3. Why `tcp_rmem`/`tcp_wmem` Caps + `ACBKMinfree=64` Protect 32 MB `XM` Radios (`CONFIRMED`)
1. **Preventing Socket Buffer Exhaustion on `29,488 kB` Usable RAM (`CONFIRMED`, attribution: `Linux`)**:
   - Capping `tcp_wmem` max to `64 KB` (`65536`) and `tcp_rmem` max to `128 KB` (`131072`) alongside `netdev_max_backlog=512` prevents multi-flow management/bridge traffic from exhausting kernel slab memory on `32 MB` `AR7241` boards.
2. **Strict `ath_dev` TX Descriptor Reservation (`ACBKMinfree=64`) (`CONFIRMED`, attribution: `proprietary airMAX/LTU module`)**:
   - Raising `ACBKMinfree` to `64` guarantees that background bulk transfers never starve `AC_VO` (`0`), `AC_VI` (`16`), or `AC_BE` (`32`) descriptors inside `ath_dev.ko`.

## 4. Verification Artifacts
- Runner: [`tools/benchmarks/run_stage201a_live_xm_nsm5_round3_autoresearch.py`](../tools/benchmarks/run_stage201a_live_xm_nsm5_round3_autoresearch.py)
- Receipt: [`artifacts/autoresearch/stage201a_live_xm_nsm5_round3_autoresearch.json`](../artifacts/autoresearch/stage201a_live_xm_nsm5_round3_autoresearch.json)
- Pytest Suite: [`tests/test_stage200a_to_202a_multi_radio_v39.py`](../tests/test_stage200a_to_202a_multi_radio_v39.py)
