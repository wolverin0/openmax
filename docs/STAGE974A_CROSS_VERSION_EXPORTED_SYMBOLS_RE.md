<!-- doc-head: STAGE974A_CROSS_VERSION_EXPORTED_SYMBOLS_RE.md cross-version exported-symbol RE over available airOS/XW/LTU module trees (static only) -->

# Stage 974A - Cross-Version Exported Symbols (Static Binary RE)

Offline ELF analysis of vendor kernel modules extracted from airOS, XW and LTU
firmware images. No device was contacted, no network was used and no firmware
was written. Classification: `CONFIRMED_STATIC_BINARY`.

- Tool: `tools/verify/verify_stage974a_cross_version_exported_symbols_re.py`
- Receipt: `artifacts/autoresearch/stage974a_cross_version_exported_symbols_re.json`
- Claim: `FMX-STAGE974A-CROSS-VERSION-EXPORTED-SYMBOLS`

## Version matrix

One row per build tree, and one row per named-but-absent version. Availability is
stated explicitly; an absent version cannot be compared at any level and is
reported as REFUTED rather than dropped from the matrix.

| Version | Build tree | Modules | Exported symbols | Availability |
| :--- | :--- | ---: | ---: | :--- |
| airOS 8.7.11 | `airos_8_7_11_xc` | 4 | 60 | AVAILABLE (partial: 4 modules) |
| airOS 8.7.25 | `airos_8_7_25_wa` | 144 | 479 | AVAILABLE |
| airOS 8.7.25 | `airos_8_7_25_xc` | 143 | 491 | AVAILABLE |
| airOS 8.7.4cs | `airos_8_7_4cs_xc` | 143 | 489 | AVAILABLE |
| airOS 8.7.4cs | `airos_8_7_4cs_wa` | 5 | 147 | AVAILABLE (partial: 5 modules) |
| XW 6.1.4 | `xw_6_1_4` | 95 | 3137 | AVAILABLE |
| XW 6.3.6 | `xw_6_3_6` | 95 | 3162 | AVAILABLE |
| LTU 2.4.2 | `ltu_2_4_2_afltu` | 154 | 803 | AVAILABLE |
| LTU 2.4.2 | `ltu_2_4_2_aflturocket` | 154 | 807 | AVAILABLE |
| airOS 8.7.21 | none | 0 | 0 | ABSENT |
| LTU 2.3.1 | none | 0 | 0 | ABSENT |

Absent versions: `LTU 2.3.1`, `airOS 8.7.21`.
These are `REFUTED` as available inputs: an absent version cannot be compared
against anything, and no symbol, ioctl or caldata statement is made about it.
Absence was measured by boundary-anchored token match over every file and
directory name under `artifacts/` and `firmware/`; zero version-bearing hits
were found for either token set.

## Totals

| Metric | Value |
| :--- | ---: |
| Versions available | 6 |
| Versions absent | 2 |
| Build trees scanned | 9 |
| Modules scanned | 937 |
| Symbols shared by all available versions | 0 |
| Symbols shared by all full (non-partial) versions | 105 |
| Union of exported symbols | 4021 |
| `eab_driver.ko` present | 0 |

The all-version intersection is 0 because `airOS 8.7.11` contributes only 4
modules, so it cannot share the full export list of a 144-module build. That zero
is a coverage artefact, not evidence of divergence; the companion metric over
full trees only is the meaningful cross-version core. It spans `LTU 2.4.2`, `XW 6.1.4`, `XW 6.3.6`, `airOS 8.7.25`, `airOS 8.7.4cs`.

## Exported symbols per version

| Version | Exported (GLOBAL union ksymtab) | Defined LOCAL names |
| :--- | ---: | ---: |
| LTU 2.4.2 | 807 | 11192 |
| XW 6.1.4 | 3137 | 890 |
| XW 6.3.6 | 3162 | 916 |
| airOS 8.7.11 | 60 | 702 |
| airOS 8.7.25 | 491 | 4023 |
| airOS 8.7.4cs | 489 | 4329 |

The `Defined LOCAL names` column matters: on the stripped builds the only
defined GLOBAL symbol is `__this_module`, so exported-set comparisons between a
stripped build and XW measure the vendor symbol-retention policy rather than code
divergence. The LOCAL column is the policy-insensitive surface.

That is measured, not inferred: every airOS module carries exactly one defined
GLOBAL symbol and it is `__this_module`; no airOS or XW module carries a
`__ksymtab_` symbol, while LTU carries 803-807 of them.

## Pairwise Jaccard - exported set

| Pair | Jaccard |
| :--- | ---: |
| LTU 2.4.2 vs XW 6.1.4 | 0.033814 |
| LTU 2.4.2 vs XW 6.3.6 | 0.033325 |
| LTU 2.4.2 vs airOS 8.7.11 | 0.000000 |
| LTU 2.4.2 vs airOS 8.7.25 | 0.102804 |
| LTU 2.4.2 vs airOS 8.7.4cs | 0.102979 |
| XW 6.1.4 vs XW 6.3.6 | 0.981441 |
| XW 6.1.4 vs airOS 8.7.11 | 0.011069 |
| XW 6.1.4 vs airOS 8.7.25 | 0.094419 |
| XW 6.1.4 vs airOS 8.7.4cs | 0.094476 |
| XW 6.3.6 vs airOS 8.7.11 | 0.010982 |
| XW 6.3.6 vs airOS 8.7.25 | 0.093713 |
| XW 6.3.6 vs airOS 8.7.4cs | 0.093769 |
| airOS 8.7.11 vs airOS 8.7.25 | 0.117647 |
| airOS 8.7.11 vs airOS 8.7.4cs | 0.118126 |
| airOS 8.7.25 vs airOS 8.7.4cs | 0.995927 |

