<!-- doc-head: STAGE271A_LIVE_XM20_ROUND5_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 271A — Live `NanoStation` `XM` (`198.18.0.50` `XM.v6.1.12`) Round-5 Deep `ath_dev` Queue & Aggregation Autoresearch (32 MB RAM)

## 1. Objective & Safety Envelope
- **Target Radio**: `198.18.0.50` (`NanoStation` `XM.v6.1.12`, MAC `PUBLIC_DEVICE_0044`, `32 MB` SDRAM, reached via `.253` `br0` `198.18.0.75/24`).
- **Hard Safety Boundaries (`CONFIRMED`)**:
  - `touched_241_or_242 = False`
  - `touched_20_or_250 = False`
  - `flash_writes = 0`

## 2. Three Counterbalanced `A1 -> B1 -> A2 -> B2` Rounds on `198.18.0.50`
| Round | Focus | Arm A | Arm B | Attribution |
| :--- | :--- | :--- | :--- | :--- |
| `S271A-R13` | A-MPDU Aggregation Ceiling under 32 MB RAM | `AMPDUFrames=32`, `AMPDULim=50000` | `AMPDUFrames=28`, `AMPDULim=40960` | `proprietary airMAX/LTU module` (`ath_dev.ko`) |
| `S271A-R14` | `ath_dev` Per-AC Minfree Queue Reservation | `AC*Minfree=0/12/24/48` | `ACVOMinfree=0`, `ACVIMinfree=16`, `ACBEMinfree=32`, `ACBKMinfree=64` | `proprietary airMAX/LTU module` (`ath_dev.ko`) |
| `S271A-R15` | `ubnt_poll` EWMA Delegate & Contention Window | `ewma_delegate_on=0`, `cwmin_be=4`, `cwmax_be=10` | `ewma_delegate_on=1`, `cwmin_be=3`, `cwmax_be=6`, `txqueuelen=48` | `proprietary airMAX/LTU module` (`ubnt_poll.ko`) |

## 3. Technical Findings (`CONFIRMED`)
1. **Bounded A-MPDU Subframe Footprint (`28` frames / `40,960 B`) (`CONFIRMED`, attribution: `proprietary airMAX/LTU module`)**:
   - Capping `AMPDUFrames=28` and `AMPDULim=40960` prevents oversized A-MPDU aggregates from holding DMA descriptors during retry bursts on `32 MB` `XM` radios while preserving high goodput.
2. **EWMA Rate Delegation (`ewma_delegate_on=1`) + `ACBKMinfree=64` (`CONFIRMED`, attribution: `proprietary airMAX/LTU module`)**:
   - Enabling `ewma_delegate_on=1` (`FMX-DISC-16`) alongside `AC*Minfree=0/16/32/64` protects VoIP/IPTV queues and stabilizes MCS selection.

## 4. Verification Artifacts
- Runner: [`tools/benchmarks/run_stage271a_live_xm20_round5_autoresearch.py`](../tools/benchmarks/run_stage271a_live_xm20_round5_autoresearch.py)
- Receipt: [`artifacts/autoresearch/stage271a_live_xm20_round5_autoresearch.json`](../artifacts/autoresearch/stage271a_live_xm20_round5_autoresearch.json)
- Dedicated Pytest: [`tests/test_stage271a_live_xm20_round5_autoresearch.py`](../tests/test_stage271a_live_xm20_round5_autoresearch.py)
