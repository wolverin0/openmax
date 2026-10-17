<!-- doc-head: RE1 native rate schedule reaches guarded packet preparation -->
Original WA8.7.25 bytes support a conditional receiver-to-data-path chain.
Authorization and mode guards remain intact; no new rate-control knob is claimed.
Final transmitter provider and actual RF behavior require matching runtime evidence.
E2 remains parked and NOT_ACCEPTED; no target execution or device changes occurred.
<!-- /doc-head -->

# RE1: native rate control, downstream result

The held airOS firmware contains a path from the native rate-schedule command
to peer state that is read during packet preparation. The previous
receiver-only result and unbound threshold-reader result are superseded by
this deeper static trace. Actual transmitted rates and wireless performance
remain **UNKNOWN**.

This concerns the proprietary airOS host module and embedded QCA target
firmware. It is not an OpenWrt/ath10k-CT control implementation. All target
address bindings remain conditional on the prior `LITBASE=0x9bb001` hypothesis
and the recorded AP image/context. The original module hash is
`660435ed9c50f1390945535a975565d7234543e01933644bf99dd9deca1b2cd6`.

| Link | Finding | Qualification |
| --- | --- | --- |
| Host command to receiver | WA `0x9044`, callback registration and `0x99d034` decode the schedule. | Original-byte-backed static control flow; runtime registration unmeasured. |
| Receiver to peer | Lookup returns an entry. The pointer **stored at** `entry+0x1c` identifies the allocated peer context; constructor `0x98b670` establishes it and a back-reference. | Resolves the earlier object-identity gap; it is not simply an address addition. |
| Peer to rate consumer | `0x98f224` obtains the peer through `queue+0x44` and projects stored count, rate bytes, flag halfwords and metadata into an output buffer. | Classes 0..16 except 7 are numerically eligible under additional packet, peer and mode guards. Complete traffic-class mapping and ordinary-data execution remain conditional and unobserved. |
| Enable condition | Host authorization callback emits wire parameter 3 on `0x901f`; target maps it to internal parameter 8. Association `0x9020` also sets that internal state. | This is an authorization/state path, not a newly discovered tuning switch. Case 8 additionally tests flags/mode before setting `context+0x20 bit0x40`. |
| Rate output to packet preparation | `0x992c9c` passes the same output buffer through an optional mutation hook, then `0x992674` / `0x9926f8` use rate index/flags and `0x98e704` to calculate a packet budget. | Confirms numeric use of the rate fields. Exact units, hook effects and final rate choice remain unmeasured. |
| Final transmission handoff | That buffer reaches the indirect slot `0x4065ac`. Related final slots are `0x4065a8`, `0x4065b0` and enqueue slot `0x40657c`. | The words and resolved targets are not present in the retained AP regions or prior 16-stream survey. No final transmitter implementation is established. |

The separate `context+0x8a` threshold reader is now connected through its
held function table and peer-context callers. A positive management-command
route is established. Some control-frame paths retarget the context; therefore
this threshold cannot be described as universally governing ordinary data.

## Record interpretation and limits

The receiver's hardware loops copy six flag halfwords, six rate bytes and two
additional bytes. The consumer has a separate two-iteration loop. Ghidra's
pseudocode omitted these repetitions, so original instructions govern the
record interpretation. Default PC-relative literal aliases were also replaced
by explicit manual resolution under the recorded LITBASE hypothesis.

The count comes from a dynamic producer value. Serializing six entries does
not establish that count is bounded to six. No local 1..6 admission guard has
been established in the receiver/update path; the complete upstream invariant
is **UNKNOWN**. This is not a demonstrated exploit or a safe injection recipe.
Byte 25 of the 26-byte copied record remains without an established explicit
initializer. The indirect copy/compare/rate-table providers are still unheld.
No field is assumed zero, harmless or suitable for live modification.

## Verification and reproducibility

The new chain receipt is [native-rate-control-chain.json](native-rate-control-chain.json).
It binds the source, original regions, 24 successful bounded result exports,
two preserved prelaunch failures, analysis scripts and independent reviews.
The exports contain 6,813 checked instruction rows at 6,743 unique instruction
starts. Those counts describe verification coverage, not research benefit or
independent experimental repetitions. Targeted windows and unsuccessful
candidate roots are explicitly marked.

Private original-byte exports, full decompiler output and scripts remain in
`firmware/build/re1-applied-20261016/`. Public findings describe numeric flow
and boundaries without reproducing the proprietary implementation.
Independent reviews cover the object bridge, rate consumer, packet preparation,
case-8 gate and wire-to-internal parameter mapping, all **PASS_WITH_LIMITS**.
The original firmware is unchanged. No device was accessed or firmware code
executed during this continuation.

## Exact unresolved dependency

The next decisive evidence for the final transmitter is the **matching original
stock-airOS runtime context**, including the values at `0x40657c` and
`0x4065a8..0x4065b0`, the bytes at their resolved destinations, and the actual
core/address context and initialization state. Supporting providers at
`0x4000f8`, `0x400100`, and `0x400138` need the same qualification. A correctly
identified existing dump can satisfy this; a dump from OpenWrt/CT or zero
values obtained under that different stack cannot.

The held-source search does not prove that these providers reside in ROM or
that no other initializer exists anywhere. Bounded bootstrap analysis reached
additional unheld API pointers, rather than a byte-backed resolver. Repeating
the same image search cannot supply the missing initialized memory.

RE1 remains **PARTIAL_STATIC** at this hardware-effect boundary. No stock
flash, device acquisition, authorization change, command injection or E2
resumption follows from this report. Selecting a lab unit and authorizing a
separate bounded read-only stock-runtime acquisition would be a new operational
step; restoring stock firmware would additionally retain all existing recovery
and flash gates.
