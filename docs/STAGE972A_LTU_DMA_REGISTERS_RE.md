<!-- doc-head: Stage 972A - the LTU DMA surface is abstract handles only, 273 queue-and-descriptor symbols carrying no register identity, with doorbell and pcie absent from all seven modules and zero register names or values recoverable without a disassembler -->
# Stage 972A - the LTU DMA register surface

- **Receipt**: [`artifacts/autoresearch/stage972a_ltu_dma_registers_re.json`](../artifacts/autoresearch/stage972a_ltu_dma_registers_re.json)
- **Tool**: [`tools/re/dissect_stage972a_ltu_dma_registers_re.py`](../tools/re/dissect_stage972a_ltu_dma_registers_re.py)
- **Scope**: static only. Offline ELF and symbol inspection of seven extracted LTU `.ko` files. No module loaded, no firmware written, no radio contacted.
- **Provenance**: `CONFIRMED_STATIC_BINARY`

## 0. Result

```
modules_ok=7          dma_token_hits=202        dma_symbols=273
ring_symbols=14       doorbell_present=0        pcie_present=0
register_names_recovered=0   register_values_recovered=0
register_accessor_symbols=11 surface_is_abstract_only=1
```

The stage answers one question and answers it in the negative: **no named DMA register exists in the
`.symtab` of any of the seven modules.** What exists is a vocabulary of handles - queues, QBDs, rings,
copy engines, ISR entry points - and a small set of accessor functions.

## 1. Which module owns what

Ownership is the module with the highest token total, where a token total is distinct matching symbol
names plus printable-ASCII runs containing the token:

| token | owner | hits | what the owner actually is |
| :--- | :--- | ---: | :--- |
| `dma` | `ame_core.ko` / `ame_dev.ko` | 20 | the radio MAC and its ethtool shim |
| `ring` | `qca-ssdk.ko` | 35 | an Ethernet switch SDK, not the airMAX MAC |
| `desc` | `cds_mac_mod.ko` | 10 | the EMAC descriptor layer |
| `ddr` | `ame_radio_mod.ko` | 6 | RFIC/DAC DDR plumbing |
| `irq` | `ame_dfs.ko` | 34 | DFS IRQ control via ubus |
| `csr` | none | 0 | absent |
| `pcie` | none | 0 | absent |
| `doorbell` | none | 0 | absent |

Read that table as a warning. The single largest DMA vocabulary in the tree belongs to `qca-ssdk.ko`,
which is a switch SDK. Attributing its ring API to the radio DMA path is a category error, and this
stage does not do it.

## 2. The token boundary policy, and why it matters

An unfiltered substring census produces large, wrong numbers. Four collision families dominate:

| family | unfiltered | correct | why |
| :--- | ---: | ---: | :--- |
| `ddr` | 87 | 2 | `address`, `macaddr` contain `ddr` |
| `dma` | 52 | 13 | camelCase embeddings such as `EnableDMAMonitor` are not counted |
| `ring` | 26 | 14 | `string` and `strings` contain `ring` |
| `csr` | 7 | 0 | `FcsRemove` contains `csr` |
| `desc` | 11 | 1 | `description` contains `desc` |

The receipt carries both columns (`loose_substring_symbol_counts` and `token_totals.symbols`) so the
filter's cost is auditable. The strict policy is a **floor**: it under-reports rather than over-reports,
which is the correct direction for a negative claim. `dma_token_hits=202` is therefore a minimum.

## 3. Register names versus abstract handles

`register_names_recovered` counts symbols that **are** a register: an `STT_OBJECT` or `STT_NOTYPE` whose
name has a register identifier shape, or an all-caps macro that survived into `.symtab` and contains
`REG` or `CSR`.

The measured value is **0**.

Every register-shaped symbol in the tree is `STT_FUNC`, which makes it an accessor, not a register:

```
ame_core.ko    testflow_hfe_regCAM
ame_dev.ko     reg_info_show   reg_obey_store   reg_info_store
qca-ssdk.ko    dess_reg_access_init   isisc_reg_access_init   shiva_reg_access_init
               isis_reg_access_init    ssdk_switch_reg_access_mode_get
               ssdk_psgmii_reg_access_mode_get   ssdk_uniphy_reg_access_mode_get
```

`AME_LMAC_GetReg` and `AME_LMAC_SetReg` are exported through `__ksymtab`, so an indirect register access
API demonstrably exists. The API proves registers exist. It does not name one of them, and it does not
give an offset. **CONFIRMED** for the accessors, **UNKNOWN** for every register they touch.

`register_values_recovered=0` is a construction, not a discovery: register offsets are `.text`
immediates, and recovering them requires a disassembler that this stage does not use.

## 4. The handle inventory

