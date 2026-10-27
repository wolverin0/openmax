<!-- doc-head: OpenMAX public-v3 four-board WA candidates, experimental champion and wired setup -->
Eight locally verified installation candidates use exact OpenWrt 24.10.4 board kernels.
The authorized-gated mac80211 v3 patch and opt-in R1..R12 queue profile are included.
Image integrity is not hardware boot, recovery, security or RF acceptance.
<!-- /doc-head -->

# OpenMAX WA public-v3

Experimental custom OpenWrt 24.10.4, Linux 6.6.110, `ath79/generic`.
These are neither official OpenWrt builds nor Ubiquiti-signed firmware.

| Model | Catalog board IDs | OpenWrt compatible | Filename component |
| :--- | :--- | :--- | :--- |
| PowerBeam 5AC Gen2 | `0xe3d6` | `ubnt,powerbeam-5ac-gen2` | `pbe5ac-gen2` |
| LiteBeam 5AC Gen2 | `0xe7f9` | `ubnt,litebeam-ac-gen2` | `lbe5ac-gen2` |
| LiteAP AC LAP-120 | `0xe7f5`, `0xe8e5` | `ubnt,lap-120` | `lap-120` |
| NanoStation 5AC Loco | `0xe7f7`, `0xe7fa` | `ubnt,nanostation-ac-loco` | `nanostation-ac-loco` |

The aliases are catalog mappings supplied for this release, not independent physical qualification of every revision.
Common WA factory headers do not distinguish these models. Each image retains its own official kernel/DTB and supported-device metadata; never interchange them or force a mismatch.

## Files and first setup

`firmware/openwrt/pbe5ac_gen2_ptp_kit/public_release_v3/` contains eight images:
`openwrt-24.10.4-ubnt-<filename component>-openmax-public-factory.bin` and
`openwrt-24.10.4-ubnt-<filename component>-openmax-public-sysupgrade.bin` for each row above.
Factory/sysupgrade are installation formats, not AP/STA roles. Each pair contains the same public rootfs.
The directory also includes `SHA256SUMS`, sources, GPL text, the module, this guide and `BENCHMARK_EVIDENCE_AND_LIMITS.json`.
Run `sha256sum -c SHA256SUMS` there; on Windows compare `Get-FileHash -Algorithm SHA256` with its entry.
Checksums identify bytes, not a publisher or a vendor signature.

- Wired management: **192.168.1.20/24**, hostname `OpenMAX`; no site gateway/DNS.
- DHCP server/IPv6 RA, Wi-Fi radio and Wi-Fi interface: **disabled** initially.
- Inactive AP template: `OpenMAX-Setup`, WPA2-PSK, `wds=1`, **no supplied key**.
- Stock first-setup administrator behavior; no embedded administrator credentials or SSH host/private keys.
- No laboratory addresses, fixed peer identities, captured vendor IEs or remote-migration/watchdog profiles.

Connect one unit at a time over isolated wired PoE. Give the computer an unused address in the same subnet and open **http://192.168.1.20/**.
Set a unique administrator password and unique management addresses before joining multiple units.
Configure the legal country, channel/width, distance/coverage, SSID and your own WPA2 key before enabling wireless.
For a standard OpenWrt pair, configure AP with WDS and station with WDS, bridged to their intended LANs.
An airOS peer needs separately supported standard 802.11/WDS operation; proprietary airMAX TDMA and stock-airOS zero-touch interoperability are not supplied or claimed.
No public-image boot, cold-boot persistence, recovery or link performance has been physically verified here.

## mac80211 v3

`/lib/modules/6.6.110/mac80211.ko` is exactly `mac80211_teb_4addr_v3_6.6.110.ko`, **815640 bytes**:
SHA256 `fe4f730fccaa68848a70c952e40c0438b32d413993f22887a0e72fed5eebaae6`.
The builder reproduces it from each pinned stock module: 21-instruction ETH_P_TEB `0x6558` patch plus 13 authorized-gated 4-address event instructions; **113 changed bytes** overall.
ELF32 big-endian MIPS, vermagic `6.6.110 mod_unload MIPS32_R2 32BIT `, module layout **352 bytes**.
The v3 event path preserves LL/SC and the cfg80211 event relocation. It gates the AP_VLAN event on the station authorization flag; it is not an EAPOL-only filter or proof of general RX security.
Do not substitute another “v3” module or independently upgrade kernel/mac80211 packages. The historical live-unit variant has different bytes.
The public admitter discovers `hostapd.phy*-ap0` dynamically and bridges existing WDS interfaces; hostapd retains authentication.

## Experimental R1..R12 champion

