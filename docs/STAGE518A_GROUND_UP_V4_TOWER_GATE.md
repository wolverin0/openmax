<!-- doc-head: Stage 518A Consolidated Verification & 5-Pillar Gate Check for Radar/DFS, DCXO Clock & Guarida v4 Queue (Stages 513A..518A) -->
Consolidates the verification receipts, SHA-256 digests, `< 220` line-count checks, strict `LF` shell checks, and `enforce_5pillar_research_gate.py --check-repo` compliance across `Stages 513A` through `518A`.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 518A — Consolidated Ground-Up Radar/DFS, `DCXO` `12X`, `Guarida v4` & 500-Stage Ledger Gate (`Stages 513A..518A`)

- **Epistemic Status**: `CONFIRMED` (`100%` pass across all 6 stage receipts, docs `< 220` lines, strict `LF` scripts, and `enforce_5pillar_research_gate.py --check-repo`)
- **Attribution**: `external controller` · `QCA firmware` · `proprietary airMAX/LTU module`
- **Verifier**: [`verify_stage518a_ground_up_v4_tower_gate.py`](../tools/verify/verify_stage518a_ground_up_v4_tower_gate.py)
- **JSON Receipt**: [`stage518a_ground_up_v4_tower_gate_receipt.json`](../artifacts/autoresearch/stage518a_ground_up_v4_tower_gate_receipt.json)

---

## 1. Consolidated Stage Summary (`Stages 513A..518A`)

| Stage | Deliverable & Scope | Key Quantitative Result | Doc Lines | Gate Status |
| :---: | :--- | :--- | :---: | :---: |
| **`513A`** | `fmx_qca988x_dfs_immunity_helper.sh` (`5250–5720 MHz` `FMX-DISC-24`) | `120 s` DFS CAC vs `45 s` Non-DFS watchdog + `nf_cal_period=1000` (`Stage 485A` `CSA` RE) | `33` | `PASS` |
| **`514A`** | `PBE-5AC-Gen2` `VHT40` Unlock & Triple-Play Exporter (`Stages 487A/488A`) | **`VHT40` `24.83 Mbps` (`0%` `64B`/`1472B` loss)** + VoIP loss under load **`13% -> 0%` (`-82.86%` `p50`)** | `28` | `PASS` |
| **`515A`** | `LTU` `DCXO` GPS vs Free-Running `TCXO` `4096-QAM` (`12X`) Pareto | **`+50.83%` goodput (`615.39` vs `408.0 Mbps`)**, **`100.0%` `12X` dwell** (`43` `dcxo` / `25` `tcxo` symbols) | `31` | `PASS` |
| **`516A`** | `fmx_guarida_full_tower_v4_master.sh` (`.60/.61` + `.84` + `.82` + `.83`) | Unifies `3` panels (`32` CPEs) + `.60<->.61` backbone (`+46.36 Mbps` joint goodput, `-70.14 ms` `p99`) | `28` | `PASS` |
| **`517A`** | 500-Stage Quantitative Architectural Breakthroughs Ledger | `6` breakthrough domains (`FMX-BRK-01..06`), **`820` live hardware windows**, `845+` JSON receipts | `32` | `PASS` |
| **`518A`** | Consolidated Verification & 5-Pillar Gate (`enforce_5pillar_research_gate.py`) | `compliant: True` (`0` failures across entire repo) | `< 60` | `PASS` |

---

## 2. Hard Safety & Topology Verification

- **Protected Bench Radios Untouched**: `198.18.0.45`, `198.18.0.46`, `198.18.0.43`, and `198.18.0.47` were **not** contacted (`0` packets sent).
- **Guarida Backbone (`SG-01`) & LTU `.110`**: `0` production writes performed; `/dev/ame*` on `.110` untouched.
