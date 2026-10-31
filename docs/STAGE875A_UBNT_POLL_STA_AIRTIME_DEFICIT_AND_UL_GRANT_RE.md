<!-- doc-head: Stage 875A - there is no per-station airtime deficit and no UL grant vocabulary in ubnt_poll_host, the four airtime hits are all the same multicast cap and the eight txop hits are quality thresholds, and the uplink is governed by rate-ratio error-rate and priority thresholds so the scheduler is admission control rather than fair queuing -->
# Stage 875A — station airtime deficit and UL grants

- **Receipt**: [`artifacts/autoresearch/stage875a_ubnt_poll_sta_airtime_deficit_and_ul_grant_re.json`](../artifacts/autoresearch/stage875a_ubnt_poll_sta_airtime_deficit_and_ul_grant_re.json)
- **Tool**: [`tools/re/dissect_stage875a_ubnt_poll_sta_airtime_deficit_and_ul_grant_re.py`](../tools/re/dissect_stage875a_ubnt_poll_sta_airtime_deficit_and_ul_grant_re.py)
- **Scope**: offline static. No module loaded, no radio contacted, nothing transmitted.

## 0. Both named mechanisms are absent

Across the two AC builds (WA and XC 8.7.25):

| Token | Hits |
| :--- | :-: |
| `deficit` | **0** |
| `drr` | **0** |
| `grant` | **0** |
| `ul_grant` | **0** |
| `quantum` | **0** |
| `round_robin` | **0** |
| `airtime` | 4 |
| `txop` | 8 |

**`REFUTED`**: `deficit_word_hits = 0`, `grant_word_hits = 0`, and the symbol table agrees —
**`scheduler_symbol_count = 0`**. No symbol in either module matches
`airtime|txop|deficit|grant|drr|quantum`.

So there is **no deficit-round-robin scheduler** here, by either the string or the symbol route.

## 1. Every `airtime` hit is the same multicast cap

All four occurrences resolve to one field:

```
ff_mcast_airtime_limit
```

**`CONFIRMED`**: `airtime_is_multicast_cap = 1`, with `multicast_airtime_cap_hits = 4` equal to
`airtime_hits = 4` — every hit, no exceptions.

That field bounds the airtime **multicast** may consume, which protects the unicast traffic behind it.
It is a **global ceiling on one traffic class**, not a per-station running debt.

The word `airtime` is therefore present and means **the opposite** of what the stage assumes.

## 2. Every `txop` hit is a threshold

Both distinct fields are criteria, not allocations:

```
cbp_use_txop_cycle_window        txop_qual_thresh_nr_nb
```

**`CONFIRMED`**: `txop_is_threshold = 1` with `txop_hits = 8`. A TXOP **quality threshold** decides
whether a station may enter a contention window. It is not a grant of airtime to that station.

## 3. What actually governs the uplink

The uplink is controlled by **thresholds and priority**, and the field names state it directly:

```
ul_rate_ratio_thresh_nb     ul_per_thresh_nb
ul_rate_ratio_thresh_nr     ul_per_thresh_nr
sta_priority                high_contention_min_up_dur      up_dur_gap
```

**`CONFIRMED`**: `ul_threshold_fields = 16` — a **rate ratio** and a **packet error rate** threshold,
each in a narrow-band and a normal-rate variant, counted across both modules.

**`CONFIRMED`**: `scheduler_model = "threshold_and_priority"`, `fair_queuing_present = 0`.

A station transmits when its rate ratio and its error rate clear the thresholds **and** its priority
ordering permits. That is **admission control with a priority tie-break**, not fair queuing.

## 4. Why the distinction is not pedantic

A deficit counter exposes **fairness**: an operator can ask who was starved and by how much, because the
debt is a number in memory.

A threshold scheduler exposes **nothing of the kind**. A station below threshold is **not queued at
all**, and no variable anywhere records how long it has been waiting. The quantity simply does not
exist, so it cannot be read, exported, trended or tuned.

Consequently `airtime_deficit_recovered = 0` and `ul_grant_recovered = 0` are **not** failures of this
analysis. They are correct statements about the design, and any tuning procedure built on deficit or
grant quantities would be tuning a mechanism that this scheduler does not implement.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| a per-station airtime deficit exists | **REFUTED** (0 words, 0 symbols) |
| a UL grant mechanism exists by name | **REFUTED** (0) |
| `airtime` appears in the module | **CONFIRMED** (4) |
| and every hit is the multicast cap | **CONFIRMED** (4 of 4) |
| `txop` appears as a quality threshold | **CONFIRMED** (8) |
| the uplink is threshold and priority driven | **CONFIRMED** (`ul_threshold_fields = 16`) |
| fair queuing is implemented | **REFUTED** (`fair_queuing_present = 0`) |
| the actual threshold values | **UNKNOWN / deployment data** |

## 6. The operational reading

For uplink tuning on AC panels, the levers are the **thresholds**, not a fairness weight:

1. `ul_rate_ratio_thresh_nb` / `ul_rate_ratio_thresh_nr` — how much rate advantage a station needs;
2. `ul_per_thresh_nb` / `ul_per_thresh_nr` — how much error a station may show and still be admitted;
3. `sta_priority` — the tie-break when thresholds are met;
4. `ff_mcast_airtime_limit` — the multicast cap that protects unicast.

There is no knob for "give station X more airtime". The equivalent move is to change which stations clear
the thresholds, which is a different intervention with different consequences.

## 7. Gaps

- **`UNKNOWN`** — the numeric values of the four UL thresholds and the priority scale.
- **`UNKNOWN`** — how `sta_priority` is assigned and whether it can be set per peer.
- **`UNKNOWN`** — the contention-window interaction behind `cbp_use_txop_cycle_window`.
- **Known limit** — absence of a name is not absence of the mechanism, but here the symbol table is
  empty for the whole vocabulary, which is stronger evidence than a string miss alone.
- **Not attempted** — dynamic validation, live airtime measurement.
