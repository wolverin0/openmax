<!-- doc-head: STAGE485A_QCA988X_BMISS_AND_CSA_CHANNEL_SWITCH_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 485A — beacon-miss thresholds, Roam and CSA channel switch

- **Receipt**: [`artifacts/autoresearch/stage485a_qca988x_bmiss_and_csa_channel_switch_re.json`](../artifacts/autoresearch/stage485a_qca988x_bmiss_and_csa_channel_switch_re.json)
- **Tool**: [`tools/re/build_stage485a_qca988x_bmiss_and_csa_channel_switch_re.py`](../tools/re/build_stage485a_qca988x_bmiss_and_csa_channel_switch_re.py)
- **Scope**: offline static. No firmware loaded, no module loaded, no radio contacted.

## 0. The firmware images are absent

`firmware-2.bin` **0**, `firmware-5.bin` **0**. Fifth stage in this series to hit the same wall.
All evidence below is from `umac.ko` (WA and XC, identical counts).

## 1. bmiss is a **software** timer, not a counter

The vocabulary is dense — `bmiss` **36**, `BMISS` **2**, `beacon_miss` **4**, and **20 distinct
symbols** — but the shape of the mechanism is the opposite of what the stage assumes.

```
ieee80211_mlme_sta_swbmiss_timer_alloc_id
ieee80211_mlme_sta_swbmiss_timer_enable
ieee80211_mlme_sta_swbmiss_timer_disable
ieee80211_mlme_sta_swbmiss_timer_free_id
ieee80211_mlme_sta_swbmiss_timer_print_status
```

**`CONFIRMED`**: **`swbmiss` = software beacon miss**, and it is a **timer with a full lifecycle** —
allocate an id, enable, disable, free an id, print status. **14** of the 20 bmiss symbols carry
`swbmiss`.

That is a materially different design from a counter that increments per missed beacon: the driver
**arms a timer** and lets it fire. The threshold is the timer's arming argument.

Related symbols complete the picture:

```
ieee80211_mlme_reset_bmiss        ieee80211_mlme_sta_bmiss_ind
ieee80211_vap_iter_beacon_miss    osif_beacon_miss
ieee80211_beacon_miss
```

**`CONFIRMED`**: there is a **reset** path, an **indication** path, and a per-VAP iterator — the
three pieces a state machine needs.

## 2. CSA has **three** variants, not one

The log strings separate them explicitly:

```
%s: CSA new channel = %d, echie=%p, secoffsie=%p, wideie=%p
%s: E-CSA new channel = %d
%s: UCSA new channel = %d, center1 = %d, width = %d
```

| Variant | Meaning | Present |
| :--- | :--- | :-: |
| **CSA** | classic 802.11h Channel Switch Announcement | **yes** |
| **E-CSA** | extended CSA, carries bandwidth/secondary-offset | **yes** |
| **UCSA** | **Ubiquiti's own** CSA, carries `center1` and `width` | **yes** |

**`CONFIRMED`**: all three are distinguished, and UCSA is a **vendor extension** that carries
80 MHz centre-frequency and width fields — which is exactly what a wide-channel airMAX AP needs and
what plain 802.11h cannot express.

The symbol table confirms it (16 CSA symbols):

```
ieee80211_process_csa_ecsa_ie      ieee80211_add_ubnt_csa
ieee80211_scan_entry_ubntcsa       ieee80211_scan_entry_csa
ieee80211_scan_entry_xcsa          ieee80211_start_csa
ieee80211_vap_request_csa          ieee80211_mlme_recv_csa
ieee80211_mlme_chanswitch_continue ieee80211_ioctl_chanswitch
```

**`CONFIRMED`**: the switch is **received** (`recv_csa`), **continued** (`chanswitch_continue`),
**started** (`start_csa`) and **requested** (`vap_request_csa`) — four distinct phases, which is a
state machine by any reasonable definition.

The WMI boundary is also present:

```
wmi_unified_vdev_chan_switch_send
wmi_unified_chan_switch_handler
```

`CONFIRMED`: the host sends the switch and the target handles it — both directions.

## 3. Roam is a timer inside the connection state machine

```
ieee80211_connection_sm_*
connection_sm_roam_check_timer_handler
connection_sm_timer_handler
wmi_unified_roam_event_handler
```

**`CONFIRMED`**: roam is not a standalone machine — it is a **roam-check timer** inside the broader
`connection_sm`, with the target reporting roam events back over WMI.

**14** distinct roam symbols. **`UNKNOWN`**: the roam decision rule (RSSI threshold? bmiss count?
candidate list order).

## 4. `WMI_VDEV_PARAM_BMISS_COUNT_MAX` does not exist

| Token | Hits |
| :--- | :-: |
| `WMI_VDEV_PARAM` | **0** |
| `VDEV_PARAM` | **0** |
| `BMISS_COUNT_MAX` | **0** |
| `max_bmiss` | **0** |

**`REFUTED`**: the parameter name is a macro, exactly as in Stage 437A (`PDEV_PARAM`) and Stage
451A (`PDEV` vs `VDEV` command names). `wmi_param_name_hits = 0`.

**Consequence:** the bmiss **maximum count** cannot be read by name. It is a numeric argument to
`swbmiss_timer_alloc_id` or `_enable`, and that argument was not traced.
`bmiss_threshold_recovered = 0`.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| `firmware-2.bin` / `firmware-5.bin` exist | **REFUTED** (0 files) |
| bmiss is implemented as a software timer with a lifecycle | **CONFIRMED** (14 symbols) |
| a bmiss reset and indication path exist | **CONFIRMED** |
| CSA exists in **three** variants including a Ubiquiti extension | **CONFIRMED** |
| the switch has recv / continue / start / request phases | **CONFIRMED** |
| the WMI switch send **and** handler both exist | **CONFIRMED** |
| roam is a timer inside `connection_sm` | **CONFIRMED** (14 symbols) |
| `WMI_VDEV_PARAM_BMISS_COUNT_MAX` exists as a string | **REFUTED** |
| the bmiss threshold **value** | **UNKNOWN / not traced** |
| the CSA announce/dwell/switch timing | **UNKNOWN / not decoded** |

## 6. Why the distinction matters operationally

A timer-based bmiss behaves differently from a counter-based one under packet loss: a counter
degrades smoothly, a timer fires on a **duration**. If a station is briefly starved but still in
range, the timer will kick it at `T` regardless of how many beacons were missed in between.

That makes the arming value the single most important number in the mechanism — and it is the one
number this stage could not recover.

## 7. Gaps

- **`UNKNOWN`** — the swbmiss timer arming value and its units.
- **`UNKNOWN`** — whether the threshold is per-VAP or per-station.
- **`UNKNOWN`** — the CSA announce count, dwell time and switch instant.
- **`UNKNOWN`** — whether UCSA is honoured by stock airOS 8 CPEs; that is an interop question, not
  a static one.
- **`UNKNOWN`** — the roam decision rule.
- **Known limit** — a named lifecycle proves a timer exists, not when it fires.
- **Not attempted** — dynamic validation, on-air CSA.
