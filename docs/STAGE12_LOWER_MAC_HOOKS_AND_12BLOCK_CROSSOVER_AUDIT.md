<!-- doc-head: October24 offline U-X lower-MAC and twelve-block crossover audit -->
Fifteen frozen R22-R26 inputs extend112 preserved records to131 and188 crossed rows/52 block IDs.
R25 focusedHolm10 accepts ten contrasts; broadHolm162/324 accepts none under stated assumptions.
Bp99 improves11/12, refuting the supplied universal12/12 claim; nine other claims are unanimous.
Exact confidence sets, period/sequence balance and factorial aliasing are independently verified.
All19 new summaries conflict with blocks; typed opt-in lower-MAC packages remain unpromoted.
595 offline tests pass; no radio, target, network-device or liveR27 operation is part of this work.
<!-- /doc-head -->

# Stage12 lower-MAC hooks and twelve-block crossover audit

Research ID: `FMX-OFFLINE-WAVES-UVWX-20261024`. Parent: the original Stage12 driver/control-authority, experimental-methodology and custom-MAC feasibility-boundary deliverables in `artifacts/2026-09-20-forward-plan.html`, and the current U-X section of [BENCH_PLAN](BENCH_PLAN.md). The analysis is retrospective and exploratory; it audits saved physical observations. It neither runs another physical experiment nor certifies device-side control authority.

## Measured answer and limits

**CONFIRMED from the frozen blocks:** R25 contains twelve supplied matched blocks, three arms, two repetitions of all six three-arm sequences, and4/4/4 treatment counts per period. The five requested outcomes for B and C versus stock produce ten explicit contrasts. Nine have12/12 improvements; **B's p99 improves11/12**, with a worse observation in block5: stock30.833ms versus B31.696ms. The operator's universal12/12 assertion is therefore **REFUTED for that contrast**. Its exact signed-rank p is0.0009765625 and exact sign-test p is0.00634765625; the other nine have both p-values0.00048828125.

**CONDITIONAL statistical result:** all ten specified R25 signed-rank contrasts survive Holm10, each with adjusted p0.0048828125. Their marginal95% and focused simultaneous confidence sets are finite. No contrast survives the broader new-round Holm162 or combined-round Holm324 families; their minimum adjusted p-values are0.0791015625 and0.158203125. Focused-family evidence does not replace the broad results or prove a portable wireless gain. The same conditional sign/rank assumptions apply to all three families.

**CONFIRMED source inconsistency:** all19 new windows disagree with their saved block means or directional summaries beyond the inherited0.021Mbps allowance. R24-R26's reported total now equals reported DL+UL, but this narrower arithmetic identity does not establish consistency with the actual repetitions. Original summaries and blocks remain untouched; no controller score is repaired to promote a package. Four new stock windows have recorded loss, including117/120 received pings in R25. The new lower-MAC controller path represents the observations and abstains from accepting them as usable promotion evidence.

**UNKNOWN:** inter-block independence, randomized treatment allocation, adequate washout, effective firmware retry behavior, precise TX-completion visibility, bounded lower-layer queues/release timing, synchronized clocks, offload behavior, and performance on independent links/sectors. Declared host controls do not pass the project's Stage4 custom-MAC gate. The earlier SimPy physical-predictor rejection and disabled optimizer proposals remain in force.

## Frozen inputs, actual units and reproducibility

All15 files were copied to the new owned folder before inspecting their contents: five JSON receipts, five matching TSVs and five recipes. The [SHA256 manifest](../artifacts/autoresearch/waves_uvwx_20261024/inputs_manifest.json) records copy times, exact names, byte counts and hashes. Subsequent measurement analysis used those copies and the prior Q-T outputs. The originals were not reopened. Recipes were read as text, not imported or executed. Antigravity owns liveRound27; this program did not inspect it, contact any radio/network device, run target code, install online dependencies or emit raw MIPS/ARM instruction dumps, hex dumps or credentials.

The truncated/escaped path and identifier text in the request was resolved against existing repository conventions: `artifacts/`, `tools/bench/`, `analysis/`, `tests/`, `force_tx_status`, `ani_enable`, `airtime_flags`, and `fq_limit`. No separate misspelled research tree was created.

