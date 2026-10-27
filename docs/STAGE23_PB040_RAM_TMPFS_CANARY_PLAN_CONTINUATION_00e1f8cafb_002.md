<!-- doc-head: STAGE23_PB040_RAM_TMPFS_CANARY_PLAN.md continuation 2 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE23_PB040_RAM_TMPFS_CANARY_PLAN.md) | Part 2/2
<a id="stage23-pb040-ram-tmpfs-canary-preparer"></a> [Stage23: PB040 RAM tmpfs canary preparer](STAGE23_PB040_RAM_TMPFS_CANARY_PLAN_CONTINUATION_00e1f8cafb_001.md#stage23-pb040-ram-tmpfs-canary-preparer) | <a id="prespecified-question-and-boundary"></a> [Prespecified question and boundary](STAGE23_PB040_RAM_TMPFS_CANARY_PLAN_CONTINUATION_00e1f8cafb_001.md#prespecified-question-and-boundary) | <a id="fresh-offline-evidence"></a> [Fresh offline evidence](STAGE23_PB040_RAM_TMPFS_CANARY_PLAN_CONTINUATION_00e1f8cafb_001.md#fresh-offline-evidence) | <a id="loader-boundary"></a> [Loader boundary](STAGE23_PB040_RAM_TMPFS_CANARY_PLAN_CONTINUATION_00e1f8cafb_001.md#loader-boundary) | <a id="ram-policy-and-script-references"></a> [RAM policy and script references](STAGE23_PB040_RAM_TMPFS_CANARY_PLAN_CONTINUATION_00e1f8cafb_001.md#ram-policy-and-script-references) | <a id="validation-and-independent-acceptance"></a> [Validation and independent acceptance](STAGE23_PB040_RAM_TMPFS_CANARY_PLAN_CONTINUATION_00e1f8cafb_001.md#validation-and-independent-acceptance)

<!-- stage822a-payload-begin -->

Reproduce from repository root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
python firmware/pb040_ram_tmpfs_canary_preparer.py
python firmware/pb040_ram_tmpfs_canary_preparer.py --validate artifacts/physical_boundary/pb040_ram_tmpfs_canary_plan_20261025.json
node ../wezbridge/scripts/heavy-slot.cjs run --wait-ms 60000 --timeout-ms 120000 --label fmx-s23-pytest -- python -m pytest -q -p no:cacheprovider tests/test_pb040_ram_tmpfs_canary_preparer.py
```

## Research decision and remaining evidence

The offline transformation is CONFIRMED; actual loading, canary execution, health
and restoration remain UNKNOWN. No wireless gain, new observation/ready cell,
stock restoration or custom MAC capability is accepted. Implemented behavior
belongs to an external offline controller; execution crosses an unqualified
board/driver/firmware boundary.

Later execution needs the exact qualified API5 pair/provenance, authorized isolated
board/build/driver scope, independently implemented/tested ownership/deadline/
health observers, semantic readback and proven recovery. No physical action is
requested now. This task stops at the offline outputs/software acceptance; it
does not resume another experiment or claim background progress.

## Revision-bound independent reviews

Both independent code/JSON reviews are **PASS_WITH_LIMITS**, with zero open material
findings. They accept only the offline preparer and inert references. Neither ran
pytest; neither claims runtime observers, operational rollback or hardware evidence.
The coordinator documentation was updated after these code reviews.

- Canary/source review:77 fresh pure checks; separately extracted all three ELF
  symbols with pyelftools, decoded12 segments and the sole canary change, checked
  bindings, canonical-plan equality and NoProbe paths. Receipt:
  `C:/_tmp/systemp/fmx_s23_canary_review_x_dj6vjc/independent_canary_review.json`,
  SHA256 `d1981f0de9ac71a988dd1f50e84b1381826f7a22da809c82cd02065ded31c2a5`.
- Plan/script safety review:59 fresh pure checks; reconstructed canary/JSON,
  checked gates, encoded/rehash attacks, nested readiness and path refusal.
  Receipt: `C:/_tmp/systemp/fmx_s23_final_review_94bqjpn1/code_review.json`,
  SHA256 `95b7a98ec2261b12f228de6018fdfdc093b0ed7143503e4e092a714b1e98e0fc`.

Reviewed bindings: preparer
`2c962c54071a4f029b12d5a70adceefc4295214fa40f095c36dabe7597f97cfd`, test file
`b5d79129a7961fd9aa9e5ea230f2443f325740d1ccfac54015d4f47d7cb0d591`, JSON
`9cc803e19091996bcdd4c72bdf53a5580d4052eea09b53d54c784074d65012f8`.

The second60s resource-guard wait also expired without pytest execution, with
free RAM1.3GB below the unchanged2GB floor (wrapper exit1). No pytest XML exists
from these two requests. A narrowly scoped operator-only exception was requested
for this single file; no exception is assumed from the earlier Stage18B task.
Normal guarded execution remains allowed while waiting. Whole-task completion
requires a real passing pytest result; independent checks do not substitute for it.

Third normal guarded request:60s timeout, free RAM0.7GB below2GB, wrapper exit1;
pytest again did not execute and produced no XML. No guard setting was lowered
and no operator exception was applied. All three resource failures are retained.
Final direct host checks passed Python test syntax and fresh canonical JSON
validation; these are not reported as pytest execution.
<!-- stage822a-payload-end -->
