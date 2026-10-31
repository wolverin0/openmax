<!-- doc-head: Stage 948A static sweep for an ath10k module and documentation of the mac80211 iTXQ push-side contract a driver would call; CONFIRMED_STATIC_BINARY, offline, no radio -->
# Stage 948A - `ath10k_mac_tx_push_txq` and the mac80211 push-side contract

Evidence class: `CONFIRMED_STATIC_BINARY`. `radio_safety: static only`. Scope: static, offline, a
corpus sweep plus one ELF symbol census. No module was loaded, no radio was contacted, nothing was
written to a device.

## Question

The stage was scoped as a reverse engineering pass over `ath10k_mac_tx_push_txq`, the driver-side
function that pulls an skb from a mac80211 TXQ and hands it to the QCA988x firmware. A dissector can
only dissect an artefact it has. So the first measurement is a corpus sweep for any ath10k module,
and the second measurement is the part of the boundary that *is* present: the mac80211 side that the
driver is required to call.

## Measurement 1 - the corpus sweep

Every `.ko` under `artifacts/` and `firmware/` was read and classified four independent ways, so that
a module cannot hide behind an unusual filename:

| Test | Meaning | Matches |
| :--- | :--- | ---: |
| filename | basename contains `ath10k` | 0 |
| `.modinfo` | a `name=ath10k...` entry | 0 |
| defined symbols | any `.symtab` name containing `ath10k` | 0 |
| raw image bytes | the literal byte string `ath10k` anywhere in the file | 0 |

| Field | Value | Label |
| :--- | ---: | :--- |
| `.ko` files scanned | 1163 | CONFIRMED |
| unparsable modules | 0 | CONFIRMED |
| `ath10k_modules_found` | 0 | CONFIRMED |
| `driver_symbols_present` | 0 | CONFIRMED |
| `push_txq_recovered` | 0 | CONFIRMED (nothing to recover from) |
| modules carrying the `ath10k` byte string | 0 | CONFIRMED |

Not one of the 1163 modules mentions ath10k in its name, its `.modinfo`, its symbol table, or its
byte content. That is a stronger negative than a filename filter alone: the absence survives four
different tests.

Consequence: `ath10k_mac_tx_push_txq` is not recoverable from this corpus. Any dissection of it
produced from this repository would be written from memory of the upstream driver, not from a binary,
so this stage reports zero and says why. The stage claim "the push loop was reverse engineered from a
driver binary" is REFUTED for this corpus.

## Measurement 2 - the mac80211 side of the boundary

What is present is the other half of the contract. Every entry point below is defined in the mac80211
module, and every one of them is also in `__ksymtab_strings`, which is what makes it callable from a
module driver:

| Contract symbol | Present | `st_size` | Exported |
| :--- | ---: | ---: | ---: |
| `ieee80211_handle_wake_tx_queue` | 1 | 168 | 1 |
| `ieee80211_txq_schedule_start` | 1 | 236 | 1 |
| `ieee80211_next_txq` | 1 | 796 | 1 |
| `__ieee80211_schedule_txq` | 1 | 592 | 1 |
| `ieee80211_txq_may_transmit` | 1 | 904 | 1 |
| `ieee80211_tx_dequeue` | 1 | 3528 | 1 |
| `ieee80211_txq_get_depth` | 1 | 88 | 1 |
| `ieee80211_txq_airtime_check` | 1 | 176 | 1 |

`contract_symbols_present = 8`, `contract_symbols_expected = 8`,
`contract_symbols_exported = 8`. Label: CONFIRMED.

The module under measurement is
`artifacts/canary_panel1_guarida/panel1_native_cutover_20261019/after/mac80211.ko`, 829464 bytes,
sha256 `19a8fde6c6e5efbec3b5b3ddb28399631fc3bba516c5341c8f40e7263124c416`, 145 exported symbols.

## The contract flow a driver would implement

Documented from the symbol names and from upstream mac80211 structure. Label: INFERRED for the
control flow, CONFIRMED for each individual symbol, its size, and its export flag.

