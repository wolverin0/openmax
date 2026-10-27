<!-- doc-head: Offline R1-R14 CoDel TSQ timing distance and crypto analysis -->
83 primary windows and two R11 summaries preserve controls, missing samples and topology.
R12 pings are conditional subsamples; paired experimental inference needs missing IDs.
R13 distance is a coverage timing setting, not demonstrated physical range.
R14 has one observed associated CPE; crypto effects remain causally unidentified.
The advisory selector keeps whole observed packages, context and negative evidence.
<!-- /doc-head -->

# Stage12: cross-layer CoDel, TSQ, timing distance and crypto

Parent: `FMX-OFFLINE-WAVES-IJKL-20261024`, Stage12 control-authority and experimental-methodology deliverables in the original forward plan. This program reads saved local data and recipes as text. It performs no SSH, device contact, radio operation, target firmware execution, live-helper import/execution or package installation.

## Wave I: the actual corpus

The [normalized dataset](../artifacts/autoresearch/waves_ijkl_20261024/normalized_r1_to_r14_measurements_20261024.json) contains 85 records: **83 primary windows and two summary-only R11 validations**. R1-R14 primary counts are 8, 5, 7, 7, 6, 7, 6, 6, 6, 6, 5, 4, 6, 4. The fourteen receipts and fourteen acquisition recipes are frozen and hashed in [the input manifest](../artifacts/autoresearch/waves_ijkl_20261024/inputs_manifest.json). The prior R1-R9 API remains 58 windows; the new API is `load_all14_measurements()` and CLI switch `--all-rounds14`.

Endpoint declarations retain `fq_target_us`, `fq_interval_us`, `tcp_limit_output_bytes`, `tcp_notsent_lowat`, `distance_meters` and `encryption_mode`, including unknown values. In particular, 4294967295 is a retained TCP notsent sentinel, not a measured queue occupancy. Policies preserve VO/VI/BE/BK order, AP versus CPE, DSCP metadata and whole-pair identity. Source round/hash and JSON pointer bind observations. AP-only R1-R4 CPE policy is absent, not fabricated.

The two R11 validations retain aggregate outcomes but have no RTT arrays, loss, station-drop or restoration observations. Those fields remain absent and the controller excludes these summaries. R5 onward does not retain individual directional goodput repetitions. R14 preserves twenty reported received pings per window but has **no raw RTT arrays**; its quantiles cannot support reconstructed samples, bootstrap intervals or rank tests.

Encryption is evidence-labeled context: R1-R13 `psk2` is **INFERRED** from the prior WPA2 baseline described by the R14 recipe, not per-window cipher readback; R14 `none` is **DECLARED** by its frozen recipe, not independently verified effective encryption. R14's WPA2 restoration flag reports connectivity success and does not prove the effective cipher of each benchmark window. CCMP versus open interpretation must retain this uncertainty.

## Wave J: sampling and identifiability

R12 is called high-power because it increases statistical acquisition to four reported repetitions and forty attempted pings per treatment; no RF transmit-power increase is recorded. Received RTT counts are 40, 40, 39 and 40. The third treatment loses one ping (2.5 percent), and remains negative evidence. Sorted, pooled RTT arrays have no retained repetition membership, timestamps or cross-treatment pairing IDs. Forty pings are not forty randomized physical trials; four reported repetitions are not four recoverable per-repetition response arrays.

The [Wave J implementation](../analysis/statistics/fmx_r10_to_r14_causal_and_power_analysis.py) and [final numerical dataset](../artifacts/autoresearch/waves_ijkl_20261024/wave_j_analysis_final.json) cover all25 primary R10-R14 windows. Mann-Whitney U uses a two-sided asymptotic test with tie and continuity correction. The fixed multiplicity family contains52 unordered within-round contrasts:15/10/6/15/6 for R10/R11/R12/R13/R14. All six unavailable R14 rank tests remain in the Holm denominator. Global52 is the primary correction; clearly named within-round adjustments are secondary. The contrast family is an offline analysis choice, not a preregistered physical experiment.

