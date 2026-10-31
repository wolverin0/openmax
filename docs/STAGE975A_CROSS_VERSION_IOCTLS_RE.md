<!-- doc-head: STAGE975A_CROSS_VERSION_IOCTLS_RE.md cross-version ioctl surface RE over available airOS/XW/LTU module trees (static only) -->

# Stage 975A - Cross-Version ioctl Surface (Static Binary RE)

Offline extraction of the ioctl surface from vendor kernel modules across every
available airOS, XW and LTU build tree. No device was contacted, no network was
used, no ioctl was issued and no firmware was written. Classification:
`CONFIRMED_STATIC_BINARY`.

- Tool: `tools/verify/verify_stage975a_cross_version_ioctls_re.py`
- Receipt: `artifacts/autoresearch/stage975a_cross_version_ioctls_re.json`
- Claim: `FMX-STAGE975A-CROSS-VERSION-IOCTLS`

## Version matrix

| Version | Build tree | Modules | Modules with ioctl | ioctl symbols | Named IOCTL tokens | Availability |
| :--- | :--- | ---: | ---: | ---: | ---: | :--- |
| airOS 8.7.11 | `airos_8_7_11_xc` | 4 | 1 | 1 | 0 | AVAILABLE (partial: 4 modules) |
| airOS 8.7.25 | `airos_8_7_25_wa` | 144 | 5 | 23 | 9 | AVAILABLE |
| airOS 8.7.25 | `airos_8_7_25_xc` | 143 | 5 | 23 | 9 | AVAILABLE |
| airOS 8.7.4cs | `airos_8_7_4cs_xc` | 143 | 5 | 23 | 9 | AVAILABLE |
| airOS 8.7.4cs | `airos_8_7_4cs_wa` | 5 | 2 | 18 | 8 | AVAILABLE (partial: 5 modules) |
| XW 6.1.4 | `xw_6_1_4` | 95 | 3 | 14 | 0 | AVAILABLE |
| XW 6.3.6 | `xw_6_3_6` | 95 | 3 | 14 | 0 | AVAILABLE |
| LTU 2.4.2 | `ltu_2_4_2_afltu` | 154 | 13 | 28 | 1 | AVAILABLE |
| LTU 2.4.2 | `ltu_2_4_2_aflturocket` | 154 | 13 | 28 | 1 | AVAILABLE |
| airOS 8.7.21 | none | 0 | 0 | 0 | 0 | ABSENT |
| LTU 2.3.1 | none | 0 | 0 | 0 | 0 | ABSENT |

Absent versions: `LTU 2.3.1`, `airOS 8.7.21`. An absent version cannot be compared at ioctl, symbol or
partition level: there is no binary to read. Both are `REFUTED` as available
inputs and are kept in the matrix so that the comparison is never silently
narrowed to the versions that happen to exist.

## Totals

| Metric | Value |
| :--- | ---: |
| Versions available | 6 |
| Versions absent | 2 |
| Build trees scanned | 9 |
| Modules scanned | 937 |
| Modules implementing ioctl | 50 |
| Shared ioctl symbols (all versions) | 0 |
| Shared ioctl symbols (full trees only) | 1 |
| Shared ioctl symbols (airOS only) | 1 |
| Union of ioctl symbols | 51 |
| Divergence count | 51 |

`Divergence count` is the union size minus the size of the set present in every
available version. The all-version intersection is empty because `airOS 8.7.11`
carries 4 modules and `LTU 2.4.2` does not implement the ath/ieee80211 stack at
all: that zero is a coverage artefact. The full-trees-only and airOS-only
intersections are the meaningful companions and are reported above.

## Per-version ioctl surface

### LTU 2.4.2

