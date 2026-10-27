<!-- doc-head: STAGE326A_ATH_DEV_BMISS_HANG_RECOVERY_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 326A — `ath_dev.ko` bmiss, hang detection and deaf-state reset

- **Receipt**: [`artifacts/autoresearch/stage326a_ath_dev_bmiss_hang_recovery_re.json`](../artifacts/autoresearch/stage326a_ath_dev_bmiss_hang_recovery_re.json)
- **Tool**: `tools/re/ath_dev_bmiss_and_reset_recovery_re.py`
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Three images, two kernel ABIs

| Image | ABI | `ath_dev.ko` bytes |
| :--- | :--- | :-: |
| `WA.v8.7.25` | 2.6.32.68 | 287,216 |
| `XC.v8.7.25` | 2.6.32.68 | 287,216 |
| `XW.v6.3.6` | **2.6.32.71** | **414,408** |

WA and XC are byte-identical in size (and were shown identical in Stage 199A's sibling
comparisons). **XW is 44 % larger and on a different ABI** — the airOS 6 M5 build carries
substantially more code in this module.

## 1. The named entry point exists

The stage names `ath_hw_hang_check`. It is **present in all three images**:

| Image | Symbols matching `ath_hw_hang_check|hw_hang_check|hang_check` |
| :--- | :--- |
| `WA.v8.7.25` | **`ath_hw_hang_check`** |
| `XC.v8.7.25` | **`ath_hw_hang_check`** |
| `XW.v6.3.6` | **`ath_hw_hang_check`** |

**`CONFIRMED`**: the function is real and named, not a hypothesis. It survived symbol stripping
in all three builds, which means it is either exported or referenced across modules.

## 2. Symbol surface

| Bucket | WA | XC | XW |
| :--- | :-: | :-: | :-: |
| **bmiss** (`bmiss|beacon_miss|beacon`) | **17** | **17** | **10** |
| **hang** (`hang|stuck|deaf|stall|wedge`) | **16** | 16 | 16 |
| **watchdog** (`watchdog|timeout|timer|panic`) | **12** | 12 | 12 |
| **reset** (`reset|recover|restart|reinit`) | **11** | 11 | 11 |
| **bbmac** (`bb_|mac_|pcu|phy_err|mib`) | **4** | 4 | 4 |

**`CONFIRMED`**: XW has **fewer** bmiss-named symbols (10) than WA/XC (17), despite being the
larger binary. The airOS 6 M5 build names fewer beacon-miss paths even though it carries more
code overall — consistent with the AC line adding station-tracking features that M5 does not
have.

## 3. Threshold candidates

Small immediates inside bmiss- and watchdog-named functions were collected as a histogram. They
are **candidates**, not verified thresholds:

- a value inside a bmiss-named function may be the miss count, a retry bound, or an unrelated
  loop limit;
- the watchdog histogram likewise mixes timeouts, retry counts and array bounds.

The receipt carries both histograms per image; no single value is claimed as "the bmiss
threshold".

## 4. What is not decoded

**No BB/MAC hang recovery state machine.** With 16 hang-named and 4 bbmac-named symbols, the
surface is thin — the actual detection logic likely lives behind `ath_hw_hang_check` and the
register reads it performs, which were not traced.

**No deaf-state reset path.** 11 reset-named symbols exist; the trigger-to-reset sequence is not
reconstructed.

**No recovery timing.** The watchdog histogram is not a timer table.

## 5. Why this matters for the operational question

The park runs `v8.7.25` on AC and `v6.3.6` on M5. Both carry `ath_hw_hang_check`, so the hang
detection entry point is **not** an AC-only feature. What differs is the *number* of bmiss paths
(17 vs 10), which suggests the AC line has more granular beacon-miss handling.

That is a testable operational difference, and it is the most actionable output of the stage:
if M5 devices show worse beacon-miss resilience, the 7 missing named paths are the first place
to look.

## 6. Gaps

- **`UNKNOWN`** — what `ath_hw_hang_check` reads and what it returns.
- **`UNKNOWN`** — the bmiss threshold value.
- **`UNKNOWN`** — the deaf-state reset trigger and sequence.
- **`UNKNOWN`** — whether the 7 missing M5 bmiss symbols correspond to 7 absent behaviours or to
  renamed ones.
- **`KNOWN LIMIT`** — a named symbol is presence, not behaviour.
- **Not attempted** — dynamic validation.
