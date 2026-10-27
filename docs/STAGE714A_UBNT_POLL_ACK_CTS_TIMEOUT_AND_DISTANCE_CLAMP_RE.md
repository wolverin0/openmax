<!-- doc-head: STAGE714A_UBNT_POLL_ACK_CTS_TIMEOUT_AND_DISTANCE_CLAMP_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 714A — ACK/CTS timeout and IFS slot written from distance and RTT

- **Receipt**: [`artifacts/autoresearch/stage714a_ubnt_poll_ack_cts_timeout_and_distance_clamp_re.json`](../artifacts/autoresearch/stage714a_ubnt_poll_ack_cts_timeout_and_distance_clamp_re.json)
- **Tool**: [`tools/re/dissect_stage714a_ubnt_poll_ack_cts_timeout_and_distance_clamp_re.py`](../tools/re/dissect_stage714a_ubnt_poll_ack_cts_timeout_and_distance_clamp_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Four modules, not two

The stage names `ubnt_poll_host.ko` and `ath_dev.ko`. The chain actually spans **four**:

| Module | What it contributes |
| :--- | :--- |
| `ubnt_poll_host.ko` | per-node **RTT** |
| `umac.ko` | distance apply, the conversion log, the **readback** event |
| `ath_hal.ko` | the **register setters** |
| `ath_dev.ko` | the proc knobs |

That is the first correction: no single module documents the mechanism end to end, and looking only
in the two the stage names would miss both the setters and the conversion.

## 1. The register names do not exist

| Token | Hits |
| :--- | :-: |
| `MAC_PCU` | **0** |
| `GBL_IFS` | **0** |
| `ni_distance` | **0** |
| `cts_timeout` | **0** |

**`REFUTED`**: `register_macros_absent = 1`. `MAC_PCU_ACK_CTS_TIMEOUT` and `MAC_D_GBL_IFS_SLOT` are
**ath9k macros**; the compiled module carries the numeric offsets, not the identifiers.

**This is a naming result, not an absence result** — the writable interface is present and named:

```
ar9300_set_ack_timeout     ar9300_get_ack_timeout     ar9300_set_slot_time
```

**`CONFIRMED`**: `both_registers_writable = 1`. **Both** registers have named setters, with the ACK
timeout also having a getter. So the mechanism the stage asks about is fully addressable — it just is
not called by the register name.

## 2. The conversion is captured verbatim

The single most valuable line in this stage:

```
%s: distance set to %d (ACK_CTS_Timeout = %d)
```

**`CONFIRMED`**: `conversion_named = 1`.

That log prints the **input and the output of the conversion in one string**. It proves the dependency
directly — no inference needed — and it is the point where a live system would reveal the
coefficient, since both numbers appear together.

## 3. The chain, step by step, every link named

| # | Step | Symbol | Module |
| :-: | :--- | :--- | :--- |
| 1 | per-node RTT | **`ubnt_poll_host_set_node_rtt`** | `ubnt_poll_host.ko` |
| 2 | RTT request | `ol_ath_rtt_meas_req` | `umac.ko` |
| 3 | RTT report | `wmi_rtt_meas_report_event_handler` | `umac.ko` |
| 4 | distance apply | **`ol_ath_set_distance`** | `umac.ko` |
| 5 | ACK/CTS write | **`ar9300_set_ack_timeout`** | `ath_hal.ko` |
| 6 | slot write | **`ar9300_set_slot_time`** | `ath_hal.ko` |
| 7 | readback | `WMI_ACK_CTS_READ_EVENTID` + `wmi_unified_ack_cts_read_event_handler` | `umac.ko` |

**`CONFIRMED`**: `rtt_chain_complete = 1` (3 of 3), `hal_setter_count = 3`,
`readback_present = 1`.

Three details stand out:

**RTT is measured, not assumed.** `ol_ath_rtt_meas_req` is a **request** and
`wmi_rtt_meas_report_event_handler` is the **report** — so RTT is a round trip through the target, not
a distance estimate derived from RSSI. That matters: RSSI-based distance is coarse and
environment-dependent; an RTT measurement is a timing quantity.

**RTT is tracked, with state.** `ubnt_poll_host_reset_ff_rtt_active` exists, so the polling module
maintains an **active/reset** state for its RTT tracking. It is a maintained quantity, not a one-shot.

**The host can read back what the target applied.** `WMI_ACK_CTS_READ_EVENTID` and its handler mean
the host does not have to trust that its written value survived — it can ask. That is exactly the
mechanism needed if the firmware **clamps** the timeout.

## 4. Both input and output are readable at runtime

`ath_dev.ko` exposes proc fields:

```
distance        get_distance
acktimeout      get_acktimeout
```

**`CONFIRMED`**: the **input** (distance) and the **output** (acktimeout) are both readable. So the
conversion can be observed at both ends:

1. set or read `distance`;
2. read `acktimeout`;
3. compare against the log line's two printed values.

That is a complete observation loop with no instrumentation beyond procfs and dmesg.

## 5. What is *not* recovered: the coefficient and the clamp

**`REFUTED`**: `distance_formula_recovered = 0`. The log prints input and output, but the arithmetic
between them is not in the module.

**`REFUTED`**: `distance_clamp_recovered = 0`. The stage asks specifically about a **clamp**, and the
host modules do not contain the clamp rule. The readback event lets you **observe** a clamp, but not
predict it.

The physical expectation is well known — the ACK timeout must cover twice the propagation delay plus
the frame duration, so it grows roughly with distance — but this stage does not restate the textbook
formula as if it had recovered it. What it recovered is the **plumbing**, not the constant.

## 6. What is established

| Claim | Status |
| :--- | :-: |
| `MAC_PCU_ACK_CTS_TIMEOUT` / `MAC_D_GBL_IFS_SLOT` exist as strings | **REFUTED** (0 hits) |
| both registers have named HAL setters | **CONFIRMED** (`set_ack_timeout`, `set_slot_time`) |
| distance and ACK/CTS timeout are directly linked | **CONFIRMED** (one log line, both values) |
| the RTT chain is complete through WMI | **CONFIRMED** (3/3) |
| RTT tracking has an active/reset state | **CONFIRMED** (`reset_ff_rtt_active`) |
| a host readback of the applied value exists | **CONFIRMED** (`WMI_ACK_CTS_READ_EVENTID`) |
| distance and acktimeout are proc-readable | **CONFIRMED** |
| the conversion coefficient | **UNKNOWN / not in the module** |
| the clamp rule | **UNKNOWN / observable but not encoded here** |
| the slot-time derivation from distance | **UNKNOWN / setter only** |

## 7. The operational reading

For a long-link problem this gives a concrete, low-risk procedure:

1. read `distance` and `acktimeout` from procfs on the AP (both exist);
2. grep the log for `ACK_CTS_Timeout =` to see the conversion fire and with what pair of numbers;
3. if `acktimeout` stops tracking `distance`, the clamp is active — confirm via the readback event
   rather than guessing.

What cannot be done from the binary is predict the clamp threshold. That has to be measured, and
this stage says so instead of inventing a limit.

## 8. Gaps

- **`UNKNOWN`** — the metres-to-microseconds coefficient.
- **`UNKNOWN`** — the clamp: threshold, whether it applies to distance or to the timeout, and
  whether it is in firmware or host.
- **`UNKNOWN`** — how slot time is derived from distance (the setter is named, the derivation is not).
- **`UNKNOWN`** — the RTT measurement's period and averaging.
- **`UNKNOWN`** — whether `rtt_us` and `ni_distance_m` are the actual field names on the wire.
- **Known limit** — a named setter proves the write path, not the value written.
- **Not attempted** — dynamic validation, on-air RTT measurement.
