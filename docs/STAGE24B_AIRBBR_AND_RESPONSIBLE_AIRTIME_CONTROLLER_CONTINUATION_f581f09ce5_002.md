<!-- doc-head: STAGE24B_AIRBBR_AND_RESPONSIBLE_AIRTIME_CONTROLLER.md continuation 2 of 2; source lines preserved -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

[Document router](STAGE24B_AIRBBR_AND_RESPONSIBLE_AIRTIME_CONTROLLER.md) | Part 2/2
<a id="stage24b-airbbr-and-responsible-airtime-controller"></a> [Stage24B: AirBBR and Responsible Airtime controller](STAGE24B_AIRBBR_AND_RESPONSIBLE_AIRTIME_CONTROLLER_CONTINUATION_f581f09ce5_001.md#stage24b-airbbr-and-responsible-airtime-controller) | <a id="prespecified-research-question-and-acceptance"></a> [Prespecified research question and acceptance](STAGE24B_AIRBBR_AND_RESPONSIBLE_AIRTIME_CONTROLLER_CONTINUATION_f581f09ce5_001.md#prespecified-research-question-and-acceptance) | <a id="paper-evidence"></a> [Paper evidence](STAGE24B_AIRBBR_AND_RESPONSIBLE_AIRTIME_CONTROLLER_CONTINUATION_f581f09ce5_001.md#paper-evidence) | <a id="historical-champion-and-preserved-source-drift"></a> [Historical Champion and preserved source drift](STAGE24B_AIRBBR_AND_RESPONSIBLE_AIRTIME_CONTROLLER_CONTINUATION_f581f09ce5_001.md#historical-champion-and-preserved-source-drift) | <a id="accounting-and-numerical-policy"></a> [Accounting and numerical policy](STAGE24B_AIRBBR_AND_RESPONSIBLE_AIRTIME_CONTROLLER_CONTINUATION_f581f09ce5_001.md#accounting-and-numerical-policy)

<!-- stage822a-payload-begin -->
must be absent or the global correction is held. Linux AC order is VO0/VI1/BE2/BK3.
No optimality or true time-based fairness is claimed for this mapping.

For median ACK RTT r, baseline b and delivery rate d:

    d = unique_acked_payload_bytes * 8e6 / window_us
    pacing_bps = min(contract_bps,
        max(1000, floor(min(contract_bps,d) * min(1,b/r) * f[i])))

Zero delivery, idle traffic or missing ACK samples means HOLD. RTT excess
max(0,r-b) remains unattributed: other hops, CPU, ACK behavior or queues may
explain it. It is never labeled measured MAC contention or used to infer N.

The synthetic example produces weights465/465/96, AC_BE1615/3230us and a weak
station's isolated-flow pacing target177777bit/s. These are fixture outputs,
not measurements or suggested values for an unidentified production device.

## Generated commands and rollback limits

All outputs are strings in JSON, dispatch_allowed=False. There is no SSH,
subprocess, device reader, executor or persistence API. Example strings:

    iw dev phy0-ap0 station set PUBLIC_DEVICE_0075 airtime_weight 96
    printf '%s\n' '2 1615 3230' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
    tc qdisc replace dev ifb-cpe3 root fq maxrate 177777bit

The fixture's separate existing egress ifb-cpe3 is a declaration, not an IFB
created by this tool. No routes or filters are installed. The AP's matching
Champion FQ-CoDel is preserved and its command is a reference, avoiding a
gratuitous reset of the root queue.

[FQ maxrate](https://raw.githubusercontent.com/iproute2/iproute2/v6.6.0/man/man8/tc-fq.8)
is PER FLOW. A candidate pacing command requires a separate dedicated egress,
identified station, exactly one stable classified flow, no bypass/offload, and
verified defaults for baseline qdisc options the model does not represent.
Missing any gate or multiple/new flows leaves only the target. The tool does
not build an HTB/platform or pretend a root FQ cap singles out a station.
[FQ-CoDel](https://raw.githubusercontent.com/iproute2/iproute2/v6.6.0/man/man8/tc-fq_codel.8)
is a mutually exclusive AQM alternative with no maxrate/pacing claim.
BBR running on a router does not replace forwarded endpoint TCP congestion control.

The iw form is station set MAC airtime_weight W, with strict nonzero unicast
MAC and uint16 validation. AQL semantics follow
[Linux6.6 mac80211](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/net/mac80211/debugfs.c?h=v6.6).
Exact installed-build capability and effective behavior are not qualified here.

Every mutation has an inverse from captured current weights, AQL or the typed
MODELED qdisc parameters, in reverse order. These are not guessed stock defaults.
Unmodeled qdisc options must be verified defaults before a qdisc command is
offered. This still does not restore queue contents, timing, unspecified live
state or runtime health; runtime_rollback_verified=False. Actual application
needs complete live inventory/snapshots, recovery, isolated canary authority
and the existing operator gates. RAM-only does not mean risk-free.

Typed identifiers, numeric ranges and a finite command grammar reject arbitrary
shell, flash commands and persistent writes. Full validation regenerates every
field from the frozen source/input contract and rejects forged nested readiness,
paper, command or rollback values. Command write destinations are transient
kernel state; config, firmware and protected partitions are excluded.

## Verification and preserved failures

After freezing the observed historical contract, generation passed with exit0
and emitted five advisory commands. The source-drift failure remains retained.
A metadata-only hash probe failed in PowerShell quoting before Python; no device
command ran. Two test/doc patch renderings failed before their intended writes;
corrected patches were applied. These are tooling failures, not passing tests.

Independent review of the initial implementation found that a missing station
ledger did not block global AQL and a500/1000us captured baseline could increase
to1615/3230us in one evaluation. Regressions now require full per-AC coverage
and symmetric25% step limits: that baseline advances only to625/1250us.
The second review also found a declared-but-missing VO ledger could leave a
station weight labeled ADVISORY. Its new regression holds weight69 while that
ledger is absent and permits target52 only when the complete observed cost is
supplied. Unknown AC coverage similarly holds whole-station weight corrections.
The partial qdisc rollback scope/default-options gate was also made explicit.
Initial review/probe receipts are preserved; old passes do not accept new revisions.

The first single-file pytest submission did NOT execute: the unchanged2GB guard
expired after60s with free RAM0.9GB, wrapper exit1, no pytest XML. This is resource
unavailability, not a pytest pass/failure. Final test/review receipts follow below.
Only the requested new test file is in scope; no bench recipe or unrelated suite.

Reproduce from repository root:

    $env:PYTHONDONTWRITEBYTECODE='1'
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
    python -m controller.stage24_airbbr_and_responsible_airtime_controller
    python -m controller.stage24_airbbr_and_responsible_airtime_controller --validate artifacts/autoresearch/stage24b_airbbr_responsible_airtime_plan_20261025.json
    node ../wezbridge/scripts/heavy-slot.cjs run --wait-ms 60000 --timeout-ms 120000 --label fmx-s24b-pytest -- python -m pytest -q -p no:cacheprovider tests/test_stage24b_airbbr_and_responsible_airtime.py

KEEP the bounded offline controller only with passing software acceptance.
Faithful AirBBR replication, effective airtime control, physical gains and runtime
restoration remain UNKNOWN/INCONCLUSIVE. No surrogate observation/training,
radio change or physical acceptance is added. Behavior implemented here belongs
to an external controller; downstream Linux/mac80211/driver/firmware effects need
measurements. Stop after the four requested outputs and software verification;
no next experiment is started.

## Revision-bound review receipts

The final reviewed bindings are:

- Controller:1c0a54c77fb8599ada008450a084068fceb034007cc16887f4acf98c2a69c8d9
- Tests:2858a101277c25585628d80426299589b62b2f36c68a004b2645f3a518efa062
- Plan:a0a2c001e1e80df4a75b788ba2d6d1a23616a900a40303f9522af51e0b9119af

Both independent reviews are PASS_WITH_LIMITS, zero open material findings,
on these code/test/JSON bindings. Neither executed pytest. Documentation was
updated afterward by the coordinator; no runtime acceptance follows.

The scientific/numerical reviewer performed48 fresh final-delta checks, including
declared-but-missing VO HOLD69, complete VO ADVISORY52, all unknown-AC cases,
extra undeclared AC, AQL completeness/step budget, qdisc gate and fresh canonical
JSON equality. Final receipt:
<tmp>
SHA256f66d91eb0ac660e02308cdcf9e0101dc9e2f36aeb7c95e0862319cd9c6c590a0.

The command/control reviewer performed17 fresh final-delta checks and verified
prior AQL fixes remained intact. Final addendum:
<tmp>
SHA25615c20e817efbaf093079f4b47d4e989be74982c558101a868d0abf7b76fcd3f8.
Its earlier64-check review is retained at the same directory/code_review.json,
SHA25609a5cd47b48a3b520a28c162778eb7432f2b9d0141b2542d8eb82bd614505305.
It accepts the preceding revision only; final acceptance includes the addendum.

Failure/counterexample evidence remains intact:

- Initial control review requiring changes:
  <tmp>
  SHA2569eead0661dff8de75d64c2dfa3d4b177b2a7ee2f2694fe51cb67629a63f9d845.
- Scientific station-coverage CHANGES_REQUIRED:
  <tmp>
  SHA256d9349ca744065d4b9fe5b939a6abbfda726a185969ff9740d6e01048871e138d.
- Historical source-drift selected-command receipt:
  <tmp>
  SHA256fd68b8bd1bd28e046c97688bf677324791994311d1829d3b5ff07464f81b4dd2.

The second normal2GB-guard request also expired after60s, free RAM1.1GB,
wrapper exit1, without executing pytest or producing XML. No guard was lowered
and no exception was applied. The operator-only exception was requested solely
for this Stage24B test file. Normal guarded execution remains allowed while
waiting. Whole-task completion requires actual passing pytest; these independent
checks and fresh canonical-plan CLI validation are not substitutes.

Third normal guard request also expired:60s, free RAM0.6GB below2GB, wrapper
exit1. No pytest process ran and no XML was produced by any of the three requests.
Final direct host validation passed Python syntax and fresh canonical JSON,
with the final three bindings unchanged. These are explicitly not pytest results.
Task status is BLOCKED_RESOURCE_PENDING_PYTEST, not DONE. The operator exception
remains unanswered/unapplied; no background runner is left active.
<!-- stage822a-payload-end -->
