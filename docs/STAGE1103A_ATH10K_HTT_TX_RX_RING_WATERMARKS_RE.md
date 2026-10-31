<!-- doc-head: Stage 1103A static dissection of ath10k_core.ko + ath10k_pci.ko from stage117a stock.tar - HTT/CE/HTC symbol surface, the refuted watermark premise, and the skb_orphan absence -->
# Stage 1103A - ath10k_core.ko HTT/TX/RX ring and watermark dissection

100% offline, static only. No module loaded, no radio contacted, no firmware written, no live address used.
Script: `tools/re/dissect_stage1103a_ath10k_htt_tx_rx_ring_watermarks_re.py`.
Receipt: `artifacts/autoresearch/stage1103a_ath10k_htt_tx_rx_ring_watermarks_re.json`.

## 1. Why this stage exists

For nineteen earlier stages, ath10k was reported **absent**. Those sweeps looked only at loose `.ko`
files on disk. The modules were inside an archive the whole time. Stage 1103A scans archive members as
well, and closes the scope error.

`stage990a_ath10k_htt_tx_credit_flow_re.json` recorded `summary.ath10k_core_present = 0` and the gap text
"ath10k_core.ko does not exist in the corpus". That is now contradicted by two independent checks: the
file is 600808 bytes on disk and its sha256 equals the `EXTRACTION.json` member digest.

## 2. Provenance

| Item | Value |
| :--- | :--- |
| core path | `artifacts/firmware_re_ath10k_tar/ath10k_core.ko` |
| core bytes | 600808 |
| core sha256 | `d7f2d1ac07a6c91fe4284eac37bbe92e822b276a59928946ff86cb9da00ddf84` |
| pci path | `artifacts/firmware_re_ath10k_tar/ath10k_pci.ko` |
| pci bytes | 56648 |
| pci sha256 | `11bc8d7a4ee1f98c8d72b68f5bb43150bd36186ceed78e5f4400fb3cab26cd66` |
| core provenance | `tar_member:artifacts/verification/stage117a_build/stock.tar:./lib/modules/6.6.110/ath10k_core.ko` |
| pci provenance | `tar_member:artifacts/verification/stage117a_build/stock.tar:./lib/modules/6.6.110/ath10k_pci.ko` |

Both are MIPS32 big-endian `ET_REL`. The canary tree
`artifacts/canary_panel1_guarida/panel1_native_cutover_20261019/after/` still holds only `mac80211.ko`
and never held ath10k; nothing in this stage is sourced from it.

## 3. Build identity - CONFIRMED

Recovered from embedded `__FILE__` markers, not from a manifest:

    target-mips_24kc_musl/linux-ath79_generic/ath10k-ct-smallbuffers/
    ath10k-ct-2024.07.30~ac71b14d/ath10k-6.10/<unit>

This is Candela `ath10k-ct` in its **smallbuffers** flavour, driver source `ath10k-6.10`, built for the
`ath79/generic` recipe under musl. The consequence matters: ring depth here is a property of the
reduced-buffer build profile, chosen when the image was built.

Source units cited by the binary: `bmi.c`, `ce.c`, `core.c`, `coredump.c`, `debug.c`, `htc.c`, `htt.c`,
`htt_rx.c`, `htt_tx.c`, `mac.c`, `txrx.c`, `wmi.c`, `wmi-tlv.c`, plus `wmi-ops.h`.

## 4. Symbol reality check - CONFIRMED

| Metric | core | pci |
| :--- | ---: | ---: |
| `.symtab` entries | 1965 | 332 |
| `STT_FUNC` in `.text` | 281 | 33 |
| size sum of those | 100572 | - |
| `.text` bytes | 350960 | - |
| readable `__ksymtab` exports | 56 | 0 |

Only about 29 percent of `.text` carries a measured `st_size`. Most bodies are unnamed. Records whose
size is a bracket rather than a measurement are marked `size_basis: next_entry_upper_bound`; five
`__ksymtab` exports could not be attributed to a `.text` symbol confidently and are listed in
`meta.ambiguous_exports_skipped` instead of being guessed.

Entry points come from three provable sources: `STT_FUNC` symbols, `__ksymtab` exports, and `R_MIPS_26`
jump targets. In an `ET_REL` object `.text` and `.text.unlikely` are both section-relative from zero, so
mixing them would fabricate address collisions. Analysis is therefore restricted to `.text`, and that
restriction is recorded as a gap.

## 5. The watermark premise is REFUTED

The stage was commissioned to find HTT TX/RX ring high and low watermarks. They are not there.

