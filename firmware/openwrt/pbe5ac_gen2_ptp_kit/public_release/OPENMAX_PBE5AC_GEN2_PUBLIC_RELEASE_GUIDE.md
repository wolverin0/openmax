<!-- doc-head: OpenMAX public dual-board PowerBeam and LiteBeam 5AC Gen2 build, wired setup and evidence boundaries -->
Public-r1 modifies pinned OpenWrt 24.10.4 with the exact Linux 6.6.110 TEB module.
Local image integrity and sanitization checks do not establish hardware acceptance.
No site credentials, captured vendor identities or remote migration profiles are included.
<!-- /doc-head -->

# OpenMAX PowerBeam & LiteBeam 5AC Gen2 public-r1

These are experimental custom OpenWrt images for **Ubiquiti PowerBeam 5AC Gen2 and LiteBeam 5AC Gen2**, target `ath79/generic`.
They are not official OpenWrt builds or Ubiquiti-signed firmware. Use only the exact matching model; no other PowerBeam, LiteBeam M5, XC or LTU is covered.

| Model | Catalog board ID | OpenWrt profile | Public filename component |
| :--- | :--- | :--- | :--- |
| PowerBeam 5AC Gen2 | `0xe3d6` | `ubnt,powerbeam-5ac-gen2` | `pbe5ac-gen2` |
| LiteBeam 5AC Gen2 | `0xe7f9` | `ubnt,litebeam-ac-gen2` | `lbe5ac-gen2` |

The IDs are hardware-catalog selectors, not new header bytes. Both official factory headers say WA;
the builder separately pins each official base, preserves its own kernel and checks its board-specific DTB.
A common WA family does not make the two images interchangeable.
The release has been built and inspected locally. Boot, flash, recovery and RF performance of these public images have **not** been verified on hardware.

## Files

The builder writes `firmware/openwrt/pbe5ac_gen2_ptp_kit/public_release/` containing:

- `openwrt-24.10.4-ubnt-pbe5ac-gen2-openmax-public-factory.bin`
- `openwrt-24.10.4-ubnt-pbe5ac-gen2-openmax-public-sysupgrade.bin`
- `openwrt-24.10.4-ubnt-lbe5ac-gen2-openmax-public-factory.bin`
- `openwrt-24.10.4-ubnt-lbe5ac-gen2-openmax-public-sysupgrade.bin`
- `SHA256SUMS`, this guide, `SOURCE_AND_LICENSES.md`, the modified module and modification sources.

For each board, factory and sysupgrade contain the same sanitized root filesystem; these are **installation formats**, not separate AP/STA credentials or roles.
Check every file with `sha256sum -c SHA256SUMS` from the release directory. On Windows, use `Get-FileHash -Algorithm SHA256` and compare the relevant checksum line.
Checksums establish content integrity, not publisher identity or a vendor signature.

## Default setup

| Setting | Public default |
| :--- | :--- |
| Wired management | **192.168.1.20/24**, hostname `OpenMAX` |
| Default gateway / DNS | No site-specific value |
| DHCP server / IPv6 RA | Disabled for initial wired setup |
| Wireless radio and interface | **Disabled** |
| Wireless role template | AP, `wds=1`, WPA2-PSK selected, **no key supplied** |
| SSID template | `OpenMAX-Setup`, inactive until configured |
| Authentication / SSH host keys | Stock OpenWrt first-setup behavior; no shared credentials or baked host keys |
| Country / DFS / power | Upstream regulatory behavior; no bypass or forced country |

Use one radio at a time on an isolated wired PoE connection. Give the computer an unused address in the same subnet and open **http://192.168.1.20/**.
Set a unique administrator password before enabling radio access. Both units initially use the same management address; assign distinct addresses before joining them to one network.
This public image deliberately has no site-specific OTA migration configuration. An unattended remote device can become unreachable after installation or a clean upgrade; initial setup requires wired access and a tested recovery plan.

## Choose AP or station

In LuCI, configure your own legal country, channel/width, SSID and unique WPA2 passphrase. Configure both peers before enabling the interfaces.
For an OpenWrt pair, choose an AP with WDS and a station with WDS, each bridged to its intended LAN. The `wds=1` setting requests four-address operation; actual association/bridge behavior still requires validation on the chosen peers.
For an airOS/OpenWrt hybrid, verify the airOS peer supports the chosen standard 802.11/WDS mode. This build does not convert an airOS peer, provide proprietary airMAX TDMA, or include captured vendor-IE admission material.
No zero-touch stock-airOS CPE interoperability or production AP migration acceptance is claimed.
Start with a legal, conservative channel plan. VHT20/40/80 and short GI are negotiated capabilities, not universally safe performance presets. Do not disable DFS or regulatory enforcement to make a link associate.

## Included changes

