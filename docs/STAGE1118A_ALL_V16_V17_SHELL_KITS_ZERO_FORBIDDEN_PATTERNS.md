<!-- doc-head: Stage1118A complete version-qualified shell-kit inventory and offline forbidden-command/line-ending audit -->
No kit is executed or modified and no device is contacted.
<!-- /doc-head -->

# Stage1118A — v16/v17 shell audit

The inventory includes every `.sh` file below `firmware/openwrt/` whose filename or directory contains an exact v16/v17 version token. Historical, backup and reproducibility copies remain in scope and are labelled separately. Missing any of the four known WA/PowerBeam v16/v17 kits fails the audit; an empty inventory cannot pass.

The audit reports executable literal `stat` and `tc` command positions, error-swallowing `|| true` commands, and raw CRLF endings. It distinguishes `/proc/PID/stat` data paths, comments, quoted diagnostic data and shell case labels from command invocations. Simple quoted executable names and `busybox stat` remain detectable.

Every current path and SHA256 is captured before and after the scan. Inventory or byte drift, unreadable/invalid UTF-8 files, empty/NUL-corrupt sources, unsupported shebangs and standalone carriage returns prevent a passing audit.

```powershell
python tools/verify/audit_stage1118a_all_v16_v17_shell_kits_zero_forbidden_patterns.py
```

The JSON stores the actual inventory, per-file findings, four exact counters and source bindings. No public tester kit, generic release manifest or live radio is changed.

Zero findings is a static detector result. Arbitrarily constructed command names, `eval`, every POSIX shell expansion and native applet availability are not certified. Quoted/heredoc diagnostic text is not counted as a command. A clean source audit does not prove native apply/readback/rollback or watchdog survival after SIGKILL.
