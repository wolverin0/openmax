<!-- doc-head: October24 offline AG-AJ dyadic and utility audit -->
Fifteen frozen inputs yield 194 records, 700 crossed rows and 262 matched IDs.
All ten new arms have rational and NumPy means exactly equal with zero ULP error.
R45/R47 improve five outcomes in 16/16 blocks but lose 6.43%/11.54% total goodput.
Strict two-percent utility rejects both; directional eligibility is offline only.
R46 p95 is 14/16, not 15/16; full period/carryover models retain rank 18/19.
A reproduced host-only owner/epoch race was repaired without weakening safety gates.
<!-- /doc-head -->

# Stage12 R43-R47 dyadic zero-ULP, exact sign-flip and utility audit

The AG/AH/AI/AJ offline program is complete as an evidence and implementation audit. **CONFIRMED from saved receipts:** all ten new arms have exact recorded-decimal rational means, exact NumPy float64 means and zero ULP error on goodput, DL, UL and Jain, with 160/160 pings per arm. R45 and R47 improve all five requested latency/UL/fairness outcomes in every matched block. **CONFIRMED adverse result:** their mean total goodput falls 6.4322% and 11.5425%, so both fail the prespecified strict two-percent preservation rule. The directional mode permits these costs and qualifies them only for conditional offline eligibility.

**REFUTED:** R46 p95 improves in 14/16 blocks, not the supplied 15/16; R39's saved target MAC counter ratio is approximately 1.57395%, not 0.21%. A completed audit preserves these failed premises rather than rewriting input values or asserting universal source correctness.

The parent is the original Stage12 control-authority, experimental-methodology and custom-MAC feasibility boundary in [the forward plan](../artifacts/2026-09-20-forward-plan.html) and the top section of [BENCH_PLAN](BENCH_PLAN.md). The [full frozen specification](../artifacts/autoresearch/waves_ag_to_aj_20261024/inputs/waves_ag_to_aj_20261024_spec.md) governs this delivery. Earlier CURRENT/ACTIVE entries are historical for this scope and authorize no automatic resumption of physical work.

## Scope and provenance

All five JSON receipts, five TSVs and five recipe files were copied before content inspection. [The input manifest](../artifacts/autoresearch/waves_ag_to_aj_20261024/inputs_manifest.json), SHA256 `02fe7cf6fcae66de4ad2c7f932ed1388c6d8d84341f7d1e5cc183d97655a8346`, binds those fifteen snapshots. Recipe files supply source provenance and are never imported or executed. Original-path pointers are documentary. R48+ contents are outside the read/hash/analysis scope.

No radio, network device, daemon, monitor, background bench runner, SSH session, target-device operation, online installation, flash, deployment, credential action, merge or push belongs to this work. The 72-hour monitor and live bench runner were not inspected, stopped, restarted or controlled. Local Python and pytest processes use saved data and disposable host fixtures only. There is no background acquisition from this task.

The control layer is external-controller analysis of saved Linux/mac80211/ath10k-facing declarations. AQL thresholds are not WMM EDCA TXOP/CW/AIFS. Retry, FTX, queue and airtime fields do not independently prove QCA-firmware or hardware control authority. Proprietary airMAX behavior is not reproduced. Stage4 remains NOT_PASSED, previous rejected models stay rejected, and model actuation remains disabled.

## AG: additive corpus and exact means

The [schema9 corpus](../artifacts/autoresearch/waves_ag_to_aj_20261024/normalized_r1_to_r47_measurements_20261024.json) contains **194 records: 192 primary windows and two prior auxiliary summaries**. The [block corpus](../artifacts/autoresearch/waves_ag_to_aj_20261024/normalized_r16_to_r47_block_observations_20261024.json) contains **700 crossed rows in 262 round-scoped matched IDs**, plus 16 separate R17 sequential rows. R43-R47 add ten arm summaries and 160 actual block windows in 80 matched units. The five-second duration is a recipe declaration, not a new wall-clock measurement by this offline task.

All 184 prior normalized record dictionaries, 540 prior crossed rows and 16 sequential rows are unchanged. The latest `load_normalized_records()` and `load_crossed_block_records()` now reach R47; `load_all42_*` and older APIs stay fixed. The additive `ROUND_SPECS` catalog declares the five new regimes. One prior R42 count test now invokes the fixed42 API explicitly; all its assertions and parameterizations remain. [Preservation checks](../artifacts/autoresearch/waves_ag_to_aj_20261024/preservation_checks.json) retain the original snapshots and test-body comparison.

