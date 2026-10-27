<!-- doc-head: Offline R15 asymmetric endpoint and genuine crossover model -->
Four frozen R15 windows extend85 prior records to89; no missing fifth row is fabricated.
Separate AP/CPE AQL, CoDel and TSQ controls retain observed WPA2-context asymmetry.
SimPy and native NSGA-II/III produce disabled exploratory proposals, not radio gains.
Crossover inference requires genuine block/step IDs; R15 has none and live R16 is untouched.
Backward compatibility, numerical tests and separate review govern software acceptance.
<!-- /doc-head -->

# Stage12: asymmetric AP/CPE and blocked-crossover model

Parent: `FMX-OFFLINE-WAVES-MNOP-20261024`, original Stage12 experimental-methodology, control-authority and model-validation deliverables. This is a100 percent offline program. Antigravity retains live Round16 ownership. No R16 artifact or recipe is read; no radio/network-device access, SSH, target execution, live-helper import/execution or online installation occurs.

## Evidence boundary and actual count

The R15 JSON, TSV and acquisition recipe were copied into [owned inputs](../artifacts/autoresearch/waves_mnop_20261024/inputs_manifest.json) before their contents were inspected. All subsequent R15 evidence comes from those copies. The I-L normalized85-record output is also frozen locally. Acquisition Python is read as text only. Older source/tests and the seven requested scientific skills inform implementation, without providing additional physical measurements.

Both the frozen JSON and TSV contain **four R15 windows**. Thus the observed corpus is **89 records =85 prior +4 R15**, including87 primary windows and two prior summary-only validations. The requested90 is retained as a discrepancy in [the normalized dataset](../artifacts/autoresearch/waves_mnop_20261024/normalized_r1_to_r15_measurements_20261024.json), with no invented fifth observation. The pre-existing master index described a fifth window and conflicting values, but neither frozen primary file supports that row; [the contradictory narrative is preserved](../artifacts/autoresearch/waves_mnop_20261024/historical_master_r15_narrative.md) and its current R15 section now matches the four frozen windows. Missing historical binaries are `UNKNOWN_LOCAL_ARTIFACT_ABSENT`, their checks complete, with no additional search required.

| R15 package | AP BE us | CPE BE us | Aggregate Mbps | DL Mbps | UL Mbps | p95 ms | p99 ms | Directional Jain |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| stock | 5000/12000 | 5000/12000 | 106.450 | 89.03 | 17.43 | 46.063 | 64.776 | .6885 |
| symmetric hybrid | 1800/3600 | 1800/3600 | 102.825 | 81.58 | 21.25 | 22.662 | 29.696 | .7439 |
| asymmetric1500 | 1500/3000 | 2100/4200 | 106.000 | 80.62 | 25.38 | 21.205 | 24.975 | .7864 |
| asymmetric1350 | 1350/2700 | 2100/4200 | 103.275 | 75.72 | 27.55 | 19.096 | 37.346 | .8213 |

These are saved sequential-window summaries, not new acquisitions. Rounded DL+UL totals and receiver means are preserved separately. All four retain40 received pooled/sorted RTTs and four reported repetitions, but no raw per-repetition goodput arrays or repetition membership. There are no `repetition_blocks` or genuine paired IDs. Jain describes two traffic directions, not subscriber fairness. [The descriptive received-RTT ECDF](../artifacts/autoresearch/waves_mnop_20261024/r15_received_rtt_ecdf.svg) plots the actual160 stored samples; it is not an independent-trial display. WPA2-PSK/CCMP is declared recipe context, not effective per-window cipher/crypto-offload readback.

Relative to the symmetric package, asymmetric1500 shows UL+4.13Mbps and DL-0.96Mbps, with lower displayed p95/p99. The more aggressive1350 package shows UL+6.30Mbps and DL-5.86Mbps, while p99 rises by7.65ms. These descriptive contrasts do not isolate BE AQL: FQ quantum, CoDel and TSQ also change. None of the four windows meets the recipe's strict p95<19ms aspiration;19.096ms remains above it.

## Questions, hypotheses and rivals

The observed outputs were already visible when this offline analysis was designed; hypotheses and predictions below are **exploratory**, not retrospectively preregistered. No hypothesis is automatically scored, ranked or accepted by the optimizer.

