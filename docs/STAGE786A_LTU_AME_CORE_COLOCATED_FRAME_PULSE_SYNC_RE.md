<!-- doc-head: STAGE786A_LTU_AME_CORE_COLOCATED_FRAME_PULSE_SYNC_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 786A — frame_pulse_offset, remote SFN sync and panel isolation

- **Receipt**: [`artifacts/autoresearch/stage786a_ltu_ame_core_colocated_frame_pulse_sync_re.json`](../artifacts/autoresearch/stage786a_ltu_ame_core_colocated_frame_pulse_sync_re.json)
- **Tool**: [`tools/re/dissect_stage786a_ltu_ame_core_colocated_frame_pulse_sync_re.py`](../tools/re/dissect_stage786a_ltu_ame_core_colocated_frame_pulse_sync_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Two modules

`ame_core.ko` (3,282,052 bytes) and `ame_dev.ko` (298,760 bytes).

## 1. `frame_pulse_offset` is a writable runtime knob

```
ame_bbp_set_frame_pulse_offset      ame_bbp_get_frame_pulse_offset        (ame_core.ko)
frame_pulse_offset_show             frame_pulse_offset_store              (ame_dev.ko)
```

**`CONFIRMED`**: `frame_pulse_offset_getset = 1`, `frame_pulse_offset_sysfs_pairs = 1`,
`frame_alignment_knob_present = 1`.

This closes a loop left open two stages apart. Stage 416A found the GPS **frame durations**
(`down_dur`, `up_dur`, `cbp_dur`, `fixed_frame`) in `ubnt_poll_host.ko` but could **not** find what
aligned the frame to the pulse. Stage 564A found `frame_pulse_offset` as a sysfs pair and flagged it
as the likely answer without proof. Here the accessor pair in `ame_core.ko` confirms it: the offset
is **set and read in the driver**, and **exposed to userspace**, so it is a tuning parameter rather
than a compile-time constant.

**`UNKNOWN`**: the units (symbols? microseconds? samples?) and the reference point the offset is
measured from.

## 2. The SFN sync predicate exists at two layers

```
ame_bbp_is_remote_SFN_synchronized
bbp_base_is_remote_SFN_synchronized
```

**`CONFIRMED`**: `sync_predicate_variants = 2` — a high-level accessor and a base-level one.

Combined with Stage 668A, the pair gives an operator **two numbers** rather than one flag:

| Symbol | What it answers |
| :--- | :--- |
| `is_remote_SFN_synchronized` | **are** the two ends aligned |
| `get_sync_sfn_count` (668A) | **by how many superframes** they are not |

That is the measurement pair for a misaligned CPE, and it requires no GPS instrumentation to read.

## 3. The isolation that exists isolates clients, not panels

```
ame_core_get_cli_isolation      ame_core_set_cli_isolation
```

**`CONFIRMED`**: `cli_isolation_getset = 1`.

**`REFUTED`**: `coloc`, `COLOC`, `sector` and `panel` all return **0**
(`coloc_sector_panel_absent = 1`).

**`cli_isolation` is client isolation** — preventing associated stations from reaching each other.
That is a **different mechanism** from isolating co-located panels, which is what the stage asks for.

This is a **semantic** trap rather than a substring one, and it is the more dangerous kind: the token
`isolation` is a perfect match, the symbol is real, and the accessor pair is complete. Only the
**meaning** is wrong. Reading `cli_isolation` as panel isolation would produce a confident, wrong
answer.

## 4. What the corpus cannot answer about panel isolation

The ingredients for panel isolation exist, spread across three stages:

| Ingredient | Where | Stage |
| :--- | :--- | :--- |
| frame pulse offset (alignment) | `ame_bbp_set/get_frame_pulse_offset` | here |
| superframe sync predicate and miss count | `is_remote_SFN_synchronized`, `get_sync_sfn_count` | 668A |
| listen-before-talk with `pause_txframe` | `ame_core_lbt_*` | 590A |
| interference level as a measurable | `get_rf_interference_avg/_curr` | 590A |

**`REFUTED`**: no `coloc`, `sector` or `panel` marker **binds them together**. There is no named
"panel isolation" object anywhere in the two modules.

So the mechanism may be **composed** from those parts at a higher layer (a management process
configuring offsets and LBT per panel), or it may live in the fabric bitstream that is absent from
the corpus. This stage does not choose between those, and `panel_isolation_scheme_recovered = 0`.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| `frame_pulse_offset` is a get/set pair in the driver | **CONFIRMED** |
| it is exposed as a sysfs show/store pair | **CONFIRMED** |
| the SFN sync predicate exists at two layers | **CONFIRMED** |
| a superframe miss count is readable (668A) | **CONFIRMED** |
| client isolation has a get/set pair | **CONFIRMED** |
| `coloc` / `sector` / `panel` exist as identifiers | **REFUTED** (0 hits) |
| a named panel-isolation scheme exists | **REFUTED** |
| the offset's units and reference point | **UNKNOWN** |
| how co-located panels are kept apart | **UNKNOWN / not named** |

## 6. The operational reading

For a two-panel co-location problem, the corpus supports a **measurement** but not a **policy**:

1. read `is_remote_SFN_synchronized` per panel — if false, the panels are not on the same superframe
   grid and no amount of TX isolation will fix the interference;
2. read `get_sync_sfn_count` — the magnitude says whether it is a one-frame slip or a persistent
   offset;
3. adjust `frame_pulse_offset` per panel — the sysfs pair makes this a live experiment rather than a
   reflash.

What cannot be read is a **panel-isolation setting**, because none is named. If a deployment expects
one, it is either composed externally or it does not exist on this platform.

## 7. Gaps

- **`UNKNOWN`** — `frame_pulse_offset` units and reference point, and its legal range.
- **`UNKNOWN`** — which layer owns the SFN sync decision (two predicates, one answer).
- **`UNKNOWN`** — how co-located panels are configured apart; no marker exists.
- **`UNKNOWN`** — whether the fabric bitstream implements TX blanking per panel.
- **`UNKNOWN`** — the `cli_isolation` semantics beyond the name (per-AP, per-SSID, or per-interface).
- **Known limit** — a perfect token match with the wrong meaning is still a wrong answer.
- **Not attempted** — dynamic validation, two-panel interference measurement.
