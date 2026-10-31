<!-- doc-head: STAGE335A_LIVE_XC198_ROUND7_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 335A — Live `Rocket Prism 5AC Gen2` (`.198` Boca 4) Round-7 Deep TCP ACK Filtering, NAPI Weight & SoftIRQ Budget Autoresearch

## 1. Objective & Safety Envelope
- **Target Radio**: `198.18.0.64` (`Rocket Prism 5AC Gen2`, Boca 4, `0xe7e9`, `XC.v8.7.25`, `128 MB` DDR2).
- **Hard Safety Boundaries (`CONFIRMED`)**:
  - `touched_241_or_242 = False`
  - `touched_250 = False`
  - `flash_writes = 0` (`45s` Non-DFS rollback watchdog enforced)

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Round-7 Windows
| Arm | `net.core.dev_weight` | `net.core.netdev_budget` | `tcp_thin_linear_timeouts` | `tx_queue_len` | `uph_wifi0` Draining | Attribution |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Arm A** (Baseline) | `64` | `300` | `0` | `256` | `swr_limit=4`, `daprot=2`, `mcast=5` | `Linux` + `proprietary airMAX/LTU module` |
| **Arm B** (Round-7 Candidate) | `96` | `600` | `1` | `192` | `swr_limit=3`, `daprot=2`, `mcast=5` | `Linux` + `proprietary airMAX/LTU module` |

## 3. Technical Mechanism (`CONFIRMED`)
1. **High-Throughput Burst Draining (`dev_weight=96`, `netdev_budget=600`) (`CONFIRMED`, attribution: `Linux`)**:
   - Under multi-stream burst saturation on `QCA9558`, raising `dev_weight=96` and `netdev_budget=600` allows a single `NET_RX` NAPI poll cycle to drain full A-MPDU completion batches from `QCA9880` (`wifi0`) without prematurely yielding to `ksoftirqd`.
2. **Thin-Stream Linear Retransmission (`tcp_thin_linear_timeouts=1`) (`CONFIRMED`, attribution: `Linux`)**:
   - Prevents exponential RTO backoff on sparse control/VoIP/SSH streams sharing the bridge with bulk TCP flows.

## 4. Verification Artifacts
- Runner: [`tools/benchmarks/run_stage335a_live_xc198_round7_autoresearch.py`](../tools/benchmarks/run_stage335a_live_xc198_round7_autoresearch.py)
- Receipt: [`artifacts/autoresearch/stage335a_live_xc198_round7_autoresearch.json`](../artifacts/autoresearch/stage335a_live_xc198_round7_autoresearch.json)
- Dedicated Pytest: [`tests/test_stage335a.py`](../tests/test_stage335a.py)
