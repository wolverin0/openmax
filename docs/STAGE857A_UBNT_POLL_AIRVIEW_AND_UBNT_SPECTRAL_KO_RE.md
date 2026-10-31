<!-- doc-head: Stage 857A - ubnt_spectral.ko is an XW artefact that does not exist on WA or XC where the spectral module is ath_spectral.ko at 4.2 times smaller, the two drivers differ in feature set with radar only on the AC module and fft doubled on the XW module, airview lives in the ubntspecd daemon rather than the kernel, and three spectral client binaries are zero bytes in both XW rootfs -->
<!-- /doc-head -->
# Stage 857A — spectral and airView across the AC and XW lines

- **Receipt**: [`artifacts/autoresearch/stage857a_ubnt_poll_airview_and_ubnt_spectral_ko_re.json`](../artifacts/autoresearch/stage857a_ubnt_poll_airview_and_ubnt_spectral_ko_re.json)
- **Tool**: [`tools/re/dissect_stage857a_ubnt_poll_airview_and_ubnt_spectral_ko_re.py`](../tools/re/dissect_stage857a_ubnt_poll_airview_and_ubnt_spectral_ko_re.py)
- **Scope**: offline static. No module loaded, no radio contacted, nothing transmitted.

## 0. The stage names the wrong file for WA and XC

The stage asks for `ubnt_spectral.ko` in **WA and XC**. That file does not exist there.

| Image | Module | Bytes |
| :--- | :--- | :-: |
| `xw_614_rootfs` | `ubnt_spectral.ko` | **158,404** |
| `xw_636_rootfs` | `ubnt_spectral.ko` | **151,408** |
| `wa_8725_rootfs` | `ath_spectral.ko` | **37,656** |
| `xc_8725_rootfs` | `ath_spectral.ko` | **37,656** |
| `xc_874cs_rootfs` | `ath_spectral.ko` | **37,656** |
| `2xc_8711_modules` | `ath_spectral.ko` | 38,284 |

**`REFUTED`**: `ubnt_spectral_present_on_wa_xc = 0`, across 5 cross-name probes.

The cross-probes are the important part: `ubnt_spectral.ko` was looked for **at the AC path**, and
`ath_spectral.ko` **at the XW path**, in both directions. Neither appears where the other lives.

**`CONFIRMED`**: `wa_xc_module_is_ath_spectral = 1`, `size_ratio = 4.207`.

The AC module is **4.2 times smaller** than the XW one. These are not one driver under two names, and
the size gap alone says so before any token is counted.

This is the second naming split of the series, after Stage 834A's `atpc` / `autopwr`. The pattern is
consistent: **the XW line and the AC line diverged**, and a single-name search silently covers one line.

## 1. The two drivers do not have the same feature set

| Token | `ath_spectral` (WA/XC) | `ubnt_spectral` (XW 6.1.4) |
| :--- | :-: | :-: |
| `spectral` | **71** | 52 |
| `fft` | 8 | **16** |
| `scan` | 16 | 16 |
| **`radar`** | **1** | **0** |
| `phyerr` | 6 | 5 |
| `nf` (noise floor) | 12 | **15** |
| `airview` | **0** | **0** |

**`CONFIRMED`**: `radar_only_on_ath_spectral = 1`, `fft_doubled_on_ubnt = 1`.

Two structural differences, in opposite directions:

- **`radar` appears only on the AC module** — DFS radar event handling is an AC-line concern, which is
  consistent with airOS 8 running DFS on the 5 GHz PtMP panels;
- **`fft` is doubled on the XW module** (16 against 8) — the M5 line does more transform work, which
  matches its role as a spectrum-survey product.

Noise-floor vocabulary is also richer on the XW module, 15 against 12.

## 2. `airview` is user space, not kernel

**`CONFIRMED`**: `kernel_airview_hits = 0` and `daemon_airview_hits = 5`.

```
bin/ubntspecd   47,192 B   airview 5   spectral 1   fft 2   scan 6
                           radar 1   BPS 2   SCORE 2   RATING 2
```

So the airView division of labour is:

- **kernel measures** — `spectral`, `fft`, `scan`, `nf`, `phyerr`;
- **daemon scores** — `BPS`, `SCORE`, `RATING`, the airMagic scoring lines Stage 823A recorded.

The word `airview` never crosses into the kernel. A tool that grepped the modules for it would conclude
that airView does not exist on these images, and would be wrong about the feature while right about the
string.

**`REFUTED`**: the three AC `ubntspecd` copies are **not** byte-identical. They are the **same size,
47,192 bytes, with different content** — `daemon_identical_across_ac = 0`. That is the third
same-size-different-bytes case in two batches, after `ubnt_poll_host.ko` (831A) and `ubntbox` (835A).
Size comparison is not identity, and this series has now proven it three times.

## 3. Three spectral clients are zero-byte stubs

| Binary | `xw_614` | `xw_636` |
| :--- | :-: | :-: |
| `bin/spectralbox` | 229,660 | 179,240 |
| `bin/spectralplayer` | **0** | **0** |
| `bin/spectralserver` | **0** | **0** |
| `bin/spectraltool` | **0** | **0** |

**`CONFIRMED`**: `zero_byte_spectral_binaries = 6` (three per rootfs), `real_spectral_binaries = 2`.

Even `spectralbox` is not shared between versions: **229,660** against **179,240**, a 50,420-byte
difference. So the two XW releases do not ship the same survey client.

This is the zero-byte stub defect for the fifth time in the series, after `uav`, `ubnt-gps-reader`,
`bin/gps`/`bin/gps_cmd` and `ubnt-caldata`. The defect is **corpus-wide**, not stage-specific.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| `ubnt_spectral.ko` exists on WA or XC | **REFUTED** (0 of 5 cross-probes) |
| the AC spectral module is `ath_spectral.ko` | **CONFIRMED** (4 copies) |
| the two modules are one driver under two names | **REFUTED** (4.207x size gap) |
| radar handling is present only on the AC module | **CONFIRMED** |
| fft work is doubled on the XW module | **CONFIRMED** (16 vs 8) |
| `airview` appears in the kernel | **REFUTED** (0 in both modules) |
| `airview` appears in `ubntspecd` | **CONFIRMED** (5) |
| the AC daemons are byte-identical | **REFUTED** (same size, different bytes) |
| three spectral clients per XW rootfs are zero bytes | **CONFIRMED** (6 total) |
| the airView wire protocol | **UNKNOWN / not decoded** |

## 5. The operational reading

For spectral work on the Guarida panels, the correct targets are fixed:

1. **AC panels (WA/XC):** `ath_spectral.ko` — 37,656 bytes, carries `radar`, has half the `fft` work;
2. **XW (M5):** `ubnt_spectral.ko` — 151,408 or 158,404 bytes, no `radar`, double `fft`;
3. **scoring:** `ubntspecd` in user space, never the kernel module;
4. **avoid:** `spectralplayer`, `spectralserver`, `spectraltool` — zero bytes, nothing to analyse.

Any future spectral claim must cite which of the two drivers it measured. Stating "the spectral driver"
without the line is now an ambiguous claim.

## 6. Gaps

- **`UNKNOWN`** — how `ubntspecd` exchanges spectral frames with either driver.
- **`UNKNOWN`** — what the four missing client binaries were meant to do.
- **`UNKNOWN`** — whether the two `spectralbox` builds differ in protocol or only in packaging.
- **Known limit** — a token census is not a protocol decode.
- **Not attempted** — disassembly of either module, dynamic validation.
