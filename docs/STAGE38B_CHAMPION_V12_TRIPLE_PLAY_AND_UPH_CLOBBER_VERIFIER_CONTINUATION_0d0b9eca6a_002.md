<!-- doc-head: STAGE38B_CHAMPION_V12_TRIPLE_PLAY_AND_UPH_CLOBBER_VERIFIER.md continuation 2 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE38B_CHAMPION_V12_TRIPLE_PLAY_AND_UPH_CLOBBER_VERIFIER.md) | Part 2/2
<a id="stage38b-champion-v12-triple-play-and-uph-clobber-verifier"></a> [Stage38B Champion v12 triple-play and UPH clobber verifier](STAGE38B_CHAMPION_V12_TRIPLE_PLAY_AND_UPH_CLOBBER_VERIFIER_CONTINUATION_0d0b9eca6a_001.md#stage38b-champion-v12-triple-play-and-uph-clobber-verifier) | <a id="the-two-observed-failure-modes-and-source-boundaries"></a> [The two observed failure modes and source boundaries](STAGE38B_CHAMPION_V12_TRIPLE_PLAY_AND_UPH_CLOBBER_VERIFIER_CONTINUATION_0d0b9eca6a_001.md#the-two-observed-failure-modes-and-source-boundaries) | <a id="deterministic-readback-contract"></a> [Deterministic readback contract](STAGE38B_CHAMPION_V12_TRIPLE_PLAY_AND_UPH_CLOBBER_VERIFIER_CONTINUATION_0d0b9eca6a_001.md#deterministic-readback-contract) | <a id="post-apply-triple-play-query-and-write-evidence"></a> [Post-apply triple-play, query and write evidence](STAGE38B_CHAMPION_V12_TRIPLE_PLAY_AND_UPH_CLOBBER_VERIFIER_CONTINUATION_0d0b9eca6a_001.md#post-apply-triple-play-query-and-write-evidence)

<!-- stage822a-payload-begin -->
The complete fenced write journal binds the baseline/final snapshots and plan.
Every event identifies role/device/boot, sequence, monotonic timestamp, literal
owned path and a valid setter payload. Writes must occur strictly between
baseline and post-apply start; active-window writes and qdisc operations fail.
AQM/AQL records use their actual setter grammar and retain the v11 foundation.
The last numeric write to each control must match the post-apply readback, and
every changed numeric coordinate must appear in the journal. The final shared
UPH write must be exactly ff_mcast_airtime_limit5. A later voip_bias/atpc/other
alias write fails even if a convenient final scalar would otherwise look right.

## Exact captured-parameter restoration scripts

`generate_restoration_scripts` returns three shell scripts, typed per-device
manifests and SHA256s. It emits **no** network calls or execution. Inputs are
the actual captured baseline, sealed plan, independent qualification record and
its separately approved digest. Caller-provided self-hashes are not independent
hardware acceptance. Qualification must bind the exact baseline/plan and approve
whole-vector alias restoration, uniform peer-AQL effects, exclusive independent
fencing, atomic identity/setter/readback, quiesced traffic and guard retention
on failure.

Each script requires an already armed native recovery journal and the exact
`/usr/libexec/fmx-stage38b-restore-guard` binary with its approved SHA256. The
script checks its token, binary presence/hash and prearmed/quiesced guard first.
Its `restore-exact` operations carry every literal captured path/type/value.
The native guard must skip already equal controls, then atomically verify
ownership, complete inventory/generations, setter and effective readback. This
avoids unnecessary snooping/AQL reapplication and closes identity races.

Restoration includes captured AQM RW fields, all four global AQL rows and
threshold, captured bridge flags and every discovered port's captured flags.
Peer-AQL restoration effects must be independently verified too. On Rocket,
restore the **entire captured16-integer vector once through ff_mcast**, last.
Never replay voip_bias and the other aliases as independent scalar controls,
and never replace captured values with champion defaults. A regression fixture
restores AP quantum777/limit4097 and CPE VO400/800, proving that the generator
does not substitute4542/2048 or300/600.

The guard's final `verify-and-release` must compare every saved parameter and
alias view against its original snapshot and verify unchanged identities before
releasing the recovery journal. Any failed operation exits the script under
`set -eu`, retaining the independent guard. The native guard is **not installed
or implemented by this task**. Without that qualified prerequisite the scripts
fail before mutation. They are guarded recovery recipes, not evidence of a
working device rollback runtime. Scripts contain no SSH, qdisc replacement,
nft flushing, profile runner, firmware operation or ignored setter failure.

The restoration scope is exact captured numeric parameters. Dropped packets,
read-only counters, hidden queues and dynamic MDB history cannot be restored
by rewriting parameters and are not claimed restored. A radio restart or
recreated port must be handled by the qualified guard rather than writing an
old value into a new object.

## Validation and completion boundary

Direct focused command, without heavy-slot:

```text
python -m pytest tests/test_stage38b_champion_v12_canary_verifier.py -q
```

The initial result was43PASS/1FAIL/exit1 (`9677f1`): a tuple-assignment error in
the TID7 test's fixture prevented that case from reaching product code. It is
preserved. The fixture now uses a mutable copy, and explicit old-quantum/voice
budget, Ethernet scope and non-default restoration regressions were added.
An intermediate50PASS/0.73s/exit0 run (`5de7e5`) is retained. Independent review
then found an unguarded change in captured parameters outside the forced overlay
(AP Ethernet fast-leave or optional CPE DMS). Full parameter stability and two
regressions were added. The final direct result is
**52PASS,0FAIL,0ERROR,0SKIP,exit0 in0.67s** (`41c84f`). The existing pytest_asyncio
unset fixture-loop deprecation warning is retained.

Independent static review: **PASS_WITH_LIMITS**,113 fresh checks and zero
material blockers. It binds the final module/test pins and explicitly reuses
the owner's52PASS console evidence; it does not claim independent pytest or
native script execution. The earlier required-change finding and the reviewer's
own corrected checker failures are retained in the immutable review receipt.

Source/test hashes, both test results, repairs and independent review are
recorded in [stage38b_champion_v12_validation_20261025.json](../artifacts/autoresearch/stage38b_champion_v12_validation_20261025.json).
Only disposable fixtures and generated text were exercised. No radio/SSH/WSL,
NMS, native guard installation, generated-script dispatch or flash action took
place. Native acquisition/guard qualification and physical acceptance remain
**UNKNOWN**. Stop after the requested software verification and independent
review; no further task or physical experiment is claimed.
<!-- stage822a-payload-end -->
