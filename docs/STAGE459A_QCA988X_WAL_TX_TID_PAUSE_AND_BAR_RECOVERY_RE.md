<!-- doc-head: STAGE459A_QCA988X_WAL_TX_TID_PAUSE_AND_BAR_RECOVERY_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 459A — WAL TX TID pause, BAR failure and the requeue / excess-retry counters

- **Receipt**: [`artifacts/autoresearch/stage459a_qca988x_wal_tx_tid_pause_and_bar_recovery_re.json`](../artifacts/autoresearch/stage459a_qca988x_wal_tx_tid_pause_and_bar_recovery_re.json)
- **Tool**: [`tools/re/build_stage459a_qca988x_wal_tx_tid_pause_and_bar_recovery_re.py`](../tools/re/build_stage459a_qca988x_wal_tx_tid_pause_and_bar_recovery_re.py)
- **Scope**: offline static. No firmware loaded, no module loaded, no radio contacted.

## 0. The firmware images are absent

`firmware-2.bin` **0**, `firmware-5.bin` **0**. Fourth stage in this run to hit the same wall. All
evidence below comes from `umac.ko` (WA and XC, identical counts).

## 1. The TX statistics dump — the counters are real, one spelling is not

Both counters live in a single statistics block:

```
phy underrun      : %u
tx_abort          : %u
mpdus_requed      : %u
excess retries    : %u
last rc           : %u
sched se…
```

| Token | Hits | Verdict |
| :--- | :-: | :--- |
| **`mpdus_requed`** | **2** (1 per image) | **exact match** |
| **`excess retries`** | **2** | the real spelling |
| **`excess_retries`** | **0** | **does not exist** |

**`CONFIRMED`**: `mpdus_requed` is spelled exactly as the stage says.

**`REFUTED`**: `excess_retries` is **not** a single token. The firmware writes
**`excess retries : %u`** — with a space. A `grep excess_retries` returns zero and would be read as
"the counter does not exist", when it is sitting right next to `mpdus_requed`.

`excess_retries_spelling_refuted = 1`.

## 2. The consequence of excess retries is a kickout

A separate format string in `umac.ko`:

```
%s … station kicked out due to excessive retries (refcnt %u) associd %d
```

**`CONFIRMED`**: excess retries is not merely a counter — it gates a **station kickout** with a
reference count and an association id. That is the operational meaning of the counter, and it is
the one line in the module that turns the number into an action.

## 3. BAR failure is a named taxonomy

Four WAL debug identifiers appear together in the debug-id table:

```
WAL_DBGID_BAR_TX_FAIL
WAL_DBGID_BAR_ALLOC_FAIL
WAL_DBGID_STA_KICKOUT
WAL_DBGID_LOCAL_DATA_TX_FAIL
```

**`CONFIRMED`**: BlockAckReq failure is split into **two distinct causes** — the BAR frame failed
to transmit (`BAR_TX_FAIL`) versus the BAR could not be **allocated** (`BAR_ALLOC_FAIL`). Those are
different faults with different fixes, and the firmware distinguishes them.

**`CONFIRMED`**: `WAL_DBGID_STA_KICKOUT` is listed beside them, so the kickout path of §2 is
instrumented in the same family.

8 hits total (the four ids, twice).

## 4. TID pause exists — under a typo

The pause mechanism is two routines, and one of them is misspelled in the shipped binary:

```
ath_net80211_exist_pendingfrm_tidq
ath_net80211_reset_pasued_tid          <-- "pasued", not "paused"
```

**`CONFIRMED`**: `ath_net80211_exist_pendingfrm_tidq` answers "does this TID queue still hold
frames", which is the predicate a pause needs. **`CONFIRMED`**: `ath_net80211_reset_pasued_tid`
resets a paused TID.

**`REFUTED`**: an exact `paused` search for that routine fails. A researcher grepping
`reset_paused_tid` gets nothing and may conclude the pause path is absent. It is present; the
vendor's own spelling is wrong.

The VAP-level pause family is separate and correctly spelled:

```
ieee80211_vap_pause      ieee80211_vap_unpause
ieee80211_vap_force_pause   ieee80211_vap_force_unpause
wlan_mlme_pause_bss      wlan_mlme_resume_bss
```

with the runtime logs `pause LMAC node` and `unpause LMAC node` gated on the count of stations in
power-save mode.

**`CONFIRMED`**: the pause/unpause mechanism the stage asks for exists at **two levels** — per-VAP
(MLME) and per-TID (queue). The VAP level is driven by power-save state; the TID level is driven by
pending frames.

## 5. The retry schedule is configurable

```
_RATE_GetTxRetrySchedule
ath_net80211_set_swretrystate
g_default_xretry_per_penalty
```

**`CONFIRMED`**: retry is a **schedule** (not a scalar), with a software retry state setter and a
default per-penalty excess-retry threshold. `g_default_xretry_per_penalty` is exactly the knob that
relates the `excess retries` counter to the kickout of §2.

## 6. What is established

| Claim | Status |
| :--- | :-: |
| `firmware-2.bin` / `firmware-5.bin` exist | **REFUTED** (0 files) |
| `mpdus_requed` exists verbatim | **CONFIRMED** |
| `excess_retries` exists as one token | **REFUTED** (real form is `excess retries`) |
| excess retries gates a station kickout | **CONFIRMED** |
| BAR failure is split into TX and ALLOC causes | **CONFIRMED** |
| TID pause is implemented | **CONFIRMED** (`exist_pendingfrm_tidq`, `reset_pasued_tid`) |
| VAP pause/unpause exists with force variants | **CONFIRMED** |
| the retry schedule is a table, not a scalar | **CONFIRMED** (`_RATE_GetTxRetrySchedule`) |
| the counter **increment sites** | **UNKNOWN / not located** |

## 7. Gaps

- **`UNKNOWN`** — where `mpdus_requed` and `excess retries` are incremented. A `%u` in a format
  string is the read side; the write side was not found.
- **`UNKNOWN`** — the value of `g_default_xretry_per_penalty` and its units.
- **`UNKNOWN`** — what queues a TID and what releases it; only the predicate and reset are named.
- **`UNKNOWN`** — the BAR recovery sequence after `BAR_ALLOC_FAIL` versus `BAR_TX_FAIL`.
- **`UNKNOWN`** — whether the pause is per-TID selective or all-TID.
- **Known limit** — a debug id proves a failure is distinguishable, not how it is handled.
- **Not attempted** — dynamic validation.