The installed `/etc/hotplug.d/net/99-fmx-wa-universal-champion` is a public OpenWrt-only adaptation of the pinned latest source, with **AP quantum=3028 / STA quantum=1514 bytes**.
It is **opt-in**: `/etc/openmax/champion.conf` starts with `enabled=0`.
After wired setup and peer configuration, set that entry to `enabled=1` and start `/etc/init.d/openmax-champion` to request the profile.
Net hotplug and boot then reapply it. Disable the entry and reboot to return to upstream transient queue settings; changing the flag alone does not undo an already applied profile.

| Configured queue policy | Value |
| :--- | :--- |
| AQL VO / VI / BE / BK low/high | `300/600`, `1000/2000`, `1500/3000`, `500/1000` microseconds |
| AQL threshold | `4500` microseconds |
| FQ limit / memory | `1024` / `3145728` bytes |
| eth0 BQL min / max / hold | `4542` / `36288` / `600` (kernel interface units) |
| dev_weight / netdev_budget / budget_usecs / TX bias | `48` / `480` / `6000` / `2` |
| TCP notsent / output limit / backlog / tx_queue_len | `8192` / `65536` / `1500` / `256` |

The script requires an allowed board and OpenWrt debugfs. Missing debugfs never selects an airOS implementation.
It resolves AP/STA per PHY, skips unknown or mixed roles, locks concurrent hooks and leaves `/var/run/openmax-champion/status` with requests, errors and raw getters. Exit 0 is **not** application acceptance; kernel setters may clamp values.
No airOS commands, filter flushing, process termination, regulatory bypass or persistent country/power/channel/width/beacon/coverage changes are included. RF-related defaults from the original source remain references only.
Upstream AQL/CoDel timing remains until opt-in; the existing 64-MiB resource guard only lowers FQ memory above 4 MiB and protects authentication daemons from OOM selection.

The saved 48 windows are twelve different four-window comparisons on one LAP-to-Loco link; they are not twelve repetitions proving all four boards.
R12 **retained stock**: aggregate goodput `51.491 -> 56.554 Mbps`, p95 `65.197 -> 90.885 ms`, p99 `75.581 -> 90.885 ms` for stock versus cumulative profile. Short windows and small RTT samples limit tail interpretation.
Stage140A configured TCP output/backlog `65536/1500`, while its final raw getters contain `98304/1000`; copied `configured` fields named `knob_readback` are not independent measurements.
These contradictions and decisions remain in `BENCHMARK_EVIDENCE_AND_LIMITS.json`. No universal throughput/latency improvement is claimed for this public adaptation.

## Build and installation boundaries

Use `build_public_openmax_release.py` in the source repository with CPython 3.12.
Keep all eight exact official base images in `firmware/openwrt/`; published checksums are at [OpenWrt 24.10.4 ath79/generic](https://downloads.openwrt.org/releases/24.10.4/targets/ath79/generic/sha256sums).
Retain the pinned champion/module/public assets and the four saved benchmark inputs referenced by the builder. The R1..R12 input is frozen in `public_assets/99-fmx-wa-universal-champion.r1-r12.source.txt`; a later mutable champion is never substituted. Its unmodified historical source reference is included only under `sources/`, never installed or executed. Inherited claims in that reference are not public-release acceptance.
Native backend: `squashfs-tools-ng-1.3.2-mingw64.zip`, SHA256 `891b1ed46dd856d05e429b01de2c7d86175a4c22478b5a6770f94b9c2100d0f6`, from the [upstream Windows directory](https://infraroot.at/pub/squashfs/windows/), unpacked under `artifacts/verification/stage117a_tools/`.
Run `python firmware/openwrt/pbe5ac_gen2_ptp_kit/build_public_openmax_release.py`; existing output needs explicit `--force`.
The fixed recipe verifies pins/ABI/DTB, repacks XZ with fixed timestamps, rebuilds CRCs and rereads files/modes/owners from the actual emitted images. Two isolated builds test reproducibility.
Receipt: `artifacts/autoresearch/stage144a_public_wa_4board_release_v3_receipt.json`. Historical public-r1 outputs are retained separately.
HTTPS checksum comparison was performed; **GPG signatures were not verified**. OpenWrt-style ENDS/fake-certificate wrappers do not authenticate firmware.

Before any installation, independently confirm exact revision, checksum, backups and a recoverable supported installation path on a spare unit.
Factory is for a supported initial-install path; sysupgrade is for the matching OpenWrt board. Retained settings/backups can carry old secrets and addresses; public defaults require a clean installation.
If custom firmware is rejected, stop. Never bypass signatures/access controls or force a board mismatch. Never write calibration, EEPROM, factory/MAC storage, bootloader or environment.
No flash commands, radio access or publication are performed by this builder.
Read `SOURCE_AND_LICENSES.md`; retain notices and provide complete corresponding sources for covered components when redistributing. Source locators/modification recipes are supplied; a complete redistribution/license audit is not established.