| Round | New primary windows | Crossed treatment rows | Matched block IDs | Recorded design question |
|---|---:|---:|---:|---|
| R22 |4|16|4| Retry7/4 versus5/3; force_tx_status0 versus1 |
| R23 |4|16|4| ANI1 versus0; combined airtime_flags/FQ-limit package |
| R24 |4|16|4| AF-only, FQ-only and combined+retry packages; nuisance-confounded nominal factorial |
| R25 |3|36|12| Stock, AF1/FQ2048 hybrid, hybrid+retry5/3 |
| R26 |4|16|4| FTX conditional on AF1/FQ2048; retry conditional on FTX1 |
| New total |19|100|28| Saved within-link treatment observations |
| Combined R16-R26 |—|188|52| Excludes R17 from crossover pairing |

The [131-record dataset](../artifacts/autoresearch/waves_uvwx_20261024/normalized_r1_to_r26_measurements_20261024.json) contains129 primary windows and two earlier summary-only validations. All112 previous record fields, classes and policy IDs are preserved. The58/85/89/112 loader APIs remain compatible. The [combined block dataset](../artifacts/autoresearch/waves_uvwx_20261024/normalized_r16_to_r26_block_observations_20261024.json) retains the prior88 crossed rows and adds100, with52 `(round_id, block_index)` IDs. Its16 R17 sequential rows remain a separate collection and never gain synthetic crossover steps. A row is one treatment observation within a block; neither188 rows nor120 pings are188/120 independent experimental units.

Each R25 arm attempted120 pings, ten per block. Stock received117, while B and C received120. The other lossful new windows are R22 stock37/40 (7.5%), R23 stock39/40 (2.5%) and R26 stock38/40 (5%). These four windows include nine lossful blocks; none was removed. Recorded window restoration is not copied into unknown per-block restoration/station-drop fields. All19 MAC TX denominators are zero, so an effective MAC retry fraction remains unknown even when a reported field says0.0. TCP retransmits are not PER.

R22/R23 keep their pooled RTT arrays in block-concatenation order. R24/R25/R26 store sorted pools in11 windows. The new parser verifies exact equality with the sorted multiset of saved block RTTs, preserves the actual pooled ordering and each original block array, and explicitly labels lost pooled chronology. The earlier strict concatenation contract remains the default for old APIs. A changed sample, duplicate unit, boolean step ID, conflicting hook declaration or mismatched ping count fails closed. No tolerance was widened to make the new data pass.

Exact hardware revision, installed firmware build hash, physical separation and per-window RF/calibration conditions are not established by this offline audit. OpenWrt/WPA2/high-power labels are source context, not a fresh device readback. All paired results refer to saved received-ping quantiles or throughput/fairness metrics on this bench link; lost-packet latency and transport to another sector remain unresolved.

Reproduction uses the existing local Python environment and recorded versions, with no installation:

```powershell
python -B -m orchestration.autoresearch.fmx_offline_data --all-rounds26
python -B -m analysis.statistics.fmx_r22_to_r26_crossover_audit
```

The statistical CLI consumes only owned snapshots and Q-T block output. It checks dependency bytes before and after computation. The [combined pytest receipt](../artifacts/autoresearch/waves_uvwx_20261024/focused_pytest_run_1.json) contains the exact16-suite command, interpreter, environment override, exit code and current hashes.

## Statistical families and exact confidence sets

The [family plan](../artifacts/autoresearch/waves_uvwx_20261024/wave_v_families_precomputation.json) was frozen before computing new outcomes. The operator had already supplied a unanimity/p-value claim, so this was not target-blind prospective preregistration. The [complete analysis](../artifacts/autoresearch/waves_uvwx_20261024/wave_v_r22_to_r26_crossover_analysis.json) and [V methods](../artifacts/autoresearch/waves_uvwx_20261024/wave_v_methods.md) retain all contrasts, non-rejections, quality limits and confidence-set components.

| Explicit retrospective family | Contrasts | Holm rejections at0.05 | Minimum adjusted p |
|---|---:|---:|---:|
| Requested R25 B/C versus stock × p50,p95,p99,UL,Jain |10|10|0.0048828125 |
| New R22-R26:27 pairs × six outcomes |162|0|0.0791015625 |
| Combined R16,R18-R26:54 pairs × six outcomes |324|0|0.158203125 |

