<!-- doc-head: STAGE37B_MAC80211_AQM_PER_TID_CANARY_VERIFIER.md continuation 2 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE37B_MAC80211_AQM_PER_TID_CANARY_VERIFIER.md) | Part 2/2
<a id="stage37b-mac80211-aqm-per-tid-canary-verifier"></a> [Stage37B mac80211 AQM per-TID canary verifier](STAGE37B_MAC80211_AQM_PER_TID_CANARY_VERIFIER_CONTINUATION_680eee28ad_001.md#stage37b-mac80211-aqm-per-tid-canary-verifier) | <a id="evidence-inspected-and-limits"></a> [Evidence inspected and limits](STAGE37B_MAC80211_AQM_PER_TID_CANARY_VERIFIER_CONTINUATION_680eee28ad_001.md#evidence-inspected-and-limits) | <a id="effective-readback-contract"></a> [Effective readback contract](STAGE37B_MAC80211_AQM_PER_TID_CANARY_VERIFIER_CONTINUATION_680eee28ad_001.md#effective-readback-contract) | <a id="snapshot-and-flow-evidence"></a> [Snapshot and flow evidence](STAGE37B_MAC80211_AQM_PER_TID_CANARY_VERIFIER_CONTINUATION_680eee28ad_001.md#snapshot-and-flow-evidence) | <a id="canary-and-exact-restoration"></a> [Canary and exact restoration](STAGE37B_MAC80211_AQM_PER_TID_CANARY_VERIFIER_CONTINUATION_680eee28ad_001.md#canary-and-exact-restoration)

<!-- stage822a-payload-begin -->

Preflight must also explicitly qualify the atomic commit gate. Under its fence,
the guard rechecks identity, station generations/membership, complete TXQs and
zero events, exact AQL/RW values and lease validity immediately before disarming.
It binds the plan and the measured proof digest to its acquisition journal;
the returned commit receipt must match both. A rejected commit retains the guard
and restoration path. Coordinator readbacks cannot replace this final check.

Before arming, capture the actual three RW values plus global identity and
allocated flow count. These values may differ from defaults and from v10.
The independent resident guard receives this snapshot and exact restore writes
before any mutation. It must survive coordinator loss, own a monotonic60s lease,
fence stale setters and recheck identity atomically under exclusive ownership.
Controller-side readbacks alone cannot provide those guarantees.

Only three typed numeric writes can target the single global AQM file.
AQL is verified and remains a readback prerequisite; no AQL, station-stat,
bridge/DMS, qdisc, nft, UCI, firmware or protected-partition writes are emitted.
After effective v10 verification, collect the post-apply triple-play window,
perform a new final readback, check counter progression and commit the guard.
Every call is bounded; a separate5s restore-call allowance is reserved within
the control deadline. Total hardware recovery latency is not established by
fixtures.

Any drop/overlimit, mismatch, stale/reordered data, partial setter failure,
cancellation or deadline triggers fence-and-restore of the captured RW values.
Independent readback must match the same global identity, all three saved
parameters and allocated flow count before guard release. Counter/backlog
changes do not invalidate parameter restoration: those fields are read-only
and must never be written or claimed restored.

| Result state | Meaning |
| --- | --- |
| `FIXTURE_ACCEPTED` | Disposable software scenario passed |
| `QUALIFIED_CANARY_ACCEPTED` | Qualified-adapter contract passed; no receiver/performance acceptance implied |
| `ROLLED_BACK_AQM_PARAMETERS_EXACT` | Failure followed by verified exact RW restoration |
| `AQM_RESTORE_UNVERIFIED_GUARD_RETAINED` | Restore/readback/release failed; guard must remain authoritative |
| `GUARD_STATUS_UNKNOWN_NO_APPLY` | Guard arming was not confirmed; controller issued no candidate setter |

## Validation and remaining acceptance

Run the operator-requested focused command directly:

```text
python -m pytest tests/test_stage37b_mac80211_aqm_canary.py -q
```

Execution and independent-review receipts are recorded in
[stage37b_mac80211_aqm_validation_20261025.json](../artifacts/autoresearch/stage37b_mac80211_aqm_validation_20261025.json).
The final direct command passed **86 tests in0.45s, exit0** (console receipt `97937c`).
The earlier81PASS/0.46s run (`9a624c`) is retained as revision-specific evidence;
the final five regressions cover commit qualification, rejection and proof binding.
The existing pytest_asyncio unset fixture-loop-scope deprecation warning is
retained. No test was skipped and no physical acceptance was inferred.
Independent static review passed **PASS_WITH_LIMITS**, with89 fresh checks and
zero material blockers. It reviewed the final module/test pins and explicitly
reused the owner's86PASS console evidence; it did not independently execute
pytest. The immutable review receipt is retained beside the validation artifact.
No heavy-slot wait, radio access, SSH/WSL, service installation or physical
traffic measurement is part of this task. Software completion does not prove
current hardware settings, voice traffic, delivery, gain or device recovery.
Physical and device-adapter qualification remain **UNKNOWN**; E2 remains
**NOT_ACCEPTED**. Stop at Stage37B software verification and independent review.
<!-- stage822a-payload-end -->
