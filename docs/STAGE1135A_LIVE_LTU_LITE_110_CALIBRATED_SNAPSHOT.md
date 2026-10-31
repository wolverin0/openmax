<!-- doc-head: Stage1135A one bounded LTU-Lite passive SSH attempt and explicit uncalibrated-readiness limits -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage1135A LTU-Lite passive snapshot

The collector targets only `198.18.0.63`, account `ubnt`, using the credential explicitly supplied for this wave. It permits one password authentication attempt and no fallback account, old password or key search.

The actual attempt on 2026-10-27 returned `AuthenticationException`: the supplied password was rejected. Zero remote commands and zero native snapshots were executed. The transport and local socket were closed. Status: `BLOCKED_ACCESS`.

The pending read-only program contains only board/version identity, boot/uptime and reads of `/proc/stat`, `/proc/interrupts`, `/proc/net/dev`, `/proc/loadavg` and `/proc/meminfo`. It contains no upload, configuration write, active workload, ioctl or proprietary device-node access. No `/dev/ame*` node is opened.

The requested calibrator path was absent. A thin pure adapter at `tools/ltu/ltu_lite_passive_threshold_calibrator.py` reuses Stage1116's strict identity, epoch, counter and clock evaluator, adding load-average and memory diagnostics. It does not connect to a radio.

At least two complete snapshots are required for a passive interval. Even successful collection would leave production thresholds, labelled false-positive calibration, application goodput and causal RF diagnoses unvalidated. No saved Stage1023 snapshot substitutes for the failed fresh attempt.

The exact native attempt, executed collector source and command-program SHA256 are retained under `artifacts/verification/stage1135a/`. Credentials are process-only and are absent from receipts and logs.

The named `calibrated_snapshot` output is a requested filename, not a claim that calibration succeeded. Readiness remains blocked.

[Receipt](../artifacts/verification/stage1135a_live_ltu_lite_110_calibrated_snapshot.json) · [Collector](../tools/autoresearch/run_stage1135a_live_ltu_lite_110_passive_snapshot.py) · [Adapter](../tools/ltu/ltu_lite_passive_threshold_calibrator.py)
