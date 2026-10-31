<!-- doc-head: Stage1189A static binary RE of ath10k_core.ko showing why WMI command-name strings do not exist there, which survey overrides and vdev-start/CSA strings do, and that the OpenWrt 24.10.5 label has no artefact behind it -->
# Stage 1189A - ath10k_core.ko survey, spectral and channel-switch surfaces

Evidence class `CONFIRMED_STATIC_BINARY`. Static analysis only: no module loaded, no radio
contacted, no firmware written, no live address used, no socket opened. `radio_safety:
"static only"`.

## Binary and provenance

| field | value |
| :--- | :--- |
| path | `artifacts/firmware_re_ath10k_tar/ath10k_core.ko` |
| bytes | 600808 |
| sha256 | `d7f2d1ac07a6c91fe4284eac37bbe92e822b276a59928946ff86cb9da00ddf84` |
| provenance | `tar_member:artifacts/verification/stage117a_build/stock.tar:./lib/modules/6.6.110/ath10k_core.ko` |
| ELF | ELF32 MSB `ET_REL`, `EM_MIPS` |
| vermagic | `6.6.110 mod_unload MIPS32_R2 32BIT` |
| depends | `mac80211,cfg80211,ath,hwmon,compat` |
| loose copies in corpus | 1 |

The loose file and the tar member hash identically, so the dissected artefact is the one the
provenance string names, and 600808 matches the byte count in the directive.

## The 24.10.5 label does not exist

`label_24_10_5_verified = 0`. Zero filenames anywhere in the corpus carry `24.10.5`, while 171
filenames carry `24.10.4`. The decisive artefact is inside the same tar as the module: its own
`./etc/openwrt_release` reads

```
DISTRIB_ID='OpenWrt'
DISTRIB_RELEASE='24.10.4'
DISTRIB_REVISION='r28959-29397011cc'
DISTRIB_TARGET='ath79/generic'
DISTRIB_ARCH='mips_24kc'
DISTRIB_DESCRIPTION='OpenWrt 24.10.4 r28959-29397011cc'
```

and `./etc/openwrt_version` reads `r28959-29397011cc`. `supported_label` is therefore
`OpenWrt 24.10.4 r28959-29397011cc`, sourced from
`artifacts/verification/stage117a_build/stock.tar::./etc/openwrt_release`.

Note the measurement boundary: only filenames were censused. A document that mentions
`24.10.5` in prose is not an artefact and was not counted, so this verdict says "no artefact",
not "no mention anywhere".

## Build identity

`build_identity = ath10k-ct-2024.07.30~ac71b14d, source ath10k-6.10, profile
ath10k-ct-smallbuffers, target ath79/generic, mips_24kc`.

That string is assembled from source-path literals embedded by the compiler, for example
`target-mips_24kc_musl/linux-ath79_generic/ath10k-ct-smallbuffers/ath10k-ct-2024.07.30~ac71b14d/ath10k-6.10/wmi.c`.
This reproduces Stage 1103A's identity from the binary itself rather than from a manifest.## Why the command names are absent

`wmi_chan_info_hits = 0`. `WMI_CHAN_INFO_EVENTID` has 0 exact-name string sites, 0 strings
containing it, and 0 raw byte occurrences in the 600808-byte file. The same holds for
`WMI_VDEV_START_REQUEST_CMDID`, `time_busy`, `time_rx` and `time_tx`.

This is not an accident of this one name. All 122 printable `WMI_` strings in the module are
`WMI_SERVICE_*` service-bit names: 0 end in `_CMDID`, 0 end in `_EVENTID`, and 0 fall outside
the `WMI_SERVICE_` prefix. ath10k addresses WMI with numeric enum constants that the compiler
inlines as immediates, so the binary has no reason to retain a command name, and it did not.

Two consequences are stated plainly rather than papered over. The numeric value of the CHAN_INFO
event id is UNKNOWN: there is no `.debug_*` and no `.BTF` section in this module, the enum
header `ath10k-6.10/wmi.h` is not in the corpus, and a compiled object carries neither, which is
why `C-1189A-03` is graded UNKNOWN. And a command-name string is not a command layout: even had
a name been present it would not have given the payload record layout or the argument order, so
no layout is asserted anywhere in the receipt.

## Survey quantities

`survey_field_tokens` is a 16-key object. The part that carries information is a five-name
cluster of ath10k-ct debug overrides in `.rodata`, sixteen bytes apart, one struct member per
slot:

| name | offset | role |
| :--- | ---: | :--- |
| `d_noise_floor` | `0x2c80` | substitutes the firmware-reported noise floor |
| `d_cycle_count` | `0x2ca0` | total cycle counter |
| `d_tx_cycle_count` | `0x2cc0` | transmit cycle counter |
| `d_rx_cycle_count` | `0x2ce0` | receive cycle counter |
| `d_busy_count` | `0x2d00` | busy counter |

