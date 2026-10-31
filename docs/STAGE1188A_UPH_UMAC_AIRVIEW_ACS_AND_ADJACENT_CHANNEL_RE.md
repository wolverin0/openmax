<!-- doc-head: Stage1188A static binary RE attributing AirView, ACS/airSelect, ANI, CCA and adjacent-channel rejection across ubnt_poll_host.ko, umac.ko and ath_dev.ko, with the poll scheduler measured as carrying none of it -->
# Stage 1188A - AirView, ACS and adjacent-channel rejection across uph / umac / ath_dev

Evidence class `CONFIRMED_STATIC_BINARY`. Static analysis only: no module loaded, no radio
contacted, no firmware written, no live address used, no socket opened. `radio_safety:
"static only"`.

The purpose is to give the bilateral PtP/site channel evaluator a defensible owner for each
signal it reasons about, so later stages stop guessing which module owns spectral, ACS or
adjacent-channel behaviour.

## Binaries

| module | bytes | sha256 (first 16) | depends | symtab | sized funcs |
| :--- | ---: | :--- | :--- | ---: | ---: |
| `ubnt_poll_host.ko` | 189880 | `bfc3f499a0867669` | *(empty)* | 469 | 154 |
| `umac.ko` | 2356432 | `660435ed9c50f139` | `ath_spectral,asf,adf,ath_dev` | 4766 | 1975 |
| `ath_dev.ko` | 287216 | `9328580821a806fe` | `asf,ath_rate_atheros,ath_spectral,adf` | 880 | 310 |

All three are ELF32 MSB `ET_REL`, `EM_MIPS`, `vermagic 2.6.32.68 mod_unload MIPS32_R2 32BIT`,
taken from the WA 8.7.25 rootfs so the three analyses describe one build. Every offset in this
document is section-relative; `0x0b22fc` means `.text+0xb22fc`.

## The result that changes planning

`ubnt_poll_host.ko` carries none of this surface. Zero defined symbols match any of the
spectral, ACS, ANI, CCA or adjacent-channel patterns out of 469 symtab entries, and its
`.modinfo depends=` field is present and empty, so it does not even link against the module
that would provide the capability. The poll scheduler is a standalone TDMA/WDS scheduler; it
has no channel-selection and no scan-evaluation role.

## AirView is named `spectral`, not AirView

`airview_hits = 0`. The literal token `AirView`, in any casing, does not occur in any of the
three modules. That is a naming result, not an absence result, and nothing in the receipt is
derived from it. The capability is spelled `spectral` throughout, and it splits in two:

- Orchestration in `umac.ko`: 41 sized spectral symbols in one contiguous block,
  `.text+0xb21c0` to `.text+0xb2d50`, including `ol_if_start_spectral_scan`
  (`0xb29ec`, 160 B), `ol_if_stop_spectral_scan` (`0xb2a9c`, 100 B),
  `ol_if_spectral_setup` (`0xb2c94`, 188 B) and the two WMI senders
  `wmi_send_vdev_spectral_enable_cmd` (`0xb2784`, 292 B) and
  `wmi_send_vdev_spectral_configure_cmd` (`0xb2634`, 336 B). A 72-byte `spectral_ops` object
  sits at `.bss+0x8b50`.
- PHY event source in `ath_dev.ko`: 21 sized spectral symbols including
  `ath_dev_start_spectral_scan` (`0x7e9c`, 144 B) and `ath_spectral_control` (`0xe424`, 496 B).
- FFT and spectral decoding are in neither. `umac.ko` imports `spectral_attach`,
  `spectral_detach`, `spectral_control`, `spectral_process_phyerr`, `spectral_register_funcs`
  and `spectral_check_hw_capability` as **undefined** symbols, and declares
  `depends=ath_spectral`. `ath_dev.ko` imports eleven spectral names on the same basis. That is
  CONFIRMED binary evidence that a fourth module owns the FFT half; `ath_spectral.ko` itself is
  outside this stage's scope and was not dissected.

