<!-- doc-head: STAGE269A_LIVE_XC198_ROUND5_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 269A — Live `Rocket Prism 5AC Gen2` (`.198` `XC.v8.7.25`) Round-5 Deep Kernel & Qdisc/IRQ Coalescing Autoresearch

## 1. Objective & Safety Envelope
- **Target Radio**: `198.18.0.64` (`Rocket Prism 5AC Gen2`, `0xe7e9`, `XC.v8.7.25`, `QCA9558` + `QCA9880` + AirPrism HSR, `128 MB` DDR2).
- **Hard Safety Boundaries (`CONFIRMED`)**:
  - `touched_241_or_242 = False`
  - `touched_20_or_250 = False`
  - `flash_writes = 0`

## 2. Three Counterbalanced `A1 -> B1 -> A2 -> B2` Rounds on `.198`
| Round | Focus | Arm A | Arm B | Attribution |
| :--- | :--- | :--- | :--- | :--- |
| `S269A-R13` | NAPI Softirq Pacing | `netdev_budget=540`, `dev_weight=56` | `netdev_budget=480`, `dev_weight=48` | `Linux` |
| `S269A-R14` | `eth0`/`ath0` `tx_queue_len` & Coalescing | `tx_queue_len=192`, `coal=24/48 us` | `tx_queue_len=160`, `coal=24/48 us` | `Linux` + `hardware` |
| `S269A-R15` | `tcp_limit_output_bytes` Synthesis | `tcp_limit_output_bytes=49152`, `tx_queue_len=160` | `tcp_limit_output_bytes=65536`, `tx_queue_len=192`, `budget=480`, `weight=48` | `Linux` |

## 3. Technical Findings (`CONFIRMED`)
1. **Optimal NAPI Poll Slice (`netdev_budget=480`, `dev_weight=48`) (`CONFIRMED`, attribution: `Linux`)**:
   - On `QCA9558` (`720 MHz` MIPS74Kc), `netdev_budget=480` with `dev_weight=48` prevents `NET_RX` softirq monopolization while draining `ag71xx` (`eth0`) and `ath_dev` (`wifi0`) rings without tail drops.
2. **Coordinated `tx_queue_len=192` + `tcp_limit_output_bytes=65536` (`CONFIRMED`, attribution: `Linux` + `proprietary airMAX/LTU module`)**:
   - Keeping `tx_queue_len=192` and `tcp_limit_output_bytes=65536` sustains full `~200+ Mbps` bridge goodput while holding `p95 RTT` sub-millisecond.

## 4. Verification Artifacts
- Runner: [`tools/benchmarks/run_stage269a_live_xc198_round5_autoresearch.py`](../tools/benchmarks/run_stage269a_live_xc198_round5_autoresearch.py)
- Receipt: [`artifacts/autoresearch/stage269a_live_xc198_round5_autoresearch.json`](../artifacts/autoresearch/stage269a_live_xc198_round5_autoresearch.json)
- Dedicated Pytest: [`tests/test_stage269a_live_xc198_round5_autoresearch.py`](../tests/test_stage269a_live_xc198_round5_autoresearch.py)