| Candidate explanation | Discriminating implication | Rival or unresolved condition |
| --- | --- | --- |
| Endpoint queue/airtime asymmetry contributes to DL dominance | Within balanced genuine blocks, endpoint-specific package differences persist across AB and BA order, with directional queue changes | Joint package changes and unequal offered load may explain the same pattern |
| A hypothesized CCMP CPU/preparation bottleneck favors DL | A model with independently justified unequal preparation costs changes the DL/UL split; an equal-cost sensitivity differs | Actual cipher offload, CPU costs and counter scope are unmeasured; model sensitivity is not mechanism proof |
| Time drift, adaptation or retained state explains part of the shift | Treatment contrasts vary with period, sequence or previous treatment, or collapse after counterbalancing | Small numbers of blocks and no retained washout/readback may leave carryover unidentifiable |
| Sparse tails and measurement selection explain apparent latency gains | Independent block-level tail summaries vary and upper-tail intervals remain broad | Pooled40-ping samples cannot establish stable p99 or unconditional latency under loss |

The target causal question is the effect of a **whole AP+CPE package** on paired block-level directional goodput and loaded-latency outcomes under matched load, actual cipher/topology and RF context. An isolated AQL or crypto effect needs a distinct factorial/control intervention. None is estimated causally from R15.

## Wave M: additive normalization and genuine units

`load_all15_measurements()` consumes the frozen I-L normalized output and R15 snapshot. `load_all_measurements()` remains58 and `load_all14_measurements()` remains85. R15 stores separate `ap_state` and `cpe_state`: asymmetric1500 has AP CoDel10000/50000us, TSQ204800/102400bytes, versus CPE12000/60000us and327680/163840bytes. Asymmetric1350 has AP9000/45000us and196608/98304bytes. Unknown distance stays unknown. All original endpoint order and policy identity are retained.

`load_blocked_crossover_blocks(receipt_dict_or_path)` is a pure local parser. It accepts top-level or iteration-local `repetition_blocks`, preserves explicit nonnegative integer `block_index` and `crossover_step`, and requires an explicit treatment identity. Step/treatment may inherit an explicit iteration value; list positions and ping indices never supply experimental-unit IDs. Duplicate block/step units, conflicting metrics/steps, malformed numbers and ambiguous identities fail closed. Returned rows are detached from the input and retain source pointers. Missing block collections return an empty list, including actual R15.

A hypothetical fixture can exercise AB/BA or ABBA rows while retaining all provided step observations. The analysis, rather than the loader, declares whether and how repeated same-treatment observations are averaged within a block. This interface is tested on **synthetic disposable receipts**; compatibility with an unseen live R16 schema is not claimed.

## Wave N: conceptual model, numerical validation and candidates

The [SimPy model](../analysis/simulation/fmx_asymmetric_ap_cpe_sim.py) uses real bounded discrete events: three Poisson sources per endpoint feed host/FQ queues, serialized endpoint preparation, AQL driver queues and one contended shared medium. AP carries DL and CPE carries UL. Default offered load is120/45Mbps with1500-byte packets; the modeled horizon is.12s, warm-up.02s and bounded drain.03s, with20000-packet and250000-event caps. Pending/preparation/inflight/queued packets and unfinished horizon cohorts are counted, not discarded to improve throughput or latency.

Each endpoint has its own AQL pending airtime, CoDel target/interval, FQ quantum and TCP TSQ/notsent backpressure. The persistent-sojourn CoDel approximation and FQ deficit service are conceptual host models, not Linux conformance implementations. CCMP preparation costs4usDL/15usUL are **hypothesized inputs**, not measured cipher CPU/offload facts. Distinct local arrival, backoff and service random streams use a retained manifest; three model replications share common random numbers across candidate comparisons. Replication-level means are numerical MC outcomes, not physical repeats.

Independent review found that an initial AQL threshold used combined AP+CPE pending airtime. That incorrectly let one host's backlog change the other host's local limit. The pre-fix source/results and actual failing regression were preserved; the minimal repair uses own-endpoint pending airtime and adds an instrumented zero-violation audit. Native results were regenerated. The final single-peer BE approximation may rarely activate the low-window threshold when threshold exceeds high plus a packet, so it cannot identify an independent threshold effect. No accuracy criterion or search range was loosened.

