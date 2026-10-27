<!-- doc-head: STAGE40B_STAGE42A_NETDEV_TXQ_AND_AIROS6_VERIFIER.md continuation 2 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE40B_STAGE42A_NETDEV_TXQ_AND_AIROS6_VERIFIER.md) | Part 2/2
<a id="stage40b-stage42a-netdev-txq-and-airos6-evidence-verifier"></a> [Stage40B: Stage42A netdev TXQ and airOS6 evidence verifier](STAGE40B_STAGE42A_NETDEV_TXQ_AND_AIROS6_VERIFIER_CONTINUATION_5a9e6c38d1_001.md#stage40b-stage42a-netdev-txq-and-airos6-evidence-verifier) | <a id="inputs-authentication-and-scope"></a> [Inputs, authentication and scope](STAGE40B_STAGE42A_NETDEV_TXQ_AND_AIROS6_VERIFIER_CONTINUATION_5a9e6c38d1_001.md#inputs-authentication-and-scope) | <a id="stage42a-actual-getters-and-results"></a> [Stage42A: actual getters and results](STAGE40B_STAGE42A_NETDEV_TXQ_AND_AIROS6_VERIFIER_CONTINUATION_5a9e6c38d1_001.md#stage42a-actual-getters-and-results) | <a id="netdev-mac80211-and-airos6-boundaries"></a> [Netdev, mac80211 and airOS6 boundaries](STAGE40B_STAGE42A_NETDEV_TXQ_AND_AIROS6_VERIFIER_CONTINUATION_5a9e6c38d1_001.md#netdev-mac80211-and-airos6-boundaries) | <a id="stage40a-route-and-metric-audit"></a> [Stage40A: route and metric audit](STAGE40B_STAGE42A_NETDEV_TXQ_AND_AIROS6_VERIFIER_CONTINUATION_5a9e6c38d1_001.md#stage40a-route-and-metric-audit)

<!-- stage822a-payload-begin -->
declared jitter/loss factors. The verifier recomputes all8 phase formulas and
arm means, preserving these names as derived scores rather than raw percentiles.
The loaded-ping parser has synthetic2/5/6ms p50/p95/p99 fallback values if no
RTTs parse, and raw ping samples/counts are not saved here. Even the loaded-ping
field's sample authentication remains UNKNOWN. Formula consistency cannot
authenticate those samples. No “full line-rate restored” result is established.

All saved Stage40A IPTV/voice loss counts are zero with positive denominators;
the audit checks counts against percentages. That does not prove actual TID,
pure RF route or universal losslessness. R1 saves four complete16-integer UPH
alias views: they agree, the first component changes10 to5 and the tail stays
stable. Unequal aliases or changing tails are reported. This does not prove
shared native addresses or a complete alias ABI. R2's `NOTSENT_LOWAT="-1"`
is retained as a signed sentinel; an empty `ETH0_1_QDISC` getter is UNKNOWN,
not an inferred `noqueue` state.

## LTU BusyBox and binary-patch semantics

The deployer's LTU1 literal uses **echo -ne**, not printf. The audit recognizes
three dd operations interleaved with two intended byte emitters. Its arithmetic
is conditional on complete reads and exactly one emitted byte at each position:

| Segment | Intended original input / output |
| --- | --- |
| Prefix |1756200 bytes before the first changed position. |
| First emitter |One intended08 byte at output offset1756200. |
| Middle |63 bytes from original1756201. |
| Second emitter |One intended01 byte at output1756264. |
| Suffix |Input begins at1756265 because dd skip1 multiplies input block size1756265. |

Under those assumptions size and unchanged-byte coordinates are preserved.
Four literal characters such as backslash-x-0-8 are not one08 byte; two
four-character emissions increase the output by6 bytes. Emission lengths0/2
preserve total size but break positions, so size alone is insufficient. The
pure arithmetic helper creates no binary and interprets no machine instruction.

Upstream BusyBox1.22.1 includes `conv=notrunc` conditionally under
FEATURE_DD_IBS_OBS; unsupported syntax is not implied by the version alone.
Its skip/count operate in blocks and reads may be partial. See the primary
[BusyBox dd source](https://raw.githubusercontent.com/mirror/busybox/1_22_1/coreutils/dd.c).
Echo's option handling depends on FEATURE_FANCY_ECHO; backslash expansion and
newline suppression must be qualified on the exact build.
[BusyBox echo source](https://raw.githubusercontent.com/mirror/busybox/1_22_1/coreutils/echo.c)
shows this dependency. Printf processes escapes in its format or through `%b`,
whereas `%s` does not expand an escaped payload. The script has no printf
operation, so a host printf example cannot authenticate its historical echo.
See the primary [BusyBox printf source](https://raw.githubusercontent.com/mirror/busybox/1_22_1/coreutils/printf.c).

The requested receipt reports a cold-boot AP role and LTU2 persistence. It
does not include the original ELF/build hash, preimage/opcode bytes, postimage
hash/size, emitter output, bound-mount identity or an exact deployed script hash.
The nested ledger's LTU.afltu.v2.4.0 label is not that missing identity evidence.
Native binary/patch/boot-effect qualification therefore remains **UNKNOWN**.
A reported AP role alongside many configuration changes is a separate saved
observation, not proof that these two bytes caused it.

The current LTU1 literal is5609UTF8 bytes/101 lines, versus saved5164/94.
LTU2 is4249/78, matching saved size/count; matching these alone still does not
prove identical bytes. The audit exposes these differences, ignored failures
and the existing-/tmp-file skip condition without repairing or executing them.
Historical LTU cfgmtd/persistent operations were reported, so Stage40A as a
whole must not be labelled RAM-only. Stage40B executes none of those operations.

## API, checks and completion

`source_contract(stage42_doc, stage40_doc)` binds the six canonical rounds and
poststart receipt. `audit_stage42a()` and `audit_stage40a()` are separate pure
semantic audits with `source_authentication="NOT_CHECKED_BY_THIS_FUNCTION"`.
They report contradictions without turning source decisions into new promotion.
`audit_saved_sources(root=...)` combines the bindings and audits, extracts only
the two constant script assignments through AST, and produces a read-only
result. No shell, runner import, firmware execution or subprocess exists here.

Local file reads reject UNC/mixed network paths, URIs, mapped network drives
and symlink/reparse ancestors before content access, then bound JSON size and
reject duplicate keys/nonfinite metadata. The filesystem is assumed stable
during the local audit; this is not a native atomic acquisition/fencing runtime.
`parse_tx_queue_len_readback()` checks complete header/value inventories;
`assess_airos6_state()` checks complete multi-integer coordinates;
`bridge_snooping_evidence()` separates optional config/probe evidence;
`patch_splice_layout()` checks arithmetic, and `assess_byte_emission()` compares
supplied bytes without qualifying their native origin. The poststart audit
checks recognized ordered dd/emitter operations, not arbitrary shell semantics
or execution success. All binary-verification flags remain false.

Fresh direct command:

```text
python -m pytest tests/test_stage40b_stage42a_verifier.py -q
```

The first result was64PASS/2FAIL/exit1 in0.45s (`7ce03e`). Both failures were
fixture assumptions exposed by the concurrent R5 append, not product acceptance:
one pop removed R5 rather than requested R4; another assumed no prior extras.
Fixtures now select the required round explicitly and preserve unassessed IDs.
The unchanged product then passed66/exit0 in0.36s (`489d0e`). Independent review
requested local-path guards, typed present-CPE AQL checks and dd/emitter ordering;
its original findings are retained in
[pre-final review findings](../artifacts/autoresearch/stage40b_pre_final_review_findings_20261025.json).
Those repairs and negative regressions produced **78PASS,0FAIL,0ERROR,0SKIP,
exit0 in0.35s** (`20d671`). The existing pytest_asyncio fixture-loop deprecation
warning remains visible. Final independent review is recorded separately from
these owner-executed tests in the validation receipt.

Software verification stops after the requested module/tests/report/global-doc
updates and independent review. No physical operator action is required for
this offline task. Current radio health, native build/acquisition/patch proof
and physical acceptance remain UNKNOWN; E2 remains NOT_ACCEPTED. No hardware
SSH, device/service/script/patch/flash action, new benchmark, next task or
background runner was started by Stage40B.
<!-- stage822a-payload-end -->
