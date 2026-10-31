<!-- doc-head: STAGE370A_MULTI_RADIO_V44_SUITE_GATE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 370A — Consolidated Multi-Radio Round 8 Campaign Suite Gate (`Stages 365A..370A`, Champion `v44.0`)

## 1. Objective & Verification Summary (`CONFIRMED`)
Audits and certifies the complete **6-Stage Ground-Up Live Multi-Radio Round 8 Autoresearch Campaign (`Stages 365A..370A`)**:
1. **`Stage 365A`**: Live `XC` `Rocket Prism 5AC Gen2` (`198.18.0.64` Boca 4) Round 8 Ground-Up AirPrism Active Filter GPIO & WAL Queue Drain Autoresearch (`athstats -ol` `wal_dbg_stats`, `tcp_limit_output_bytes=49152`, `rmem_default=131072`).
2. **`Stage 366A`**: Live `2XC` `Rocket 2AC Prism` (`198.18.0.65` Boca 6) Round 8 Ground-Up 2.4 GHz Asymmetric Chain-Imbalance & `athstats -ol` Verification (`daprot=2`, `ff_mcast_airtime_limit=4`, `swr_limit=3`, `chain_delta_db`).
3. **`Stage 367A`**: Live `XM` `NanoStation M5` (`198.18.0.50` / `.20` via `.253` bridge) Round 8 Ground-Up OpenWrt `23.05.5` `ath9k` Per-Chain RSSI & `Minstrel-HT` Retry-Chain Autoresearch (`[4,4,2,2]`, `aggr_limit_bytes=16384` under `32 MB` RAM).
4. **`Stage 368A`**: Cumulative 8-Round (`32-Window` per Radio = `96-Window` Multi-Radio) Statistical Scorecard & Wilcoxon / Cohen's $d$ Effect-Size Matrix.
5. **`Stage 369A`**: Cross-Fleet Champion `v44.0` Package Generator (`XC`, `2XC`, `XM`, `WA`, `XW`, `LTU`).
6. **`Stage 370A`**: Consolidated Suite Gate (`verify_stage370a_multi_radio_v44_suite_gate.py`, `test_stage365a_to_370a_multi_radio_v44.py`) + repo-wide 5-Pillar Research Gate check.

## 2. Gate Audit Table
| Stage | Script | Receipt | Doc (`< 220` lines, 1 `doc-head`) | Pytest | 5-Pillar Gate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `STAGE-365A` | `run_stage365a_live_xc198_round8_autoresearch.py` | `stage365a_live_xc198_round8_autoresearch.json` | `STAGE365A_LIVE_XC198_ROUND8_AUTORESEARCH.md` | `test_stage365a.py` | `PASS` |
| `STAGE-366A` | `run_stage366a_live_2xc253_round8_autoresearch.py` | `stage366a_live_2xc253_round8_autoresearch.json` | `STAGE366A_LIVE_2XC253_ROUND8_AUTORESEARCH.md` | `test_stage366a.py` | `PASS` |
| `STAGE-367A` | `run_stage367a_live_xm20_round8_autoresearch.py` | `stage367a_live_xm20_round8_autoresearch.json` | `STAGE367A_LIVE_XM20_ROUND8_AUTORESEARCH.md` | `test_stage367a.py` | `PASS` |
| `STAGE-368A` | `build_stage368a_multi_radio_8round_scorecard.py` | `stage368a_multi_radio_8round_scorecard.json` | `STAGE368A_MULTI_RADIO_8ROUND_SCORECARD.md` | `test_stage368a.py` | `PASS` |
| `STAGE-369A` | `build_stage369a_cross_fleet_champion_v44.py` | `stage369a_cross_fleet_champion_v44.json` | `STAGE369A_CROSS_FLEET_CHAMPION_V44.md` | `test_stage369a.py` | `PASS` |
| `STAGE-370A` | `verify_stage370a_multi_radio_v44_suite_gate.py` | `stage370a_multi_radio_v44_suite_gate_receipt.json` | `STAGE370A_MULTI_RADIO_V44_SUITE_GATE.md` | `test_stage365a_to_370a_multi_radio_v44.py` | `PASS` |

## 3. Verification Artifacts
- Script: [`tools/verify/verify_stage370a_multi_radio_v44_suite_gate.py`](../tools/verify/verify_stage370a_multi_radio_v44_suite_gate.py)
- Receipt: [`artifacts/autoresearch/stage370a_multi_radio_v44_suite_gate_receipt.json`](../artifacts/autoresearch/stage370a_multi_radio_v44_suite_gate_receipt.json)
- Consolidated Test Suite: [`tests/test_stage365a_to_370a_multi_radio_v44.py`](../tests/test_stage365a_to_370a_multi_radio_v44.py)
