<!-- doc-head: STAGE24B_AIRBBR_AND_RESPONSIBLE_AIRTIME_CONTROLLER.md continuation 1 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE24B_AIRBBR_AND_RESPONSIBLE_AIRTIME_CONTROLLER.md) | Part 1/2
<a id="generated-commands-and-rollback-limits"></a> [Generated commands and rollback limits](STAGE24B_AIRBBR_AND_RESPONSIBLE_AIRTIME_CONTROLLER_CONTINUATION_f581f09ce5_002.md#generated-commands-and-rollback-limits) | <a id="verification-and-preserved-failures"></a> [Verification and preserved failures](STAGE24B_AIRBBR_AND_RESPONSIBLE_AIRTIME_CONTROLLER_CONTINUATION_f581f09ce5_002.md#verification-and-preserved-failures) | <a id="revision-bound-review-receipts"></a> [Revision-bound review receipts](STAGE24B_AIRBBR_AND_RESPONSIBLE_AIRTIME_CONTROLLER_CONTINUATION_f581f09ce5_002.md#revision-bound-review-receipts)

<!-- stage822a-payload-begin -->

Observed Stage21v3 snapshot is frozen; the concurrent Stage24C profile is preserved.
Complete station/AC coverage prevents partial-cost weight and AQL adjustments.
ACK RTT and weak-fraction policies are local; AirBBR attribution remains unverified.
Two final independent reviews pass with limits; pytest never executed below2GB guard.
No command execution, physical observation or operational rollback is accepted.


# Stage24B: AirBBR and Responsible Airtime controller

Deliverables: [controller](../controller/stage24_airbbr_and_responsible_airtime_controller.py),
[JSON plan](../artifacts/autoresearch/stage24b_airbbr_responsible_airtime_plan_20261025.json),
this document, and [tests](../tests/test_stage24b_airbbr_and_responsible_airtime.py).

Task `T-S24B-AIRBBR-AND-RESPONSIBLE-AIRTIME-CONTROLLER`.

## Prespecified research question and acceptance

Parent deliverable: airtime fairness, queueing and control-authority research in
the original `artifacts/2026-09-20-forward-plan.html`, under BENCH_PLAN's evidence
and recovery boundaries. The operator explicitly authorizes this controller
extension; this task does not execute RF/load experiments or apply radio changes.
E2 and prior physical gates remain unchanged.

Question: can measured airtime plus only missing, attributable overhead support
bounded station-weight, per-AC AQL and ACK-RTT pacing proposals on top of
`openwrt_lap120_ptmp_multicpe_champion`, without double counting, invented
per-station AQL, or confusing FQ-CoDel with a rate shaper?

Existing evidence: the retained scholar query contains Responsible Airtime's
abstract; current Champion declares1850/3700us AQL, threshold6000, airtime_flags7,
FQ-CoDel quantum1514 target10ms interval50ms, plus other Stage21 settings.
These are source-profile declarations, not newly observed effective controls.

Minimum missing evidence for software acceptance: primary-paper scope/formulas,
actual Linux command semantics, explicit input units/coverage, bounded correction
and pacing rules, command provenance and exact rollback values; deterministic
tests of numerical behavior and rejected unsafe/unsupported inputs. Export the
four requested files and run the single requested pytest file. Stop after this
software deliverable; no deployment or performance acceptance is implied.

All implementation ownership stays in the four requested Stage24B paths. Existing
Champion, shared source/bench documents and prior tasks are not silently rewritten.

## Paper evidence

The retained scholar JSON (research/temp/scholar_queries_20261025.json under the
hyperresearch vault) has SHA256
1decd5bd95754cc0a2b9fd8f065343a3c4539e71c2bd8b45da187b6de79f772b.
It contains Yu/Park2018, DOI10.3390/s18113658. AirBBR appears in a query key,
but the requested title, authors and DOI10.2139/ssrn.7434484 are absent as a
paper record. Exact public title/DOI searches and the inaccessible SSRN page
did not authenticate it. This remains UNKNOWN, not evidence of nonexistence.

The [Responsible Airtime primary full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC6264109/)
defines total attributable time, including reverse TCP acknowledgments.
Sections5.1-5.2 describe measured MAC-request-to-MAC-ACK durations, an EMA with
alpha0.1, and time-deficit DRR. Evaluation is ns3 AP download; no QCA988x gain
follows. Section3.2/equations6-7 evaluate throughput achievement against a
matching homogeneous baseline, not PHY-rate divided by station count.

This module implements explicit-overhead accounting and a local mapping to
Linux weights/AQL, not a reproduction of the paper's DRR. RTT pacing and the
requested (N-1)/N rule are explicit local experimental policies; AirBBR attribution
is unverified. No RTT-to-N estimator, paper threshold or causal RF gain is invented.

## Historical Champion and preserved source drift

First generation failed closed with Champion source SHA256 drift, exit1:
expected5d559357d28fc08778b9cab0e305b74df31c17bf7850d1ce63cdcc6cbf3ce1fd;
observed later source e4bb49f6071578662c94fbc25fcef17e7bbbba56be4af6daf4abc555a9863d97.
Another writer advanced the shared profile to Stage24C, including different
per-AC AQL, threshold5000, qdisc memory_limit and pacing-ratio settings. It was
preserved; these values are not consumed as Stage21v3.

The owner and independent reviewer had both read the eight Stage21 commands
before that edit. The new module retains their selected historical snapshot,
canonical JSON-list SHA256
c09b44695f2a7d33bfb54f6ea79ab703e90a475f6396897abd4fc0062910be46.
The complete old module preimage was not found. Its old file hash is an observed
historical binding, not freshly authenticated held bytes. The snapshot is labeled
accordingly. Its old suppressed-error strings are evidence only; new generated
control commands do not inherit them.

The separate Stage21 package is
artifacts/autoresearch/stage21_deep_driver_and_3cpe_all_champion_20261025.json,
SHA256081540bedefc4ffaa1c1ce4009eec5e5f523b705589e3d452027f563f0bf7742.
It establishes package/profile names and recorded weight declarations, not
the eight original commands or the current installed PtMP state.

The frozen parent is all-AC1850/3700us AQL, threshold6000, airtime_flags7,
retry5/4, nf_cal_period30, queue length256 and FQ-CoDel quantum1514,
target10ms/interval50ms/ECN, with existing TSQ/notsent/budget coordinates
preserved. The controller does not apply the whole old profile.

## Accounting and numerical policy

Inputs describe one explicit observation window, AP interface/PHY, station
contract/current weights, backlogged/weak classifications, unique acknowledged
payload bytes, contract rates and baseline/sample ACK RTTs. Capabilities,
attribution and flow isolation are caller declarations, not runtime proof.
The exported example is SYNTHETIC: zero new physical observations.

Each AP-only station/AC component ledger uses:

    M[i,a] = AP mac_tx_us + AP mac_rx_us
    R[i,a] = M[i,a] + sum(O[k] for k not already covered by M[i,a])

The complete overhead dictionary requires TCP-ACK body airtime, IFS, backoff,
RTS/CTS body and PHY preambles, even when explicitly zero. Counter coverage must
be declared. Missing, negative or nonfinite inputs are rejected. TCP ACK differs
from MAC ACK. ACK/RTS/CTS bodies exclude their separately charged preambles/IFS;
preamble counts must follow PPDUs, not each MSDU in an aggregate. Retries belong
in their actual observed event ledger. AP TX and receiving-CPE RX represent
the same occupancy: combined endpoint scope and duplicate station/AC ledgers
are rejected. Disjoint costs may not exceed the shared PHY observation window.

Elapsed mode uses an attributable elapsed total directly, keeping M only as a
correction reference; component fields must be null. It never adds overhead over
that complete duration. No collector is installed and missing backoff/collision
time is not reconstructed from mean PHY rates.

The caller supplies four explicit per-AC participant sets; null means UNKNOWN.
Global AQL correction requires exactly all expected station/AC ledgers. If every
participant set is declared complete, their union must cover backlogged stations.
Partial/unknown coverage, idle traffic or unqualified attribution holds AQL.
Whole-station weight corrections also require every declared AC ledger for that
station; any unknown AC participant set prevents certification of its full cost.

For station i:

    c[i] = sum_a(M[i,a]) / sum_a(R[i,a])
    f[i] = (N-1)/N if weak and backlogged with N>=2; otherwise1
    raw_weight[i] = contract_weight[i] * c[i] * f[i]

N must equal the declared backlogged-station count, not an RTT estimate. Targets
are floored/clamped to1..65535 and move at most25% from captured current weights.
They remain anchored to stable contract weights on subsequent evaluations, so
constant overhead does not repeatedly decay current weights to zero. Missing
MAC evidence/capabilities means HOLD. N=1 explicitly avoids zero pacing; N=0 is
an idle-sector HOLD and is invalid for the weak-fraction helper.

Weights are relative TX scheduling credit, not an aggregate rate cap. Ideal
backlogged share is target_weight/sum(target_weights). Multiplying a weight
by2/3 does not guarantee a2/3 change in airtime/goodput. AP TX weights do not
control the uplink contention scheduler.

For each AC, c[a]=sum_i(M[i,a])/sum_i(R[i,a]). Desired low/high limits are
floor(1850*c[a]) and floor(3700*c[a]), clamped to minimum500/1000us and the
Stage21 upper bounds1850/3700us. Each limit also moves at most25% UP or DOWN
from its captured current value. High never falls below low. These are local
experimental safeguards, not paper constants.

AQL values are microseconds of pending estimated airtime. They change global
PHY defaults per AC, not individual CPE limits. Custom per-station overrides
<!-- stage822a-payload-end -->
