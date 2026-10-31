<!-- doc-head: Stage 949A synthesis of the mac80211 iTXQ layer, internal fair queue, AQL ownership and the absent ath10k driver into one measured layer table; CONFIRMED_STATIC_BINARY, offline, no radio -->
# Stage 949A - iTXQ, internal fair queue and ath10k: where the boundary actually is

Evidence class: `CONFIRMED_STATIC_BINARY`. `radio_safety: static only`. Scope: static, offline
synthesis. No module was loaded, no radio was contacted, nothing was written to a device.

## Question

Stages 947A and 948A each measured one side of the same boundary. This stage joins them and adds the
one measurement neither made: which module owns the AQL limit fields. The output is a layer table
that says, layer by layer, whether the transmit path is present as a binary artefact in the corpus,
plus a statement of where the mac80211 responsibility ends and where it stops being measurable.

## Inputs

| Input | Present | Used for | Label |
| :--- | ---: | :--- | :--- |
| `stage947a_mac80211_itxq_fq_codel_re.json` | 1 | iTXQ symbol count, fair-queue strings, `tc` census | CONFIRMED |
| `stage948a_ath10k_mac_tx_push_txq_re.json` | 1 | ath10k module count, contract symbol count | CONFIRMED |
| `stage950a_mac80211_aql_txq_limit_re.json` | 1 | presence reference only, never a source of values | CONFIRMED |
| `artifacts/.../after/mac80211.ko` | 1 | recomputed AQL fields, airtime symbols, sizes | CONFIRMED |

The previous AQL receipt is cited by presence and never trusted for a number: the four field counts
in this receipt are recomputed from `mac80211.ko` with sha256
`19a8fde6c6e5efbec3b5b3ddb28399631fc3bba516c5341c8f40e7263124c416`. That choice is deliberate. If
an upstream stage reshapes its receipt, a value copied from it would move this receipt too, and a
synthesis that silently follows its inputs is not reproducible. Label: CONFIRMED.

## The layer table

| Layer | Owner | Artefact expected | Found | Status |
| :--- | :--- | :--- | :--- | :--- |
| L1 nl80211 userspace API | cfg80211 | a cfg80211 module | `cfg80211_rom_241.ko` | MEASURED |
| L2 iTXQ queue core | mac80211 | `mac80211.ko` | 8 iTXQ entry points | MEASURED |
| L3 internal fair queue | mac80211 | `fq_impl.h` inline | `backports-6.12.52/include/net/fq_impl.h` | MEASURED |
| L4 AQL airtime admission | mac80211 | four `aql_*` fields plus `aql_disable` | 4 of 4 fields, symbol present | MEASURED |
| L5 airtime fairness scheduler | mac80211 | airtime accounting symbols | 4 of 4 symbols, 16 string hits | MEASURED |
| L6 driver push side | ath10k | a module with `ath10k_mac_tx_push_txq` | none | ABSENT |
| L7 netdev fq_codel qdisc | net/sched | `sch_fq_codel.ko` | none | ABSENT |
| L8 userspace qdisc tool | iproute2 | a `tc` binary | 8 binaries | MEASURED |

`layers_total = 8`, `layers_measured = 6`, `layers_absent = 2`, and
`measured_plus_absent_equals_total = 1`, so no layer is silently unclassified.

Two absences are the interesting rows and both are measured, not assumed:

- L6 is absent because 1163 `.ko` files were swept four different ways and none is an ath10k module
  (Stage 948A). Label: CONFIRMED.
- L7 is absent because no module in the corpus has `fq_codel` in its name. The corpus does carry
  `sch_codel.ko` and `sch_sfq.ko` separately, which is not the same object as `sch_fq_codel.ko`.
  Label: CONFIRMED for the absence, UNKNOWN for whether the qdisc is built into the kernel.

## The AQL ownership finding, preserved

This is the load-bearing result of the stage and it is stated as it must be stated: mac80211 owns the
AQL limit. The four field names were counted in every module of the corpus.

| Field name | Hits in `mac80211.ko` | Modules carrying it | Non-mac80211 carriers |
| :--- | ---: | ---: | ---: |
| `aql_txq_limit` | 1 | 20 | 0 |
| `aql_threshold` | 1 | 20 | 0 |
| `aql_enable` | 1 | 20 | 0 |
| `aql_pending` | 1 | 20 | 0 |
| `aql_disable` (symbol) | 1 | 20 | 0 |

Reading:

1. Each of the four field names occurs exactly once in the target `mac80211.ko`. They are the four
   AQL knobs, not incidental byte collisions. Label: CONFIRMED.
2. All 20 modules that carry any of the four names are mac80211 builds: the 7 cutover captures under
   `artifacts/canary_panel1_guarida/`, the 7 files directly under
   `firmware/openwrt/pbe5ac_gen2_ptp_kit/`, and the 6 copies in its `public_release*`
   subdirectories. `aql_mac80211_copies = 20`. Label: CONFIRMED.
3. Zero non-mac80211 modules carry any of the four names. `aql_non_mac80211_owners = 0`, so
   `aql_owned_by_mac80211 = 1`. Label: CONFIRMED.
