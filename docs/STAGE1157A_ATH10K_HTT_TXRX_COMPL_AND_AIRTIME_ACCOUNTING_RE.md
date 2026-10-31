<!-- doc-head: Stage 1157A offline RE of ath10k_core.ko HTT tx/rx completion and airtime call sites; static only -->
# Stage 1157A — ath10k HTT completion and airtime accounting (static)

## 1. Scope and inputs

Offline dissection of one ET_REL MIPS32 big-endian kernel module. No radio was
contacted, no firmware was written, no live address was used.

| item | value |
| :--- | :--- |
| binary | `artifacts/firmware_re_ath10k_tar/ath10k_core.ko` |
| bytes | `600808` |
| sha256 | `d7f2d1ac07a6c91f...` (prefix asserted by the tool) |
| provenance | `tar_member:artifacts/verification/stage117a_build/stock.tar:./lib/modules/6.6.110/ath10k_core.ko` |
| identity | Candela ath10k-ct-smallbuffers, source `ath10k-6.10`, package `ath10k-ct-2024.07.30~ac71b14d`, target `ath79/generic` |
| ELF | `ET_REL`, `EM_MIPS`, ELF32, big endian |
| tools | `tools/re/ath10k_htt_txrx_airtime_re_analyzer.py`, python stdlib only |
| receipt | `artifacts/verification/stage1157a_ath10k_htt_txrx_airtime_re.json` |

## 2. Method, and why it is not pattern matching

This object carries 281 `FUNC` symbols whose names are synthetic (`_0`, `_169`,
...), covering 100572 of 350960 `.text` bytes, so name lookup alone cannot answer
the question. Three mechanical rules were used instead.

1. **Export anchoring via `__ksymtab`.** The table encoding was detected, not
   assumed. The tool decodes both candidate forms — prelinked relative (`PREL32`)
   and absolute (`R_MIPS_32` relocation plus in-place addend) — scores each by how
   often the value field lands exactly on a `.text` `FUNC` symbol start, and uses
   the better one. Result: `absolute`, 56 of 61 entries land on a symbol start,
   0 for `PREL32`.
2. **Call sites via `R_MIPS_26` relocations.** For an imported symbol the
   relocation offset IS the address of the `jal`. Each site was additionally
   verified to hold a `jal` instruction (`0x0c000000`) with a zero 26-bit addend,
   so a relocation cannot be mistaken for a data reference.
3. **Static-function recovery via the call graph.** A callee of an exported
   function is itself an entry; its identity was constrained by the upstream
   contract rather than by a name.

## 3. Findings

### 3.1 `ath10k_htt_txrx_compl_task` (CONFIRMED)

Exported at `.text+0x2ac04`, `st_size = 5672`. The export value lands exactly on a
`FUNC` symbol start, which 56 of 61 exports in this object do.

Its `st_size` is reported as the symbol table states it and is **not** used to
bound any inner analysis: this build has 65 non-contiguous symbol pairs and its
281 `FUNC` symbols cover only 100572 of 350960 `.text` bytes, so unnamed statics
can hide inside a named span. That is a documented limit, not a licence to assume.

Callees recovered from `R_MIPS_26` inside the span include `_169`, `_168`
(`ath10k_mac_tx_push_pending`), `_217`, `__ieee80211_schedule_txq`,
`dev_kfree_skb_any_reason` and `__local_bh_enable_ip`, which is consistent with a
completion task that also drives the TX push path.

### 3.2 `ath10k_mac_tx_push_txq` (INFERRED identity, CONFIRMED offset)

No symbol or string in this build spells this name. It was recovered in three
steps, all of which the tool enforces:

| step | evidence | grade |
| :--- | :--- | :--- |
| `ath10k_mac_tx_push_pending` entry | `__ksymtab` export, `.text+0xf8d4`, `st_size 324` | CONFIRMED |
| its per-txq callee | `jal` at `.text+0xf9a8` inside the `ieee80211_next_txq` loop, return value tested with `bgez` | CONFIRMED |
| that callee dequeues | `.text+0xf594` is the only callee containing `jal ieee80211_tx_dequeue` (at `.text+0xf64c`) | CONFIRMED |
| the callee is `ath10k_mac_tx_push_txq` | matches the upstream contract; nothing in the image names it | INFERRED |

