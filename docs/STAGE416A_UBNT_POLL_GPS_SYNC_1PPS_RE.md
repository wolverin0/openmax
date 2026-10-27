<!-- doc-head: STAGE416A_UBNT_POLL_GPS_SYNC_1PPS_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 416A — GPS 1PPS TDMA frame sync in `ubnt_poll_host.ko`

- **Receipt**: [`artifacts/autoresearch/stage416a_ubnt_poll_gps_sync_1pps_re.json`](../artifacts/autoresearch/stage416a_ubnt_poll_gps_sync_1pps_re.json)
- **Tool**: [`tools/re/ubnt_poll_gps_sync_1pps_timingslot_re.py`](../tools/re/ubnt_poll_gps_sync_1pps_timingslot_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Three modules, one vocabulary, identical counts

| Module | Bytes | `down_dur` | `up_dur` | `cbp_dur` | `fixed_frame` | `pps` | `gps` |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| `WA.v8.7.25` | 189,880 | **8** | **6** | **4** | **1** | 4 | 3 |
| `XC.v8.7.25` | 189,880 | **8** | **6** | **4** | **1** | 4 | 3 |
| `2XC.v8.7.11` | 186,560 | **8** | **6** | **4** | **1** | 4 | 3 |

**`CONFIRMED`**: the TDMA GPS duration vocabulary is real, and the counts are **identical across
three builds spanning two versions and a 3,320-byte size difference** (WA/XC 189,880 vs 2XC
186,560). The three symbols `down_dur`, `up_dur`, `cbp_dur` and the flag `fixed_frame` are the
frame-shape contract the stage describes.

That is a stronger result than it looks: a delta of 3,320 bytes between 8.7.11 and 8.7.25 changes
nothing in this vocabulary, so the durations are inherited code, not a recent addition.

## 1. What is *not* there

| Token | Hits |
| :--- | :-: |
| `gps_sync` | **0** |
| `frame_offset` | **0** |
| `coloc`, `co-loc`, `colocated`, `auto_interference` | **0** |
| `1pps` | **0** |
| `sector` | **0** |

**`REFUTED`**: `gps_sync` and `frame_offset` are not literals. The stage names them as if they
were fields; the module names the **durations** and a `fixed_frame` flag instead.

**`REFUTED`**: there is **no co-location or auto-interference marker anywhere**. The sector
self-interference prevention the stage describes has **no anchor in this corpus**. It may exist in
the scheduler arithmetic, but it is not named, and this stage will not manufacture it.

## 2. `ubnt-gps-reader` has no bytes

| Candidate path | Exists | Bytes |
| :--- | :-: | :-: |
| `afltu_2.4.2/.../bin/ubnt-gps-reader` | yes | **0** |
| `aflturocket_2.4.2/.../bin/ubnt-gps-reader` | yes | **0** |
| `afltu_2.4.2/.../usr/bin/ubnt-gps-reader` | no | — |
| `aflturocket_2.4.2/.../usr/bin/ubnt-gps-reader` | no | — |

**`CONFIRMED`**: **0 of 4** candidate readers is readable. The two that exist are **zero-byte
stubs**, as are `bin/gps` and `bin/gps_cmd` in the same trees.

So the userspace half of the stage — the 1PPS source, its device node, its ioctl contract — **has
no bytes to analyse**. This is the same corpus-wide defect already recorded for the LTU rootfs:
files that exist by name and contain nothing.

## 3. What 1PPS synchronisation actually requires, and what is missing

A GPS-locked TDMA frame needs four things. The corpus supplies one and a half:

| Requirement | State in this corpus |
| :--- | :--- |
| 1. a 1PPS edge source | **blocked** — `ubnt-gps-reader` is 0 bytes |
| 2. a frame origin aligned to that edge | **partial** — `fixed_frame` exists, `frame_offset` does not |
| 3. a frame shape (down / up / CBP durations) | **present** — `down_dur`, `up_dur`, `cbp_dur` |
| 4. inter-sector separation | **absent** — no `coloc`/`sector`/`auto_interference` marker |

**`CONFIRMED`**: the frame shape (3) is the part that is solidly named. The **alignment** to an
absolute time reference (2) is only half-named, and the reader that would supply (1) is empty.

That is why `sync_state_machine_recovered = 0`. The durations tell you the frame's *geometry*;
nothing in the readable corpus tells you *when* it starts relative to the GPS second.

## 4. The 5 / 8 / 10 ms fixed frames

The stage asserts fixed frames of 5, 8 and 10 ms. The tool looked for those as strings
(`5ms`, `8ms`, `10ms`, and spaced variants) and found **none** (see the receipt's
`frame_ms_strings`).

**`REFUTED`**: the frame periods are not enumerated as literals. `fixed_frame` is a boolean
selector; the period it selects is not written down in a string.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| `down_dur` / `up_dur` / `cbp_dur` exist, identically on WA, XC and 2XC | **CONFIRMED** |
| `fixed_frame` exists as a flag | **CONFIRMED** |
| the vocabulary is unchanged across 8.7.11 and 8.7.25 | **CONFIRMED** |
| `gps_sync` / `frame_offset` exist as literals | **REFUTED** |
| a co-location / auto-interference marker exists | **REFUTED** |
| `ubnt-gps-reader` is readable | **REFUTED** (0 of 4, the two existing ones are 0 bytes) |
| 5 / 8 / 10 ms fixed frames are enumerable from strings | **REFUTED** |
| the 1PPS alignment mechanism | **UNKNOWN / not recoverable here** |

## 6. The one operational consequence

Because the duration vocabulary is **identical** on 8.7.11 and 8.7.25 and on both the 189,880-byte
and 186,560-byte builds, a GPS timing difference between those versions **cannot** come from these
field names. If a park reports different GPS behaviour between firmware versions, the cause is in
the arithmetic or in the (empty) reader — not in the field set.

That is a narrow but real conclusion, and it is the only one the evidence supports.

## 7. Gaps

- **`UNKNOWN`** — the units, range and defaults of `down_dur`, `up_dur`, `cbp_dur`.
- **`UNKNOWN`** — what `fixed_frame` selects, and what the unfixed mode does.
- **`UNKNOWN`** — how the frame origin is aligned to the 1PPS edge.
- **`UNKNOWN`** — whether sector separation exists and under what name.
- **Blocked** — every userspace question, until a non-empty `ubnt-gps-reader` exists.
- **Not attempted** — dynamic validation, and any GPS hardware interaction.