The [pymoo optimizer](../controller/optimizer/fmx_asymmetric_pareto_optimizer.py) ran native **NSGA-II and NSGA-III**, each population12 for3 generations and36 evaluations. The twelve integer coordinates are six per endpoint: BE-low us, FQ bytes, CoDel target/interval us, TSQ/notsent KiB. Encoding fixes BE-high=2*low and threshold=4*low. Proposed ranges are BE-low1000..2500us, FQ200..400B, target5000..20000us, interval30000..100000us, TSQ96..512KiB, notsent48..256KiB. Integer repair and original endpoint constraints are rechecked; target<=interval and proposed notsent<=TSQ are enforced. The stock4GiB-1 notsent sentinel remains independently representable for calibration; a proposed search restriction is not a general Linux validity rule or hardware-safe range.

Objectives minimize negative DL goodput, negative UL goodput, the latency proxy and1-directional-Jain. Across calibration, validation and both searches, the global bank used **75 unique scenarios x3 replications =225 SimPy runs**, below the128-case cap. The [candidate artifact](../artifacts/autoresearch/waves_mnop_20261024/asymmetric_pareto_candidates_20261024.json) retains two NSGA-II rows and one NSGA-III row, all AP!=CPE, with two rows nondominated across the combined returned set. The separately returned NSGA-III row need not be nondominated against NSGA-II's set. Every row is disabled, non-actuating, unmeasured and physically unqualified. This is a bounded Pareto approximation in an assumed model, not a global optimum.

Only a global capacity grid90/120/150Mbps is calibrated on the four R15 windows. It selects150 at the grid boundary, with in-sample total-goodput RMSE23.175Mbps; this is not independent validation and does not establish a150Mbps physical capacity. Earlier I-L comparisons hold out complete **modeled** endpoint-pair keys and exclude modeled policies seen in R15. Four known-complete WPA2 windows remain: three R11 and one lossful R12, with the lossful result preserved. Unknown controls, summary-only windows, nonzero unmodeled timing distance and open-crypto R14 are excluded with explicit reasons. Unmodeled AC/RC/driver controls and sequential context remain confounders.

| Whole-modeled-policy-held-out quantity | RMSE |
| --- | ---: |
| DL goodput | 43.979Mbps |
| UL goodput | 17.367Mbps |
| Total goodput | 26.653Mbps |
| Sum-of-directional-p95 latency proxy | 60.512ms |
| Directional Jain | .238693 |

The RTT proxy is a sum of modeled directional95ths, **not** a physical ICMP RTT percentile. Predicted DL/UL means remain about40.4/41.12Mbps for the displayed matched cases and fail to reproduce the observed DL dominance. This is a qualified negative model result: **REJECT physical predictive accuracy and gain claims**, KEEP the requested exploratory model/optimizer implementation. The grid is not expanded or retuned to hide that failure.

Independent replay reproduced the full75-case/225-run outputs and both algorithm results exactly. Packet/byte conservation was checked at450 horizon/drain snapshots;450 local-AQL audit summaries showed zero violations. These checks establish numerical/software consistency only. They do not validate the queue discipline, hypothesized CCMP mechanism or physical wireless behavior.

## Wave O: conditional R15 inference and paired crossover methods

The [audit implementation](../analysis/statistics/fmx_r15_and_crossover_statistical_audit.py) and [numerical results](../artifacts/autoresearch/waves_mnop_20261024/wave_o_analysis.json) retain all six unordered within-R15 RTT contrasts in one Holm family. The family is an offline exploratory analysis choice, not a preregistered physical design. Mann-Whitney U uses the reviewed I-L tie/continuity-corrected two-sided implementation; it contrasts distributions/ranks, not medians alone.

| R15 contrast | MWU p | Holm6 p | HL median pair-difference ms | Conservative95 percent interval ms |
| --- | ---: | ---: | ---: | --- |
| stock to symmetric | .001914 | .007656 | -12.425 | [-44.06,17.85] |
| stock to asymmetric1500 | .000461 | .002303 | -14.380 | [-44.20,13.74] |
| stock to asymmetric1350 | .000357 | .002142 | -15.545 | [-44.19,13.23] |
| symmetric to asymmetric1500 | .441405 | .923181 | -.700 | [-20.67,16.81] |
| symmetric to asymmetric1350 | .307727 | .923181 | -.925 | [-20.67,20.66] |
| asymmetric1500 to asymmetric1350 | .776511 | .923181 | -.205 | [-17.63,21.83] |