| Round | Workload | Flows | Bidir | Arms | Blocks/arm | Received pings/arm |
| --- | --- | --- | --- | --- | --- | --- |
| R43 | unidir_dl_2flow | 2 | False | 2 | 16 | 160 |
| R44 | unidir_dl_2flow | 2 | False | 2 | 16 | 160 |
| R45 | bidir_6flow | 6 | True | 2 | 16 | 160 |
| R46 | unidir_ul_2flow | 2 | False | 2 | 16 | 160 |
| R47 | bidir_8flow | 8 | True | 2 | 16 | 160 |

The [dyadic helper](../orchestration/autoresearch/fmx_offline_data.py) independently reports four distinctions: recorded-decimal `Fraction` mean deltas, `np.mean(dtype=float64)` deltas, IEEE-754 representable-step distance, and exact binary-rational arithmetic. A nonzero rational delta is never rounded away. Numeric equality treats signed zeros alike. The source's decimal values are also checked for power-of-two denominators and exact binary64 representability, rather than inferring dyadic granularity from a filename.

All ten new arms, including both R43 arms, satisfy `DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP`: all four rational deltas are `'0'`, all four NumPy deltas are `0.0`, all four ULP distances are zero and the exact binary-rational mean deltas are zero. This is stronger than the eight explicitly named R44-R47 arms. One-ULP perturbations are rejected. Reapplying this helper to the older R41 data does not erase its small NumPy reduction differences; the prior rational/Python-sum result remains a different, preserved contract.

All ten retain chronological block-concatenated RTT pools, positive per-block/window WDS denominators and exact packet/retry counter sums. Both arms in each new round report zero loss, zero station drops and successful restoration. These are recorded reports, not independent device, restoration or counter-interface acceptance. The counters name `phy0-ap0.sta1` through frozen recipe provenance. Unknown physical range remains unknown; coverage6/13 in the earlier corpus means programmed timing, not measured 3km/6km separation.

## AH: exact statistics and family scope

The [AH implementation](../analysis/statistics/fmx_r43_to_r47_dyadic_zero_loss_audit.py) and [bound result](../artifacts/autoresearch/waves_ag_to_aj_20261024/wave_ah_dyadic_zero_loss_analysis.json) audit six metrics per round: total GP, p50, p95, p99, UL and Jain, giving 30 primary contrasts over 80 genuine matched block units. RTT samples are subsamples; ten arm summaries are not ten independent sector trials. Pure unidirectional constant/opposite-flow metrics remain explicitly degenerate. Total GP and UL in pure UL are algebraically identical, correlated tests, not extra measurements.

For every contrast the implementation actually enumerates all **65,536** sign assignments. It computes three distinct two-sided statistics: signed doubled midrank sum, positive-minus-negative sign count, and arithmetic mean of signed differences. The mean tail uses exact integer sums of the supplied float differences represented as binary rationals; no epsilon or floating comparison changes a tail count. Zeros repeat assignment multiplicities correctly. A separate source-decimal sensitivity agrees with the primary rank/mean p-values for all 30 actual contrasts.

HL estimates use Walsh averages; marginal 95% and 99.9% confidence sets invert the exact signed-rank test at every breakpoint and intervening cell, preserving endpoints and any disconnected components. They are not simultaneous confidence regions. Conditional symmetry/sign-exchangeability and block independence are assumptions, not conclusions from the IDs or small p-values.

The [family recipe](../artifacts/autoresearch/waves_ag_to_aj_20261024/wave_ah_family_recipe.json) was frozen before outcome inference. The 30 primary rank tests are conservatively completed to a scoped family of 500 using 470 p=1 placeholders. Prior 747 plus 30 gives a complete known **rank** scope of 777; full-known Holm500 is inapplicable. The 30 secondary arithmetic-mean flip tests receive a separate scoped500 family. Sign-count results are diagnostics on the same observations. These separate analyses do not claim one global familywise guarantee across every statistic or all project research.

