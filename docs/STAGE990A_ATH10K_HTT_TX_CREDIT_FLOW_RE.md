<!-- doc-head: Stage 990A refutes the ath10k_htt_tx_32 premise, then measures the umac.ko HTT transmit and HTC credit proxy with exact section-relative symbol offsets. -->
# Stage 990A - ath10k HTT transmit, credit flow, and the umac proxy

## Verdict in one line

`ath10k_htt_tx_32` is **REFUTED** as recoverable: `ath10k_core.ko` does not exist
here, the token `htt_tx_32` occurs in no module, and the ath10k HTT-to-WMI credit
flow therefore has no bytes. The only related binary is `umac.ko`, which carries
its own HTT transmit vocabulary and an HTC credit mechanism. 167 umac symbols are
reported with offsets; zero offsets are attributed to ath10k.

## Absence of the requested artefact

| Test | Result |
| :--- | :--- |
| `ath10k_core.ko` present | 0 |
| ath10k symbol hits across 1169 modules | 0 |
| `htt_tx_32` / `HTT_TX_32` / `ath10k_htt_tx_32` / `htt_tx_64` raw hits | 0 |
| `offset_from_ath10k` | 0 |

The absence is established the same way as stage 989A: filename, symbol, string
and raw byte passes over the whole corpus. The corpus is 1169 modules; stage 949A
measured 1163 with the same result, so the 6 new modules changed nothing.

## The proxy: umac.ko HTT transmit symbols

Canonical copy
`artifacts/firmware_re_xc_ltu/wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko`,
MIPS32 big-endian, `ET_REL`, 4749 symbols. All offsets are section-relative
`st_value` inside `.text`.

| Symbol | Offset | Size | What the name says |
| :--- | ---: | ---: | :--- |
| `htt_tx_compl_desc_id` | `0x0d7494` | 16 | transmit completion descriptor id |
| `htt_tx_attach` | `0x0d85c0` | 204 | transmit path attach |
| `htt_tx_detach` | `0x0d868c` | 36 | transmit path detach |
| `htt_tx_desc_alloc` | `0x0d86b0` | 84 | transmit descriptor allocation |
| `htt_tx_desc_free` | `0x0d8704` | 32 | transmit descriptor release |
| `htt_tx_desc_flag_postponed` | `0x0d8724` | 8 | postponed-frame flag |
| `htt_tx_desc_flag_batch_more` | `0x0d872c` | 8 | batch continuation flag |
| `htt_tx_sched` | `0x0d8734` | 572 | transmit scheduling |
| `htt_tx_send_std` | `0x0d8970` | 556 | standard transmit send |

Nine symbols, three of them substantial (`htt_tx_sched` 572 bytes,
`htt_tx_send_std` 556, `htt_tx_attach` 204). This is a real transmit path, just
not ath10k's.

The family split bounds the proxy: 9 `htt_tx*`, 57 `htt_rx*`, 68 `wmi*` and 7
`credit*` symbols, 167 proxy symbols in total.

These are overlapping subsets, not a partition: `htt_tx_compl_desc_id` matches
both `htt_tx` and `tx_compl`, and `wmi_htc_tx_complete` matches both `tx_compl`
and `wmi`, so the subsets do not sum to 167.

The asymmetry is the important reading: the receive side is six times larger than
the transmit side. A 9-symbol transmit family cannot describe ath10k's 32-bit HTT
transmit descriptor, its message ids or its credit units.

## Credit flow: what exists is HTC, not HTT

| Symbol | Offset | Size | Section |
| :--- | ---: | ---: | :--- |
| `GetHTCSendPacketsCreditBased` | `0x0c501c` | 280 | `.text` |
| `HTCProcessCreditRpt` | `0x0c62b4` | 396 | `.text` |
| `HTCSetCreditDistribution` | `0x0c7364` | 8 | `.text` |
| `HTCGetCreditAllocation` | `0x0c7714` | 44 | `.text` |
| `HTCDumpCreditStates` | `0x0c7a28` | 208 | `.text` |
| `htc_credit_flow` | `0x01be1c` | 4 | `.bss` |
| `ol_cfg_target_tx_credit` | `0x0d49d4` | 32 | `.text` |

Supporting strings, taken from printable runs only, with a leading word boundary
so that substrings such as `ACREDIT` inside other words are not miscounted:

```
%s: tx FAILED, target_tx_credit exhausted
%s: tx_credit initialised to %d
<1> TxCreditSize       : %d
<1> TxCredits          : %d
<1> TxCreditsPerMaxMsg : %d
%s: failed to alloc HTT tx desc (%d of %d)
%*sSW enqueue index = %d, SW dequeue index: desc = %d, buf = %d
```

That is a credit-based transmit path with configurable credit size, per-message
credit cost, a descriptor pool and software enqueue/dequeue indices. It is a
credible structural analogue of transmit back-pressure.

It is **not** the ath10k HTT-to-WMI credit flow, and the receipt records that
equivalence as REFUTED. HTC credit accounting runs over the host-target mailbox.
ath10k HTT credits are a different protocol layer with different wire messages.
The names rhyme; the implementations do not. Treating them as one mechanism would
fabricate an equivalence that no byte in this corpus supports.

