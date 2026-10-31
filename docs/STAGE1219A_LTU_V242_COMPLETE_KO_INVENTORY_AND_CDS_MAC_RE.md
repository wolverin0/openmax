<!-- doc-head: Stage 1219A - LTU 2.4.2 complete .ko inventory, eab_driver.ko absence answer and cds_mac/ame dependency-based role RE, static ARM ELF only -->
# Stage 1219A - LTU 2.4.2 Complete `.ko` Inventory and `cds_mac` / `ame` Roles

Static analysis of the whole LTU 2.4.2 module corpus. No radio was contacted, no live IP was touched,
no firmware was written, no module was loaded.

| Item | Value |
| :--- | :--- |
| Tool | `tools/re/ltu_v242_complete_ko_inventory_and_cds_mac_re_analyzer.py` |
| Receipt | `artifacts/verification/stage1219a_ltu_v242_ko_inventory_re.json` (181,630 B) |
| Provenance | `CONFIRMED_STATIC_BINARY` |
| Determinism | two consecutive runs byte-identical (`7D3F62E5...`, and `FEF9...` for 1218A) |
| Scope | `static` - census, ELF parse, .modinfo parse, receipt audit |
| Directory | `.../afltu_2.4.2/rootfs_extracted/lib/modules/3.14.65` |

## 1. Inventory of what is actually there

154 `.ko` files, every one `EM_ARM` little-endian ELF32, kernel `3.14.65 SMP preempt ARMv7 p2v8`.
The count is a directory measurement, not a list copied from a directive, and the tool fails closed if
the directory yields anything other than 154.

| Aggregate | Value |
| :--- | ---: |
| Modules enumerated | 154 |
| Parse errors | 0 |
| Defined symbols (sum) | 24,187 |
| Exported symbols (sum over `__ksymtab`) | 803 |
| Modules exporting nothing | 119 |
| Modules with zero defined symbols | 0 |
| `inventory_digest` | `8dbb1c9f926492020dd3566590d9348ca3220448b71bb81b7f7eb6f0d70db132` |

`inventory_digest` is SHA-256 over the sorted `module<TAB>bytes<TAB>sha256` lines, so any change to a
single byte of any module changes the digest.

Ten largest modules, with export counts (exports resolved by following every `.rel__ksymtab` entry to
its defined symbol, not by counting `__ksymtab` bytes):

| Module | Bytes | Exports |
| :--- | ---: | ---: |
| `ame_core.ko` | 3,282,052 | 31 |
| `qca-ssdk.ko` | 1,607,052 | 324 |
| `ame_radio_mod.ko` | 578,424 | 4 |
| `ipv6.ko` | 388,512 | 63 |
| `ame_dev.ko` | 298,760 | 27 |
| `ubnthal.ko` | 152,640 | 17 |
| `ame_dfs.ko` | 141,472 | 9 |
| `cds_mac_mod.ko` | 139,672 | 0 |
| `nf_conntrack.ko` | 84,992 | 96 |
| `ubus.ko` | 47,764 | 47 |

## 2. `eab_driver.ko`: measured absence, then the reason

The measurement, over three independent scopes:

| Scope | Result |
| :--- | :--- |
| Loose files named `eab_driver.ko`, whole repository | **0** |
| Tar members named `eab_driver.ko`, every member of every tar (141 archives, 209,121 members, 0 unreadable) | **0** |
| Filesystem paths containing `eab` anywhere in the extracted LTU rootfs | **0** |
| `modules.dep` / `modules.alias` / `modules.builtin` / `modules.order` | all absent |
| `/etc/modules` | absent |

So the file is not missing from one directory that someone forgot to untar. It is absent from the
corpus. Load order cannot be recovered either, because the module metadata files are not in the
extracted rootfs.

The reason is visible in the symbols. Counting a symbol as Ubiquiti-EAB requires `eab` in the name
**and** excludes ARM `__aeabi_*` runtime helpers - a raw substring match would report 128 phantom hits
in `ame_core.ko` alone and say nothing about EAB:

| Module | EAB symbols defined | EAB symbols imported | Example |
| :--- | ---: | ---: | :--- |
| `ame_core.ko` | 123 | 0 | `AME_EAB_ActivateQueue`, `AME_EAB_CheckRxQBD`, `AME_EAB_DumpAirInternal` |
| `ame_dev.ko` | 0 | 1 | `AME_EAB_DumpAirInternal` |
| all other 152 modules | 0 | 0 | - |

`AME_EAB_DumpAirInternal` appears in `ame_core.ko`'s export set and in `ame_dev.ko`'s undefined set,
which is a `CONFIRMED_STATIC` cross-module edge: the EAB block is compiled **into** `ame_core.ko` and
consumed from there. There is no separate EAB module in this build to find. Mark the explanation
`INFERRED`: the corpus cannot exclude a separate module shipping in a firmware tree not extracted here.

