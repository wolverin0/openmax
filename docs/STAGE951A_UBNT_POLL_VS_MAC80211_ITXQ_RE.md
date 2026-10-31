<!-- doc-head: Stage 951A - explicit two-column comparison of the airOS TDMA slot model against the mac80211 iTXQ fair-queue model, with the non-comparable boundary stated, static only -->
# Stage 951A - airOS TDMA slot model against mac80211 iTXQ

This stage synthesises Stage 950A. It reads one static receipt, derives which layers of each stack
actually exist in the corpus, and puts the two queueing models in one matrix with an explicit
comparability flag per row.

- Provenance: `CONFIRMED_STATIC_BINARY`
- Radio safety: `static only`. No radio contacted, no device written, no module loaded.
- Receipt: `artifacts/autoresearch/stage951a_ubnt_poll_vs_mac80211_itxq_re.json`
- Script: `tools/re/dissect_stage951a_ubnt_poll_vs_mac80211_itxq_re.py`
- Input: `artifacts/autoresearch/stage950a_ubnt_poll_host_queues_re.json` (hash recorded in the receipt)

Headline: `divergence_count = 11` of 11 dimensions, `shared_vocabulary = ["txq"]` only,
`equivalence_claimed = 0`. The models are not comparable as queue implementations, and the reason is
structural rather than a matter of detail: one side keeps the queue inside the module under
inspection, the other keeps it outside.

## 1. Layer accounting

Six layers were defined in advance, and each one's presence is derived from a filename or blob probe
rather than assumed. The counts reconcile: 2 measured + 1 absent + 3 present but unmeasured = 6.

| Layer | Side | Artifact | State | Evidence |
| :--- | :--- | :--- | :--- | :--- |
| L1 host policy module | airOS | `ubnt_poll_host.ko` | measured | 2 modules hashed in 950A, 0 queue-API imports |
| L2 vendor driver | airOS | `umac.ko`, `ath_dev.ko` | present, unmeasured | 9 copies of each in the corpus |
| L3 radio firmware | airOS | AR9888v2 SGMT blob | present, unmeasured | 33 `.bin` files contain `UBNT_POLL_MEM_ALLOC` |
| L4 mac80211 iTXQ | mac80211 | `mac80211.ko` | measured | 3 of 3 iTXQ entry points defined |
| L5 driver bridge | mac80211 | `ath10k_core.ko` | absent | 0 `ath10k_core.ko`, 0 `ath10k_pci.ko` |
| L6 qdisc layer | mac80211 | `sch_fq_codel.ko` | present, unmeasured | 0 modules, but 6 `tc` binaries contain `fq_codel` |

`layers_total = 6`, `layers_measured = 2`, `layers_absent = 1`, `layers_present_not_measured = 3`.

CONFIRMED: the airOS queue owner is not L1. UNKNOWN: whether it is L2 or L3, because neither was
measured in this stage. L5 is absent as a module only, so built-in kernel linkage is not excluded and
the layer records that caveat explicitly.

## 2. Two-column comparison

`comparable = 1` means both sides hold a measured value for that dimension. `divergence = 1` means the
mechanisms differ. Rows where one side has no measured counterpart are non-comparable by definition,
and are not filled with an ath10k mechanism that was not observed in this corpus.

| # | Dimension | airOS TDMA slot | mac80211 iTXQ | Comp | Div |
| :--- | :--- | :--- | :--- | ---: | ---: |
| M1 | queue ownership | not in module (0 queue imports) | in module (3 of 3 iTXQ symbols) | 1 | 1 |
| M2 | enqueue site | WMI command emission to firmware | in-module iTXQ enqueue, skb primitives | 1 | 1 |
| M3 | dequeue pull | absent, no dequeue token or import | `ieee80211_tx_dequeue` defined | 0 | 1 |
| M4 | admission control | absent, no `may_transmit`, no AQL vocabulary | `ieee80211_txq_may_transmit` defined | 0 | 1 |
| M5 | fairness unit | per-station `sta_priority` sysctl | per-TID flow queue, header-inline | 1 | 1 |
| M6 | time-slot geometry | 10 of 10 geometry fields, 8 slot tokens | absent, no duration or guard field | 0 | 1 |
| M7 | aggregation budget | CBP slot budget: `ff_cbp_s`, `ff_cbp_slots` | absent | 0 | 1 |
| M8 | power-control coupling | ATPC target, max and min power | absent | 0 | 1 |
| M9 | station state | station list plus deferred list | node plus per-TID txq flows | 1 | 1 |
| M10 | fairness vocabulary | fair 0, codel 0, deficit 0 | fair queue inline, codel word 0, quantum and flows present | 1 | 1 |
| M11 | code provenance | proprietary vendor module | in-tree mac80211, exports pull and admission | 1 | 1 |

`dimensions_total = 11`, `dimensions_comparable = 6`, `dimensions_non_comparable = 5`,
`divergence_count = 11`.

CONFIRMED: no row is both comparable and non-divergent, which is why `equivalence_claimed` is computed
as 0 rather than asserted as 0.

