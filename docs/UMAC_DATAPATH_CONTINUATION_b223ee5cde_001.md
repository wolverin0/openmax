<!-- doc-head: UMAC_DATAPATH.md continuation 1 of 5; source lines preserved -->
<!-- /doc-head -->

[Document router](UMAC_DATAPATH.md) | Part 1/5
<a id="b-htt-aggregation-path--numeric-packing-confirmed-meanings-inferred"></a> [B. HTT aggregation path — numeric packing confirmed, meanings inferred](UMAC_DATAPATH_CONTINUATION_b223ee5cde_002.md#b-htt-aggregation-path--numeric-packing-confirmed-meanings-inferred) | <a id="b-mcs-capability-mask--exact-numeric-filter-inferred-capability-meaning"></a> [B. MCS capability mask — exact numeric filter, inferred capability meaning](UMAC_DATAPATH_CONTINUATION_b223ee5cde_002.md#b-mcs-capability-mask--exact-numeric-filter-inferred-capability-meaning) | <a id="b-held-whal-table-and-encoded-bytes--available-static-data-not-live-state"></a> [B. Held WHAL table and encoded bytes — available static data, not live state](UMAC_DATAPATH_CONTINUATION_b223ee5cde_002.md#b-held-whal-table-and-encoded-bytes--available-static-data-not-live-state) | <a id="a-htchif-transport-to-ce---original-source-chain"></a> [A. HTC/HIF transport to CE - original source chain](UMAC_DATAPATH_CONTINUATION_b223ee5cde_002.md#a-htchif-transport-to-ce---original-source-chain) | <a id="b-subtype1e-receiver-fields---conditional-radio-model"></a> [B. Subtype1e receiver fields - conditional radio model](UMAC_DATAPATH_CONTINUATION_b223ee5cde_002.md#b-subtype1e-receiver-fields---conditional-radio-model) | <a id="b-initial-umac-only-boundary---preserved-scope-subsequently-extended"></a> [B. Initial umac-only boundary - preserved, scope subsequently extended](UMAC_DATAPATH_CONTINUATION_b223ee5cde_003.md#b-initial-umac-only-boundary---preserved-scope-subsequently-extended) | <a id="b-actual-poll-host-serialization---original-bytes-now-qualified"></a> [B. Actual poll host serialization - original bytes now qualified](UMAC_DATAPATH_CONTINUATION_b223ee5cde_003.md#b-actual-poll-host-serialization---original-bytes-now-qualified) | <a id="continued-source-proof-hook-contexts-and-the-hif-buffer-handle"></a> [Continued source proof: hook contexts and the HIF buffer handle](UMAC_DATAPATH_CONTINUATION_b223ee5cde_004.md#continued-source-proof-hook-contexts-and-the-hif-buffer-handle) | <a id="dependency-acquisition-result-initializer-found-submit-invariant-under-review"></a> [Dependency acquisition result: initializer found, submit invariant under review](UMAC_DATAPATH_CONTINUATION_b223ee5cde_004.md#dependency-acquisition-result-initializer-found-submit-invariant-under-review) | <a id="independent-source-decision-and-corrected-callback-condition"></a> [Independent source decision and corrected callback condition](UMAC_DATAPATH_CONTINUATION_b223ee5cde_005.md#independent-source-decision-and-corrected-callback-condition)

<!-- stage822a-payload-begin -->

Scope: held latest8.7.25 wireless path and authorized offline dependencies; originals unchanged.
DNS/libcurl/decompiler fixtures are PARKED by operator; no such run is resumed.
CE ring fields and configured capacities are static evidence, not radio ACK/live ownership.
HAL type names and radio ABI remain candidates until exact vendor binding is proved.
Native rate schedule and HTT aggregation are separate from the vendor poll subtypes.


# Wireless data path: original umac and conditional radio fields

Parent: RE1/E4 wireless datapath. Questions: CE count/ring structure; exact
WMI command serialization and candidate TXQ/rate fields. No source modules
outside umac/radio were changed; no target execution, RF experiment or flash.

## A. CE initialization count, not packet count — CONFIRMED static use

Operator PC `0x000dc788`, under text load-base `0x10000`, corresponds to
original `.text+0xcc788`: `aea400e4`, SW a0 at s5+0xe4, the delay slot of
the preceding J. Owner: exact ELF symbol `ol_ath_pci_configure`.
This is the **instruction address**, not the destination address of a counter.
The preceding LW reads `targetdef+0x11c`; HIF_PCIDeviceProbed uses context+0xe4
as the loop bound for CE_init calls. The count field is +0xe4 in WA/XC and
+0x88 in2WA/2XC. Target-selection7's descriptor supplies8, conditional on
that selection/globals/normal ABI, not a live-board measurement.
HIF entries advance0x2c; their configuration rows advance0x18.

## A. Source TX ring — source-backed inferred field roles

Offsets below are hexadecimal and refer to two **different objects**.
Names describe observed uses, not recovered vendor C type names.

| Object | Offset | Observed use |
| --- | --- | --- |
| CE state | +0 | parent context used for MMIO |
| CE state | +4 | engine index stored by CE_init |
| CE state | +8 | source/send ring pointer |
| CE state | +c | destination/receive ring pointer |
| CE state | +10 | engine register-base offset |
| CE state | +14 | copy of configuration first word / attribute bits |
| Registration input object | +1c/+20 | a1/a2 stored by CE_send_cb_register; candidate callback/context, concrete type unproved |
| Source ring | +0 | N, rounded from config+8 when needed |
| Source ring | +4 | N−1 mask |
| Source ring | +8 | software-completed/consumed index |
| Source ring | +c | software write/producer index |
| Source ring | +10 | cached hardware read index |
| Source ring | +1c/+20 | aligned CPU descriptor pointer / bus address |
| Source ring | +28 | aligned heap shadow descriptor pointer |
| Source ring | +2c | per-entry transfer-context array |

CE_send_entries_avail returns `(ring[+8] - ring[+c] - 1) & ring[+4]`.
CE_send_nolock checks that same space, indexes descriptors with stride8 and
contexts with stride4, updates write index modulo mask and conditionally
calls WAR_CE_SRC_RING_WRITE_IDX_SET after SYNC. Its descriptor receives a2
at word+0 and low16(a3) with SH at+6; address/length are candidate argument
roles, not proven parameter types. Other metadata is inserted into word+4.
CE_completed_send_next_nolock reads the hardware index via ioread32 at
CE register-base+0x44 when cached state is exhausted; it returns descriptor
metadata/context, clears that context entry and advances ring+8.
This qualifies **CE/DMA completion**, not over-air TX, ACK, retransmissions,
radio firmware queue depth or mac80211 TXQ ownership.

The original .data configuration rows are identical across four variants.
Matching R_MIPS_HI16/LO16 .data relocations bind the HIF table pointer, then
the loop advances each row24bytes. Under the conditional count8 setup:

| CE index | config+0 (raw attrs) | config+8 (source entries selected by CE_init) |
| --- | --- | --- |
| 0 | 2 | 16 |
| 1 | 2 | 0 |
| 2 | 2 | 0 |
| 3 | 2 | 32 |
| 4 | 10 | 2048 |
| 5 | 2 | 0 |
| 6 | 2 | 0 |
| 7 | 2 | 2 |

Zero source entries skip that send-ring allocation. These rows are configured
capacities, not current occupancy, firmware queue depth or an actual selected
WMI service/pipe. A source ring with N entries reserves one slot under its
availability formula. No capacity change or traffic experiment was performed.

## A. HAL_TXQ_INFO / tqi_qflags — candidate identity only

Original four umac binaries contain neither exact type-name token nor debug
sections. Therefore a recovered HAL_TXQ_INFO ABI cannot be asserted from them.
Conditional radio TXQ callee (WA9b7124/XC9b7128/2WA9ba2e0/2XC9ba2e4)
writes a4/a5/a6 to current stack record+14/+18/+1c and applies
`(a9 & 0xffffc5ef) | (a7 & 0x3a10)` to record+8. This replaces bits4,9,11,12,13.
Unknown provider calls at offsetsf4/288/28c prevent assigning API/type identity.
The callback length38 and frame60 are hexadecimal, distinct quantities.
This is compatible in shape with a flags-containing TXQ record, not proof.

WA subtype17's adapter at9b23e0 loads three unsigned halfwords from
incoming a3+106/+108/+10a into a12/a13/a14 and a word from a3+10c
into a15. It separately loads a byte from a3+a4+84 into a11, then
CALL8s9b7124 with a10 copied from incoming a2. Under the conditional
register-window mapping, that byte is the callee's a3; the three halfwords
become a4/a5/a6 and reach record+14/+18/+1c; the word becomes a7 and
supplies the3a10-masked record+8 update. This binds the observed receiver
input widths to the TXQ record stores, NOT an adopted HAL field layout.
The two input bases (a3 and a3+a4) must not be silently aliased or treated
as an exact host-wire structure; no byte-order bridge is established.

Public [FreeBSD HAL header](https://raw.githubusercontent.com/freebsd/freebsd-src/main/sys/dev/ath/ath_hal/ah.h)
is a comparator only: its type has flags/cwmin/cwmax fields and two16-bit
retry fields. No proof the vendor matches that layout or flags namespace;
do not import the public names into the binary as verified annotations.
The radio addressing/core/ABI remains explicitly conditional under B9bb000.

## Evidence and acceptance

- Original15function/family capture: `umac-queues-receipt.json`, SHA256
  dbed58ade7d7b36d5a969f4504df9e905b6dfb4b18153f073b8462b11da39c02.
- Original6completion functions/family: `umac-completion-receipt.json`, SHA256
  ef5af827c0e44351bf7dcd8aab0bbfce9109f860b963ddfef4668751b3ece6bb.
- Independent source review: `independent-queue-source-review-v1.json`, SHA256
  30868eae807cf92734c931e8995c78dead45f182e268fd69acfc63e962758b04.
  All original rows rechecked; zero byte mismatches, source hashes unchanged.
- Independent interpretation review: `independent-datapath-interpretation-review-v1.json`,
  SHA256 dee8c1b97ed72ca8b0ee7f64ba3db0dec1cbae116a59fe8fd89286663d2bc9d9.
  Two original wording errors corrected above; prior note hash8058790f...fe8444d
  remains recorded in that review. No verified address/length/type imposed.
- Original configuration rows: `umac-geometry-receipt.json`, SHA256
  4c67f938bd1fa4720393593c9f0a4569377d66d6d070dbf640a0a35ce8998760;
  independent row/relocation review227353e1...f110d62 confirms exact eight rows.
- Reused original count qualification: existing count-writer receiptafdcf36e...34adabb.
- Reused radio mask/source review279ced1a...f64fa9, under explicit literal model.

A is PARTIAL: CE structural uses qualified; exact vendor HAL ABI and radio
queue effect unproved. No research acceptance is inferred from a script return
code or a decompiler listing.

## B. Different command namespaces/paths — CONFIRMED static distinctions

| Family | get_cmd_label's WMI_UBNT_POLL_CMDID | native rate-schedule sender |
| --- | --- | --- |
| WA/XC | 9064 | 9044,188bytes |
| 2WA/2XC | 9070 | 9045,188bytes |

Hex command IDs. The original label branch/delay-slot/HI16/LO16 string link
is source-qualified; a label does not establish execution. Another unowned
2WA/2XC sender uses9064 with436bytes, not the poll path or subtype17/1e.
The earlier statement that native9044 applied to all four families is rejected
and superseded by these per-family original instruction literals.

The existing conditional radio routes identify17 as TXQ record replacement
and1e as rate override through host-selector provenance. They do NOT identify
either subtype as the native188-byte schedule or the HTT aggregation command.
No evidence here accepts an A-MPDU control specifically under poll subtype17/1e.

## B. Native rate schedule producer — source-bound call chain

`_RATE_GetTxRetrySchedule` passes its stack schedule to `ratectrl_update_rate_sched`.
The wrapper preserves that argument as a3 and has R_MIPS_26 to the .text
section: encoded addendd40a0 (WA/XC) /e1240 (2WA/2XC) is the actual anonymous
<!-- stage822a-payload-end -->
