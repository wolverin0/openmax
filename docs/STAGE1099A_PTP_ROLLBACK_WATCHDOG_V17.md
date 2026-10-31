<!-- doc-head: Stage 1099A | PtP rollback watchdog v17 | statless tcless BusyBox sh | 2-consecutive-fail debounce, verify-manifest-before-restore, UCI self-export | STATLESS_TCLESS_ROLLBACK_WATCHDOG | offline -->
# Stage 1099A - PtP rollback watchdog v17

Script: `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_ptp_rollback_watchdog_v17.sh`.
Receipt: `artifacts/autoresearch/stage1099a_ptp_rollback_watchdog_v17.json`. Builder: `tools/verify/build_stage1099a_1100a_watchdog_v17_receipts.py`.
The three older watchdogs (`fmx_ptp_rollback_watchdog.sh`, `_ap_241.sh`, `_sta_242.sh`) and every `SHA256SUMS` are untouched.

## Usage
- `--arm --peer HOST`: reuses a valid snapshot or takes one, exports UCI, then monitors for 45 s (`--dfs` 120 s, `--watchdog-seconds N` overrides).
- `--rollback`: restores the snapshot now.
- Common: `--root DIR`, `--iface IF`, `--phy NAME`. Hook: `FMX_WRITE_TRACE=FILE`.
- TEST-ONLY: `FMX_PING_RESULT` (0 peer answered, 1 failed; a space list is consumed one per iteration). Never set on a radio.
- Exit codes: 0 link held, 1 rolled back cleanly, 2 rollback failed. Manual `--rollback`: 0 ok, 2 failed, 3 snapshot invalid.

## Snapshot path
Snapshot dir is `/etc/fmx-pbe5ac-v17-snapshot/` (hyphen), as written by `fmx_pbe5ac_v17_pareto_aqm_aql_busybox_kit.sh`.
The directive's `fmx-pbe5ac-v17.snapshot` (dot) was a typo; using it would make rollback miss the snapshot.

## Behaviour
- Debounce: one `ping -c 3 -W 2 HOST` per iteration (integer flags only), then `sleep 1`. Rollback fires only after TWO CONSECUTIVE failed iterations. fail/ok/fail/ok never rolls back.
- Verify before restore: `(cd "$SNAP" && md5sum -c manifest)` must pass. If it fails, nothing is written and the exit is non-zero.
- Restore re-emits writes (`aql` rows as `idx low high` x4, `aqm` RW lines as `fq_xxx N` x3, cat-back of `thr`, `lowat`, `qdisc`), never `cp` onto debugfs, then reads back aql and thr.
- UCI self-export: the v17 kit saves no UCI state, so `--arm` runs `uci export wireless` into `uci-wireless.export` (outside the md5 manifest). Restore does `uci import`, `uci commit wireless`, `wifi reload`.
  Without the export it prints `UCI_RESTORE_SKIPPED_NO_EXPORT`. Under a non-empty `--root`, uci and wifi are skipped with a trace line.
- `set -u` only, never `set -e`: each failure is checked explicitly so a failed write cannot abort a restore midway. No `|| true`.
- No `stat`, `tc`, `timeout`, `seq`, `usleep`; the window counts loop iterations (shortcut: a failing ping burst can stretch the real window).

Not checked: a real radio (offline only); real `ping`, `uci`, `wifi` behaviour.