273 distinct names across the union of the seven modules. The `ame_core.ko` share is the shape of the
radio data path:

```
AME_EAB_SetupQueues   AME_EAB_ResetQueues   AME_EAB_ActivateQueue   AME_EAB_MakeSuperQueue
AME_EAB_CheckQueueStatus   AME_EAB_GetQueueStatus   AME_EAB_GetQueuesInfo_CPE
AME_CPYENG_AllocFB   AME_CPYENG_FreeFB   AME_CPYENG_HandleRxQBD   AME_CPYENG_SetRxQBD
AME_EAB_DeliverTxQBD   AME_EAB_ReturnRxQBD   AME_EAB_CheckRxQBD   AME_EAB_FreeTxQBD
AME_EAB_EnableDMAMonitor   AME_EAB_GetISRInfo   AME_EAB_MaskDataINT
```

`AME_EAB_*` is the airMAX engine block: **94** functions named `AME_EAB_*` in `ame_core.ko` shape the
queue, descriptor and interrupt surface. They are handles. None of them carries an address.

Sub-counts over the 273: 25 descriptor-shaped (`qbd`, `desc`, `bd_`), 194 queue-shaped, 23 IRQ-shaped.
The queue figure is dominated by `qca-ssdk.ko` shaper and policer queueing, not by the air frame path.

## 5. Rings

14 ring symbols. Thirteen belong to `qca-ssdk.ko` (`fal_edma_ring_queue_map_get/set`,
`fal_ring_flow_ctrl_thres_get/set`, `bg_ring_buf_read/write` and their `dess_`/`_fal_` twins). Exactly
one belongs to a radio-fabric module: `cgrd_et_get_ringparam` in `cds_mac_mod.ko`, an ethtool-style
getter with no register identity.

`ame_core.ko` has **zero** ring symbols. The radio MAC expresses its DMA as queues and QBDs, not as a
ring with an index register.

## 6. Doorbell and PCIe

Measured across all seven modules, as symbols and as printable-ASCII strings:

| token | symbols | strings |
| :--- | ---: | ---: |
| `doorbell` | 0 | 0 |
| `pcie` | 0 | 0 |

**REFUTED.** The LTU module set contains no PCIe endpoint and no doorbell mechanism, by name. The fabric
is described through `AME_GEM_*` (an EMAC/GEM MAC) and `AME_CPYENG_*`, which is an on-die copy engine,
not a host bus doorbell.

## 7. `eab_driver.ko`

Absent. `*eab*.ko` matches 0 files under `artifacts/` and `firmware/`; the module tree holds 154
modules and none is eab. The prior DMA-ring receipts (323A, 694A, 754A, 858A) describe a binary that
this corpus does not contain. **REFUTED** as reproducible claims; nothing here contradicts them, and
nothing here confirms them either.

## 8. Labels

| claim | label |
| :--- | :--- |
| 7 modules parse, 154 in tree | CONFIRMED |
| 273 DMA-vocabulary symbols exist | CONFIRMED |
| 14 ring symbols, 13 of them in `qca-ssdk.ko` | CONFIRMED |
| `AME_EAB_*` is a 94-function queue/descriptor handle API | CONFIRMED |
| zero register-shaped `STT_OBJECT` symbols | CONFIRMED |
| `AME_LMAC_GetReg`/`SetReg` are exported accessors | CONFIRMED |
| `doorbell` absent | REFUTED (0 symbols, 0 strings) |
| `pcie` absent | REFUTED (0 symbols, 0 strings) |
| which register `AME_LMAC_GetReg` touches | UNKNOWN |
| any register offset value | UNKNOWN (no disassembly) |
| `eab_driver.ko` reproduces the prior DMA receipts | REFUTED (0 files) |

## 9. Gaps

1. No disassembler, so `.text` immediates are not attributed to symbols. `register_values_recovered=0`
   reflects the method, not the hardware.
2. The DMA engine is reached only through accessors; the physical register map behind them is
   **UNKNOWN**.
3. `qca-ssdk.ko` supplies the majority of the ring and queue vocabulary and is an Ethernet switch SDK.
   Any radio-DMA claim built on its symbols would be a category error.
4. The strict token policy is a floor, so `dma_token_hits=202` under-counts camelCase embeddings such
   as `AME_EAB_EnableDMAMonitor`.
5. `doorbell` and `pcie` absence is a name-level result; an unnamed mechanism is not excluded.
6. `eab_driver.ko` is absent from the corpus, so the DMA-ring receipts citing it cannot be checked
   against a source binary here.
7. No dynamic trace of any DMA operation; no radio was contacted.

## 10. Reproduce

```
python tools/re/dissect_stage972a_ltu_dma_registers_re.py
```

Two consecutive runs are byte-identical, including under differing `PYTHONHASHSEED`.