Nineteen tokens - `watermark`, `water_mark`, `high_wm`, `low_wm`, `hi_water`, `lo_water`, `highmark`,
`lowmark`, `hi_mark`, `lo_mark`, `hwm`, `lwm`, `_hwm`, `_lwm`, `threshold`, `max_num_pending`,
`num_pending_tx`, `pending_tx`, `fill_cnt` - were scanned across `.rodata.str1.4`, `.rodata`, `.modinfo`,
`__param`, `__ksymtab_strings`, `.data`, `.bss` and the entire raw byte stream.

Three token families produced hits, and every one is a false positive:

* `hwm` and `_hwm` match only inside `ath10k_hwmon`, the hardware-monitor driver name, and inside
  `depends=...,hwmon,...` in `.modinfo`.
* `threshold` matches RTS threshold, PS wake threshold, sta kickout threshold and rc-max-per-threshold.
  All four are unrelated to ring occupancy.

`watermark_symbols` is therefore empty and no watermark offset is claimed. Claim C-1103A-03 carries grade
`REFUTED`.

## 6. skb_orphan is absent - REFUTED

Scanned three independent ways:

1. symbol table - zero names containing `orphan`;
2. reloc-reachable `.rodata.str1.4` strings - zero;
3. raw byte stream for `orphan`, `skb_orphan`, `__skb_orphan`, `skb_orphan_frags` - zero.

`summary.skb_orphan_present` is `0`. The honest limit: a call that exists in ath10k-ct source but which
the compiler eliminated cannot be distinguished from a call that was never written. That residue is
recorded as `UNKNOWN` in the gaps.

## 7. What the HTT and CE surfaces actually contain - CONFIRMED

26 HTT-anchored offsets, each pinned to an export, a `__FILE__` marker or a diagnostic string:

| Offset | Role | Anchor |
| :--- | :--- | :--- |
| `0x2426c` | htt.c body | `__FILE__` `ath10k-6.10/htt.c` |
| `0x245a4`, `0x27f8c`, `0x28c10` | htt_rx.c bodies | `__FILE__` `ath10k-6.10/htt_rx.c` |
| `0x2d0b4`, `0x2d154`, `0x2ec28`, `0x2f824` | htt_tx.c bodies | `__FILE__` `ath10k-6.10/htt_tx.c` |
| `0x24598` | `ath10k_htt_rx_pktlog_completion_handler` | `__ksymtab` |
| `0x25bc8` | `ath10k_htt_t2h_msg_handler` | `__ksymtab` |
| `0x27a1c` | `ath10k_htt_rx_hl_indication` | `__ksymtab` |
| `0x2ac04` | `ath10k_htt_txrx_compl_task` | `__ksymtab` |
| `0x2c790` | `ath10k_htt_hif_tx_complete` | `__ksymtab` |

26 CE offsets, all named and all with measured `st_size`, spanning `ath10k_ce_send_nolock` at `0x52e00`
through `ath10k_ce_init_pipe` at `0x55440`. Four TX-completion anchors are reported, including
`ath10k_htc_notify_tx_completion` at `0x22b24` and `ath10k_htc_tx_completion_handler` at `0x22c34`.

The nearest thing to a watermark is a byte-count guard: the format string
`%s: send more we can (nbytes: %d, max: %d)` is relocated from `.text+0x53ff0` and `.text+0x54258`, inside
the entry-point bracket `[0x53d90, 0x542b0)`. That interval may hold more than one function, so no exact
size is claimed for it. It is offered as a substitute, not as the watermark the stage set out to find.

## 8. Grades

| Claim | Grade |
| :--- | :--- |
| C-1103A-01 core present, size and digest match the manifest | CONFIRMED |
| C-1103A-02 ath10k-ct-smallbuffers, ath10k-6.10, ath10k-ct-2024.07.30~ac71b14d | CONFIRMED |
| C-1103A-03 HTT ring watermarks exist | REFUTED |
| C-1103A-04 skb_orphan is referenced | REFUTED |
| C-1103A-05 CE `nbytes` guard string | CONFIRMED |
| C-1103A-06 exported CE and HTT surface sizes | CONFIRMED |
| C-1103A-07 earlier stages recorded ath10k as absent | CONFIRMED |
| C-1103A-08 ring depth is build-time, not a module parameter | INFERRED |

## 9. Unresolved

CE ring descriptor field offsets were **not** recovered. `ath10k_ce_alloc_pipe` is located, but its
struct layout is not asserted. `ath10k_pci.ko` has no `__ksymtab` at all and all 33 of its `.text`
functions carry generated `_NNN` names, so no pci-side function is reported by name. The seven-item
`gaps` array in the receipt carries the full list.

## 10. Reproduce

    python tools/re/dissect_stage1103a_ath10k_htt_tx_rx_ring_watermarks_re.py

Two consecutive runs produce byte-identical output; the script also re-renders its own payload and
refuses to write if the two renders differ. Deterministic because no timestamp, host path or iteration
order reaches the JSON: keys are sorted, and sibling keys are normalised through `decase(node)` so no two
keys can collide case-insensitively.
