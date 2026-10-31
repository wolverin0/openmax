<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: Stage 1083A - PREPARE-ONLY operator dossier for a PowerBeam/LiteBeam PtP OTA rollout and Guarida Panel2 prerequisites; DOSSIER_NOT_EXECUTED; LiteBeam NO_EVIDENCE; PowerBeam NOT_READY; owner Codex #1 live lane -->
# Stage 1083A - PtP LB/PB and Guarida Panel2 rollout dossier

Status: `DOSSIER_NOT_EXECUTED`. Offline authoring only. Nothing here was run on a device.
Owner of any execution: Codex #1 (live lane). Receipt: `artifacts/autoresearch/stage1083a_ptp_lb_and_guarida_panel2_rollout_dossier.json`.

## 0. Honest readiness (read first)
- PowerBeam PtP (.241 <-> .242): `NOT_READY` (Stage 1009A, 1077A).
- LiteBeam PtP: `NO_EVIDENCE`. The LiteBeam half of the link has NO controlled evidence yet (Stage 1009A/1077A).
  LiteBeam is NOT equivalent to PowerBeam; no PowerBeam result may be transferred to it.
- Guarida Panel2: Stage 882A shows `ready=false` on all endpoints.
- No verdict in this wave equals PRODUCTION_READY. Do not infer it from this dossier.

## 1. Open operator decision
- `aql_threshold` discrepancy: 24000 in the champion profile vs 12000 in the v17 kit. OPEN, operator decides before any flash.
  Do not silently pick one. Record the choice in the live receipt.

## 2. Pre-flight (all must be true before step 3)
- Both radios reachable from the operator host; record model, firmware, MAC, current IP (`stage1015a_powerbeam_ptp_241_242_retest_spec.json`).
- Runbook reviewed: `stage1053a_production_ptp_ota_rollout_runbook.json`.
- Kits at hand: `stage1049a_pbe5ac_v17_pareto_aqm_aql_busybox_kit.json`, `stage1050a_wa_v17_pareto_aqm_aql_busybox_kit.json`, champion `firmware/openwrt/common/99-fmx-wa-universal-champion-v17`.
- Custom SquashFS factory.bin built per side with embedded uci-defaults; sha256 recorded; fail-closed SquashFS gate passed (Stage 983A-988A).
- `aql_threshold` decision recorded (section 1).
- A maintenance window and a physical fallback person exist. Channel is classified DFS or non-DFS (sets the watchdog, section 5).
- Baseline capture taken before any change (same load profile as the retest).

## 3. Two-step OTA conversion
Mandate, verbatim:
"OTA: flash the remote STA FIRST with uci-defaults embedded in the custom SquashFS factory.bin (exact IP, disabled=0, SSID, freq, WPA2, wds=1, 24 dBm, stp=0, champion profile); then flash the local AP SECOND. Never bring a production radio to the local switch."
1. Step 1: flash the remote STA first (embedded uci-defaults as above).
2. Step 2: flash the local AP second.
3. Verify the link re-forms from the STA side before leaving the site; do not bench-configure a production radio.

## 4. v17 kit deployment
- v17 kits are RUNTIME-ONLY (no persistence). Runtime writes do NOT survive a reboot.
- After ANY reboot: re-apply the v17 kit, or bake it into the SquashFS. Treat a rebooted radio as unconverted until verified.
- Apply the kit on the AP and STA, then run the 1007A probe (section 7).

## 5. Rollback and autonomous watchdog
- Manual rollback: the v17 kit `--rollback` flag.
- Autonomous rollback watchdog: 45 s on non-DFS channels, 120 s on DFS channels (DFS needs the longer window for CAC/relock).
- Arm the watchdog BEFORE the change; disarm only after the link and the probe pass.
- If the link does not return inside the window, the watchdog reverts without operator action; then escalate.

## 6. Guarida Panel2 prerequisites (22 CPEs)
- Stage 882A: `ready=false` on all endpoints. Nothing is cleared.
- Gate: the <memorymaster-id> AP-local 2-consecutive-round confirmation (2 x 5 probes). Both rounds must pass back to back.
- Panel2 was not audited by 1010A. Panel3 remains `NO_EVIDENCE`.
- Passing the gate does not equal PRODUCTION_READY; it only permits the next staged step.

## 7. Measurement tools
- 1013A adapter: converts raw load output into a controlled receipt input.
- 1007A probe: the on-air probe run per round.
- 1014A validator: validates the receipt shape and thresholds.
- 1073A provenance bundler: `tools/autoresearch/ptp_cohort_provenance_and_gatekeeper_bundler.py` bundles the evidence with provenance.

## 8. result_receipt_contract
Every live result receipt must carry:
- `controlled_aa_valid`
- `physical_workload_acceptance`
- `zero_false_positive`
- `evidence_provenance_class`
A missing key, or a synthetic fixture, invalidates the result.

## 9. Not covered
No live action, no SSH, no flashing, no SHA256SUMS edits. LiteBeam needs its own controlled evidence run first.
