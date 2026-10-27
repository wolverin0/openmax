<!-- doc-head: STAGE374A_UBNT_AIRSELECT_STATE_MACHINE_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 374A — AirSelect frequency-hop state machine

- **Receipt**: [`artifacts/autoresearch/stage374a_ubnt_airselect_state_machine_re.json`](../artifacts/autoresearch/stage374a_ubnt_airselect_state_machine_re.json)
- **Tool**: [`tools/re/ubnt_airselect_and_freq_hop_state_machine_re.py`](../tools/re/ubnt_airselect_and_freq_hop_state_machine_re.py)
- **Scope**: offline static. No module loaded, no radio contacted, nothing hopped.

## 0. Two structural facts before the analysis

**XW has no `ubnt_poll_host.ko`.** The 2.6.32.71 module tree ships **`ubnt_poll.ko`**,
529,284 bytes. That is 2.79× the AC module. A "WA/XC/XW" comparison that pretends the same file
exists on all three would be wrong from the first line, so the receipt records
`xw_expected_module.exists = false` as its own field.

**`ubnt_poll_host.ko` has no AirSelect vocabulary.** Zero hits for `airselect`, `hop_interval`,
`hopint`, `hop`, `dwell`, `announce`, `chanchange`, `athselect` — in **both** AC images. Not one
token.

| Module | Bytes | AirSelect tokens |
| :--- | :-: | :-: |
| `WA.v8.7.25:ubnt_poll_host.ko` | 189,880 | **none** |
| `XC.v8.7.25:ubnt_poll_host.ko` | 189,880 | **none** |
| `XW.v6.3.6:ubnt_poll.ko` | 529,284 | **14 token classes** |

## 1. The feature is there on XW — under the name `fh`

The vocabulary the stage asked for does not exist as `airselect*`. On XW the mechanism is
implemented as **`fh` (frequency hopping)**:

| Token | Hits | What it names |
| :--- | :-: | :--- |
| `fh_` | **15** | the field family |
| `fh_list` | 1 | the allowed-frequency list |
| `fh_hops` | 1 | hop counter |
| `fh_retries` | 1 | retry counter |
| `fh_time` | 1 | hop timing field |
| `fh_announce_cnt` | 1 | **announce count** |
| `tx_sync_master` | 1 | the AP side of the sync pair |
| `tx_sync_mode` | 1 | sync mode selector |
| `chanidx` | 1 | channel index |
| `hopping to chanidx` | 1 | hop log site |
| `failed hop to freq` | 1 | failed-hop log site |
| `channel change announce` | 1 | announcement log site |

**`CONFIRMED`**: `fh_list`, `fh_hops`, `fh_retries`, `fh_time` and `fh_announce_cnt` are real
field names in `ubnt_poll.ko`. **`CONFIRMED`**: three log sites exist for the hop itself, the
failed hop, and the channel-change announcement.

Note the direct correspondence with the shipped knobs: the help page calls them **Frequency
List**, **Announce Count** and **Hop Interval**; the binary calls them `fh_list`,
`fh_announce_cnt` and `fh_time`. That is a name-to-name match, not an inference.

The hop log line is worth quoting because it shows the decision carries a **penalty**:

```
%s: hopping to chanidx %d freq %d penalty %d
%s failed hop to freq %u (flags %08x). Channel not found
ubnt_poll: STA Drop channel change announce RX from %pM when not associated
```

**`CONFIRMED`**: channel selection is scored (`penalty`), the hop can fail with flags, and a
station refuses an announcement when it is not associated. Those are three distinct behaviours of
a real state machine.

**`CONFIRMED`**: `tx_sync_master` / `tx_sync_mode` / `tx_sync_udp_port` sit beside the `fh_`
fields, which is the coordination channel the stage describes — the AP announces, the CPE
follows.

## 2. The documented contract, from the shipped help pages

| Knob | Documented meaning | Value |
| :--- | :--- | :--- |
| **Hop Interval** | how long the AP stays on one frequency | **3000 ms default** |
| **Announce Count** | announcements sent between hops | e.g. 10000 ms ÷ 10 = **every 1000 ms** |
| **Frequency List** | user-selected frequencies | device-dependent |

**`CONFIRMED`**: `airSelect` hoppea "to the least used channel in the Frequency List within a
designated time interval", and it "tracks interference levels on each channel, hopping more
frequently to those with interference".

The announce arithmetic is explicit in the help text: with a 10,000 ms interval and an announce
count of 10, the AP sends an announcement **every 1000 ms**. That is `hop_interval /
announce_count`, and it is the only timing relationship the shipped documentation states.

## 3. Where the vocabulary does appear in userspace

One carrier in the binary directories: **`lib/tinysnmp/ubnt.so`**, `airselect` ×1. That is the
SNMP MIB binding, not the state machine.

**`CONFIRMED`**: no binary under `usr/bin` or `usr/sbin` contains the literal `airselect` or
`hopint`. The knob labels exist in the web help pages and in the translation JSONs; the
implementation is reached through configuration keys rather than a named executable.

## 4. What is established

| Claim | Status |
| :--- | :--- |
| XW ships `ubnt_poll.ko`, not `ubnt_poll_host.ko` | **CONFIRMED** |
| `ubnt_poll_host.ko` (WA/XC) has zero AirSelect vocabulary | **CONFIRMED** |
| XW `ubnt_poll.ko` implements it as `fh_*` with list, hops, retries, time, announce count | **CONFIRMED** |
| hop selection is penalty-scored and can fail with flags | **CONFIRMED** |
| a station drops announcements when unassociated | **CONFIRMED** |
| default hop interval is 3000 ms and announcements divide the interval | **CONFIRMED** (documentation) |
| the state machine exists on the AC line under another name | **UNKNOWN** — not found in the polling module |
| the transition graph (states, guards, timers) | **UNKNOWN / not decoded** |

## 5. The asymmetry that matters operationally

AirSelect is documented as an **AP** feature. The two AP images in this park are AC
(`WA`/`XC`), and their polling module has **no** frequency-hopping vocabulary at all, while the
M5 image — historically the CPE/backhaul line — carries the full `fh_*` surface.

Two readings, neither claimed:

1. on airOS 8 AC the function moved elsewhere (userspace daemon, or a different module), and the
   `ubnt_poll_host.ko` name is simply not where it lives;
2. AirSelect is deprecated on the AC line in favour of airMAX/ac channel handling, and the code
   only survives on M5.

Reading 1 is testable by sweeping every AC module and binary for `fh_hops`. Reading 2 is testable
from the AC web UI: if the AirSelect menu is absent there, the feature is gone.

## 6. Gaps

- **`UNKNOWN`** — where AirSelect lives on WA/XC, if anywhere.
- **`UNKNOWN`** — the hop timer value in code; 3000 ms is the documented default, not a decoded
  constant.
- **`UNKNOWN`** — the penalty function used to rank candidates.
- **`UNKNOWN`** — the announcement schedule implementation (`fh_announce_cnt` semantics in code).
- **`UNKNOWN`** — the `flags` bits reported by a failed hop.
- **Known limit** — located is not decoded. Field names and log sites prove the machinery exists;
  they do not give its transition graph.
- **Not attempted** — dynamic validation.
