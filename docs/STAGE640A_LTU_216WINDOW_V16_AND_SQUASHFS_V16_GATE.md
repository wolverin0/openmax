<!-- doc-head: STAGE640A_LTU_216WINDOW_V16_AND_SQUASHFS_V16_GATE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


`Stage 640A` certifica el bloque `Stages 635A..640A` (**`216` ventanas reales** en `198.18.0.63`, guard `fmx_ltu_tof_ta_cp_guard.sh`, helper `fmx_qca_txbf_stbc_ldpc_guard.sh`, `LTU Champion v16` y `180` imágenes `WA/XC/XW v16` SquashFS).


# Stage 640A — `LTU v16` (`216`-Window Milestone!) & Universal `WA/XC/XW` SquashFS `v16` (`180` Images) Gate (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `external controller`, `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `proprietary airMAX/LTU module`, `hardware`
- **Verifier**: [`tools/verify/verify_stage640a_ltu_216window_v16_and_squashfs_v16_gate.py`](../tools/verify/verify_stage640a_ltu_216window_v16_and_squashfs_v16_gate.py)
- **Receipt**: [`artifacts/verification/stage640a_ltu_216window_v16_and_squashfs_v16_gate_receipt.json`](../artifacts/verification/stage640a_ltu_216window_v16_and_squashfs_v16_gate_receipt.json)

## 1. Matriz de Certificación `Stages 635A..640A` (`CONFIRMED`)

| Stage | Claim `memory-master` | Entregable Principal | Métrica / Hallazgo Clave | Estado |
| :--- | :---: | :--- | :--- | :---: |
| **`635A`** | `<memorymaster-id>` (`155456`) | [`stage635a_live_ltu110_round18_216window_autoresearch.json`](../artifacts/autoresearch/stage635a_live_ltu110_round18_216window_autoresearch.json) | **`216` ventanas reales** en `.110` (`udp_rmem_min=16384`, `wmem_min=16384`, RTT `0.187 ms`) | `PASS` |
| **`636A`** | `<memorymaster-id>` (`155457`) | [`stage636a_ltu_tof_ta_and_cp_guard.json`](../artifacts/autoresearch/stage636a_ltu_tof_ta_and_cp_guard.json) | `fmx_ltu_tof_ta_cp_guard.sh` (`distance_meter`, `ame_core_update_ta_cpe`, `early_data_cfg`, `cpsample`) | `PASS` |
| **`637A`** | `<memorymaster-id>` (`155458`) | [`stage637a_qca_txbf_stbc_and_ldpc_guard.json`](../artifacts/autoresearch/stage637a_qca_txbf_stbc_and_ldpc_guard.json) | `fmx_qca_txbf_stbc_ldpc_guard.sh` (`LDPC=1`, `STBC=1`, `SU-TxBF=0`, desambiguación `bf_`) | `PASS` |
| **`638A`** | `<memorymaster-id>` (`155459`) | [`stage638a_ltu_18round_216window_champion_v16_receipt.json`](../artifacts/autoresearch/stage638a_ltu_18round_216window_champion_v16_receipt.json) | `rc.poststart_ltu_safe_champion.sh` (`v16`, `18` campañas / `216` ventanas, `0` `/dev/ame*`) | `PASS` |
| **`639A`** | `<memorymaster-id>` (`155460`) | [`stage639a_universal_wa_xc_xw_v16_squashfs_bake.json`](../artifacts/autoresearch/stage639a_universal_wa_xc_xw_v16_squashfs_bake.json) | `180` imágenes `WA/XC/XW v16` SquashFS (`hsqs` + `WA Champion v10` `256` ventanas) | `PASS` |
| **`640A`** | `<memorymaster-id>` (`155460`) | [`stage640a_ltu_216window_v16_and_squashfs_v16_gate_receipt.json`](../artifacts/verification/stage640a_ltu_216window_v16_and_squashfs_v16_gate_receipt.json) | Suite `test_stage635a_to_640a_suite.py` + `enforce_5pillar_research_gate.py` | `PASS` |

## 2. Hard Safety & Boundary Audit (`CONFIRMED`)
- **`.241`, `.242`, `.20`, `.250` untouched**: `True`
- **`/dev/ame*` character devices untouched on `198.18.0.63`**: `True`
- **All 6 Stage Docs `< 220` lines with paired `` / ``**: `True`
