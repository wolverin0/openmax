<!-- doc-head: STAGE270A_LIVE_2XC253_ROUND5_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 270A — Live `Rocket 2AC Prism` (`.253` `2XC.v8.7.11` 2.4 GHz) Round-5 Deep Noise-Floor & 2.4 GHz Coexistence Autoresearch

## 1. Objective & Safety Envelope
- **Target Radio**: `198.18.0.65` (`Rocket 2AC Prism`, `0xe2f2`, `2XC.v8.7.11`, `QCA9558` + 2.4 GHz AirPrism HSR, `128 MB` DDR2).
- **Hard Safety Boundaries (`CONFIRMED`)**:
  - `touched_241_or_242 = False`
  - `touched_20_or_250 = False`
  - `flash_writes = 0`

## 2. Three Counterbalanced `A1 -> B1 -> A2 -> B2` Rounds on `.253`
| Round | Focus | Arm A | Arm B | Attribution |
| :--- | :--- | :--- | :--- | :--- |
| `S270A-R13` | 2.4 GHz AirPrism HSR Filter Telemetry & Retries | `swr_limit=4`, `ff_cap_rep=1` | `swr_limit=3`, `ff_cap_rep=2` + `hs-uart` IRQ `22` / `ath-spectral-filter` IRQ `64` | `proprietary airMAX/LTU module` + `hardware` |
| `S270A-R14` | 2.4 GHz Coexistence & `uph_wifi0` 64B Vector | `daprot=1`, `mcast=10`, `cms/voip_bias=0` | `daprot=2` before `ff_mcast_airtime_limit=5`, `cms_bias=6`, `voip_bias=6` | `proprietary airMAX/LTU module` |
| `S270A-R15` | Memory Reserve & Backlog Synthesis | `min_free_kbytes=2048`, `backlog=512` | `min_free_kbytes=4096`, `backlog=1024`, `budget=480`, `weight=48` | `Linux` |

## 3. Technical Findings (`CONFIRMED`)
1. **2.4 GHz Coexistence under ISM Noise (`swr_limit=3`, `ff_cap_rep=2`, `daprot=2`) (`CONFIRMED`, attribution: `proprietary airMAX/LTU module` + `hardware`)**:
   - In 2.4 GHz ISM environments with non-airMAX Wi-Fi bursts, `daprot=2` (dynamic airMAX protection written before `ff_mcast_airtime_limit=5` per `FMX-DISC-11`) paired with `swr_limit=3` and `ff_cap_rep=2` bounds sliding-window retry stalls while the active 2.4 GHz AirPrism filter (`hs-uart` IRQ `22` / `ath-spectral-filter` IRQ `64`) attenuates adjacent-channel energy.

## 4. Verification Artifacts
- Runner: [`tools/benchmarks/run_stage270a_live_2xc253_round5_autoresearch.py`](../tools/benchmarks/run_stage270a_live_2xc253_round5_autoresearch.py)
- Receipt: [`artifacts/autoresearch/stage270a_live_2xc253_round5_autoresearch.json`](../artifacts/autoresearch/stage270a_live_2xc253_round5_autoresearch.json)
- Dedicated Pytest: [`tests/test_stage270a_live_2xc253_round5_autoresearch.py`](../tests/test_stage270a_live_2xc253_round5_autoresearch.py)
