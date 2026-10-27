<!-- doc-head: STAGE564A_LTU_AME_CORE_TDMA_FRAMING_AND_SPLIT_UL_DL_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 564A — LTU TDMA frame geometry, split TX/RX frequency and the UL/DL ratio

- **Receipt**: [`artifacts/autoresearch/stage564a_ltu_ame_core_tdma_framing_and_split_ul_dl_re.json`](../artifacts/autoresearch/stage564a_ltu_ame_core_tdma_framing_and_split_ul_dl_re.json)
- **Tool**: [`tools/re/build_stage564a_ltu_ame_core_tdma_framing_and_split_ul_dl_re.py`](../tools/re/build_stage564a_ltu_ame_core_tdma_framing_and_split_ul_dl_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. `eab_driver.ko` absent — tenth confirmation

**0 files.** Readable targets: `ame_core.ko` (3,282,052 bytes) and `ame_dev.ko` (298,760 bytes).

## 1. The frame geometry is a set of settable quantities, not a constant

Three **get/set accessor pairs**, all complete:

| Quantity | Getter | Setter |
| :--- | :--- | :--- |
| frame length | `ame_bbp_get_frame_len` | `ame_bbp_set_frame_len` |
| duty cycle | `ame_bbp_get_duty_cycle` | `ame_bbp_set_duty_cycle` |
| broadcast DL symbols | `ame_core_get_bc_dl_symbols` | `ame_core_set_bc_dl_symbols` |

**`CONFIRMED`**: `get_set_pair_count = 3`. Every frame-shape quantity is **readable and writable**,
which is what makes the frame tunable at runtime rather than fixed at build time.

Three **sub-frame length getters**:

```
bbp_get_tx_sub_frame_length
bbp_get_rx_sub_frame_length
bbp_get_ul_subframe_length_forDFS
```

**`CONFIRMED`**: `subframe_getter_count = 3`. The **separate TX and RX sub-frame lengths** are the
direct evidence that this is a TDD split: the frame is divided into a transmit part and a receive
part with independently computed lengths.

The third one is the interesting one — `bbp_get_ul_subframe_length_for**DFS**`. The uplink
sub-frame length **changes when DFS is active**, because a radar-detected channel forces a
different frame structure. That couples Stage 499A's DFS work to the frame scheduler.

## 2. Four sysfs knobs, every one a show/store pair

In `ame_dev.ko`:

```
duty_cycle           frame_len            bc_dl_symbols         frame_pulse_offset
duty_cycle_show/store  frame_len_show/store  bc_dl_symbols_show/store  frame_pulse_offset_show/store
```

**`CONFIRMED`**: `sysfs_knob_count = 4`. Each is a **complete** show/store pair, so an operator can
read and set it from userspace without a module rebuild.

`frame_pulse_offset` is the most operationally significant: it is the **frame start offset relative
to the sync pulse** — the alignment knob that Stage 416A was looking for when it found the GPS
durations but not the alignment.

## 3. The UL symbol assignment is a record subsystem

```
ame_core_fill_ul_sym_asgmt_record
ame_core_dump_ul_sym_asgmt
ame_core_print_ul_sym_asgmt_record
ame_ul_sym_asgmt_dump            (in ame_dev.ko)
ul_sym_asgmt_open                (in ame_dev.ko)
```

**`CONFIRMED`**: uplink symbol allocation is **recorded per assignment** — fill, dump, print, plus a
device-side dump entry and an `open` for a userspace handle. That is a scheduler that keeps an
audit trail, not one that just computes an index.

**`UNKNOWN`**: the allocation rule itself. The record proves allocations happen and are recorded;
it does not reveal the policy.

## 4. The split TX/RX frequency is in the frame log

```
Replaced channel info, [%3d:%s] duty_cycle:%d framelen:%d, rx/tx freq: %d/%d
```

**`CONFIRMED`**: `rx_tx_freq_pair = 1`. The log prints **two** frequencies — receive and transmit —
alongside the frame length and duty cycle. For a split-band TDD link that is exactly the expected
shape: the LO is programmed separately for RX and TX.

**`UNKNOWN`**: `synthesizer_programming_recovered = 0`. The line prints the pair; the code that
programs the synthesizer for the two frequencies was not located, and Stage 486A established that
the frequency discipline is DCXO-based rather than a named synthesizer API.

## 5. Three token traps

| Token | Hits | Reality |
| :--- | :-: | :--- |
| **`tdma`**, `TDMA` | **0** | the acronym does not exist in either module |
| **`TDD`** | **1** | inside the mangled symbol **`bbp_mrx_foe_TDDeRotCFO`** — a BBP observation-mode name, not frame control |
| **`split`** | **1** | inside **`c_string_smart_split`** — a string helper |

**`REFUTED`**: none of the three is frame vocabulary. This is the sixth instance of the
substring-token failure mode in the series (after `LQ`, `BE`, `moder`, `rx_lo` and `backoff`).

`tdd_literal_hits = 1` and `split_is_coincidence = 1` are recorded so the negative is visible
rather than inferred.

## 6. No ratio literals — again

`duty_ratio_values_recovered = 0`. No `75/25`, `67/33` or `50/50` exists as text, confirming Stage
388A's result on a different pair of modules.

**`CONFIRMED`**: the ratio is **derived** from `dl_symbols` and `ul_symbols` at runtime. The
module logs a validation when the relationship breaks:

```
result->ap.num_of_dl_symbols(%d) > result->ap.dl_symbols(%d) !!
```

That is a **guard**, and it tells us the two symbol counts are not independent: `num_of_dl_symbols`
must not exceed the configured `dl_symbols`. So the configured value is an **upper bound** that the
scheduler may reduce but not exceed.

## 7. What is established

| Claim | Status |
| :--- | :-: |
| `eab_driver.ko` exists | **REFUTED** (0 files, 10th) |
| frame_len / duty_cycle / bc_dl_symbols are get+set pairs | **CONFIRMED** (3/3) |
| four sysfs knobs exist with show+store | **CONFIRMED** (4/4) |
| TX and RX sub-frame lengths are separate | **CONFIRMED** (3 getters) |
| the UL sub-frame length changes under DFS | **CONFIRMED** (`_forDFS` variant) |
| UL symbol allocation is recorded per assignment | **CONFIRMED** (fill/dump/print) |
| the frame log prints a split RX/TX frequency pair | **CONFIRMED** |
| `tdma` exists as a token | **REFUTED** (0 hits) |
| `TDD` / `split` are frame vocabulary here | **REFUTED** (mangled symbol, string helper) |
| a 75/25-style ratio literal exists | **REFUTED** (0 hits) |
| the `dl_symbols` guard exists | **CONFIRMED** (log comparison) |
| the allocation policy | **UNKNOWN / not recovered** |
| the synthesizer programming | **UNKNOWN / not located** |

## 8. The operational reading

This stage answers the "how do I change the split" question with a concrete list, all of it
userspace-reachable:

1. `duty_cycle` — the coarse ratio;
2. `dl_symbols` / `bc_dl_symbols` — the fine symbol budget (an upper bound the scheduler may reduce);
3. `frame_len` — the absolute frame duration;
4. `frame_pulse_offset` — where the frame starts relative to the sync pulse.

Because all four are sysfs pairs, a bench can sweep them and measure, without touching firmware. And
because `ul_subframe_length_forDFS` exists, any sweep on a DFS channel must expect the uplink
length to move for reasons the sweep did not set.

## 9. Gaps

- **`UNKNOWN`** — the legal range and units of `duty_cycle`, `frame_len` and `frame_pulse_offset`.
- **`UNKNOWN`** — the UL symbol allocation policy.
- **`UNKNOWN`** — how the DFS variant changes the UL sub-frame length.
- **`UNKNOWN`** — the synthesizer programming for the RX/TX frequency split.
- **`UNKNOWN`** — whether `frame_pulse_offset` is the 1PPS alignment knob Stage 416A could not find.
- **Known limit** — a get/set pair proves a knob exists, not what value to set.
- **Not attempted** — dynamic validation, on-air frame timing measurement.