## Pairwise Jaccard - defined LOCAL set (policy-insensitive lens)

| Pair | Jaccard |
| :--- | ---: |
| LTU 2.4.2 vs XW 6.1.4 | 0.000000 |
| LTU 2.4.2 vs XW 6.3.6 | 0.000000 |
| LTU 2.4.2 vs airOS 8.7.11 | 0.000168 |
| LTU 2.4.2 vs airOS 8.7.25 | 0.010829 |
| LTU 2.4.2 vs airOS 8.7.4cs | 0.034802 |
| XW 6.1.4 vs XW 6.3.6 | 0.927428 |
| XW 6.1.4 vs airOS 8.7.11 | 0.094158 |
| XW 6.1.4 vs airOS 8.7.25 | 0.043543 |
| XW 6.1.4 vs airOS 8.7.4cs | 0.040886 |
| XW 6.3.6 vs airOS 8.7.11 | 0.092505 |
| XW 6.3.6 vs airOS 8.7.25 | 0.043304 |
| XW 6.3.6 vs airOS 8.7.4cs | 0.040675 |
| airOS 8.7.11 vs airOS 8.7.25 | 0.172457 |
| airOS 8.7.11 vs airOS 8.7.4cs | 0.160286 |
| airOS 8.7.25 vs airOS 8.7.4cs | 0.902939 |

## Symbols unique to a version

| Version | Unique count | Sample |
| :--- | ---: | :--- |
| LTU 2.4.2 | 663 | `AME_EAB_DumpAirInternal`, `AME_LMAC_GetReg`, `AME_LMAC_SetReg`, `AME_Scheduler_DfsDummyTraffic`, `__cookie_v6_check`, `__cookie_v6_init_sequence` |
| XW 6.1.4 | 16 | `ath_hal_ether_sprintf`, `flock_set`, `ieee80211_find_tdlsnode`, `ubnt_poll_get_status`, `ubnt_poll_hash_create`, `ubnt_poll_hash_destroy` |
| XW 6.3.6 | 41 | `DFS_check_PRI_blakc_list`, `DFS_chirp_protect`, `DFS_pulse_cntr_FF`, `DUR_black_list`, `PRI_black_list`, `PRI_black_list_delta` |
| airOS 8.7.11 | 2 | `min_buf_resv`, `spectral_record_chan_info` |
| airOS 8.7.25 | 2 | `ubnt_radar_mode`, `ubnthal_get_eth_port_count` |
| airOS 8.7.4cs | 0 | none |

## Excluded duplicate tree

- `artifacts/autoresearch/waves_abcd_20261024/wave_a_wa/complete_rootfs_r2/staging_4c809c4d5fe845f193481bb6f8a78ea9/lib/modules/2.6.32.68` (144 modules) is byte-identical to `airos_8_7_25_wa` and is excluded from every count: re-extraction of firmware/WA.8.7.25.bin; despite the wave_a_wa directory name it is NOT an 8.7.4cs set.

Without this exclusion the matrix would have contained a phantom airOS 8.7.4cs
WA build that is in fact a second extraction of the 8.7.25 WA module set.

## Method

Per module: parse `.symtab`, keep DEFINED symbols (`st_shndx` is not `SHN_UNDEF`),
split GLOBAL / WEAK / LOCAL, drop `__this_module` and section symbols, then union
the `__ksymtab*` string names, with kernel 3.14 `__ksymtab_<name>` symbols
de-prefixed to the real export name. Per version: union its build trees. Across
versions: pairwise Jaccard plus the intersection over all available versions.
## Findings

1. Six of the eight named versions are available. `airOS 8.7.21` and `LTU 2.3.1`
   have zero files in the corpus and are REFUTED as inputs.
2. The directive's premise that `airOS 8.7.11` contributes no `.ko` files is
   itself REFUTED: 4 modules survive in `2xc_8711_modules/`. What is true is that
   no full 8.7.11 rootfs exists, so its 8.7.11 restriction is module-scoped.
3. `eab_driver.ko` is absent from the entire corpus (0 files). Every LTU
   `eab_driver` claim in earlier stages is documentary, not binary.
4. The airOS 8.7.25 and 8.7.4cs trees carry 143-144 modules and expose exports
   almost exclusively through `__ksymtab_strings`, since only `__this_module` is a
   defined GLOBAL symbol. A `.symtab`-only study would wrongly conclude that
   these builds export nothing.
5. LTU 2.4.2 is the only ARM LE surface and the only build that carries
   `__ksymtab_<name>` synthetic symbols, so its export list is recoverable from
   either lens.

## Gaps

- airOS 8.7.21 is absent from the corpus (0 files). It cannot be compared at symbol, ioctl or partition level; the version is REFUTED as an available input.
- LTU 2.3.1 is absent from the corpus (0 files). Same refutation: no comparison of any kind is possible.
- airOS 8.7.11 exists only as a flash-backup partition set plus 4 rescued modules, so only those 4 modules are symbol-comparable; the other ~140 modules of an 8.7.11 rootfs are not on disk.
- airOS 8.7.4cs WA exists only as a 5-module subset from a retained squashfs; there is no WA 8.7.4cs .bin in the corpus.
- eab_driver.ko is absent from the corpus (0 files), so no LTU eab_driver symbol surface can be compared across versions.
- Exported-set Jaccard is confounded by vendor symbol-retention policy: stripped builds keep only __this_module as a defined GLOBAL symbol. The defined-LOCAL matrix is the policy-insensitive lens.
- Symbol presence is static linkage evidence only. It does not establish that a symbol is reachable, correctly sized, or behaviourally identical on hardware.

## Reproduce

```
python tools/verify/verify_stage974a_cross_version_exported_symbols_re.py
```

