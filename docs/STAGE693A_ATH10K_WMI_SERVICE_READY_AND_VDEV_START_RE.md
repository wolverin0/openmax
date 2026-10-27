<!-- doc-head: STAGE693A_ATH10K_WMI_SERVICE_READY_AND_VDEV_START_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 693A — WMI service-ready, vdev start/up and phymode negotiation

- **Receipt**: [`artifacts/autoresearch/stage693a_ath10k_wmi_service_ready_and_vdev_start_re.json`](../artifacts/autoresearch/stage693a_ath10k_wmi_service_ready_and_vdev_start_re.json)
- **Tool**: [`tools/re/dissect_stage693a_ath10k_wmi_service_ready_and_vdev_start_re.py`](../tools/re/dissect_stage693a_ath10k_wmi_service_ready_and_vdev_start_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. `ath10k_core.ko` absent — fifth confirmation

**0 files.** The ath10k side of the WMI sequence cannot be read. The **vendor `umac.ko`** name table
carries every identifier this stage needs, so the sequence is dissectable — just not on the ath10k
implementation.

## 1. All three identifiers exist, plus three more that complete the sequence

| Identifier | Present |
| :--- | :-: |
| **`WMI_SERVICE_READY_EVENTID`** | **yes** |
| **`WMI_VDEV_START_REQUEST_CMDID`** | **yes** |
| **`WMI_VDEV_UP_CMDID`** | **yes** |
| `WMI_VDEV_RESTART_REQUEST_CMDID` | yes |
| `WMI_VDEV_START_RESP_EVENTID` | yes |
| `WMI_VDEV_STOPPED_EVENTID` | yes |
| `WMI_VDEV_CREATE_CMDID` | yes |

**`CONFIRMED`**: `required_three_present = 1` and `wmi_name_count = 7`.

The neighbours are not decoration — they establish that the vdev lifecycle is a **paired
request/response** flow:

```
VDEV_CREATE -> VDEV_START_REQUEST -> VDEV_START_RESP -> VDEV_UP -> VDEV_STOPPED
                    ^
                    +-- VDEV_RESTART_REQUEST (channel change)
```

**`CONFIRMED`**: `vdev_sequence_complete = 1`. Start has a matching **response**, and stop has its
own event. That means the host does not assume the vdev came up; it waits.

**`CONFIRMED`**: `restart_variant_present = 1`. A **restart** request is a distinct command from a
start — which is what a channel switch needs (Stage 485A's CSA/E-CSA/UCSA).

## 2. The host-side path has a channel-specific variant

Seven send/receive entry points:

```
ol_ath_service_ready_event        wmi_service_ready_event_rx     wmi_ready_event_rx
wmi_unified_vdev_start_send       wmi_unified_vdev_start_chan_send
wmi_unified_vdev_restart_send     wmi_unified_vdev_up_send
```

**`CONFIRMED`**: `host_path_count = 7`, `channel_start_variant = 1`.

`wmi_unified_vdev_start_chan_send` sits **beside** the generic `vdev_start_send`. A separate
channel-start sender means bringing a vdev up on a specific channel is a **different call path**,
not a parameter on the generic one — which is the signature of a two-phase bring-up (create, then
start on a channel).

The service-ready side has three receivers (`ol_ath_service_ready_event`, `wmi_service_ready_event_rx`,
`wmi_ready_event_rx`), so the event is handled at more than one layer — the UMAC does something with
it before the OS-facing layer does.

## 3. The phymode enumeration is explicit and directional

Five strings, taken from the ioctl name table:

```
11ACVHT20    11ACVHT40PLUS    11ACVHT40MINUS    11ACVHT40    11ACVHT80
```

**`CONFIRMED`**: `phymode_count = 5`, `vht40_directional = 1`.

**`11ACVHT40PLUS` and `11ACVHT40MINUS` are separate enum values.** That is the detail that makes
bandwidth negotiation real: a 40 MHz channel is **above or below** its primary 20 MHz, and the two
orientations are different values, not a flag on one value. The bare `11ACVHT40` also exists — so
the stack can express "40 MHz, orientation unspecified" as well as each orientation.

This is more precise than the capability table, which lists bandwidths only:

```
CDD  .STBC.TXBF..CCK  .OFDM .HT20 .HT40 .VHT20.VHT40.VHT80.HTDUP
```

**`CONFIRMED`**: the capability table (Stage 615A) says *which* bandwidths a peer supports; the
phymode enum says *how* the AP is configured. The missing piece — the 40 MHz **orientation** — is
only in the enum.

## 4. What the service-ready payload would contain, and why it is not here

The stage asks for the target's **resource limits** — peer count, vdev count, ring depth. Those are
carried in the **`WMI_SERVICE_READY_EVENTID` payload**, which is runtime data written by the target.

**`REFUTED`**: they are not recoverable from the module. `resource_limits_recovered = 0`,
`service_ready_payload_recovered = 0`.

The module names the message and provides three receivers; it does not contain the answer.

The same limitation applies to the phymode **wire encoding**: the enum is recovered from ioctl name
strings, not from the WMI payload field. **`UNKNOWN`**: whether the vdev-start request sends a
string, an index into that enum, or a bitmask.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| `ath10k_core.ko` exists | **REFUTED** (0 files) |
| all three named WMI identifiers exist in the vendor UMAC | **CONFIRMED** |
| the vdev lifecycle has paired request and response events | **CONFIRMED** (sequence complete) |
| a separate restart request exists for channel change | **CONFIRMED** |
| a channel-specific start sender exists beside the generic one | **CONFIRMED** |
| the phymode enum has directional 40 MHz values | **CONFIRMED** (PLUS / MINUS) |
| 20 / 40 / 80 VHT are all enumerated | **CONFIRMED** |
| the target resource limits | **UNKNOWN / runtime payload** |
| the phymode wire encoding | **UNKNOWN / not recovered** |
| the numeric CMDID values | **UNKNOWN / no id table located** |

## 6. The operational reading

Three things a bench can use:

1. **the bring-up is two-phase** — create, then start on a channel — so a vdev that exists but never
   comes up is a **start** failure, not a create failure, and the start has a response to check;
2. **a channel change uses restart**, not start — so a channel-switch problem should be looked for
   in the restart path;
3. **40 MHz orientation is explicit**, so a "40 MHz but poor throughput" symptom can be checked
   against whether the AP chose PLUS or MINUS relative to the primary — the wrong orientation next
   to a strong neighbour is a real failure mode the enum makes visible.

## 7. Gaps

- **`UNKNOWN`** — the numeric CMDID/EVENTID values; no id table was located.
- **`UNKNOWN`** — the service-ready payload schema and the actual resource limits.
- **`UNKNOWN`** — how phymode is encoded on the wire (string, index, or mask).
- **`UNKNOWN`** — what the three service-ready receivers each do.
- **`UNKNOWN`** — whether the ath10k and vendor sequences differ in shape.
- **Known limit** — a named identifier proves the message exists, not what it carries.
- **Not attempted** — dynamic validation, on-air WMI capture.