| Family | Known | Declared size | Two-sided rejections at .05 |
| --- | --- | --- | --- |
| new_rank30_bound500 | 30 | 500 | 17 |
| complete_known_rank777_bound777 | 777 | 777 | 52 |
| new_meanflip30_bound500 | 30 | 500 | 17 |

The 17 new scoped rejections include adverse goodput effects and algebraically redundant outcomes; they are not 17 independent improvements. No old/new package pooling is performed. In particular, R45's AP BE1100/2200 and CPE BE2200/4400 package differs from R41/R42, which used AP1500/3000 and CPE2100/4200 alongside different queue/timing declarations. Effect evidence is not transferred between them.

## Requested claims and saved outcomes

R45 and R47 each have **16/16 favorable blocks on p50, p95, p99, UL and Jain**. Every requested contrast has rank, sign and arithmetic-mean flip tail count 2/65536, p=0.000030517578125. Primary scoped Holm500 q=0.0152587890625 and complete-known Holm777 q=0.02325439453125. Both current controls and targets have 160/160 pings, zero saved packet loss and exact dyadic means. Their candidate counter retry fractions are lower: R45 1067/543926=0.196166% versus 1392/674823=0.206276%; R47 862/486824=0.177066% versus 1305/650506=0.200613% (rounded percentages).

R44 has 16/16 p50 and p95 wins; its p99 is 14/16 and fails broad rank Holm500 (q=0.2055053711). R43 p50 is 16/16; p95 is 14/16 and p99 12/16, so the complete unidirectional QoE conjunction is not established. R43's actual target counter fraction is 1505/757212=0.198755%, lower than stock 0.210547%, but not exactly the specification's 0.198821%. R44's candidate ratio is slightly higher than its control despite fewer absolute retry events, demonstrating why event counts alone are not a rate comparison.

| Round | Outcome | Favorable | Rank tails/65536 | Sign tails/65536 | Mean tails/65536 | Rank Holm500 q |
| --- | --- | --- | --- | --- | --- | --- |
| R43 | p50_rtt_ms | 16/16 | 2 | 2 | 2 | 0.01525878906 |
| R43 | p95_rtt_ms | 14/16 | 602 | 274 | 584 | 1 |
| R43 | p99_rtt_ms | 12/16 | 1196 | 5034 | 1344 | 1 |
| R43 | ul_goodput_mbps | 0/16 | 65536 | 65536 | 65536 | 1 |
| R43 | jain_fairness | 0/16 | 65536 | 65536 | 65536 | 1 |
| R44 | p50_rtt_ms | 16/16 | 2 | 2 | 2 | 0.01525878906 |
| R44 | p95_rtt_ms | 16/16 | 2 | 2 | 2 | 0.01525878906 |
| R44 | p99_rtt_ms | 14/16 | 28 | 274 | 22 | 0.2055053711 |
| R44 | ul_goodput_mbps | 0/16 | 65536 | 65536 | 65536 | 1 |
| R44 | jain_fairness | 0/16 | 65536 | 65536 | 65536 | 1 |
| R45 | p50_rtt_ms | 16/16 | 2 | 2 | 2 | 0.01525878906 |
| R45 | p95_rtt_ms | 16/16 | 2 | 2 | 2 | 0.01525878906 |
| R45 | p99_rtt_ms | 16/16 | 2 | 2 | 2 | 0.01525878906 |
| R45 | ul_goodput_mbps | 16/16 | 2 | 2 | 2 | 0.01525878906 |
| R45 | jain_fairness | 16/16 | 2 | 2 | 2 | 0.01525878906 |
| R46 | p50_rtt_ms | 12/16 | 1402 | 5034 | 1344 | 1 |
| R46 | p95_rtt_ms | 14/16 | 14 | 274 | 12 | 0.1029663086 |
| R46 | p99_rtt_ms | 15/16 | 10 | 34 | 8 | 0.07369995117 |
| R46 | ul_goodput_mbps | 0/16 | 2 | 2 | 2 | 0.01525878906 |
| R46 | jain_fairness | 0/16 | 65536 | 65536 | 65536 | 1 |
| R47 | p50_rtt_ms | 16/16 | 2 | 2 | 2 | 0.01525878906 |
| R47 | p95_rtt_ms | 16/16 | 2 | 2 | 2 | 0.01525878906 |
| R47 | p99_rtt_ms | 16/16 | 2 | 2 | 2 | 0.01525878906 |
| R47 | ul_goodput_mbps | 16/16 | 2 | 2 | 2 | 0.01525878906 |
| R47 | jain_fairness | 16/16 | 2 | 2 | 2 | 0.01525878906 |

