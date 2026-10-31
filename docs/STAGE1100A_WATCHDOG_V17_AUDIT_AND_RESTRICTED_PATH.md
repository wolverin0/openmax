<!-- doc-head: Stage 1100A | watchdog v17 audit + restricted-PATH harness | audit_text 0 findings, 0 masked failures, poison stubs | WATCHDOG_V17_AUDIT | offline -->
# Stage 1100A - Watchdog v17 audit and restricted-PATH proof

Audited: `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_ptp_rollback_watchdog_v17.sh` (Stage 1099A).
Test: `tests/test_stage1100a_watchdog_v17_restricted_path.py`. Receipt: `artifacts/autoresearch/stage1100a_watchdog_v17_audit_and_restricted_path.json`.
Builder: `tools/verify/build_stage1099a_1100a_watchdog_v17_receipts.py`.

## Static audit
- `audit_text` from `tools/verify/audit_stage1025a_shell_kits_busybox_applet_compatibility.py`: 0 findings (integer ping is clean; only fractional `-i 0.x` is flagged).
- `grep -c '|| true\||| :'` is 0; 0 CR bytes; `sh -n` clean.

## Restricted-PATH harness
Reuses the Stage 1051A shell discovery (`C:\Program Files\Git\...\sh.exe` first, trap-validated, skip if none) and poison stubs
(`stat`, `tc`, `timeout`, `seq`, `usleep`; any call writes the marker and exits 127). A fake `--root` holds a stock-valued snapshot with a correct md5 manifest and a champion-valued live tree.
- Peer up (`FMX_PING_RESULT=0`): exit 0, no writes.
- Two failed iterations (`1`, window 2): exit 1, 10 re-emitted writes restore the stock values.
- Single blip (`1 0`) and `1 0 1 0`: no rollback (debounce).
- Corrupt manifest (tampered file or missing manifest): `--rollback` and `--arm` exit non-zero, trace empty, tree byte-identical (verify-before-restore).
- Manual `--rollback` restores; the poison marker stays empty in every case.

Not checked: real BusyBox on a radio; real `ping`/`uci`/`wifi`.
