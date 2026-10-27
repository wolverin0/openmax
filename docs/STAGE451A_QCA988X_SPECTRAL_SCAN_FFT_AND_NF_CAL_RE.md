<!-- doc-head: STAGE451A_QCA988X_SPECTRAL_SCAN_FFT_AND_NF_CAL_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 451A — spectral FFT bin packer, WMI spectral commands and NF calibration

- **Receipt**: [`artifacts/autoresearch/stage451a_qca988x_spectral_scan_fft_and_nf_cal_re.json`](../artifacts/autoresearch/stage451a_qca988x_spectral_scan_fft_and_nf_cal_re.json)
- **Tool**: [`tools/re/build_stage451a_qca988x_spectral_scan_fft_and_nf_cal_re.py`](../tools/re/build_stage451a_qca988x_spectral_scan_fft_and_nf_cal_re.py)
- **Scope**: offline static. No firmware loaded, no module loaded, no radio contacted.

## 0. The firmware images are absent

| Image | Files |
| :--- | :-: |
| `firmware-2.bin` | **0** |
| `firmware-5.bin` | **0** |

Same wall as Stages 423A, 437A and 451A's own predecessors. The spectral surface is read from the
vendor modules instead, and it is **split across three** of them.

## 1. The headline: `PDEV` should be `VDEV`

The stage asks for `WMI_PDEV_SPECTRAL_SCAN_CONFIGURE_CMDID` and `..._ENABLE_CMDID`.

| Name | Hits |
| :--- | :-: |
| `WMI_PDEV_SPECTRAL_SCAN_CONFIGURE_CMDID` | **0** |
| `WMI_PDEV_SPECTRAL_SCAN_ENABLE_CMDID` | **0** |
| `PDEV_SPECTRAL` (any form) | **0** |
| **`WMI_VDEV_SPECTRAL_SCAN_CONFIGURE_CMDID`** | **present** |
| **`WMI_VDEV_SPECTRAL_SCAN_ENABLE_CMDID`** | **present** |

The name table in `umac.ko` reads:

```
…WMI_PDEV_SEND_BCN_CMDID . WMI_VDEV_SPECTRAL_SCAN_CONFIGURE_CMDID ..
WMI_VDEV_SPECTRAL_SCAN_ENABLE_CMDID . WMI_REQUEST_STATS_CMDID…
```

**`REFUTED`**: the prefix is **`PDEV`** in the stage and **`VDEV`** in the firmware.

**`CONFIRMED`**: both commands exist as `VDEV` commands. That is a semantic difference, not a
typo: the scan is configured **per virtual interface** (per VAP), not per physical device. A
dual-VAP AP running spectral scan on one interface and not the other is consistent with the
firmware; a PDEV-scoped command would make that impossible.

`pdev_prefix_refuted = 1`, `wmi_vdev_command_hits = 4`.

## 2. The FFT bin packer is named — four functions

`ath_spectral.ko` (37,656 bytes) exports the whole packer:

```
get_fft_bin_count
process_search_fft_report
dump_search_fft_report
spectral_dump_fft
```

**`CONFIRMED`**: the packer is `get_fft_bin_count` (how many bins) plus
`process_search_fft_report` / `dump_search_fft_report` (the two directions of the report), with
`spectral_dump_fft` as the debug dumper.

**`UNKNOWN`**: the bin **format**. Stage 327A measured the immediates inside the FFT functions —
32, 64, 256 and 512 present, **128 absent**, 13 sites — but the dB encoding, the byte stride and
the descriptor were never derived. `fft_bin_format_recovered = 0` still holds.

## 3. Noise-floor calibration is named — eleven functions

The NF family is larger than the FFT family, and it spreads across all three modules:

```
adjust_rssi_with_nf_dbm          get_nfc_ctl_rssi        get_nfc_ext_rssi
spectral_get_noise_power         wlan_get_noise_floor    wlan_get_chan_noise_floor
wlan_scan_entry_noise_floor      ieee80211_scan_entry_noise_floor
ol_if_spectral_get_chain_noise_floor   ol_if_spectral_get_ctl_noisefloor
ol_if_spectral_get_ext_noisefloor
```

**`CONFIRMED`**: calibration has **two RSSI sources** — `get_nfc_ctl_rssi` (control channel) and
`get_nfc_ext_rssi` (extension channel) — plus a per-chain floor
(`ol_if_spectral_get_chain_noise_floor`), and `adjust_rssi_with_nf_dbm` folds the floor into the
reported RSSI in dBm.

That is a complete, named chain: sample → per-chain floor → dBm adjustment → per-channel floor →
scan-entry cache. **The chain is named; the numbers are not.** `nf_cal_table_recovered = 0`: no
offset table, no interpolation curve, no period.

## 4. The enable path

```
spectral_scan_enable          spectral_scan_enable_params
spectral_check_hw_capability  spectral_attach / spectral_detach
ol_if_spectral_detach
```

`ath_dev.ko` carries `spectral_scan_enable` and `spectral_scan_enable_params`; `umac.ko` carries
the `ol_if_*` wrappers and the capability check.

**`CONFIRMED`**: enable is a **capability-gated, parameterised** operation with an explicit detach
path — not a bare boolean.

## 5. The `bin_` trap

`umac.ko` has **9** `bin_` hits, and **all of them are firmware blobs**, not FFT bins:

```
ol_transfer_bin_file
otp_AR9888v2_bin_len
athwlan_AR9888v2_ptmp_sta_bin_len
```

**`REFUTED`**: `bin_` in `umac.ko` has nothing to do with spectral bins. Counting it as packer
evidence would have been a false positive — the same failure mode as `LQ` in Stage 438A.

## 6. What is established

| Claim | Status |
| :--- | :-: |
| `firmware-2.bin` / `firmware-5.bin` exist | **REFUTED** (0 files) |
| the commands are `WMI_PDEV_`-scoped | **REFUTED** (0 hits) |
| the commands are `WMI_VDEV_`-scoped | **CONFIRMED** (both names present) |
| an FFT bin packer exists by name | **CONFIRMED** (`get_fft_bin_count` + 3) |
| NF calibration exists with two RSSI sources and per-chain floors | **CONFIRMED** (11 symbols) |
| the enable path is capability-gated with params | **CONFIRMED** (5 symbols) |
| `bin_` in `umac.ko` means FFT bins | **REFUTED** (all firmware blobs) |
| the FFT bin byte format | **UNKNOWN / not recovered** |
| the NF calibration table | **UNKNOWN / not recovered** |

## 7. Gaps

- **`UNKNOWN`** — the FFT bin encoding: dB scale, stride, header. 327A's 32/64/256/512 immediates
  are counts, not a layout.
- **`UNKNOWN`** — the NF calibration period and the dBm offset table.
- **`UNKNOWN`** — the `WMI_VDEV_SPECTRAL_SCAN_*` payload schema; the names are known, the struct
  is not.
- **`UNKNOWN`** — whether a VDEV-scoped scan can run concurrently on two VAPs.
- **`UNKNOWN`** — why 128 bins are absent while 32/64/256/512 are present.
- **Known limit** — a named function is a control point, not a format.
- **Not attempted** — dynamic validation, and Stage 327A's `shm = 0` result still stands: the
  `ubntspecd` shared layout is not in these modules.