## 3. Receipt audit: binaries cited that this corpus does not contain

Scope: the two flat receipt corpora, `artifacts/autoresearch/*.json` and
`artifacts/verification/*.json`. 1,610 receipts scanned, 12 skipped by the 1 MB size cap, 6 excluded
as in-flight stages 1218A-1223A so concurrent work cannot move the numbers.

| Metric | Value |
| :--- | ---: |
| Receipts referencing `eab_driver` somewhere | 111 |
| Receipts asserting it as an analysed binary | **1** |
| Receipts acknowledging its absence | 34 |
| Receipts citing at least one basename absent from the corpus | 150 |
| Distinct absent basenames cited | 19 |

The single presence assertion is `stage85a_versioned_profile_tagging_and_safeguard_registry_20261026.json`,
whose compliance evidence names the analysed set as "airOS 8 WA/XC ubnt_poll_host.ko/umac.ko, airOS 6
XW ath_dev.ko, and LTU ame_core.ko/eab_driver.ko". Two of those five are real in this corpus; the fifth
is not. The receipt references a binary this corpus does not contain, and the tool records the excerpt
so the sentence can be read rather than trusted.

Nineteen absent basenames, classified rather than lumped together:

| Basename | Receipts | Class | Grade |
| :--- | ---: | :--- | :--- |
| `eab_driver.ko` | 104 | phantom module - no file anywhere in the corpus | `CONFIRMED_STATIC` |
| `bridge.ko`, `8021q.ko`, `sch_fq_codel.ko` | 10 / 5 / 2 | standard kernel module, not present as a loadable module here | `INFERRED` |
| `uph.ko` | 10 | abbreviation of `ubnt_poll_host.ko`, which is present (`xc_8725_uph_*.ko` artefacts exist) | `INFERRED` |
| `ame_core_fmx.ko`, `ame_dev_fmx.ko` | 7 / 7 | name not in corpus | `INFERRED` |
| `rocket_ame_core.ko`, `ap_ame_core.ko`, `cpe_ame_core.ko`, `cpe_ame_radio_mod.ko`, `ame_dev_stage80a.ko`, `ubnt_common.ko`, `sch_cake.ko` | 3 / 2 / 1 / 1 / 1 / 1 / 1 | name not in corpus | `INFERRED` |
| `module.ko`, `test_module.ko` | 1 / 1 | generic placeholder, not a claim about a shipped binary | `INFERRED` |
| `loose-.ko`, `trunc.ko`, `5-.ko` | 3 / 2 / 1 | tokenisation noise - fails the filename shape check | `CONFIRMED_STATIC` |

The `_fmx`, `_stage80a`, `rocket_`, `ap_`, `cpe_` names look like build variants of the AME modules.
Only one variant of each AME module exists in this corpus (`ame_core.ko`, `ame_dev.ko`), so those
citations cannot be resolved to bytes from here.

## 4. Roles, from metadata and from measured imports

Role text is inferred. What backs each one is stated per module, and the import/export intersections
are counts of symbol names actually resolved across module boundaries - not names that merely look
related.

| Module | Bytes | Exports | Imports | Imports from `ame_core` | `.modinfo` description |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `ame_core.ko` | 3,282,052 | 31 | 123 | - | none (license `proprietary`) |
| `ame_dev.ko` | 298,760 | 27 | 185 | 12 | none (GPL, `depends=ame_core`) |
| `ame_dfs.ko` | 141,472 | 9 | 97 | 10 | none (GPL, `depends=` empty) |
| `cds_mac_mod.ko` | 139,672 | 0 | 117 | 0 | **Cadence EMAC Reference Driver** (GPL) |
| `ame_radio_mod.ko` | 578,424 | 4 | 42 | 0 | **AME RFIC Driver** (GPL v2) |

**`cds_mac_mod.ko`** - the description string is `Cadence EMAC Reference Driver`, which is
`CONFIRMED_STATIC`. Its import set is pure net/ethtool/platform: `alloc_etherdev_mqs`, `eth_type_trans`,
`__napi_schedule`, `__netdev_alloc_skb`, `__platform_driver_register`, `fixed_phy_add`, `free_netdev`.
It defines `CPS_Lock` / `CPS_UncachedRead32` / `CPS_WritePhysAddress32` (Cadence platform services),
`ame_ethtool_*`, `ame_phy_get_cable_length`, `ame_phy_get_cable_snr`. It exports **nothing** and imports
**nothing** from `ame_core.ko`. Role: wired Cadence GEM Ethernet MAC driver, outside the AME radio data
path. That placement is `INFERRED`; the zero-export, zero-core-import counts behind it are measured. The
`ame_` prefix on its symbols is a packaging artefact, not a dependency - worth stating because the prefix
is exactly the kind of thing a name-based analysis would get wrong.

