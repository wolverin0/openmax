<!-- doc-head: Exclusive RE1 wireless datapath source findings -->
Scope: held latest8.7.25 wireless path and authorized offline dependencies; originals unchanged.
DNS/libcurl/decompiler fixtures are PARKED by operator; no such run is resumed.
CE ring fields and configured capacities are static evidence, not radio ACK/live ownership.
HAL type names and radio ABI remain candidates until exact vendor binding is proved.
Native rate schedule and HTT aggregation are separate from the vendor poll subtypes.
<!-- /doc-head -->

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
producer entry. That producer invokes named `wmi_send_node_rate_sched`,
which allocates/copies/sends188bytes. Missing STT_FUNC ownership of the producer
does NOT erase the exact section-relative edge. This corrects an earlier
overly narrow 'not proven to feed sender' interpretation.

Producer payload offsets (hex), source is its incoming a3 schedule:

| Source | Destination | Observed transformation |
| --- | --- | --- |
| incoming a2 | +0 | word store |
| six bytes from incoming a1 | +4/+8 | byte-reordered word construction |
| source+0..14 | +c..20 | six words |
| source+18..22 | +24..38 | six halfwords expanded to word slots |
| source+24..29 | +3c..50 | six bytes expanded to word slots |
| source+2a..2f | +54..68 | six bytes expanded to word slots |
| source+30..35 | +6c..80 | six bytes expanded to word slots |
| later source words/bytes | +84..b8 | source-qualified scalar copies; see receipt |

These are exact byte/register layouts, not adopted vendor structure labels.
New original lookup evidence resolves the normal-path first array as selected
**row indices**, not the separately returned encoded code byte. Callback slot3
in relocation-backed rateInternalIndirectionTable points to `_GetRateTblAndIndex`.
The caller supplies index output at sp+85, table pointer at+80 and code output
at+86; it reads the index for row comparisons/array stores, with no code-output
load in the bounded body. Sentinel/fallback paths remain excluded.
Second-array stores draw an unnamed byte from an indirect object+4c; TX-power
is only a candidate interpretation. That cursor can reach third-array offsets
30..35 if its data-dependent iteration exceeds six; no fixed-zero/unwritten
or retry-count interpretation is accepted. Exact iteration remains unknown.
Final radio handler/core/ABI/state remain unqualified.

## B. HTT aggregation path — numeric packing confirmed, meanings inferred

`ol_txrx_aggr_cfg` tail-calls `htt_h2t_aggr_cfg_msg` after a0 pointer loads.
It does not overwrite a1/a2: both arguments are forwarded, not ignored.
The callee saves them as P/Q and constructs a four-byte CPU word:
tag5; P shifted8 when P!=0 and signedP<65; Q ORed at shift16 when Q!=0
and signedQ<32. This has **no explicit lower-bound check or masking**,
so it is not a general validated1..64/1..31 API. Native calls/HTCSendPkt
and allocation fields are source-qualified; final on-wire endian is not.
The 2WA/2XC named setter's selector49 dispatch loads P from its incoming
value and sets Q=0, through the original .rodata table/branch/forwarding path.
Parameter names/units are not established by the numeric selector alone.

