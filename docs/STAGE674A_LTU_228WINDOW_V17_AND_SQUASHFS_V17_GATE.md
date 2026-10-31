<!-- doc-head: STAGE674A_LTU_228WINDOW_V17_AND_SQUASHFS_V17_GATE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


`Stage 674A` certifica el bloque `Stages 669A..674A` (**`228` ventanas reales** en `198.18.0.63`, guard `fmx_ltu_gps_1pps_sync_guard.sh`, helper `fmx_qca_htt_tx_compl_guard.sh`, `LTU Champion v17` y `180` imágenes `WA/XC/XW v17` SquashFS).


# Stage 674A — `LTU v17` (`228`-Window Milestone!) & Universal `WA/XC/XW` SquashFS `v17` (`180` Images) Gate (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `external controller`, `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `proprietary airMAX/LTU module`, `hardware`
- **Verifier**: [`tools/verify/verify_stage674a_ltu_228window_v17_and_squashfs_v17_gate.py`](../tools/verify/verify_stage674a_ltu_228window_v17_and_squashfs_v17_gate.py)
- **Receipt**: [`artifacts/autoresearch/stage674a_ltu_228window_v17_and_squashfs_v17_gate_receipt.json`](../artifacts/autoresearch/stage674a_ltu_228window_v17_and_squashfs_v17_gate_receipt.json)

## 1. Matriz de Certificación `Stages 669A..674A` (`CONFIRMED`)

| Stage | Claim `memory-master` | Entregable Principal | Métrica / Hallazgo Clave | Estado |
| :--- | :---: | :--- | :--- | :---: |
| **`669A`** | `<memorymaster-id>` (`155461`) | [`stage669a_live_ltu110_round19_228window_autoresearch.json`](../artifacts/autoresearch/stage669a_live_ltu110_round19_228window_autoresearch.json) | **`228` ventanas reales** en `.110` (`budget_usecs=4000`, `tsq=131072`, RTT `0.186 ms`) | `PASS` |
| **`670A`** | `<memorymaster-id>` (`155462`) | [`stage670a_ltu_gps_1pps_sync_and_holdover_guard.json`](../artifacts/autoresearch/stage670a_ltu_gps_1pps_sync_and_holdover_guard.json) | `fmx_ltu_gps_1pps_sync_guard.sh` (`frame_pulse_offset`, `SFN_synchronized`, `holdover=10.7s`) | `PASS` |
| **`671A`** | `<memorymaster-id>` (`155463`) | [`stage671a_qca_htt_tx_compl_and_aql_guard.json`](../artifacts/autoresearch/stage671a_qca_htt_tx_compl_and_aql_guard.json) | `fmx_qca_htt_tx_compl_guard.sh` (`HTT_T2H_MSG_TYPE_TX_COMPL_IND`, `aql_threshold=24000`, `aql=4000`) | `PASS` |
| **`672A`** | `<memorymaster-id>` (`155464`) | [`stage672a_ltu_19round_228window_champion_v17_receipt.json`](../artifacts/autoresearch/stage672a_ltu_19round_228window_champion_v17_receipt.json) | `rc.poststart_ltu_safe_champion.sh` (`v17`, `19` campañas / `228` ventanas, `0` `/dev/ame*`) | `PASS` |
| **`673A`** | `<memorymaster-id>` (`155465`) | [`stage673a_universal_wa_xc_xw_v17_squashfs_bake.json`](../artifacts/autoresearch/stage673a_universal_wa_xc_xw_v17_squashfs_bake.json) | `180` imágenes `WA/XC/XW v17` SquashFS (`hsqs` + `WA v11` + `PtP v3`) | `PASS` |
| **`674A`** | `<memorymaster-id>` (`155465`) | [`stage674a_ltu_228window_v17_and_squashfs_v17_gate_receipt.json`](../artifacts/autoresearch/stage674a_ltu_228window_v17_and_squashfs_v17_gate_receipt.json) | Suite `test_stage669a_to_674a_suite.py` + `enforce_5pillar_research_gate.py` | `PASS` |

## 2. Hard Safety & Boundary Audit (`CONFIRMED`)
- **`.241`, `.242`, `.20`, `.250` untouched**: `True`
- **`/dev/ame*` character devices untouched on `198.18.0.63`**: `True`
- **All 6 Stage Docs `< 200` lines with paired `` / ``**: `True`
