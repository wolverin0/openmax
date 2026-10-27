<!-- doc-head: STAGE388A_AF4X_INVICTUS2_TDD_CP_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 388A — airFiber / LTU asymmetric TDD, cyclic prefix and strict timing

- **Receipt**: [`artifacts/autoresearch/stage388a_af4x_invictus2_tdd_cp_re.json`](../artifacts/autoresearch/stage388a_af4x_invictus2_tdd_cp_re.json)
- **Tool**: [`tools/re/af4x_invictus2_fpga_tdd_cyclic_prefix_re.py`](../tools/re/af4x_invictus2_fpga_tdd_cyclic_prefix_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. The product the stage names is not in the corpus

A recursive name search for `invictus`, `airfiber`, `af4x*` and `af5x*` returns **11 artefacts**.
Classified by suffix:

| Kind | Count |
| :--- | :-: |
| PNG product images | 3 |
| MIB text | 1 |
| JSON receipts / templates / notes | 7 |
| **firmware, rootfs, `.bin`, `.ko`, `.ipk`** | **0** |

One of the seven JSON entries is the **Stage 449A** sibling receipt
(`stage449a_af4x_af5x_invictus2_tdd_tuning_kit.json`), which was created after this stage ran; the
count moved from 10 to 11 for that reason and the conclusion is unaffected. It keeps drifting: later workstreams added stage822a documentation archives that match the same filter, so the test now pins the substantive claim (zero firmware binaries) rather than the count.

**`CONFIRMED`**: there is **no AF4X Invictus firmware and no rootfs** in this corpus. The airFiber
side of the stage cannot be answered from what is on disk, and the receipt says so rather than
borrowing LTU numbers and calling them airFiber.

## 1. The documented contract is not available either

`UBNT-AirFIBER-MIB.txt` (42,281 bytes, revision `201405090000Z`) defines **157 `OBJECT-TYPE`s**.

| Object family | Objects |
| :--- | :-: |
| **TDD** | **0** |
| **cyclic prefix** | **0** |
| **strict timing** | **0** |
| duty | 0 |

**`REFUTED`**: the AirFIBER MIB carries no TDD, cyclic-prefix or strict-timing object. It is the
Ethernet/radio configuration group (`ethLinkOffDuration`, port config, status counters). So there
is no shipped documentation to anchor 75/25, 67/33, 50/50 or `cp=4/8/16` to.

## 2. The frame contract *is* in the LTU modules — as attribute names

| Module | Bytes | Frame parameters present |
| :--- | :-: | :--- |
| `ame_core.ko` | 3,282,052 | `duty_cycle`, `frame_len`, `dl_symbols`, `ul_symbols`, `gap0`, `sync_mode` |
| `ame_dev.ko` | 298,760 | **all ten**, incl. `cpsample`, `frame_period`, `sample_rate`, `gps_sync_timeout` |
| `ame_dfs.ko` | 141,472 | `duty_cycle` |
| `cds_mac_mod.ko` | 139,672 | none |
| `ubnthal.ko` | 152,640 | none |

**10 distinct parameter names** across the set. `ame_core.ko` also exports the function symbol
**`ame_bbp_get_duty_cycle`**, and `ame_dev.ko` prints the frame descriptor in one line:

```
{ bandwidth:%u, frame_period:%u, duty_cycle:%u, sample_rate:%u, cpsample:%u,
  dl_symbols:%u, ul_symbols:%u, ... }
```

**`CONFIRMED`**: the asymmetric TDD frame is described by **`duty_cycle`** together with the
symbol counts **`dl_symbols` / `ul_symbols`**, the period **`frame_len` / `frame_period`**, and
the guard **`gap0`**. That is a real, checkable contract — expressed as runtime attributes, not as
a table of ratios.

**`CONFIRMED`**: the cyclic prefix is **`cpsample`**, in `ame_dev.ko` only.

## 3. Duty cycle is validated against load

`ame_dfs.ko` carries the only *behavioural* statement in the whole set:

```
duty cycle (%d%%) too low for %d%% traffic load
```

**`CONFIRMED`**: the LTU DFS logic compares the configured duty cycle against the offered traffic
load and refuses a frame whose duty is too low. This is the first place in the corpus where a
TDD ratio has a consequence rather than just a name — and it validates **relative** duty, not the
75/25 / 67/33 / 50/50 labels.

## 4. What is absent, precisely

| Token | Occurrences across all five modules |
| :--- | :-: |
| `75/25`, `67/33`, `50/50` (and colon forms) | **0** |
| `cp=4`, `cp=8`, `cp=16`, `cp_len`, `cp_prefix`, `cyclic prefix` | **0** |
| `stricttiming`, `strict_timing`, `strict timing` | **0** |
| `TDD` | **1** |

**`REFUTED`**: no ratio literal and no cyclic-prefix enumeration exists in the LTU module set.

The single `TDD` hit is a false positive and worth naming: it sits inside the mangled symbol
fragment **`bbp_mrx_foe_TDDeRotCFO`** in `ame_core.ko` — a BBP observation-mode identifier, not a
TDD frame control. Counting it as evidence would be exactly the error this project guards against.

## 5. What is established

| Claim | Status |
| :--- | :--- |
| an AF4X Invictus firmware or rootfs exists in the corpus | **REFUTED** (0 files) |
| the AirFIBER MIB documents TDD / CP / strict timing | **REFUTED** (0 of 157 objects) |
| LTU exposes `duty_cycle`, `cpsample`, `dl_symbols`, `ul_symbols`, `gap0`, `frame_len` | **CONFIRMED** |
| `ame_core.ko` exports `ame_bbp_get_duty_cycle` | **CONFIRMED** |
| duty cycle is validated against traffic load | **CONFIRMED** |
| a 75/25, 67/33 or 50/50 ratio table exists | **REFUTED** |
| a cp = 4 / 8 / 16 table exists | **REFUTED** |
| `stricttiming` exists anywhere | **REFUTED** |
| the single `TDD` token is frame control | **REFUTED** (mangled symbol fragment) |

## 6. The practical reading for the park

The frame is specified by **two numbers and two symbol counts**, not by a named ratio:

```
duty_cycle  ≈  dl_symbols / (dl_symbols + ul_symbols)   [not verified numerically]
cpsample    =  cyclic prefix duration
gap0        =  guard interval
```

That means a 75/25 request is expressible on LTU as a symbol-count split, and the module will
accept or reject it based on the duty-versus-load check in `ame_dfs.ko`. Nothing in this corpus
lets us verify the mapping `75/25 ↔ dl_symbols/ul_symbols` numerically, and the receipt keeps
that as `UNKNOWN` rather than asserting `dl_symbols = 3 × ul_symbols`.

## 7. Gaps

- **`UNKNOWN`** — the numeric relation between `dl_symbols`/`ul_symbols` and any named ratio.
- **`UNKNOWN`** — the set of legal `cpsample` values; 4/8/16 is the stage's claim, not observed.
- **`UNKNOWN`** — the default `duty_cycle`, `frame_len` and `gap0` per bandwidth.
- **`UNKNOWN`** — whether `stricttiming` exists under another name (`sync_mode` and
  `gps_sync_timeout` are the nearby candidates, unverified).
- **`UNKNOWN`** — the duty-versus-load threshold in `ame_dfs.ko`.
- **Known limit** — an attribute name proves a knob exists, not what it is set to.
- **Not attempted** — dynamic validation, and any airFiber analysis (no image on disk).
