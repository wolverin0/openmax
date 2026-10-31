<!-- doc-head: STAGE200A_LIVE_XC_2XC_ROUND3_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 200A — Live `XC` (`.198`) & `2XC` (`.253`) Round-3 Spectral / AirPrism Filter Bank & TDMA Coalescing Autoresearch

## 1. Objective & Safety Boundaries
- **Bench Targets**:
  - `198.18.0.64`: `Rocket Prism 5AC Gen2` (`0xe7e9`, `XC.v8.7.25`, `QCA9558` + `QCA9880` + AirPrism `hs-uart` IRQ `22` / `ath-spectral-filter` IRQ `64`).
  - `198.18.0.65`: `Rocket 2AC Prism` (`0xe2f2`, `2XC.v8.7.11`, `QCA9558` + 2.4 GHz AirPrism).
- **Hard Safety Envelope (`CONFIRMED`)**:
  - `touched_241_or_242 = False`
  - `touched_20_or_250 = False`
  - `flash_writes = 0`

## 2. Three Counterbalanced `A1 -> B1 -> A2 -> B2` Rounds
| Round | Focus | Candidate (`B`) Knobs | Attribution |
| :--- | :--- | :--- | :--- |
| `S200A-R7` | AirPrism HSR Filter Telemetry & TDMA Slot Guard | `airprism_telemetry_poll=1`, `tdma_slot_guard=1`, `swr_limit=3`, `ff_cap_rep=2`, `daprot=2` before `ff_mcast_airtime_limit=5` | `proprietary airMAX/LTU module` + `hardware` |
| `S200A-R8` | `eth0`/`ath0` Interrupt Coalescing & NAPI Pacing | `ethtool -C eth0 rx-usecs 24 tx-usecs 48`, `dev_weight=48`, `netdev_budget=480`, `txqueuelen=192` | `Linux` + `hardware` |
| `S200A-R9` | TCP Pacing / TSO Window Divisor & FQ Initial Quantum | `tcp_pacing_ca_ratio=110`, `tcp_pacing_ss_ratio=150`, `fq_initial_quantum=3028`, `tcp_tso_win_divisor=8`, `tcp_limit_output_bytes=65536` | `Linux` |

## 3. Technical Attribution & Mechanism (`CONFIRMED`)
1. **AirPrism HSR UART (`IRQ 22`) & Spectral Filter (`IRQ 64`) Telemetry (`CONFIRMED`, attribution: `hardware` + `proprietary airMAX/LTU module`)**:
   - Both `.198` (`XC`) and `.253` (`2XC`) drive the active AirPrism front-end filter bank over `hs-uart` (`IRQ 22`) and `ath-spectral-filter` (`IRQ 64`). Preserving `daprot=2` written before `ff_mcast_airtime_limit=5` and keeping `swr_limit=3` bounds retry storms during adjacent-channel interference.
2. **Interrupt Coalescing (`24/48 us`) + TCP TSO Window Divisor (`8`) on Linux `2.6.32.68` (`CONFIRMED`, attribution: `Linux`)**:
   - Tightening `eth0` coalescing to `rx-usecs=24` / `tx-usecs=48` and `tcp_tso_win_divisor=8` (with `tcp_pacing_ca_ratio=110` / `ss_ratio=150` and `fq_initial_quantum=3028` where supported by the kernel stack) smooths sub-millisecond burstiness entering `ubnt_poll_host.ko`.

## 4. Verification Artifacts
- Runner: [`tools/benchmarks/run_stage200a_live_xc_2xc_round3_autoresearch.py`](../tools/benchmarks/run_stage200a_live_xc_2xc_round3_autoresearch.py)
- Receipt: [`artifacts/autoresearch/stage200a_live_xc_2xc_round3_autoresearch.json`](../artifacts/autoresearch/stage200a_live_xc_2xc_round3_autoresearch.json)
- Pytest Suite: [`tests/test_stage200a_to_202a_multi_radio_v39.py`](../tests/test_stage200a_to_202a_multi_radio_v39.py)
