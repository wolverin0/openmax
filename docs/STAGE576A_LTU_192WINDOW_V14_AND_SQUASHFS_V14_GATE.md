<!-- doc-head: STAGE576A_LTU_192WINDOW_V14_AND_SQUASHFS_V14_GATE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


`Stage 576A` certifica el bloque `Stages 571A..576A` (**`192` ventanas reales** en `198.18.0.63`, helper `AF-LTU` `TDMA Framing/Split/SFN`, helper `QCA PAPRD/TPC/CTL`, `LTU Champion v14` y `180` imágenes `WA/XC/XW v14` SquashFS).


# Stage 576A — `LTU v14` (`192`-Window Milestone!) & Universal `WA/XC/XW` SquashFS `v14` (`180` Images) Gate (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `external controller`, `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `proprietary airMAX/LTU module`, `hardware`
- **Verifier**: [`tools/verify/verify_stage576a_ltu_192window_v14_and_squashfs_v14_gate.py`](../tools/verify/verify_stage576a_ltu_192window_v14_and_squashfs_v14_gate.py)
- **Receipt**: [`artifacts/autoresearch/stage576a_ltu_192window_v14_and_squashfs_v14_gate_receipt.json`](../artifacts/autoresearch/stage576a_ltu_192window_v14_and_squashfs_v14_gate_receipt.json)

## 1. Matriz de Certificación `Stages 571A..576A` (`CONFIRMED`)

| Stage | Claim `memory-master` | Entregable Principal | Métrica / Hallazgo Clave | Estado |
| :--- | :---: | :--- | :--- | :---: |
| **`571A`** | `<memorymaster-id>` (`155446`) | [`stage571a_live_ltu110_round16_192window_autoresearch.json`](../artifacts/autoresearch/stage571a_live_ltu110_round16_192window_autoresearch.json) | **`192` ventanas reales** en `.110` (`pacing_ca=110`, `pacing_ss=160`, `usecs=4000`, RTT `0.19 ms`) | `PASS` |
| **`572A`** | `<memorymaster-id>` (`155447`) | [`stage572a_ltu_tdma_framing_and_split_sfn_helper.json`](../artifacts/autoresearch/stage572a_ltu_tdma_framing_and_split_sfn_helper.json) | `fmx_ltu_tdma_split_sfn_helper.sh` (`frame_len=2ms`, `duty_cycle=67%`, `bc_dl_symbols=2`, `SFN`) | `PASS` |
| **`573A`** | `<memorymaster-id>` (`155448`) | [`stage573a_qca_paprd_olpc_and_thermal_tpc_helper.json`](../artifacts/autoresearch/stage573a_qca_paprd_olpc_and_thermal_tpc_helper.json) | `fmx_qca_paprd_olpc_tpc_helper.sh` (`PAPRD 7-stage`, `GreenTX=0`, `TPC/CTL` & `thermal_send`) | `PASS` |
| **`574A`** | `<memorymaster-id>` (`155449`) | [`stage574a_ltu_16round_192window_champion_v14_receipt.json`](../artifacts/autoresearch/stage574a_ltu_16round_192window_champion_v14_receipt.json) | `rc.poststart_ltu_safe_champion.sh` (`v14`, `16` campañas / `192` ventanas, `0` `/dev/ame*`) | `PASS` |
| **`575A`** | `<memorymaster-id>` (`155450`) | [`stage575a_universal_wa_xc_xw_v14_squashfs_bake.json`](../artifacts/autoresearch/stage575a_universal_wa_xc_xw_v14_squashfs_bake.json) | `180` imágenes `WA/XC/XW v14` SquashFS (`hsqs` + `PB-050`) | `PASS` |
| **`576A`** | `<memorymaster-id>` (`155450`) | [`stage576a_ltu_192window_v14_and_squashfs_v14_gate_receipt.json`](../artifacts/autoresearch/stage576a_ltu_192window_v14_and_squashfs_v14_gate_receipt.json) | Suite `test_stage571a_to_576a_suite.py` + `enforce_5pillar_research_gate.py` | `PASS` |

## 2. Hard Safety & Boundary Audit (`CONFIRMED`)
- **`.241`, `.242`, `.20`, `.250` untouched**: `True`
- **`/dev/ame*` character devices untouched on `198.18.0.63`**: `True`
- **All 6 Stage Docs `< 220` lines with paired `` / ``**: `True`
