<!-- doc-head: Stage 1053A prepare-only, NOT executed 2-step OTA PtP rollout runbook (STA first, then AP) + 45s/120s rollback for PowerBeam/LiteBeam 5AC with v17 kits; offline, no live devices. -->
<!-- /doc-head -->
# Stage 1053A - production PtP OTA rollout runbook

Status: `RUNBOOK_NOT_EXECUTED`. Owner: Codex #1 (live lane). Prepared 100% offline by the
offline engineer. Nothing here was run, no device was touched, no pane was messaged.

## Flashing mandate (verbatim, project mandate)

> OTA: flash the remote STA FIRST with uci-defaults embedded in the custom SquashFS factory.bin (exact IP, disabled=0, SSID, freq, WPA2, wds=1, 24 dBm, stp=0, champion profile); then flash the local AP SECOND. Never bring a production radio to the local switch.

## Honest scope (read before use)

- PowerBeam has live in-range evidence but is `NOT_READY` (Stage 1009A).
- LiteBeam is `NO_EVIDENCE` in Stages 905A-956A (Stage 1009A). There is no LiteBeam data.
- PowerBeam and LiteBeam are NOT at parity. Do not extrapolate PowerBeam results to LiteBeam;
  LiteBeam needs its own controlled A/A and paired blocks before any rollout claim.
- This runbook proves nothing by itself. It is a checklist; acceptance comes only from the
  live lane's result receipt (below).

## Inputs

- v17 kits (Stages 1049A/1050A): `firmware/openwrt/common/fmx_wa_v17*.sh` (WA) and
  `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_pbe5ac_v17*.sh` (PtP PBE/LBE 5AC).
  Modes: `--dry-run` (default, writes nothing), `--apply`, `--verify`, `--rollback`;
  `--root DIR` is for offline emulation only, never on a device.
- Gate evidence: `tools/verify/verify_stage1054a_v17_pareto_kits_gate.py` must be CONFIRMED
  (`artifacts/autoresearch/stage1054a_v17_pareto_kits_gate_receipt.json`).
- Custom SquashFS factory.bin per radio with the uci-defaults embedded (see mandate).

## Measurement tools (live lane CALLS, never rewrites)

- `workloads/busybox_nc_uhttpd_bridge_sink_adapter.py` (Stage 1013A) - BusyBox sink adapter.
- `workloads/host_driven_triple_play_socket_probe.py` (Stage 1007A) - host-driven triple-play probe.
- `tools/qca988x/validate_wa_tcless_statless_profile_readback.py` (Stage 1014A) - profile readback.

## Two-step order

### Step 0 - pre-flight (per radio, both ends)

1. Confirm the Stage 1054A gate receipt is CONFIRMED and the kit hashes match what was gated.
2. Run the v17 kit `--dry-run` on the target and keep the plan output as evidence.
3. Run the readback-verify (`tools/qca988x/validate_wa_tcless_statless_profile_readback.py`) and
   record the pre-change profile. Abort on any mismatch or unreachable radio.
4. Confirm out-of-band access to both ends and that a rollback snapshot will exist.
5. Decide DFS vs non-DFS from the champion channel: rollback timer is 45 s (non-DFS) or
   120 s (DFS; CAC/re-association is slower).

### Step 1 - remote STA FIRST

1. Flash the remote STA with the custom SquashFS factory.bin (uci-defaults: exact IP,
   `disabled=0`, SSID, freq, WPA2, `wds=1`, 24 dBm, `stp=0`, champion profile).
2. Start the rollback timer (45 s non-DFS / 120 s DFS) before the radio reboots into the link.
3. Apply the v17 kit (`--apply`), then `--verify`; readback-verify the profile.
4. Cancel the timer only if the STA is reachable and readback matches. Otherwise let it fire.

### Step 2 - local AP SECOND

1. Only after Step 1 is verified. Flash the local AP the same way (same timer rule).
2. Never bring a production radio to the local switch; flash over the production path only.
3. Apply `--apply`, `--verify`, readback-verify; confirm the PtP link re-associates.
4. Run the measurement tools against the live link per the acceptance contract.

## Rollback checklist (45 s non-DFS / 120 s DFS)

- Trigger: timer expiry, failed `--verify`, readback mismatch, link not up, or any operator abort.
- Action: v17 kit `--rollback` on the affected end (STA first if both changed, since the AP
  carries management), then re-run readback-verify against the pre-change profile.
- Record: timer used, trigger, rollback exit code, post-rollback readback. A rollback is a valid,
  reportable outcome; it is not hidden or retried silently.
- Do not re-apply after a rollback without a new pre-flight.

## Acceptance (existing stats contract; the live lane CALLS it)

- `analysis/regression_gate/gatekeeper.py`: `OBJECTIVES` and `evaluate_paired()` with at least
  4 paired blocks. Do not edit or reimplement the gate.
- A/A negative control: Stage 886A must show the rig does not invent effects (`controlled_aa_valid`).
- Block count n comes from the Stage 977A minimum-detectable-effect (MDE) calculation.
- Multiplicity: Sidak-adjusted alpha across the evaluated objectives.
- Zero false positives required; an unsupported claim is reported as not accepted.

## result_receipt_contract

The live lane writes `artifacts/autoresearch/stage<N>_live_ptp_ota_rollout_result.json` with keys:

- `controlled_aa_valid` (bool) - A/A control passed (Stage 886A).
- `physical_workload_acceptance` (bool/verdict) - from `evaluate_paired()` on physical workloads.
- `zero_false_positive` (bool) - no false-positive claim.
- `evidence_provenance_class` (string) - e.g. live-physical vs offline-synthetic; never blur them.

Also record per radio: model (PowerBeam or LiteBeam, separately), timer used, rollback taken or not.

## Non-goals

No execution here, no ssh, no messaging any lane, no edits to lane-owned files, no claim of
LiteBeam readiness, no claim of PowerBeam readiness (`NOT_READY`).