The six broad-family outcomes are total goodput, p50, p95, p99, UL goodput and Jain fairness. The focused ten deliberately omit total goodput because they reproduce the operator's five named claims; the throughput cost is still reported below and included in the broader families. No unadjusted, focused or historical Holm81 result substitutes for a broad discovery. The separate sign tests are sensitivity checks, not additional unadjusted confirmatory claims.

Differences are treatment minus control within genuine round-scoped block IDs. Equal-weight repeated arm observations are averaged within a block first; missing arms/outcomes and unbalanced counts are explicit exclusions rather than newly invented pairs. Exact Wilcoxon probabilities use doubled tie-aware midranks, Wilcox zero removal and the complete conditional sign distribution. Exact sign tests condition on nonzero signs. Walsh averages estimate a paired pseudomedian; their n(n+1)/2 derived terms are not independent observations.

For n12 without zeros,4096 sign assignments yield the minimum two-sided p2/4096=0.00048828125. This makes the first Holm10 threshold0.005 attainable but not the first Holm162 threshold0.000308642 or Holm324 threshold0.000154321. These are attainability limits, not80% power or sample-size sufficiency. No observed power, invented effect size or unapproved physical replication is presented. A prospective experiment would need its own operator-approved estimand, practical effect, independent-unit assumptions and matching power calculation.

Exact confidence sets invert the same conditional signed-rank test at all Walsh breakpoints and intervening cells. Open/closed endpoints, singleton atoms, disconnected components and infinities are retained. The method assumes independent symmetric location-shift block differences for the usual shift interpretation; saved IDs or counterbalancing do not establish that assumption. A conservative hull is available but is not silently substituted for the exact set.

All focused R25 marginal95% sets are finite. The focused simultaneous95% family bounds use Bonferroni10, each at marginal99.5%; they are also finite and exclude zero. The broader Bonferroni162/324 sets are the whole real line at these block counts. A finite interval in the smaller family cannot be advertised as a finite broad-family interval.

### R25 effects and the refuted unanimity claim

Arm A is the stock package. B combines asymmetric queue/CoDel/TSQ/steering settings with AF1/FQ2048 and retry7/4. C is the hybrid plus retry5/3. These are complete observed packages; B versus stock does not isolate AF, FQ limit or asymmetry alone. HL values and confidence sets below are conditional shifts from the saved blocks.

| Outcome | B-minus-stock HL | B focused simultaneous95% set | C-minus-stock HL | C focused simultaneous95% set |
|---|---:|---|---:|---|
| p50 (ms) | -17.80925 | (-21.856,-13.868] | -19.36125 | [-21.835,-14.4605) |
| p95 (ms) | -23.38025 | [-33.329,-11.2245] | -27.0125 | [-40.151,-16.804] |
| p99 (ms) | -24.138 | [-36.9075,-10.1365] | -28.0035 | (-41.9565,-13.108] |
| UL (Mbps) | 10.35 | [7.65,12.3] | 10.225 | [7.7,11.7) |
| Jain | 0.126025 | (0.0993,0.1501] | 0.1406 | [0.11515,0.15655] |

Nine of the ten named comparisons have12/12 favorable differences and both raw exact p-values0.00048828125. Bp99 has11 favorable, one unfavorable, zero equal blocks: in block5 B31.696ms exceeds stock30.833ms by0.863ms. Its rank p0.0009765625 differs from sign p0.00634765625 because the unfavorable difference has a small rank. It still survives the specified signed-rank Holm10 family, but its broader adjusted p-values are0.1484375 and0.306640625. The assertion that every named contrast has p2/4096 is false.

Aggregate goodput prevents a latency-only reading: B-minus-stock HL is-0.15Mbps, with a marginal exact set containing zero and an isolated accepted atom (`{-2.0} union (-1.25,0.25]`). C-minus-stock HL is-5.45Mbps, with marginal set approximately(-6.9,-4.3]Mbps. These are reported even though total goodput is outside the focused ten; neither broad family accepts a global throughput or latency gain. No equivalence/noninferiority margin was specified or established.

![R25 blocks and multiplicity](../artifacts/autoresearch/waves_uvwx_20261024/r25_blocks_and_multiplicity.svg)

