<!-- doc-head: STAGE29A_DEEP_FIRMWARE_AND_KNOB_MINING_SYNTHESIS.md continuation 2 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE29A_DEEP_FIRMWARE_AND_KNOB_MINING_SYNTHESIS.md) | Part 2/2
<a id="stage29a-deep-firmware-and-knob-mining-synthesis"></a> [Stage29A: deep firmware and knob mining synthesis](STAGE29A_DEEP_FIRMWARE_AND_KNOB_MINING_SYNTHESIS_CONTINUATION_a8bdad0aa1_001.md#stage29a-deep-firmware-and-knob-mining-synthesis) | <a id="prespecified-question-and-acceptance"></a> [Prespecified question and acceptance](STAGE29A_DEEP_FIRMWARE_AND_KNOB_MINING_SYNTHESIS_CONTINUATION_a8bdad0aa1_001.md#prespecified-question-and-acceptance) | <a id="result-and-source-boundary"></a> [Result and source boundary](STAGE29A_DEEP_FIRMWARE_AND_KNOB_MINING_SYNTHESIS_CONTINUATION_a8bdad0aa1_001.md#result-and-source-boundary) | <a id="declaration-census-and-remaining-gaps"></a> [Declaration census and remaining gaps](STAGE29A_DEEP_FIRMWARE_AND_KNOB_MINING_SYNTHESIS_CONTINUATION_a8bdad0aa1_001.md#declaration-census-and-remaining-gaps) | <a id="testedness-and-cross-references"></a> [Testedness and cross references](STAGE29A_DEEP_FIRMWARE_AND_KNOB_MINING_SYNTHESIS_CONTINUATION_a8bdad0aa1_001.md#testedness-and-cross-references) | <a id="ranked-m9-m15-hypotheses"></a> [Ranked M9-M15 hypotheses](STAGE29A_DEEP_FIRMWARE_AND_KNOB_MINING_SYNTHESIS_CONTINUATION_a8bdad0aa1_001.md#ranked-m9-m15-hypotheses)

<!-- stage822a-payload-begin -->
Common WMI/HTT messages may already be used routinely by a driver; absence of an
identified payload experiment does not mean their opcode has never been sent.

Each candidate carries its namespace/path/platform sources, hypothesis, missing
qualification gates, fixed-workload randomized paired ABBA design, primary
worst-station p95 latency and secondary aggregate/per-CPE goodput, p99, loss, retries,
fairness, CPU and resets. Repetitions must be preregistered from pilot variance
before acquisition. Prespecified guardrails: at most 2% goodput loss, no increased
loss or p99 regression and no firmware reset. State, associations and health must
be independently verified after exact captured-state restoration. These are future
experiment contracts; result=NOT_RUN and decision=INCONCLUSIVE for every candidate.
No performance improvement is claimed.

## Reproduction and validation

Run the miner from the repository root with Python; no third-party package is
required for generation. Its default action writes only the requested Stage29A
artifact. --validate <saved-local-json> reconstructs the report from authenticated
inputs and rejects changed values, altered ranking/claims, forged metadata, omitted
sources, new source population and source-byte drift. A new cutoff must be explicitly
generated after shared evidence changes. This guard does not preserve unavailable
historical source preimages or prove that the source report is true.

Inputs reject UNC/URI/device/mapped-remote paths and symlink/reparse traversal,
oversized files/trees, duplicate JSON keys and nonfinite JSON constants. The miner
imports only the pinned existing offline ELF/SGMT parsers after verifying their
source and location. There is no process, network, SSH, firmware loader or radio
mutation API. This is a bounded local analysis tool, not a hostile-host sandbox.

Preserved failures and repairs:

- Initial independent protocol review found six event bounds incorrectly unmarked,
  three BMISS_COUNT_MAX parameters incorrectly marked and HTT_DBG_NUM_STATS unmarked.
  The first suffix-based correction also caught three real MU_CAL_START commands;
  explicit ABI-bound matching fixes both directions. Regression assertions cover them.
- A stricter literal-path validator initially rejected six already-curated
  /proc/sys/dev/uph declarations; source-based expansion preserves this population.
  The failed generation exited 1 before replacing the saved JSON.
- The independent source-read guard rejected an older cutoff after the shared
  Champion ledger changed. The failed receipt is retained at
  C:/_tmp/systemp/fmx_s29a_code_review_fqnytqsq/manifest_drift_checkpoint.json
  (SHA256 be4350634ec733a9e4e9767b9558532a903c9e3832ce27689905785e5a7df6a5).
  Two later independent reads preserved further live-ledger drift failures, including
  C:/_tmp/systemp/fmx_s29a_source_drift_7sdsl2dx/source_drift_review_failure.json
  (SHA256 b5c72615dc3176d1a67c3f0dd40d3c6a008e50ee4afd302bcdfa2696d16f83c6).
  The independently pinned retained ledger and a new 81-source generation resolve
  the acquisition race without weakening source-hash checks or blocking its owner.
- The first syntax-only invocation was blocked by a hook matching prose containing
  the test-runner name. Removing that prose allowed AST syntax validation, exit 0;
  this is not test execution and did not alter any guard.
- The first normal machine-wide test-slot wait expired after 60 seconds at
  0.6..0.8 GB free RAM, below the unchanged 2 GB floor. The child never started;
  there is no test pass/fail count or XML receipt from that attempt.

The requested test module covers restricted arithmetic, unresolved enum propagation,
sentinel/real-control regressions, protocol/knob populations, malformed API5
containers, literal recipe/readback distinctions, typed mutation values, safe local
input boundaries, source drift/omission and forged candidate metadata. Fresh test
execution remains pending at this checkpoint. The normal resource guard is unchanged;
an operator-only exception for this single test file has been requested and is not
inferred from silence or elapsed time.

Fresh canonical CLI reconstruction completed with exit 0 after the snapshot fix.
Independent protocol review completed 50 light probes with PASS_WITH_LIMITS and
zero open findings, bound to the current source/test/JSON hashes:
C:/_tmp/systemp/fmx_s29a_protocol_accepted_an5etehv/independent_protocol_review.json
(SHA256 70bcdb0578ee54b83b2135511854fed464318f505887d3f079d51aa2a09a522f).
It covers source bindings, the independent ledger pin, reconstructed protocol
rows/source lines, sentinels, API5 parser and SGMT metadata/literal reconstruction.

A separate code/source-join review completed 45 light checks, PASS_WITH_LIMITS and
zero open findings, including the final report-card data entry:
C:/_tmp/systemp/fmx_s29a_final_review_2czxn5c1/code_review.json
(SHA256 36994b98c0b22b2fee5115a251f663cd64f9f079d6b244cb9b779195ae8a24f2).
It verifies the 81 source bindings, 145 controls/590 references, source pointers and
categories, line-numbered vault references, ranking, typed mutation values, tamper
rejection and snapshot separation from the advancing live ledger. These light probes
and syntax checks do not substitute for the requested test run.

The existing Command Center generator receives one report-card data entry linking
the four Stage29A outputs, with an offline/conditional badge and the same coverage
limitations. It changes no dashboard layout or Champion state.
The requested Python generator completed with exit 0 and wrote
artifacts/dashboard/FUTURAMAX_COMMAND_CENTER.html. A static artifact check verified
the unique report-card entry, all four source links and the M11/M12/M13/M14/M15/M9/M10
order; this is not browser-render or hardware acceptance.

## Continuity, decisions and next evidence

Current state: offline census and seven qualified hypotheses implemented; no new RF
measurements, device accesses, firmware exports, live writes or claimed improvement.
Research ledger result: a measured local absence and declaration census answer part
of PB010/PB012; exhaustive firmware-5 mining and universal testedness remain incomplete.
Decision: KEEP this reproducible bounded analysis and reject automatic dispatch.

After software checks, the next research evidence is a lawfully held exact-build
QCA988x firmware-5.bin with board/role/build/API provenance, a complete scoped tested
registry and actual setter/getter/domain/restoration qualification for the selected
candidate. Neither a firmware file nor this ranking authorizes a physical experiment.
Shared CURRENT_STATE/RESEARCH_LEDGER/DECISIONS files have concurrent work; this scoped
stage report records the state, ledger and decisions without rewriting their unrelated
current sections. No other experiment is resumed by finishing this task.
<!-- stage822a-payload-end -->
