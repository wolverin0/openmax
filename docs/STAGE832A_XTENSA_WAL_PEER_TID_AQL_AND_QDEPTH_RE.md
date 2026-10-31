<!-- doc-head: Stage 832A - the QCA988x container returns zero hits for wal_peer_tid peer_tid tid qdepth aql and even the generic word queue, and the host umac.ko is equally silent on peer_tid qdepth and aql, so the per-TID depth limit has no name on either side and the PB-080 patch point cannot be identified without fabricating an offset -->
<!-- /doc-head -->
# Stage 832A — WAL peer-TID queues, per-TID depth and the PB-080 patch point

- **Receipt**: [`artifacts/autoresearch/stage832a_xtensa_wal_peer_tid_aql_and_qdepth_re.json`](../artifacts/autoresearch/stage832a_xtensa_wal_peer_tid_aql_and_qdepth_re.json)
- **Tool**: [`tools/re/dissect_stage832a_xtensa_wal_peer_tid_aql_and_qdepth_re.py`](../tools/re/dissect_stage832a_xtensa_wal_peer_tid_aql_and_qdepth_re.py)
- **Scope**: offline static. No firmware loaded, no module loaded, no radio contacted.

## 0. Seven zeros on the firmware side

Container `openwrt_qca988x_hw20_firmware_2_ct.bin`, 204,796 bytes.

| Token | Hits |
| :--- | :-: |
| `wal_peer_tid` | **0** |
| `peer_tid` | **0** |
| `tid`, `TID` | **0** |
| `qdepth` | **0** |
| `aql`, `AQL` | **0** |
| **`queue`, `QUEUE`** | **0** |

**`REFUTED`**: `firmware_names_absent = 1`.

The last row is the striking one: not `wal_peer_tid`, not `peer_tid`, but the **generic word `queue`**
is absent from 204 KB of firmware. That is consistent with a fully stripped Xtensa image — and it
means **there is no lexical path to the queue structure at all**.

## 1. The host is silent too

`umac.ko` carries `wal_` six times (the two rate-control debug IDs, Stage 459A) and **no**
`peer_tid`, `qdepth` or `aql`.

**`CONFIRMED`**: `host_queue_vocabulary_absent = 1`.

So the per-TID depth limit is **not a host constant either**. It is not that the firmware has it and
the host does not; **neither side names it**.

One nuance the measurement forced: the host carries **exactly one** `tidq` token,
`ath_net80211_exist_pendingfrm_tidq` (Stage 459A). That is a **pending-frames predicate**, not a depth
limit — it answers *"does this TID queue still hold frames"*, never *"how deep may it be"*. So the
queue appears on the host as a **predicate** and is absent as a **limit**.

## 2. What that does to PB-080

The PB-040 precedent (Stage 806A) requires an **ASCII anchor** to locate a rename target: it mutated
`UBNT_POLL_MEM_ALLOC` → `OMAX_POLL_MEM_ALLOC`, a 4-byte diff at a named string.

| Requirement for PB-080 | State |
| :--- | :--- |
| a `wal_peer_tid` anchor | **absent** (0) |
| a per-TID depth constant | **absent** |
| any queue vocabulary at all | **absent** (not even `queue`) |
| a corroborated load base | **absent** (806A) |

**`REFUTED`**: `pb080_patch_point_identified = 0`.

All four requirements fail **simultaneously and independently**. A patch with an offset here would be
a **fabricated offset**, and it would also have no proven base to be relative to.

## 3. The precise refusal

The stage asks for "the exact point for the PB-080 patch". The honest answer has three parts:

1. **it is not in this container** — no anchor, no queue vocabulary;
2. **it is not in the host** — no `peer_tid`/`qdepth`/`aql` symbol;
3. **it could not be addressed even if found** — the load base is ambiguous.

That is a stronger statement than "not found". Each of the three is independently verifiable from the
receipt, and no future run of the same tool on the same corpus can change it.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| the container carries `wal_peer_tid` | **REFUTED** (0) |
| it carries *any* queue vocabulary | **REFUTED** (0, including `queue`) |
| the host names `peer_tid` / `qdepth` / `aql` | **REFUTED** (0) |
| the host has WAL debug IDs | **CONFIRMED** (`wal_`, 6 — Stage 459A) |
| a PB-080 patch point is identifiable | **REFUTED** |
| the per-TID depth limit value | **UNKNOWN / not named anywhere** |

## 5. The operational reading

For anyone planning PB-080, this closes the lexical route:

- **do not** search harder for `wal_peer_tid`; it is not there, and neither is `queue`;
- **do not** assume the limit is a host sysctl; it is not named there either;
- the only remaining routes are a **numeric** search for the depth constant inside the SGMT payload
  (which needs a way to recognise it) or a **dynamic** observation of queue depth on a live radio.

Neither is available in this offline corpus, and PB-080 stays blocked on that basis rather than on
effort.

## 6. Gaps

- **`UNKNOWN`** — whether the per-TID limit is a constant, a computation, or derived from airtime.
- **`UNKNOWN`** — the queue structure layout.
- **`UNKNOWN`** — whether `wal_`'s two debug IDs lead anywhere near the queue code.
- **Blocked** — no anchor and no proven load base; PB-080 cannot be built here.
- **Known limit** — absence of a name is not absence of the mechanism.
- **Not attempted** — numeric scanning for the constant, any dynamic observation.
