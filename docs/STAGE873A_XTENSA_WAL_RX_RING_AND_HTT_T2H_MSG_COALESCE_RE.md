<!-- doc-head: Stage 873A - the QCA988x container carries zero receive vocabulary including the bare word ring in both cases, and because a T2H message type is one byte wide while the rarest byte in the image occurs 133 times the numeric route to the RX indication path is information-free by construction -->
# Stage 873A — QCA988x RX ring and HTT T2H RX indication

- **Receipt**: [`artifacts/autoresearch/stage873a_xtensa_wal_rx_ring_and_htt_t2h_msg_coalesce_re.json`](../artifacts/autoresearch/stage873a_xtensa_wal_rx_ring_and_htt_t2h_msg_coalesce_re.json)
- **Tool**: [`tools/re/dissect_stage873a_xtensa_wal_rx_ring_and_htt_t2h_msg_coalesce_re.py`](../tools/re/dissect_stage873a_xtensa_wal_rx_ring_and_htt_t2h_msg_coalesce_re.py)
- **Scope**: offline static. No firmware loaded, no module loaded, no radio contacted.

## 0. No receive vocabulary exists

`openwrt_qca988x_hw20_firmware_2_ct.bin`, 204,796 bytes.

| Token | Hits |
| :--- | :-: |
| `wal_rx_ring`, `rx_ring` | **0** |
| `RX_IND`, `rx_ind` | **0** |
| `RX_FRAG`, `FRAG`, `frag` | **0** |
| `T2H`, `t2h`, `T2H_MSG` | **0** |
| **`ring`, `RING`** | **0** |

**`REFUTED`**: `rx_vocabulary_hits = 0`, `ring_word_hits = 0`.

The last row is the decisive one. It is not that the specific identifiers are missing — the bare
English word `ring` and its uppercase form are absent too, in both cases, from 204 KB. Compare Stage
855A, which found `ring` absent as well. The image is **fully stripped in this region**, so there is no
lexical path to the receive path at all.

## 1. The discriminant search is saturated, and that is provable

An HTT T2H message type is a **one-byte** discriminant. Stage 855A tested 16-bit constants against a
chance expectation. At **8 bits** the method stops working, and the arithmetic says so:

```
expected occurrences of any single byte value = 204_796 / 256 = 799.984
```

The tool measures the real distribution instead of assuming it:

| Statistic | Value |
| :--- | :-: |
| expected per byte value | **799.984** |
| **minimum** observed | **133** |
| distinct values present | 256 |

**`CONFIRMED`**: `byte_space_saturated = 1`, `byte_discriminant_is_uninformative = 1`.

Even the **rarest** byte occurs **133** times. So **every** possible message-type value is present
hundreds of times, and a numeric hit carries **zero** information about which one is `RX_IND`. A tool
reporting "found the discriminant at offset X" would be reporting one of at least 133 coincidences.

This is a stronger statement than "not found": it says the search **cannot** succeed at that width, no
matter how much effort is applied.

## 2. The 32-bit route fails for the same structural reason

At 32 bits the expectation falls to `4.8e-05` per value, so the tool scans discriminants 1 to 16.

**`CONFIRMED`**: `candidates_32bit = 16` — **all sixteen** values are candidates.

That is not a discovery, it is a signature of **zero-padding**: a small little-endian integer appears as
`01 00 00 00`, `02 00 00 00` and so on, because most 32-bit fields in a firmware image are small values
in wide slots. The scan therefore cannot discriminate either, and the offsets are recorded with **no
attribution**.

Note also the width argument: a T2H message type is one byte, so a 32-bit match **cannot** be a message
type by construction.

## 3. What is confirmed

The container is **two SGMT segments** behind a `QCA-ATH10K` magic, with **113** long printable ASCII
runs (8 bytes or more) between them. That structure matches Stage 855A exactly.

The receive path is **unanchored**, and both numeric widths are non-discriminating.

`rx_ring_recovered = 0`, `t2h_rx_ind_recovered = 0`.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| the container carries receive vocabulary | **REFUTED** (0) |
| it carries the bare word `ring` in either case | **REFUTED** (0) |
| the byte space is saturated | **CONFIRMED** (rarest value occurs 133 times) |
| a one-byte numeric search can isolate `RX_IND` | **REFUTED** (information-free) |
| the 32-bit scan discriminates | **REFUTED** (16 of 16 candidates) |
| the file is a two-segment QCA-ATH10K container | **CONFIRMED** |
| the RX ring or RX indication path is located | **REFUTED** |

## 5. The operational reading

For anyone planning work on the RX path, three things follow:

1. **the name route is closed** — there is nothing to grep for, not even `ring`;
2. **the byte route is closed** — every discriminant value is present hundreds of times;
3. **the remaining route is disassembly** of the Xtensa text section at the entry point, which needs the
   load base that Stage 855A showed is ambiguous (`0x00980000` little-endian against `0x00009800`
   big-endian).

So the sequence is: resolve the base, disassemble, then read the completion handling. No numeric or
lexical shortcut exists, and this stage proves that rather than asserting it.

## 6. Gaps

- **`UNKNOWN`** — the RX ring layout and its depth.
- **`UNKNOWN`** — the actual `RX_IND` discriminant value.
- **`UNKNOWN`** — the segment load base.
- **Blocked** — no anchor, saturated byte space, ambiguous base.
- **Known limit** — absence of a name is not absence of the mechanism.
- **Not attempted** — disassembly, dynamic validation.