Hodges-Lehmann estimates use the median of treatment-minus-control pairwise differences, **not** the difference of the two sample medians. Default intervals invert simultaneous DKW marginal-CDF bounds; this handles ties without treating the nm derived differences as independent samples. Null endpoints denote negative/positive infinity. The callable exact-U rank-inversion option requires an explicit continuous common-shape location-shift model with no ties; it is tested independently and is not imposed on the rounded bench data. Marginal95 percent HL/tail intervals are not familywise confidence intervals.

Wilcoxon runs only with unique matching genuine unit IDs. Its tested API aligns IDs instead of zipping positions. Real pooled/sorted arrays have no such IDs, so production contrasts return `UNIDENTIFIED_PAIRING`; R14 returns raw-data absent. No artificial pairing or per-repetition block bootstrap is manufactured.

| R12 contrast against stock | MWU p | Global52 Holm p | HL shift ms | Conservative95 percent HL interval ms |
| --- | ---: | ---: | ---: | --- |
| universal | 0.004329 | 0.203472 | -10.215 | [-38.64,26.61] |
| max-throughput,2.5 percent loss | 0.003421 | 0.167646 | -13.080 | [-38.19,17.99] |
| hybrid | 0.000246 | 0.012797 | -16.825 | [-38.68,14.47] |

Only the stock/hybrid rank contrast survives the primary correction under the **conditional independent-ping model**. These broad median-difference bounds and the rank test address different estimands/assumptions; no causal or physical effect is accepted. R13 distance0 versus3000 hybrid has global Holm p1.0; its scaled versus unscaled3000 package also has p1.0. Their conservative20-sample HL intervals are unbounded, and a smaller displayed p95 alone is insufficient evidence of improvement.

Tail intervals use1999 seeded empirical percentile bootstrap draws over received RTTs, with linear quantile interpolation. R12 stock p95 interval is [36.1005,48.59]ms and hybrid is [11.6395,24.8]ms; p99 intervals are [41.0389,48.59] and [17.7435,24.8]ms. These are separate pointwise intervals, not an interval for their difference. Stored RTT rounding explains small differences from receipt quantiles. Under iid sampling only, with40 responses the probability the maximum exceeds the true p99 is just33.10 percent: empirical resampling cannot reveal unseen upper tails. Lost packets censor the received-only distribution.

Prospective standardized-effect sensitivity uses normal paired/independent t models, **not observed post-hoc power**. For assumed d=0.5 and80 percent target power, an unadjusted comparison needs34 independent randomized AB pairs or64 independent windows **per arm**; a conservative Bonferroni52 plan needs75 pairs or141 per arm. With10 percent whole-unit dropout these become38/72 and84/157, respectively. The paired effect is d_z and the independent effect is d, so these are distinct assumptions. Even if four independent pairs existed, d_z0.5 planning power would be about11.1 percent; the current files do not identify four such pairs. None of these planning calculations schedules a physical experiment.

All ping intervals and tests remain conditional sensitivity analyses. Sequential adaptive order, load, cipher status, RF conditions and device counters remain uncontrolled.

## CoDel and TSQ associations across R10-R11

The R10 matched declared package with CoDel20/100ms reports104.85Mbps, p95=30.619ms and p99=35.967ms. Changing only declared CoDel timing to10/50ms reports104.60Mbps, p95=23.952ms and p99=26.962ms. Tightening further to5/30ms reports106.00Mbps, p95=25.943ms and p99=47.395ms. These one-window sequential observations do not establish monotonic benefit from lower targets.

For the R10-derived package in R11, TSQ1MiB/notsent4294967295 reports107.25Mbps and p95/p99=18.559/19.277ms. TSQ256KiB/notsent128KiB reports107.65Mbps and17.998/25.514ms; TSQ128KiB/notsent64KiB reports109.15Mbps and21.132/33.295ms. Different metrics move in different directions. The selector retains complete observed settings rather than assuming a smaller TCP queue always improves latency.

