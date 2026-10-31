<!-- doc-head: Stage 950A - aql_txq_limit aql_threshold aql_enable and aql_pending all live in mac80211 rather than in ath10k, aql_disable is one of its exported symbols, and no other module in the corpus carries any of the four field names so the airtime-queue limit is enforced above the driver boundary -->
# Stage 950A — where `aql_txq_limit` actually lives

- **Receipt**: [`artifacts/autoresearch/stage950a_mac80211_aql_txq_limit_re.json`](../artifacts/autoresearch/stage950a_mac80211_aql_txq_limit_re.json)
- **Tool**: [`tools/re/dissect_stage950a_mac80211_aql_txq_limit_re.py`](../tools/re/dissect_stage950a_mac80211_aql_txq_limit_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. The stage's assumption is inverted

```
aql_total = 9   fields present = 8
aql_txq_limit 1   aql_threshold 1   aql_enable 1   aql_pending 1
aql_disable symbol = 1   other modules with AQL = 0
```

**`CONFIRMED`**: `aql_owned_by_mac80211 = 1`.

AQL — the airtime queue limit — is normally described as an ath10k mechanism. In this build the four
field names and the disable symbol are in **mac80211**, and **no other module** in the corpus carries any
of them.

## 1. The field set, recovered exactly

| Field | Occurrences |
| :--- | :-: |
| `aql_txq_limit` | **1** |
| `aql_threshold` | **1** |
| `aql_enable` | **1** |
| `aql_pending` | **1** |
| `aqm` | present |
| `airtime_flags` | present |
| `airtime` | present |
| **total `aql`/`AQL` tokens** | **9** |

The tool's first version searched for the bare token `aql` across every module and reported **13 modules
with AQL**. That was binary noise: a three-character ASCII sequence occurs by chance in a thousand large
binaries. Restricting the census to the four **field names** gives **zero** other modules, which is the
attributable answer.

## 2. The disable path is a symbol

**`CONFIRMED`**: `aql_disable` is an **exported mac80211 symbol**.

That places the disable path on the same layer as the iTXQ API Stage 947A measured, not in a driver.
Combined with the field names appearing alongside `txq` and `airtime`, the reading is that the limit is
enforced **above** the driver boundary.

## 3. What this changes about the model

| Older model | Measured model |
| :--- | :--- |
| driver (ath10k) owns AQL | **mac80211 owns AQL** |
| the limit is per driver queue | limit lives with the per-TID TXQ machinery |
| disabling requires a driver change | `aql_disable` is a mac80211 symbol |

**`CONFIRMED`**: on this image the limit and its switch are inside the kernel's 802.11 stack, so an
operator tuning it is tuning the stack, not a vendor module.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| AQL fields are present | **CONFIRMED** (4 of 4) |
| they are in mac80211 | **CONFIRMED** |
| any other module carries them | **REFUTED** (0) |
| `aql_disable` is an exported symbol | **CONFIRMED** |
| the numeric limit is recovered | **REFUTED** (`limit_recovered = 0`) |
| the limit is enforced per station or per TID | **UNKNOWN** |

## 5. The operational reading

1. **Look in mac80211 for AQL tuning on OpenWrt 6.6.110.** Searching ath10k would find nothing, because
   the module is not even present.
2. **The fields look like a debugfs directory dump** — `aql_enable`, `aql_pending`, `aql_txq_limit`,
   `aql_threshold` sit beside `aqm` and `airtime_flags`. The directory path was not confirmed.
3. **A bare three-letter token is not evidence**, and this stage has the before-and-after numbers to prove
   it: 13 modules against 0.

## 6. Gaps

- **`UNKNOWN`** — the field values, which only a running system exposes.
- **`UNKNOWN`** — the per-station versus per-TID granularity.
- **`UNKNOWN`** — the exact debugfs path, since only the names were found.
- **Known limit** — naming plus one symbol locates the owner, not the semantics.
- **Not attempted** — disassembly, any dynamic validation.
