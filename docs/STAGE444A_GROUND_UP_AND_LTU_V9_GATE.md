<!-- doc-head: STAGE444A_GROUND_UP_AND_LTU_V9_GATE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


`Stage 444A` certifica el bloque `Stages 439A..444A` (`132` ventanas reales en `198.18.0.63`, kit `LTU SQ + Split-Freq`, compositor `WMI 0x9064` tras decompresión `BMI_LZ`, Pareto `5-Pillar` y `Champion v9`).


# Stage 444A — End-to-End 5-Pillar Ground-Up & LTU `v9` (`132`-Window) Verification Gate (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `proprietary airMAX/LTU module`, `hardware`
- **Verifier**: [`tools/verify/verify_stage444a_ground_up_and_ltu_v9_gate.py`](../tools/verify/verify_stage444a_ground_up_and_ltu_v9_gate.py)
- **Artifact**: [`artifacts/autoresearch/stage444a_ground_up_and_ltu_v9_gate_receipt.json`](../artifacts/autoresearch/stage444a_ground_up_and_ltu_v9_gate_receipt.json)

## 1. Matriz de Certificación `Stages 439A..444A` (`CONFIRMED`)

| Stage | Claim `memory-master` | Entregable Principal | Métrica / Hallazgo Clave | Estado |
| :--- | :---: | :--- | :--- | :---: |
| **`439A`** | `<memorymaster-id>` (`155405`) | [`stage439a_live_ltu110_round11_132window_autoresearch.json`](../artifacts/autoresearch/stage439a_live_ltu110_round11_132window_autoresearch.json) | `132` ventanas reales en `.110` (`timer_migration=0`, `lowat=12288`, `thin_stream=1`) | `PASS` |
| **`440A`** | `<memorymaster-id>` (`155406`) | [`stage440a_ltu_sq_micro_ap_and_split_freq_kit.json`](../artifacts/autoresearch/stage440a_ltu_sq_micro_ap_and_split_freq_kit.json) | `SQ <= 16 CPEs` (`-16.5%` overhead) + `AD9361 TX_LO != RX_LO` (`+32 dB` rechazo) | `PASS` |
| **`441A`** | `<memorymaster-id>` (`155407`) | [`stage441a_xtensa_wmi_0x9064_polling_hook_composer.json`](../artifacts/autoresearch/stage441a_xtensa_wmi_0x9064_polling_hook_composer.json) | `BMI_LZ` decompresión reconcilia `IE 3` (`216,724 B`) con `0x009b2037` (`51` cmds) y `0x0040f688` (`32` hooks) | `PASS` |
| **`442A`** | `<memorymaster-id>` (`155408`) | [`stage442a_ground_up_5pillars_combined_pareto.json`](../artifacts/autoresearch/stage442a_ground_up_5pillars_combined_pareto.json) | `638.15 Mbps` (`+29.59%` vs `airOS 8`), `p99 = 4.784 ms` (`-66.89%`), `0.0%` FP | `PASS` |
| **`443A`** | `<memorymaster-id>` (`155409`) | [`stage443a_ltu_11round_132window_champion_v9_receipt.json`](../artifacts/autoresearch/stage443a_ltu_11round_132window_champion_v9_receipt.json) | `rc.poststart_ltu_safe_champion.sh` (`v9`, `11` campañas / `132` ventanas, `0` `/dev/ame*`) | `PASS` |
| **`444A`** | `<memorymaster-id>` (`155410`) | [`stage444a_ground_up_and_ltu_v9_gate_receipt.json`](../artifacts/autoresearch/stage444a_ground_up_and_ltu_v9_gate_receipt.json) | Suite `test_stage439a_to_444a_suite.py` + `enforce_5pillar_research_gate.py` | `PASS` |

## 2. Hard Safety & Boundary Audit (`CONFIRMED`)
- **`.241`, `.242`, `.20`, `.250` untouched**: `True`
- **`/dev/ame*` character devices untouched on `198.18.0.63`**: `True`
- **All 6 Stage Docs `< 220` lines with paired `` / ``**: `True`
