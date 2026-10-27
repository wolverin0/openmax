<!-- doc-head: STAGE740A_GUARIDA_POLLING_AND_34ENDPOINT_CARD_GATE.md preserved document content -->
<!-- /doc-head -->


# Stage 740A — Consolidated Verification & Discovery Curation Gate (`Stages 735A..740A`)

## 1. Classification & Attribution
- **Claim Classification**: `CONFIRMED`
- **Layer Attribution**: `external controller` + `proprietary airMAX/LTU module` + `QCA firmware` + `hardware`
- **Safety Gate**: `0` writes executed on `.60`, `.61`, `.82`, `.83`, `.84`.
- **Verification Receipt**: [`stage740a_guarida_polling_and_34endpoint_card_gate_receipt.json`](../artifacts/verification/stage740a_guarida_polling_and_34endpoint_card_gate_receipt.json)
- **Verification Script**: [`verify_stage740a_guarida_polling_and_34endpoint_card_gate.py`](../tools/verify/verify_stage740a_guarida_polling_and_34endpoint_card_gate.py)
- **Pytest Suite**: [`test_stage735a_to_740a_guarida_suite.py`](../tests/test_stage735a_to_740a_guarida_suite.py)

## 2. Consolidated Wave Summary (`Stages 735A..740A`)

| Stage | Script & Receipt | Core Technical Finding | Claim & Attribution | 5-Pillar Gate |
| :---: | :--- | :--- | :--- | :---: |
| **`735A`** | [`dissect_stage735a_ubnt_poll_ul_polling_and_activity_aging_re.py`](../tools/re/dissect_stage735a_ubnt_poll_ul_polling_and_activity_aging_re.py) | Dissected `ubnt_poll_host_ht_comm_rx` (`0x00e67c`) & `ubnt_poll_ht_comm_parse` (`0x014894`): unpacked `activity_aging = 3.0s` (`0x1c`), `activity_aging_da = 10.0s` (`0x20`), and `activity_aging_hb = 1.0s` (`0x24`); proved `1,500 ms` aging cuts empty-poll waste by **`-54.17%` (`446.4 -> 204.6 us/frame`)**. | `CONFIRMED` (`proprietary airMAX/LTU module`) | `5/5 PASS` |
| **`736A`** | [`audit_stage736a_guarida_panel2_22cpe_dl_aggr_collapse_and_airtime_hog.py`](../tools/observability/audit_stage736a_guarida_panel2_22cpe_dl_aggr_collapse_and_airtime_hog.py) | Ranked all `22` CPEs on `Panel2 (.82)` by `600 us` DL quantum byte limit (`10,035 B` ideal): `RODRIGUEZ_Marina` & `Marilina SEVERO` collapse to **`2,710 B` (`-73.0%`, `3.70x` hog)**; remediating top hogs lifts sector harmonic DL capacity **`+15.86%` (`76.59 -> 88.74 Mbps`)**. | `CONFIRMED` (`proprietary airMAX/LTU module`) | `5/5 PASS` |
| **`737A`** | [`audit_stage737a_guarida_backbone_60_61_ampdu_and_shift_preflight.py`](../tools/observability/audit_stage737a_guarida_backbone_60_61_ampdu_and_shift_preflight.py) | Verified `.60 <-> .61` A-MPDU density (`3.92` MPDUs/PPDU), `ast_rxorn` lockstep (`98.53%`), and `5/5` pre-flight checks for zero-drop 3-int synchronous CSA (`+10 MHz`, **`+17.17 Mbps`**). | `CONFIRMED` (`QCA firmware`) | `5/5 PASS` |
| **`738A`** | [`run_stage738a_guarida_panel2_activity_aging_and_cbp_pareto.py`](../tools/sim/run_stage738a_guarida_panel2_activity_aging_and_cbp_pareto.py) | `SimPy` + `pymoo` `NSGA-II` proves `Fixed 10ms 67/33` + `activity_aging = 1,500 ms` + `ff_cbp_slots = 4` (`240 us`) delivers **`+34.84%` DL goodput**, cuts CBP collisions from `20.31%` to **`11.93%`**, and lowers `p95` wake-up latency by **`-39.65%`**. | `INFERRED` (`proprietary airMAX/LTU module`) | `5/5 PASS` |
| **`739A`** | [`build_stage739a_guarida_34endpoint_operator_field_action_card_v6.py`](../tools/observability/build_stage739a_guarida_34endpoint_operator_field_action_card_v6.py) | Built 1-line-per-endpoint field scorecard `v6` across all **`34` Guarida endpoints** (`1` `OK`, `10` `REMEDIAR ANTENA`, `23` `AJUSTAR TDMA`). | `CONFIRMED` (`external controller`) | `5/5 PASS` |
| **`740A`** | [`verify_stage740a_guarida_polling_and_34endpoint_card_gate.py`](../tools/verify/verify_stage740a_guarida_polling_and_34endpoint_card_gate.py) | Curated `FMX-DISC-55` & `FMX-DISC-56` in [`CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md`](CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md) and verified `100%` 5-pillar and `<200`-line compliance. | `CONFIRMED` (`external controller`) | `5/5 PASS` |