The [plot script](../artifacts/autoresearch/waves_uvwx_20261024/wave_x_make_figure.py) and [figure receipt](../artifacts/autoresearch/waves_uvwx_20261024/wave_x_figure_receipt.json) bind the saved block data and full analysis. Each line is a matched block on one link; the plot uses block values, not repaired summaries. Visualization was retrospective descriptive work.

## Period/carryover and factorial identifiability

R25's saved positions match its declared schedule. Each of the six permutations appears once in each six-block cycle, giving two copies overall. Each treatment appears four times in each period. The24 contiguous within-block transitions contain each distinct directed treatment pair four times. The stated model matrix with block effects, period effects, current-treatment indicators and categorical previous-treatment indicators has rank18/18 in36 observations, leaving18 residual degrees of freedom before adding other structure.

This is count balance and algebraic estimability in a simplified model. Sequence is fixed within block and aliases block fixed effects if added independently. Recorded waits do not prove effective completion or washout, inter-block dependence may remain, and a full-rank lag model is not a no-carryover test. The file name`abba` does not turn this three-treatment Williams-style schedule into a two-treatment ABBA design.

| Audit | What is estimable from the declared cells | What is not identified |
|---|---|---|
| R24 nominal AF×FQ matrix | Four-arm package contrasts; nominal rank4/4 | Pure AF/FQ main effects and interaction after the stock queue-package and changed retry nuisances |
| R24 nuisance-adjusted matrix | Rank4 with six columns exposes aliasing | Queue-package indicator equals AF+FQ-AF×FQ; changed-retry indicator equals AF×FQ |
| R26 hybrid FTX×retry matrix | C versus B changes only declared FTX; D versus C changes the declared retry pair | Missing FTX0+changed-retry hybrid cell; rank3/4; retry and interaction columns identical |

R24 uses stock A, AF-only hybrid B, FQ-only hybrid C and combined AF/FQ+retry6/3 hybrid D. Stock A's endpoint queue settings differ from the hybrid cells, and D changes retry as well as the AF/FQ combination. A nominal2×2 table cannot remove these simultaneous changes. R26 provides a clean declared FTX conditional package contrast and a retry conditional contrast, but effective hardware isolation is still unverified and the interaction is not recoverable from the missing hybrid cell. Stock A cannot fill that cell because its base package differs.

The result is an explicit unresolved causal question with concrete missing evidence, not a fabricated interaction coefficient. No extra physical factorial experiment was run or queued by this offline program.

## Typed lower-MAC hooks and advisory control boundary

The [normalizer](../orchestration/autoresearch/fmx_offline_data.py) retains six exact optional integer fields. They are shared declarations for AP and CPE in these recipes; absent fields remainNone and do not inherit stock defaults. The complete joint-policy identity includes all six for both endpoints as well as existing per-AC queues, cross-layer settings, ACK/VI fields and burst sizes.

| Field | Parser representation domain | Frozen source boundary |
|---|---|---|
| short_retry_limit / long_retry_limit |0..255, integer only | Host retry-setting request and saved PHY debugfs context; firmware behavior unknown |
| force_tx_status |0 or1, integer only | Saved host PHY force-status flag; no per-frame completion/timing proof |
| ani_enable |0 or1, integer only | ath10k debugfs declaration; effective ANI behavior not independently verified |
| airtime_flags |0..3 integer bitmask | mac80211 host airtime setting context; no custom TDMA authority |
| fq_limit |1..2^32-1, integer only | Host AQM/FQ setting declaration; no hardware queue-depth bound |

These ranges encode input values; they are **not safe physical operating ranges**. True/False, numeric strings and floats do not alias integer controls. Zero and unknown are distinct. Declared hook values and saved readback envelopes are retained as source evidence, not promoted into proof of target efficacy.

The [controller](../controller/adaptive_aql_regime_controller.py) adds the explicit opt-in path:

```python
from orchestration.autoresearch.fmx_offline_data import load_all26_measurements
from controller.adaptive_aql_regime_controller import AdaptiveAQLRegimeController

records, source_refs = load_all26_measurements()
controller = AdaptiveAQLRegimeController(records, include_lower_mac=True)
```

Lower-MAC opt-in implies the ACK-aware representation. Default callers and callers using only the earlier three-tier option retain their selections, policy IDs and scoring behavior. Six exact optional query constraints apply before support, ranking and hysteresis; omission is unconstrained, explicitNone matches unknown only, and integer0 matches declared zero. No individual knob is synthesized into a new policy.