## 3. Shared vocabulary

`shared_vocabulary = ["txq"]`. Out of 19 mechanism nouns checked (`queue`, `dequeue`, `enqueue`,
`txq`, `flow`, `flows`, `fair`, `codel`, `deficit`, `quantum`, `slot`, `tdma`, `airtime`, `admission`,
`transmit`, `sched`, `priority`, `budget`, `requeue`), exactly one appears in the API symbol names on
both sides.

That single shared term is a false friend. On the airOS side `txq` exists only as
`ubnt_poll_host_set_txq_param` and `ubnt_poll_host_get_txq_param`, which are a parameter getter and
setter pair on a character device. On the mac80211 side `txq` denotes a queue object that is dequeued
by `ieee80211_tx_dequeue` and admitted by `ieee80211_txq_may_transmit`. The word is shared; the object
is not.

For transparency the receipt also records `shared_tokens_all` (the unrestricted identifier
intersection, which includes generic code words taken from kernel helpers mac80211 imports and the
airOS module does not). That broader set is noise by construction and is not the headline measure.

## 4. Where the two cannot be compared

`boundary_documented = 1`. The boundary is not a disclaimer, it is the finding:

1. **No common object.** On the mac80211 side the queue is inside the module being inspected. On the
   airOS side it is outside it. A symbol-level queue comparison therefore has nothing to compare.
2. **Five of eleven dimensions have one empty side** (M3, M4, M6, M7, M8). They are marked
   non-comparable rather than resolved by importing knowledge of ath10k that this corpus does not
   contain.
3. **Header-inline asymmetry.** The mac80211 fair-queue internals are compiled inline, so a symbol
   census understates them. The airOS side has no equivalent code to understate, so a symbol census
   flatters the comparison in one direction only.
4. **Different quantities.** CBP slot duration and guard units are not airtime credit. An equivalence
   claim about airtime control would be comparing a slot schedule with an airtime limit.
5. **Different authority placement.** The airOS module emits WMI commands and imports no queue
   primitive; mac80211 exports both the pull and the admission API. Scheduling authority sits below the
   host module on one side and inside the host stack on the other. This is INFERRED from placement
   evidence, not from reading either implementation.
6. **No dynamic measurement.** Both stages read static binaries. No queue depth, drain rate, latency
   or fairness outcome was observed on either stack, so no performance equivalence or non-equivalence
   is established here.

## 5. What the comparison does establish

- CONFIRMED: the premise that `ubnt_poll_host.ko` manages per-station queues is REFUTED. The module
  imports no queue, skb or netif primitive at all.
- CONFIRMED: the module is a slot and frame-geometry scheduler that delegates queueing. It owns frame
  duration, guard, allocation, CBP slot budget, per-station priority, ATPC targets and UL thresholds.
- CONFIRMED: the mac80211 iTXQ pull model is present in the corpus and is structurally different, not
  merely differently named.
- INFERRED: the airOS design intent is to keep MAC scheduling authority out of the host module, in the
  vendor driver or the radio firmware. This matches the earlier finding that airMAX polling code runs
  on the QCA988x Xtensa core, but that finding is not re-measured in this stage.
- UNKNOWN: the actual arbitration rule that decides which station gets the next slot, and whether the
  airOS slot model could be reproduced on mac80211 iTXQ. Both need L2 or L3 measured.

## 6. Claims ledger

| ID | Label | Claim |
| :--- | :--- | :--- |
| C1 | CONFIRMED | the airOS host module does not own the per-station queue |
| C2 | CONFIRMED | the mac80211 side owns its queue inside the module |
| C3 | CONFIRMED | the models diverge on every measured dimension |
| C4 | CONFIRMED | the shared vocabulary is generic naming, not shared mechanism |
| C5 | CONFIRMED | five of six layers exist somewhere in the corpus |
| C6 | UNKNOWN | how the airOS stack arbitrates between two stations in practice |
| C7 | UNKNOWN | whether the airOS slot model can be reproduced on mac80211 iTXQ |
| C8 | REFUTED | `ubnt_poll_host.ko` and mac80211 iTXQ are equivalent queue models |
| C9 | INFERRED | airOS places scheduling authority below the host module, mac80211 inside it |

## 7. Gaps

- L2 and L3 are present but unmeasured, so the airOS queue owner is bounded to "not L1" and not
  positively identified. This is the single largest remaining gap in the comparison.
- L5 and L6 are absent only as modules. Built-in kernel linkage or a userspace `tc` qdisc cannot be
  excluded by a module-file probe, and the receipt flags that per layer.
- The mac80211 fair-queue internals are header-inline and were not disassembled, so M10 rests on
  string and symbol evidence rather than on recovered arithmetic.
- No dynamic measurement on either stack, so no latency or fairness claim is supported.
- AQL material sits in a sibling stage that shares the 950A identifier and is deliberately not merged
  here, so the airtime-accounting dimension is omitted rather than guessed.
- Coverage is WA and XC 8.7.25 against one `mac80211.ko` build. Cross-version generalisation is
  unproven.