Control ownership: normalization/statistics/selection belong to the **external offline controller**. CoDel timing and FQ quantum belong to **Linux/mac80211 host queueing**; AQL belongs to the mac80211/ath10k host boundary. TSQ/notsent values belong to the **Linux TCP sender stack** and are not proof of an effect on forwarded subscriber TCP flows. Coverage timing traverses **Linux/ath10k to QCA firmware**; an attempted setter and echoed intent are not independent effective timing readback. Crypto behavior spans Linux/driver/firmware/hardware and remains **UNKNOWN** in effective per-window offload detail. No proprietary airMAX scheduler is recreated or qualified here.

## R13: coverage timing versus range

| Declared timing distance | Package | Goodput Mbps | p95 ms | p99 ms |
| --- | --- | ---: | ---: | ---: |
| 0 | stock | 105.15 | 46.072 | 53.810 |
| 0 | hybrid BE1800/3600 | 104.00 | 30.538 | 37.679 |
| 1500 | hybrid BE1800/3600 | 107.50 | 25.780 | 26.823 |
| 3000 | hybrid BE1800/3600 | 105.10 | 17.845 | 24.403 |
| 3000 | scaled BE1900/3800 | 104.50 | 15.544 | 21.811 |
| 3000 | stock | 101.70 | 38.558 | 40.378 |

These are saved sequential measurements on the bench. `distance_meters` programs coverage/slot/ACK timing; it does **not** establish physical 1.5 km or 3 km links. The scaled package changes both BE AQL and the AQL threshold. Its apparent latency change cannot be assigned uniquely to BE scaling, and neither a distance-response curve nor an optimum has been established.

## R14: observed UL/DL symmetry and missing multivendor acceptance

Despite its 3-CPE filename/title, the receipt lists only `Loco195` associated. SXT and LBM5 RTT counts are zero with -1 sentinels. Those sentinels are missing results, not negative latency; no three-CPE capacity or per-subscriber fairness result exists. Reported Jain values describe two aggregate traffic directions, not fairness among three subscribers. MAC packet deltas of 29-30 are sparse relative to bulk traffic, so their zero retry ratios do not establish an absence of radio retransmissions.

The stock R13 distance-0 window reports DL91.55/UL13.60 Mbps; R14 stock reports DL40.30/UL64.50. The hybrid package reports DL82.20/UL21.80 at R13 distance0 versus DL57.10/UL53.95 in R14. The shift toward symmetric direction totals is **CONFIRMED in the saved summaries**. Attribution to removal of CCMP is **UNKNOWN**: crypto context is partly inferred and round/time/setup may change alongside it. No paired crypto experiment or packet-level crypto CPU cost is retained.

## Wave K: non-actuating selection

The [controller](../controller/adaptive_aql_regime_controller.py) selects whole observed AP+CPE packages within workload and declared context. Package identity includes every CoDel, TSQ, coverage-distance and encryption coordinate, preserving unknowns. The heuristic still ranks observed goodput/latency and declared queue/RC costs; its constants are assumptions, not learned causal coefficients. It supports the legacy API and the new fourteen-round corpus.

`select()` accepts exact `distance_meters`, `encryption_mode`, `associated_cpes`, `fq_target_us`, `fq_interval_us`, `tcp_limit_output_bytes` and `tcp_notsent_lowat` constraints. Omitted context/knob constraints are unconstrained; explicitly supplied `None` matches recorded unknown only, and a supplied value requires an exact match. Known CoDel/TSQ constraints apply to both recorded endpoints, never substitute defaults for absent controls. This lets the caller require a measured cross-layer package without pooling it with an older package whose extra controls were unrecorded. Filtering precedes scoring and hysteresis revalidation.

Unspecified context that leaves multiple distance/crypto/topology pools causes abstention. A request outside the observed timing point, topology, regime or achieved UL/DL-ratio support also abstains. The ratio input is **observed achieved UL/DL**, not offered demand. Previous scores and settings are untrusted; hysteresis recomputes identity and eligibility in the current constrained pool. Any loss, station drop or failed reported restoration quarantines the complete package within its regime/context, including positive duplicate windows. Summary-only R11 validation windows cannot promote policies.

