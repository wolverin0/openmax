<!-- doc-head: Stage 1015A PowerBeam PtP .241/.242 retest spec; SPEC ONLY, offline, not executed, not a readiness claim -->
<!-- /doc-head -->
# Stage 1015A PowerBeam PtP .241-.242 retest spec

Receipt: `artifacts/autoresearch/stage1015a_powerbeam_ptp_241_242_retest_spec.json`. Builder: `tools/verify/build_stage1015a_to_1017a_retest_specs.py`.
Status CONFIRMED = spec authored. Nothing here was executed; no key equals PRODUCTION_READY.
Owner: Codex #1 (live lane). Execution status: `SPEC_ONLY_NOT_EXECUTED`.

## Target and source readiness
- Target: PtP PowerBeam 5AC Gen2 .241 (AP) <-> .242 (STA)
- `from_1009A`: {"verdict": "NOT_READY", "receipt": "stage1009a_ptp_powerbeam_litebeam_production_readiness_audit.json", "signals_906A": "controlled_aa_valid=ABSENT, zero_loss_confirmed=false, A/A gate reasons ['Invalid baseline health/loss']", "signals_931A": "status=BLOCKED_PRECONDITIONS, acceptance=NOT_ACCEPTED"}
- `from_1011A`: stage1011a_real_production_readiness_rollup_matrix.json (production_ready_count=0)

## Cited queue rows (from `stage1004a_pending_live_retest_queue.json`)
| rank | receipt | score | suggested measurement |
|---|---|---|---|
| 31 | `stage699a_pbe5ac_ptp_complete_evolution_ledger_v4.json` | 6 | counterbalanced iperf goodput windows (>=4 rounds), champion vs baseline |
| 20 | `stage522a_pbe5ac_lbe5ac_vht40_25mbps_field_rollout_validator.json` | 7 | counterbalanced iperf goodput windows (>=4 rounds), champion vs baseline |
| 21 | `stage514a_pbe5ac_triple_play_and_vht40_telemetry_exporter.json` | 7 | counterbalanced iperf goodput windows (>=4 rounds), champion vs baseline |
| 41 | `stage549a_pbe5ac_lbe5ac_ptp_ptmp_unified_field_installer_v3.json` | 6 | counterbalanced iperf goodput windows (>=4 rounds), champion vs baseline |
| 60 | `stage701a_pbe5ac_vht40_25mbps_pb050_field_kit.json` | 4 | counterbalanced iperf goodput windows (>=4 rounds), champion vs baseline |
| 113 | `stage489a_live_pbe5ac_bidirectional_end_to_end_via_mk1_251.json` | 2 | counterbalanced iperf goodput windows (>=4 rounds), champion vs baseline |

## Measurement tools
- `workloads/busybox_nc_uhttpd_bridge_sink_adapter.py`
- `tools/qca988x/validate_wa_tcless_statless_profile_readback.py`
- `workloads/host_driven_triple_play_socket_probe.py`
both radios are 8 MB: NO iperf3. TCP sink/source via the 1013A BusyBox nc/dd adapter; bridge mode via 1007A host-driven probe. 1013A radio roles are UNAVAILABLE unless the capability probe confirms the BusyBox applets; then the stage is reported BLOCKED, not faked.

## Preconditions
| id | precondition | source |
|---|---|---|
| 1 | Resolve 906A 'Invalid baseline health/loss': acquire a zero-loss IDLE baseline (>=100 ICMP probes each direction, 0 lost; N spec-chosen) BEFORE any load | `stage906a_live_powerbeam_loss_diagnosis_and_aa.json` |
| 2 | Clear 931A BLOCKED_PRECONDITIONS blockers: NATIVE_AUTONOMOUS_ROLLBACK_PROOF_FAILED_OR_MISSING, HISTORICAL_906_AA_FAILED_ZERO_LOSS_ADMISSION, NEW_CAMPAIGN_AA_NOT_ACQUIRED, NO_REVIEWED_RESTORER_FOR_AQL_AND_TCP_NOTSENT_LOWAT | `stage931a_live_powerbeam_aql_notsent_holdout.json` |
| 3 | If no reviewed restorer exists for AQL/tcp_notsent_lowat the lane must NOT change them; report BLOCKED | `stage931a_live_powerbeam_aql_notsent_holdout.json` |
| 4 | BusyBox capability probe on both radios parsed by parse_capability_probe(); nc -l/-p and dd confirmed | `workloads/busybox_nc_uhttpd_bridge_sink_adapter.py` |
| 5 | Operator approval + exclusive RF window for the link; passive pre-snapshot of both radios | `AGENTS.md operator gates` |
| 6 | Any reflash follows the flashing_mandate below (STA first, AP second) | `flashing_mandate` |

## Procedure
- 1. Verify preconditions P1-P6; stop and write a BLOCKED result if any fails.
- 2. Run the 1013A capability probe on .241 and .242; record applet support.
- 3. Idle zero-loss baseline (P1) -> raw capture + sha256.
- 4. Pre-register objective, m, n (stats_contract) in the result receipt before acquiring data.
- 5. A/A negative control: >=2 measured runs, validated by validate_aa_campaign() (886A); same config both arms.
- 6. A/B: n=12 paired blocks, A=stock-OpenWrt arm, B=Champion arm, ABBA-alternating order; per block run the 1013A TCP sink/source transfer (dd|nc, host-timed), both directions, plus 1007A bridge probe for UDP flows.
- 7. Holdout: >=6 disjoint paired blocks, fresh run ids and raw hashes.
- 8. Call RegressionGatekeeper(...).evaluate_paired(runs, replication_receipt_path=..., candidate_fingerprint=...); do not edit the gatekeeper.
- 9. Write the result receipt (result_receipt_contract); restore baseline config and read it back.

