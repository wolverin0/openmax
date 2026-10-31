<!-- doc-head: Stage1171A preserved failures, static-contract remediation and current admission block -->
<!-- /doc-head -->

# Stage1171A historical pytest remediation

Original Wave17 captured 262 PASS and nine failures. Its logs, XML and receipts remain unchanged.
`artifacts/verification/stage1171a/original_manifest.json` binds39 original sources and outputs.

Corrections preserve measurements:

-1085A now publishes the current loose ath10k census and exact module hashes.
-1087A embedded tar evidence remains independently checked; historical loose counts are snapshots.
-1090A validates current loose/embedded presence and exact ELF-derived symbol rows.
-No peer-assoc field layout or runtime driver claim is inferred from symbol names.
-1088A shell facts bind the actual shell hash; kernel claims still require kernel symbols.
-1105A write counts use valid+invalid+unknown=total; unknown is never silently reclassified.
-1106A uses the exact three-way path census, preserving five valid paths rather than boolean1.
-1108A checks those corrected contracts while retaining provenance and fabricated-offset guards.

The first repair attempt's two test-expectation errors are retained under`focused1/`.
The repaired test independently recomputes symbol rows; no peer-assoc symbol is fabricated.
The focused and complete17-file matrices retain their actual logs/XML/exits.
Full1/full2 each measured455PASS; subsequent broad1001A..1172A execution refreshed older inputs.
The1091A test now verifies its real319PASS capture against archived original bytes in a temporary tree.
Strict current-root replay still rejects drift; archived success is never promoted to current freshness.
The regression repair and freshfull3 are recorded separately; no obsolete receipt is restored.

Reproduce offline under the machine heavy slot:

`python tools/verify/remediate_stage1171a_historical_pytest_contracts.py --execute`

Existing attempt directories are immutable; execution refuses overwrite.
The top-level receipt replays the stored complete matrix and source bindings.
Local tests confer no physical acceptance, active-profile proof or deployment authority.

## Current execution boundary

The latest heavy-slot admission timed out after1800seconds, before Python started.
The new historical-replay regression, full3, owned2 and final58 pytest were NOT EXECUTED.
Previous455PASS counts belong only to the archived priorrevision; they are not current validation.
The current1171A receipt is INCOMPLETE because its latest sources lack fresh matrix evidence.
The319PASS archived1091A replay is historical-only; strict current-root replay still rejects drift.
Actual admission shell exit1 is separate from UNKNOWN/unexecuted native pytest exit.
Evidence: `artifacts/verification/stage1171a/regression1_admission_outcome.json`.
No automatic retry, slot override, process termination or other-pane message occurred.

The shared WA v17 kit also changed externally during the admission wait.
1169A/1170A replay now rejects its new revision: `new_kit_revision_requires_explicit_source_review`.
The earlier c52-reviewed native captures remain priorrevision evidence; this worker neither changed
that kit nor silently restored or repinned it. Current source-review failure remains a gate blocker.
