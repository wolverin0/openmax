<!-- doc-head: Stage 1025A static BusyBox applet compatibility audit of firmware shell kits (< 180 lines) -->
Offline static audit of all 101 `firmware/**/*.sh` for applets the 8 MB OpenWrt BusyBox radios do not ship. Reports real CRITICAL findings in the WA and LTU field kits.
<!-- /doc-head -->

# Stage 1025A: shell kits vs BusyBox applet set

- **Status**: `CONFIRMED` means the audit completed. It does not mean zero findings.
- **Auditor**: `tools/verify/audit_stage1025a_shell_kits_busybox_applet_compatibility.py`
- **Tests**: `tools/verify/test_audit_stage1025a_shell_kits_busybox_applet_compatibility.py`
- **Receipt**: `artifacts/autoresearch/stage1025a_shell_kits_busybox_applet_compatibility.json`
- **Claim id**: `FMX-STAGE1025A-BUSYBOX-APPLET-AUDIT`
- **Attribution**: external controller (offline static audit); `live_devices_touched=false`
- **Provenance of the allowlist**: OpenWrt 24.10 BusyBox default applet set plus binaries observed in Stage 953A/929A (`nc`, `awk`, `dd`, `ping`, `wget`, `sh`, `cat`). This is not a literal applet-list capture from a device.

## 1. Forbidden set

`stat`, `timeout`, `usleep`, `seq`, `tc`, `iperf3`, `python`/`python3`, and fractional `ping -i` (for example `-i 0.2`, `-i0.2`, `-i .5`). Integer `ping -i 1` is allowed.

## 2. Static-match discipline

- Comments, quoted-string contents and heredoc bodies are blanked before matching. `$( ... )` inside double quotes stays visible because it is code.
- An applet only counts in command position: line start, or after `|`, `;`, `&`, `(`, `$(`, backtick, `{`, `!`, `then`, `do`, `else`, `if`, `while`, `until`, `exec`, `command`, `env`, `time`, `nohup`, `busybox`. Path forms `/usr/bin/<name>` and `/bin/<name>` match too.
- `case` labels such as `auto|tc|sysfs)` and `tc) ...` are not commands and are skipped.
- No hit for `tc` in `/etc/config`, `fq_codel ... target`, `tc-optional`, or `seq` in `sequence`. `command -v tc` is a probe and is not flagged.
- Known limits: backtick substitutions inside double quotes are blanked; `ping -i "0.2"` (quoted value) is missed.

## 3. Severity by intended target

| Target class | Rule | Severity |
| :--- | :--- | :---: |
| `RADIO_FIELD_KIT` | `firmware/openwrt/common/*field_kit.sh` (runs on the radio) | `CRITICAL` |
| `PBE5AC_GEN2_PTP_KIT` | path contains `pbe5ac_gen2_ptp_kit/` | `INFO` |
| `IMAGE_BAKE` | path contains `bake` or `image` | `INFO` |
| `HOST_SIDE` | `#!/bin/bash` shebang, or text references `python3` or `ssh` | `INFO` |
| `UNCLASSIFIED` | target cannot be inferred (for example `firmware/ltu_safe_kit/`) | `WARNING` |

The heuristic never invents a target. Unclassified scripts get `WARNING` rather than a guessed class. `ok` in `audit_text` is false only for `CRITICAL` or `WARNING` findings.

## 4. Results

| Metric | Value |
| :--- | :---: |
| Scripts scanned | `101` |
| Scripts with findings | `14` |
| Findings total | `35` |
| Scripts with `CRITICAL` | `4` |
| Findings by applet | `tc` 21, `stat` 14 |
| Findings by severity | `CRITICAL` 16, `INFO` 15, `WARNING` 4 |

No `timeout`, `usleep`, `seq`, `iperf3`, `python` or fractional `ping` hit exists in any firmware `.sh` today.

## 5. Flagged kits

| Script | Class | Applets (count) | Severity |
| :--- | :--- | :--- | :---: |
| `firmware/openwrt/common/fmx_wa_v13_344window_field_kit.sh` | `RADIO_FIELD_KIT` | `stat` 2, `tc` 2 | `CRITICAL` |
| `firmware/openwrt/common/fmx_wa_v14_356window_field_kit.sh` | `RADIO_FIELD_KIT` | `stat` 2, `tc` 2 | `CRITICAL` |
| `firmware/openwrt/common/fmx_wa_v15_368window_field_kit.sh` | `RADIO_FIELD_KIT` | `stat` 2, `tc` 2 | `CRITICAL` |
| `firmware/openwrt/common/fmx_ltu_v21_276window_field_kit.sh` | `RADIO_FIELD_KIT` | `tc` 4 | `CRITICAL` |
| `firmware/ltu_safe_kit/fmx_ltu_runtime_transaction.sh` | `UNCLASSIFIED` | `stat` 2, `tc` 2 | `WARNING` |
| `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_pbe_lbe_runtime_transaction.sh` | `PBE5AC_GEN2_PTP_KIT` | `stat` 2, `tc` 2 | `INFO` |
| `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_ptp_rollback_watchdog.sh` | `PBE5AC_GEN2_PTP_KIT` | `stat` 4 | `INFO` |
| `wa_champion_openwrt_body.sh` and `99-fmx-wa-universal-champion.public.sh` copies under `firmware/openwrt/pbe5ac_gen2_ptp_kit/` (6 files) | `PBE5AC_GEN2_PTP_KIT` | `tc` 1 each | `INFO` |

## 6. Interpretation

- The WA v13/v14/v15 field kits call `tc qdisc replace ... fq_codel` and `stat -c '%u:%a:%h'` for snapshot metadata. Neither `tc` nor `stat` is in the BusyBox default set assumed for the 8 MB radios, so these are real incompatibilities, not noise.
- The WA kits guard the `tc` backend with `command -v tc` at one site (backend selection), but the later `tc` calls are still reachable in `tc` mode and are reported. The audit does not judge whether a runtime guard makes them safe.
- `fmx_ltu_v21_276window_field_kit.sh` uses `tc` four times with no applet probe seen by the matcher.
- Kits owned by other lanes were read only. No `.sh` was edited.
- The Stage 1030A gate calls `audit_text(text, script_name)` and `audit_firmware(firmware_dir=None)` from the auditor module.

## 7. Public API

- `audit_text(text: str, script_name: str) -> dict` returns `{script, target_class, findings:[{applet, line, snippet, severity}], ok}`.
- `audit_firmware(firmware_dir=None) -> dict` returns `{scripts_scanned, scripts_with_findings, findings_total, scripts_with_critical, findings_by_applet, per_script}` plus `findings_by_severity` and `clean_scripts`. Default directory is `<repo>/firmware`.

## 8. Reproduce

- `python -m pytest tools/verify/test_audit_stage1025a_shell_kits_busybox_applet_compatibility.py -q`
- `python tools/verify/audit_stage1025a_shell_kits_busybox_applet_compatibility.py` (rewrites the receipt; read-back self-check rejects an all-NUL file, 3 attempts)

## 9. Test coverage

- Positive fixture: `stat -c %s f`, `timeout 5 cmd`, `usleep 200`, `seq 1 5`, `tc qdisc replace`, `iperf3 -c`, `python3 -`, `ping -i 0.2` give all 8 applets.
- Negative fixture: `/etc/config/network`, `fq_codel target 5ms` in a string, comments, heredoc body, `case` labels, `sequence`, `tc-optional`, `command -v tc`, `ping -i 1` give zero findings.
