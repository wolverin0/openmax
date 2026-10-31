<!-- doc-head: Stage 1101A PtP production cutover + emergency rollback checklist (v17 kit, STA-first OTA, watchdog); prepare-only, CHECKLIST_NOT_EXECUTED, owner Codex #1 live lane; integrates 1049A..1100A by reference -->
# Stage 1101A - PtP production cutover zero-touch checklist

Status: `CHECKLIST_NOT_EXECUTED`. Owner: Codex #1 (live lane). Authored 100% offline; no device touched.
No readiness value is asserted anywhere in this document. Receipt:
`artifacts/autoresearch/stage1101a_ptp_production_cutover_zero_touch_checklist.json`.

References only (do not restate): runbook `docs/STAGE1053A_PRODUCTION_PTP_OTA_ROLLOUT_RUNBOOK.md`,
kit `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_pbe5ac_v17_pareto_aqm_aql_busybox_kit.sh` (1049A),
canary verifier (1097A), its self-test (1098A), watchdog (1099A), restricted-PATH test (1100A).

## Flashing mandate (verbatim)

> OTA: flash the remote STA FIRST with uci-defaults embedded in the custom SquashFS factory.bin (exact IP, disabled=0, SSID, freq, WPA2, wds=1, 24 dBm, stp=0, champion profile); then flash the local AP SECOND. Never bring a production radio to the local switch.

## Ordered cutover steps

1. Pre-flight (read-only).
   - Kit: `fmx_pbe5ac_v17_pareto_aqm_aql_busybox_kit.sh --dry-run` (writes nothing).
   - Canary: `tools/autoresearch/ptp_canary_pre_and_post_flight_verifier.py --role pre` (1097A).
   - Stop on any non-zero exit or non-matching baseline.
2. OTA, STA first, AP second, per the mandate above.
   - STA: custom SquashFS `factory.bin` with embedded uci-defaults, see `firmware/openwrt/pbe5ac_gen2_ptp_kit/pbe5ac_remote_ota_prebaked_manifest_20261026.json`.
   - AP: flashed only after the STA is up with the exact IP.
3. Apply.
   - Kit: `fmx_pbe5ac_v17_pareto_aqm_aql_busybox_kit.sh --apply`.
4. Arm watchdog (1099A).
   - `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_ptp_rollback_watchdog_v17.sh --arm` (non-DFS).
   - `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_ptp_rollback_watchdog_v17.sh --arm --dfs` (DFS channel).
   - Snapshot name: `fmx-pbe5ac-v17-snapshot`.
5. Post-flight (1097A).
   - `tools/autoresearch/ptp_canary_pre_and_post_flight_verifier.py --role post`.
   - Compare against the `--role pre` capture; any regression triggers step 6.
6. Emergency rollback.
   - Manual: `fmx_pbe5ac_v17_pareto_aqm_aql_busybox_kit.sh --rollback`.
   - Automatic: watchdog auto-rollback after 45 s (non-DFS) or 120 s (DFS) of lost link.

## Open decisions (listed, NOT resolved here)

- `aql_threshold`: 24000 (champion) vs 12000 (v17 kit). Operator/Codex #1 to decide.
- LiteBeam PtP: `NO_EVIDENCE` (1009A); not equivalent to PowerBeam (`NOT_READY`).
- `common/SHA256SUMS` re-sign pending Codex #2 (not touched here).
- v17 kits are runtime-only: re-apply or bake into the image after a reboot.

## Boundaries

- This checklist executes nothing. Live execution belongs to Codex #1.
- Gate: `tools/verify/verify_stage1102a_ptp_canary_and_watchdog_v17_gate.py`.
