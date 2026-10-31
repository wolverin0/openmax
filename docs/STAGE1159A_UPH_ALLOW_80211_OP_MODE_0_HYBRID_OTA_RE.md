<!-- doc-head: Stage 1159A - ubnt_poll_host.ko allow_80211 / op_mode hybrid OTA interop, static binary RE, offline, no radio -->
# Stage 1159A - `ubnt_poll_host.ko` `allow_80211` / `op_mode` Hybrid OTA Interop

**Provenance class:** `CONFIRMED_STATIC_BINARY`
**Radio safety:** static only. No SSH, no live IP, no firmware write, no target execution.
**Receipt:** `artifacts/verification/stage1159a_uph_allow_80211_hybrid_ota_re.json`
**Tool:** `tools/re/uph_allow_80211_hybrid_ota_re_verifier.py`
**Reproduce:** `python tools/re/uph_allow_80211_hybrid_ota_re_verifier.py --verify-determinism`

## 1. Question under test

The OTA staged PtP conversion plan asserts that an airOS 8 AP can be placed in a
hybrid mode, `allow_80211=1` with `op_mode=0`, so that a repacked OpenWrt STA can
associate over a plain 802.11 path driven by `uph.ko` CSMA/CA WDS, while stock
airOS 8 CPEs keep working. That plan is executable only if some host artifact
exposes those controls and an 802.11, non-proprietary, association path.

This stage measures whether `ubnt_poll_host.ko` is that artifact. It is not.

## 2. What is actually present

| Claim | Result | Label |
| :--- | :--- | :--- |
| Loose `ubnt_poll_host.ko` copies | 10 (7 canonical name, 3 renamed or patch-suffixed) | CONFIRMED |
| Distinct binaries after sha256 dedupe | 8 | CONFIRMED |
| airOS 8.7.11 present | yes, 4 modules at `artifacts/firmware_re_xc_ltu/2xc_8711_modules/` | CONFIRMED |
| airOS 8.7.25 present | yes, `wa_8725_rootfs` and `xc_8725_rootfs` | CONFIRMED |
| airOS 8.7.4-cs present | yes, `xc_874cs_rootfs` and `wa874cs_modules` | CONFIRMED |
| airOS 8.7.15 present | 0 filename hits, 0 tar members, 0 extracted trees | REFUTED |
| Tar archives scanned | 141, 209121 members, 0 unreadable | CONFIRMED |

Version comparison is therefore **8.7.11 versus 8.7.25**, with 8.7.4-cs as a third
build. The directive's 8.7.15 does not exist in this repository and is not
substituted by a nearby version.

The eight distinct binaries are not eight releases. Three share size and symbol
count with a version-confirmed build but differ in hash, so they are reported as
same-shape siblings with `family_attribution` set to `UNKNOWN` rather than being
promoted to versions.

| sha256 prefix | size | symbols | version label |
| :--- | ---: | ---: | :--- |
| `1829cf8e5a282fb1` | 186560 | 443 | airOS 8.7.11 |
| `a5f705ecf7d1fa58` | 186560 | 443 | airOS 8.7.4-cs |
| `d662330985464263` | 186560 | 443 | airOS 8.7.4-cs |
| `19f379b1a7766036` | 186528 | 443 | UNKNOWN |
| `bfc3f499a0867669` | 189880 | 457 | airOS 8.7.25 (WA) |
| `d327c4c8190b7c22` | 189880 | 457 | airOS 8.7.25 (XC) |
| `6684c768e42062c8` | 189880 | 457 | UNKNOWN |
| `88595c2118a8aec2` | 189880 | 457 | UNKNOWN |

All are MIPS32 big-endian, `EM_MIPS`, ELF class 32.

## 3. The control tokens are absent

Case-insensitive raw-byte census over the full file bytes of every distinct
binary, summed across all eight:

| Token | Raw hits | Symbol hits | Label |
| :--- | ---: | ---: | :--- |
| `allow_80211` | 0 | 0 | REFUTED |
| `op_mode` | 0 | 0 | REFUTED |
| `wds` | 0 | 0 | REFUTED |
| `4addr` | 0 | 0 | REFUTED |
| `four_addr` | 0 | 0 | REFUTED |
| `bridge` | 0 | 0 | REFUTED |
| `mesh` | 0 | 0 | REFUTED |
| `802.11` (literal) | 0 | 0 | REFUTED |
| `80211` | 40 | 40 | CONFIRMED but not a knob |

