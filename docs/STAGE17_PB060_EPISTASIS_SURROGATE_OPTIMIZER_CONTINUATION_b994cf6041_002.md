<!-- doc-head: STAGE17_PB060_EPISTASIS_SURROGATE_OPTIMIZER.md continuation 2 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE17_PB060_EPISTASIS_SURROGATE_OPTIMIZER.md) | Part 2/2
<a id="pb050pb060-epistasis-and-next-variable-discovery"></a> [PB050/PB060: epistasis and next-variable discovery](STAGE17_PB060_EPISTASIS_SURROGATE_OPTIMIZER_CONTINUATION_b994cf6041_001.md#pb050pb060-epistasis-and-next-variable-discovery) | <a id="prespecified-question-and-boundary"></a> [Prespecified question and boundary](STAGE17_PB060_EPISTASIS_SURROGATE_OPTIMIZER_CONTINUATION_b994cf6041_001.md#prespecified-question-and-boundary) | <a id="posterior-and-acquisition-contract"></a> [Posterior and acquisition contract](STAGE17_PB060_EPISTASIS_SURROGATE_OPTIMIZER_CONTINUATION_b994cf6041_001.md#posterior-and-acquisition-contract) | <a id="catalog-discovery-and-switching"></a> [Catalog discovery and switching](STAGE17_PB060_EPISTASIS_SURROGATE_OPTIMIZER_CONTINUATION_b994cf6041_001.md#catalog-discovery-and-switching) | <a id="validation-record"></a> [Validation record](STAGE17_PB060_EPISTASIS_SURROGATE_OPTIMIZER_CONTINUATION_b994cf6041_001.md#validation-record)

<!-- stage822a-payload-begin -->
nonintegrable ratio contrasts and a spoofable Top15 copy. Repairs retain complete
source packages, use log-ratios, keep CoDel IDs unmapped and require exact Top15
row equality, eligibility and ranked prefix. Regression cases cover each finding.
Independent EHVI probes matched 25 deterministic area oracles to ≤1.67e−16.

## Saved result

The emitted JSON contains **308 unique rounds, 398 modeled contrasts, 93 exact
saved contexts**, and eight excluded contrasts. Of the 398 contrasts, 118 are
one-round phase-aggregate comparisons. The requested roster is 320; the twelve
missing rounds are not synthesized. The six retained input JSONs are authenticated
by pinned SHA256; the adapter and its pinned input snapshots retain source pointers.

Strict validation covers 32 held-out rounds: 3 folds yield 16 predictions and
29 are unsupported after purging both complete packages. Mean absolute errors
are 0.109905 throughput fraction and 0.366950 p95-reduction fraction. This sparse,
poorly generalizing evidence does not qualify a calibrated predictor. No final
context has two clean trailing saturation comparisons, so the saved corpus
triggers **zero current pivots**. Synthetic regression cases verify conditional
pivot behavior without asserting that the actual hardware reached those gates.

The defined conditional portion of Top15 at the R174 baseline is:

| Rank | Catalog ID | Monte Carlo EHVI |
| --- | --- | ---: |
| 1 | `aql_txq_limit` | 0.00000927888 |
| 2 | `aql_threshold` | 0 |
| 3 | `ct_special_7` | 0 |
| 4 | `fq_quantum` | 0 |

The AQL estimate has MC standard error 0.00000555789, about 60% of its mean.
The three zeros mean no improvement appeared in 2048 posterior draws; they are
not proofs of analytic EHVI zero, ineffectiveness or equal benefit. Stable IDs
order those numerical ties. Eleven further slots contain seven width/mask and
four coding descriptors, all labeled PRIOR_ONLY with null evidence-based EHVI.
They include platform-specific descriptors; none has an authenticated cross-platform
join. Full IDs, platform scopes, domains, gates, uncertainty and prior sensitivity
are in [the JSON frontier](../artifacts/physical_boundary/pb060_epistasis_surrogate_frontier_20261025.json).

Reproduce with installed Python3.12, NumPy1.26.4 and SciPy1.17.1:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
$env:NUMEXPR_NUM_THREADS='1'
node 'G:/_OneDrive/OneDrive/Desktop/Py Apps/wezbridge/scripts/heavy-slot.cjs' run -- python -m orchestration.autoresearch.pb060_epistasis_surrogate_optimizer
node 'G:/_OneDrive/OneDrive/Desktop/Py Apps/wezbridge/scripts/heavy-slot.cjs' run -- python -m pytest -q tests/test_pb060_epistasis_surrogate_optimizer.py -p no:cacheprovider
```

Output SHA256: `c380aa0cb562169c258fae70b7175f0e9fd8226586c048a96fedc6acc019391f`.
It binds engine `8035b9f2429c7a584345b6456a9993119a08222cb3da0423d268bf0e3964b6c1`
and test `f18a22c15d9f6b287042678ea400666f4e456c31848f601958368ff5c93d7883`.
Final independent review: **PASS_WITH_LIMITS**, F1–F5 closed, no material open
findings, on the exact engine/test/artifact hashes above. Receipt:
`C:/_tmp/systemp/fmx_bayes_source_review_e130d03a0d414fc79905f6d16ae42374/code_review_final/code_review.json`,
SHA256 `040f81e2cdacab9d5e5ec85a759a980687971ff575b06084b57ab304f8f1cb0a`.
The reviewer reused the unchanged-revision 34PASS XML and freshly checked all571
catalog metadata rows, exact Top15/eligibility/pins, 30 bounded numerical cases,
12 log-transformed EHVI oracles (error≤6.51e−19) and all four emitted acquisitions
against the saved posterior/seed. The review covers code, tests and JSON; this
final documentation receipt was added by the coordinator after review.

An optional artifact-present pytest repetition was canceled while waiting for
the unchanged heavy-slot RAM floor, before any child process started. That attempt
has **no new pytest result**. The already accepted source/test hashes did not change;
fresh independent JSON/pin checks cover the emitted artifact. Cancellation targeted
only owned node PID536104, creation2026-10-25T05:59:57.4058810Z, with zero children;
no RAM guard or other process was changed. No runner remains active.

Completion is limited to this task's four files and its explicitly requested
task-board update. No next task is claimed. Physical acceptance remains false;
E2 NOT_ACCEPTED. Further physical research requires the concrete missing factorial,
exact control/build readback, legal RF conditions and original recovery/timing gates;
it is not started by this offline result.
<!-- stage822a-payload-end -->
