<!-- doc-head: Source-qualified evidence and v23 offline source release through940A -->
<!-- /doc-head -->

# Public engineering and evidence index

## Reproduce the software checks

Use Python3.12 with [requirements-audit.txt](../requirements-audit.txt), POSIX bash
and standard coreutils. Windows development checks use Git for Windows bash.

```sh
python tools/verify/verify_chatgpt_audit_1afaeb7.py
```

This runs isolated synthetic fixtures and command stubs. It does not SSH to radios,
apply host networking, load firmware, alter RF or contact research/memory services.
`--collect-only` checks public imports/collection. `--private` additionally requests
separately held local firmware checks; it never downloads or substitutes their inputs.
Software results do not certify native OpenWrt tc, target execution or recovery.

## Canonical contracts

| Component | Contract |
| --- | --- |
| [WA field kit](../firmware/openwrt/common/fmx_wa_v13_344window_field_kit.sh) | Default PLANNED; explicit identity-bound apply, snapshot, native getters, verified rollback. No unconditional OK. |
| [Measurement parser](../workloads/flent_orchestrator.py) | Empty replies are unavailable, errors invalidate acquisition, received goodput is separate from sender rate and actual packet counts. |
| [Regression gate](../analysis/regression_gate/gatekeeper.py) | Explicit width, finite metrics, unique paired IDs, whole-baseline drift, predeclared objective and independent hash-bound holdout. |
| [Search campaign](../controller/pb_060_070_autonomous_search_and_phy_gate.py) | Observed null controls, applied-config fingerprints, frozen family/contract, disjoint source identities/windows. |
| [SGMT inspection](../tools/qca988x/sgmt_container_inspector.py) | Diagnostic inspection is separate from structural validation; failed board/EOF/version/range cannot pass. |
| [Surgical patcher](../firmware/xtensa_sgmt_surgical_patcher.py) | Raw/compressed paths, bounded nonoverlapping segments and optional complete identity binding. Unbound results remain offline only. |

SYNTHETIC and STATIC_VERIFIED are not physical acceptance. Later states are
BENCH_EXECUTED, BENCH_REPLICATED, FIELD_CANARY and PRODUCTION_ACCEPTED.
Changing a label or copying a summary does not supply primary acquisition evidence.
The gate verifies supplied receipt bytes, arithmetic, readbacks and protocol identity;
it cannot authenticate the honesty of an instrument or establish target execution.

Latency with capacity non-inferiority, capacity with QoE constraints and robustness
are distinct predeclared objectives. Capability discovery needs its own witness.
The family correction is single-step Sidak, not Holm-Sidak. Unattainable resolution
is inconclusive; alpha is never increased to rescue a candidate.

## Historical evidence

Some historical reports and primary inputs are private or deliberately absent from
the public tree. This index provides their public context; it does not impersonate
the full reports. Absence here means UNAVAILABLE_TO_THIS_REVIEW, not nonexistent.

| Historical claim | Qualification in this software review |
| --- | --- |
| WA v13:344 windows,78.51Mbps VHT20 peak,-86.37% loaded p50 | Imported Stage773A claim; original acquisition IDs/date/raw not established by its packaging generator. No new measurement. |
| PBE/LBE PtP v4/v5:25.47Mbps VHT40 peak | Imported Stage741A claim; distinct board profiles do not prove universal runtime compatibility. |
| PB040/PB050/PB060 | Stage817A offline byte composition; loader/target execution remains UNKNOWN. |
| LTU v20:264 windows and DHCP kit | Imported Stage774A count; local DHCP stubs are not packet capture or persistence on a radio. |
| Guarida | Stage819A/v10 is an uncalibrated model;514.80Mbps belongs to the imported775A/v9 claim. |

The R71-R75 saved-data auditor is a separate path with its own exact-Holm controls;
defects in the legacy generic gate or Flent parser do not invalidate its results.
The older PB070 boolean predicate is hypothetical capability metadata, not a
hardware witness or authorization to execute a custom PHY experiment.

## Remediation and next experiment

[Remediation handoff](AUDIT_1AFAEB7_REMEDIATION.md) records red/green scope,
entrypoint classification and remaining gaps. The only proposed next physical
experiment is an inert target-execution canary with sham control and demonstrated
restoration. It is a blocked plan requiring separate operator authorization.

## Stages935A..940A: source-only v23 release

42 active source scripts: two guarded native transactions and40 retired legacy actuators;103 historical archive files are excluded.
Defaults inspect only; explicit apply, exact identity, snapshot, real readback and verified rollback gate the supported transient operations.
tc-less mode verifies the fq_codel default policy, not an existing active root qdisc. LTU native prerequisites and physical compatibility remain UNKNOWN.
Saved906A:12 diagnostic A/A windows; receiver goodput1.254..1.330Mbps; loss0.0..5.0%; original gateINCONCLUSIVE, no promotion.
Saved908A:24 native snapshots/12 passive intervals; aggregate CPU busy31.06..78.62%; application goodput and zero-FP remain UNKNOWN.
Saved909A:24 native snapshots/12 passive intervals; aggregate CPU busy30.47..40.70%; application goodput and zero-FP remain UNKNOWN.
905A..934A: 28/30 receipts available; 2 stages absent at this read. No new radio measurements were made.
[Source manifests](STAGE937A_V23_ACTIVE_SOURCE_SHA256_MANIFESTS.md) and [qualified saved evidence](STAGE938A_905_TO_934_VERIFIED_SAVED_MEASUREMENTS.md).
