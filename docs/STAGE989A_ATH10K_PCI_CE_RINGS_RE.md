<!-- doc-head: Stage 989A proves the ath10k_pci absence in a 1169-module corpus by three independent methods and censuses the Copy Engine vocabulary that does exist, inside umac.ko. -->
# Stage 989A - ath10k_pci, Copy Engine rings, and the absence boundary

## Verdict in one line

The stage premise is **REFUTED**: `ath10k_pci.ko` does not exist in this corpus, so
`ath10k_pci_hif_tx_sg` and the Copy Engine ring descriptor layout cannot be
disassembled here. The Copy Engine code that *does* exist lives in `umac.ko`, the
airOS vendor driver, and is reported below as a proxy with explicit attribution.

## What the stage asked for, and what exists

| Requested artefact | Belongs to | Present in corpus | Status |
| :--- | :--- | :--- | :--- |
| `ath10k_pci.ko` | mainline ath10k PCI/HIF | no | REFUTED |
| `ath10k_core.ko` | mainline ath10k protocol | no | REFUTED |
| `ath10k_pci_hif_tx_sg` | ath10k_pci | no | REFUTED |
| Copy Engine ring descriptors | ath10k_pci + ath10k_ce | no | REFUTED |
| `CE_*` ring control symbols | `umac.ko` vendor driver | yes, 38 names | CONFIRMED (proxy) |

## Three independent absence methods

Every method shares one denominator: all 1169 `.ko` files under `artifacts/` and
`firmware/`. The repo-wide walk finds the same 1169, so the denominator is the
whole corpus and not a subset.

| Method | Rule | Hits |
| :--- | :--- | :--- |
| M1 filename glob | basename lowercased starts with `ath10k` | 0 |
| M2 symbol and string sweep | every ELF symtab name plus every printable run >= 4 chars, case-insensitive `ath10k` | 0 |
| M3 raw byte scan | `bytes.count()` for `ath10k_pci`, `ath10k_core`, `ath10k_pci_hif_tx_sg`, `ath10k`, `ATH10K` | 0 |

All three agree on zero, which is why the absence is reported as CONFIRMED rather
than as a single-tool negative result. Zero modules failed to parse, so there is
no "could not read it" hole in the sweep. Object shapes: 841 MIPS32 big-endian
`ET_REL` and 328 x86 `ET_REL`.

This is the seventeenth consecutive confirmation. Stage 949A measured 1163 modules
with 0 ath10k; the corpus has since grown by 6 modules and the count is still 0.

## Offset discipline

No offset is emitted for any ath10k symbol in this stage. The receipt carries an
`offset_guard` block recording `offsets_emitted_for_ath10k_symbols = 0` with the
reason stated. An invented offset would be the worst possible output of a stage
whose whole subject is missing, so the script has no code path that can produce
one.

## What the corpus does contain: Copy Engine code in umac.ko

`umac.ko` (canonical copy
`artifacts/firmware_re_xc_ltu/wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko`,
MIPS32 big-endian, `ET_REL`, 4749 symbols) carries a full QCA/ol_ath Copy Engine
layer. Offsets are section-relative `st_value`, which is the only meaningful
address in an unlinked object.

| Symbol | Offset | Size | Section |
| :--- | ---: | ---: | :--- |
| `WAR_CE_SRC_RING_WRITE_IDX_SET` | `0x0bcac0` | 288 | `.text` |
| `CE_send_nolock` | `0x0c7be8` | 264 | `.text` |
| `CE_send` | `0x0c7cf0` | 172 | `.text` |
| `CE_sendlist_send` | `0x0c7dd4` | 368 | `.text` |
| `CE_send_entries_avail` | `0x0c8184` | 32 | `.text` |
| `CE_send_entries_done` | `0x0c8210` | 12 | `.text` |
| `CE_recv_entries_done` | `0x0c8268` | 12 | `.text` |
| `CE_completed_send_next_nolock` | `0x0c84ec` | 284 | `.text` |
| `CE_per_engine_service_any` | `0x0c8bd0` | 148 | `.text` |
| `CE_init` | `0x0c8dfc` | 1396 | `.text` |
| `HIF_PCI_CE_send_done` | `0x0c9fe4` | 336 | `.text` |
| `HIF_PCI_CE_recv_data` | `0x0ca134` | 364 | `.text` |

38 CE-token symbol names exist across 8 module copies (6 `umac.ko` plus 2 curated
patch copies). 34 are `.text` functions and 4 are `.bss` context objects such as
`ce_debug_rvkrn_context` at `0x01bdf4`, size 4.

`WAR_CE_SRC_RING_WRITE_IDX_SET` is the most on-subject artefact in the corpus: a
288-byte function that applies a hardware workaround to the Copy Engine *source
ring write index*. It is a named anchor for the ring-index problem the stage
asked about, but it is umac code, not ath10k code.

## Token census and its honesty limits

A two-letter token cannot be counted as a raw substring. `ce` occurs 12,770 times
in these files, almost all of it inside "device", "source", "once" and similar
English. The receipt therefore reports every token four ways and flags
`substring_reliable = false` for tokens shorter than three characters.