**`ame_dev.ko`** - GPL, `depends=ame_core` in `.modinfo`, and 12 imports actually satisfied by
`ame_core.ko` exports (`AME_LMAC_GetReg`, `AME_LMAC_SetReg`, `ame_register_hook`, `ame_deregister_hook`,
`ame_log`, `AME_EAB_DumpAirInternal`, BBP getters). Its own 27 exports are `ubus_func_*` registration and
call entry points plus `speedtest_set_callback`. Role: device/shim layer between the netstack and the
proprietary core. `INFERRED`, with the dependency itself `CONFIRMED_STATIC`.

**`ame_dfs.ko`** - GPL, `depends=` is **empty** in `.modinfo`, yet 10 of its 97 imports are satisfied by
`ame_core.ko` exports (`AME_Scheduler_DfsDummyTraffic`, `ame_bbp_get_rxgain`, `ame_bbp_get_duty_cycle`,
`ame_core_set_forceFixedRxGain`, `dfs_adjust_custom_threshold`). The declared dependency metadata
understates the real one, so the measured intersection is what gets reported. Its 9 exports are all DFS
entry points: `ubus_func_call_dfsdetect`, `ubus_func_call_sync_dfsdetect`,
`ubus_func_register_startdfs`, `ubus_func_register_stopallrx`, `ubus_func_register_dfs_irq_ctl`,
`ubus_func_register_dfs_hit_monitor_mode_get`, `ubus_func_register_eng_info`,
`ubus_func_register_fixrxgain`, `ubus_func_register_startallrx`. Defined functions include `DFSdetect`,
`DFS_heavy_env_det`, `ETSI_5G_main`, `ETSI_5G8_main`, `ame_dfs_isr`, `ame_start_ep_dfs`,
`callback_dfsdetect`. Role: regulatory radar-detection engine with its own ISR and char device, exposed
to the stack through a ubus API. `INFERRED` - the names and exports are consistent and specific, but no
call graph across the ubus boundary was walked here.

**`ame_core.ko`** and **`ame_radio_mod.ko`** are included as anchors: the proprietary core (31 exports,
scheduler/LMAC/BBP access) and the AD9361 RFIC driver (4 exports, all `ame_ad9361_*`), both `INFERRED`.

## 5. Grades

| Claim | Grade |
| :--- | :--- |
| 154 modules, sizes, SHA-256, `inventory_digest`, arch mix | `CONFIRMED_STATIC` |
| `eab_driver.ko` present in 0 loose files and 0 of 209,121 tar members | `CONFIRMED_STATIC` |
| 123 Ubiquiti-EAB symbols defined in `ame_core.ko`, 1 imported by `ame_dev.ko` | `CONFIRMED_STATIC` |
| EAB is compiled into `ame_core.ko` rather than shipping as a module | `INFERRED` |
| 111 receipts reference `eab_driver`, 1 asserts it as analysed, 34 acknowledge absence | `CONFIRMED_STATIC` |
| `cds_mac_mod.ko` is a Cadence EMAC driver with no dependency on `ame_core` | description `CONFIRMED_STATIC`, placement `INFERRED` |
| `ame_dfs.ko` is the regulatory radar-detection engine with a ubus API | `INFERRED` |
| Role of `ame_core.ko` / `ame_dev.ko` / `ame_radio_mod.ko` | `INFERRED` |

## 6. Gaps

1. Static only: no module was loaded and no behaviour was observed at runtime.
2. The compiled-into-`ame_core` explanation for EAB is inferred from symbols; the corpus cannot exclude a
   separate EAB module in a firmware tree not extracted here.
3. Nested wave directories under `artifacts/autoresearch` (about 1.3 GB of simulation matrices) were not
   scanned; the 12 receipts above the 1 MB cap are listed individually as skipped.
4. `modules.dep`, `modules.alias`, `modules.builtin`, `modules.order` and `/etc/modules` are absent, so
   load order and built-in status cannot be recovered.
5. Symbol counts come from `.symtab`; a stripped module would report zero, and none was found, but that
   does not prove every module retains a full symbol table.
6. Roles rest on `.modinfo` metadata, export sets and import intersections. No runtime dispatch, no ubus
   call and no interrupt path was traced.
7. The absent-basename audit is name-based: a receipt that refers to a binary by prose rather than a
   filename is not counted.
8. `uph.ko` is classified as an abbreviation of `ubnt_poll_host.ko` because the XW patch artefacts are
   named `xc_8725_uph_*.ko`; that mapping is inferred, not documented anywhere in the corpus.
9. Export counts follow `__ksymtab` relocations; a module using only `EXPORT_SYMBOL_GPL` aliases under a
   different section name would be undercounted, and no such section was found in this corpus.
