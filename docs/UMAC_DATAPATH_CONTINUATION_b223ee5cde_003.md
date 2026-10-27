<!-- doc-head: UMAC_DATAPATH.md continuation 3 of 5; source lines preserved -->
<!-- /doc-head -->

[Document router](UMAC_DATAPATH.md) | Part 3/5
<a id="wireless-data-path-original-umac-and-conditional-radio-fields"></a> [Wireless data path: original umac and conditional radio fields](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#wireless-data-path-original-umac-and-conditional-radio-fields) | <a id="a-ce-initialization-count-not-packet-count--confirmed-static-use"></a> [A. CE initialization count, not packet count — CONFIRMED static use](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#a-ce-initialization-count-not-packet-count--confirmed-static-use) | <a id="a-source-tx-ring--source-backed-inferred-field-roles"></a> [A. Source TX ring — source-backed inferred field roles](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#a-source-tx-ring--source-backed-inferred-field-roles) | <a id="a-hal_txq_info--tqi_qflags--candidate-identity-only"></a> [A. HAL_TXQ_INFO / tqi_qflags — candidate identity only](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#a-hal_txq_info--tqi_qflags--candidate-identity-only) | <a id="evidence-and-acceptance"></a> [Evidence and acceptance](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#evidence-and-acceptance) | <a id="b-different-command-namespacespaths--confirmed-static-distinctions"></a> [B. Different command namespaces/paths — CONFIRMED static distinctions](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#b-different-command-namespacespaths--confirmed-static-distinctions) | <a id="b-native-rate-schedule-producer--source-bound-call-chain"></a> [B. Native rate schedule producer — source-bound call chain](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#b-native-rate-schedule-producer--source-bound-call-chain) | <a id="b-htt-aggregation-path--numeric-packing-confirmed-meanings-inferred"></a> [B. HTT aggregation path — numeric packing confirmed, meanings inferred](UMAC_DATAPATH_CONTINUATION_b223ee5cde_002.md#b-htt-aggregation-path--numeric-packing-confirmed-meanings-inferred) | <a id="b-mcs-capability-mask--exact-numeric-filter-inferred-capability-meaning"></a> [B. MCS capability mask — exact numeric filter, inferred capability meaning](UMAC_DATAPATH_CONTINUATION_b223ee5cde_002.md#b-mcs-capability-mask--exact-numeric-filter-inferred-capability-meaning) | <a id="b-held-whal-table-and-encoded-bytes--available-static-data-not-live-state"></a> [B. Held WHAL table and encoded bytes — available static data, not live state](UMAC_DATAPATH_CONTINUATION_b223ee5cde_002.md#b-held-whal-table-and-encoded-bytes--available-static-data-not-live-state) | <a id="a-htchif-transport-to-ce---original-source-chain"></a> [A. HTC/HIF transport to CE - original source chain](UMAC_DATAPATH_CONTINUATION_b223ee5cde_002.md#a-htchif-transport-to-ce---original-source-chain) | <a id="b-subtype1e-receiver-fields---conditional-radio-model"></a> [B. Subtype1e receiver fields - conditional radio model](UMAC_DATAPATH_CONTINUATION_b223ee5cde_002.md#b-subtype1e-receiver-fields---conditional-radio-model) | <a id="continued-source-proof-hook-contexts-and-the-hif-buffer-handle"></a> [Continued source proof: hook contexts and the HIF buffer handle](UMAC_DATAPATH_CONTINUATION_b223ee5cde_004.md#continued-source-proof-hook-contexts-and-the-hif-buffer-handle) | <a id="dependency-acquisition-result-initializer-found-submit-invariant-under-review"></a> [Dependency acquisition result: initializer found, submit invariant under review](UMAC_DATAPATH_CONTINUATION_b223ee5cde_004.md#dependency-acquisition-result-initializer-found-submit-invariant-under-review) | <a id="independent-source-decision-and-corrected-callback-condition"></a> [Independent source decision and corrected callback condition](UMAC_DATAPATH_CONTINUATION_b223ee5cde_005.md#independent-source-decision-and-corrected-callback-condition)

<!-- stage822a-payload-begin -->
conditional CALL8 register window these become incoming a3..a7.
The callee checks a3 and a4 before its first lookup; stores a4 to
context+491; uses a5 as the first encoded selector and context+494 as
the halfword output pointer; stores a6 at context+498; and conditionally
uses a7 as a second selector with output pointer context+49a.
The store at+498 is from a6, NOT a child-return byte; +418+80 is the same
address, not an additional field. It eventually writes0 or1 at+490.
These are observed numeric gates/stores, not adopted vendor field names.

The child extracts bits1..4 and5..6 of the selector and branches on bit0.
Group candidates0/1/2 select table groups4/5/6 (or2/3 under a separate
stack condition); group3 takes a separate legacy-rate lookup. The rate
callee supplies zero at the relevant extra stack argument in its model.
INFERRED table correspondence: bits5..6 select nominal20/40/80MHz/legacy
mode, bits1..4 MCS/legacy ordinal, bit0 distinguishes one/two-stream
masks. This selector is not the native table's hardware-code byte format
described above: its bits5..6 must NOT silently be labeled NSS.
Provider-returned table identity, exact ABI/core/LOOP state and actual
on-air selection are still UNKNOWN. No A-MPDU control is proved in1e.

Independent review confirms the child's output halfword is initialized0
before the row loop and replaced by the current row index on a match.
A no-match path retains0, not a distinct invalid-index/status sentinel;
the parent does not check a child status before its later byte stores.
The bounded child reads selector bits0..6, with no observed bit7 read.
These static facts do not prove that an unsupported rate request executes
live or that row0 is transmitted; implicit LOOP state/ABI remain conditional.

A bounded search in the four held ptmp_ap radio maps did not qualify an
equivalent150-row LE table. Each family had exactly one in-bounds6012-byte
candidate headed by LE150, but90/91 of its row group words were outside0..6,
and its remaining group0 rows had no matching code/ordinal patterns.
All16 segment hashes/sizes matched their manifests before/after. This
rejects only those candidates under that specific LE/layout hypothesis:
it does NOT establish absence in other roles, provider memory or runtime.
Adjacent umac-wmi `ptmp-ap-rate-table-search.json`, SHA256
ef38e14803a3e05ee5f13dd3172a9171b426bb7b7af7c8fd49dc1dd9e3705f9e.

The separate WA parser window at9b59ef copies input9..d to outputc..10.
Its jump to9b5476 was previously outside the384-byte metadata window,
not outside held bytes. A new private read-only capture of that exact
WA destination yields only `0c02` movi.n a2,0 and `1df0` retw.n, with
no calls/frontiers. This resolves the window gap without manufacturing
a parser-to-rate-adapter link or using the same address in another family.

A separate outer-dispatcher proof now qualifies the missing pointer-base
alias under the same conditional CALL8/core model. In WA/XC it passes
parser output=context+5d0, then uses recordbase=context+4d8 and adapter
offset argument80. Thus parser+c..10 equals recordbase+80+84..88 for
the five rate fields; parser+c/e/10/12/14 equals the TXQ byte/halfwords/word
input offsets. In2WA/2XC the bases are5bc/4c4, not5d0/4d8, with the same
relative alias equations. The selector recordbase+fe equals parser+6.
Original rows/segment hashes were rechecked for all four families.
This resolves the local source-layout alias, not actual reception, provider
copy semantics or runtime selection. The failed v1 universal-base
assumption is preserved; the corrected v2 checks actual family constants.
- `radio-parser-adapter-alias-v2.json`, SHA256
  2b9f89bb8ac34d9b55b48baf8fd686ff07aea0dbcadef62ac3b5f2a3d437cd94.

- Adjacent umac-wmi `rate-override-selector-table-qualification.json`, SHA256
  41985f6ba2e2d0b9616ae9f656deab5c78b18cfd6c2e2d26947a8c60d5282379;
  its older child-result wording is superseded by the correction above.
- `wa-parser-continuation-v1/receipt.json`, SHA256
  b62665a3b483a6a97cc0ca85dff73e0f6f2c38667831415b69c84e6a8b3c1c53.
  Original radio bytes, profile and parent private database unchanged;
  no import, analysis pass, shared DB mutation or target execution.

## B. Initial umac-only boundary - preserved, scope subsequently extended

The exact ubnt_poll_host_set_rate_override, ubnt_poll_host_set_txq_param
and ubnt_poll_host_set_ptmp_poll_info symbol names are absent from all
four original umac .symtab tables. This is NOT proof those behaviors are
absent, nor license to identify an unnamed function by a matching immediate.
Selected umac sender evidence does not bind the requested17/1e message
payload to poll9064/9070. The native188-byte9044/9045 path and HTT tag5
aggregation remain separately qualified. The unnamed2*9064/436-byte
tail jump remains distinct; it is not reclassified as poll9070 or as a call.

Minimum missing evidence is the exact poll sender implementation bound
to its payload and transport. The conditional receiver base alias above
supersedes the earlier blanket missing-alias claim, not wire acceptance.
The initial negative scan did not open other modules. The operator then
explicitly selected option1 to include READ-ONLY ubnt_poll_host.ko;
source-bound17/1e host serialization from that module is qualified below.
Exact HAL ABI/provider/core/runtime effects also remain unproved; do not
replace those missing facts with decompiler names or synthetic acceptance.

- Adjacent umac-wmi `umac-poll-host-serialization-boundary.json`, SHA256
  bea89bf78cb60c0e215b531c7a4e41050db123770b3cdee5b49cbfff22f6ec51.

## B. Actual poll host serialization - original bytes now qualified

Explicitly authorized read-only ubnt_poll_host.ko analysis supplies the
missing serializer implementations; the earlier umac-only negative remains
true for that narrower module, not a global missing implementation claim.
Both named setters have exact R_MIPS_26 to local ubnt_poll_host_ht_comm_tx.
Its outer command is9064 in WA/XC and9070 in2WA/2XC, in the send delay slot.
The inner subtype selector is a different namespace:17/1e. Native umac
rate-schedule9044/9045 and HTT aggregation tag5 remain distinct paths.

The transport allocates1024bytes, zeroes output storage and runs prepare/setup;
the original .rodata relocation table directs17 to.text+14520 and1e to14480.
Common header before per-word swap: bytes0..3 are00 00 00 01; byte4 is
source record+4; bytes5..6 are the source+6 subtype halfword, high byte first;
bytes7..8 are source+8 halfword, high byte first. Source+4/+8 provenance is
UNKNOWN: neither bounded setter nor complete prepare/setup bodies write
them before use. This is not a confirmed uninitialized-value/leak finding.
Setup DOES store1 at source/input+0 before writing the version header;
the frozen correction's 'output/local stack only' phrase was too broad.
The independent erratum preserves that error and limits the negative
write finding to source+4/+8, not all source memory.

| Subtype | Prepared CPU-buffer fields after9-byte header | Prepared / sent length |
| --- | --- | --- |
| 17 | byte9 from record+c; halfwords a..b/c..d/e..f from record+e/+10/+12, high byte first; word10..13 from record+14 | 20 /20 bytes |
| 1e | bytes9..d from record+c..10 in order; bytes e/f zero padding | 14 /16 bytes |

Offsets in this table are HEX; lengths in the last column are DECIMAL.
TXQ setter's delay-slot SW stores the caller-stack word into record+14
BEFORE serializer entry; the handler's SWR delay slot completes the word.
The rate setter's delay slot supplies its record pointer. Send length is
`(prepared_length+3)&~3`; the exact dword-swap function reverses every
four-byte chunk IN PLACE before the WMI send. The table is pre-swap CPU
layout, NOT an accepted on-wire capture. No hardware endian/receiver
behavior is inferred solely from this host-buffer transformation.

The rate setter has a250-hex-byte frame. Loads at its current SP+263/267/
26b/26f/273/277 refer to ENTRY SP+13/17/1b/1f/23/27. The initial frozen
receipt's entry-SP+26b wording was wrong and is superseded by the new
correction, not edited away. Exact byte packing:

`bw(x) = 20hex if x=28hex, 40hex if x=50hex, otherwise0`;
`stream(n) = 0 for byte0/1, otherwise1`.

Primary byte= `((entry_a3<<1)&1e) | bw(entry_stack[17]) | stream(entry_stack[13])`.
Secondary byte= `((entry_stack[1f]<<1)&1e) | bw(entry_stack[27]) | stream(entry_stack[23])`.
Record+f copies raw entry_stack[1b]; record+c/+d are original a1/a2 bytes.
INFERRED MCS/width/stream meaning is consistent with the separately qualified
radio bit extraction/table correspondence. Numeric packing alone does not
validate MCS bounds, requested rates, physical stream count or radio execution.

The poll-host module imports __wmi_unified_cmd_send. New original umac
__ksymtab evidence binds that SAME export name to its exact function via
two R_MIPS_32 relocations: entry170/name-string3d0/function c21e0 in WA/XC;
entry178/name-string3e5/function ced90 in2WA/2XC. Function binding STB_LOCAL
does NOT negate this explicit export declaration. This supersedes the
earlier mere-same-name-only static boundary. Actual loaded-module/runtime
binding and delivery remain unproved; no module was loaded to test them.
Together with the reviewed HTC/HIF/CE and receiver-base-alias evidence,
this establishes a bounded static serialization/control path with explicit
dynamic/provider/core limits, not an accepted RF experiment or exact HAL ABI.

- Adjacent umac-wmi `ubnt-poll-host-subtype-17-1e-source-serialization.json`, SHA256
  e1879f4f6ac93c400dd762c29133e499996bc4645785d695b465d6058aea378b.
- Adjacent umac-wmi `rate-override-source-stack-and-packing-correction.json`, SHA256
<!-- stage822a-payload-end -->
