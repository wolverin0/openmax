<!-- doc-head: Stage 831A - one pps does not exist and pps is a VoIP packet-rate bound, frame_start_offset has no AC counterpart, while the guard unit field and the three AC-side atpc bounds are the real panel-alignment levers and WA and XC polling modules differ despite identical size -->
<!-- /doc-head -->
# Stage 831A — ubnt_poll_host GPS sync and frame-start offset

- **Receipt**: [`artifacts/autoresearch/stage831a_ubnt_poll_gps_sync_and_frame_start_offset_re.json`](../artifacts/autoresearch/stage831a_ubnt_poll_gps_sync_and_frame_start_offset_re.json)
- **Tool**: [`tools/re/dissect_stage831a_ubnt_poll_gps_sync_and_frame_start_offset_re.py`](../tools/re/dissect_stage831a_ubnt_poll_gps_sync_and_frame_start_offset_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Two modules, same size, different content

| Image | Bytes | SHA-256 |
| :--- | :-: | :--- |
| `WA.v8.7.25:ubnt_poll_host.ko` | 189,880 | distinct |
| `XC.v8.7.25:ubnt_poll_host.ko` | 189,880 | distinct |

**`CONFIRMED`**: `modules_identical = 0`. The two are **the same size and different binaries** — so a
size check would have called them identical, and a byte-level comparison catches the difference.

## 1. `1pps` does not exist, and `pps` is a VoIP packet rate

| Token | Hits (both images) |
| :--- | :-: |
| **`1pps`** | **0** |
| `voip_pps` | **8** |
| `gps` | 6 |

**`REFUTED`**: `one_pps_absent = 1`. The one-second pulse has **no identifier** in this module.

**`CONFIRMED`**: `pps_is_voip_rate = 1` — every `pps` hit is `voip_pps_min` / `voip_pps_max`, a
**packets-per-second bound for VoIP admission**. Reading it as a 1PPS edge would be wrong.

This is the same finding Stage 668A reached on the LTU side, now confirmed on AC: **neither line names
the 1PPS edge**.

## 2. `frame_start_offset` has no AC counterpart

| Token | Hits |
| :--- | :-: |
| `frame_start` | **0** |
| `start_offset` | **0** |
| `offset` | **0** |

**`REFUTED`**: `frame_start_offset_absent = 1`.

Stage 564A found `frame_pulse_offset` in the **LTU** modules (get/set + sysfs), and Stage 786A proved
it is the alignment knob. The **AC** polling module has **no equivalent name at all** — not even the
word `offset`.

## 3. What the AC module actually offers: a guard field and three ATPC bounds

```
ff_guard_units     ff_frame_dur     ff_dl_alloc     ff_cbp_s…
atpc_target_rssi   atpc_max_power   atpc_min_power
```

**`CONFIRMED`**: `guard_units_field = 1` — `ff_guard_units` is the **TDD guard in units**, and it is a
**sysctl field**, not a constant. It appears in the same dump as `ff_unit_shift` and
`ff_ack_arbit_max`, which is the frame-geometry block.

**`CONFIRMED`**: `atpc_control_count = 3` — target RSSI plus a **max and min power bound**.

That triple is the panel-alignment lever set: with three co-located panels, what keeps them apart is
the **guard** (time separation) and the **ATPC bounds** (power separation), both settable.

## 4. GPS is a proc node, not an engine

```
gps_info    enabled    disabled    enable    status    timing    gpsreset
```

**`CONFIRMED`**: `gps_proc_node_present = 1` (2 hits). The GPS state exposes **status** and
**timing**, and `gpsreset` resets it — so it is **observable and resettable**.

**`REFUTED`**: no 1PPS edge handler, no interrupt, no counter. The node **reports**; nothing named
**consumes an edge**.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| WA and XC `ubnt_poll_host.ko` are identical to size but not to bytes | **CONFIRMED** |
| a `1pps` identifier exists | **REFUTED** (0) |
| `pps` is a 1PPS edge | **REFUTED** (VoIP packet rate) |
| `frame_start_offset` exists on AC | **REFUTED** (0) |
| the TDD guard is a settable field | **CONFIRMED** (`ff_guard_units`) |
| ATPC has a target and two bounds | **CONFIRMED** (3 controls) |
| the GPS state is a readable proc node | **CONFIRMED** (`gps_info` status/timing) |
| a three-panel alignment scheme is named | **REFUTED** (`panel`/`coloc`/`sector` = 0) |
| the frame-start offset formula | **UNKNOWN / not in this module** |

## 6. The operational reading

For the Guarida three-panel alignment, the AC corpus offers **two knobs and one observer**:

1. **`ff_guard_units`** — the time separation between frames;
2. **`atpc_max_power` / `atpc_min_power` / `atpc_target_rssi`** — the power separation;
3. **`gps_info` status and timing** — whether the reference is healthy.

What it does **not** offer is a named panel offset. The LTU line has `frame_pulse_offset`; the AC line
does not. So an alignment procedure on AC must be built from guard plus ATPC, and any claim that an
`offset` field exists there would be false.

## 7. Gaps

- **`UNKNOWN`** — the `ff_guard_units` value that prevents collision between three panels; it is
  deployment data.
- **`UNKNOWN`** — the unit scale of `ff_guard_units`.
- **`UNKNOWN`** — how `gps_info.timing` is expressed and who consumes it.
- **`UNKNOWN`** — whether the AC line has an offset under a name none of the probes used.
- **Known limit** — a proc node that reports timing is not a synchronisation engine.
- **Not attempted** — dynamic validation, live panel measurement.