## Token counts, and the 949A reconciliation

Counted inside printable runs of length >= 4, across the whole corpus:

| Token | Hits | Note |
| :--- | ---: | :--- |
| `htt_tx` | 72 | 9 per copy x 8 copies |
| `htt_tx_compl` | 8 | 1 per copy x 8 copies |
| combined | 80 | matches stage 949A's figure of 80 |
| `htt_rx` | 472 | receive family dominates |
| `credit` | 32 | credit accounting |
| `wmi` | 1381 | WMI command and event layer |
| `HTT_TX` / `HTT_T2H` / `HTT_H2T` | 0 | uppercase HTT spellings absent |

Both `umac_htt_tx_hits = 72` and `umac_htt_tx_compl_hits = 8` are emitted
separately, plus `umac_htt_tx_vocabulary_hits = 80` so the 949A number is
reproduced without arithmetic on the reader's side.

Eight modules carry `htt_tx` symbols: 6 `umac.ko` copies and 2 curated patch
copies. Nine `umac.ko` copies exist; the three XW/M5 copies (kernel 2.6.32.71,
915 KB and 885 KB) have no `htt_tx` vocabulary, which is consistent with the
XW/M5 platform having no QCA988x offload path.

A caution recorded in the receipt: the broad regex `htt|tx_compl|credit|flow|wmi`
matches 99 modules, but that is not evidence of 99 HTT implementations. `flow`
appears throughout ECM and netfilter modules and `wmi` inside unrelated
identifiers. Only `modules_with_htt_tx_symbols = 8` is comparable with 949A.

## Firmware containers carry no HTT vocabulary

| Container | Bytes | htt / HTT / htt_tx / credit / wmi / HTC / ath10k |
| :--- | ---: | --- |
| `artifacts/firmware_re_xc_ltu/openwrt_qca988x_hw20_firmware_2_ct.bin` | 204796 | all zero |
| `artifacts/verification/stage932a/192_168_100_241_firmware-2.bin` | 204796 | all zero |
| `artifacts/verification/stage932a/192_168_100_242_firmware-2.bin` | 204796 | all zero |

Ten further `.bin` files under `artifacts/` have `firmware` in the name and are
7 MB to 16 MB whole airOS images or mtd2 flash regions. They are excluded and
listed with that reason. Including them would count the HTT strings of the
embedded `umac.ko` as firmware vocabulary, the exact false positive to avoid.

## Claim ledger

| Id | Claim | Class |
| :--- | :--- | :--- |
| 990A-C1 | `ath10k_core.ko` absent, so `ath10k_htt_tx_32` and its credit ring are unavailable | CONFIRMED |
| 990A-C2 | Token `htt_tx_32` occurs in no module | CONFIRMED |
| 990A-C3 | `umac.ko` carries 9 `htt_tx*` symbols with exact offsets | CONFIRMED |
| 990A-C4 | umac HTT vocabulary is asymmetric: 9 transmit against 57 receive | CONFIRMED |
| 990A-C5 | umac implements credit flow control in the HTC layer | CONFIRMED |
| 990A-C6 | umac HTC credit is the same mechanism as ath10k HTT-to-WMI credit | REFUTED |
| 990A-C7 | HTC credit is a usable structural analogue for back-pressure semantics | INFERRED |
| 990A-C8 | QCA988x firmware containers carry zero HTT vocabulary | CONFIRMED |
| 990A-C9 | An ath10k offset can be derived from a umac symbol | REFUTED |

## Attribution

| Layer | Attribution |
| :--- | :--- |
| `htt_tx*` and `wmi*` symbols | proprietary airMAX/LTU module (`umac.ko`) |
| HTC credit symbols and credit strings | proprietary airMAX/LTU module |
| firmware containers | QCA firmware (no HTT vocabulary present) |
| ath10k HTT transmit path | absent, therefore UNKNOWN |

## Reproduce

```
python tools/re/dissect_stage990a_ath10k_htt_tx_credit_flow_re.py
```

Output `artifacts/autoresearch/stage990a_ath10k_htt_tx_credit_flow_re.json`,
`evidence_provenance_class: CONFIRMED_STATIC_BINARY`, `radio_safety: static only`.
No wall-clock field is emitted, so consecutive runs are byte-identical. Static
only: no module loaded, no radio contacted, no firmware written.

## Gaps

1. `ath10k_core.ko` is absent, so `ath10k_htt_tx_32` has no bytes and no offset.
2. umac offsets are section-relative `ET_REL` values and need relocation before use.
3. A 9-symbol transmit family cannot describe ath10k's 32-bit HTT descriptor.
4. HTC credit and ath10k HTT credit are different protocols; the proxy is functional.
5. Firmware carries no HTT strings, so credit ring sizes are not recoverable there.
6. `st_size` gives code extent, not struct field offsets; no function bodies were
   disassembled, so evidence is symbol names and strings only.
