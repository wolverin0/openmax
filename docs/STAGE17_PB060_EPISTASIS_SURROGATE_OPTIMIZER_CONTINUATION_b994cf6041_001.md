<!-- doc-head: STAGE17_PB060_EPISTASIS_SURROGATE_OPTIMIZER.md continuation 1 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE17_PB060_EPISTASIS_SURROGATE_OPTIMIZER.md) | Part 1/2
<a id="saved-result"></a> [Saved result](STAGE17_PB060_EPISTASIS_SURROGATE_OPTIMIZER_CONTINUATION_b994cf6041_002.md#saved-result)

<!-- stage822a-payload-begin -->

Four offline deliverables:571 knobs,308 rounds,398 contrasts,Top15 with limits.
Requested pytest34PASS; independent code/artifact review PASS_WITH_LIMITS.
Predictive interaction is not causal identification; all actuation remains disabled.
Missing rounds,failures,prior-only ties and E2 NOT_ACCEPTED remain explicit.


# PB050/PB060: epistasis and next-variable discovery

## Prespecified question and boundary

Parent: the original `artifacts/2026-09-20-forward-plan.html` observability,
algorithmic improvement and custom-MAC feasibility deliverables; current operator
task PB050/PB060, under BENCH_PLAN's offline saved-evidence boundary. E2 remains
NOT_ACCEPTED. This work belongs to the external controller/analysis layer.

Question: can a conditional Bayesian surrogate represent AQL/FQ/CoDel interactions,
detect saturation within one saved context and prioritize the next catalog variables
without mistaking a firmware descriptor, a synthetic timing fixture or an SSH
stream for demonstrated radio capacity?

Before implementation: the retained catalog has 571 descriptors, all disabled;
the saved corpus has 308 unique round IDs. Missing are R110–113, PBM5-R6–8 and
R5AC-R1–5. R173 contains Jain 0.951965; R174 contains +4.1314% goodput. Their
candidate policies differ. Neither number establishes a controlled factorial
interaction, nor does a source's KEEP establish independent acceptance.

Minimum deliverable: authenticate retained inputs; preserve per-radio/workload/
timing and measurement semantics; fit a genuine posterior over treatment contrasts;
calculate Monte Carlo expected Pareto hypervolume improvement; expose uncertainty,
validation and missing factorial cells; emit a reproducible Top15 and guarded pivots.
Hold whole rounds and identical packages out of validation. Learn scaling on the
training fold only. No RF, device access, load, recipe execution or deployment.

Stop after the requested test, independent review, reproducible artifact and exact
task-board completion. Park physical evaluation until exact board/build, permitted
control, readback, recovery and regulatory gates are satisfied. PB050 target timer
gating requires its original timing/queue-ownership gates; a generic WMI timer
descriptor does not satisfy them.

## Posterior and acquisition contract

The implementation reads SHA256-pinned JSON snapshots. Stage13's accepted
normalization is reused; its source recipes are never imported. Stage15 contributes
eight aggregate comparisons. Stage16 contributes provenance only: its audit,
port reports, defaults and synthetic examples do not become observations.

Each context separates radio, saved build identity, workload, flow count,
direction, declared distance/coverage/slot/ACK timing, cipher and metric meaning.
An unknown build stays `SAVED_BUILD_UNVERIFIED`; that is an explicit limitation,
not an authenticated firmware join. SSH streaming, OTA payload, five-request HTTP
timing and the unassociated three-host LTU proxy remain different objective spaces.
No proxy is relabeled sector capacity. Four aggregate phases yield one comparison,
not four independent trials. Five R13/R17 contrasts that change context without a
matched baseline remain in the exclusion audit; no replacement baseline is invented.
Three R36 contrasts have zero baseline goodput and cannot define a log-ratio;
their failed evidence remains in the retained source and exclusion audit.

For each context the GP represents a latent state function using an RBF plus
linear positive-semidefinite kernel. The encoder retains the full declared AP/CPE
package, including lower controls, unknown masks and the canonical VO/VI/BE/BK
order. It adds state products AQL(BE low)×FQ quantum/target/interval on each endpoint.
The contrast kernel is:

`kΔ = k(t,t′) − k(t,a′) − k(a,t′) + k(a,a′)`.

Training responses are `log(GP_B/GP_A)` and `−log(p95_B/p95_A)`. Log-ratios make
reverse treatments antisymmetric; ordinary relative ratios would violate that
constraint. Posterior draws are transformed back to fractional throughput gain
and fractional p95 reduction before computing acquisition. For HTTP timing the
first response is derived requests/second; its context names that proxy explicitly.

The two objective GPs are independent. Prior SDs are 0.10/0.30 log units; observation
noise floors are 0.04/0.12, doubled for phase aggregates. These are declared modeling
assumptions, not estimates of hardware noise or calibrated confidence intervals.
Scaling and categorical levels come only from the training fold. Whole rounds and
both complete packages are purged for validation; unsupported folds are retained.
The model remains exploratory regardless of fixture success or a small validation error.

EHVI is the Monte Carlo mean of the exact incremental dominated area in two
maximization objectives, with reference `(−0.20, −0.50)`, seed 60050 and 2048 draws
in the final artifact. Common random numbers reduce comparison noise. The artifact
reports Monte Carlo standard error; that error measures numerical integration,
not model correctness. The observed incumbent frontier requires zero reported loss,
reported restoration and no station drops. Failed/lossy treatments remain training
evidence. Jain and loss are descriptive guards, not imputed objectives; the saved
bidirectional Jain score is directional fairness, not fairness across CPEs.

Method references: [Monte Carlo acquisition definition](https://botorch.org/docs/v0.14.0/acquisition),
[Daulton et al., EHVI](https://arxiv.org/abs/2006.05078), and
[Gaussian process posterior/noise](https://scikit-learn.org/stable/modules/gaussian_process.html).
This implementation uses installed NumPy/SciPy; it installs no framework.

## Catalog discovery and switching

All 571 catalog descriptors are evaluated. The 127 excluded and 142 observation-only
entries cannot enter Top15. The other 302 remain physically unqualified. A static
`CONFIRMED` descriptor does not establish effective control or a safe range.

For a defined saved-coordinate intervention at the R174 baseline, the engine changes
only that variable's declared coordinates, holds the rest fixed and ranks its best
observed-value alternative by conditional posterior EHVI. AP/CPE are distinct
coordinates. These recombinations are model predictions, not executed treatments.
The catalog's CoDel-in-ms policy metadata is **not** aliased to the observed
`fq_target_us`/`fq_interval_us` API: those IDs retain null evidence-based EHVI.

Variables with no supported intervention have `evidence_based_ehvi=null`. Their
separate `hypothetical_prior_ehvi` integrates an explicitly zero-centered generic
log-ratio prior; SD sensitivity at 0.5×/1×/2× is published. Positive prior EHVI arises
from favorable distribution tails and does not demonstrate likely improvement.
These entries are tied; requested pivot-dimension order then stable catalog ID
breaks ties for presentation. The Top15 is therefore supported conditional EHVI
followed by labeled prior-only research questions. It is not a fabricated empirical
performance ordering of 571 untested controls.

The existing WallDetectorGate is reused only after exact-context partitioning,
positive-baseline checks and a clean trailing streak of two comparisons within
1.5% throughput and 5% p95 bands. Loss, missing restoration, drops, multiple
comparisons or renewed improvement break the streak. Historical wall hits do not
force a current pivot. When the trailing rule holds for an inferred single-CPE
context, the search questions switch to:

- PB030 5/10 MHz support and goodput/MHz characterization;
- PB031 LDPC/STBC and CCA/AGC characterization;
- asymmetric chain-mask rescue;
- PB050 target-timer gating feasibility.

These are proposed research dimensions. Name matches are navigation leads, not
API equivalence. No width enum is fabricated from a MHz number, no CCA/regulatory
exclusion is relaxed, and no generic timer is promoted to target TSF authority.
The output includes matched/excluded IDs, missing evidence and blocked state.

## Validation record

The requested test file is the only suite executed for this task. All fixtures are
disposable local numerical/data fixtures. Pytest runs under the existing machine
heavy-slot semaphore, its unchanged 2GB floor and one BLAS/OpenMP thread. No shared
service, device, WSL invocation, bench acquisition or source recipe is exercised.

Preserved development failures:

1. First run: exit1, 24 passed, 2 failed, 7 errors. The loader incorrectly assumed
   every source reference had `round_id`; the CLI test double lacked receipt fields.
2. Second run: exit1, 26 passed, 1 failed, 7 errors. A mixed-context R13 contrast
   correctly failed the strict context assumption. The adapter now retains unmatched
   R13/R17 comparisons in an explicit exclusion audit instead of aborting all input.
3. Third run: exit1, 32 passed, 2 failed. NumPy mean scalars were rejected by the
   strict Python numeric boundary for phase aggregates. Conversion to Python numeric
   values repaired the adapter. Three zero-goodput R36 contrasts remained explicitly
   ineligible for log-ratio modeling; no failed hardware result was turned into a pass.
4. Fourth run: exit0, **34 passed**, 0 failed/errors/skipped, 1.69s. Receipt
   `C:/_tmp/systemp/pb060_pytest_fourth_20261025.xml`, SHA256
   `d4783b8d80a414bf985c836cd18cf9e51c58e415e9b218c0de76159d567cac58`.

Independent review identified AC ordering, missing lower controls, CoDel API aliasing,
<!-- stage822a-payload-end -->