- ioctl symbols: 28, token hits: 64, modules: 26
- names: `ame_add_ioctl_callback`, `ame_core_ioctls_callback`, `ame_dev_ioctl_deregister`, `ame_dev_ioctl_register`, `ame_dev_ioctl_wCmd_deregister`, `ame_dev_ioctl_wCmd_register`, `ame_dfs_ioctl`, `ame_ioctl`, `ame_sched_ioctl_callback`, `cgrd_ioctl`, `device_ioctl_uni`, `inet6_ioctl`, `ioctl_argp`, `ioctl_buf`, `ip6mr_ioctl`, `ip_tunnel_ioctl`, `ipgre_tunnel_ioctl`, `ipv6_route_ioctl`, `ppp_async_ioctl`, `ppp_asynctty_ioctl`, `ppp_ioctl`, `ppp_net_ioctl`, `pppoe_ioctl`, `pppox_ioctl`, `pptp_ppp_ioctl`, `rawv6_ioctl`, `ssdk_miireg_do_ioctl`, `switch_ioctl`
- exported: `inet6_ioctl`, `ip_tunnel_ioctl`, `pppox_ioctl` | named tokens: `IOCTL_ETH_LINK_SUSPEND`

### XW 6.1.4

- ioctl symbols: 14, token hits: 14, modules: 3
- names: `ath_cwm_ioctl`, `ath_ioctl_debug`, `ath_ioctl_ethtool`, `ieee80211_ioctl`, `ieee80211_ioctl_chanswitch`, `ieee80211_ioctl_getmode`, `ieee80211_ioctl_getparam`, `ieee80211_ioctl_vattach`, `ieee80211_ioctl_vdetach`, `ifmedia_ioctl`, `osif_ioctl_create_vap`, `osif_ioctl_delete_vap`, `osif_ioctl_switch_vap`, `pppox_ioctl`
- exported: `ath_ioctl_debug`, `ifmedia_ioctl`, `pppox_ioctl` | named tokens: none

### XW 6.3.6

- ioctl symbols: 14, token hits: 14, modules: 3
- names: `ath_cwm_ioctl`, `ath_ioctl_debug`, `ath_ioctl_ethtool`, `ieee80211_ioctl`, `ieee80211_ioctl_chanswitch`, `ieee80211_ioctl_getmode`, `ieee80211_ioctl_getparam`, `ieee80211_ioctl_vattach`, `ieee80211_ioctl_vdetach`, `ifmedia_ioctl`, `osif_ioctl_create_vap`, `osif_ioctl_delete_vap`, `osif_ioctl_switch_vap`, `pppox_ioctl`
- exported: `ath_ioctl_debug`, `ifmedia_ioctl`, `pppox_ioctl` | named tokens: none

### airOS 8.7.11

- ioctl symbols: 1, token hits: 1, modules: 1
- names: `ath_ioctl_debug`
- exported: `ath_ioctl_debug` | named tokens: none

### airOS 8.7.25

- ioctl symbols: 23, token hits: 46, modules: 10
- names: `__adf_net_eth_ioctl`, `__adf_net_vap_ioctl`, `__adf_net_wifi_ioctl`, `ath_cwm_ioctl`, `ath_ioctl_debug`, `ath_ioctl_ethtool`, `athrs17_ioctl`, `ieee80211_ioctl`, `ieee80211_ioctl_chanswitch`, `ieee80211_ioctl_chn_n_widthswitch`, `ieee80211_ioctl_get_htc_stats`, `ieee80211_ioctl_getmode`, `ieee80211_ioctl_getparam`, `ieee80211_ioctl_send_action_frame_cb`, `ieee80211_ioctl_vattach`, `ieee80211_ioctl_vdetach`, `osif_ioctl_create_vap`, `osif_ioctl_delete_vap`, `osif_ioctl_eacs`, `osif_ioctl_get_vap_info`, `osif_ioctl_switch_vap`, `pppox_ioctl`, `wlan_ioctl_set_key`
- exported: `ath_ioctl_debug`, `pppox_ioctl` | named tokens: `ADF_NET_IOCTL_SUPPORT`, `IEEE80211_IOCTL_GETKEY`, `IEEE80211_IOCTL_GETMAC`, `IEEE80211_IOCTL_GETWPAIE`, `IEEE80211_IOCTL_GET_SCAN_SPACE`, `IEEE80211_IOCTL_RES_REQ`, `IEEE80211_IOCTL_SCAN_RESULTS`, `IEEE80211_IOCTL_STA_INFO`, `IEEE80211_IOCTL_STA_STATS`

