<!-- doc-head: STAGE634A_LIVE_WA_284WINDOW_V11_GATE.md preserved document content -->
<!-- /doc-head -->



# Stage 634A — Consolidated `284`-Window `WA v11` Verification & 5-Pillar Gate

- **Claim Classification**: `CONFIRMED`
- **Subsystem Attribution**: `QCA firmware`, `ath10k`, `mac80211`, `Linux`, `hardware` (`AR9342` + `QCA9882`)
- **Gate Verdict**: **`PASS` (`compliant: true`, `6/6` receipts verified, `6/6` docs `< 220` lines)**

---

## 1. Audited Receipts (`Stages 629A..634A`)

| Stage | Receipt | Status | 5-Pillar Gate |
| :--- | :--- | :--- | :--- |
| **`Stage 629A`** | [`stage629a_live_wa_pb050_v3_and_sgi_guard_r64_66.json`](../artifacts/autoresearch/stage629a_live_wa_pb050_v3_and_sgi_guard_r64_66.json) | `CONFIRMED` (`268` win) | `PASS` |
| **`Stage 630A`** | [`stage630a_live_wa_70round_284window_milestone_r67_70.json`](../artifacts/autoresearch/stage630a_live_wa_70round_284window_milestone_r67_70.json) | `CONFIRMED` (`284` win) | `PASS` |
| **`Stage 631A`** | [`stage631a_live_wa_mk1_251_e2e_v11_milestone.json`](../artifacts/autoresearch/stage631a_live_wa_mk1_251_e2e_v11_milestone.json) | `CONFIRMED` (`S631A-E2E-R7`) | `PASS` |
| **`Stage 632A`** | [`stage632a_live_panel1_guarida_84_v11_20h_audit.json`](../artifacts/autoresearch/stage632a_live_panel1_guarida_84_v11_20h_audit.json) | `CONFIRMED` (`0` RF drops) | `PASS` |
| **`Stage 633A`** | [`stage633a_cumulative_70round_284window_wa_champion_v11.json`](../artifacts/autoresearch/stage633a_cumulative_70round_284window_wa_champion_v11.json) | `CONFIRMED` (`70` rounds) | `PASS` |
| **`Stage 634A`** | [`stage634a_live_wa_284window_v11_gate_receipt.json`](../artifacts/autoresearch/stage634a_live_wa_284window_v11_gate_receipt.json) | `CONFIRMED` | `PASS` |

---

## 2. Verification Suite

- Gate Runner: [`verify_stage634a_live_wa_284window_v11_gate.py`](../tools/verify/verify_stage634a_live_wa_284window_v11_gate.py)
- Consolidated Pytest Suite: [`test_stage629a_to_634a_wa_284window_v11.py`](../tests/test_stage629a_to_634a_wa_284window_v11.py)