## Acceptance criteria
| metric | comparator | threshold | source |
|---|---|---|---|
| aa_negative_control_valid | == | True | tools/verify/build_stage886a_post_audit_aa_control_protocol.py validate_aa_campaign (A03) |
| aa_control_result | == | PASS_NO_PROMOTION | analysis/regression_gate/gatekeeper.py evaluate_paired in AA_CONTROL mode |
| paired_ab_blocks | >= | 12 | artifacts/autoresearch/stage977a_sidak_permutation_power_curve_and_mde_calculator.json (A07), floor 4 per analysis/regression_gate/gatekeeper.py |
| holdout_paired_blocks_disjoint_from_discovery | >= | 6 | analysis/regression_gate/gatekeeper.py min_blocks_for_promote=6; tools/verify/build_stage886a_post_audit_aa_control_protocol.py |
| sidak_adjusted_alpha_applied | == | compute_adjusted_alpha(0.05, m) | analysis/regression_gate/gatekeeper.py |
| gatekeeper_verdict_from_evaluate_paired | in | ['KEEP', 'PROMOTE'] | analysis/regression_gate/gatekeeper.py (objective=CAPACITY_WITH_QOE_CONSTRAINTS) |
| idle_baseline_loss_pct | == | 0.0 | stage906a_live_powerbeam_loss_diagnosis_and_aa.json |
| aggregate_goodput_champion_arm_mbps | >= | 22.8 | FLOOR PROVENANCE CAVEAT: the 22.8 Mbps floor is the Stage 105A stock-baseline aggregate (stock airOS8 TDMA, 20 MHz, DL 19.2 + UL 3.6) reached via stage699a_pbe5ac_ptp_complete_evolution_ledger_v4.json evolution_timeline; it is NOT a named field in 695A |
| reference_695A_arm_b_mean_aggregate_mbps | reference_only | 12.79 | stage695a_live_pbe5ac_vht40_pb040_pb050_champion_v4.json (historical, below the floor -> DEGRADED) |
| zero_false_positive | == | True | analysis/regression_gate/gatekeeper.py + tools/verify/build_stage886a_post_audit_aa_control_protocol.py |

## Stats contract (existing, read-only)
- Objective `CAPACITY_WITH_QOE_CONSTRAINTS` from `analysis/regression_gate/gatekeeper.py`; gatekeeper is Codex-#2-owned: call it, never edit it.
- n=12 paired blocks from `artifacts/autoresearch/stage977a_sidak_permutation_power_curve_and_mde_calculator.json`; Sidak alpha 0.05 (m=1).
- A/A control via `tools/verify/build_stage886a_post_audit_aa_control_protocol.py` (audit A03).

## Five-pillar plan
- `pillar_a_fullrea_binary_re`: knob catalog orchestration/autoresearch/firmware_knob_candidates.json; static caldata RE in stage927a_powerbeam_241_242_caldata_comparison.json
- `pillar_b_closed_loop_hyperresearch_scholar`: result receipt is ingested by tools/research/closed_loop_research_reactor.py (static_offline_disabled; no auto-actuation)
- `pillar_c_karpathy_autoresearch_harness`: pre-registered keep/discard: A/A control -> discovery -> disjoint holdout; offline boundary kept until operator approves live run
- `pillar_d_kdense_scientific_skills`: scientific-critical-thinking (floor provenance caveat, UNKNOWN cause of 906A loss) and statistical-analysis (977A MDE/Sidak)
- `pillar_e_memory_master`: claim FMX-STAGE1015A-POWERBEAM-PTP-RETEST-SPEC; scope project:futuramax

## Flashing mandate (verbatim)
> OTA: flash the remote STA first with uci-defaults embedded in the custom SquashFS factory.bin (exact IP, disabled=0, SSID, freq, WPA2, wds=1, 24 dBm, stp=0, Champion profile); then flash the local AP second. Never bring a production radio to the local switch.

## Result receipt the live lane must write
- File: `artifacts/autoresearch/stage1015a_live_powerbeam_ptp_241_242_retest_result.json`
- Readiness keys: `controlled_aa_valid`, `physical_workload_acceptance`, `zero_false_positive`, `evidence_provenance_class`, `application_goodput_mbps`
- Extra keys: `gatekeeper_verdict`, `aa_control_result`, `n_blocks`, `sidak_adjusted_alpha`, `raw_evidence_paths_with_sha256`, `live_devices_touched`, `spec_ref`, `idle_baseline_loss_pct`, `floor_22_8_provenance_acknowledged`
- Rule: values come from measurement only; unmeasured -> 'ABSENT' or null, never invented
- Rule: evidence_provenance_class=CONFIRMED_LIVE_HARDWARE only with raw captures hashed in the receipt
- Rule: no key may equal PRODUCTION_READY; readiness verdict is the audit lane's, not this receipt's
- Rule: a BLOCKED precondition is reported as BLOCKED with the blocker id, not skipped
