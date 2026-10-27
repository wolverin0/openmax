<!-- doc-head: STAGE436A_MULTI_RADIO_V46_SUITE_GATE.md preserved document content -->
<!-- /doc-head -->


# Stage 436A: Consolidated Multi-Radio Round 10 (`120-Window` Milestone) Suite Gate (`Stages 431A..436A`, Champion `v46.0`)

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `external controller` (verification harness) + `proprietary airMAX/LTU module` + `Linux`
- **Safety Gate**: `.241`, `.242`, `.250` untouched (`CONFIRMED`)
- **Artifact**: [`stage436a_multi_radio_v46_suite_gate_receipt.json`](../artifacts/autoresearch/stage436a_multi_radio_v46_suite_gate_receipt.json)
- **Verifier**: [`verify_stage436a_multi_radio_v46_suite_gate.py`](../tools/verify/verify_stage436a_multi_radio_v46_suite_gate.py)
- **Test Suite**: [`test_stage431a_to_436a_multi_radio_v46.py`](../tests/test_stage431a_to_436a_multi_radio_v46.py)

## 1. Audited Stages (`Stages 431A..436A`)

| Stage | Scope | Receipt | Doc (`<220` lines) | 5-Pillar Gate |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 431A** | Live `XC` (`.198`) R10 Active-AirPrism GPIO `13..16` + WMI Retry | `stage431a_live_xc198_round10_120window_autoresearch.json` | `STAGE431A_LIVE_XC198_ROUND10_120WINDOW_AUTORESEARCH.md` | `PASS` |
| **Stage 432A** | Live `2XC` (`.253`) R10 2.4 GHz Interference Immunity + Dynamic RTS/CTS | `stage432a_live_2xc253_round10_120window_autoresearch.json` | `STAGE432A_LIVE_2XC253_ROUND10_120WINDOW_AUTORESEARCH.md` | `PASS` |
| **Stage 433A** | Live `XM` (`.20`) R10 Asymmetric LGI Rescue + `120-Window` Milestone | `stage433a_live_xm20_round10_120window_autoresearch.json` | `STAGE433A_LIVE_XM20_ROUND10_120WINDOW_AUTORESEARCH.md` | `PASS` |
| **Stage 434A** | 10-Round (`120-Window`) Multi-Radio Statistical Scorecard | `stage434a_multi_radio_10round_120window_scorecard.json` | `STAGE434A_MULTI_RADIO_10ROUND_120WINDOW_SCORECARD.md` | `PASS` |
| **Stage 435A** | Cross-Fleet Champion `v46.0` Package Synthesis | `stage435a_cross_fleet_champion_v46.json` | `STAGE435A_CROSS_FLEET_CHAMPION_V46.md` | `PASS` |
| **Stage 436A** | End-to-End Suite Gate & Repo-Wide 5-Pillar Check | `stage436a_multi_radio_v46_suite_gate_receipt.json` | `STAGE436A_MULTI_RADIO_V46_SUITE_GATE.md` | `PASS` |