R46 p95 improves in **14/16**, not 15/16. Its rank/sign/mean tail counts are 14/274/12 out of 65536. R46 p99 is 15/16 with counts 10/34/8. Thus the supplied 34/65536 is the p99 **sign-count** p-value, not a general signed-rank or arithmetic-mean p-value, and it does not apply to p95. Neither p95 nor p99 rank contrast passes scoped500 (q=0.1029663086 and 0.07369995117). The result and failed premise remain visible in the tests and report.

The saved R46 pooled-window p95 falls 42.0633% and p99 falls 55.0155% versus its own stock, while UL falls 65.275390625 to 58.0390625 Mbps (-11.0858%) and retry-event fraction rises 1.56218% to 4.69710%. The older R39 target has 64.125 Mbps UL and a counter fraction 2055/130563=**1.57395%**, refuting 0.21%. R39 and R46 differ in full policy and have no shared matched block identities; their cross-round comparison is descriptive, not a paired or causal test. The 43.299% reduction of R46's `fmx_loss` objective is not a packet-loss reduction: both arms' packet loss is zero.

## Period adjustment and carryover boundary

Every new receipt has eight AB and eight BA blocks, exact schedule conformity and balanced treatment counts by period. Independent Fraction Gaussian elimination confirms that the full block/period/current/lag design has rank **18/19** for all five rounds. Current-treatment and lag effects cannot be separately certified by silently discarding an aliased column.

AH also executes a named, identified **block fixed effects + period + current treatment, assuming no differential carryover** submodel. Its 18 columns have rank 18. Exact decimal coefficients are `(mean_AB_difference + mean_BA_difference)/2` for the restricted direct estimate and `(mean_AB_difference - mean_BA_difference)/2` for the period estimate, cross-checked against least squares for all 30 metrics. They are conditional estimates under that restriction. Raw difference sign-flip p-values are not relabeled period-adjusted causal p-values when a period nuisance exists. A synthetic counterexample and alias tests preserve this distinction. Count balance does not establish random allocation, washout, no carryover, independent links or physical performance acceptance.

## AI: source-bound utility modes and selector

The [new six-regime selector](../orchestration/autoresearch/fmx_multi_regime_dyadic_selector.py) adds no network or actuator. It accepts three explicit immutable evidence views (Z, AD and AH), each tied to an externally accepted statistics-receipt SHA256. It verifies every source manifest and exact preservation of prior records/blocks in the current view; original-source pointers are not followed. The union of all three verified manifests resolves old provenance explicitly, rather than assuming prior files are absent or recursively opening advertised paths. Prior selector and gate modules remain unchanged.

The [utility contract](../artifacts/autoresearch/waves_ag_to_aj_20261024/wave_ai_prespecified_contract.json) was fixed before actual evaluation. Both modes require the same exact complete package/context, one target/control pair and all source units for one round; current control AND target must report zero loss/drop, successful restoration, chronological RTT membership, positive exact MAC sums, four rational/NumPy zero-ULP means, and a strictly lower candidate counter retry fraction. Historical true target-package/context negatives remain quarantining, including per-block health. Old stock failures do not globally quarantine unrelated healthy current stock comparisons.

Both modes require direct favorable HL effects and authenticated scoped rank Holm500 support for all five bidirectional latency/UL/Jain outcomes. Unidirectional modes require three RTT outcomes and the correct directional GP outcome, with exact algebraic direction identity; they do not require improvement in constant Jain or an absent opposite flow. All required outcomes must share the same complete control and unit set. No cross-regime or new-AQL/retry/coverage transfer is implemented.

STRICT is the default and additionally requires the target's observed total GP mean to be at least 98% of control, evaluated with exact rational arithmetic at the boundary. DIRECTIONAL retains the common source/statistical conjunction while allowing total GP cost. Neither mode is a statistical noninferiority test or independent physical qualification. Eligible policies are ranked deterministically by saved target p95, descending total GP, exact policy ID and round; no synthetic package is created.

