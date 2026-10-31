<!-- doc-head: Stage 991A synthesises 989A and 990A into an eight-layer boundary table and states that the requested ath10k artefacts are not recoverable, with 205 umac proxy offsets and zero ath10k offsets. -->
# Stage 991A - the ath10k absence boundary and the umac proxy

## Verdict

The three artefacts this stage family requests - Copy Engine ring descriptors,
`ath10k_htt_tx_32`, and the HTT-to-WMI transmit credit flow - are **not
recoverable** from this corpus. Five of eight stack layers have no bytes at all.
The only named offsets available anywhere are umac.ko proxy offsets: 205 of them.
Zero offsets are attributed to ath10k.

The consequence is blunt and worth stating without hedging: further static work
on this corpus will not produce ath10k Copy Engine or HTT detail. It requires an
ath10k source tree or a kernel build containing `ath10k_core.ko` and
`ath10k_pci.ko`. No amount of additional symbol sweeping changes that.

## Why a synthesis stage exists

Stages 989A and 990A each answer one narrow question. Read alone, a reader can
still mistake a umac.ko offset for an ath10k offset, because both arrive as
plausible-looking hexadecimal numbers from the same receipt family. This stage
draws the line explicitly, so proxy provenance cannot be laundered into ath10k
provenance.

## The boundary table

Status vocabulary: `ABSENT` means no bytes exist; `MEASURED_PRESENT` means bytes
exist and were measured as a proxy; `MEASURED_ZERO` means bytes exist but carry
none of the requested vocabulary.

| # | Layer | Status | Offsets | Source |
| ---: | :--- | :--- | ---: | :--- |
| L1 | `ath10k_pci.ko` module, PCI/HIF and CE host interface | ABSENT | 0 | 989A |
| L2 | `ath10k_core.ko` module, HTT/WMI protocol layer | ABSENT | 0 | 989A + 990A |
| L3 | CE ring descriptor layout, `ath10k_pci_hif_tx_sg`, `ath10k_ce_*ring` | ABSENT | 0 | 989A |
| L4 | HTT 32-bit transmit descriptor path, `ath10k_htt_tx_32` | ABSENT | 0 | 990A |
| L5 | ath10k HTT-to-WMI transmit credit flow control | ABSENT | 0 | 990A |
| L6 | umac.ko Copy Engine ring control symbols | MEASURED_PRESENT | 38 | 989A |
| L7 | umac.ko HTT/WMI/HTC vocabulary and HTC credit accounting | MEASURED_PRESENT | 167 | 990A |
| L8 | QCA988x `firmware-2.bin` HTT vocabulary | MEASURED_ZERO | 0 | 990A |

Totals: 8 layers, 5 absent, 3 measured (2 present, 1 zero). The counts partition
exactly, which the receipt asserts as a consistency check rather than leaving to
the reader.

Layer-by-layer boundary notes, because the status alone understates the limit:

- **L1/L2** - no binary, therefore no function body, no register write sequence,
  no message id table. Nothing about ath10k's internals is knowable here.
- **L3** - the ring descriptor struct is unrecovered even on the proxy side. No
  DWARF, no BTF, no shipped header. Base address, entry count, write index and
  read index field offsets remain unknown.
- **L4/L5** - the 32-bit HTT transmit descriptor, its message ids and its credit
  units are all outside the boundary.
- **L6** - 38 CE symbol anchors, 34 `.text` functions and 4 `.bss` context
  objects. `WAR_CE_SRC_RING_WRITE_IDX_SET` at `0x0bcac0` (288 bytes) is the most
  on-subject artefact, and it is umac code, not ath10k code.
- **L7** - a real transmit path and a real credit mechanism, in a different code
  lineage. Probe-quality analogue, not an implementation counterpart.
- **L8** - three containers, 204796 bytes each, zero HTT vocabulary. The firmware
  route to the protocol is closed as well.

## The three requested artefacts

| Artefact | Status | Why | What the proxy offers instead |
| :--- | :--- | :--- | :--- |
| `ce_ring_descriptors` | NOT_RECOVERABLE | `ath10k_pci.ko` absent, no struct info | 38 CE symbol anchors in umac.ko |
| `ath10k_htt_tx_32` | NOT_RECOVERABLE | `ath10k_core.ko` absent, token occurs nowhere | `htt_tx_sched`, `htt_tx_send_std`, `htt_tx_desc_alloc/free`, `htt_tx_compl_desc_id` |
| `htt_to_wmi_credit_flow` | NOT_RECOVERABLE | ath10k protocol has no bytes, umac uses HTC | HTC credit symbols plus `TxCreditSize`, `TxCredits`, `TxCreditsPerMaxMsg` strings |