```
driver wake_tx_queue op
  -> ieee80211_handle_wake_tx_queue        (168 B, exported)
  -> ieee80211_txq_schedule_start          (236 B, exported)   start of an AC round
  -> ieee80211_next_txq                    (796 B, exported)   pick candidate TXQ
  -> ieee80211_txq_may_transmit            (904 B, exported)   AQL admission for that TXQ
  -> ieee80211_tx_dequeue                  (3528 B, exported)  one skb out of the TXQ
  -> driver tx op                          firmware push
partial pull
  -> __ieee80211_schedule_txq              (592 B, exported)   re-arm the TXQ
```

Three properties matter for the boundary and each is a measured fact:

1. The entry from the driver is `ieee80211_handle_wake_tx_queue`, not `ieee80211_tx_dequeue`. The
   driver does not walk the queue itself; it is woken and mac80211 drives the round. Label: CONFIRMED
   for the export, INFERRED for the direction.
2. `ieee80211_tx_dequeue` is exported, so the pull primitive is available to a module driver, and its
   3528-byte body is the largest object on this path. Label: CONFIRMED.
3. Admission is not the driver's job: `ieee80211_txq_may_transmit` (904 bytes) and
   `ieee80211_txq_airtime_check` (176 bytes) sit above the pull, so the AQL and airtime decisions are
   taken inside mac80211 before the driver sees an skb. Label: CONFIRMED for presence and export,
   INFERRED for the ordering.

## What is not here

| Thing | Status | Label |
| :--- | :--- | :--- |
| `ath10k_mac_tx_push_txq` | absent from every binary searched | CONFIRMED (absent) |
| `ath10k_mac_op_wake_tx_queue` | absent from every binary searched | CONFIRMED (absent) |
| `ath10k_htt_tx` | absent from every binary searched | CONFIRMED (absent) |
| driver ring depth and firmware handoff | unmeasured, no driver binary | UNKNOWN |
| whether a real image loads ath10k at runtime | runtime fact, not measured | UNKNOWN |

The three driver-side names are carried in the receipt under
`contract.driver_side_names_not_in_corpus` precisely so that a later stage cannot mistake them for
measured symbols.

## Why the negative is the useful result

A driver that is absent from the corpus still constrains the analysis, because the boundary is
one-sided in a specific way: mac80211 performs the AQL and airtime admission before the driver is
asked for an skb. So a measurement of the mac80211 side is sufficient to say where the queue decision
lives, even with no driver binary. What cannot be said without the driver is how many skbs per round
are pulled, how deep the hardware ring is, and how the firmware handoff paces the medium.

That division is exactly what Stage 949A consumes: mac80211 owns the queue decision, the driver side
is absent, and the firmware boundary beyond the driver is not a module at all.

## Verdicts

| ID | Claim | Label |
| :--- | :--- | :--- |
| C1 | zero ath10k modules in the corpus by four independent tests | CONFIRMED |
| C2 | `ath10k_mac_tx_push_txq` was recovered from a binary | REFUTED |
| C3 | 8 of 8 mac80211 contract entry points are defined and exported | CONFIRMED |
| C4 | the pull primitive is exported and is the largest body on the path (3528 B) | CONFIRMED |
| C5 | the documented call flow matches the real instruction order | INFERRED |
| C6 | the driver-side push loop, ring depth, and firmware handoff | UNKNOWN |

## Gaps

- No ath10k module exists in the 1163-module corpus, so `push_txq_recovered` is 0 by measurement and
  not by omission.
- The call flow is documented from symbol names and export flags; no disassembly was performed, so
  the ordering is inferred.
- Whether a deployed image loads ath10k at runtime is a runtime fact and was not measured.
- The QCA988x firmware blob is not a kernel module and is outside the sweep.
- No dynamic validation. Nothing was loaded and no radio was contacted.

## Files

- `tools/re/dissect_stage948a_ath10k_mac_tx_push_txq_re.py`
- `artifacts/autoresearch/stage948a_ath10k_mac_tx_push_txq_re.json`
- `docs/STAGE948A_ATH10K_MAC_TX_PUSH_TXQ_RE.md`
