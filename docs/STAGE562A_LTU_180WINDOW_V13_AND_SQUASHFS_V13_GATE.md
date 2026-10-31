<!-- doc-head: STAGE562A_LTU_180WINDOW_V13_AND_SQUASHFS_V13_GATE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


`Stage 562A` certifica el bloque `Stages 557A..562A` (**`180` ventanas reales** en `198.18.0.63`, guard `Super-4096-QAM` DPD/EVM, helper `XW/XM` `ANI` & `SWR`, `LTU Champion v13` y `180` imágenes `WA/XC/XW v13` SquashFS).


# Stage 562A — `LTU v13` (`180`-Window Milestone!) & Universal `WA/XC/XW` SquashFS `v13` (`180` Images) Gate (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `external controller`, `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `proprietary airMAX/LTU module`, `hardware`
- **Verifier**: [`tools/verify/verify_stage562a_ltu_180window_v13_and_squashfs_v13_gate.py`](../tools/verify/verify_stage562a_ltu_180window_v13_and_squashfs_v13_gate.py)
- **Receipt**: [`artifacts/autoresearch/stage562a_ltu_180window_v13_and_squashfs_v13_gate_receipt.json`](../artifacts/autoresearch/stage562a_ltu_180window_v13_and_squashfs_v13_gate_receipt.json)

## 1. Matriz de Certificación `Stages 557A..562A` (`CONFIRMED`)

| Stage | Claim `memory-master` | Entregable Principal | Métrica / Hallazgo Clave | Estado |
| :--- | :---: | :--- | :--- | :---: |
| **`557A`** | `<memorymaster-id>` (`155441`) | [`stage557a_live_ltu110_round15_180window_autoresearch.json`](../artifacts/autoresearch/stage557a_live_ltu110_round15_180window_autoresearch.json) | **`180` ventanas reales** en `.110` (`slow_start_after_idle=0`, `no_metrics_save=1`, RTT `0.192 ms`) | `PASS` |
| **`558A`** | `<memorymaster-id>` (`155442`) | [`stage558a_ltu_super4096_dpd_evm_guard.json`](../artifacts/autoresearch/stage558a_ltu_super4096_dpd_evm_guard.json) | `fmx_ltu_super4096_dpd_evm_guard.sh` (`<= -38 dB` EVM, `4 dB` PA backoff para `12x`) | `PASS` |
| **`559A`** | `<memorymaster-id>` (`155443`) | [`stage559a_xw_xm_ani_and_swr_limit_helper.json`](../artifacts/autoresearch/stage559a_xw_xm_ani_and_swr_limit_helper.json) | `fmx_xw_xm_ani_and_swr_limit_helper.sh` (`ANI=1`, `short=7`, `long=4` en `AR934x/AR724x`) | `PASS` |
| **`560A`** | `<memorymaster-id>` (`155444`) | [`stage560a_ltu_15round_180window_champion_v13_receipt.json`](../artifacts/autoresearch/stage560a_ltu_15round_180window_champion_v13_receipt.json) | `rc.poststart_ltu_safe_champion.sh` (`v13`, `15` campañas / `180` ventanas, `0` `/dev/ame*`) | `PASS` |
| **`561A`** | `<memorymaster-id>` (`155445`) | [`stage561a_universal_wa_xc_xw_v13_squashfs_bake.json`](../artifacts/autoresearch/stage561a_universal_wa_xc_xw_v13_squashfs_bake.json) | `180` imágenes `WA/XC/XW v13` SquashFS (`hsqs`) | `PASS` |
| **`562A`** | `<memorymaster-id>` (`155445`) | [`stage562a_ltu_180window_v13_and_squashfs_v13_gate_receipt.json`](../artifacts/autoresearch/stage562a_ltu_180window_v13_and_squashfs_v13_gate_receipt.json) | Suite `test_stage557a_to_562a_suite.py` + `enforce_5pillar_research_gate.py` | `PASS` |

## 2. Hard Safety & Boundary Audit (`CONFIRMED`)
- **`.241`, `.242`, `.20`, `.250` untouched**: `True`
- **`/dev/ame*` character devices untouched on `198.18.0.63`**: `True`
- **All 6 Stage Docs `< 220` lines with paired `` / ``**: `True`
