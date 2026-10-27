<!-- doc-head: STAGE492A_PBE5AC_PTP_MASTER_GATE.md preserved document content -->
<!-- /doc-head -->



# Stage 492A — `PowerBeam 5AC Gen2` (`.241 <-> .242`) Live PtP Master Verification Gate (`Stages 105A, 425A..430A, 487A..492A`)

## 1. Master Gate Scope
- Executes the consolidated `pytest` verification suite across all live `PowerBeam 5AC Gen2` PtP stages (`Stages 425A..430A` and `Stages 487A..491A`) plus the repository-wide 5-Pillar Research Gate (`tools/verify/enforce_5pillar_research_gate.py --check-repo`).
- Enforces:
  1. Presence and JSON schema integrity of all stage artifacts under `artifacts/autoresearch/`.
  2. Documentation line-count budget (`< 220` lines) and mandatory `` header across `docs/STAGE425A..430A.md` and `docs/STAGE487A..492A.md`.
  3. Live hardware invariants: `0.0%` full-MTU `1472B` packet loss in `PtP Champion v2`, `>20 Mbps` aggregate goodput (`20.58 Mbps` mean / `22.46 Mbps` peak), `>5 Mbps` UL goodput (`5.54 Mbps` mean / `7.23 Mbps` peak, beating Stock `airOS 8` TDMA's `3.60 Mbps` UL), and zero flash modifications during Pillar 1 RAM bind-mount canary testing.

---

## 2. Artifacts & Verification
- Gate Script: [`verify_stage492a_pbe5ac_ptp_master_gate.py`](../tools/verify/verify_stage492a_pbe5ac_ptp_master_gate.py)
- Receipt JSON: [`stage492a_pbe5ac_ptp_master_gate_receipt.json`](../artifacts/autoresearch/stage492a_pbe5ac_ptp_master_gate_receipt.json)
- Suite Test: [`test_stage487a_to_492a_suite.py`](../tests/test_stage487a_to_492a_suite.py)
