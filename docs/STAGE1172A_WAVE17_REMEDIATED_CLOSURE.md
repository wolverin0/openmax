<!-- doc-head: Stage1172A explicit supersession with native and current-matrix readiness blockers -->
<!-- /doc-head -->

# Stage1172A Wave17 remediated closure

Stage1169A and1170A preserve actual auth attempts, native captures and bounded repairs.
The original1133A..1138A receipts remain unchanged. They are never relabeled as successful.

Stage1136A and1138A accept explicit`--input-map` and`--out` arguments for supersession.
Default behavior still reads the original Wave17 inputs.
The exact map selects1169A,1170A and the complete repaired1171A matrix.
Alternative host sets or provider paths are rejected.

New outputs are stored under`artifacts/verification/stage1172a/`:

-`1136_superseded.json`: exact native-source replay, scope, identity and read-only requirements.
-`1138_superseded.json`: native readiness and complete remediated pytest matrix.
-`readiness_command.json` and`gate_command.json`: actual producer argv, stdout/stderr and exits.

Authentication, dry-run completion, complete AQM configuration readback and profile matching
remain independent facts. A missing upload, native command or AQM scalar remains UNKNOWN.
No apply is authorized. Active v17 mismatch cannot be repaired by writing configuration here.
A successful passive LTU capture does not establish calibrated production thresholds.

Reproduce offline:

`python tools/verify/verify_stage1172a_wave17_remediated_closure.py --execute`

Exit2 records incomplete native closure; exact replay integrity can still pass.
Physical readiness and deployment authority remain false even if read-only closure later passes.

## Current blocked graph

The latest heavy-slot admission timed out after1800seconds before Python execution.
Regression1, full3, owned2 and final58 pytest were NOT EXECUTED.
The earlier455PASS results are archived priorrevision evidence only.
Current1171A is INCOMPLETE; mapped1138A propagates that matrix block and the .84 native readback gap.
Mapped1136A/1138A were re-emitted offline with actual CLI exits2/1 preserved.
Their truthful blocked outputs can replay correctly while readiness and wave17_closed stay false.
Admission shell exit1 is not a pytest result; the latest native pytest exit remains UNKNOWN.

The shared WA v17 kit also changed externally during the admission wait.
1169A/1170A replay now rejects its new revision: `new_kit_revision_requires_explicit_source_review`.
The earlier c52-reviewed native captures remain priorrevision evidence; this worker neither changed
that kit nor silently restored or repinned it. Current source-review failure remains a gate blocker.
