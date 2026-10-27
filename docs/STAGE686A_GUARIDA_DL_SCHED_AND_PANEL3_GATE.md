<!-- doc-head: STAGE686A_GUARIDA_DL_SCHED_AND_PANEL3_GATE.md preserved document content -->
<!-- /doc-head -->


# Stage 686A — Consolidated Verification & Discovery Curation Gate (`Stages 681A..686A`)

## 1. Classification & Attribution
- **Claim Classification**: `CONFIRMED`
- **Layer Attribution**: `external controller` + `proprietary airMAX/LTU module` + `mac80211` + `hardware`
- **Safety Gate**: `0` writes executed on `.60`, `.61`, `.82`, `.83`, `.84`.
- **Verification Receipt**: [`stage686a_guarida_dl_sched_and_panel3_gate_receipt.json`](../artifacts/verification/stage686a_guarida_dl_sched_and_panel3_gate_receipt.json)
- **Verification Script**: [`verify_stage686a_guarida_dl_sched_and_panel3_gate.py`](../tools/verify/verify_stage686a_guarida_dl_sched_and_panel3_gate.py)
- **Pytest Suite**: [`test_stage681a_to_686a_guarida_suite.py`](../tests/test_stage681a_to_686a_guarida_suite.py)

## 2. Consolidated Wave Summary (`Stages 681A..686A`)

| Stage | Script & Receipt | Core Technical Finding | Claim & Attribution | 5-Pillar Gate |
| :---: | :--- | :--- | :--- | :---: |
| **`681A`** | [`dissect_stage681a_ubnt_poll_dl_scheduler_and_aggr_budget_re.py`](../tools/re/dissect_stage681a_ubnt_poll_dl_scheduler_and_aggr_budget_re.py) | Dissected `ubnt_poll_host.ko` (`0x00b400..0x00c800` & `0x00dc38..0x00e658`) and `104B` (`0x68`) `.rodata + 0x09f0..0x0e67` `ptmp_netconf` templates; proved SISO/EVM-degraded CPEs suffer a **`-40.0%` to `-73.0%` collapse in per-quantum `aggr_limit_bytes` (`2,710..6,025 B` vs `10,035 B`)** or `1.67x..3.70x` DL airtime/Mbit. | `CONFIRMED` (`proprietary airMAX/LTU module`) | `5/5 PASS` |
| **`682A`** | [`audit_stage682a_guarida_panel3_6cpe_slot_guard_and_evm_radiography.py`](../tools/observability/audit_stage682a_guarida_panel3_6cpe_slot_guard_and_evm_radiography.py) | Radiographed all `6` CPEs of `Panel3 (.83)` (`slot_guard_us = 22..36 us`); proved remediating `SOSA_Joaquin` (`0 dB` RSSI delta vs `16.26 dB` TX EVM gap, `115/256` samples `< 27 dB`) cuts its UL airtime/Mbit by **`-54.99%`** (`9.17%` of sector UL airtime reclaimed) and DL airtime/Mbit by **`-32.49%`**. | `CONFIRMED` (`hardware`) | `5/5 PASS` |
| **`683A`** | [`audit_stage683a_panel1_guarida_84_per_tid_aql_and_atf_20h.py`](../tools/observability/audit_stage683a_panel1_guarida_84_per_tid_aql_and_atf_20h.py) | Audited all `24` active station-TID queues (`TID 0..7`) on `Panel1-Guarida (.84)` across `20.12+` hours (`39,343,195` total TX packets): **`0` CoDel drops, `0` ECN marks, `0` overlimit events, and `0 B` backlog across all `1,185,020` `TID 1..7` packets** (`807,288` `AC_VO`, `200,518` `AC_VI`, `237,214` `AC_BK/Alt-BE`). | `CONFIRMED` (`mac80211`) | `5/5 PASS` |
| **`684A`** | [`run_stage684a_guarida_panel2_panel3_tdma_frame_alignment_pareto.py`](../tools/sim/run_stage684a_guarida_panel2_panel3_tdma_frame_alignment_pareto.py) | `SimPy` + `pymoo` `NSGA-II` proves synchronizing `.82` and `.83` to `Fixed 10ms 67/33` (`0 us` offset) eliminates the **`43.15% -> 0.00%` AP-to-AP TX/RX self-interference overlap**, boosting `.82` DL goodput **`+42.74%`** and tower goodput **`+7.58%` (`119.12 -> 128.15 Mbps`)**. | `INFERRED` (`proprietary airMAX/LTU module`) | `5/5 PASS` |
| **`685A`** | [`build_stage685a_guarida_34endpoint_production_rollout_playbook_v5.py`](../tools/observability/build_stage685a_guarida_34endpoint_production_rollout_playbook_v5.py) | Built 4-phase zero-risk rollout playbook `v5` covering all `34` Guarida endpoints (`2` Backhaul PtP + `32` Sector CPEs) under `45s` Non-DFS / `120s` DFS rollback watchdogs. | `INFERRED` (`external controller`) | `5/5 PASS` |
| **`686A`** | [`verify_stage686a_guarida_dl_sched_and_panel3_gate.py`](../tools/verify/verify_stage686a_guarida_dl_sched_and_panel3_gate.py) | Curated `FMX-DISC-53` & `FMX-DISC-54` in [`CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md`](CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md) and verified `100%` 5-pillar and `<200`-line compliance. | `CONFIRMED` (`external controller`) | `5/5 PASS` |
