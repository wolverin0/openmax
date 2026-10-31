<!-- doc-head: STAGE1214A_BINARY_CONSTANTS_RECONCILIATION_POLL_TIMER_AND_PENALTY.md reconciles the two Stage 1187A unreconciled binary constants with doc line and binary provenance -->
# Stage 1214A Binary Constants Reconciliation: Poll Timer and Penalty

Status: CONFIRMED (offline, `live_devices_touched=false`). Evidence class `BINARY_CONSTANTS_RECONCILIATION`.
Code: `tools/re/reconcile_stage1187a_binary_constants_audit.py`. Test: `tests/test_stage1214a_constants.py`.
Receipt: `artifacts/verification/stage1214a_binary_constants_reconciliation.json`.

## Question
`docs/STAGE1187A_UBIQUITI_COMMUNITY_FORUM_M_AC_LTU_FIELD_ISSUES_AND_KO_ROOT_CAUSES.md` line 140 flags two unreconciled values. This stage reads the cited docs and the on-disk `.ko` files read-only.

## Value 1: missing-poll timer (30 s vs 1,800,000 ms)
- 30 s: `docs/STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md` line 45 ("~30 seconds", panic branch `.text+0x7c08` on 8.7.25, `0x7920` on 8.5.12); also `docs/STAGE12_HIDDEN_NODE_CROSSOVER_BOUNDARY_AUDIT.md` lines 14 and 24.
- 1,800,000 ms: `docs/STAGE70A_UBNT_POLL_AND_UPH_FULLREA_BINARY_DISSECTION.md` line 99 (UPH-BUG-01, callback `0x07bd8`, patch site `0x07c08`, "30 min").
- Units: 1,800,000 ms = 1800 s = 30 minutes, 60 times 30 s.
- Same code site: both patch `0x07c08` (`bnez` to `b`), so it is ONE constant with two incompatible values, not two timers.
- Different timers, kept apart: a 2000-jiffies (20 s) watchdog in `ubnt_poll_host_sta_bmiss_ind` (`docs/STAGE70A_UBNT_POLL_AND_UPH_FULLREA_BINARY_DISSECTION.md` line 61) and a 2 s beacon-miss path (`docs/STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md` line 152).
- Caveat: the 35 s outage survival at Stage 10 line 152 ran on the module patched at `0x7c08`, so it does not measure the unpatched timer.
- Binary check: in six `ubnt_poll_host.ko` builds the callback computes `(jiffies - uph_dev+0x288) * 1000` and panics at `>= 0x01c9c768` (30,001,000), about 30 s if jiffies are ms. The value `0x001b7740` (1,800,000) is absent as `lui/ori` immediate or raw word in all six.
- Result: `same_constant=True`; 30 s is better supported; the 30 min figure looks like a unit error. HZ scaling is inferred, not verified.
- Gap: `docs/STAGE10_11_COMPLETE_RE_AND_BENCH_ARCHIVE_20261021.md` has none of these values (recorded as `provenance_gap`).

## Value 2: `penaltyThreshold` (25 vs 60)
- 25: `docs/STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE_CONTINUATION_dfb5467f5c_002.md` line 139 (hand-written prose list).
- 60: `docs/STAGE249A_LTU_HARQ_RETRANSMISSION_AND_RATE_FSM_RE.md` line 20; `docs/STAGE1191A_LTU_MODULATION_ATPC_AND_DISCONNECT_STORM_RE.md` line 106 (`.data+0x12d2`); machine JSON `artifacts/firmware_re_xc_ltu/ubnt_poll_and_ltu_12x_deep_re_20261024.json` line 3100.
- Context: both are `ame_core.ko` of LTU 2.4.2 (afltu CPE and aflturocket AP), same unit (raw `.data` byte), so the same constant.
- Binary check: `.data` byte is `0x3c` = 60 in both builds (offsets `0x12d2` CPE, `0x12ee` AP).
- Result: `same_constant=True`; 60 confirmed; 25 is a transcription error in Stage 12 prose.

## Limits
- Static analysis only; no live behaviour shown. Doc cites are re-verified at run time; a miss becomes `provenance_gap`.
