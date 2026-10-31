<!-- doc-head: STAGE734A_LTU_252WINDOW_V19_AND_SQUASHFS_V19_GATE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


`Stage 734A` certifica el bloque `Stages 729A..734A` (**`252` ventanas reales** en `198.18.0.63`, guard `fmx_ltu_thermal_pa_bias_guard.sh`, helper `fmx_qca_spectral_radar_phyerr_guard.sh`, `LTU Champion v19` y `180` imágenes `WA/XC/XW v19` SquashFS).


# Stage 734A — `LTU v19` (`252`-Window Milestone!) & Universal `WA/XC/XW` SquashFS `v19` (`180` Images) Gate (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `external controller`, `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `proprietary airMAX/LTU module`, `hardware`
- **Verifier**: [`tools/verify/verify_stage734a_ltu_252window_v19_and_squashfs_v19_gate.py`](../tools/verify/verify_stage734a_ltu_252window_v19_and_squashfs_v19_gate.py)
- **Receipt**: [`artifacts/verification/stage734a_ltu_252window_v19_and_squashfs_v19_gate_receipt.json`](../artifacts/verification/stage734a_ltu_252window_v19_and_squashfs_v19_gate_receipt.json)

## 1. Matriz de Certificación `Stages 729A..734A` (`CONFIRMED`)

| Stage | Claim `memory-master` | Entregable Principal | Métrica / Hallazgo Clave | Estado |
| :--- | :---: | :--- | :--- | :---: |
| **`729A`** | `<memorymaster-id>` (`155471`) | [`stage729a_live_ltu110_round21_252window_autoresearch.json`](../artifacts/autoresearch/stage729a_live_ltu110_round21_252window_autoresearch.json) | **`252` ventanas reales** en `.110` (`no_metrics=1`, `temp=47500 mC`, RTT `0.184 ms`) | `PASS` |
| **`730A`** | `<memorymaster-id>` (`155472`) | [`stage730a_ltu_thermal_pa_bias_and_gain_guard.json`](../artifacts/autoresearch/stage730a_ltu_thermal_pa_bias_and_gain_guard.json) | `fmx_ltu_thermal_pa_bias_guard.sh` (`ame_core.ko` + `ame_dev.ko`, `EVM <= -38 dB`, `0` `/dev/ame*`) | `PASS` |
| **`731A`** | `<memorymaster-id>` (`155473`) | [`stage731a_qca_spectral_radar_phyerr_guard.json`](../artifacts/autoresearch/stage731a_qca_spectral_radar_phyerr_guard.json) | `fmx_qca_spectral_radar_phyerr_guard.sh` (`ATH10K_PHYERR_SPECTRAL`, `ATH10K_PHYERR_RADAR`, `phy0..phy2`) | `PASS` |
| **`732A`** | `<memorymaster-id>` (`155474`) | [`stage732a_ltu_21round_252window_champion_v19_receipt.json`](../artifacts/autoresearch/stage732a_ltu_21round_252window_champion_v19_receipt.json) | `rc.poststart_ltu_safe_champion.sh` (`v19`, `21` campañas / `252` ventanas, `0` `/dev/ame*`) | `PASS` |
| **`733A`** | `<memorymaster-id>` (`155475`) | [`stage733a_universal_wa_xc_xw_v19_squashfs_bake.json`](../artifacts/autoresearch/stage733a_universal_wa_xc_xw_v19_squashfs_bake.json) | `180` imágenes `WA/XC/XW v19` SquashFS (`hsqs` + `PHYERR` guard + `phy*`) | `PASS` |
| **`734A`** | `<memorymaster-id>` (`155475`) | [`stage734a_ltu_252window_v19_and_squashfs_v19_gate_receipt.json`](../artifacts/verification/stage734a_ltu_252window_v19_and_squashfs_v19_gate_receipt.json) | Suite `test_stage729a_to_734a_suite.py` + `enforce_5pillar_research_gate.py` | `PASS` |

## 2. Hard Safety & Boundary Audit (`CONFIRMED`)
- **`.241`, `.242`, `.20`, `.250` untouched**: `True`
- **`/dev/ame*` character devices untouched on `198.18.0.63`**: `True`
- **All 6 Stage Docs `< 200` lines with paired `` / ``**: `True`
