<!-- doc-head: STAGE18_WMI_0x9044_RATE_SCHEDULE_AND_SUB20MHZ_CONTROLLER.md continuation 1 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE18_WMI_0x9044_RATE_SCHEDULE_AND_SUB20MHZ_CONTROLLER.md) | Part 1/2
<a id="verification-and-evidence-limits"></a> [Verification and evidence limits](STAGE18_WMI_0x9044_RATE_SCHEDULE_AND_SUB20MHZ_CONTROLLER_CONTINUATION_417f3263fc_002.md#verification-and-evidence-limits) | <a id="reproduction-and-concrete-remaining-evidence"></a> [Reproduction and concrete remaining evidence](STAGE18_WMI_0x9044_RATE_SCHEDULE_AND_SUB20MHZ_CONTROLLER_CONTINUATION_417f3263fc_002.md#reproduction-and-concrete-remaining-evidence)

<!-- stage822a-payload-begin -->

Twelve synthetic schedules,three blocked width plans; requested single-file pytest77PASS.
Primary header masks govern16-byte descriptors; native188-byte binding remains unknown.
PB040 table bytes verified; PLL/effective5/10MHz authority remains unknown.
No device,SSH,RF,patch,load or flash; E2 NOT_ACCEPTED and all actuation disabled.


# Stage18B: WMI retry schedules and sub20MHz planning

## Prespecified parent, question and acceptance

Task `T-S18B-CODEX-WMI-0x9044-AND-SUB20MHZ-PLANNER` extends the original
`artifacts/2026-09-20-forward-plan.html` rate-control authority and reproducible
experiment deliverables, under BENCH_PLAN's offline saved-evidence boundary.
The implementation is external-controller planning, not firmware execution.
E2 remains NOT_ACCEPTED. Only the four requested files and the explicit task-board
completion are written; other shared work is preserved.

Question: what exact descriptor bytes and guarded sub20MHz proposals can be
constructed from the retained WMI/hardware headers and held module, without
inventing a proprietary ABI, clock register or physical gain?

Existing evidence before implementation: WMI10X command0x9044 and WMI10.2
command0x9045; a retained four-dword `series_bw.h`; an independently documented
188-byte vendor schedule producer; and PB040's eight-byte table spec. The vendor
schedule's unnamed arrays are not authenticated retry/chain-mask fields. A
16-byte hardware descriptor cannot be inserted into that message by analogy.

The primary header corrects the PB010 summary: chain_mask has4 bits, short_gi2
bits and ldpc2 bits. Their auxiliary symbol bits must be preserved. A 1-stream
STBC step requires two transmitting chains; it cannot be encoded on one TX chain.
The sub20 table bytes match the held module but identify rate-like constants,
not a proved PLL divider. The retained chan_to_phymode path does not establish
an operational5/10MHz host route. Coverage class adds3us per class using the
current PHY clock; propagation time must not be multiplied by bandwidth ratio.

Minimum acceptance: exact16-byte encoder/parser and field-mask checks; an adaptive
four-series policy with validated capability/rate combinations; exact family/opcode
selection; authenticated PB040 table bytes; separate5/10MHz theoretical models
and source-based coverage arithmetic; fail-closed execution status; requested
single-file pytest and independent review. Primary timing, packet-dependent
descriptor fields and the native188-byte ABI remain explicit missing evidence.

Stop after those four outputs, verification and exact task-board completion.
No parent physical experiment, device access, build, kernel reload, firmware patch,
deployment or next card is started. No physical user action is needed for this
offline deliverable. Physical control qualification remains a separate dependency.

## WMI command and descriptor contracts

| Family | WMI version | Command |
| --- | --- | --- |
| WA / XC | 10.1 | `0x9044` |
| 2WA / 2XC | 10.2 | `0x9045` |

CONFIRMED static: the retained `wmi.h` enums and the vendor sender evidence in
`docs/UMAC_DATAPATH.md` distinguish those namespaces. The builder rejects mismatched
family/version pairs. This is not acceptance by any installed firmware build.

The independently written encoder/parser implements19 fields in four dwords.
Little-endian is an explicit hardware-reference representation; big-endian and
the existing dword-swap helper are checked separately. Neither representation
establishes the final proprietary transport ABI.

| Dword | Principal fields |
| --- | --- |
| 0 | duration[13:0], TxBF[14], legacy-BW[15], chain-mask[19:16], TPC[25:20], RTS/CTS[26:27], SGI[29:28], LDPC[31:30] |
| 1 | MAC pad[19:0], STBC[20], rate[27:24], NSS code[29:28], preamble[31:30] |
| 2 | PSDU octets[19:0], PPDU symbols[30:20] |
| 3 | MPDU spacing[9:0], MPDU count[22:16], fixed delimiters[31:24] |

The header's4-bit chain field is preserved; the specific two-chain planner restricts
it to the declared two-chain hardware. NSS is human1..3 in the descriptor API and
encoded0..2. SGI bit0 enables short GI; bit1 describes a symbol-count condition.
LDPC bit0 enables coding; bit1 describes an extra11ac symbol and is rejected for HT.
Reserved bits are zero and rejected by the parser when set. The semantic MPDU limit
is64 even though its storage field has7 bits.

The codec rejects VHT20 MCS9 at1/2SS, VHT80 MCS6 at3SS, invalid legacy/HT combinations,
insufficient chains, numeric booleans and unsupported VHT/HT sub20 mappings. The
planner does not reuse a VHT20 row to represent5/10MHz operation.

`WmiPeerRateRetryScheduleBuilder.build()` emits this declared ladder:

| Series | NSS / TX chains | GI / coding | Example MCS, balanced / asymmetric |
| --- | --- | --- | --- |
| 0 | 2SS / two TX chains | SGI, LDPC | 8 / 6 |
| 1 | 2SS / two TX chains | LGI, LDPC | 7 / 5 |
| 2 | 1SS / two TX chains | LGI, STBC, LDPC | 3 / 3 |
| 3 | 1SS / stronger single TX chain | LGI, LDPC | 0 / 0 |

The third step means one spatial stream encoded across two transmitting chains.
STBC is never combined with a single TX chain. A missing declared2SS/LDPC/STBC/SGI
capability rejects this requested ladder rather than silently inventing support.
TxBF defaults off and requires explicit peer support and steering/training declarations.

The policy accepts two typed EVM/RSSI observations with explicit negative
error-to-signal EVMdB and RSSIdBm conventions. Raw pilot words, positive relative
chain RSSI or uncalibrated vendor encodings are not silently converted. Default
inputs also require a caller-supplied stream-to-TX-chain mapping; this mapping is
not qualified by the planner or by the retained EVM descriptor words. Default
imbalance thresholds are6dB; a significant EVM delta selects the lower-error chain,
otherwise RSSI selects it. Conflicting rankings are reported. Asymmetry lowers the
initial MCS by2 and changes attempts from `(2,2,2,2)` to `(1,1,3,3)`. Poor absolute
inputs cap initial MCS at2 using declared heuristic thresholds −80dBm / −15dB EVM.
Those thresholds are illustrative policy, not calibrated IEEE limits or observed
performance. Reversed asymmetry reverses the selected single-chain fallback.

Raw6-bit TPC stays constant across all four series. No TPC-to-dBm interpretation,
TX-power increase or legal EIRP assertion is made. MAC/node identity, retry budget,
TPC, bandwidth and ladder invariants are shared between the builder, exported typed
plan and JSON validator. This is a data planner, without a send API.

Four descriptors produce a **64-byte descriptor bundle**. Each descriptor is16B;
the upstream fixed-rate structure is24B; the vendor native schedule is188B. These
are separate objects. Packet-dependent duration/symbol/padding/aggregation fields
remain zero placeholders and `packet_fields_complete=false`. No descriptor is
inserted into unnamed vendor arrays, no retry count is assigned an unverified
188B offset, and `native_payload()` raises `NativeWmiAbiUnqualified`.

## PB030 and PB040

| Requested width | Candidate flag | Ideal symbol multiplier | Ideal OFDM LGI symbol | Ideal noise benefit |
| --- | --- | --- | --- | --- |
| 20MHz | neither HALF nor QUARTER | 1 | 4µs | 0dB |
| 10MHz | HALF, `1<<13` | 2 | 8µs | 3.0103dB |
| 5MHz | QUARTER, `1<<14` | 4 | 16µs | 6.0206dB |

The noise calculation is `10 log10(20/width)`, assuming equal total received signal
power, flat noise PSD and unchanged noise figure. It is not measured SNR, throughput,
range or spectral-mask compliance. A hypothetical20MHz reference clock of88 ticks/µs
gives44/22 ticks/µs under2×/4× division; no actual PLL register or divider write is
identified by that arithmetic. The requested `chanbw` values and channel flags are
proposals. Other channel flags, including DFS, passive and AP-disabled flags, remain
preserved. Conflicting HALF+QUARTER flags are rejected; unqualified sub20 HT/VHT
flags remain explicitly flagged and blocked.

Source `ath10k-ct/ath10k-7.2/hw.c:589–728` reads the current PHY clock and firmware's
base slot/ACK/CTS values. It adds `3*coverage_class*ticks_per_us` to each timer,
capping slot at65535 and ACK/CTS at16383. Its existing slot guard accepts only an
integer9µs or20µs base. These facts are preserved, including the guard's refusal of
a hypothetical13µs narrow-channel base. There is no universal ACK baseline.

`TimingReadback` must explicitly identify the requested bandwidth and state that
its base excludes prior coverage adjustment. A20MHz snapshot is not reused at5/10MHz.
Without a same-width baseline, timer output is null with
`NEEDS_BASELINE_AT_REQUESTED_BANDWIDTH`. The propagation increment stays3µs per
class; it is not multiplied by2/4. No sub20 SIFS/slot/ACK value is fabricated.

Fresh held-byte verification reads the pinned2,340,372-byte `umac.ko`, extracts the
251,681-byte `athwlan_AR9888v2_ptmp_ap_bin` ELF symbol and reuses the existing pure
SGMT memory decoder. It never calls the tracing/WSL path, saves decoded firmware,
modifies an image or applies PB040's proposed replacement bytes.

<!-- stage822a-payload-end -->
