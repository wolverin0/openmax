<!-- doc-head: Public WA tester v4, qualified champion-v2 configuration and local build evidence -->
Four board-specific pairs use official OpenWrt 24.10.4 kernels and the pinned mac80211 v3 patch.
Desired v2 settings are included without claiming actuator or physical benchmark acceptance.
All tuning is opt-in; wired first setup and regulatory protections remain.
<!-- /doc-head -->

# OpenMAX public WA tester v4

This experimental package covers PowerBeam 5AC Gen2, LiteBeam 5AC Gen2, LAP-120 and NanoStation 5AC Loco.
Each has its own factory/sysupgrade image and official kernel/DTB. Board catalog aliases do not establish physical acceptance of every revision.
It is neither an official OpenWrt build nor Ubiquiti-signed firmware. Never interchange models or force a board mismatch.
The base is OpenWrt 24.10.4, Linux 6.6.110, with the generic authorized-gated mac80211 v3 module SHA256 `fe4f730fccaa68848a70c952e40c0438b32d413993f22887a0e72fed5eebaae6`.

## First setup and files

Files are in `firmware/openwrt/pbe5ac_gen2_ptp_kit/public_release_v4/`.
Both `SHA256SUMS.txt` and `SHA256SUMS` are verified by the packager. The latter additionally binds the former; neither hashes itself.
Check with `sha256sum -c SHA256SUMS.txt` and `sha256sum -c SHA256SUMS` from that directory.
Checksums establish content integrity, not publisher authentication.

Wired management is **192.168.1.20/24**, hostname `OpenMAX`; DHCP/IPv6 RA and Wi-Fi are initially disabled.
Use one unit at a time on isolated wired PoE, set your own administrator password, distinct management address, legal country/channel/width, SSID and unique WPA2 key.
The inactive wireless template has WDS enabled and no supplied key. No site gateway, captured vendor IE, fixed peer or remote migration watchdog is included.
AP and station are user-selected roles; factory/sysupgrade denote installation formats.
No radio, flash, reboot or upload is performed by the local builder.

## Desired champion-v2 settings

`REQUESTED_PROFILE.json` and `/etc/openmax/champion-v2.json` contain:

| Setting | Desired value |
| :--- | :--- |
| vm.min_free_kbytes | 4096 |
| AQL threshold | 4000 microseconds |
| distance | 300 metres |
| TCP pacing CA / SS ratio | 110 / 150 |
| fq initial_quantum | 3028 bytes |
| packet_steering / flow_offloading | 1 / 1 |
| nf_conntrack_max | 16384 |

The queue recipe retains AP/STA FQ quantum3028/1514, AQL VO300/600, VI1000/2000, BE1500/3000, BK500/1000, FQ limit1024/memory3MiB, Ethernet fq_codel quantum1514/target5ms/interval100ms/ECN and BQL4542/36288/600.
These are requested experimental settings, not readbacks or universal safe performance claims.
All four `/etc/openmax/champion.conf` switches start at0:

- `enabled`: apply the host queue/VM/TCP profile after a known AP/STA role exists.
- `distance_enabled`: additionally request300m on the recognized active PHYs; choose a distance suitable for your actual link.
- `forwarding_enabled`: stage packet steering and software offload UCI settings. Network/firewall restart is required; no automatic reload or filter flushing occurs.
- `fq_pacing_enabled`: separately experiment with **sch_fq**, including initial_quantum3028. It replaces the fq_codel root qdisc and is not the same queue recipe.

Enable only the intended options after wired setup, then start `/etc/init.d/openmax-champion`. Disabling a flag alone does not undo earlier transient settings; disable and reboot to restore upstream transient queues. Staged UCI changes persist and must be restored separately.
Raw requests/errors/getters are in `/var/run/openmax-champion/status`; exit0 does not mean the requested state took effect.
The official base inventories have **no tc executable or sch_fq module file**. Builtin/loadable support is unverified. Qdisc experiments require a matching target `tc` package and kernel capabilities installed by the tester; this package does not supply or install those dependencies.
Unsupported commands are recorded as failures, never evidence of a successful actuator.
Do not infer true offload activation from nf_conntrack_max, or multiple-CPU execution from RPS mask1. Offload can bypass queueing/shaping and needs its own validation.

## What the saved evidence establishes

`CHAMPION_V2_EVIDENCE.json` pins the saved objects: **18 RF comparisons/72 windows plus one E2E comparison/4 windows**, total76 saved windows.
It does not combine them into18 homogeneous76-window rounds or establish the same result across four boards.
Stage161 requested initial_quantum on fq_codel with errors suppressed; no successful actuator/qdisc getter was demonstrated.
The Stage162 runner varied conntrack sizing under the flow_offloading label, without demonstrating an activated flowtable. Its auxiliary Boca ping fields use999 sentinels with samples1; the claimed end-to-end route/RTT benefit is **unproven**.
Copied configured fields are not independent readbacks. Earlier R12 tail regressions, R15 retained-arm settings and later consolidation differences remain qualified.
No new RF measurements, performance improvements, security acceptance, cold boot or recovery are claimed by packaging these files.

## Build and redistribution

Run `python tools/firmware/package_public_wa_tester_release.py` locally. Existing output requires `--force`.
This adapter creates the missing named packager using the existing verified native SquashFS recipe; it does not invoke VM/device bakers.
The build pins official base hashes/DTBs, the exact v3 module, frozen v2 source and saved evidence, then compares the whole decoded output filesystem with the allowlisted input.
Public source references retain historical source text only for reproduction; unsafe airOS branches are never installed.
HTTPS source hashes were checked in the preceding public builder work; GPG authentication and complete redistribution/license audit are not established.
Retain notices and make complete corresponding sources available where required. The provided modification recipes and source locators are not a blanket licensing review.
Before considering installation, independently verify exact revision, image size/checksum, your backups and a recoverable supported path on a spare unit.
Never bypass signatures/access controls or write calibration, factory/MAC data, bootloader or environment. Public defaults require a clean installation; retained configuration can carry old secrets and addresses.
