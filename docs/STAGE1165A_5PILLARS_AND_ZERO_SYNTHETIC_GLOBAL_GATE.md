<!-- doc-head: Stage 1165A global gate: 5-pillar repo check, broken-link re-audit via the 1001A tool, zero-synthetic scan of artifacts JSON; sub-check results reported as measured -->
# Stage 1165A - 5-pillar and zero-synthetic global gate

Evidence class: FIVE_PILLAR_AND_ZERO_SYNTHETIC_GLOBAL_GATE (offline, no devices touched).

- gate_status: PASS (PASS iff 5-pillar rc 0, broken links 0 and no synthetic leak in Wave 22 receipts)
- 5-pillar `--check-repo`: rc 0
- broken links after (1001A tool; `audit_broken_links_and_supersession.py` does not exist): 0, tool rc 0
- synthetic_leak_count: 0 in 0 files; wave22_receipts_clean: true
- Pre-existing hits outside Wave 22 receipts are other-lane and listed in the receipt, not edited here.

Builder: `tools/verify/enforce_5pillar_and_zero_synthetic_global_gate_1165a.py`
Receipt: `artifacts/verification/stage1165a_5pillars_and_zero_synthetic_global_gate.json`
