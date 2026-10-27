<!-- doc-head: UMAC_DATAPATH.md continuation 2 of 5; source lines preserved -->
<!-- /doc-head -->

[Document router](UMAC_DATAPATH.md) | Part 2/5
<a id="wireless-data-path-original-umac-and-conditional-radio-fields"></a> [Wireless data path: original umac and conditional radio fields](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#wireless-data-path-original-umac-and-conditional-radio-fields) | <a id="a-ce-initialization-count-not-packet-count--confirmed-static-use"></a> [A. CE initialization count, not packet count — CONFIRMED static use](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#a-ce-initialization-count-not-packet-count--confirmed-static-use) | <a id="a-source-tx-ring--source-backed-inferred-field-roles"></a> [A. Source TX ring — source-backed inferred field roles](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#a-source-tx-ring--source-backed-inferred-field-roles) | <a id="a-hal_txq_info--tqi_qflags--candidate-identity-only"></a> [A. HAL_TXQ_INFO / tqi_qflags — candidate identity only](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#a-hal_txq_info--tqi_qflags--candidate-identity-only) | <a id="evidence-and-acceptance"></a> [Evidence and acceptance](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#evidence-and-acceptance) | <a id="b-different-command-namespacespaths--confirmed-static-distinctions"></a> [B. Different command namespaces/paths — CONFIRMED static distinctions](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#b-different-command-namespacespaths--confirmed-static-distinctions) | <a id="b-native-rate-schedule-producer--source-bound-call-chain"></a> [B. Native rate schedule producer — source-bound call chain](UMAC_DATAPATH_CONTINUATION_b223ee5cde_001.md#b-native-rate-schedule-producer--source-bound-call-chain) | <a id="b-initial-umac-only-boundary---preserved-scope-subsequently-extended"></a> [B. Initial umac-only boundary - preserved, scope subsequently extended](UMAC_DATAPATH_CONTINUATION_b223ee5cde_003.md#b-initial-umac-only-boundary---preserved-scope-subsequently-extended) | <a id="b-actual-poll-host-serialization---original-bytes-now-qualified"></a> [B. Actual poll host serialization - original bytes now qualified](UMAC_DATAPATH_CONTINUATION_b223ee5cde_003.md#b-actual-poll-host-serialization---original-bytes-now-qualified) | <a id="continued-source-proof-hook-contexts-and-the-hif-buffer-handle"></a> [Continued source proof: hook contexts and the HIF buffer handle](UMAC_DATAPATH_CONTINUATION_b223ee5cde_004.md#continued-source-proof-hook-contexts-and-the-hif-buffer-handle) | <a id="dependency-acquisition-result-initializer-found-submit-invariant-under-review"></a> [Dependency acquisition result: initializer found, submit invariant under review](UMAC_DATAPATH_CONTINUATION_b223ee5cde_004.md#dependency-acquisition-result-initializer-found-submit-invariant-under-review) | <a id="independent-source-decision-and-corrected-callback-condition"></a> [Independent source decision and corrected callback condition](UMAC_DATAPATH_CONTINUATION_b223ee5cde_005.md#independent-source-decision-and-corrected-callback-condition)

<!-- stage822a-payload-begin -->
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
<!-- stage822a-payload-end -->
