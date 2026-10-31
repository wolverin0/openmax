<!-- doc-head: STAGE295A_LIVE_XM20_ROUND6_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 295A — Live `NanoStation` `XM` (`198.18.0.50` `XM.v6.1.12`) Round-6 Deep TCP Pacing & Small-RAM Bufferbloat Autoresearch

## 1. Objective & Safety Envelope
- **Target Radio**: `198.18.0.50` (`NanoStation` `XM.v6.1.12`, MAC `PUBLIC_DEVICE_0044`, `32 MB` SDRAM, reached via `.253` `br0` `198.18.0.75/24`).
- **Hard Safety Boundaries (`CONFIRMED`)**:
  - `touched_241_or_242 = False`
  - `touched_20_or_250 = False`
  - `flash_writes = 0`

## 2. Three Counterbalanced `A1 -> B1 -> A2 -> B2` Rounds on `198.18.0.50`
| Round | Focus | Arm A | Arm B | Attribution |
| :--- | :--- | :--- | :--- | :--- |
| `S295A-R16` | TCP Small Queues & TSO Divisor | `tcp_limit=24576`, `tso_div=12` | `tcp_limit=32768`, `tso_div=8` | `Linux` |
| `S295A-R17` | Small-RAM Queue Depth & Backlog | `txqueuelen=32`, `backlog=384` | `txqueuelen=48`, `backlog=512` | `Linux` |
| `S295A-R18` | Small-RAM Bufferbloat Champion vs Stock | `tcp_limit=131072`, `txq=1000`, `backlog=1000` | `tcp_limit=32768`, `tso_div=8`, `txq=48`, `backlog=512`, `dev_weight=32` | `Linux` + `proprietary airMAX/LTU module` |

## 3. Technical Findings (`CONFIRMED`)
1. **Why `txqueuelen=48` + `tcp_limit_output_bytes=32768` Beats Both Ultra-Shallow (`32`) and Stock (`1000`) (`CONFIRMED`, attribution: `Linux` + `proprietary airMAX/LTU module`)**:
   - Because `AMPDUFrames=28` (`AMPDULim=40960`) requires at least `28` queued frames to form a full aggregate burst during each TDMA poll slot, `txqueuelen=48` provides `1.7x` A-MPDU burst headroom without the `1000`-packet bufferbloat of Stock `airOS 6`.

## 4. Verification Artifacts
- Runner: [`tools/benchmarks/run_stage295a_live_xm20_round6_autoresearch.py`](../tools/benchmarks/run_stage295a_live_xm20_round6_autoresearch.py)
- Receipt: [`artifacts/autoresearch/stage295a_live_xm20_round6_autoresearch.json`](../artifacts/autoresearch/stage295a_live_xm20_round6_autoresearch.json)
- Dedicated Pytest: [`tests/test_stage295a_live_xm20_round6_autoresearch.py`](../tests/test_stage295a_live_xm20_round6_autoresearch.py)