The 40 `80211` hits are five imported symbols repeated per binary:
`ieee80211_find_node`, `ieee80211_free_node`, `ieee80211_indicate_node_assoc`,
`ieee80211_kick_node`, `ieee80211_mlme_sta_bmiss_ind`. These are callouts from
the proprietary 802.11 stack, not configuration controls, and must not be read as
mac80211 involvement.

`offsets_recovered` sums to 3172 symbol offsets across the eight binaries.

## 4. Where the tokens actually live

Attribution pass over 1161 loose kernel modules and the userspace `bin`/`sbin` of
every extracted airOS rootfs tree:

| Token | Kernel module owner | Userspace owner | Label |
| :--- | :--- | :--- | :--- |
| `allow_80211` | none (0 of 1161 modules) | `bin/wpad` in all three rootfs trees | CONFIRMED |
| `op_mode` | `umac.ko` (8 copies) | `bin/wpad`, `bin/ubntbox` | CONFIRMED |

The consequence is direct. `allow_80211` is a supplicant option read by `wpad`,
and `op_mode` is consumed by `umac.ko`, the proprietary QCA and Ubiquiti 802.11
stack. Neither is a `ubnt_poll_host.ko` knob, so no build of the host polling
module can be configured into a hybrid 802.11 association mode by setting them.

## 5. Control surface `ubnt_poll_host.ko` does expose

Fifteen confirmed channels, from defined symbols and their imports. Offsets are
ELF `st_value`, `.text`-relative.

| Mechanism | Symbol | Offset | Size |
| :--- | :--- | ---: | ---: |
| char device | `ubnt_poll_host_init_char_dev` | `0x1c30` | 76 |
| char device | `ubnt_poll_host_uninit_char_dev` | `0x1c7c` | 12 |
| hook registration | `ubnt_poll_host_install_hooks` | `0xe40` | 120 |
| hook registration | `ubnt_poll_host_uninstall_hooks` | `0xeb8` | 120 |
| sysctl | `ubnt_poll_host_init_proc_sysctl` | `0x1bfc` | 40 |
| sysctl | `ubnt_poll_host_uninit_proc_sysctl` | `0x1c24` | 12 |

Imports include `register_chrdev_region`, `cdev_init`, `cdev_add`,
`proc_create_data` and `register_sysctl_table`. The module therefore has a real
char-device and sysctl surface, and it registers scheduler hooks. What it does
not have is any token, symbol or string that selects an 802.11 association path.
Enumerating this surface is CONFIRMED. Whether an unlisted ioctl command ID could
flip association mode is UNKNOWN, because ioctl command IDs were not reversed.

## 6. Verdict

`hybrid_path_confirmed = 0`.

The directive's premise is REFUTED at the host module layer: `ubnt_poll_host.ko`
contains neither token and exposes no control that would enable a non-proprietary
802.11 association path. The hybrid OTA Step 1 cannot be justified from this
module, and no amount of re-parameterising it will produce the behaviour the plan
assumes.

This does not by itself refute that an airOS 8 AP could accept an OpenWrt STA.
It refutes only that this module is the lever. Live association behaviour remains
UNKNOWN and untested.

## 7. Gaps

1. airOS 8.7.15 is absent from the repository, so the comparison is 8.7.11 versus
   8.7.25 by necessity, not by choice.
2. `allow_80211` was located in `bin/wpad` by string presence only. The option's
   parsing and its effect on association are UNKNOWN.
3. `op_mode` was located in `umac.ko` by string presence only. Which values it
   accepts and what it changes are UNKNOWN.
4. Three of the eight distinct binaries carry no version label. Their family is
   INFERRED from size and symbol count, and their exact origin is UNKNOWN.
5. Static string absence cannot exclude a control implemented purely as a numeric
   ioctl command. Command IDs were not reversed here.
6. No live association, no radio interaction and no firmware write occurred.

## 8. Claim ledger

- CONFIRMED: 10 loose copies, 8 distinct binaries, 141 tars and 209121 members
  scanned, zero hits for `allow_80211`, `op_mode`, `wds`, `4addr`, `bridge`,
  `mesh`, zero `wds` symbols, 15 control channels, token ownership as tabulated.
- REFUTED: airOS 8.7.15 presence; the existence of these tokens in
  `ubnt_poll_host.ko`; a hybrid 802.11 path reachable from this module.
- INFERRED: build family of the three unlabelled binaries.
- UNKNOWN: ioctl command semantics, `wpad` and `umac.ko` runtime behaviour, live
  interop outcome.
