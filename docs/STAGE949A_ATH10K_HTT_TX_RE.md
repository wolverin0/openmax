<!-- doc-head: Stage 949A - there is no htt_tx.c source and no ath10k module anywhere, but the airOS driver umac.ko carries the HTT transmit vocabulary at eighty hits across eight module copies, which is the only binary evidence for the HTT path that this corpus contains -->
# Stage 949A — `htt_tx.c` and the HTT transmit vocabulary

- **Receipt**: [`artifacts/autoresearch/stage949a_ath10k_htt_tx_re.json`](../artifacts/autoresearch/stage949a_ath10k_htt_tx_re.json)
- **Tool**: [`tools/re/dissect_stage949a_ath10k_htt_tx_re.py`](../tools/re/dissect_stage949a_ath10k_htt_tx_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Source absent, driver absent, vocabulary present

```
sources = 0   modules scanned = 1163   modules with HTT = 8
HTT hits = 80   firmware container hits = 0
```

**`REFUTED`**: there is **no `htt_tx.c`** in the corpus and **no ath10k module** to substitute for it.

**`CONFIRMED`**: there **is** HTT transmit vocabulary in a driver module, and it is not the one the stage
names.

## 1. Where the vocabulary actually is

Eight module copies, all of them `umac.ko` or its patched variants, each carrying:

```
htt_tx       9
htt_tx_compl 1
```

| Module | Copies |
| :--- | :-: |
| `umac.ko` | 6 |
| `wa_8725_umac_stage78b_patched.ko` | 1 |
| `xc_8725_umac_stage78b_patched.ko` | 1 |

`umac` is the **airOS** driver, the proprietary counterpart of `ath10k` on these images. So the HTT
transmit path is named by the vendor driver that speaks it, not by the open-source module the stage
expected.

That is a materially different result from "HTT is absent", and it is why the token set was tightened
before this number was reported.

## 2. A correction worth recording

The first token set included `tx_desc`, `CE_TX` and `HTC_`. It produced **958 hits across 13 modules**,
almost all of them generic descriptor names in unrelated networking code.

Tightening to HTT-specific identifiers — `htt_tx`, `htt_tx_compl`, `msdu_id`, `htt_peer`, `htt_stats`,
`HTT_T2H`, `HTT_H2T` — gives **80 hits across 8 modules**, every one of them `umac`.

**`CONFIRMED`**: the number is now attributable. The first version was a substring trap of the same
family this series has logged a dozen times; the difference is that this one was caught before the doc
was written.

## 3. The firmware is silent

**`REFUTED`**: `firmware_container_hits = 0`.

The QCA988x container carries **no** HTT vocabulary, which matches Stage 855A (transfer vocabulary zero)
and Stage 873A (receive vocabulary zero). The firmware side cannot corroborate the driver naming.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| `htt_tx.c` exists in the corpus | **REFUTED** (0) |
| an ath10k module exists to supply it | **REFUTED** (0) |
| HTT transmit vocabulary exists in some module | **CONFIRMED** (80 hits) |
| and that module is `umac.ko`, the airOS driver | **CONFIRMED** (8 of 8 rows) |
| the firmware container names HTT | **REFUTED** (0) |
| the HTT transmit path was recovered | **REFUTED** (`htt_tx_recovered = 0`) |

## 5. The operational reading

1. **Search `umac.ko`, not `ath10k`, on airOS images.** The open-source module is not shipped; the vendor
   driver is, and it is the one that names the HTT path.
2. **A generic token set is worthless here.** `tx_desc` alone matched thirteen unrelated modules; only
   `htt_tx` narrows to the right eight.
3. **Do not expect the firmware to help.** Three separate stages now report zero vocabulary in that
   container, so the naming evidence lives exclusively on the driver side.

## 6. Gaps

- **`UNKNOWN`** — the HTT transmit structure layout; the strings prove naming, not format.
- **`UNKNOWN`** — whether `umac` uses the same message numbers as ath10k.
- **Blocked** — no source, no ath10k module.
- **Known limit** — a driver string is not a protocol specification.
- **Not attempted** — disassembly of `umac.ko`, any dynamic validation.
