<!-- doc-head: UMAC_DATAPATH.md continuation 5 of 5; source lines preserved -->
<!-- /doc-head -->

[Document router](UMAC_DATAPATH.md) | Part 5/5
<a id="wireless-data-path-original-umac-and-conditional-radio-fields"></a> [Wireless data path: original umac and conditional radio fields](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#wireless-data-path-original-umac-and-conditional-radio-fields) | <a id="a-ce-initialization-count-not-packet-count--confirmed-static-use"></a> [A. CE initialization count, not packet count — CONFIRMED static use](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#a-ce-initialization-count-not-packet-count--confirmed-static-use) | <a id="a-source-tx-ring--source-backed-inferred-field-roles"></a> [A. Source TX ring — source-backed inferred field roles](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#a-source-tx-ring--source-backed-inferred-field-roles) | <a id="a-hal_txq_info--tqi_qflags--candidate-identity-only"></a> [A. HAL_TXQ_INFO / tqi_qflags — candidate identity only](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#a-hal_txq_info--tqi_qflags--candidate-identity-only) | <a id="evidence-and-acceptance"></a> [Evidence and acceptance](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#evidence-and-acceptance) | <a id="b-different-command-namespacespaths--confirmed-static-distinctions"></a> [B. Different command namespaces/paths — CONFIRMED static distinctions](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#b-different-command-namespacespaths--confirmed-static-distinctions) | <a id="b-native-rate-schedule-producer--source-bound-call-chain"></a> [B. Native rate schedule producer — source-bound call chain](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#b-native-rate-schedule-producer--source-bound-call-chain) | <a id="b-htt-aggregation-path--numeric-packing-confirmed-meanings-inferred"></a> [B. HTT aggregation path — numeric packing confirmed, meanings inferred](UMAC_DATAPATH_CONTINUATION_b223ee5cde_002.md#b-htt-aggregation-path--numeric-packing-confirmed-meanings-inferred) | <a id="b-mcs-capability-mask--exact-numeric-filter-inferred-capability-meaning"></a> [B. MCS capability mask — exact numeric filter, inferred capability meaning](UMAC_DATAPATH_CONTINUATION_b223ee5cde_002.md#b-mcs-capability-mask--exact-numeric-filter-inferred-capability-meaning) | <a id="b-held-whal-table-and-encoded-bytes--available-static-data-not-live-state"></a> [B. Held WHAL table and encoded bytes — available static data, not live state](UMAC_DATAPATH_CONTINUATION_b223ee5cde_002.md#b-held-whal-table-and-encoded-bytes--available-static-data-not-live-state) | <a id="a-htchif-transport-to-ce---original-source-chain"></a> [A. HTC/HIF transport to CE - original source chain](UMAC_DATAPATH_CONTINUATION_b223ee5cde_002.md#a-htchif-transport-to-ce---original-source-chain) | <a id="b-subtype1e-receiver-fields---conditional-radio-model"></a> [B. Subtype1e receiver fields - conditional radio model](UMAC_DATAPATH_CONTINUATION_b223ee5cde_002.md#b-subtype1e-receiver-fields---conditional-radio-model) | <a id="b-initial-umac-only-boundary---preserved-scope-subsequently-extended"></a> [B. Initial umac-only boundary - preserved, scope subsequently extended](UMAC_DATAPATH_CONTINUATION_b223ee5cde_003.md#b-initial-umac-only-boundary---preserved-scope-subsequently-extended) | <a id="b-actual-poll-host-serialization---original-bytes-now-qualified"></a> [B. Actual poll host serialization - original bytes now qualified](UMAC_DATAPATH_CONTINUATION_b223ee5cde_003.md#b-actual-poll-host-serialization---original-bytes-now-qualified) | <a id="continued-source-proof-hook-contexts-and-the-hif-buffer-handle"></a> [Continued source proof: hook contexts and the HIF buffer handle](UMAC_DATAPATH_CONTINUATION_b223ee5cde_004.md#continued-source-proof-hook-contexts-and-the-hif-buffer-handle) | <a id="dependency-acquisition-result-initializer-found-submit-invariant-under-review"></a> [Dependency acquisition result: initializer found, submit invariant under review](UMAC_DATAPATH_CONTINUATION_b223ee5cde_004.md#dependency-acquisition-result-initializer-found-submit-invariant-under-review)

<!-- stage822a-payload-begin -->
  656742a38adeb0c378cc21680333bacb0c7e125a5c1f3a88ce084afcab0fee87.

Kernel value/name-pointer candidates were bound to the held raw bytes and
qualified uImage load base. Their two-word form is consistent with the
public [Linux2.6.32 export declaration](https://raw.githubusercontent.com/torvalds/linux/v2.6.32/include/linux/module.h);
this comparator is not proof of actual module loading or runtime resolution.
All acquired original hashes remained equal before/after. No tests of a
synthetic decompiler or target/RF operation were run.

### Independent source decision and corrected callback condition

PASS_WITH_LIMITS, not live-word or firmware acceptance. The reviewer checked
the original initializer/callback windows and concrete no-op origin windows,
and all12 newly captured WMI/HTC function bodies against the four UMACs
with zero instruction-byte mismatches. Kernel source ranges and module hashes
matched the recorded identities. Numeric CE composition is conditional on
the initializer's marker surviving into HIF; that runtime fact is NOT proved.

The source callback issue was resolved more precisely, without discarding
failures: HTC sets bit0 of P+34 after WMI clears it. This changes a packet
field, NOT B+3c/+40. WMI request R+1c is zero and HTCConnectService copies
R+0c onward to endpoint+8, so endpoint+18 starts null. The issue helper HAS
an outer nonnull guard at c5278/c527c (2* d1dd8/d1ddc). If this setup-null
survives, the callback arm is skipped. The preliminary inference from the
absence of an immediate guard at JALR was incomplete and is rejected.
Later endpoint-slot writers, cache selection, payload aliasing and requeue
effects on a later HIF invocation are UNKNOWN. No claimed proof rests on
the earlier packet-flag zero, a presumed zero allocator, or all DMA code
being absent. The DMA pointer WORD locations are unheld; source-derived
candidate bodies and their initializer are held and were verified.

- Adjacent umac-wmi `wmi-htc-endpoint-sendfull-followup.json`, SHA256
  5b998e27597313b873b79ff227e5843dc31d9dda0d16f1bfe4c05e53c580cf6d;
  preserved preliminary receipt, incomplete callback inference superseded.
- Adjacent umac-wmi `wmi-htc-endpoint-sendfull-followup-v2.json`, SHA256
  53b4eea1d834ddc852bc52fa37a4f24b65f3ca577d0ac8148209b4849b0fd2a5.
- Adjacent umac-wmi `dma-map-pointer-value-interpretation-v1.json`, SHA256
  4251c39977cbd5790e079892d3afa7bb49a62ac77f282aa1d72811270bc36681.
- `independent-wireless-buffer-init-review-v2.json`, SHA256
  0fa2a9d16b55d333bfe35dd0a2bad12e51a0a97276128d7ddeed5d2945d32afb.
- `independent-wireless-buffer-init-review-v2-erratum.json`, SHA256
  46a65115146184a50fe14d27613e702e102409e1eb5f23fd7025a2e213e5f366;
  corrects provider-code versus pointer-word availability, v2 preserved.

Next decisive source question EXECUTING, same RE1/E4: does original UMAC
boot/download initialization supply the radio provider words at400000/
4062dc despite their absence from all16 held radio ranges? Existing evidence
is that bounded range negative and the conditional radio dispatch, not a
ROM classification. Minimum missing evidence is exact host initialization/
download target, payload and binding, if held. Reuse existing wireless/SGMT
receipts; inspect only concrete relevant original functions and relocations.
Park at a concrete missing payload or runtime state; no generic firmware
decompile, new platform, device access or speculative ROM assignment.
<!-- stage822a-payload-end -->