These calculations assume iid independent **received pings only as a conditional sensitivity model**. No such independence is established physically. HL uses the median of treatment-minus-control pairwise differences; its conservative marginal-DKW intervals do not count nm derived differences as independent samples. All intervals include zero. Rank-test rejection for stock contrasts does not establish a causal package or crypto effect; the asymmetric-versus-symmetric RTT distribution comparisons remain inconclusive.

The1999-draw seeded pointwise received-ping bootstrap gives p95 intervals stock[42.038,75.87]ms, symmetric[15.125,33.47], asymmetric1500[13.219,27.02], asymmetric1350[10.02,45.05]. Corresponding p99 intervals are [44.6757,75.87], [20.8923,33.47], [16.5678,27.02], [13.9288,45.05]ms. These are separate conditional empirical intervals, not simultaneous intervals or a paired treatment difference. Forty responses cannot expose unseen tails, repetition dependence or missing physical replication.

Actual R15 crossover returns `NOT_AVAILABLE_NO_IDENTIFIED_BLOCKS`. The exact future-block API requires supplied integer block/step IDs and explicit treatment IDs. For balanced ABBA or repeated same-treatment steps, it first computes an equal-weight mean outcome per treatment/block and then one B-minus-A difference per genuine block. Mean windowp95 is not pooled-pingp95. Missing arm, missing outcome, unequal counts or another treatment excludes the entire block with its ID/reason retained; loss and unknown quality remain separately reported rather than silently removed. Entirely missing blocks cannot be detected without an explicit expected schedule.

The paired methods are:

- **Exact signed-rank:** remove exact zeros under the Wilcox rule, midrank tied absolute nonzero differences, double ranks to integers and count the complete sign-assignment distribution with subset-sum dynamic programming. The bilateral p-value sums outcomes at least as far from the rank-sum center. No asymptotic tie shortcut is substituted.
- **Exact sign test:** two-sided binomial test of positive versus negative nonzero signs, with zeros disclosed; it is a sensitivity analysis rather than another unadjusted confirmatory claim. Its equal-sign null is not a universal median-only null with arbitrary point masses.
- **Paired HL:** median of Walsh averages i<=j, a pseudomedian of block differences rather than their sample median. The confidence set inverts that same exact signed-rank test across every Walsh breakpoint and open cell, including zero/tie transitions and unbounded tails. Its conservative hull may contain rejected gaps. Walsh count is derived information, never a replication count. Symmetric common-shift independent-block assumptions remain explicit.
- **Crossover diagnostics:** retain provided step/period IDs, show AB/BA/ABBA/BAAB sequence contrasts, missing-step gaps and period outcome means; inspect block+period+current-treatment+previous-observed-treatment design rank and conditional column estimability. A first/gap lag encoded zero is not known washout. Rank and descriptive contrasts do not prove absence or magnitude of carryover.

Synthetic fixtures test exact ties/zeros and paired-HL coverage against exhaustive sign allocations, including a counterexample where a four-tied-positive normal approximation crosses .05 but the exact p is .125. Root independent review additionally enumerated625 four-difference sign/tie/zero profiles, reproduced the complete1999-resample R15 output and independently recomputed Holm6. These validate numerical software, not a physical crossover.

With four nonzero genuine independent blocks, even all differences in the same direction give minimum exact two-sided p=.125. Six can first attain .03125 for a single contrast; eight can attain .0078125, below the first Bonferroni6 threshold. Attainable significance is not adequate power. Prospective normal standardized-effect sensitivity for assumed d=.5 and80 percent power requires34 paired blocks or64 independent windows per arm unadjusted; conservative family6 planning requires52 pairs or99 per arm, rising to58/110 with10 percent whole-unit dropout. This t-model planning is distinct from exact signed-rank power and does not certify the current design or schedule an experiment.

A block label alone does not establish randomization, independence, symmetry, washout or effective restoration. No R16 data is imported; actual blocked-crossover results remain unavailable for this program.

## Wave P: observed-package selector and compatibility