- The module installed at `/lib/modules/6.6.110/mac80211.ko` is exactly `mac80211_teb_6.6.110.ko`: **815640 bytes**, SHA-256 `3e3d812ff0d4a2fd1a1f9c1257a9356058ac439108e3c27ef6b11d944b696868`.
- Its ELF32 big-endian MIPS ABI is pinned to the official base: vermagic `6.6.110 mod_unload MIPS32_R2 32BIT`, module layout 352 bytes. The reproducible 21-instruction patch changes 71 bytes and handles the inner **ETH_P_TEB 0x6558** header. This does not prove general interoperability or an RF gain.
- `/usr/sbin/fmx_pbe5ac_admitter.sh`, managed by procd, discovers **`hostapd.phy*-ap0`** dynamically and maintains existing WDS AP/VLAN bridge interfaces. Hostapd retains authentication control. There are no fixed MACs, copied vendor IEs, beacon timing changes or management destinations.
- AQL limits and CoDel timing retain upstream defaults. No benchmark-specific BQL/NAPI/IRQ settings or root-qdisc replacement is installed. Generic `sch_fq_codel` target 5 ms / interval 100 ms are that qdisc's defaults, not an override of mac80211 timing.
- On 64 MiB-class devices only, the helper lowers an existing FQ memory cap above **4 MiB** and applies OOM protection `-900` to hostapd/wpa_supplicant. It never raises a smaller cap. This is a memory-stability policy, not measured QoE improvement.

Do not replace kernel/mac80211 packages independently: the patched object has an exact build ABI. A later package upgrade may replace the patch. Keep the original supported recovery image and your own backups.

## Installation boundaries

`factory.bin` is the initial-install container for a supported installation path. Confirm the exact board revision, image size, checksum and a working vendor/OpenWrt recovery procedure **before** considering a write.
Follow the device's documented supported OpenWrt installation method. If firmware rejects an unsigned/custom image, stop; this builder does not bypass signatures, secure boot or access controls.
`sysupgrade.bin` is for a matching OpenWrt installation. A clean upgrade without retaining previous configuration is required to get these public defaults; retained settings or backups can carry old addresses and credentials into any image.
Never force a board mismatch. Never write calibration, EEPROM, factory data, MAC storage, U-Boot or its environment. No installation command was executed as part of creating this release.
An integrity check is not a flash, cold-boot, recovery or physical link test. Test on a spare recoverable unit before any wider deployment.

## Rebuild locally

Use the repository builder `firmware/openwrt/pbe5ac_gen2_ptp_kit/build_public_openmax_release.py` with CPython 3.12 and the pinned native SquashFS tool bundle.
The earlier `repack_pbe5ac_squashfs.py` was not present in this checkout; this builder supplies the complete replacement recipe and does not depend on a missing temporary script.

1. Obtain all four official base images (factory/sysupgrade for each exact board) from [OpenWrt 24.10.4 ath79/generic](https://downloads.openwrt.org/releases/24.10.4/targets/ath79/generic/) and compare them with the published `sha256sums`.
2. Keep the exact base names in `firmware/openwrt/`. The builder rejects modified/private prebaked images by SHA-256.
3. Obtain `squashfs-tools-ng-1.3.2-mingw64.zip` from the [upstream Windows tools directory](https://infraroot.at/pub/squashfs/windows/), retain the ZIP and unpack it under `artifacts/verification/stage117a_tools/`.
4. The pinned ZIP hash is `891b1ed46dd856d05e429b01de2c7d86175a4c22478b5a6770f94b9c2100d0f6`. The builder also checks the executables/DLLs against that ZIP. The HTTPS sources and hashes were checked; GPG signatures were not verified in this build.
5. Run `python firmware/openwrt/pbe5ac_gen2_ptp_kit/build_public_openmax_release.py`. Existing output requires explicit `--force`.

The recipe preserves the kernel prefix, repacks XZ SquashFS with 256 KiB blocks and fixed timestamps, reconstructs factory and sysupgrade CRC wrappers, and decodes the result again for a file/mode/owner comparison. New rootfs content comes only from a fixed public allowlist. Each board is independently extracted and sanitized; the LiteBeam image is not a renamed PowerBeam image. The source archive includes each board's public payloads.
The OpenWrt-style `ENDS` suffix and `# fake certificate` metadata are format placeholders inherited from the base; they provide **no vendor authentication**.
The local build receipt is `artifacts/autoresearch/stage132a_public_lbe5ac_pbe5ac_release_receipt.json`; its detailed paths and audit TARs are local build evidence, not part of the public firmware configuration.

## Sources and redistribution

Read `SOURCE_AND_LICENSES.md`. The public bundle supplies the modification recipe, bootstrap/admitter sources, GPL text and exact original/modified module hashes. Original notices remain in the upstream filesystem.
Retain applicable notices and make complete corresponding sources available for covered components when redistributing. This guide supplies source locators and the modifications; it does not assert a blanket legal review of every upstream component.
Building this bundle does not upload it to Reddit, GitHub or another service. Publication is a separate action.
