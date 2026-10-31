<!-- doc-head: STAGE340A_MULTI_RADIO_V43_SUITE_GATE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 340A — Consolidated Multi-Radio Round 7 Campaign Suite Gate (`Stages 335A..340A`, Champion `v43.0`)

## 1. Objective & Verification Summary (`CONFIRMED`)
Audits and certifies the complete **6-Stage Live Multi-Radio Round 7 Autoresearch Campaign (`Stages 335A..340A`)**:
1. **`Stage 335A`**: Live `XC` `Rocket Prism 5AC Gen2` (`198.18.0.64` Boca 4) Round 7 Deep TCP ACK Filtering, NAPI Weight (`dev_weight=96`), & SoftIRQ Budget (`netdev_budget=600`).
2. **`Stage 336A`**: Live `2XC` `Rocket 2AC Prism` (`198.18.0.65` Boca 6) Round 7 2.4 GHz High-Noise Floor & Co-Channel Contention Autoresearch (`daprot=2`, `ff_mcast_airtime_limit=4`, ARP/multicast pinning).
3. **`Stage 337A`**: Live `XM` `NanoStation M5` (`198.18.0.50` via `.253` bridge) Round 7 `ath9k`/`ath_dev` ANI (`intmit=1`), `eth0` BQL (`limit_max=24576`), & `fq_codel` (`300`/`384`) Deep Tuning under `32 MB` RAM.
4. **`Stage 338A`**: Cumulative 7-Round (`28-Window` per Radio = `84-Window` Multi-Radio) Statistical Scorecard & Wilcoxon / Cohen's $d$ Effect-Size Matrix.
5. **`Stage 339A`**: Cross-Fleet Champion `v43.0` Package Generator (`XC`, `2XC`, `XM`, `WA`, `XW`, `LTU`).
6. **`Stage 340A`**: Consolidated Suite Gate (`verify_stage340a_multi_radio_v43_suite_gate.py`, `test_stage335a_to_340a_multi_radio_v43.py`) + repo-wide 5-Pillar Research Gate check.

## 2. Gate Audit Table
| Stage | Script | Receipt | Doc (`< 220` lines, 1 `doc-head`) | Pytest | 5-Pillar Gate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `STAGE-335A` | `run_stage335a_live_xc198_round7_autoresearch.py` | `stage335a_live_xc198_round7_autoresearch.json` | `STAGE335A_LIVE_XC198_ROUND7_AUTORESEARCH.md` | `test_stage335a.py` | `PASS` |
| `STAGE-336A` | `run_stage336a_live_2xc253_round7_autoresearch.py` | `stage336a_live_2xc253_round7_autoresearch.json` | `STAGE336A_LIVE_2XC253_ROUND7_AUTORESEARCH.md` | `test_stage336a.py` | `PASS` |
| `STAGE-337A` | `run_stage337a_live_xm20_round7_autoresearch.py` | `stage337a_live_xm20_round7_autoresearch.json` | `STAGE337A_LIVE_XM20_ROUND7_AUTORESEARCH.md` | `test_stage337a.py` | `PASS` |
| `STAGE-338A` | `build_stage338a_multi_radio_7round_scorecard.py` | `stage338a_multi_radio_7round_scorecard.json` | `STAGE338A_MULTI_RADIO_7ROUND_SCORECARD.md` | `test_stage338a.py` | `PASS` |
| `STAGE-339A` | `build_stage339a_cross_fleet_champion_v43.py` | `stage339a_cross_fleet_champion_v43.json` | `STAGE339A_CROSS_FLEET_CHAMPION_V43.md` | `test_stage339a.py` | `PASS` |
| `STAGE-340A` | `verify_stage340a_multi_radio_v43_suite_gate.py` | `stage340a_multi_radio_v43_suite_gate_receipt.json` | `STAGE340A_MULTI_RADIO_V43_SUITE_GATE.md` | `test_stage335a_to_340a_multi_radio_v43.py` | `PASS` |

## 3. Verification Artifacts
- Script: [`tools/verify/verify_stage340a_multi_radio_v43_suite_gate.py`](../tools/verify/verify_stage340a_multi_radio_v43_suite_gate.py)
- Receipt: [`artifacts/autoresearch/stage340a_multi_radio_v43_suite_gate_receipt.json`](../artifacts/autoresearch/stage340a_multi_radio_v43_suite_gate_receipt.json)
- Consolidated Test Suite: [`tests/test_stage335a_to_340a_multi_radio_v43.py`](../tests/test_stage335a_to_340a_multi_radio_v43.py)