The85-record corpus yields67 eligible contextual packages; seven lossful primary windows and four positive aliases are excluded, as are both summary-only windows. [Saved examples](../artifacts/autoresearch/waves_ijkl_20261024/wave_k_offline_examples.json) show separate unknown/zero/1500/3000 timing contexts and the declared open single-Loco195 context. At3000/psk2 the score selects the recorded BE1900/3800 package with CoDel10000/50000us and TSQ262144/131072bytes. This is **selection among observed packages**, not an inferred physical optimum or isolated BE effect. No interpolated distance formula, synthetic coordinates, shell command or actuator exists.

A bounded query illustrates the interface (metadata only):

```python
from orchestration.autoresearch.fmx_offline_data import load_all14_measurements
from controller.adaptive_aql_regime_controller import AdaptiveAQLRegimeController

rows, provenance = load_all14_measurements()
controller = AdaptiveAQLRegimeController(rows)
result = controller.select(
    6, 0.3, 0.1,
    distance_meters=3000, encryption_mode="psk2",
    associated_cpes=("Loco195",),
    fq_target_us=10000, fq_interval_us=50000,
    tcp_limit_output_bytes=262144, tcp_notsent_lowat=131072,
)
assert result["automatic_execution_allowed"] is False
```

`distance_scaling` exposes the selected BE pair and every supported same-context option, with interpolation/extrapolation/physical-distance qualification all false. Cipher/topology evidence remains attached to candidate source windows. An inferred `psk2` annotation never becomes effective CCMP readback, and neither a selected package nor a score is authorization to change radios.

## Wave L: interpretation and reproducibility

KEEP the offline data/software and qualified associations. REJECT causal performance, physical-range, three-CPE or safe-actuation claims. Historical missing evidence has status `UNKNOWN_LOCAL_ARTIFACT_ABSENT` with its check complete, as explicitly required by the operator; it does not block this delivery. A future causal physical experiment would require separate authorization and matched randomized blocks, actual cipher/topology/timing readback, retained per-repetition responses and adequate received tail observations. No such experiment is queued by this report.

Fresh combined validation passed **300 tests, zero failures, errors or skips, exit0**, across eight focused pure-offline suites. [The captured run](../artifacts/autoresearch/waves_ijkl_20261024/focused_pytest_run_1.json) binds exact arguments, environment, test hashes and raw stdout/stderr. This includes the203 earlier focused regression cases plus97 added cases. Earlier failed fixtures and controller regressions remain in the wave artifact directory; a passing run does not erase them. The initial HL fixture expected the wrong exact interval; the independent rank-distribution/coverage checks established the corrected expectation. Controller negative/unknown-context regressions and the out-of-envelope ratio fixture are also preserved, with the changed hypothesis and repair documented.

Separate independent Wave I, J and K reviews bind the final source/test/data revisions. [Final validation](../artifacts/autoresearch/waves_ijkl_20261024/final_validation.json) records those reviews, frozen input preservation, numerical and example runs, current document links and remaining scientific limitations. Acceptance applies to offline source/data/numerical deliverables. Physical range, effective cipher/firmware control, causal gains and live policy safety remain unaccepted. No physical action is required for this delivery.

Reproduce with the already installed local dependencies; the recorded versions are in the dataset and final receipt:

```powershell
python -B -m orchestration.autoresearch.fmx_offline_data --all-rounds14
python -B -m analysis.statistics.fmx_r10_to_r14_causal_and_power_analysis --output artifacts/autoresearch/waves_ijkl_20261024/wave_j_reproduced.json
python -B -m artifacts.autoresearch.waves_ijkl_20261024.wave_k_generate_examples
```

Wave J creates a new output file and refuses to overwrite an existing result; choose a fresh owned `wave_j_*.json` name for each reproduction. Wave K examples are metadata-only generated outputs; frozen inputs remain read-only. The final pytest receipt provides the complete eight-file test invocation. No installation, live acquisition, deployment or commit/push is part of these commands.