## ACS is the real name behind airSelect

`airselect_hits = 0` for every casing of `airSelect`, `airselect`, `air_select` and `airSel`.
The mechanism is called ACS and it lives entirely in `umac.ko`:

| symbol | offset | size |
| :--- | ---: | ---: |
| `ieee80211_acs_attach` | `0x4c2f0` | 144 |
| `ieee80211_acs_detach` | `0x4c380` | 60 |
| `wlan_acs_find_best_channel` | `0x4c4f4` | 1908 |
| `ieee80211_acs_stats_update` | `0x4cc68` | 212 |
| `ieee80211_acs_scan_report` | `0x4cd3c` | 368 |
| `osif_ioctl_eacs` | `0xa2620` | 300 |

Nine sized ACS symbols in total, all in `umac.ko`. The operator-facing strings carry resolved
`.text` references: `Invoking ACS module for Best channel selection `, `%s: ACS picked %d as
best channel`, `ACS scan is in progress, Please request for the report after a while... ` and
`%s: ACS returned NULL channel`. `osif_ioctl_eacs` is the userspace entry point, so ACS is
driven over an ioctl and reports asynchronously through an event handler.

`umac.ko` is partially symbol-stripped: `get_acs_state`, `osif_acs_start_bss`,
`osif_acs_event_handler`, `osif_acs_dfs_nol_event_handler`, `chscaninit` and
`ieee80211_acs_free_scan_resource` survive only as string literals, so their code offsets are
unknown and are not asserted.

## ANI

ANI is real and it is split. `umac.ko` carries the level surface: the `.rodata` attribute names
`ani_enable`, `get_ani_enable`, `ani_poll_len`, `ani_listen_len`, `ani_ofdm_level`,
`ani_cck_level`, the `ANI Enable:  %d`, `ANI POLLING:`, `ANI UPDATE ofdm level`,
`ANI CONTROL ofdmlevel` and `ANI resetting` literals, and one sized symbol
`dbglog_ani_print_handler` (`0xba4ec`, 616 B). `ath_dev.ko` carries the attribute-name pair
`ANIEna` / `GetANIEna` and imports `ath_hal_enabledANI` as undefined, so the switch that
actually enables ANI in the PHY belongs to `ath_hal.ko`, which was not dissected.

## CCA and adjacent-channel rejection

`cca_hits = 2`. Two distinct program-data strings survive, and both are the same knob:
`CWMIgnExCCA` at `.rodata+0x1860` and `GetCWMIgnExCCA` at `.rodata+0x1878` in `ath_dev.ko`.
Neither is a symbol and no `.text` reference to either string was recovered, so the meaning is
INFERRED from the name and the handler is UNKNOWN. The receipt keeps the two rejected raw
matches visible: `WHAL_ERROR_RESET_ADCDCCAL1` and `ADCDCCAL2` contain the letter run `CCA` but
are ADC calibration error names, and the token-boundary classifier excludes them.

The load-bearing adjacent-channel evidence is elsewhere and it is symbol-backed:

- `ol_if_spectral_get_ctl_noisefloor` (`0xb232c`, 48 B) and
  `ol_if_spectral_get_ext_noisefloor` (`0xb22fc`, 48 B) are a matched control-channel /
  extension-channel noise-floor pair in `umac.ko`.
- `ol_if_spectral_get_extension_channel` (`0xb222c`, 88 B) resolves the extension channel.
- Four sized symbols implement the extension-busy threshold in the channel-width manager:
  `ol_cwm_get_extbusythreshold` (`0xb0588`, 8 B), `ol_cwm_set_extbusythreshold`
  (`0xb0548`, 8 B), `cwm_get_extbusythreshold` (`0x1f55c`, 20 B) and
  `cwm_set_extbusythreshold` (`0x1f6a0`, 48 B). This is the value that decides whether a wide
  channel is kept as the secondary channel gets busy, so it is the host-side counterpart of
  refusing to widen.

