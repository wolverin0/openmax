<!-- doc-head: Stage 1016A WA radio .20 retest spec; SPEC ONLY, offline, not executed, not a readiness claim -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# Stage 1016A WA .20 retest spec

Receipt: `artifacts/autoresearch/stage1016a_wa_20_retest_spec.json`. Builder: `tools/verify/build_stage1015a_to_1017a_retest_specs.py`.
Status CONFIRMED = spec authored. Nothing here was executed; no key equals PRODUCTION_READY.
Owner: Codex #1 (live lane). Execution status: `SPEC_ONLY_NOT_EXECUTED`.

## Target and source readiness
- Target: WA radio .20 (AP20, 198.18.0.43)
- `from_1009A`: {"verdict": "NOT_READY (PtP Champion v4 window row; 897A/898A/900A cited there)", "receipt": "stage1009a_ptp_powerbeam_litebeam_production_readiness_audit.json"}
- `from_1010A`: no WA-specific target in 1010A (Panel3 only); not applicable
- `wa_live_state`: {"stage897a_live_wa_hardened_kit_verify.json": "BLOCKED/NOT_ACCEPTED (AP20_TC_NOT_INSTALLED_AND_ATH0_NOT_PRESENT, VERIFY_MODE_UNSUPPORTED in the older kit)", "stage898a_live_wa_aa_and_holdout.json": "BLOCKED/NOT_ACCEPTED (NO_VERIFIED_OPENWRT_STA_ON_OPERATOR_CANDIDATE_ADDRESSES)", "stage900a_post_audit_live_execution_gate.json": "INCOMPLETE/NOT_ACCEPTED (WA_APPLY_AND_REQUESTED_FQ_CODEL_VERIFY_NOT_E

## tc-less limit
AP20 has no tc (897A). The kit's `tc qdisc` parameters (fq_codel quantum/target/interval/flows/limit) CANNOT be read back on-radio; 1014A validates ONLY default_qdisc, phy aqm and phy aql_txq_limit. A passing readback proves those three, NOT the netdev-level qdisc parameters.

## Kit and sequence
Kit: `firmware/openwrt/common/fmx_wa_v15_368window_field_kit.sh`
1. `--dry-run (default; prints PLANNED, mutates nothing)`
2. `--apply --identity <id> --state-dir <root-owned 0700 dir> --qdisc-mode sysfs-default (creates the snapshot; transient queues only)`
3. `snapshot check (files root-owned 0600, ready=READY, fingerprint matches)`
4. `--verify (same --identity/--state-dir)`
5. `--rollback on any apply/verify/readback failure (restores snapshot; queued packets are NOT restored)`

## Cited queue rows (from `stage1004a_pending_live_retest_queue.json`)
| rank | receipt | score | suggested measurement |
|---|---|---|---|
| 33 | `stage641a_wa_champion_v10_256window_field_rollout_kit.json` | 6 | counterbalanced ping/RTT p50/p95 windows, champion vs baseline, same radio pair |
| 12 | `stage385a_cumulative_42round_172window_wa_champion_v7.json` | 8 | counterbalanced iperf goodput windows (>=4 rounds), champion vs baseline |
| 13 | `stage315a_cumulative_36round_148window_wa_champion_v6.json` | 8 | counterbalanced ping/RTT p50/p95 windows, champion vs baseline, same radio pair |
| 14 | `stage279a_cumulative_30round_124window_wa_champion_v5.json` | 8 | counterbalanced iperf goodput windows (>=4 rounds), champion vs baseline |
| 15 | `stage214a_cumulative_24round_100window_wa_champion_v4.json` | 8 | counterbalanced ping/RTT p50/p95 windows, champion vs baseline, same radio pair |
| 16 | `stage169a_cumulative_21round_wa_champion_v3.json` | 8 | counterbalanced iperf goodput windows (>=4 rounds), champion vs baseline |

## Measurement tools
- `workloads/busybox_nc_uhttpd_bridge_sink_adapter.py`
- `tools/qca988x/validate_wa_tcless_statless_profile_readback.py`
- `workloads/host_driven_triple_play_socket_probe.py`

## Preconditions
| id | precondition | source |
|---|---|---|
| 1 | Identify the actually associated OpenWrt STA for .20 (898A blocker); do not guess candidate addresses | `stage898a_live_wa_aa_and_holdout.json` |
| 2 | Kit is root-run, needs id/ubus/jsonfilter/ethtool/sysctl/sha256sum/stat on the radio; confirm with --dry-run first | `firmware/openwrt/common/fmx_wa_v15_368window_field_kit.sh` |
| 3 | Pre-apply read-only capture via the 1014A readback_commands() (3 cat commands) for the pre-state | `tools/qca988x/validate_wa_tcless_statless_profile_readback.py` |
| 4 | Operator approval + exclusive RF window; rollback path rehearsed before --apply | `stage900a_post_audit_live_execution_gate.json` |
| 5 | Any reflash follows the flashing_mandate (STA first, AP second) | `flashing_mandate` |

## Procedure
- 1. Verify preconditions; BLOCKED result if any fails.
- 2. Pre-register objective, m, n (stats_contract) in the result receipt.
- 3. `sh firmware/openwrt/common/fmx_wa_v15_368window_field_kit.sh --dry-run` and record the PLANNED line.
- 4. Pre-state readback via 1014A commands (A arm = stock/pre-state).
- 5. A/A negative control (>=2 measured runs, 886A validate_aa_campaign) on the pre-state.
- 6. `--apply` with --identity/--state-dir/--qdisc-mode sysfs-default; confirm the snapshot.
- 7. `--verify`; then 1014A validate_readback(aql, aqm, default_qdisc) must return ok=true, profile_state=CHAMPION_APPLIED.
- 8. On ANY failure: `--rollback`, re-read via 1014A, report FAILED_ROLLED_BACK.
- 9. A/B: n=12 paired blocks (A=pre-state, B=wa-v15 applied) via the 1013A TCP sink/source adapter (+ 1007A for UDP VoIP/IPTV); then >=6 disjoint holdout blocks.
- 10. Call RegressionGatekeeper(...).evaluate_paired(...); write the result receipt; rollback and read back.

## Acceptance criteria
| metric | comparator | threshold | source |
|---|---|---|---|
| aa_negative_control_valid | == | True | tools/verify/build_stage886a_post_audit_aa_control_protocol.py validate_aa_campaign (A03) |
| aa_control_result | == | PASS_NO_PROMOTION | analysis/regression_gate/gatekeeper.py evaluate_paired in AA_CONTROL mode |
| paired_ab_blocks | >= | 12 | artifacts/autoresearch/stage977a_sidak_permutation_power_curve_and_mde_calculator.json (A07), floor 4 per analysis/regression_gate/gatekeeper.py |
| holdout_paired_blocks_disjoint_from_discovery | >= | 6 | analysis/regression_gate/gatekeeper.py min_blocks_for_promote=6; tools/verify/build_stage886a_post_audit_aa_control_protocol.py |
| sidak_adjusted_alpha_applied | == | compute_adjusted_alpha(0.05, m) | analysis/regression_gate/gatekeeper.py |
| gatekeeper_verdict_from_evaluate_paired | in | ['KEEP', 'PROMOTE'] | analysis/regression_gate/gatekeeper.py (objective=LATENCY_WITH_CAPACITY_NONINFERIORITY) |
| kit_dry_run_exit_code | == | 0 | firmware/openwrt/common/fmx_wa_v15_368window_field_kit.sh |
| kit_verify_exit_code | == | 0 | firmware/openwrt/common/fmx_wa_v15_368window_field_kit.sh |
| readback_validate_ok | == | True | tools/qca988x/validate_wa_tcless_statless_profile_readback.py validate_readback (1014A) |
| readback_profile_state | == | CHAMPION_APPLIED | stage1014a_validate_wa_tcless_statless_profile_readback.json |
| capacity_loss_pct_vs_A | <= | 2.0 | analysis/regression_gate/gatekeeper.py max_capacity_loss_pct default |
| latency_gain_pct_vs_A | >= | 5.0 | analysis/regression_gate/gatekeeper.py min_latency_gain_pct default |
| netdev_tc_qdisc_params_readback | == | NOT_VERIFIABLE_TCLESS | tcless_limit above |

## Stats contract (existing, read-only)
- Objective `LATENCY_WITH_CAPACITY_NONINFERIORITY` from `analysis/regression_gate/gatekeeper.py`; gatekeeper is Codex-#2-owned: call it, never edit it.
- n=12 paired blocks from `artifacts/autoresearch/stage977a_sidak_permutation_power_curve_and_mde_calculator.json`; Sidak alpha 0.05 (m=1).
- A/A control via `tools/verify/build_stage886a_post_audit_aa_control_protocol.py` (audit A03).

## Five-pillar plan
- `pillar_a_fullrea_binary_re`: applied profile is the reverse-engineered wa-v15 knob set in firmware/openwrt/common/fmx_wa_v15_368window_field_kit.sh; catalog orchestration/autoresearch/firmware_knob_candidates.json
- `pillar_b_closed_loop_hyperresearch_scholar`: result receipt ingested by tools/research/closed_loop_research_reactor.py (no auto-actuation)
- `pillar_c_karpathy_autoresearch_harness`: dry-run -> apply -> snapshot -> verify -> rollback-on-fail is the keep/discard loop; offline boundary until approved
- `pillar_d_kdense_scientific_skills`: scientific-critical-thinking (tc-less readback limit stated, not papered over) and statistical-analysis
- `pillar_e_memory_master`: claim FMX-STAGE1016A-WA-20-RETEST-SPEC; scope project:futuramax

## Flashing mandate (verbatim)
> OTA: flash the remote STA first with uci-defaults embedded in the custom SquashFS factory.bin (exact IP, disabled=0, SSID, freq, WPA2, wds=1, 24 dBm, stp=0, Champion profile); then flash the local AP second. Never bring a production radio to the local switch.

## Result receipt the live lane must write
- File: `artifacts/autoresearch/stage1016a_live_wa_20_retest_result.json`
- Readiness keys: `controlled_aa_valid`, `physical_workload_acceptance`, `zero_false_positive`, `evidence_provenance_class`, `application_goodput_mbps`
- Extra keys: `gatekeeper_verdict`, `aa_control_result`, `n_blocks`, `sidak_adjusted_alpha`, `raw_evidence_paths_with_sha256`, `live_devices_touched`, `spec_ref`, `kit_exit_codes`, `readback_validation_result`, `rollback_executed`
- Rule: values come from measurement only; unmeasured -> 'ABSENT' or null, never invented
- Rule: evidence_provenance_class=CONFIRMED_LIVE_HARDWARE only with raw captures hashed in the receipt
- Rule: no key may equal PRODUCTION_READY; readiness verdict is the audit lane's, not this receipt's
- Rule: a BLOCKED precondition is reported as BLOCKED with the blocker id, not skipped
