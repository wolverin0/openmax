<!-- doc-head: Stage 855A - the QCA988x container carries zero transfer vocabulary, the Stage 671A constants occur at chance expectation in 16 bits while the 1425 negative control behaves identically, one 32-bit word equal to 2500 survives as unattributable INFERRED, and only the two-segment QCA-ATH10K structure with its ambiguous base is confirmed -->
<!-- /doc-head -->
# Stage 855A — QCA988x TX-completion fast path

- **Receipt**: [`artifacts/autoresearch/stage855a_xtensa_wal_tx_send_and_htt_tx_compl_re.json`](../artifacts/autoresearch/stage855a_xtensa_wal_tx_send_and_htt_tx_compl_re.json)
- **Tool**: [`tools/re/dissect_stage855a_xtensa_wal_tx_send_and_htt_tx_compl_re.py`](../tools/re/dissect_stage855a_xtensa_wal_tx_send_and_htt_tx_compl_re.py)
- **Scope**: offline static. No firmware loaded, no module loaded, no radio contacted.

## 0. The container has no transfer vocabulary

`openwrt_qca988x_hw20_firmware_2_ct.bin`, 204,796 bytes.

| Token | Hits |
| :--- | :-: |
| `htt`, `HTT` | **0** |
| `tx_compl`, `TX_COMPL` | **0** |
| `t2h`, `T2H` | **0** |
| `ring` | **0** |
| `pending` | **0** |
| `coalesc` | **0** |
| `copyengine` | **0** |

**`REFUTED`**: `tx_vocabulary_hits = 0`.

A stripped Xtensa image carries no identifiers, and this one carries none of the transfer vocabulary.
So the fast path cannot be located by name, and a stage that reported an offset here would be guessing.

## 1. The constants from Stage 671A were tested against chance

Stage 671A operationalised `max_num_pending_tx` with the values **1424** and **2500**. Both are
searched here at 16 and 32 bits, with **1425** as a **negative control**.

The control is the whole method. In a 204,796-byte blob there are 204,795 16-bit windows, so a given
16-bit value is expected to appear by accident

```
204_795 / 65_536 = 3.125
```

| Value | Width | Observed | Expected | Weight |
| :-: | :-: | :-: | :-: | :--- |
| 1424 | 16 | **3** | 3.125 | `no_weight` |
| **1425 (control)** | 16 | **2** | 3.125 | `no_weight` |
| 2500 | 16 | **2** | 3.125 | `no_weight` |
| 1424 | 32 | 0 | 4.8e-05 | `no_weight` |
| 1425 | 32 | 0 | 4.8e-05 | `no_weight` |
| **2500** | 32 | **1** | 4.8e-05 | `candidate` |

**`REFUTED`**: `sixteen_bit_candidates = 0` and `control_behaves_like_chance = 1`.

The control behaves **exactly** like the targets, and every 16-bit observation sits at or below chance.
Reporting "1424 found" on that basis would have been reporting noise — and the same tool would have
"found" 1425 just as convincingly.

## 2. One 32-bit word survives, and it stays unauthorised

At 32 bits the expectation collapses to `4.8e-05`, and one word equals **2500**.

**`INFERRED`** — not promoted. A single small-integer word with no anchor cannot be attributed to a
completion ring: it could be a timer, a length, a threshold, or padding. Its exact offsets are recorded
in the receipt so a future disassembly can confirm or discard it.

The distinction matters. `32bit_candidates = 1` is a **lead**, and `tx_compl_fastpath_recovered = 0`
is the **result**. The first is a place to look; the second is what is known.

## 3. What the container does support: structure

```
magic      QCA-ATH10K    1 occurrence, offset 0
segments   2             SGMT at 0x0000006c and 0x000001c58
```

**`CONFIRMED`**: the file is a **two-segment QCA-ATH10K container**. Each segment header is recorded
**raw with both endianness readings**, because the base field reads

```
0x00980000  little-endian
0x00009800  big-endian
```

**`CONFIRMED`**: `base_ambiguity_recorded = 1`. This stage does **not** resolve it, and therefore no
address-relative claim is possible. That is the same blocker Stage 423A recorded, and it is inherited
here rather than re-argued.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| the container carries transfer vocabulary | **REFUTED** (0) |
| the 16-bit occurrences of 1424 and 2500 are evidence | **REFUTED** (chance level, control identical) |
| a 32-bit word equal to 2500 exists | **CONFIRMED** (1 occurrence, offsets recorded) |
| that word is a completion-ring depth | **UNKNOWN** — no anchor, not promoted |
| the file is a two-segment QCA-ATH10K container | **CONFIRMED** |
| the segment base is unambiguous | **REFUTED** (`0x00980000` vs `0x00009800`) |
| the TX-completion fast path is located | **REFUTED** (`tx_compl_fastpath_recovered = 0`) |

## 5. The operational reading

Three things follow for anyone planning work on PB-090:

1. **do not** search the container for `htt` or `tx_compl`; the words are not there;
2. **do not** treat a 16-bit match on 1424 or 2500 as a finding, because the 1425 control matches just
   as well and the arithmetic says chance;
3. **do** treat the single 32-bit 2500 word as the only candidate lead, and require a disassembly to
   promote it.

The method is the deliverable here. A constant search without a negative control and a chance
expectation is a random number generator with extra steps.

## 6. Gaps

- **`UNKNOWN`** — whether the 32-bit 2500 word is a completion-ring depth or something unrelated.
- **`UNKNOWN`** — the segment load base, unresolved since Stage 423A.
- **`UNKNOWN`** — the Xtensa text entry point and the completion handler.
- **Blocked** — no anchor and no resolved base, so no patch point can be named.
- **Known limit** — absence of a name is not absence of the mechanism.
- **Not attempted** — disassembly of the text section, dynamic validation.
