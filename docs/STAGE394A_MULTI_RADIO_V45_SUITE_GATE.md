<!-- doc-head: STAGE394A_MULTI_RADIO_V45_SUITE_GATE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 394A — Consolidated Multi-Radio Round 9 Campaign Suite Gate (`Stages 389A..394A`, Champion `v45.0`)

## 1. Objective & Verification Summary (`CONFIRMED`)
Audits and certifies the complete **6-Stage Ground-Up Live Multi-Radio Round 9 Autoresearch Campaign (`Stages 389A..394A`)**:
1. **`Stage 389A`**: Live `XC` `Rocket Prism 5AC Gen2` (`198.18.0.64` Boca 4) Round 9 Ground-Up Per-AC WMM Queue Weights & `ubnt_poll` `/proc/sys/dev/uph_wifi0` Deep Audit & Autoresearch (`AC*Minfree=64/32/16/0`, `set_multiq=3`, `daprot=2`, `ff_mcast_airtime_limit=5`, `swr_limit=3`).
2. **`Stage 390A`**: Live `2XC` `Rocket 2AC Prism` (`198.18.0.65` Boca 6) Round 9 Ground-Up 2.4 GHz `/proc/sys/dev/uph_wifi0` & AirPrism 2.4 GHz Coexistence Autoresearch (`daprot=2`, `ff_mcast_airtime_limit=4`, `swr_limit=3`).
3. **`Stage 391A`**: Live `XM` `NanoStation M5` (`198.18.0.50` / `.20` via `.253` bridge) Round 9 Ground-Up OpenWrt `ath9k` Queue Depth (`64`), `AQL` (`2000/4000 us`), `BQL` (`24576 B`) & SoftIRQ Coalescing (`4000 us`) Autoresearch.
4. **`Stage 392A`**: Cumulative 9-Round (`36-Window` per Radio = `108-Window` Multi-Radio) Statistical Scorecard & Wilcoxon / Cohen's $d$ Effect-Size Matrix.
5. **`Stage 393A`**: Cross-Fleet Champion `v45.0` Package Generator (`XC`, `2XC`, `XM`, `WA`, `XW`, `LTU`).
6. **`Stage 394A`**: Consolidated Suite Gate (`verify_stage394a_multi_radio_v45_suite_gate.py`, `test_stage389a_to_394a_multi_radio_v45.py`) + repo-wide 5-Pillar Research Gate check.

## 2. Gate Audit Table
| Stage | Script | Receipt | Doc (`< 220` lines, 1 `doc-head`) | Pytest | 5-Pillar Gate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `STAGE-389A` | `run_stage389a_live_xc198_round9_autoresearch.py` | `stage389a_live_xc198_round9_autoresearch.json` | `STAGE389A_LIVE_XC198_ROUND9_AUTORESEARCH.md` | `test_stage389a.py` | `PASS` |
| `STAGE-390A` | `run_stage390a_live_2xc253_round9_autoresearch.py` | `stage390a_live_2xc253_round9_autoresearch.json` | `STAGE390A_LIVE_2XC253_ROUND9_AUTORESEARCH.md` | `test_stage390a.py` | `PASS` |
| `STAGE-391A` | `run_stage391a_live_xm20_round9_autoresearch.py` | `stage391a_live_xm20_round9_autoresearch.json` | `STAGE391A_LIVE_XM20_ROUND9_AUTORESEARCH.md` | `test_stage391a.py` | `PASS` |
| `STAGE-392A` | `build_stage392a_multi_radio_9round_scorecard.py` | `stage392a_multi_radio_9round_scorecard.json` | `STAGE392A_MULTI_RADIO_9ROUND_SCORECARD.md` | `test_stage392a.py` | `PASS` |
| `STAGE-393A` | `build_stage393a_cross_fleet_champion_v45.py` | `stage393a_cross_fleet_champion_v45.json` | `STAGE393A_CROSS_FLEET_CHAMPION_V45.md` | `test_stage393a.py` | `PASS` |
| `STAGE-394A` | `verify_stage394a_multi_radio_v45_suite_gate.py` | `stage394a_multi_radio_v45_suite_gate_receipt.json` | `STAGE394A_MULTI_RADIO_V45_SUITE_GATE.md` | `test_stage389a_to_394a_multi_radio_v45.py` | `PASS` |

## 3. Verification Artifacts
- Script: [`tools/verify/verify_stage394a_multi_radio_v45_suite_gate.py`](../tools/verify/verify_stage394a_multi_radio_v45_suite_gate.py)
- Receipt: [`artifacts/autoresearch/stage394a_multi_radio_v45_suite_gate_receipt.json`](../artifacts/autoresearch/stage394a_multi_radio_v45_suite_gate_receipt.json)
- Consolidated Test Suite: [`tests/test_stage389a_to_394a_multi_radio_v45.py`](../tests/test_stage389a_to_394a_multi_radio_v45.py)
