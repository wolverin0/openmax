<!-- doc-head: STAGE36B_IPTV_DMS_AC_VI_CANARY_GATE.md continuation 2 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE36B_IPTV_DMS_AC_VI_CANARY_GATE.md) | Part 2/2
<a id="stage36b-â-iptv-dms--ac_vi-canary-gate"></a> [Stage36B â€” IPTV DMS / AC_VI canary gate](STAGE36B_IPTV_DMS_AC_VI_CANARY_GATE_CONTINUATION_efaee85008_001.md#stage36b-â-iptv-dms--ac_vi-canary-gate) | <a id="inspected-evidence-and-scope"></a> [Inspected evidence and scope](STAGE36B_IPTV_DMS_AC_VI_CANARY_GATE_CONTINUATION_efaee85008_001.md#inspected-evidence-and-scope) | <a id="required-readbacks-and-targets"></a> [Required readbacks and targets](STAGE36B_IPTV_DMS_AC_VI_CANARY_GATE_CONTINUATION_efaee85008_001.md#required-readbacks-and-targets) | <a id="dynamic-wds-inventory-and-setter-fencing"></a> [Dynamic WDS inventory and setter fencing](STAGE36B_IPTV_DMS_AC_VI_CANARY_GATE_CONTINUATION_efaee85008_001.md#dynamic-wds-inventory-and-setter-fencing) | <a id="prespecified-iptv-and-hls-receiver-gate"></a> [Prespecified IPTV and HLS receiver gate](STAGE36B_IPTV_DMS_AC_VI_CANARY_GATE_CONTINUATION_efaee85008_001.md#prespecified-iptv-and-hls-receiver-gate) | <a id="independent60s-lease-and-exact-restoration"></a> [Independent60s lease and exact restoration](STAGE36B_IPTV_DMS_AC_VI_CANARY_GATE_CONTINUATION_efaee85008_001.md#independent60s-lease-and-exact-restoration)

<!-- stage822a-payload-begin -->
journal before any candidate write. It survives coordinator/SSH/applier loss,
fences all setters and triggers restore on failure or **60-second monotonic expiry**.
The restore operation has a separate five-second timeout; completion inside sixty
seconds is not claimed or physically proven by these fixtures.

Only exact numeric sysfs/debugfs operations are emitted: bridge flags, each discovered
port's DMS flag and the four indexed AQL rows. No shell glob, `eval`, rollback
defaults or stock CPE command is generated. Threshold/BCMC and foundation settings
must remain unchanged. Partial apply, a failed station, wrong effective value,
bad/missing jitter report, loss/classification failure, cancellation, replay or
deadline enters the fenced restore path.

Restoration compares independent readback of every captured control and station
AQL value with the original snapshot. The adapter checks identity before every
restore setter. A vanished/recycled port must not receive an old station's value.
If exact restoration is unavailable or readback disagrees, the result stays
`ROLLBACK_UNVERIFIED_GUARD_RETAINED`, with its journal retained. `ROLLED_BACK_EXACT`
means verified captured configuration restoration; it does not claim subsequent
RF/link health or a production rollback drill.

## Verification and disposition

Executed exactly as requested, without heavy-slot:

```powershell
python -m pytest tests/test_stage36b_iptv_canary_gate.py -q
```

**73 PASS / 0 FAIL / 0 ERROR, exit0 in1.62s** (console receipt `23a946`).
The pre-existing pytest_asyncio fixture-loop configuration warning was retained.
Tests use disposable dictionaries and clocks; no shell, radio, NMS, service,
credential, firmware or live load action occurs. This is software acceptance only.

The [tests](../tests/test_stage36b_iptv_canary_gate.py) cover strict AQL parsing and
queue identity, source/plan integrity, explicit budgets, all-station readbacks,
dynamic port identity, uniform per-station AQL, partial apply, jitter/loss/stream
and classification failures, replay/deadline/cancellation, exact mixed-state
restoration and retained guards on mismatches. The first static review exposed
the conditional per-station AQL update risk; its restrictive guard and regressions
were added before the first pytest run. No failed pytest result was discarded.

KEEP the gate as a local software component. The next physical evidence, only
under separately authorized lab execution, is an exact-build collector plus
independent guard/fencing/restore qualification, complete current WDS/peer AQL
inventory, effective readbacks and synchronized receiver windows under fixed
predeclared budgets. No physical operator action is needed for this code review,
and no background experiment is running.

Independent final source/test/report review: **PASS_WITH_LIMITS,0 material blockers**,
58 fresh static checks. Receipt: `C:/_tmp/systemp/fmx_s36b_independent_review_ya17_pbp/independent_review.json`,
SHA256 `73a2609c1301bc94bafd54e56e4e54da391c718c7b336fbe5a77b83398c12eee`.
The reviewer reused the owner73PASS console receipt and did not run pytest independently.
[Final source-bound validation](../artifacts/autoresearch/stage36b_iptv_canary_validation_20261025.json)
retains the exact command, source pins, review and physical/runtime limits.
Stage35B remains byte-unchanged at `eacef354a5a657d049fa7b81a0aab761f6784cd34fe9039e0ff1838d333745e7`.

Context revision note: the IPTV optimizer and Stage36A artifact changed concurrently
after the initial inspection/review. The negative result discussed above is
specifically **S36A-R1**; it remains unchanged. Later rounds and promotion labels
are outside this software acceptance. The validation receipt records current
context snapshots; the independent review retains its earlier exact source pins.
The gate module/tests and executed73PASS revision did not change.
<!-- stage822a-payload-end -->
