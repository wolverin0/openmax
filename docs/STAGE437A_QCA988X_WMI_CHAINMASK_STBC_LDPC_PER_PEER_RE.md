<!-- doc-head: STAGE437A_QCA988X_WMI_CHAINMASK_STBC_LDPC_PER_PEER_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 437A — chainmask, fixed rate and per-peer STBC / LDPC / NSS indexing

- **Receipt**: [`artifacts/autoresearch/stage437a_qca988x_wmi_chainmask_stbc_ldpc_per_peer_re.json`](../artifacts/autoresearch/stage437a_qca988x_wmi_chainmask_stbc_ldpc_per_peer_re.json)
- **Tool**: [`tools/re/build_stage437a_qca988x_wmi_chainmask_stbc_ldpc_per_peer_re.py`](../tools/re/build_stage437a_qca988x_wmi_chainmask_stbc_ldpc_per_peer_re.py)
- **Scope**: offline static. No firmware loaded, no module loaded, no radio contacted.

## 0. Two of the three named sources do not exist

| Source | Files |
| :--- | :-: |
| `firmware-2.bin` | **0** |
| `firmware-5.bin` | **0** |
| `ath10k_core.ko` | **0** |

The vendor `umac.ko` and `ath_dev.ko` (WA and XC, 8.7.25) are analysed instead — the same
substitution used in Stages 371A, 395A and 423A.

**`REFUTED`**: the firmware side of this stage cannot be read at all, because neither firmware
image exists in the corpus.

## 1. The WMI parameter identifiers are macros, not strings

| Identifier | Hits in 4 modules |
| :--- | :-: |
| `PDEV_PARAM`, `WMI_PDEV_PARAM` | **0** |
| `VDEV_PARAM`, `WMI_VDEV_PARAM` | **0** |
| `TX_CHAIN_MASK`, `RX_CHAIN_MASK`, `CHAIN_MASK` | **0** |
| `FIXED_RATE` | **0** |
| `spatial` | **0** |

**`REFUTED`**: none of the WMI parameter names exists as a string. `0x43` and `0x44` are enum
values compiled to immediates; a string sweep cannot bind them to a handler, and this stage does
not claim it did.

`per_peer_table_recovered = 0`, `wmi_id_to_name_map = 0`.

## 2. The per-peer knobs are real — and readable

| Module | `nss` | `NSS` | `stbc` | `ldpc` | `vhtmcs` | `1x1` | `2x2` |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| `WA:umac.ko` | 4 | 5 | 4 | 2 | 2 | 2 | 2 |
| `XC:umac.ko` | 4 | 5 | 4 | 2 | 2 | 2 | 2 |
| `WA:ath_dev.ko` | 0 | 0 | **5** | 0 | 0 | 0 | 0 |
| `XC:ath_dev.ko` | 0 | 0 | **5** | 0 | 0 | 0 | 0 |

**`CONFIRMED`**: `nss`, `stbc`, `ldpc` and `vhtmcs` are the per-peer rate vocabulary, and `stbc`
also lives in `ath_dev.ko`, so the STBC decision is made on the device side, not only in the UMAC
rate layer.

**`CONFIRMED`**: the fields are exposed through a proc/sysctl table with a getter each:

```
vhtmcs … get_vhtmcs … nss … get_nss … ldpc … get_ldpc …
```

That means all three are **readable per station at runtime** — the practical entry point for any
per-peer rate audit.

## 3. The one hard number: NSS is bounded at 3

`umac.ko` (both AC images) contains the bounds-check message:

```
%s : NSS greater than 3!
```

| Property | Value |
| :--- | :-: |
| modules with the check | **2** (`WA`, `XC`) |
| bound value | **3** |

**`CONFIRMED`**: any NSS value above **3** is rejected. That is the only hard numeric fact about
NSS indexing anywhere in the corpus.

## 4. Does that settle FMX-DISC-40? No — and the honest answer matters

FMX-DISC-40 asserts **0-based** indexing: `nss=0` is 1x1 VHT-NSS1, `nss=1` is 2x2 VHT-NSS2.

A bound of 3 is compatible with **two** different readings:

| Reading | Legal values | Implied max streams |
| :--- | :--- | :--- |
| **0-based** (DISC-40) | 0, 1, 2, 3 | **4** spatial streams |
| **1-based** | 1, 2, 3 (0 = unset) | **3** spatial streams |

QCA988x is a **3x3** part. Under the 0-based reading the bound would permit a **fourth** stream
that the radio cannot physically have — unless the bound is deliberately loose, or the part is a
2x2 SKU where both readings are harmless.

**Verdict: `consistent with 0-based indexing, not proven`.**

What the corpus does support is weaker and still useful:

- both `1x1` and `2x2` appear as strings (2 each in `umac.ko`), so the firmware names the two
  configurations DISC-40 talks about;
- the field is a per-peer value with a getter, so it is observable;
- the bound is real.

What would settle it: the `.rodata` array indexed by `nss`, or the `nss + 1` / `nss - 1`
arithmetic at the point of use. Neither was recovered here. **This stage does not upgrade
DISC-40 from `INFERRED` to `CONFIRMED`.**

## 5. What is established

| Claim | Status |
| :--- | :-: |
| the firmware images and `ath10k_core.ko` exist | **REFUTED** (0 files each) |
| `WMI_PDEV_PARAM_TX_CHAIN_MASK` / `RX_CHAIN_MASK` / `WMI_VDEV_PARAM_FIXED_RATE` exist as strings | **REFUTED** |
| `0x43` / `0x44` were bound to a handler | **REFUTED** (not attempted successfully) |
| `nss` / `stbc` / `ldpc` / `vhtmcs` are per-peer fields with getters | **CONFIRMED** |
| STBC is also decided in `ath_dev.ko` | **CONFIRMED** |
| NSS is bounded at 3 | **CONFIRMED** |
| `1x1` and `2x2` are named configurations | **CONFIRMED** |
| FMX-DISC-40's 0-based indexing | **INFERRED — consistent, unproven** |

## 6. Gaps

- **`UNKNOWN`** — whether `nss` is 0-based or 1-based. The bound alone cannot decide it.
- **`UNKNOWN`** — the per-peer struct layout: field order, widths, packing.
- **`UNKNOWN`** — the handler reached by PDEV param `0x43`/`0x44`.
- **`UNKNOWN`** — whether `WMI_VDEV_PARAM_FIXED_RATE` exists in the vendor WMI at all; it may be
  ath10k-only.
- **`UNKNOWN`** — how `stbc` in `ath_dev.ko` combines with `stbc` in `umac.ko`.
- **Known limit** — an absent macro is not an absent parameter.
- **Not attempted** — dynamic validation, register-level chainmask writes (Stage 396A covered the
  `ath_dev.ko` side).
