# OpenMAX public-r1 sources and notices
Base: OpenWrt 24.10.4 r28959-29397011cc, ath79/generic.
Separate official ubnt,powerbeam-5ac-gen2 and ubnt,litebeam-ac-gen2 base images.
Modified OpenWrt image, not Ubiquiti-signed firmware or an official OpenWrt build.
Original package notices remain in the unchanged stock filesystem.

- Base images/checksums/buildinfo: https://downloads.openwrt.org/releases/24.10.4/targets/ath79/generic/
- Base source/build recipes: https://github.com/openwrt/openwrt/tree/v24.10.4
- Package sources: https://sources.openwrt.org/ (exact versions/hashes are in those build recipes).
- Modified mac80211 is GPL: the included builder contains the complete deterministic 21-instruction patch and pins.
- New bootstrap, service and admitter sources are in sources/public_payloads/, GPL-2.0-or-later.
- GPLv2 text: sources/public_assets/COPYING.GPL-2.0.

Rebuild in the source repository using the pinned official base images; no device dump or private config is needed.
Retain notices and provide complete corresponding sources for covered components when redistributing.
These source locators and the modification recipe do not assert a blanket licensing review of upstream packages.
