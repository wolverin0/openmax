<!-- doc-head: STAGE668A_LTU_AME_CORE_GPS_1PPS_AND_FRAME_SYNC_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 668A — GPS 1PPS and the TDMA superframe clock

- **Receipt**: [`artifacts/autoresearch/stage668a_ltu_ame_core_gps_1pps_and_frame_sync_re.json`](../artifacts/autoresearch/stage668a_ltu_ame_core_gps_1pps_and_frame_sync_re.json)
- **Tool**: [`tools/re/dissect_stage668a_ltu_ame_core_gps_1pps_and_frame_sync_re.py`](../tools/re/dissect_stage668a_ltu_ame_core_gps_1pps_and_frame_sync_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. `eab_driver.ko` absent — twelfth confirmation

**0 files.** Targets: `ame_core.ko` (3,282,052 bytes) and `ame_dev.ko` (298,760 bytes).

## 1. The superframe clock is real and complete: 28 symbols, 207 hits

```
ame_bbp_get_rx_sfn        ame_bbp_set_rx_sfn
ame_bbp_get_tx_sfn        ame_bbp_set_tx_sfn
ame_bbp_op_sync_sfn       ame_bbp_sync_SFN
ame_bbp_get_sync_sfn_count
ame_bbp_get_sync_mode     ame_bbp_set_sync_mode
ame_bbp_is_remote_SFN_synchronized
ame_bbp_set_remote_SFN
ame_bbp_reset_aes_sfn_ext
```

**`CONFIRMED`**: `sfn_counter_count = 6`, `sync_control_count = 5`.

The single most important structural fact: **RX and TX superframe numbers are separate counters with
separate setters** (`rx_tx_sfn_separate = 1`).

That is not an implementation quirk. In a split-frequency TDD link — which Stage 564A confirmed
(`rx/tx freq: %d/%d`) — the receive and transmit timelines are on different frequencies and can drift
independently. Keeping two counters and a **`is_remote_SFN_synchronized` predicate** is exactly how
you detect that drift before it becomes frame misalignment.

**`CONFIRMED`**: `ame_bbp_get_sync_sfn_count` exposes a **miss count** — how far apart the two ends
are — which turns alignment from a boolean into a measurable quantity.

The SFN also appears in scheduler diagnostics:

```
giveup schedCnt:%d SFN 0x%03X, 2partCnt:%d SFN 0x%03X, symbolGiveupCnt:%d SFN 0x%03X
```

**`CONFIRMED`**: the SFN is a **12-bit field** (`0x%03X` = three hex digits) and it is stamped onto
every scheduler abandonment record. So an operator can correlate a scheduling failure with the exact
superframe it happened in.

## 2. GPS is a requirement, not a reader

**44 hits**, and the decisive message:

```
NxN needs GPS sync!
```

**`CONFIRMED`**: `gps_required_message = 1`. MIMO (NxN) mode **requires** GPS synchronisation and
says so explicitly.

And there is a documented fallback path:

```
cpeFsmNxN_OffGPS_OnCIR
```

**`CONFIRMED`**: a CPE state machine transition leaves GPS and switches to **CIR-based** tracking.
That is what a unit does when it loses its GPS feed: it keeps operating using channel impulse
response rather than failing.

Stage 486A already found the consumer side — `bbp_rf_dcxo_is_sync_by_gps` and
`bbp_rf_dcxo_is_sync_by_tcxo` — so the stack distinguishes GPS-disciplined from crystal-only
operation. This stage adds the **requirement** message and the **fallback** state.

## 3. Three token traps, and one is total

| Token | Hits | Reality |
| :--- | :-: | :--- |
| **`pps`** | 2 | `ATX: (data=%u, bytes=%llu, pps=%u)` — **packets per second** |
| **`ptp`** | 26 | mostly `AME_Sched_PtP_master` / `_slave` — **Point-to-Point** |
| **`1pps`** | **0** | the identifier does not exist |

**`REFUTED`**: `one_pps_absent = 1`. The one-second pulse the stage names is **not present as a
token anywhere** in either module.

**`REFUTED`**: the two `pps` hits are **throughput statistics** on the AX TX/RX counters
(`pps_trap_hits = 2`), not a pulse.

**`REFUTED`**: `ptp` is dominated by **Point-to-Point** link scheduling — `AME_Sched_PtP_master`,
`_slave`, `_escape1`, `_escape2`, `_early_data_decision`, `AME_Sched_PtP_SubmitSymbols`
(`ptp_trap_hits = 7`). Only a minority of the 26 hits could plausibly be Precision Time Protocol
(`ame_bbp_op_txnrx_cmd_ptp_cpe`, `__ame_core_ptp_range_optimize_step2`), and this stage does not
claim which.

This is the ninth and tenth substring trap of the series in one stage, and they are dangerous
together: a search for "GPS 1PPS over PTP" finds `pps` and `ptp` in abundance and would conclude the
mechanism is documented.

## 4. What the corpus can and cannot answer

| Question | Answer |
| :--- | :--- |
| Is there a superframe clock? | **yes** — 28 symbols, RX and TX separate |
| Can alignment be measured? | **yes** — `get_sync_sfn_count` plus a synchronised predicate |
| Is GPS required? | **yes** — `NxN needs GPS sync!`, with a CIR fallback |
| Where does the 1PPS edge come from? | **no** — `ubnt-gps-reader` is a zero-byte file (Stage 416A) |
| Is PTP involved? | **unknown** — `ptp` is mostly Point-to-Point |
| How wide is the SFN? | **12 bits** (from the `0x%03X` format) |

**`CONFIRMED`**: the clock is named, measurable and correlated with scheduler failures.
**`CONFIRMED ABSENT`**: the 1PPS source, in every artefact the corpus holds.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| `eab_driver.ko` exists | **REFUTED** (0 files, 12th) |
| the superframe counter family is complete | **CONFIRMED** (6 get/set/sync) |
| RX and TX SFN are separate counters | **CONFIRMED** |
| a remote-synchronised predicate exists | **CONFIRMED** |
| a sync miss count is readable | **CONFIRMED** (`get_sync_sfn_count`) |
| the SFN is 12 bits and stamped on scheduler giveups | **CONFIRMED** (`0x%03X`) |
| NxN requires GPS sync | **CONFIRMED** (message) |
| a GPS-loss fallback to CIR exists | **CONFIRMED** (`cpeFsmNxN_OffGPS_OnCIR`) |
| `1pps` exists as a token | **REFUTED** (0 hits) |
| `pps` means one pulse per second here | **REFUTED** (packets per second) |
| `ptp` means Precision Time Protocol here | **REFUTED** (mostly Point-to-Point) |
| the 1PPS source and its ioctl | **UNKNOWN / zero-byte reader** |

## 6. The operational reading

The practical value of this stage is a **measurement that already exists**:

```
ame_bbp_get_sync_sfn_count      ->  how many superframes apart are the two ends
ame_bbp_is_remote_SFN_synchronized  ->  are they aligned at all
```

Combined with the 12-bit SFN stamped on every `giveup` record, a park can answer "is this CPE
misaligned, and by how many superframes" **without GPS instrumentation** — the counter is the
instrument.

What cannot be answered is where the absolute time reference comes from, because the only reader in
the corpus is empty. That is a corpus defect, not a finding about the hardware.

## 7. Gaps

- **`UNKNOWN`** — the SFN epoch: what it counts from, and how it is aligned to any external time.
- **`UNKNOWN`** — the legal range of `sync_sfn_count` and the threshold that declares loss of sync.
- **UNKNOWN** — whether the minority `ptp` hits are Precision Time Protocol or more Point-to-Point.
- **`UNKNOWN`** — the CIR fallback's accuracy relative to GPS.
- **`UNKNOWN`** — the `sync_mode` enumeration values.
- **Blocked** — the 1PPS source, until a non-empty `ubnt-gps-reader` exists.
- **Not attempted** — dynamic validation, GPS hardware interaction.