INFERRED comparison only: primary [Linux HTT definitions](https://raw.githubusercontent.com/torvalds/linux/master/drivers/net/wireless/ath/ath10k/htt.h)
identify tag5 aggregation with A-MPDU/A-MSDU subframe-count fields. This
supports interpreting P/Q as those limits, not exact vendor ABI, effective
radio aggregation or a poll-subtype association.

## B. MCS capability mask — exact numeric filter, inferred capability meaning

WA/XC `_RateInMCSSetCheck` reads two-bit groups from input halfword+18.
Cases0/1/2/3 select source byte+13 /source word+10&1ff /word&3ff /zero,
respectively; it accumulates10-bit groups and ANDs them into child+20/+24/+28.
The case0 byte is a source-dependent8-bit mask, not an unconditionalff.
INFERRED VHT capability comparison: [Linux ath10k mapping](https://github.com/torvalds/linux/blob/master/drivers/net/wireless/ath/ath10k/mac.c)
uses the corresponding two-bit capability cases for MCS0..7/0..8/0..9.
Exact vendor object type/NSS limit/radio effect are not adopted from that match.
2WA/2XC lack this exact named symbol; that is not proof the behavior is absent.
Their named default-mask function/table accessor remain separately captured.
The initial helper's StopIteration is preserved; no fake function is created.

B evidence, relative private files in adjacent umac-wmi directory:

- `umac-aggregation-parameter-followup.json`, SHA256
  13c38a7c2be3fba85a0dd7f68fcf2de11eaed58d4b79e2ccc2d63c4f7cc8ac74.
- `umac-producer-windows.json`, SHA256
  b713e28bc453b4bd7a1fd9227cb4a4d1c69a0288a935ed54f8c0c1a46d03463e.
- `umac-call-contexts.json`, SHA256
  45791fbb49185045c45ef476dfa2577ac61dfd884f913db4081205fec2310179.
- `vap-set-param-rodata-table.json`, SHA256
  e9ac8d701e0be7c3fd8b09de502bd24a6476575298faefcda9cf758befb52d87.
- Independent static chain/geometry review: `independent-wireless-wmi-geometry-review-v2.json`,
  SHA256 227353e10958245bcb4158a1d257bdd7ab36e7213a2c412b8495dcb5cf110d62.
- Named MCS capture: `umac-mcs-mask-receipt-v2.json`, SHA256
  924c9d71730e715ddc3a941ac80dc33c02b7ffea97ffdbd13d1387f2571e42df;
  independent `independent-wireless-mcs-review-v1.json`, SHA256
  93bcf8fb9b08afcd4aa68f8045447beacb532853f06ea64f68798ce2b7a11a1b.

## B. Held WHAL table and encoded bytes — available static data, not live state

whalGetRateTable's matching HI16/LO16 .rodata reference points to section
offsetf858 in WA/XC and10408 in2WA/2XC. The four tables are byte-identical:
6012bytes, 12-byte prefix and150 records of40bytes; table SHA256
9b3681b2318b412197b4a438af81d614bc43e8c21afa3a330bec57b429f3689e.
The static contents are AVAILABLE; actual runtime table binding/row remains
unproved. This supersedes any blanket assertion that all table contents are missing.

Offset legend: all offsets are HEX. The lookup cursor b=table_base+40*i
still includes the12-byte prefix; the actual record starts b+c. Therefore
field b+10 is a big-endian group WORD at actual record+4, whose low byte is
at record decimal7. Code b+24 is actual record+18hex (decimal24); b+26 is
record+1ahex (decimal26). Never conflate record base/header base/decimal/hex.

| Group word b+10 | Rows | Original code-byte b+24 pattern |
| --- | --- | --- |
| 0 | 4 | 40..43 |
| 1 | 8 | 00..07 |
| 2 / 3 | 24 each | 80 /90 /a0 blocks,8 ordinal values each |
| 4 /5 /6 | 30 each | c0 /d0 /e0 blocks,10 ordinal values each |

Numerical formula is source-observed: prefix80 orc0 OR block<<4 OR ordinal.
INFERRED meaning, supported by matching legacy rates and primary
[Linux WMI rate-code definitions](https://raw.githubusercontent.com/torvalds/linux/master/drivers/net/wireless/ath/ath10k/wmi.h):
high2bits=preamble, bits4..5=NSS−1, low4bits=MCS for HT/VHT.
No proof this table is selected live or that the physical radio supports3SS.
Zero-validity rows are retained (including20MHz candidate MCS9 with1/2SS);
listing a row does not mean it is enabled or safe to select.
The extra hypothesis b+26 always equals within-block ordinal was REJECTED:
rows20..27/44..51 have values8..15. The failed original helper remains;
only the independently observed code-byte invariant is adopted.

- `rate-index-vs-code-followup.json` (adjacent umac-wmi), SHA256
  c157b44e5e7f96dd2af86136983d426669494e5214a11f047da5b9492b149251.
- `rate-schedule-array-origin-followup.json`, SHA256
  21678ab32320566719ff83822fbfbe74d1e0afede472c202b9be3155128650b9;
  original frozen bytes intact; mistaken reconstruction is REJECTED/nonmatching.
- `umac-whal-rate-table-receipt-v2.json`, SHA256
  d9078950ab5538b8ac4cdb090e75ad3421984bfd2181603a9b8db3bfcd9340d6.
- Independent `independent-whal-index-code-review-v1.json`, SHA256
  5d2e7a2d2dabd502a5378a3e97dd14c50e9c00c42c479d41795b21fd4f225048.

## A. HTC/HIF transport to CE - original source chain

The exact named HTCSendPkt wraps its packet argument in a stack list and
calls HTCSendPktsMultiple. The latter has a R_MIPS_26 .text section edge
to an unnamed entry: c51ec in WA/XC, d1d4c in2WA/2XC. A bounded1996-byte
original window from that entry contains the HIFSend_head transfer
at c5748 /d22a8. This is a source-bound edge, not an adopted function name,
complete CFG or a runtime observation. HTCSendDataPkt independently has
an exact HIFSend_head relocation and obtains its pipe from endpoint+48.

HIFSend_head masks its pipe argument to8bits, selects the entry at
HIF_base+28+pipe*2c, and loads its CE pointer from entry+4. It constructs
a send list from the original buffer segments and calls CE_sendlist_send.
Its available-entry accounting is not a radio firmware queue-depth metric.
HIFMapServiceToPipe's normal numeric mappings are source0/destination1
for service1 orfe00; source3/destination2 for100..104; source4/destination1
for300. Unknown service paths return1 without establishing a valid mapping.
HTCConnectService writes these pipe outputs to endpoint+48/+49; actual
endpoint/service selection by a live WMI/HTT handle remains unproved.
These conditional configured source pipes select capacities16/32/2048
from the table above, not live occupancy, usable radio slots or ACKs.

- `umac-transport-receipt.json`, SHA256
  5ad5f5a031bbb081b3324011359059927c6c43e5dc6ba957c362e9a4ace633c2.
- `umac-transport-callers-receipt.json`, SHA256
  5f17f87c3f03ae837ce36fb1ddd3ef6e6af099068221941dc934653cc856b850.
- `umac-transport-issue-window-receipt.json`, SHA256
  766b740608cee784988aba048c1ba4d8a0b26abab3b9940df926aaa6a0734527.

## B. Subtype1e receiver fields - conditional radio model

The frozen WA adapter at9b232d reads five consecutive bytes at
record+84..88 into a11..a15, then calls9b7684. Under the explicitly
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
