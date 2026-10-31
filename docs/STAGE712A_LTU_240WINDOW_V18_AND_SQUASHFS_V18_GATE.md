<!-- doc-head: STAGE712A_LTU_240WINDOW_V18_AND_SQUASHFS_V18_GATE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


`Stage 712A` certifica el bloque `Stages 707A..712A` (**`240` ventanas reales** en `198.18.0.63`, guard `fmx_ltu_dma_ring_backpressure_guard.sh`, helper `fmx_qca_wmi_vdev_start_guard.sh`, `LTU Champion v18` y `180` imágenes `WA/XC/XW v18` SquashFS).


# Stage 712A — `LTU v18` (`240`-Window Milestone!) & Universal `WA/XC/XW` SquashFS `v18` (`180` Images) Gate (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `external controller`, `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `proprietary airMAX/LTU module`, `hardware`
- **Verifier**: [`tools/verify/verify_stage712a_ltu_240window_v18_and_squashfs_v18_gate.py`](../tools/verify/verify_stage712a_ltu_240window_v18_and_squashfs_v18_gate.py)
- **Receipt**: [`artifacts/verification/stage712a_ltu_240window_v18_and_squashfs_v18_gate_receipt.json`](../artifacts/verification/stage712a_ltu_240window_v18_and_squashfs_v18_gate_receipt.json)

## 1. Matriz de Certificación `Stages 707A..712A` (`CONFIRMED`)

| Stage | Claim `memory-master` | Entregable Principal | Métrica / Hallazgo Clave | Estado |
| :--- | :---: | :--- | :--- | :---: |
| **`707A`** | `<memorymaster-id>` (`155466`) | [`stage707a_live_ltu110_round20_240window_autoresearch.json`](../artifacts/autoresearch/stage707a_live_ltu110_round20_240window_autoresearch.json) | **`240` ventanas reales** en `.110` (`thin_lt=1`, `early_retrans=3`, RTT `0.184 ms`) | `PASS` |
| **`708A`** | `<memorymaster-id>` (`155467`) | [`stage708a_ltu_dma_ring_backpressure_guard.json`](../artifacts/autoresearch/stage708a_ltu_dma_ring_backpressure_guard.json) | `fmx_ltu_dma_ring_backpressure_guard.sh` (`eab_driver.ko` + `ame_core.ko`, `BQL=36288`, `0` `/dev/ame*`) | `PASS` |
| **`709A`** | `<memorymaster-id>` (`155468`) | [`stage709a_qca_wmi_vdev_start_and_phymode_guard.json`](../artifacts/autoresearch/stage709a_qca_wmi_vdev_start_and_phymode_guard.json) | `fmx_qca_wmi_vdev_start_guard.sh` (`WMI_SERVICE_READY`, `WMI_VDEV_START`, dynamic `phy0..phy2`) | `PASS` |
| **`710A`** | `<memorymaster-id>` (`155469`) | [`stage710a_ltu_20round_240window_champion_v18_receipt.json`](../artifacts/autoresearch/stage710a_ltu_20round_240window_champion_v18_receipt.json) | `rc.poststart_ltu_safe_champion.sh` (`v18`, `20` campañas / `240` ventanas, `0` `/dev/ame*`) | `PASS` |
| **`711A`** | `<memorymaster-id>` (`155470`) | [`stage711a_universal_wa_xc_xw_v18_squashfs_bake.json`](../artifacts/autoresearch/stage711a_universal_wa_xc_xw_v18_squashfs_bake.json) | `180` imágenes `WA/XC/XW v18` SquashFS (`hsqs` + `WMI_VDEV_START` + `phy*`) | `PASS` |
| **`712A`** | `<memorymaster-id>` (`155470`) | [`stage712a_ltu_240window_v18_and_squashfs_v18_gate_receipt.json`](../artifacts/verification/stage712a_ltu_240window_v18_and_squashfs_v18_gate_receipt.json) | Suite `test_stage707a_to_712a_suite.py` + `enforce_5pillar_research_gate.py` | `PASS` |

## 2. Hard Safety & Boundary Audit (`CONFIRMED`)
- **`.241`, `.242`, `.20`, `.250` untouched**: `True`
- **`/dev/ame*` character devices untouched on `198.18.0.63`**: `True`
- **All 6 Stage Docs `< 200` lines with paired `` / ``**: `True`