Boundary self-check: `0xf594 + 832 = 0xf8d4`, exactly the start of
`ath10k_mac_tx_push_pending`, so the size is contiguous at that seam.

`register_airtime` is **not** called from this function: the only two call sites
are elsewhere (section 3.3). Airtime for TX is therefore reported on the
completion paths, not on the push path.

### 3.3 `ieee80211_sta_register_airtime` call sites (CONFIRMED)

Exactly two, both `R_MIPS_26` against the undefined symbol, both verified `jal`
with zero addend:

| site | container | Δ into container | context |
| :--- | :--- | :--- | :--- |
| `.text+0x26978` | `_131` = `ath10k_htt_t2h_msg_handler` (`0x25bc8`, 5432) | +0xdb0 | T2H message parse: the airtime word is read from the payload as a byte-swapped 32-bit field (`lwl`/`lwr`/`wsbh`), the TID is extracted with `ext $a1, $s2, 8, 4`, then the call |
| `.text+0x3042c` | `_217` (`0x2fec4`, 2060, unnamed) | +0x568 | TX completion: `lbu $a1, 8($s3)` supplies the TID and `move $a3, $zero` forces the fourth argument to 0 |

`.text+0x3042c` sits in a function that also calls `ieee80211_tx_status_ext`
(`.text+0x30124`), which is the TX-completion shape.

## 4. Claims

| id | grade | claim |
| :--- | :--- | :--- |
| C1 | CONFIRMED | `ath10k_htt_txrx_compl_task` is exported at `.text+0x2ac04`, `st_size` 5672 |
| C2 | CONFIRMED | `ieee80211_sta_register_airtime` has exactly 2 call sites: `.text+0x26978`, `.text+0x3042c` |
| C3 | CONFIRMED | `ieee80211_tx_dequeue` is called from `.text+0xf64c` |
| C4 | INFERRED | the unnamed function at `.text+0xf594` is `ath10k_mac_tx_push_txq` |
| C5 | CONFIRMED | `__ksymtab` encoding is `absolute` (56 symbol-start hits, `PREL32` 0) |
| C6 | UNKNOWN | whether the reported airtime unit is microseconds or back-to-back slots |

`offsets_recovered = 289`: distinct offsets in the receipt that are backed by an
export, a `FUNC` symbol start, or a relocation site.

## 5. Gaps and what this stage does not claim

- The `st_size` of `ath10k_htt_txrx_compl_task` is a symbol-table figure that
  covers more code than the upstream body; unnamed statics may sit inside it.
  No inner bound of that span is asserted anywhere in the receipt.
- The identity of `.text+0xf594` as `ath10k_mac_tx_push_txq` is inferred from the
  call graph and the upstream contract, never from a name.
- The direction of each airtime report (tx only versus tx plus rx) is inferred
  from register use. `.text+0x3042c` has a literal-zero fourth argument, which is
  consistent with a tx-only report, but there is no type information to prove it.
- The airtime unit is unrecoverable from the call site: the value is copied
  through unchanged from the message payload.
- No ring watermark, ring depth limit or airtime quantum constant is claimed.
  Stage 1103A already reported the watermark question as absent.
- Static only: nothing here shows that either call site executes on the target
  hardware, and no measured airtime value is available offline.

## 6. Reproduce

```text
python tools/re/ath10k_htt_txrx_airtime_re_analyzer.py
python tools/re/ath10k_htt_txrx_airtime_re_analyzer.py --check
```

`--check` regenerates the receipt in memory and compares it byte for byte with the
file on disk. Two consecutive runs produced identical sha256
`c1bd67261f1cb239e0a625fdc6d8e8e336758f37f59826ea100dd08aa43f2901` (67179 bytes)
and the same payload from a different working directory.