4. `aql_disable` is a defined symbol in mac80211, which places the disable path on the iTXQ layer
   rather than in a driver. Label: CONFIRMED for the symbol, INFERRED for the placement.

The consequence is practical and worth being blunt about: the limit is not in the wireless driver and
not in the firmware interface. A limit applied anywhere else would be a second, different limit. Any
tuning claim about `aql_txq_limit` is a claim about mac80211 state, and it cannot be validated from a
driver-side knob because no driver-side knob exists in the corpus.

## The boundary, documented

| Boundary fact | Value | Label |
| :--- | ---: | :--- |
| mac80211 iTXQ entry points | 8 of 8 | CONFIRMED |
| `ieee80211_tx_dequeue` present | 1 (3528 B body) | CONFIRMED |
| `ieee80211_txq_schedule_start` present | 1 (236 B body) | CONFIRMED |
| driver-side contract symbols present | 0 | CONFIRMED |
| ath10k modules | 0 | CONFIRMED |
| `boundary_documented` | 1 | CONFIRMED |

The measured responsibility split is:

```
  cfg80211            configuration surface, no queue state
  mac80211            queue selection, fair queueing, AQL admission, airtime accounting
  ---------------- driver boundary: wake, then pull one admitted skb ----------------
  ath10k driver       absent from the corpus  (L6)
  firmware            not a kernel module, outside this layer table
  netdev qdisc        absent from the corpus  (L7)
  tc                  present, never references mac80211  (L8)
```

Everything above the driver boundary is measured. The boundary itself is documented from the exported
contract: mac80211 is woken, runs the round, applies AQL and airtime admission, and only then hands an
skb downward. Label: INFERRED for the ordering, CONFIRMED for each symbol, its size and its export
flag.

The two summary flags must be read apart, because collapsing them would overstate the result:

| Flag | Value | Reading | Label |
| :--- | ---: | :--- | :--- |
| `boundary_documented` | 1 | the mac80211 side of the boundary is fully measured | CONFIRMED |
| `interaction_recovered` | 0 | the iTXQ to ath10k interaction was **not** recovered, because the driver half is not in the corpus | CONFIRMED |

`interaction_recovered` is 0 by construction: it requires both sides of the interaction to exist, and
`ath10k_modules = 0`. The stage is honest about a one-sided result rather than promoting a documented
interface into a measured interaction.

## Why this matters for the queue question

Three consequences follow, and each is labelled:

1. There is exactly one fair queue under measurement and it lives inside mac80211 (L3). The netdev
   `fq_codel` qdisc module does not exist in the corpus (L7), so it cannot be the thing that is
   shaping traffic on a box built from these artefacts. Label: CONFIRMED.
2. `tc` cannot be a prerequisite for the internal queue, because it never references mac80211 and it
   operates on netdev qdiscs while mac80211 operates on `fq_tin` state. Label: CONFIRMED.
3. Whether the internal queue is active and how deep it runs on a live radio is unmeasured. Nothing
   in this table says the feature is enabled, only that the code is present and reachable. Label:
   UNKNOWN.

## Verdicts

| ID | Claim | Label |
| :--- | :--- | :--- |
| C1 | 8 layers, 6 present as binary artefacts, 2 absent | CONFIRMED |
| C2 | mac80211 owns the AQL limit; zero non-mac80211 carriers of the four field names | CONFIRMED |
| C3 | the driver push layer is absent from 1163 modules | CONFIRMED |
| C4 | there is no netdev `fq_codel` qdisc module in the corpus | CONFIRMED |
| C5 | the iTXQ to ath10k interaction is not recovered (`interaction_recovered = 0`) while the mac80211 boundary is documented | CONFIRMED |
| C6 | a driver with a `wake_tx_queue` op would receive skbs already admitted by AQL | INFERRED |
| C7 | the runtime queue state, pulls per round, and firmware handoff | UNKNOWN |
| C8 | the AQL limit is enforced by the wireless driver or by firmware | REFUTED (both are absent) |

## Gaps

- This is a synthesis. The only new measurement is the AQL ownership census; the rest is read from
  the 947A and 948A receipts.
- The driver push layer is absent, so the real push loop, its ring depth and its firmware handoff
  cannot be described, and `interaction_recovered` is 0 for that reason.
- Presence of the internal fair queue does not prove the queue is active on a running radio.
- No disassembly in this stage, so the layer ordering is read from the exported contract.
- Whether `fq_codel` is built into the kernel cannot be decided from a module census.
- The previous AQL receipt is cited by presence only, so this stage does not detect a divergence
  between that receipt and the module if one ever appears.
- The firmware boundary is not a kernel module and is outside this layer table entirely.
- No dynamic validation. Nothing was loaded and no radio was contacted.

## Files

- `tools/re/dissect_stage949a_itxq_ath10k_interaction_re.py`
- `artifacts/autoresearch/stage949a_itxq_ath10k_interaction_re.json`
- `docs/STAGE949A_ITXQ_ATH10K_INTERACTION_RE.md`