### airOS 8.7.4cs

- ioctl symbols: 23, token hits: 41, modules: 7
- names: `__adf_net_eth_ioctl`, `__adf_net_vap_ioctl`, `__adf_net_wifi_ioctl`, `ath_cwm_ioctl`, `ath_ioctl_debug`, `ath_ioctl_ethtool`, `athrs17_ioctl`, `ieee80211_ioctl`, `ieee80211_ioctl_chanswitch`, `ieee80211_ioctl_chn_n_widthswitch`, `ieee80211_ioctl_get_htc_stats`, `ieee80211_ioctl_getmode`, `ieee80211_ioctl_getparam`, `ieee80211_ioctl_send_action_frame_cb`, `ieee80211_ioctl_vattach`, `ieee80211_ioctl_vdetach`, `osif_ioctl_create_vap`, `osif_ioctl_delete_vap`, `osif_ioctl_eacs`, `osif_ioctl_get_vap_info`, `osif_ioctl_switch_vap`, `pppox_ioctl`, `wlan_ioctl_set_key`
- exported: `ath_ioctl_debug`, `pppox_ioctl` | named tokens: `ADF_NET_IOCTL_SUPPORT`, `IEEE80211_IOCTL_GETKEY`, `IEEE80211_IOCTL_GETMAC`, `IEEE80211_IOCTL_GETWPAIE`, `IEEE80211_IOCTL_GET_SCAN_SPACE`, `IEEE80211_IOCTL_RES_REQ`, `IEEE80211_IOCTL_SCAN_RESULTS`, `IEEE80211_IOCTL_STA_INFO`, `IEEE80211_IOCTL_STA_STATS`

## Cross-version comparison

| Version | Shared with every other version | Unique to this version |
| :--- | :--- | :--- |
| LTU 2.4.2 | 0 | `ame_add_ioctl_callback`, `ame_core_ioctls_callback`, `ame_dev_ioctl_deregister`, `ame_dev_ioctl_register`, `ame_dev_ioctl_wCmd_deregister`, `ame_dev_ioctl_wCmd_register`, `ame_dfs_ioctl`, `ame_ioctl`, `ame_sched_ioctl_callback`, `cgrd_ioctl`, `device_ioctl_uni`, `inet6_ioctl`, `ioctl_argp`, `ioctl_buf`, `ip6mr_ioctl`, `ip_tunnel_ioctl`, `ipgre_tunnel_ioctl`, `ipv6_route_ioctl`, `ppp_async_ioctl`, `ppp_asynctty_ioctl`, `ppp_ioctl`, `ppp_net_ioctl`, `pppoe_ioctl`, `pptp_ppp_ioctl`, `rawv6_ioctl`, `ssdk_miireg_do_ioctl`, `switch_ioctl` |
| XW 6.1.4 | 0 | none |
| XW 6.3.6 | 0 | none |
| airOS 8.7.11 | 0 | none |
| airOS 8.7.25 | 0 | none |
| airOS 8.7.4cs | 0 | none |

airOS-only core shared by `airOS 8.7.11`, `airOS 8.7.25` and `airOS 8.7.4cs`: `ath_ioctl_debug`.

`unique_to_version` reads 0 for both XW builds and for `airOS 8.7.25` with
`airOS 8.7.4cs`, because each of those pairs is identical to its own sibling.
The family deltas carry the real difference:

| Family delta | Count | Names |
| :--- | ---: | :--- |
| XW only, relative to airOS | 1 | `ifmedia_ioctl` |
| airOS only, relative to XW | 10 | `__adf_net_eth_ioctl`, `__adf_net_vap_ioctl`, `__adf_net_wifi_ioctl`, `athrs17_ioctl`, `ieee80211_ioctl_chn_n_widthswitch`, `ieee80211_ioctl_get_htc_stats`, `ieee80211_ioctl_send_action_frame_cb`, `osif_ioctl_eacs` (+2 more) |
| LTU only, relative to airOS and XW | 27 | `ame_add_ioctl_callback`, `ame_core_ioctls_callback`, `ame_dev_ioctl_deregister`, `ame_dev_ioctl_register`, `ame_dev_ioctl_wCmd_deregister`, `ame_dev_ioctl_wCmd_register`, `ame_dfs_ioctl`, `ame_ioctl` (+19 more) |