One naming trap worth recording: `umac.ko` stores the knob as the eleven-character string
`extbusythres` and its accessor as `get_extbusythres`. The literal name is truncated in the
binary, and tooling that greps for `extbusythreshold` in the string table will miss it.

## thresh62

`thresh62_hits = 0` across all three modules, confirmed against every casing and every variant
(`thresh62`, `THRESH62`, `thresh_62`, `thr62`, `THR62`). This reproduces Stage 1087A, which
found `thresh62_ext` only in `ath10k_core.ko` `.rodata.str1.4`. The airOS 2.6.32 MAC stack does
not expose that knob; the extension-channel CCA threshold there is `extbusythres` plus
`CWMIgnExCCA`.

## Ownership map

| capability | owner | grade |
| :--- | :--- | :--- |
| AirView scan orchestration | `umac.ko` | CONFIRMED |
| AirView PHY event source | `ath_dev.ko` | CONFIRMED |
| AirView FFT / spectral decode | `ath_spectral.ko` | CONFIRMED (undefined imports plus `depends=`) |
| ACS channel selection | `umac.ko` | CONFIRMED |
| ACS DFS-NOL handling | `umac.ko` | CONFIRMED |
| ACS userspace ioctl | `umac.ko` | CONFIRMED |
| `airselect` identifier | none | REFUTED |
| ANI control and levels | `umac.ko` | CONFIRMED |
| ANI PHY enable | `ath_hal.ko` | CONFIRMED (undefined `ath_hal_enabledANI`) |
| CCA extension-busy threshold | `umac.ko` | CONFIRMED |
| Adjacent-channel rejection control | `umac.ko` | CONFIRMED |
| `thresh62` | `ath10k_core.ko` | REFUTED for all three modules here |
| Poll scheduling | `ubnt_poll_host.ko` | CONFIRMED |

## Copy census

The directive states 10 loose `ubnt_poll_host.ko`, 11 `umac.ko` and 11 `ath_dev.ko`. Three
censuses were run and they do not agree, so all three are reported:

| module | exact filename | filename stem | anchor symbol |
| :--- | ---: | ---: | ---: |
| `ubnt_poll_host.ko` | 7 | **10** | 8 |
| `umac.ko` | 9 | **11** | 11 |
| `ath_dev.ko` | 9 | **11** | 8 |

The directive's 10 / 11 / 11 is reproduced exactly by the filename-stem column, which also
counts renamed patched artefacts such as `wa_8725_umac_stage78b_patched.ko`. The anchor census
is neither a superset nor a subset, because the XW 2.6.32.71 family has no spectral anchors at
all. Tar members: 0 for all three, so every copy is a loose file.

## Grades and limits

`evidence_grade = A`. Every offset in the receipt comes from a symbol-table entry with a
declared size, or from a joined `R_MIPS_HI16`/`R_MIPS_LO16` relocation pair pointing at a
string. `offsets_recovered = 94`: 68 defined symbol offsets plus 26 string sites pinned to at
least one `.text` reference.

Not measured here: `ath_spectral.ko`, `ath_hal.ko`, `asf.ko` and `adf.ko` internals; the FFT
bin count and spectral payload size; the handler behind `CWMIgnExCCA`; the code offsets of the
partially stripped `umac.ko` names; and the XW 2.6.32.71 build family. Do not read the
`airview_hits = 0` count as an absence statement.

## Reproduce

```powershell
python tools/re/uph_umac_airview_acs_adjacent_channel_re_analyzer.py
```

Receipt: `artifacts/verification/stage1188a_uph_umac_airview_acs_re.json`, sha256
`5aeffc4e08bda47963b2071bcdcfddedce84dad10759f272b160a5b4372207d6`. Two consecutive runs are
byte-identical; the script renders the full analysis twice and refuses to write if the two
renders differ.
