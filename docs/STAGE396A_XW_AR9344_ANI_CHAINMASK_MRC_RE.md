<!-- doc-head: STAGE396A_XW_AR9344_ANI_CHAINMASK_MRC_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 396A — XW AR9344 ANI, chainmask and the MRC / SIMO-TX path

- **Receipt**: [`artifacts/autoresearch/stage396a_xw_ar9344_ani_chainmask_mrc_re.json`](../artifacts/autoresearch/stage396a_xw_ar9344_ani_chainmask_mrc_re.json)
- **Tool**: [`tools/re/xw_ar9344_ath9k_ani_and_chainmask_mrc_re.py`](../tools/re/xw_ar9344_ath9k_ani_and_chainmask_mrc_re.py)
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Two premise corrections

**There is no XM rootfs.** The M5 corpus holds `xw_614_rootfs` and `xw_636_rootfs`; no `xm_*` tree
exists (`xm_roots_found = []`). The two data points are therefore **XW 6.1.4** and **XW 6.3.6**,
not XW/XM.

**The register names are macros, not strings.** `AR_PHY_MULTICHAIN_GAIN_CTL`, `MULTICHAIN_GAIN`,
`AR_PHY_TIMING2` and `TIMING2` return **0 hits in all 8 modules**. On the ath9k side these are
`#define`s; the compiled object carries the numeric offsets, never the identifiers.

**`REFUTED`**: the register names appear anywhere. **`UNKNOWN`**: their numeric values — this
stage does not claim them, because a name search cannot find what was never emitted.

## 1. The eight modules

| Version | Module | Bytes | `txchainmask` | `rxchainmask` | `chainmask` | EWMA symbols |
| :--- | :--- | :-: | :-: | :-: | :-: | :-: |
| 6.1.4 | `ath_hal.ko` | 562,576 | 0 | 0 | 2 | 0 |
| 6.1.4 | `ath_dev.ko` | 436,552 | **4** | **3** | 23 | 0 |
| 6.1.4 | `ath_rate_atheros.ko` | 152,816 | 0 | 0 | 0 | **6** |
| 6.1.4 | `ubnt_ewma_ht.ko` | 22,652 | 0 | 0 | 0 | **24** |
| 6.3.6 | `ath_hal.ko` | 503,892 | 0 | 0 | 2 | 0 |
| 6.3.6 | `ath_dev.ko` | 414,408 | **4** | **3** | 23 | 0 |
| 6.3.6 | `ath_rate_atheros.ko` | 139,128 | 0 | 0 | 0 | **6** |
| 6.3.6 | `ubnt_ewma_ht.ko` | 21,784 | 0 | 0 | 0 | **24** |

Totals: `chainmask` **64** hits, `ewma` **56** hits, across **8** modules.

**`CONFIRMED`**: the chainmask configuration lives in **`ath_dev.ko`**, and its wire form is
identical across 6.1.4 and 6.3.6 despite the module shrinking 22,144 bytes (5.1 %).

## 2. `txchainmask` / `rxchainmask` are proc entries with getters

The strings do not appear in isolation. The context is a handler table:

```
... t_keycache ... printBBDebug ... get_printBBDebug ... txchainmask ...
    get_txchainmask ... rxchainmask ... get_rxchainmask ... txchmaskleg ...
    get_txchmaskleg ...
```

**`CONFIRMED`**: each chainmask has a **name and a `get_` accessor pair** registered in the same
region — the classic proc/sysctl table shape. So both are readable knobs on the running device,
which is what a SIMO-TX / 2x2-MRC-RX audit needs.

**`UNKNOWN`**: the accepted value range, and which values select 1x2 STBC/CDD versus 2x2 MRC.

## 3. `ubnt_ewma_delegate_on` is a module parameter, not a function

This is the sharpest result of the stage. The symbol family in **`ath_rate_atheros.ko`** is:

```
ubnt_ewma_delegate_on
__param_ubnt_ewma_delegate_on
__param_str_ubnt_ewma_delegate_on
```

**`CONFIRMED`**: `ubnt_ewma_delegate_on` is a **`module_param`**, in both XW versions. The
`__param_*` and `__param_str_*` symbols are the kernel's parameter registration machinery, so the
name is exposed under `/sys/module/ath_rate_atheros/parameters/` at runtime.

That reframes the stage's question. It asked for "`ubnt_ewma_delegate_on`" as if it were logic to
decode. It is a **switch**: whether the EWMA rate controller delegates to `ubnt_ewma_ht.ko`. The
delegation logic itself is in the EWMA module, which exports **24** ewma symbols against
`ath_rate_atheros`'s 6.

**`UNKNOWN`**: the parameter's type, default and the condition under which delegation occurs.

## 4. The ANI surface

Only two ANI symbols survive in the rate/HAL modules:

```
ar9300_is_ani_noise_spur
ath_hal_log_ani_callback_register
```

**`CONFIRMED`**: ANI is present and instrumented by callback registration. The noise-spur test is
named; the tuning curve is not.

Stage 373A already found the companion evidence on the same image: XW `ath_hal.ko` carries the INI
override messages `firstep[level]=%d ini=%d` and `cycpwrThr1[level]=%d ini=%d`. Together those are
the ANI state and its override path — but neither was traced to a register write here.

## 5. What is established

| Claim | Status |
| :--- | :--- |
| an XM rootfs exists | **REFUTED** (0 trees) |
| `AR_PHY_MULTICHAIN_GAIN_CTL` / `AR_PHY_TIMING2` are strings in these modules | **REFUTED** |
| `txchainmask` / `rxchainmask` are real, with `get_` accessors | **CONFIRMED** |
| the chainmask vocabulary lives in `ath_dev.ko` | **CONFIRMED** |
| `ubnt_ewma_delegate_on` is a `module_param` of `ath_rate_atheros.ko` | **CONFIRMED** |
| ANI is present with a noise-spur test and a callback register | **CONFIRMED** |
| the register offsets for the two named registers | **UNKNOWN** |
| the SIMO-TX / 2x2-MRC-RX selection path | **UNKNOWN / not recovered** |

## 6. Gaps

- **`UNKNOWN`** — the numeric value of `AR_PHY_MULTICHAIN_GAIN_CTL` and `AR_PHY_TIMING2`. Locating
  them requires the ath9k header or a register-access trace, not a string search.
- **`UNKNOWN`** — which chainmask value yields 1x2 STBC/CDD and which yields 2x2 MRC on RX.
- **`UNKNOWN`** — the `ubnt_ewma_delegate_on` type and default.
- **`UNKNOWN`** — the EWMA delegation condition in `ubnt_ewma_ht.ko`.
- **`UNKNOWN`** — the ANI tuning curve; only the state vector's names are known (373A).
- **Known limit** — a `module_param` proves a switch exists, not what flipping it does.
- **Not attempted** — dynamic validation; no XM image exists to compare.
