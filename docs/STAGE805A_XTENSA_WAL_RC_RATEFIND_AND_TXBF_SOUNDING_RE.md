<!-- doc-head: STAGE805A_XTENSA_WAL_RC_RATEFIND_AND_TXBF_SOUNDING_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 805A — Xtensa WAL rate-control ratefind and TxBF sounding

- **Receipt**: [`artifacts/autoresearch/stage805a_xtensa_wal_rc_ratefind_and_txbf_sounding_re.json`](../artifacts/autoresearch/stage805a_xtensa_wal_rc_ratefind_and_txbf_sounding_re.json)
- **Tool**: [`tools/re/dissect_stage805a_xtensa_wal_rc_ratefind_and_txbf_sounding_re.py`](../tools/re/dissect_stage805a_xtensa_wal_rc_ratefind_and_txbf_sounding_re.py)
- **Scope**: offline static. No firmware loaded, no module loaded, no radio contacted.

## 0. The firmware carries no names at all

Container `openwrt_qca988x_hw20_firmware_2_ct.bin`, **204,796 bytes**, **2 `SGMT` segments**
totalling **204,677 bytes**.

| Token | Hits in the container |
| :--- | :-: |
| `wal`, `WAL` | **0** |
| `ratefind` | **0** |
| `txbf` | **0** |
| `sounding` | **0** |
| `rc_`, `rate` | **0** |

**`REFUTED`**: `firmware_names_absent = 1`, `firmware_named_token_hits = 0`.

That is expected — a compiled Xtensa image has no identifier table, and Stage 423A already proved the
payload is code rather than a named structure. **The rate table cannot be read by name.**

## 1. The ratefind walk is host-side, and it is complete

`umac.ko` carries the whole rate-control vocabulary:

```
rcGetFirstValidTxRate      rcGetNextValidTxRate
wal_rcquery                wal_rcupdate
_RATE_GetTxRetrySchedule   _RATE_GetSGIFlag   _RATE_SetSGIMasks
g_default_sgi_per_thresh   g_default_xretry_per_penalty
```

**`CONFIRMED`**: `ratefind_walk_complete = 1` and `ratefind_is_host_side = 1`.

The pair **first valid rate → next valid rate** is the rate search. The firmware supplies per-rate
statistics; the host **walks** them. So "ratefind" is a host loop over firmware measurements, not a
firmware routine.

**`CONFIRMED`**: `host_wal_dbg_count = 2` — `wal_rcquery` and `wal_rcupdate` are the two WAL
rate-control debug IDs, matching the debug-id format Stage 459A found
(`ratectrl_dbgid_wal_rcquery [rix1 %d rix2 %d rix3 %d proberix %d ppduflag 0x%x]`).

**`CONFIRMED`**: `host_ratecontrol_symbol_count = 16` — the family is substantial, and includes both
the SGI mask setter and the excess-retry penalty default.

## 2. There is no sounding sequence

| Token | `umac.ko` hits |
| :--- | :-: |
| **`sounding`** | **0** |
| `SU-BF` | **0** |
| `TXBF` | **7** |

**`REFUTED`**: `sounding_absent = 1`.

`TXBF` appears 7 times, and Stage 615A established exactly what those are: a **capability name table**
(CDD/STBC/TXBF beside VHT20/40/80), a runtime **rejection** message (`TXBF not supported`), and
**per-rate-group power limits** (`MaxRegPwrAGTXBF0/0`).

So the beamforming capability is **enumerated and power-accounted**, and the **training sequence is
not named**. A TxBF implementation with no sounding identifier is a capability flag, not a beamformer.

## 3. What each side actually contributes

| Side | Contribution | Evidence |
| :--- | :--- | :--- |
| **Firmware** | per-rate statistics (no names) | 0 named tokens |
| **Host** | the ratefind walk, SGI masks, retry schedule | 16 symbols |

`CONFIRMED`: the split is clean. Any rate-selection question splits into "what did the firmware
measure" (unreadable here) and "how did the host walk it" (readable here).

`firmware_rate_table_recovered = 0`, `txbf_sounding_sequence_recovered = 0`.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| the firmware names any rate-control entity | **REFUTED** (0 hits) |
| the ratefind walk exists and is complete | **CONFIRMED** (`rcGetFirstValidTxRate` → `rcGetNextValidTxRate`) |
| the walk runs on the host | **CONFIRMED** (both symbols in `umac.ko`) |
| two WAL rate-control debug IDs exist | **CONFIRMED** |
| SGI is a per-rate mask with a default threshold | **CONFIRMED** (`_RATE_SetSGIMasks`, 615A) |
| an excess-retry penalty default exists | **CONFIRMED** (`g_default_xretry_per_penalty`) |
| a TxBF sounding sequence is named | **REFUTED** (0 hits) |
| the firmware rate table | **UNKNOWN / numeric data, undecoded** |

## 5. The operational reading

For a rate-selection problem the corpus points at the **host loop** and nothing else:

1. `g_default_xretry_per_penalty` is the penalty that feeds `excess retries` (Stage 459A);
2. `_RATE_SetSGIMasks` decides SGI eligibility per rate, seeded by `g_default_sgi_per_thresh`;
3. `rcGetFirstValidTxRate` / `rcGetNextValidTxRate` is the search itself.

What it cannot tell you is **why** a rate is judged valid — that input comes from firmware statistics
that carry no names in the container. Any explanation of a rate choice must come from measurement
(the `RATE: ChainMask ... vht_mcs_set ...` log line Stage 589A found), not from the blob.

## 6. Gaps

- **`UNKNOWN`** — the firmware rate table and its per-rate statistics.
- **`UNKNOWN`** — what makes a rate "valid" in `rcGetFirstValidTxRate`.
- **`UNKNOWN`** — the beat between `g_default_xretry_per_penalty` and the `excess retries` counter.
- **`UNKNOWN`** — whether sounding exists under a different vendor name; none was found.
- **Known limit** — a host walk over unnamed firmware data cannot be explained statically end to end.
- **Not attempted** — dynamic validation, live rate capture.
