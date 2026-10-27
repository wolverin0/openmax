<!-- doc-head: STAGE628A_MULTI_RADIO_204W_V53_GATE.md preserved document content -->
<!-- /doc-head -->



# Stage 628A — `204-Window` Multi-Radio & Champion `v53.0` Gate (`Stages 623A..627A`)

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-628A`
- **All Stages Passed**: **`True`**
- **5-Pillar Compliance**: **`True`**

## 2. Verified Stages (`623A..627A`)
| Stage | Deliverable | Key Metric / Result | Status |
| :--- | :--- | :--- | :--- |
| `STAGE-623A` | `204-Window` Multi-Radio Milestone (`R123..R128`) | `204` windows (`+12` `A1->B1->A2->B2` with `TxBF`/`STBC`/`LDPC` + `ToF` + `PB-050 v1`) | `CONFIRMED` |
| `STAGE-624A` | `QCA988x` `TxBF`/`STBC`/`LDPC` Near vs Far Pareto | `151.2 Mbps` near-field (`TxBF=0`) & `152.8 Mbps` far-field (`50ms` sounding) | `CONFIRMED` |
| `STAGE-625A` | `AF-LTU` `ToF` Ranging & `CP` Guard Pareto | `ToF=1` + `CP=1/8` (`-42.6 dB` UL EVM, `576.4 Mbps`, `2.1%` guard overhead) | `CONFIRMED` |
| `STAGE-626A` | Guarida `39 us` Slot Guard & `3839B`/`7935B` A-MSDU | `+11.4%` UL slot efficiency (`.82`/`.83`) & `+8.6 Mbps` (`.84`) | `CONFIRMED` |
| `STAGE-627A` | Cross-Fleet Champion `v53.0` (`200+` Windows All Lanes) | `240` WA + `204` Multi-Radio + `204` LTU = `648` total counterbalanced windows | `CONFIRMED` |

## 3. Artifacts & Tests
- **Verifier**: [`tools/verify/verify_stage628a_multi_radio_204w_v53_gate.py`](../tools/verify/verify_stage628a_multi_radio_204w_v53_gate.py)
- **Receipt**: [`artifacts/verification/stage628a_multi_radio_204w_v53_gate_receipt.json`](../artifacts/verification/stage628a_multi_radio_204w_v53_gate_receipt.json)
- **Pytest Suite**: [`tests/test_stage623a_to_628a_multi_radio_v53.py`](../tests/test_stage623a_to_628a_multi_radio_v53.py)
