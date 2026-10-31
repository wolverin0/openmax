<!-- doc-head: Stage1227A qualified binary proposals with strict passive bilateral PWO review and no device actions -->
<!-- /doc-head -->

# Stage1227A qualified discovery to PWO integration

This module processes supplied samples offline. It has no SSH, device API, control command or deployment path.
The existing Stage1183A bridge is called with allowed=false, so every outcome is NO-CHANGE.
Complete diagnostic inputs allow human review cards only; auto_approve=false and actual_control_actions=[] always.

## Qualified findings

The original DISC27/28 ledger entries retain their historical meanings. New proposal aliases are:

- `FMX-DISC-27@Stage1190A/free-node-stall`.
- `FMX-DISC-28@Stage1191A/ltu-timer-asymmetry`.

check_sta has a raw comparison literal120000000. The paired umac lookup increments and free_node decrements a reference.
Calling free_node alone does not prove association deletion or that the peer was left silently associated.
No-wrap120000ticks is not unconditional120000ms; HZ and 32-bit wrapping require separate evidence.
The two LTU2.4.2 ame_core variants have timer literals1/90. Their parameter ratio is90; timer units and measured recovery ratio remain UNKNOWN.
These binary observations are distinct from runtime causal confirmation and from any channel or power remedy.

## API and bilateral requirements

`recommend(observations, bilateral, now_s=..., max_age_s=30)` re-runs the Stage1224A/1225A pure evaluators.
Observations map each qualified alias to supplied sample rows. Missing/invalid samples cannot become a healthy result or a candidate card.
Both distinct ends must be present with reciprocal identities, explicit allowed=true, no vetoes, width20MHz, fresh timestamps and boot IDs.
Samples and endpoint snapshots share a named clock domain and collector epoch. AP/STA boots and link IDs must match;
LTU device/boot identity must correspond to one of the bilateral endpoints. Old, future, cross-clock and replayed observations fail closed.
The candidate status means investigate. alert_firing=false; production false-positive thresholds and runtime causality are not calibrated here.

The existing six PWO preflight gates remain TO_BE_CHECKED_BY_PWO. This adapter does not grant an operator window or approval.
No sample can authorize channel/power changes, resets, kicks, deauthentication, protected PoE operations or proprietary device-node access.

## Evidence and reproduction

`python tools/verify/verify_stage1227a_disc27_28_pwo_bridge_integration.py`

build_ledger/replay_ledger reproduce Stage1226A; build/replay_receipt reproduce Stage1227A.
ELF32 byte order, machine, symbols, relocation targets, reference deltas and scalar offsets are independently checked from local modules.
The ledger preimage and exact original DISC27/28 rows are preserved. Full64-character SHA256 values identify every binary.
Fixtures are synthetic offline contract checks; no fixture is a hardware measurement or live PWO acceptance.
The receipt binds the detector and existing bridge implementation as well as the current ledger and binary evidence.

[Ledger receipt](../artifacts/verification/stage1226a_curated_discoveries_disc27_28_sync.json)
| [Bridge receipt](../artifacts/verification/stage1227a_disc27_28_pwo_bridge.json)
| [Detector](STAGE1224A_FMX_DISC27_FREE_NODE_STALL_AND_DISC28_LTU_90X_HYSTERESIS.md)
