<!-- doc-head: UMAC_DATAPATH.md continuation 4 of 5; source lines preserved -->
<!-- /doc-head -->

[Document router](UMAC_DATAPATH.md) | Part 4/5
<a id="wireless-data-path-original-umac-and-conditional-radio-fields"></a> [Wireless data path: original umac and conditional radio fields](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#wireless-data-path-original-umac-and-conditional-radio-fields) | <a id="a-ce-initialization-count-not-packet-count--confirmed-static-use"></a> [A. CE initialization count, not packet count — CONFIRMED static use](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#a-ce-initialization-count-not-packet-count--confirmed-static-use) | <a id="a-source-tx-ring--source-backed-inferred-field-roles"></a> [A. Source TX ring — source-backed inferred field roles](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#a-source-tx-ring--source-backed-inferred-field-roles) | <a id="a-hal_txq_info--tqi_qflags--candidate-identity-only"></a> [A. HAL_TXQ_INFO / tqi_qflags — candidate identity only](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#a-hal_txq_info--tqi_qflags--candidate-identity-only) | <a id="evidence-and-acceptance"></a> [Evidence and acceptance](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#evidence-and-acceptance) | <a id="b-different-command-namespacespaths--confirmed-static-distinctions"></a> [B. Different command namespaces/paths — CONFIRMED static distinctions](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#b-different-command-namespacespaths--confirmed-static-distinctions) | <a id="b-native-rate-schedule-producer--source-bound-call-chain"></a> [B. Native rate schedule producer — source-bound call chain](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#b-native-rate-schedule-producer--source-bound-call-chain) | <a id="b-htt-aggregation-path--numeric-packing-confirmed-meanings-inferred"></a> [B. HTT aggregation path — numeric packing confirmed, meanings inferred](UMAC_DATAPATH_CONTINUATION_b223ee5cde_002.md#b-htt-aggregation-path--numeric-packing-confirmed-meanings-inferred) | <a id="b-mcs-capability-mask--exact-numeric-filter-inferred-capability-meaning"></a> [B. MCS capability mask — exact numeric filter, inferred capability meaning](UMAC_DATAPATH_CONTINUATION_b223ee5cde_002.md#b-mcs-capability-mask--exact-numeric-filter-inferred-capability-meaning) | <a id="b-held-whal-table-and-encoded-bytes--available-static-data-not-live-state"></a> [B. Held WHAL table and encoded bytes — available static data, not live state](UMAC_DATAPATH_CONTINUATION_b223ee5cde_002.md#b-held-whal-table-and-encoded-bytes--available-static-data-not-live-state) | <a id="a-htchif-transport-to-ce---original-source-chain"></a> [A. HTC/HIF transport to CE - original source chain](UMAC_DATAPATH_CONTINUATION_b223ee5cde_002.md#a-htchif-transport-to-ce---original-source-chain) | <a id="b-subtype1e-receiver-fields---conditional-radio-model"></a> [B. Subtype1e receiver fields - conditional radio model](UMAC_DATAPATH_CONTINUATION_b223ee5cde_002.md#b-subtype1e-receiver-fields---conditional-radio-model) | <a id="b-initial-umac-only-boundary---preserved-scope-subsequently-extended"></a> [B. Initial umac-only boundary - preserved, scope subsequently extended](UMAC_DATAPATH_CONTINUATION_b223ee5cde_003.md#b-initial-umac-only-boundary---preserved-scope-subsequently-extended) | <a id="b-actual-poll-host-serialization---original-bytes-now-qualified"></a> [B. Actual poll host serialization - original bytes now qualified](UMAC_DATAPATH_CONTINUATION_b223ee5cde_003.md#b-actual-poll-host-serialization---original-bytes-now-qualified) | <a id="independent-source-decision-and-corrected-callback-condition"></a> [Independent source decision and corrected callback condition](UMAC_DATAPATH_CONTINUATION_b223ee5cde_005.md#independent-source-decision-and-corrected-callback-condition)

<!-- stage822a-payload-begin -->
  6be7fdb0d65bc9c159203a290718fa1d7dd7f351e52dbfc35d5bcf6b36c0f6e3.
- `umac-wmi-export-link-v1.json`, SHA256
  9c71068ae78d2d6b599b81545a11e25a21f09025a83065af40c8c6f930c0444f.

Independent review of the transport, receiver selector and base aliases is
frozen PASS_WITH_LIMITS. The reviewer re-read original bytes and arithmetic;
the9b23e0 Xtensa interpretation was NOT independently regenerated and
remains explicitly common-profile-conditional, not vendor ABI acceptance.

- `independent-rate-override-selector-review-v1.json`, SHA256
  851208f5d41d0dbe9bbf72df2fa24956116301ea806666655b3da99a000fddb6.
- `independent-wireless-review-errata-v1.json`, SHA256
  aee96450a75f584106ad79476c40b124f03148af2560ae3bd4d99e2e45e546ec.
  Corrects four-byte/two-instruction wording without changing frozen evidence.
- `independent-radio-parser-alias-review-v1.json`, SHA256
  a90bbc51089307a4f42dee93922973b1f96fc8560c9005f7c763df2507485c9e.
- `independent-transport-edge-supplement-v1.json`, SHA256
  f19f8b5021f336088ff3daac3704f87a2fbd97d6218231048162d3afa5232fa4.
- `independent-transport-chain-review-v1.json`, SHA256
  47cc63e76fb40441b7cab63a2ad70591a49b9f3af541ab1c1d832d854b61f83f.
- `independent-poll-host-serialization-review-v1.json`, SHA256
  e97e6a52ff31d019f05a39dc39ad5941631600104ff37dcac6b51b2607b6e196.
- `independent-poll-host-serialization-review-errata-v1.json`, SHA256
  8caf2818c2bd0e2995486570917d50c97f2525299da69106827d77cca2942619.

Host serialization and static export linkage are independently reviewed
PASS_WITH_LIMITS. Original module/radio bytes remain unchanged; only private
wireless analysis artifacts were written. No source code was transferred
into a replacement firmware and no target/RF/flash operation was performed.

Requested bounded wireless mapping now has source-qualified answers for
CE count/rings/transport,17/1e CPU serialization and conditional receiver
field/rate packing. Remaining exact HAL type/flags namespace, provider
implementation, radio table binding/core state and runtime/on-air effects
are UNKNOWN, not static acceptance. No A-MPDU association to17/1e is
established; the distinct numeric HTT tag5 path is the held aggregation
candidate. A/B full semantic acceptance remains PARTIAL, not completed
firmware RE or wireless improvement. DNS/libcurl/decompiler fixtures are PARKED.

Next dependent proof needs unavailable provider contents/core state or an
authorized runtime observation, not another decompiler fixture. An audit
of all16 held radio manifests (AP/STA/PTP/bootstrap across four families)
shows the words at400000/4062dc outside their held ranges. Their memory
type is still UNKNOWN, not automatically ROM. Offline originals cannot
establish live module selection, firmware acceptance or ACK behavior.

## Continued source proof: hook contexts and the HIF buffer handle

Parent remains RE1/E4 wireless datapath, not DNS/E2. Minimum missing evidence:
the original initializer/writer of the buffer word HIF reads to form CE send
flags. The operator selected option1 authorizing read-only implementation and
dependency inspection in these same held8.7.25 images. No target execution,
device access, new import database or firmware change is authorized here.
Park the dependent claim at an unheld implementation or runtime-only value;
do not infer a default from an allocator name or public upstream ABI.

CONFIRMED static source edges across all four families: poll-host hook data
slot0 relocates to .text+a10. That callback saves incoming a0 as S, passes S
to data_create, and publishes its normal returned R at S+1dedc (WA/XC) or
S+1df48 (2WA/2XC), in the event-registration call delay slot at b7c.
The constructor receipt separately qualifies R+0=S under normal-return ABI
assumptions; this is not observed runtime object identity. The source WMI
handle field is S+1df7c /1dfe8. Service setup requests100, stores its response
endpoint at W+8 and HTC argument at W+800c; the sender reads those fields.
Exact source registration/use is proved, not actual loading or call order.

The corrected transport chain distinguishes list, packet and buffer objects:
sender stores B at cookie C+44; packet P=C+4; issue helper initially keeps a
list in s2, THEN overwrites s2 from P+40. Its HIF call delay-slot SW at c574c
(WA/XC) /d22ac (2WA/2XC) therefore passes B, not the list, as argument5.
HIF reads B+3c on WA/2WA or B+40 on XC/2XC. Those offsets are hex. Neither
this word's initialization nor its vendor type/name was proved by that chain.
The original list-pointer interpretation is rejected and preserved unchanged.

Reused independently accepted CE correction v15 gives numeric descriptor
bit17 = config_word.bit1 AND NOT(sendword.bit0), NOT inverse bit16. No
fixture was rerun. That numeric formula is not a hardware byte-swap finding.

- `wireless-context-link-v1.json`, SHA256
  f1c46771972c475a843629718729a68dd3400b7a2ca4dd3b24b8a0b12682bcce.
- Adjacent umac-wmi `wmi-hif-metadata-writer-boundary.json`, SHA256
  823eff0e5dc90dcc587e4d681e5276621762c9be889c6787921841b0220a048e;
  retained first receipt, list-pointer interpretation REJECTED.
- Adjacent umac-wmi `wmi-hif-metadata-buffer-pointer-correction.json`, SHA256
  490a345df83420b1667bdae4ff5adbb381ca1269baab3230e468eb1196424910.
- `independent-hif-context-review-v1.json`, SHA256
  2ee333dd7dbfd0f012810902d134f017291ba5e38c9f87dbd691e87bf8520e2d;
  PASS_WITH_LIMITS, original-byte pointer/context checks, no runtime proof.
- `../../re1-ce-framing-20261012T1640Z-worker/ce-descriptor-bit17-correction-v15.json`, SHA256
  b6aa5939ba553b9562f699ea60faa97a202dee9978466d767aebbd225aed9cda.
- Same directory `independent-ce-bit17-v15-review-v1.json`, SHA256
  fa8dbc77451bb19b92dc23d9ee5d696e0988ab6075ec22b952850f6f3179a23d.

Next decisive step EXECUTING: identify original wbuf_alloc/adf/map providers
and read only the necessary allocation/mapping bodies to resolve B+3c/+40
writer/default-bit provenance. The newly authorized dependency read means
this remaining offline step is executable; no hardware gate is fabricated.

### Dependency acquisition result: initializer found, submit invariant under review

The requested offline read found explicit static export records for
ath_dev.ko:wbuf_alloc and adf.ko:__adf_nbuf_alloc/map/map_single in all four
families. Successful ADF allocation clears [B+20,B+50) on WA/2WA, or
[B+24,B+54) on XC/2XC, then stores byte e0 at B+3d /B+41. Thus its
source-derived HIF-word initialization is bytes00 e0 00 00, numeric
M=00e00000 under the held BE-MIPS interpretation, NOT zero. The actual
imported kernel memset source was read, not assumed solely from its name.
General __alloc_skb zeroing is NOT asserted: a recycled-buffer return exists;
the separate ADF clear is the relevant normal-return initializer.

The normal kernel skb_push/trim/put source stores are outside B+3c/+40.
ADF map_single saves B but passes the VALUE *(B+c4) / *(B+c8) to DMA,
not B and not the address B+data_offset. Its local map-result store is at
B+24 /B+28. Payload/object non-aliasing remains a valid-buffer assumption,
not an observed runtime address relation. The held DMA wrapper is available:
it dispatches direction-specific callbacks, then computes a mapping result;
its mapping-error wrapper returns zero. The callback words themselves lie
outside the held raw range, but their initializer code is held. One setup
branch installs an exact JR-ra/NOP function, another installs held CACHE/
indirect-dispatch candidates. Candidate origins were followed from original
constants through slot stores; runtime selection and other writers are
unproved. Out-of-file pointer words do not prove all provider code is absent.

Original HIF/CE forwarding gives a qualified numeric relation: HIF extracts
x=((M>>21)>>i)&1 for a fragment row, or x=(M>>23)&1 for the final linear row;
it passes f=x XOR1. The send-list stores f at row+10, forwards it unchanged
for the final descriptor, and ORs10000hex for non-final descriptors. With
the accepted CE correction, descriptor.bit17=config.bit1 AND x;
descriptor.bit16 is the non-final-row bit. IF the ADF-initialized M survives
to HIF, leading count is0, x=1, f=0, final bit16=0 and bit17=config.bit1.
The earlier source-only M=0 case is hypothetical, not the allocator default.
These are numeric source fields, not accepted hardware byte-swap or RF facts.

Minimum missing submit evidence: any intervening B-capable callback and its
guard. WMI explicitly clears C+38, hence P+34 for P=C+4; issue-helper's
indirect callback is guarded by bit0 of P+34. Its intervening writes and
endpoint callback origin are being checked rather than guessed. Independent
semantic review of initializer, kernel helpers and flag composition is active.

- Adjacent umac-wmi `allocator-export-and-hif-source-initialization.json`, SHA256
  81244563efe8db67abb5c78bb0b5432c98a0e67152c14ff8fd4386e2a2cbdc0d.
- Adjacent umac-wmi `dma-map-object-boundary-followup.json`, SHA256
  e3de6d42e27c63c27e2f1fd06075bd5163dd7272250dc487324323fe8b3342dd;
  pointer-value wording requires the explicit correction above.
- `wireless-kernel-buffer-helper-source-v1.json`, SHA256
  d75be4552e9f3e306dd458eca4d19bab84364531cb8ffa5bdff0cc4fb32759a1.
- `wireless-kernel-length-helper-source-v1.json`, SHA256
  c733843350068f4ed864710a336e837321030a756ba92ed931321d5d596d8887.
- `wireless-ce-send-list-flag-source-v1.json`, SHA256
  c13b017249c54f7345b99dc98782a18b8f3a9329119e8ada2a85f7d61b9039a6.
- `wireless-kernel-dma-provider-frontier-v1.json`, SHA256
  94a69f05cfdc2da4ee81f96a19b039b3de4038f11d52f2e758934456bf2dc821.
- `wireless-kernel-dma-callback-initializer-v1.json`, SHA256
  54f3ce06199f574a87c61b915c9a6e51cb09af6a25216111eb3fefc0243c2f78.
- `wireless-kernel-dma-initializer-origin-v1.json`, SHA256
<!-- stage822a-payload-end -->
