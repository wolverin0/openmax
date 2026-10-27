<!-- doc-head: STAGE524A_MULTI_RADIO_V49_SUITE_GATE.md preserved document content -->
<!-- /doc-head -->


# Stage 524A: Consolidated Multi-Radio `v49` Suite Gate (`Stages 519A..524A`, `156-Window` Milestone & Cross-Fleet Champion `v49.0`)

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `external controller` (verification harness) + `QCA firmware` + `proprietary airMAX/LTU module` + `Linux`
- **Safety Gate**: `.241`, `.242`, `.250` untouched (`CONFIRMED`)
- **Artifact**: [`stage524a_multi_radio_v49_suite_gate_receipt.json`](../artifacts/verification/stage524a_multi_radio_v49_suite_gate_receipt.json)
- **Verifier**: [`verify_stage524a_multi_radio_v49_suite_gate.py`](../tools/verify/verify_stage524a_multi_radio_v49_suite_gate.py)
- **Test Suite**: [`test_stage519a_to_524a_multi_radio_v49.py`](../tests/test_stage519a_to_524a_multi_radio_v49.py)

## 1. Audited Stages (`Stages 519A..524A`)

| Stage | Scope | Receipt | Doc (`<220` lines) | 5-Pillar Gate |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 519A** | `156-Window` Multi-Radio Milestone (`R99–R104`, `VHT40` MCS 2 LGI + `pktlog=0x0` + `nf_cal=120`) | `stage519a_156window_multi_radio_milestone_r99_r104.json` | `STAGE519A_156WINDOW_MULTI_RADIO_MILESTONE_R99_R104.md` | `PASS` |
| **Stage 520A** | `WA`/`XC` Xtensa `PB050` RC Probe Dampening Pareto Frontier ($3 \times 3$ Grid) | `stage520a_wa_xc_xtensa_pb050_rc_dampen_pareto.json` | `STAGE520A_WA_XC_XTENSA_PB050_RC_DAMPEN_PARETO.md` | `PASS` |
| **Stage 521A** | `32-CPE` PtMP Airtime Fairness & VoIP Protection `v3` (`aql_txq_limit=1500/2000`) | `stage521a_ptmp_32cpe_airtime_fairness_and_voip_protect_v3.json` | `STAGE521A_PTMP_32CPE_AIRTIME_FAIRNESS_AND_VOIP_PROTECT_V3.md` | `PASS` |
| **Stage 522A** | `PBE-5AC-Gen2` & `LBE-5AC-Gen2` `VHT40` `24.83 Mbps` (`0.0%` Loss) Field Rollout Validator | `stage522a_pbe5ac_lbe5ac_vht40_25mbps_field_rollout_validator.json` | `STAGE522A_PBE5AC_LBE5AC_VHT40_25MBPS_FIELD_ROLLOUT_VALIDATOR.md` | `PASS` |
| **Stage 523A** | Cross-Fleet Champion `v49.0` & Tester Matrix (`208` `WA`, `156` Multi-Radio, `144` `LTU`) | `stage523a_cross_fleet_champion_v49_and_tester_matrix.json` | `STAGE523A_CROSS_FLEET_CHAMPION_V49_AND_TESTER_MATRIX.md` | `PASS` |
| **Stage 524A** | End-to-End Suite Gate & Repo-Wide 5-Pillar Check | `stage524a_multi_radio_v49_suite_gate_receipt.json` | `STAGE524A_MULTI_RADIO_V49_SUITE_GATE.md` | `PASS` |