| Round | Stock GP Mbps | Target GP Mbps | GP change | STRICT | DIRECTIONAL |
| --- | --- | --- | --- | --- | --- |
| R41 | 108.11250000 | 103.10625000 | -4.6306% | BLOCKED | BLOCKED |
| R42 | 108.68125000 | 107.28750000 | -1.2824% | BLOCKED | BLOCKED |
| R45 | 108.25000000 | 101.28710938 | -6.4322% | BLOCKED | ELIGIBLE_OFFLINE_DIRECTIONAL |
| R47 | 107.82128906 | 95.37597656 | -11.5425% | BLOCKED | ELIGIBLE_OFFLINE_DIRECTIONAL |

R45 and R47 fail STRICT solely because total GP loss exceeds 2%; they pass DIRECTIONAL within their explicit saved-link scopes. R41 fails both-arm zero-ULP means, and STRICT also fails its GP floor. R42 passes the GP floor but retains a lost control ping and candidate NumPy-mean error, so neither mode qualifies. This does not rewrite the older, less strict offline eligibility result from AC-AF.

The [actual matrix](../artifacts/autoresearch/waves_ag_to_aj_20261024/wave_ai_evaluation.json) evaluates R39/R41/R42/R43/R44/R45/R46/R47 under both modes: 16 direct comparisons yield 14 BLOCKED and two directional-eligible results. The six-regime selector has 12 mode/regime examples: 10 BLOCKED and two directional-eligible selections, R45 for 6-flow and R47 for 8-flow. The DL/UL/coverage regimes remain blocked under their actual evidence; no missing criterion is replaced with a favorable result from another regime. Eligibility is not execution, production approval or independent sector acceptance.

![Each saved treatment relative to its own stock; GP cost and QoE gains remain separate](../artifacts/autoresearch/waves_ag_to_aj_20261024/r41_r42_r45_r47_observed_utility_tradeoffs.png)

The [standard Matplotlib generator](../artifacts/autoresearch/waves_ag_to_aj_20261024/wave_aj_make_figure.py) and [figure receipt](../artifacts/autoresearch/waves_ag_to_aj_20261024/wave_aj_figure_receipt.json) bind all plotted values. The PNG was visually inspected locally. These are saved window means/pooled p95 values relative to each round's own stock, not a randomized comparison between policies or workload regimes. R45's UL mean gain is 80.3678%; R47's is 60.6687%, while their aggregate goodput costs remain adverse and statistically visible.

## Verification and independent acceptance

Affected local suites pass: AG 182 cases (148 prior file cases +34 new), AH 24 and AI 136, each exit0. The fresh [complete first-party offline run](../artifacts/autoresearch/waves_ag_to_aj_20261024/full_offline_pytest_run_3.json) has **2021 PASS, 5 SKIP, zero failures/errors, exit0**, elapsed 112.875s. The [actual passed research node IDs](../artifacts/autoresearch/waves_ag_to_aj_20261024/focused_regression_from_full_suite.json) give 1026 PASS = 832 prior + 34 AG + 24 AH + 136 AI, with no research skips or failures. Every prior 832 passed node ID is present; no test was removed to obtain a pass.

The [suite boundary](../artifacts/autoresearch/waves_ag_to_aj_20261024/full_suite_offline_boundary.json) includes all configured first-party offline roots and 89 test files. Only the real Rocket acquisition test and nested third-party research checkout/virtualenv external-service tests are excluded. The five skips need the absent held Flent runtime. Literal unfiltered pytest is not claimed. A process-local inherited guard prevents nonloopback network/DNS and SSH-style subprocesses; its denial log is empty. Global configuration and pytest.ini are unchanged. Disposable host WSL fixtures retain their original timeouts/assertions.

One initial AI fixture failure remains preserved: a shared Python reference accidentally changed a fixture manifest, and the binding loader correctly rejected it. The repair deep-copied the fixture. Independent review then found two material bypasses despite the first full suite passing. Generic workloads validated coverage only for named coverage aliases, incorrectly allowing a target with class 6 and a control with class 13. Historical restoration and failure fields also accepted malformed values such as integer 0 or a string instead of a boolean. The repaired selector validates every declared coverage class, distance and provenance under both utility modes, requires identical control/target coverage knowledge, and rejects malformed historical health metadata. Legitimate legacy None/absent values remain explicitly UNKNOWN rather than invented failures; actual negative history still quarantines its exact package/context. Version 1 artifacts, both independent BLOCK proofs and the failing regression run remain archived; no gate was weakened. The final affected suite and a fresh full run on the repaired source pass. AH's false R46 source premise is a qualified research result, not a discarded unit-test failure or an edited measurement.

