<!-- doc-head: Stage 951A - the interaction splits into four layers of which two are measured and two are not, with mac80211 owning the iTXQ fair queue and the AQL limit while the driver push and HTT transmit paths are absent from the corpus, so the handoff is documented from one side only and interaction_recovered stays zero -->
# Stage 951A — the iTXQ and AQL boundary

- **Receipt**: [`artifacts/autoresearch/stage951a_itxq_aql_interaction_re.json`](../artifacts/autoresearch/stage951a_itxq_aql_interaction_re.json)
- **Tool**: [`tools/re/dissect_stage951a_itxq_aql_interaction_re.py`](../tools/re/dissect_stage951a_itxq_aql_interaction_re.py)
- **Scope**: offline static synthesis. Reads four receipts, no binary read, no radio contacted.

## 0. Result

```
layers=4  measured=2  absent=2  itxq=8  aql_fields=8  ath10k=0
interaction_recovered=0  boundary_documented=1
```

This stage reads no binary. Its deliverable is the **boundary table**: a precise statement of where the
evidence stops.

## 1. The four layers

| Layer | Evidence | State | Content |
| :--- | :--- | :--- | :--- |
| **mac80211 iTXQ** | 947A | **measured** | 8 of 8 symbols, FQ header-inline |
| **mac80211 AQL** | 950A | **measured** | 8 fields, `aql_disable` symbol |
| **driver push** | 948A | **absent** | 0 ath10k modules |
| **driver HTT TX** | 949A | **partial** | no source, but 80 HTT strings in `umac.ko` |

**`CONFIRMED`**: `layers_measured = 2`, `layers_absent = 2` (counting `partial` as not measured).

Two layers are documented from binaries. One (the HTT path) has naming evidence but no implementation.
One (the driver push) has nothing at all.

## 2. The inversion this batch produced

The stage assumed the interaction flows from an ath10k mechanism into mac80211's queueing. The
measurements put both **mechanisms** on the mac80211 side:

- the fair queue is mac80211's (`ieee80211_txq_setup_flows` plus the `fq_` / `flows` / `quantum`
  strings);
- the AQL limit and its disable switch are mac80211's (`aql_txq_limit`, `aql_disable`).

So the driver, when it exists, is a **consumer** that calls `ieee80211_tx_dequeue` and reports airtime
back through `ieee80211_sta_update_pending_airtime`. It is not the owner of the limit.

**`CONFIRMED`**: `boundary_documented = 1` — the direction of the dependency is established from the two
measured layers, even though the consumer is missing.

## 3. What is explicitly not claimed

**`REFUTED`**: `interaction_recovered = 0`.

Nothing in this batch shows:

- which ath10k function calls `ieee80211_tx_dequeue`;
- whether the AQL threshold is compared before or after dequeue;
- whether the limit is per station or per TID;
- what happens to a TXQ that is held by the limit.

Each of those needs the absent module or a running system. The layer table exists so that nobody has to
re-derive which of them is missing and why.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| mac80211 owns the iTXQ fair queue | **CONFIRMED** (947A) |
| mac80211 owns the AQL limit and switch | **CONFIRMED** (950A) |
| the driver layer is present in the corpus | **REFUTED** (0 modules) |
| the HTT path has no implementation here | **REFUTED** (partial: naming only) |
| the dependency direction is established | **CONFIRMED** |
| the end-to-end interaction is traced | **REFUTED** (`interaction_recovered = 0`) |

## 5. The operational reading

1. **Tune the stack, not a vendor module.** On this image the queue discipline and the airtime limit are
   mac80211's, and the ath10k module is not even shipped.
2. **A partial layer must stay labelled partial.** The 80 HTT strings in `umac.ko` are real evidence that
   the vendor driver speaks HTT, and they are not evidence of what it sends.
3. **The boundary table is the reusable artefact.** When an ath10k module appears, only the bottom two
   rows change, and the answer to "what is still missing" is one lookup.

## 6. Gaps

- **`UNKNOWN`** — everything on the driver side of the handoff.
- **`UNKNOWN`** — the comparison point of the AQL threshold inside the stack.
- **Blocked** — the module is absent; no amount of analysis here substitutes for it.
- **Known limit** — a layer marked `partial` is weaker than `measured` and stronger than `absent`.
- **Not attempted** — disassembly, any dynamic validation.
