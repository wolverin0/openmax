<!-- doc-head: STAGE807A_LTU_SPLIT_FREQ_AND_OFDMA_SUBCHANNEL_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 807A — LTU split-frequency programming and OFDMA subchannel vocabulary

- **Receipt**: [`artifacts/autoresearch/stage807a_ltu_split_freq_and_ofdma_subchannel_re.json`](../artifacts/autoresearch/stage807a_ltu_split_freq_and_ofdma_subchannel_re.json)
- **Tool**: [`tools/re/dissect_stage807a_ltu_split_freq_and_ofdma_subchannel_re.py`](../tools/re/dissect_stage807a_ltu_split_freq_and_ofdma_subchannel_re.py)
- **Scope**: offline static. No module loaded, no radio contacted, nothing transmitted.

## 0. The subchannel vocabulary does not exist; the UL map does

| Token | `ame_core.ko` + `ame_dev.ko` |
| :--- | :-: |
| `ofdma` + `OFDMA` | **102** |
| **`ulmap`** | **20** (17 named symbols) |
| `rx/tx freq` | **4** |
| **`subchannel`, `sub_chan`, `ru_`** | **0** |

**`REFUTED`**: `subchannel_vocabulary_absent = 1`.

**`CONFIRMED`**: the allocation concept is named **`ulmap`** — the **uplink MAP**, the WiMAX/LTE
lineage term for the same thing. A search for "subchannel" or "resource unit" finds nothing; the
mechanism is there under a different name.

The UL map is a **real API**, not a field:

```
AME_EAB_PushULMap          Ctrl_GetULMap_Info
Ctrl_DebugULMap            IF_Ctrl2Sched_GetULMap_Info
ame_core_dump_ul_sym_asgmt ame_core_fill_ul_sym_asgmt_record
```

**`CONFIRMED`**: `ulmap_is_named_subsystem = 1`, `ulmap_symbol_count = 17`.

Note the direction of the calls: `PushULMap` (EAB layer pushes a map **to the ASIC**) beside
`GetULMap_Info` (the scheduler reads it **back**). So the map is **written by the ARM and read by the
scheduler** — matching Stage 694A's finding that the ARM polls the ASIC for queue state.

`IF_Ctrl2Sched_GetULMap_Info` is the informative one: **control-plane to scheduler** — the map is
produced above the scheduler and consumed by it.

## 1. The OFDMA surface is dense and symbol-rich

**`CONFIRMED`**: `ofdma_token_hits = 102`, `ofdma_symbol_count = 22`.

That is more than Stage 438A's first pass measured (88 tokens), and it confirms the LTU frame
scheduler is **OFDMA-aware**, not merely TDD. Combined with Stage 564A's `frame_len` / `duty_cycle` /
`dl_symbols` / `ul_symbols`, the picture is a TDD frame that **carries an OFDMA uplink map**.

## 2. The split frequency is printed and configured, never "programmed"

**`CONFIRMED`**: `split_freq_pair_present = 1` — 4 hits of the log line Stage 564A first read:

```
Replaced channel info, [%3d:%s] duty_cycle:%d framelen:%d, rx/tx freq: %d/%d
```

**`CONFIRMED`**: `split_preference_keys = 2` — `prefer_work_txfreq` and `prefer_work_rxfreq` are
**separate** configuration keys (Stage 590A found them in the auto-frequency block).

**`REFUTED`**: no `synthesizer`, `pll` or `lo` symbol programs the two frequencies by name. Stage 486A
established the frequency discipline is **DCXO**-based (`bbp_rf_dcxo_sync_*`,
`bbp_rf_dcxo_is_sync_by_gps`), and nothing here contradicts that.

So the split is **declared and preferred** at the driver level, and **applied** through the DCXO
discipline — with the actual retune arithmetic not in these modules.

## 3. What is established

| Claim | Status |
| :--- | :-: |
| a `subchannel` or resource-unit vocabulary exists | **REFUTED** (0 hits) |
| the allocation is named `ulmap` | **CONFIRMED** (20 tokens, 17 symbols) |
| the UL map is pushed to the ASIC and read back | **CONFIRMED** (`PushULMap`, `GetULMap_Info`) |
| the map crosses control-plane → scheduler | **CONFIRMED** (`IF_Ctrl2Sched_GetULMap_Info`) |
| the frame scheduler is OFDMA-aware | **CONFIRMED** (102 tokens, 22 symbols) |
| the split frequency appears as a printed rx/tx pair | **CONFIRMED** (4 hits) |
| TX and RX preferences are separate keys | **CONFIRMED** (`prefer_work_txfreq`/`rxfreq`) |
| a named synthesizer routine programs the split | **REFUTED** |
| the `ulmap` structure (subchannels, widths, CPE assignment) | **UNKNOWN / not decoded** |
| the split-frequency retune arithmetic | **UNKNOWN / DCXO-based, 486A** |

## 4. The operational reading

For an OFDMA uplink problem, the corpus gives a clear chain and one blind spot:

1. the **map** is built control-side and handed to the scheduler (`IF_Ctrl2Sched_GetULMap_Info`);
2. the **EAB layer pushes** it to the ASIC (`AME_EAB_PushULMap`);
3. the **allocation is recorded** per assignment (`ul_sym_asgmt`, Stage 564A) — so a mismatch is
   auditable after the fact.

The blind spot is the **map's internal structure**: how many subchannels, their widths, and which CPE
gets which. The names are all present; the layout is numeric.

For a split-frequency problem the handles are `prefer_work_txfreq` and `prefer_work_rxfreq` — and the
expectation should be that the **DCXO** does the retune, not a per-packet synthesizer.

## 5. Gaps

- **`UNKNOWN`** — the `ulmap` structure and its field widths.
- **`UNKNOWN`** — how many OFDMA subchannels the frame supports.
- **`UNKNOWN`** — the mapping from a CPE to its UL map entry.
- **`UNKNOWN`** — the split-frequency retune arithmetic and its settling time.
- **`UNKNOWN`** — whether `prefer_work_txfreq`/`rxfreq` are enforced or advisory.
- **Known limit** — 17 named UL map symbols still do not describe a layout.
- **Not attempted** — dynamic validation, on-air uplink measurement.