Full run 2 preserved an additional baseline host-fixture failure: 2,019 PASS, one FAIL, five SKIP. The recording-only watchdog published its owner file before establishing its monotonic epoch, so a concurrent health writer could produce a valid report that the replay gate then rejected as too early. [Independent controlled diagnosis](../artifacts/autoresearch/waves_ag_to_aj_20261024/review_wave_ai_watchdog_diagnosis_r2.json) reproduced that ordering. A deterministic regression failed against the original source (36 PASS, one FAIL); the minimal canonical host-source correction initializes the epoch/deadlines before owner publication. [Affected checks](../artifacts/autoresearch/waves_ag_to_aj_20261024/watchdog_epoch_pytest_run_2.json) then pass all 37 cases. All original test bodies, replay validation, fixture deadlines and immutable public-kit source remain unchanged. The archived standalone kit retains its historical version and is not requalified by tests invoking the canonical CLI. This necessary AJ verification repair neither operates a running daemon nor adds any production driver. [Independent acceptance](../artifacts/autoresearch/waves_ag_to_aj_20261024/review_watchdog_epoch_support.json) binds the narrow delta; run 3 follows this causal change, not an unchanged retry until green.

Independent [AG source acceptance](../artifacts/autoresearch/waves_ag_to_aj_20261024/review_wave_ag.json), [AH statistical acceptance](../artifacts/autoresearch/waves_ag_to_aj_20261024/review_wave_ah.json), [AI controller acceptance](../artifacts/autoresearch/waves_ag_to_aj_20261024/review_wave_ai.json) and [AJ documentary acceptance](../artifacts/autoresearch/waves_ag_to_aj_20261024/review_wave_aj_documentation.json) remain separate from implementation. Root AH review uses independent scalar rank polynomials and integer subset-count distributions, not production Gray-code enumeration: 30 contrasts, 90 exact tails, 480 source pairs, 30 HL estimates, 60 confidence sets, 11596 membership cells, 30 exact restricted period coefficients, three Holm families and five rational-rank designs all match. Source-bound owner tests may be explicitly reused by reviewers; the broader suite and numerical replays are fresh.

The [final validation](../artifacts/autoresearch/waves_ag_to_aj_20261024/final_validation.json) and [final seal](../artifacts/autoresearch/waves_ag_to_aj_20261024/final_seal.json) bind current source/artifact hashes, all eight documentary scopes and resolved links. Documentation bytes use explicit LF serialization, avoiding ambiguous line-ending hash claims. All earlier AC-AF artifacts remain immutable.

## Decisions and remaining boundary

KEEP the 194-record corpus, exact dyadic/ULP helper, all 65536-assignment audits, explicit carryover alias and restricted estimates, layered source trust and deterministic dual utility modes. REFUTE the supplied R46 p95 count and R39 retry-rate premise. KEEP R45/R47 directional eligibility separate from STRICT rejection and the aggregate GP cost. No source summary, acceptance threshold or test was changed to create positive utility evidence.

This completes the authorized offline deliverables with qualified source findings. No physical operator action is needed to finish this task. Independent same-regime sector replication, physical range, effective queue/firmware/timing authority and any real canary operation remain under their existing operator-controlled plans. E2, optional tuning, custom firmware/MAC experiments and autonomous actuation remain parked; no task runner resumes them automatically.

## Method references

The installed Scientific Agent Skills guide units, multiplicity, power/precision and causal separation: [statistical-analysis](../.agents/skills/statistical-analysis/SKILL.md), [statistical-power](../.agents/skills/statistical-power/SKILL.md), [experimental-design](../.agents/skills/experimental-design/SKILL.md) and [scientific-critical-thinking](../.agents/skills/scientific-critical-thinking/SKILL.md). Local metadata requests attribution to Kassis, T., Agarwal, V., He, Y., Patel, D., and Brueckner, A. M. (2026), *Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents*, arXiv:2609.00065, DOI10.48550/arXiv.2609.00065. This is transcribed installed metadata and was not independently verified online under the offline boundary.