Forty-nine further `d_*` counters follow in the same struct. `mac80211`'s own member names
(`time_busy`, `time_rx`, `time_tx`) are absent, and their absence carries no information: C
does not emit struct member names without debug information, and this module has none. The
survey mechanism itself is present and referenced: `bss channel survey timed out\n` at
`.rodata.str1.4+0x458` carries one resolved `.text` reference, and `d_noise_floor` is one of the
16 `__param` entries.

Grade: CONFIRMED for the five names and their offsets, INFERRED for mapping that triple onto
`time_busy` / `time_rx` / `time_tx`. The arithmetic is not recovered and is not claimed.

## vdev start

`vdev_start_hits = 5`. Five distinct strings pin the vdev life-cycle, each with its own
section, offset and `.text` reference list:

| offset | string | references |
| ---: | :--- | ---: |
| `0xd1c` | `failed to start WMI vdev %i: %d` | 1 |
| `0xda8` | `failed to stop WMI vdev %i: %d` | 1 |
| `0x2060` | `failed to create WMI vdev %i: %d` | 1 |
| `0x2804` | `failed to delete WMI vdev %i: %d` | 1 |
| `0xc5f4` | `failed to parse vdev start event: %d` | 1 |

All offsets are `.rodata.str1.4`. The fifth line is the informative one for the evaluator: the
host parses the **vdev-start event** as well as sending the command, so the start handshake is
two-sided and observable on the host. What is not recovered is the request argument order,
because that lives in the enum and struct headers.

## Channel switch

`chan_switch_symbols` has four entries, all string-level:

| mechanism | offset | references | string |
| :--- | ---: | ---: | :--- |
| `csa_beacon_template_update` | `0x5b8` | 0 | `failed to update bcn tmpl during csa: %d` |
| `csa_probe_response_template_update` | `0x5e4` | 2 | `failed to update prb tmpl during csa: %d` |
| `csa_offload_service_bit` | `0x5fbc` | 0 | `WMI_SERVICE_CSA_OFFLOAD` |
| `restart_channel_service_bit` | `0x66bc` | 0 | `WMI_SERVICE_RESTRT_CHNL_SUPPORT` |

The two template-update strings are the actual host-side channel-switch mechanic on an AP: the
beacon and probe-response templates are rewritten when a CSA is issued. The two service-bit
names are names only, and the stage says so rather than promoting them into a firmware
capability claim.

One coverage limit is recorded in the receipt: `ath10k_core.ko` has no symbol entry in the
first 32800 bytes of its 350960-byte `.text`, so the reference at `.text+0x221c` is reported
with containment `before_first_symbol_entry` instead of being attributed to a neighbouring
function.

## Spectral, and what is not here

`ath10k_core.ko` carries no AirView and no spectral-scan code. Every one of the four strings
matching a spectral needle is a service-bit name:
`WMI_SERVICE_AUX_CHAN_LOAD_INTF`, `WMI_SERVICE_AUX_SPECTRAL_INTF`,
`WMI_SERVICE_BSS_CHANNEL_INFO_64` and `WMI_SERVICE_PERIODIC_CHAN_STAT_SUPPORT`. The AirView
implementations are the airOS `spectral` stack recorded in Stage 1188A, not this driver.

`thresh62` is present, and it is the only place in the corpus it appears:
`thresh62_ext` at `.rodata.str1.4+0x5c8c` and
`Only CT firmware supports this method of setting thresh62_ext.` at `.rodata.str1.4+0xd27c`.
That matches Stage 1087A's attribute block and confirms the knob is a Candela ath10k-ct
extension, not an airOS 2.6.32 knob.

## Symbol table shape

1965 symtab entries: 1631 `STT_NOTYPE`, 286 `STT_FUNC`, 39 `STT_OBJECT`, 9 `STT_SECTION`.
324 local function names are anonymised to `_<n>` and 0 symbols start with `ath10k`. The 61
real names survive only through `__ksymtab_strings` (`ath10k_core_start`, `ath10k_ce_send`,
`ath10k_htt_t2h_msg_handler` and so on), and none of them is a WMI entry point. Every handler in
this receipt is therefore reported by anonymised symbol plus section-relative offset and
declared size, never by a guessed name.

## Grades and limits

`evidence_grade = A`. `offsets_recovered = 139`: 122 `WMI_` name offsets, the string sites
pinned to at least one `.text` reference, and the reference sites themselves. The label verdict
is also grade A because it rests on first-party release metadata shipped in the same tar as the
module.

Not measured or not recoverable: the CHAN_INFO event id value; the CHAN_INFO payload and
VDEV_START_REQUEST layouts; the arithmetic that turns cycle counts into survey members; any DFS
timing, since `dfs_pattern_detector` is imported and was not dissected. Stage 1087A also
recorded a live module of 548864 bytes against this 600808-byte artefact, so the running
module is still not proven identical to the dissected one.

## Reproduce

```powershell
python tools/re/ath10k_survey_spectral_chan_switch_re_analyzer.py
```

Receipt: `artifacts/verification/stage1189a_ath10k_survey_spectral_re.json`, sha256
`ee778798827852a00c68b19ff5405a3f670a4db6ed351e9c63bf206fe1db7cbf`. Two consecutive runs are
byte-identical: the script renders the full analysis twice and refuses to write on any mismatch.
