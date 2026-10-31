<!-- doc-head: STAGE294A_LIVE_2XC253_ROUND6_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 294A — Live `Rocket 2AC Prism` (`.253` `2XC.v8.7.11` 2.4 GHz) Round-6 Deep Socket Buffer & Interrupt Coalescing Autoresearch

## 1. Objective & Safety Envelope
- **Target Radio**: `198.18.0.65` (`Rocket 2AC Prism`, `0xe2f2`, `2XC.v8.7.11`, `128 MB` DDR2).
- **Hard Safety Boundaries (`CONFIRMED`)**:
  - `touched_241_or_242 = False`
  - `touched_20_or_250 = False`
  - `flash_writes = 0`

## 2. Three Counterbalanced `A1 -> B1 -> A2 -> B2` Rounds on `.253`
| Round | Focus | Arm A | Arm B | Attribution |
| :--- | :--- | :--- | :--- | :--- |
| `S294A-R16` | Socket Buffer Ceilings (`rmem_max`/`wmem_max`, `tcp_rmem`/`wmem`) | `131072` (`128 KB`) | `262144` (`256 KB`), `tcp_rmem='4096 65536 262144'`, `tcp_wmem='4096 32768 262144'` | `Linux` |
| `S294A-R17` | `eth0` Interrupt Coalescing (`ag71xx`) | `rx-usecs=16`, `tx-usecs=32` | `rx-usecs=24`, `tx-usecs=48` | `Linux` + `hardware` |
| `S294A-R18` | TSQ & TSO Window Divisor Synthesis | `tcp_limit_output_bytes=131072`, `tso_div=3` | `tcp_limit_output_bytes=65536`, `tso_div=8`, `coal=24/48 us` | `Linux` |

## 3. Technical Findings (`CONFIRMED`)
1. **Balanced Socket Buffers (`256 KB` max) + Tight TSQ (`64 KB`) on `128 MB` `2XC` (`CONFIRMED`, attribution: `Linux`)**:
   - Allowing `256 KB` receive/send window scaling for high-BDP TDMA links while clamping per-socket unsent queue depth via `tcp_limit_output_bytes=65536` and `tcp_tso_win_divisor=8` maximizes goodput without inducing local bufferbloat.

## 4. Verification Artifacts
- Runner: [`tools/benchmarks/run_stage294a_live_2xc253_round6_autoresearch.py`](../tools/benchmarks/run_stage294a_live_2xc253_round6_autoresearch.py)
- Receipt: [`artifacts/autoresearch/stage294a_live_2xc253_round6_autoresearch.json`](../artifacts/autoresearch/stage294a_live_2xc253_round6_autoresearch.json)
- Dedicated Pytest: [`tests/test_stage294a_live_2xc253_round6_autoresearch.py`](../tests/test_stage294a_live_2xc253_round6_autoresearch.py)