## What the tokens mean

The named identifier tokens are the driver's own printed ioctl names, recovered
from `.rodata.str*` string tables. `IEEE80211_IOCTL_*` names are wireless ioctl
commands; `ADF_NET_IOCTL_SUPPORT` is a feature flag rather than a command, and
`IOCTL_ETH_LINK_SUSPEND` on LTU is a switch-driver command. They are reported
together because the same scanning rule finds them, and each is listed verbatim
so the distinction stays visible.

Numeric `_IOW`/`_IOR`/`_IOWR` values are compile-time integer immediates. They
appear in neither the symbol table nor the string table, so this stage does not
claim any numeric command value. Recovering those requires disassembling each
handler switch, which is listed as a gap.

## Findings

1. `airOS 8.7.25` WA, `airOS 8.7.25` XC and `airOS 8.7.4cs` XC expose identical
   identical 23-name ioctl sets. The airOS wireless ioctl surface did not change
   between 8.7.4cs and 8.7.25, and the 5-module 8.7.4cs WA subset adds no name
   beyond that set.
2. `airOS 8.7.11` carries exactly one ioctl symbol, `ath_ioctl_debug`, because
   only 4 of its modules are on disk: a coverage limit, not a regression.
3. `XW 6.1.4` and `XW 6.3.6` carry the same 14-name set. Relative to airOS, XW
   adds exactly one name, `ifmedia_ioctl`, and carries none of the ten
   airOS-only names (`__adf_net_*` trio, `athrs17_ioctl`, the three extra
   `ieee80211_ioctl_*` handlers, `osif_ioctl_eacs`, `osif_ioctl_get_vap_info`,
   `wlan_ioctl_set_key`).
4. `LTU 2.4.2` is structurally different: the ioctl surface lives in `ame_*`
   and in the PPP / IP-tunnel / switch modules, with registration and
   de-registration callbacks (`ame_dev_ioctl_register`,
   `ame_dev_ioctl_wCmd_register`) instead of a single wireless handler. It shares
   only `pppox_ioctl` with the airOS builds; the other 27 LTU names are LTU-only.
5. `eab_driver.ko` does not exist anywhere in the corpus, so the LTU ioctl
   telemetry path documented in earlier stages has no binary to compare.

## Excluded duplicate tree

- `artifacts/autoresearch/waves_abcd_20261024/wave_a_wa/complete_rootfs_r2/staging_4c809c4d5fe845f193481bb6f8a78ea9/lib/modules/2.6.32.68` (144 modules) is byte-identical to `airos_8_7_25_wa` and is excluded from every count: re-extraction of firmware/WA.8.7.25.bin; despite the wave_a_wa directory name it is NOT an 8.7.4cs set.

## Gaps

- airOS 8.7.21 is absent from the corpus (0 files), so its ioctl surface cannot be compared. The version is REFUTED as an available input.
- LTU 2.3.1 is absent from the corpus (0 files), so its ioctl surface cannot be compared. Same refutation.
- Numeric _IOW/_IOR/_IOWR command values are compile-time immediates and are not recoverable from these symbol or string tables. Only handler names and printed identifier tokens are measured here.
- airOS 8.7.11 contributes 4 modules and airOS 8.7.4cs WA contributes 5, so those two versions are only partially observable and cannot carry a full ioctl comparison.
- The all-version intersection of ioctl symbols is empty for coverage reasons (partial 8.7.11 tree plus a non-overlapping LTU stack), not because the airOS builds diverged.
- Presence of a handler symbol is static linkage evidence. It does not prove the handler is registered in file_operations at runtime or that its command switch accepts a given command.
- No live ioctl was issued against any radio; every statement here is static-only and no behavioural equivalence is claimed.

## Reproduce

```
python tools/verify/verify_stage975a_cross_version_ioctls_re.py
```