Legacy unknown-hook packages are canonicalized consistently in opt-in mode, preventing an older negative observation from re-entering through a new schema alias. Source-consistency checks remain fail-closed; missing or false consistency cannot become a usable lower-MAC candidate. The [nine executed examples](../artifacts/autoresearch/waves_uvwx_20261024/wave_w_offline_examples.json) and [W methods](../artifacts/autoresearch/waves_uvwx_20261024/wave_w_methods.md) preserve exact source IDs, exclusions and abstention reasons. All19 newly inconsistent windows remain unpromoted, alongside the prior23 inconsistencies. Genuine loss negatives remain loss negatives; a summary discrepancy is not mislabeled as a wireless failure. Valid disposable fixtures verify the new selection path.

Known lower-hook queries abstain on this actual corpus. Unknown-only queries may select older supported packages with unknown controls; that is not acceptance of a new R22-R26 treatment. No method here writes a radio configuration. Force-status or retry declarations do not establish the eight Stage4 prerequisites for a custom MAC: precise completion, bounded queues/release, clocks, ACK/retry interaction, management survival, missed-slot recovery and timing/GPS access remain unqualified by this audit.

## Verification, scientific guidance and disposition

The fresh combined run passed **595 tests across16 offline suites**, with zero failures, errors or skips and exit0:501 prior cases plus40 U,24 V and30 W. The [pytest receipt](../artifacts/autoresearch/waves_uvwx_20261024/focused_pytest_run_1.json) binds the current code. Independent U and W reviewers ran163 and142 affected cases respectively and replayed normalization/example evidence. The independent V review used the current combined run plus a separate oracle verifying324 contrasts,648 exact rank/sign probabilities,324 HL estimates,820 confidence sets and26962 acceptance-set probes. No numerical suite was rerun for documentation-only changes.

The [independent V review](../artifacts/autoresearch/waves_uvwx_20261024/review_wave_v.json), [independent U review](../artifacts/autoresearch/waves_uvwx_20261024/review_wave_u.json), [independent W review](../artifacts/autoresearch/waves_uvwx_20261024/review_wave_w.json), and [final validation](../artifacts/autoresearch/waves_uvwx_20261024/final_validation.json) preserve separate implementation and acceptance. V's boolean-versus-zero declaration regression and W's initial constraint failures remain archived with their fixes. No failed result was discarded and no acceptance threshold was reduced. Unchanged prior Q-T output artifacts remain revision-bound historical evidence; new source acceptance is bound to this program's receipts.

The four requested local skills materially guided the work: [statistical-analysis](../.agents/skills/statistical-analysis/SKILL.md) for outcomes, families, effect estimates and exact uncertainty; [statistical-power](../.agents/skills/statistical-power/SKILL.md) for attainable p-values and avoiding observed power; [experimental-design](../.agents/skills/experimental-design/SKILL.md) for genuine units, sequence balance and factorial aliasing; [scientific-critical-thinking](../.agents/skills/scientific-critical-thinking/SKILL.md) for source contradictions, proxy limits and causal boundaries. No online literature verification was performed under the operator's offline instruction.

The installed skill metadata requests attribution to Kassis,T., Agarwal,V., He,Y., Patel,D., and Brueckner,A.M.(2026), *Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents*, arXiv:2609.00065, DOI10.48550/arXiv.2609.00065. This entry is transcribed from local SKILL.md metadata and was not independently verified online; it does not validate this audit's conclusions.

**Disposition:** KEEP the source-preserving normalizer, exact statistical tools and opt-in advisory representation. Retain the focused R25 evidence with its p99 counterexample, finite focused confidence sets, throughput tradeoffs, source conflicts and broader-family non-rejections. Do not promote a new lower-MAC package, claim isolated factorial interactions, global wireless gains or Stage4 success. Missing historical local binaries complete`UNKNOWN_LOCAL_ARTIFACT_ABSENT` checks without stalling. No physical user action is required for this completed offline scope. Device/source-summary clarification or independent replication is a separate operator-controlled bench task; no radio access, target execution, flash, deployment, commit/push or background acquisition occurred or is queued here.
