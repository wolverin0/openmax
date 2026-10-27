<!-- doc-head: STAGE570A_LIVE_WA_256WINDOW_V10_GATE.md preserved document content -->
<!-- /doc-head -->



# Stage 570A — Consolidated `256`-Window `WA v10` Verification & 5-Pillar Gate

- **Claim Classification**: `CONFIRMED`
- **Subsystem Attribution**: `QCA firmware`, `ath10k`, `mac80211`, `Linux`, `hardware` (`AR9342` + `QCA9882`)
- **Gate Verdict**: **`PASS` (`compliant: true`, `6/6` receipts verified, `6/6` docs `< 220` lines)**

---

## 1. Audited Receipts (`Stages 565A..570A`)

| Stage | Receipt | Status | 5-Pillar Gate |
| :--- | :--- | :--- | :--- |
| **`Stage 565A`** | [`stage565a_live_wa_pb050_v2_and_pacing_r57_59.json`](../artifacts/autoresearch/stage565a_live_wa_pb050_v2_and_pacing_r57_59.json) | `CONFIRMED` (`240` win) | `PASS` |
| **`Stage 566A`** | [`stage566a_live_wa_256window_milestone_r60_63.json`](../artifacts/autoresearch/stage566a_live_wa_256window_milestone_r60_63.json) | `CONFIRMED` (`256` win) | `PASS` |
| **`Stage 567A`** | [`stage567a_live_wa_mk1_251_e2e_v10_milestone.json`](../artifacts/autoresearch/stage567a_live_wa_mk1_251_e2e_v10_milestone.json) | `CONFIRMED` (`S567A-E2E-R6`) | `PASS` |
| **`Stage 568A`** | [`stage568a_live_panel1_guarida_84_v10_rollout_audit.json`](../artifacts/autoresearch/stage568a_live_panel1_guarida_84_v10_rollout_audit.json) | `CONFIRMED` (`0` RF drops) | `PASS` |
| **`Stage 569A`** | [`stage569a_cumulative_63round_256window_wa_champion_v10.json`](../artifacts/autoresearch/stage569a_cumulative_63round_256window_wa_champion_v10.json) | `CONFIRMED` (`63` rounds) | `PASS` |
| **`Stage 570A`** | [`stage570a_live_wa_256window_v10_gate_receipt.json`](../artifacts/autoresearch/stage570a_live_wa_256window_v10_gate_receipt.json) | `CONFIRMED` | `PASS` |

---

## 2. Verification Suite

- Gate Runner: [`verify_stage570a_live_wa_256window_v10_gate.py`](../tools/verify/verify_stage570a_live_wa_256window_v10_gate.py)
- Consolidated Pytest Suite: [`test_stage565a_to_570a_wa_256window_v10.py`](../tests/test_stage565a_to_570a_wa_256window_v10.py)