| Token | raw bytes | string runs | symbol exact | symbol ci | reliable |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `CE` | 1004 | 952 | 272 | 304 | no |
| `ce` | 12770 | 12733 | 32 | 304 | no |
| `ring` | 1598 | 1598 | 102 | 114 | yes |
| `desc` | 1808 | 1808 | 340 | 442 | yes |
| `qbd` | 0 | 0 | 0 | 68 | yes |
| `doorbell` | 0 | 0 | 0 | 0 | yes |
| `pcie` | 46 | 46 | 41 | 41 | yes |

Reading the table correctly matters more than the numbers:

- `CE` symbol-exact 272 is 34 uppercase `CE_*` names across 8 copies. `ce`
  symbol-exact 32 is the 4 lowercase `ce_debug_*` names across 8 copies. They are
  different tokens and are not double counted.
- `qbd` is zero as an exact lowercase token and 68 case-insensitively. The `QBD`
  spelling appears only in the LTU `ame_core.ko` symbols (`AME_CPYENG_*`,
  `AME_EAB_*`, `AME_HFE_*`). QBD there is the ame copy-engine descriptor, not the
  QCA988x host CE.
- `doorbell` is zero everywhere. No doorbell vocabulary exists in the corpus.
- `pcie` is dominated by `ath_pcie_pwrsave_enable` (ath9k power save) and by Intel
  `e1000e`/`igb`/`ixgbe` helpers in the LTU 4.14 rootfs. Neither is a CE ring.
- `ring` is a corpus-wide census, not an attribution: `ar9300_*_tx_status_ring`,
  `fal_*_ring_*`, `htt_*_ring_*`, `e1000_clean_rx_ring` and `igb_*` all match. 60
  symbols carry ring/qbd/doorbell tokens. One family, `fal_edma_ring_queue_map_*`,
  is left UNKNOWN because its origin cannot be established from symbols alone.

The `string`/`ring` trap is real: a naive substring rule counts 276 "ring symbols",
of which the majority are `ame_string_concat`, `proc_dostring` and friends. The
identifier-boundary split used here removes them.

## What is still not recovered

The ring descriptor *structure* is not recovered, and the receipt says so with
`ce_ring_descriptors_recovered = 0`. Symbol names and `st_size` describe code
extent. They do not describe field layout. There is no DWARF, no BTF and no
shipped struct definition in these modules, so base address, entry count, write
index and read index offsets remain unrecovered. A related debug string,
`SW enqueue index = %d, SW dequeue index: desc = %d, buf = %d`, proves such a
descriptor exists but does not give its field offsets. It is recorded as INFERRED
evidence of ring bookkeeping, nothing stronger.

## Claim ledger

| Id | Claim | Class |
| :--- | :--- | :--- |
| 989A-C1 | No `ath10k*` filename under artifacts/ or firmware/ | CONFIRMED |
| 989A-C2 | No ath10k symbol or string in any of the 1169 modules | CONFIRMED |
| 989A-C3 | No raw ath10k byte sequence in any module | CONFIRMED |
| 989A-C4 | Therefore no ath10k CE ring code or offset is recoverable here | CONFIRMED |
| 989A-C5 | The stage premise (disassemble ath10k_pci CE rings) holds | REFUTED |
| 989A-C6 | CE vocabulary exists inside umac.ko, not inside ath10k | CONFIRMED |
| 989A-C7 | umac CE symbols carry section-relative offsets and sizes | CONFIRMED |
| 989A-C8 | CE ring descriptor field layout is recoverable from symbols | INFERRED, not supported |
| 989A-C9 | Absence here implies absence upstream | UNKNOWN |
| 989A-C10 | Two-letter `ce` is measurable as a raw substring | REFUTED |

## Attribution

| Layer | Attribution |
| :--- | :--- |
| Copy Engine symbols | proprietary airMAX/LTU module (`umac.ko`) |
| HTT ring config messages in `umac.ko` | proprietary airMAX/LTU module |
| QBD symbols | proprietary LTU module (`ame_core.ko`) |
| ath10k artefacts | absent, therefore UNKNOWN |
| `fal_edma_ring_*` family | UNKNOWN |

## Reproduce

```
python tools/re/dissect_stage989a_ath10k_pci_ce_rings_re.py
```

Output `artifacts/autoresearch/stage989a_ath10k_pci_ce_rings_re.json`,
`evidence_provenance_class: CONFIRMED_STATIC_BINARY`, `radio_safety: static only`.
No wall-clock field is emitted, so consecutive runs are byte-identical. Scope is
static: no module is loaded, no radio is contacted, no firmware is written.

## Gaps

1. No `ath10k_pci.ko` or `ath10k_core.ko`, so CE ring descriptors cannot be read here.
2. `umac.ko` CE struct offsets are not derivable from symbol names alone.
3. Ring entry counts and per-engine register bases are runtime values, not constants.
4. `ring_symbols` mixes ame, fal, ath9k and Intel NIC code; it is a census only.
5. The corpus is 1169 files from partial rootfs extractions, not a kernel tree.
6. MIPS32 `ET_REL` `st_value` is section-relative and is not a virtual address.
