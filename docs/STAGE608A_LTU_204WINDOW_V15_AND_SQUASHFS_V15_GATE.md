<!-- doc-head: STAGE608A_LTU_204WINDOW_V15_AND_SQUASHFS_V15_GATE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


`Stage 608A` certifica el bloque `Stages 603A..608A` (**`204` ventanas reales** en `198.18.0.63`, guard `fmx_ltu_200w_golden_guard.sh`, helper `fmx_qca988x_wmi_peer_rate_sgi_guard.sh`, `LTU Golden Champion v15` y `180` imágenes `WA/XC/XW v15` SquashFS).


# Stage 608A — `LTU v15` (`204`-Window Milestone!) & Universal `WA/XC/XW` SquashFS `v15` (`180` Images) Gate (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `external controller`, `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `proprietary airMAX/LTU module`, `hardware`
- **Verifier**: [`tools/verify/verify_stage608a_ltu_204window_v15_and_squashfs_v15_gate.py`](../tools/verify/verify_stage608a_ltu_204window_v15_and_squashfs_v15_gate.py)
- **Receipt**: [`artifacts/verification/stage608a_ltu_204window_v15_and_squashfs_v15_gate_receipt.json`](../artifacts/verification/stage608a_ltu_204window_v15_and_squashfs_v15_gate_receipt.json)

## 1. Matriz de Certificación `Stages 603A..608A` (`CONFIRMED`)

| Stage | Claim `memory-master` | Entregable Principal | Métrica / Hallazgo Clave | Estado |
| :--- | :---: | :--- | :--- | :---: |
| **`603A`** | `<memorymaster-id>` (`155451`) | [`stage603a_live_ltu110_round17_204window_autoresearch.json`](../artifacts/autoresearch/stage603a_live_ltu110_round17_204window_autoresearch.json) | **`204` ventanas reales** en `.110` (`tcp_recovery=1`, `early_retrans=3`, RTT `0.188 ms`) | `PASS` |
| **`604A`** | `<memorymaster-id>` (`155452`) | [`stage604a_ltu_204window_lbt_and_spectral_guard.json`](../artifacts/autoresearch/stage604a_ltu_204window_lbt_and_spectral_guard.json) | `fmx_ltu_200w_golden_guard.sh` (`24` símbolos `LBT`, `lbt_cfg_pause_txframe`, `interf_avg/curr`, `7` auto-freq keys) | `PASS` |
| **`605A`** | `<memorymaster-id>` (`155453`) | [`stage605a_qca988x_wmi_peer_rate_sgi_guard.json`](../artifacts/autoresearch/stage605a_qca988x_wmi_peer_rate_sgi_guard.json) | `fmx_qca988x_wmi_peer_rate_sgi_guard.sh` (`WMI_PEER_ASSOC_CMDID`, `_RATE_SetSGIMasks`, `Stage 487A` clean re-assoc) | `PASS` |
| **`606A`** | `<memorymaster-id>` (`155454`) | [`stage606a_ltu_17round_204window_champion_v15_receipt.json`](../artifacts/autoresearch/stage606a_ltu_17round_204window_champion_v15_receipt.json) | `rc.poststart_ltu_safe_champion.sh` (`v15`, `17` campañas / `204` ventanas, `0` `/dev/ame*`) | `PASS` |
| **`607A`** | `<memorymaster-id>` (`155455`) | [`stage607a_universal_wa_xc_xw_v15_squashfs_bake.json`](../artifacts/autoresearch/stage607a_universal_wa_xc_xw_v15_squashfs_bake.json) | `180` imágenes `WA/XC/XW v15` SquashFS (`hsqs` + `WMI SGI Guard` + `PB-050`) | `PASS` |
| **`608A`** | `<memorymaster-id>` (`155455`) | [`stage608a_ltu_204window_v15_and_squashfs_v15_gate_receipt.json`](../artifacts/verification/stage608a_ltu_204window_v15_and_squashfs_v15_gate_receipt.json) | Suite `test_stage603a_to_608a_suite.py` + `enforce_5pillar_research_gate.py` | `PASS` |

## 2. Hard Safety & Boundary Audit (`CONFIRMED`)
- **`.241`, `.242`, `.20`, `.250` untouched**: `True`
- **`/dev/ame*` character devices untouched on `198.18.0.63`**: `True`
- **All 6 Stage Docs `< 220` lines with paired `` / ``**: `True`
