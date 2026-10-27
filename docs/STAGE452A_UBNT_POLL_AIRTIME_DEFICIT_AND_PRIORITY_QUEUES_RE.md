<!-- doc-head: STAGE452A_UBNT_POLL_AIRTIME_DEFICIT_AND_PRIORITY_QUEUES_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 452A — airtime deficit, WMM weights and low-MCS penalization in `ubnt_poll_host.ko`

- **Receipt**: [`artifacts/autoresearch/stage452a_ubnt_poll_airtime_deficit_and_priority_queues_re.json`](../artifacts/autoresearch/stage452a_ubnt_poll_airtime_deficit_and_priority_queues_re.json)
- **Tool**: [`tools/re/build_stage452a_ubnt_poll_airtime_deficit_and_priority_queues_re.py`](../tools/re/build_stage452a_ubnt_poll_airtime_deficit_and_priority_queues_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Three vocabularies, all absent

Both images are identical in size (189,880 bytes) and identical in every count below.

| Vocabulary | Tokens probed | Hits |
| :--- | :--- | :-: |
| **deficit accounting** | `deficit`, `quantum`, `credit`, `surplus` | **0** |
| **WMM access categories** | `wmm`, `WMM`, `AC_BE`, `AC_VI`, `AC_VO`, `AC_BK` (and lower-case) | **0** |
| **penalization** | `penal`, `punish`, `starve`, `low_mcs`, `mcs`, `weight` | **0** |

**`REFUTED`**: there is **no per-CPE airtime deficit counter**, **no 4-AC weight table** and **no
low-MCS penalty term** in this module. The stage's three mechanisms are all absent by name.

That is a strong negative, and it is worth stating precisely: a weighted fair-queueing scheduler
implemented with deficits would need a field called something like `deficit` or the arithmetic
`deficit += quantum`. Neither the word nor the AC names exist.

## 1. `airtime` is multicast, not per-station

| Token | Hits | What it actually is |
| :--- | :-: | :--- |
| `airtime` | 2 | **`ff_mcast_airtime_limit`** |

The two hits sit in the sysctl description block:

```
cms_bias   voip_bias   ff_cap_rep   ff_mcast_airtime_limit   daprot
```

**`REFUTED`**: `airtime` here bounds **multicast** airtime (`ff_mcast_airtime_limit`), a single
global cap. It is not a per-CPE quantum and it is not part of a deficit loop.

## 2. `BE` is not an access category — it is `PROBE`

| Token | Hits | Where |
| :--- | :-: | :--- |
| `BE` | 3 | all three inside `PROBE` / `NEXT-PROBE` |

The containing line is the rate-control debug output:

```
NOACK mode RATE CTRL DATA
RIX: %d  PROBE-RIX: %d  NCPC: %d  OVERALL-PER: %d
LAST-CHECK: %d  LAST-CHANGE: %d  LAST-PROBE: %d  NEXT-PROBE: %d
RATE-%d: %d
```

**`REFUTED`**: `BE` appears **3 times and every one is a substring of `PROBE`**. `VI`, `VO` and
`BK` have **0** hits. A two-letter access-category search in a binary is exactly the kind of probe
that produces false positives, and this is the second stage in a row where a short token had to be
disqualified by context (cf. `LQ` in 438A).

## 3. What *is* there: a per-station priority surface

| Knob | Hits | Meaning |
| :--- | :-: | :--- |
| `sta_priority` | 3 | per-station priority field |
| `prio` | 6 | the same, plus two log sites |
| **`ubnt_poll_host_set_sta_priority`** | symbol | the setter |
| **`ubnt_poll_host_set_ap_sta_priority`** | symbol | the **AP-forced** setter |

Log sites:

```
ubnt-poll-host: [%s] AP forcing priority for %02X:%02X:%02X:%02X:%02X:%02X to %d
ubnt-poll-host: [%s] Station priority configured to %d (no-auto=%d)
```

**`CONFIRMED`**: there is a **per-station priority** that the AP can **force**, with an explicit
`no-auto` flag distinguishing a manual assignment from an automatic one. That is a real
prioritisation mechanism — just not a WMM-AC weight table.

## 4. The nearest thing to a penalty threshold

The same sysctl region exposes the frame and radio knobs:

| Knob | Role |
| :--- | :--- |
| **`ff_sta_rx_rssi_th`** | station RX RSSI threshold — the only per-station gate |
| `ff_unit_shift`, `ff_guard_units` | frame-unit geometry |
| `dack_arbit_max` | downstream ACK arbitration cap |
| `daprot` | DAPR (TDMA) protocol selector |
| `cms_bias`, `voip_bias` | bias terms |
| `ff_cap_rep` | capacity report flag |

**`CONFIRMED`**: `ff_sta_rx_rssi_th` is a **per-station RSSI threshold**, and it is the closest
mechanism in the module to "penalize a weak station". **`UNKNOWN`**: what it gates — admission,
rate selection, or scheduling share. It is a threshold, not a weight.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| a per-CPE airtime deficit counter exists | **REFUTED** (0 tokens) |
| a 4-AC WMM weight table exists | **REFUTED** (0 tokens) |
| a low-MCS penalization term exists | **REFUTED** (0 tokens) |
| `airtime` is per-station | **REFUTED** (`ff_mcast_airtime_limit`) |
| `BE` is an access category | **REFUTED** (all three hits are `PROBE`) |
| per-station priority exists and the AP can force it | **CONFIRMED** |
| a per-station RSSI threshold exists | **CONFIRMED** (`ff_sta_rx_rssi_th`) |
| WA and XC differ in any of this | **REFUTED** (identical counts, identical size) |

## 6. Why this matters operationally

The stage's model was "weighted queues with deficit accounting". The module's model is
**priority plus thresholds**: a station is assigned (or forced to) a priority, and a weak station
crosses an RSSI threshold. There is no quantum, no credit, no AC weight.

That distinction is testable on the bench. If a park is trying to equalise airtime between a
strong and a weak CPE, **there is no knob in `ubnt_poll_host.ko` that does it by weight** — the
available levers are `sta_priority` and `ff_sta_rx_rssi_th`. Reaching for a "WMM weight" that does
not exist would waste a test window.

## 7. Gaps

- **`UNKNOWN`** — what `ff_sta_rx_rssi_th` gates, and its units (dBm vs a raw register scale).
- **`UNKNOWN`** — the priority value range and whether it maps to a WMM AC at all.
- **`UNKNOWN`** — the `daprot` protocol enumeration.
- **`UNKNOWN`** — how `dack_arbit_max` interacts with priority.
- **`UNKNOWN`** — whether deficit accounting exists in `umac.ko` or `ath_dev.ko` instead; this
  stage only covers `ubnt_poll_host.ko`.
- **Known limit** — absent by name is not absent by arithmetic; a deficit could be an unnamed
  integer field.
- **Not attempted** — dynamic validation.
