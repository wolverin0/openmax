<!-- doc-head: STAGE259A_XW_ATH_RATE_ATHEROS_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 259A — `ath_rate_atheros.ko` (XW.v6.3.6, M5)

- **Receipt**: [`artifacts/autoresearch/stage259a_xw_ath_rate_atheros_re.json`](../artifacts/autoresearch/stage259a_xw_ath_rate_atheros_re.json)
- **Tool**: `tools/re/dissect_stage259a_xw_ath_rate_atheros_re.py`
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Module

`artifacts/firmware_re_xw_m5/xw_636_rootfs/lib/modules/2.6.32.71/ath_rate_atheros.ko`
— **139,128 bytes**, MIPS32 big-endian `ET_REL`.

Note the kernel path: `2.6.32.**71**`, not the `2.6.32.68` used by the airOS 8 AC images. The
M5 airOS 6 tree ships a different kernel ABI revision.

## 1. Symbol budget

| Metric | Value |
| :--- | :-: |
| Symbols total | 74 |
| Defined | 74 |
| Rate-named | **34** |
| PER-named | **6** |
| Retry-named | **0** |

**`CONFIRMED`: the module carries only 74 defined symbols.** That is the whole surface. A
rate-control module of 139 KB with 74 symbols is heavily stripped — it exports its entry points
and hides everything else.

This single fact determines what the stage can deliver. Every question about the rate ladder,
the PER thresholds and the retry logic is a question about **internal** code that has no symbol.

## 2. Data arrays

One candidate array survives the `.rel.data` / `.rel.rodata` `R_MIPS_32` clustering:

| First | Last | Entries | Span |
| :--- | :--- | :-: | :-: |
| one cluster only | | **20** | 20 |

**`INFERRED`**: a 20-entry pointer array in a rate module is consistent with a per-rate or
per-MCS descriptor table, but 20 does not match a canonical HT20 (8) / HT40 (8) or VHT (10)
ladder. It may be a driver-ops table rather than a rate table. Not claimed either way.

## 3. PER and retry constants

| Surface | Constant histogram |
| :--- | :--- |
| PER-named functions | **empty** |
| Retry-named functions | **empty** (no retry symbols at all) |

The `addiu $zero,N` sweep over the 6 PER-named functions found **no** small positive constant in
1..100. Two readings:

1. the thresholds are loaded from **static tables** (`.data`) rather than materialised as
   immediates;
2. the 6 PER-named symbols are not the functions that compare thresholds.

Both point at the same conclusion: the constants are not reachable by scanning those functions.

## 4. Why the requested dissection is not achievable here

The stage asked for HT20/HT40 rate tables, up/down PER thresholds and retry handling. Each
requires one of:

| Requirement | Present? |
| :--- | :--- |
| symbol names for the internal functions | **no** (74 total) |
| immediate constants for thresholds | **no** (histograms empty) |
| a rate table with a recognisable stride | **no** (one 20-entry cluster, unverified) |
| relocations binding the tables to code | **yes** (`.rel.data` exists) |

Only the last is available. The relocation binding could be used to find **which function reads
the table**, which is the one concrete next step — but it does not by itself decode the
descriptors.

## 5. Disposition

**`CONFIRMED`**: 139,128 B module, 74 defined symbols, 34 rate-named, 6 PER-named, 0 retry-named,
one 20-entry pointer array, empty PER and retry constant histograms.

**`REFUTED`**: the implicit assumption that a rate-control module exposes enough symbols to
reconstruct its ladder. It does not.

**`UNKNOWN`**: the rate descriptor layout, the PER up/down pair, the retry ladder.

## 6. Gaps

- **`UNKNOWN`** — descriptor layout of the 20-entry array.
- **`UNKNOWN`** — which function consumes that array.
- **`UNKNOWN`** — PER thresholds and retry logic (no symbols, no immediates).
- **`KNOWN LIMIT`** — the module is stripped to 74 symbols; deeper work requires
  access-pattern recovery over the whole `.text`, not symbol lookup.
- **Not attempted** — dynamic validation.