`allow_asymmetric=True` is the compatible constructor default because earlier R5-R7 packages already allowed unequal endpoints. A per-query `allow_asymmetric=None` inherits that setting; True admits complete observed unequal packages and False filters known unequal packages **before** context, ratio support, ranking and hysteresis. AP-only bulk remains explicitly CPE-unknown, not falsely symmetric. Both endpoint CoDel/TSQ vectors and ordered joint-policy identity are preserved; no coordinate is synthesized or swapped.

Negative-evidence quarantine, exact context/CoDel/TSQ constraints, unsupported-ratio abstention and hysteresis revalidation remain in force. A prior asymmetric choice cannot be retained after the pool is constrained or that joint package receives negative evidence. The ten accepted I-L example statuses, reasons, policy IDs, endpoints and scores reproduce exactly. Controller output remains non-actuating and physically unqualified. Native optimizer proposals are not automatically admitted as observations.

## Ownership and interpretation

Normalization, statistics, model and advisory selection belong to the external offline software. Linux/mac80211 owns host FQ/CoDel/AQL behavior; ath10k/QCA firmware retains lower-layer queue/timing boundaries. Linux TCP sender controls are not proof of effects on forwarded subscriber flows. Effective CCMP preparation/offload and any exact hardware bottleneck remain UNKNOWN. This program neither reproduces proprietary airMAX TDMA nor demonstrates a physical wireless improvement.

KEEP the requested offline implementation and reproducible numerical evidence. Physical/causal acceptance and live R16 analysis are outside this order. Fresh combined validation passed **411 tests with zero failures, errors or skips**, exit0, in12 offline suites: the300 earlier I-L cases,107 added M/N/O/P cases and four existing pure autoresearch-harness cases. [The exact pytest receipt](../artifacts/autoresearch/waves_mnop_20261024/focused_pytest_run_1.json) captures arguments, environment, test hashes and stdout/stderr. These are all selected FMX offline suites, not a claim that operational/device tests were collected.

Separate M/P, N and O acceptance reviews bind final source/test/data revisions. [Final validation](../artifacts/autoresearch/waves_mnop_20261024/final_validation.json) records those reviews, native runs, hashes, input preservation and documentary checks. Earlier errors remain: invalid model-domain treatment of stock notsent, a too-short fixture without a completion cohort, cross-host AQL threshold coupling, and four M loader regressions where direct positive fields masked nested failure/malformed evidence. The M guard now validates both representations and rejects conflicts before merging; the original RED results remain preserved. A green run does not erase failed evidence or turn a model into a physical result. No physical user action is needed for these deliverables.

## Scientific skills and local reference

Applied the locally installed `pymoo`, `simpy`, `experimental-design`, `statistical-analysis`, `statistical-power`, `scientific-critical-thinking` and `hypothesis-generation` skills. They guided bounded native algorithms, experimental-unit definitions, dependence/multiplicity, explicit model assumptions, rival explanations and validation. Existing installed library versions and seeds are recorded in artifacts; no installation or online documentation lookup is performed.

The skills request this software/method reference: Kassis,T., Agarwal,V., He,Y., Patel,D., and Brueckner,A.M. (2026), *Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents*, arXiv:2609.00065, [DOI](https://doi.org/10.48550/arXiv.2609.00065). Bibliographic metadata is reproduced from the local SKILL.md files and was not verified online under this task's explicit offline boundary. This is provenance for the procedural guidance, not empirical support for any radio mechanism or gain.


## Offline reproduction

Use the already installed local environment (Python3.12, SimPy4.1.2, pymoo0.6.2, NumPy1.26.4, SciPy1.17.1; exact versions are captured in receipts). No installation or live acquisition is required.

```powershell
python -B -m orchestration.autoresearch.fmx_offline_data --all-rounds15
python -B -m controller.optimizer.fmx_asymmetric_pareto_optimizer
python -B -m analysis.statistics.fmx_r15_and_crossover_statistical_audit --output artifacts/autoresearch/waves_mnop_20261024/wave_o_reproduced.json
```

The O CLI creates a new owned output and refuses to overwrite it; choose a fresh wave_o_*.json name for another replay. The normalized and N outputs are generated artifacts in the owned wave folder; all frozen inputs remain unchanged. The pytest receipt gives the complete twelve-file invocation. No R16 source, blocked receipt, device or network is needed to reproduce this offline delivery.