## Proxy provenance and the zero-offset guarantee

| Quantity | Value |
| :--- | ---: |
| CE symbol names from 989A | 38 |
| HTT/WMI/HTC symbol names from 990A | 167 |
| overlap between the two sets | 0 |
| `umac_proxy_symbols` (set union) | 205 |
| `exact_offsets_total` | 205 |
| `ath10k_offsets_claimed` | 0 |

The two sets are disjoint, so the union equals the sum and no symbol is double
counted. Offsets are section-relative `st_value` inside a MIPS32 big-endian
`ET_REL` object. They are anchors for further work, not virtual addresses, and
they cannot be promoted to runtime addresses without applying relocations against
a specific linked kernel image.

`offsets_from_ath10k` is 0 and `ath10k_offsets_claimed` is 0 because the modules
are absent. The two fields are computed independently from the two upstream
receipts and then summed, so a single upstream regression that started emitting
ath10k offsets would be caught by the consistency block rather than silently
inherited.

## Consistency checks

The stage refuses to emit a table it cannot stand behind. Six upstream facts and
two structural invariants are re-read from the receipts at build time:

| Check | Expected | Observed | Pass |
| :--- | ---: | ---: | :--- |
| 989A absence proven | 1 | 1 | yes |
| 989A ath10k offsets recovered | 0 | 0 | yes |
| 990A ath10k offsets recovered | 0 | 0 | yes |
| 990A `htt_tx_32` absent | 0 | 0 | yes |
| 990A `ath10k_core` absent | 0 | 0 | yes |
| firmware HTT hits | 0 | 0 | yes |
| layer count partitions | 8 | 8 | yes |
| ath10k offset claims zero | 0 | 0 | yes |

Result 8 of 8, so `boundary_documented = 1`. If either upstream receipt is
missing the script exits 2 rather than writing an empty table, because an empty
table is indistinguishable from a finding to a downstream reader.

## Claim ledger

| Id | Claim | Class |
| :--- | :--- | :--- |
| 991A-C1 | Five of eight layers have no bytes in the corpus | CONFIRMED |
| 991A-C2 | CE ring descriptors are not recoverable here | CONFIRMED |
| 991A-C3 | `ath10k_htt_tx_32` is not recoverable here | CONFIRMED |
| 991A-C4 | The ath10k HTT-to-WMI credit flow is not recoverable here | CONFIRMED |
| 991A-C5 | 205 named offsets exist, all traceable to umac.ko | CONFIRMED |
| 991A-C6 | Zero offsets are attributable to ath10k | CONFIRMED |
| 991A-C7 | The umac HTT/AE family is a usable structural analogue for study | INFERRED |
| 991A-C8 | The umac CE symbols imply a specific ring descriptor layout | UNKNOWN |
| 991A-C9 | airMAX polling depends on a host-side ath10k code path | REFUTED |
| 991A-C10 | Absence in this corpus implies absence upstream | UNKNOWN |

On 991A-C9: this stage produces no evidence for a host-side ath10k dependency,
and every byte-level artefact for the airMAX path in this corpus lives in the
vendor `umac.ko`/`ubnt_poll_host.ko` layer. Claiming an ath10k dependency would
invert the one thing the corpus does show.

## Attribution

| Layer | Attribution |
| :--- | :--- |
| L1 to L5 | absent, therefore UNKNOWN |
| L6 to L7 | proprietary airMAX/LTU module (`umac.ko`) |
| L8 | QCA firmware, no HTT vocabulary present |

## Reproduce

```
python tools/re/dissect_stage991a_ath10k_absence_and_umac_proxy_re.py
```

Run 989A and 990A first; this stage consumes their receipts and records each one
by path, byte count and sha256 in `analysis_dependencies`. Output
`artifacts/autoresearch/stage991a_ath10k_absence_and_umac_proxy_re.json`,
`evidence_provenance_class: CONFIRMED_STATIC_BINARY`, `radio_safety: static only`.
No wall-clock field is emitted, so consecutive runs are byte-identical.

## Gaps

1. `ath10k_pci.ko` and `ath10k_core.ko` are absent, so all five ath10k layers stay closed.
2. The umac proxy gives symbol anchors, not structure layouts; no descriptor field offset is claimed.
3. HTC credit accounting is a different protocol layer from ath10k HTT credits.
4. The QCA988x firmware containers carry no HTT vocabulary, so firmware bytes cannot close the gap.
5. Section-relative offsets need relocation before they become usable addresses.
6. This stage reads receipts only and cannot discover anything the upstream stages missed.
7. Absence in this 1169-module corpus does not establish absence from upstream Linux trees.
8. The `fal_edma_ring_*` symbol family in umac.ko remains unattributed and is not used in any claim.
