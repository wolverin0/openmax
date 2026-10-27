<!-- doc-head: STAGE615A_QCA988X_TXBF_BEAMFORMING_AND_STBC_LDPC_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 615A — TxBF, sounding, STBC and LDPC capability and knobs

- **Receipt**: [`artifacts/autoresearch/stage615a_qca988x_txbf_beamforming_and_stbc_ldpc_re.json`](../artifacts/autoresearch/stage615a_qca988x_txbf_beamforming_and_stbc_ldpc_re.json)
- **Tool**: [`tools/re/build_stage615a_qca988x_txbf_beamforming_and_stbc_ldpc_re.py`](../tools/re/build_stage615a_qca988x_txbf_beamforming_and_stbc_ldpc_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Seven modules across two lines

| Module | bytes |
| :--- | :-: |
| `WA:umac.ko` / `XC:umac.ko` | 2,356,432 / 2,358,768 |
| **`XW:umac.ko`** | **884,988** |
| `WA:ath_dev.ko` / `XC:ath_dev.ko` | 287,216 each |
| `WA:ath_hal.ko` / `XC:ath_hal.ko` | 367,456 / 360,896 |

## 1. `TXBF` is capability text, not a beamforming engine

`txbf_tokens = 14` (counting both cases), but **every hit is a label or a power limit**:

```
CDD  .STBC.TXBF..CCK  .OFDM .HT20 .HT40 .VHT20.VHT40.VHT80.HTDUP    <- capability table
%s : TXBF not supported                                            <- rejection
MaxRegPwrAGTXBF0/0    MaxRegPwrAGSTBC1/0                           <- per-rate-group power
```

**`CONFIRMED`**: `capability_table_modules = 2` — the AC UMACs carry a **capability name table** that
lists TXBF beside CDD, STBC, CCK, OFDM, HT20/40, VHT20/40/80 and HTDUP. That is a negotiated-feature
bitmap rendered as names.

**`CONFIRMED`**: `txbf_not_supported_modules = 2` — there is a **runtime rejection** path. The stack
can refuse TXBF.

**`CONFIRMED`**: `maxregpwr_txbf_modules = 2` — TXBF and STBC have **separate per-rate-group power
limits** (`MaxRegPwrAGTXBF0/0` versus `MaxRegPwrAGSTBC1/0`). Beamforming and STBC are regulated
differently because they change the transmit pattern.

**`REFUTED`**: there is **no sounding sequence**. `sounding_token_hits = 0`, and `SU-BF` / `SU_BF`
return zero as well. A transmit-beamforming implementation without a named sounding procedure is
not a beamforming engine — it is a **capability flag with power accounting**.

## 2. The `bf_` trap: it is the TX buffer

`ath_dev.ko` has 14 `bf_` hits, and a naive read would call that beamforming. It is the **TX buffer
struct**:

```
bf_node is null. bf=%p
ath_node is null in bf %p
bf_lastfrm != bf->bf_lastbf
bf_q NOT EMPTY
```

**`CONFIRMED`**: `bf_buffer_marker_hits = 12` — twelve explicit occurrences of `bf_node`, `bf_q`,
`bf_lastfrm` or `bf_lastbf`. Those are unambiguous buffer identifiers, so the identification does
not depend on a context window.

The only two symbols matching a beamforming pattern in `ath_dev.ko` are `ath_print_tbf_usage` and
`ath_tx_uapsdqnulbf_complete` — where `tbf` is `t`+`bf` and `nulbf` is `nul`+`bf`. **Neither is
beamforming.**

This is the seventh substring trap of the series, and it is the one most likely to produce a false
positive, because `bf` is the obvious abbreviation for beamforming and the module really does have
14 of them.

## 3. XW carries none of it

| Image | TxBF + STBC + LDPC tokens |
| :--- | :-: |
| `WA:umac.ko` | 27 |
| `XC:umac.ko` | 27 |
| **`XW:umac.ko`** | **0** |

**`CONFIRMED`**: `xw_umac_feature_free = 1`. The M5 UMAC is **884,988 bytes** against the AC's
2,356,432 — 37 % of the size — and contains **zero** hits for the entire token set, in every case.

So TxBF, STBC and LDPC are **AC-line features**. An M5 deployment does not negotiate them, and a
question about M5 beamforming has no binary to answer it here.

## 4. What *is* well instrumented: the runtime getters

```
Getting LDPC: %x
Getting TX STBC: %x
Getting RX STBC: %x
Getting VHT MCS MAP set: %x
```

**`CONFIRMED`**: `runtime_getter_count = 4` and `capability_readable = 1`. Four negotiated values are
**printed per station**: LDPC on/off, TX STBC, RX STBC, and the VHT MCS map.

Plus the proc field:

```
LDPC … getLDPC
```

**`CONFIRMED`**: `proc_knobs = [LDPC, getLDPC]` — LDPC is a **readable proc attribute**, so it can
be polled per interface without any debug flag.

Note the asymmetry: **TX STBC and RX STBC are reported separately**, which is correct — a station can
support transmit STBC without receive STBC. Stage 437A found `stbc` in both `umac.ko` and
`ath_dev.ko`; this stage shows why the UMAC needs its own copy.

## 5. The token totals

| Token set | Hits |
| :--- | :-: |
| `TXBF` + `txbf` | **14** |
| `STBC` + `stbc` | **38** |
| `LDPC` + `ldpc` | **18** |
| **`sounding` / `SU-BF`** | **0** |
| `beamform` / `mu_mimo` | **0** |

**`CONFIRMED`**: STBC is the most-mentioned of the three by a wide margin (38 against 14 and 18).
That ordering matches how the code treats them: STBC is a per-frame transmit choice, LDPC is a
coding capability, and TXBF is a label with power accounting.

## 6. What is established

| Claim | Status |
| :--- | :-: |
| a capability name table lists TXBF beside CDD/STBC/VHT modes | **CONFIRMED** (2 modules) |
| a runtime TXBF rejection path exists | **CONFIRMED** |
| TXBF and STBC have separate per-rate-group power limits | **CONFIRMED** |
| a sounding / SU-BF identifier exists | **REFUTED** (0 hits) |
| `bf_` in `ath_dev.ko` is beamforming | **REFUTED** (TX buffer, 12 markers) |
| XW `umac.ko` carries any TxBF/STBC/LDPC vocabulary | **REFUTED** (0 hits) |
| LDPC, TX STBC, RX STBC and the VHT MCS map are printed per station | **CONFIRMED** |
| LDPC is a readable proc attribute | **CONFIRMED** |
| the beamforming engine / steering matrix | **UNKNOWN / not in these modules** |
| the per-peer capability bit layout | **UNKNOWN / not recovered** |

## 7. The operational reading

This changes what a beamforming question on this hardware can mean:

- a station's **LDPC, TX STBC, RX STBC and VHT MCS map** are readable directly from the log and the
  proc field — that part is answerable today;
- **TXBF capability** is visible as a negotiated flag, and the stack will refuse it where
  unsupported;
- but there is **no sounding procedure and no steering-matrix code** in these modules. Whatever
  performs beamforming training, it is not the AC UMAC's named surface — and on the M5 line the
  capability is not present at all.

So "does this link use TxBF" is answerable; "how does this link steer its beam" is not.

## 8. Gaps

- **`UNKNOWN`** — where the beamforming training runs, if anywhere. Not named in these modules.
- **`UNKNOWN`** — the capability bitmap layout in the table.
- **`UNKNOWN`** — the per-peer LDPC/STBC bit packing behind the getters.
- **`UNKNOWN`** — whether TXBF is ever actually negotiated, or only ever refused.
- **`UNKNOWN`** — the `MaxRegPwrAG*` values.
- **Known limit** — a capability name proves a feature is enumerable, not that it is used.
- **Not attempted** — dynamic validation, on-air sounding capture.
