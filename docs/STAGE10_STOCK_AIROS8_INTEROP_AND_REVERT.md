# Stage 10 (`FMX-0015`) — Stock `airOS 8` (`5AC`) Interoperability, OpenWrt $\to$ `airOS 8` Rollback Qualification & Cold-Boot Persistence Report

**Date**: 2026-10-18  
**Experiment ID**: `FMX-0015` / `FMX-0002-REVERT`  
**Verdict**: **`KEEP` (CONFIRMED ON PHYSICAL HARDWARE)**

---

## 1. Executive Summary

We have answered all four engineering questions on physical hardware (`OpenWrt LAP-120 AP` $\leftrightarrow$ `NanoStation 5AC Loco` flashed back to stock `airOS 8` `WA.v8.5.12` + `LiteBeam M5` on stock `airOS 6.1.4`):

1. **Proven Fallback to Stock `airOS 8` (`FMX-0002-REVERT` — `CONFIRMED`)**:
   - We flashed the bench `NanoStation 5AC Loco` (`board.sysid=0xe7fa`, MAC `fc:ec:da:c2:54:0a`) directly from OpenWrt 24.10.4 back to official Ubiquiti **`airOS 8` (`WA.v8.5.12.40181.190213.1104.bin`)** via `/dev/mtd3` (`firmware`) without touching `u-boot`, `u-boot-env`, or `ART` (`mtd5`). It booted cleanly into stock `airOS 8.5.12` on the first try.
2. **Why AP-Only Beacon Spoofing Alone Is Not Enough (`CONFIRMED`)**:
   - Even if an OpenWrt AP spoofs Ubiquiti's `airMAX AC` vendor IE in its beacons so an unpatched `airOS 8` CPE associates, the unpatched `airOS 8` CPE enters TDMA polling slave mode (`addradio` mode `1`), holds its TX queues waiting for proprietary TDMA polls, and triggers a hard `80211_Stop` disconnect after **30 seconds** (`.text + 0x00791c` in `ubnt_poll_host.ko`).
3. **Complete 2-Sided Interoperability Solution (`FMX-0015` — `CONFIRMED`)**:
   - **On the Stock `airOS 8` CPE (`ubnt_poll_host.ko`, `MD5: 994e82faac67b6d40632fac960ab1996`)**: A 6-byte (3-instruction) in-RAM patch disables the `ubnt_poll_host_is_ap_valid` vendor-IE check (`.text + 0x009f74` = `24020001`), bypasses the 30-second missing-TDMA-poll reset while keeping the `ubnt_poll_host` state machine running (`.text + 0x007920` = `10000006`), and nops the 2-second TDMA beacon-miss check (`.text + 0x007518` = `00000000`).
   - **On the OpenWrt AP (`mac80211.ko`, `MD5: 6c869e80d4748753727192be08b7bbe6`)**: Because `airOS 8`'s QCA988x target firmware encapsulates TX data frames in RFC 1701 Transparent Ethernet Bridging (`0x6558` `ETH_P_TEB`: `[outer 802.11 + LLC 0x6558][14-byte inner ethhdr][IP/ARP payload]`), we patched 21 instructions in `ieee80211_rx_mesh_data` (`.text + 0x033c18..0x033c68`) in OpenWrt's `mac80211.ko` (persisted in `/overlay/upper/lib/modules/6.6.110/mac80211.ko`). It automatically strips the 14-byte outer `0x6558` header and clears `skb->ip_summed` across `fast_rx`, `rx_h_data`, and `rx_h_amsdu`, while leaving standard `802.11n/ac` stations (`airOS 6 M5`, `MikroTik`, `OpenWrt`) completely untouched.
4. **Hands-Free Cold-Boot Flash Persistence on Stock `airOS 8.5.12` Without Downgrading or Custom Firmware (`CONFIRMED`)**:
   - We discovered that `airOS 8.5.12`'s `/init` runs `/sbin/uav` before `/sbin/ubntconf`, deleting custom scripts in `/etc/persistent/` that contain keywords like `mount` (`uav: Removing ... as potentially malicious`), and standard (non-`CS`) firmware builds ignore `/etc/persistent/rc.poststart`.
   - However, `/sbin/ubntconf` natively parses `cron.status=enabled` and `cron.1.job.1.cmd=...` from `/tmp/system.cfg` **after** `/sbin/uav` has already exited! Embedding our backslash-free `dd` + `awk` module patcher directly in `cron.1.job.1.cmd` and saving with `cfgmtd -w -p /etc/ -f /tmp/system.cfg` survived a full cold reboot and automatically associated the stock `airOS 8.5.12` `Loco 5AC` at **`650.0 MBit/s` (`VHT80`, `VHT-MCS 7`, `NSS 2`)**.

---

## 2. Physical Benchmark Results (`Stock airOS 8.5.12 Loco 5AC` + `Stock airOS 6.1.4 LiteBeam M5` $\leftrightarrow$ `OpenWrt LAP-120 AP`)

| Test / Metric | Channel Width | Measured Result | Notes / Status |
| :--- | :---: | :---: | :--- |
| **Cold-Boot Auto-Association** | `80 MHz` (`VHT80`) | **`650.0 MBit/s` TX / `526.6–650.0 MBit/s` RX** (`VHT-MCS 7`, `NSS 2`) | Hands-free after `reboot`, SNR `51–54 dB`, zero disconnects past 30s+ |
| **Idle Ping RTT (`LAP-120 <-> Loco 5AC`)** | `80 MHz` (`VHT80`) | **`1.115 / 1.231 / 1.343 ms`** (`min/avg/max`, `0%` loss) | `1.184 / 1.411 / 1.679 ms` on `20 MHz` (`0%` loss) |
| **Standalone `Loco 5AC` TCP Uplink (`4 streams`)** | `80 MHz` (`VHT80`) | **`147.0 Mbps` mean (`152.0 Mbps` peak interval)** | Only `4` TCP retransmits across `140 MBytes` transferred |
| **Standalone `Loco 5AC` TCP Uplink (`1 stream`)** | `80 MHz` / `20 MHz` | **`63.9 Mbps` (`80 MHz`) / `58.1 Mbps` (`20 MHz`)** | **`0` TCP retransmissions** in both widths |
| **Standalone `Loco 5AC` UDP Downlink** | `80 MHz` (`VHT80`) | **`85.0 Mbps`** (`1.036 ms` jitter) | Terminated directly on `Loco 5AC` (`AR9342` 535 MHz CPU) |
| **Standalone `Loco 5AC` TCP Downlink (`4S / 1S`)** | `80 MHz` (`VHT80`) | **`62.0 Mbps` (`4S`) / `32.2 Mbps` (`1S`, `0` retrans)** | Local `iperf3 -s` on `Loco 5AC` |
| **Simultaneous Mixed-Gen PtMP Uplink (`5AC + M5 -> AP`)** | `80 MHz` AP (`5AC VHT80 + M5 HT40`) | **`99.5 Mbps` total** (`Loco 5AC = 87.7 Mbps`, `LiteBeam M5 = 11.8 Mbps`) | **`0%` packet loss**, `Loco 5AC` loaded RTT **`8.21 ms` avg (`5.17 ms` min)** |
| **Simultaneous Mixed-Gen PtMP Downlink (`AP -> 5AC + M5`)** | `80 MHz` AP (`5AC VHT80 + M5 HT40`) | **`56.1 Mbps` total** (`Loco 5AC = 42.2 Mbps`, `LiteBeam M5 = 13.9 Mbps`) | **`0%` packet loss** on both `airOS 8` (`5AC`) and `airOS 6` (`M5`) |

---

## 3. Exact Reproduction Recipe

### A. OpenWrt AP Side (`/lib/modules/6.6.110/mac80211.ko`)
- Patched `ieee80211_rx_mesh_data` at `.text + 0x033c18..0x033c68` (`MD5: 6c869e80d4748753727192be08b7bbe6`) persisted directly in `/overlay/upper/lib/modules/6.6.110/mac80211.ko` on `LAP-120`.
- If `skb->len >= 28` and `*(u16 *)(skb->data + 12) == 0x6558` (`ETH_P_TEB`), pulls 14 bytes (`skb->data += 14`, `skb->len -= 14`) and clears `skb->ip_summed` (`ins $t2, $zero, 1, 2` at `0x64($a2)`), revealing the inner Ethernet header to `mac80211`'s `ether_In` / `eth_type_trans`.

### B. Universal Stock `airOS 8` (`WA` / `XC` `v8.5.12` through `v8.7.25`) CPE Side (`/tmp/system.cfg` + `cfgmtd -w -p /etc/`)
Add/replace the following lines in `/tmp/system.cfg`, run `/sbin/ubntconf -c /tmp/system.cfg`, and persist to flash with `/sbin/cfgmtd -w -p /etc/ -f /tmp/system.cfg`:

```ini
radio.1.ptpmode=0
radio.1.wds.status=disabled
cron.status=enabled
cron.1.status=enabled
cron.1.user=ubnt
cron.1.job.1.status=enabled
cron.1.job.1.schedule=* * * * *
cron.1.job.1.cmd=if [ ! -f /tmp/uph.ko ]; then O=/lib/modules/2.6.32.68/ubnt_poll_host.ko; SZ=$(wc -c < $O); if [ $SZ -eq 186528 ]; then S1=30040; S2=30044; S3=31076; C3=9808; S4=40888; elif [ $SZ -eq 186560 ]; then S1=30072; S2=30076; S3=31108; C3=9808; S4=40920; else S1=30784; S2=30788; S3=31820; C3=10156; S4=41980; fi; (dd if=$O bs=1 count=$S1; dd if=/dev/zero bs=1 count=4; dd if=$O bs=1 skip=$S2 count=1028; awk 'BEGIN{printf "%c",16}'; dd if=/dev/zero bs=1 count=2; awk 'BEGIN{printf "%c",6}'; dd if=$O bs=1 skip=$S3 count=$C3; awk 'BEGIN{printf "%c%c",36,2}'; dd if=/dev/zero bs=1 count=1; awk 'BEGIN{printf "%c",1}'; dd if=$O bs=1 skip=$S4) > /tmp/uph.ko 2>/dev/null; mount --bind /tmp/uph.ko $O; sed -i 's|echo 1 > /sys/module/umac/parameters/is_ubnt_ptp|echo 0 > /sys/module/umac/parameters/is_ubnt_ptp|;s|echo wifi0 1 0 0 > /proc/sys/dev/uph/addradio|echo wifi0 0 0 0 > /proc/sys/dev/uph/addradio|' /etc/sysinit/radio.conf; sed -i 's|iwpriv "ath0" wds 1|iwpriv "ath0" wds 0|' /etc/sysinit/wireless.conf; /usr/etc/init.d/plugin stop wireless; /usr/etc/init.d/plugin stop radio; /usr/etc/init.d/plugin start radio; /usr/etc/init.d/plugin start wireless; /usr/etc/init.d/plugin start bridge; /usr/etc/init.d/plugin start net; /usr/etc/init.d/plugin start route; sleep 2; fi; if iwconfig ath0 2>/dev/null | grep -q Not-Associated; then athchans -i ath0 5180 2>/dev/null; iwconfig ath0 essid FuturaMAX-LAB 2>/dev/null; fi
```

---

## 4. Official `WA.v8.7.25` Physical Bench Upgrade & Universal `WA`/`XC` Offset Table (`CONFIRMED`)

1. **UISP 5-Panel Firmware Audit**:
   - Audited the 5 candidate low-client sectors in UISP (`Edificio-Panel-Belgrano`, `FT-UOM-1`, `Panel3-Guarida`, `Panel2-ACVNEW`, `Panel1-Guarida`): all 5 APs and the majority of CPEs run **`WA.v8.7.25`** (with remaining CPEs on `8.7.22`, `8.7.19`, `8.7.17`, `8.7.13`, `8.7.11`).
2. **Universal `ubnt_poll_host.ko` Offset Table (`WA` & `XC`)**:
   - Extracted `lib/modules/2.6.32.68/ubnt_poll_host.ko` across `WA` and `XC` builds hosted on the local UISP server (`https://192.168.2.197/nms/firmwares/ubnt/...`):

| Firmware Build(s) | `.ko` Size (Bytes) | Stock `.ko` MD5 | Patched `.ko` MD5 | `S1` (`bmiss_2s`) | `S2` | `C2` (`timer_30s` gap) | `S3` | `C3` (`is_ap_valid` gap) | `S4` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`WA.v8.5.12`** | `186,528` | `6f4b39bd2284ca599ca4d5d4425c6277` | `994e82faac67b6d40632fac960ab1996` | `30040` | `30044` | `1028` | `31076` | `9808` | `40888` |
| **`WA.v8.7.1` / `WA.v8.7.4`** | `186,560` | `caab5177b3953e1bc51d43b46ca6ff8e` | *(+32B shift)* | `30072` | `30076` | `1028` | `31108` | `9808` | `40920` |
| **`XC.v8.7.1` / `XC.v8.7.4`** | `186,560` | `4103f9d0a2fdbf312d93a68b10647bca` | *(+32B shift)* | `30072` | `30076` | `1028` | `31108` | `9808` | `40920` |
| **`WA.v8.7.22` / `WA.v8.7.25`** | `189,880` | `7c76c8ced16cab0ce9ca680ce9c94e51` | `3f2e756225bf67947abcc5dd46bccd9d` | `30784` | `30788` | `1028` | `31820` | `10156` | `41980` |
| **`XC.v8.7.22` / `XC.v8.7.25`** | `189,880` | `5b26b076967befe129f669096539ae21` | *(same offsets)* | `30784` | `30788` | `1028` | `31820` | `10156` | `41980` |

3. **Physical Bench Verification on Official `WA.v8.7.25` (`192.168.1.20` `NanoStation 5AC Loco`)**:
   - Flashed the bench `Loco 5AC` to official **`WA.v8.7.25`** (`WA-8.7.25.260730.bin`, `SHA256: e87ffba1f0ed9e245b42541a86044f7688f3a7ba1ca783a30263ad7d9ad3dbc3`) via `/sbin/fwupdate.real -m`.
   - Installed the universal `system.cfg` `cron` unlock, saved via `cfgmtd -w -p /etc/ -f /tmp/system.cfg` (`rc=0`), and executed a full cold `reboot`.
   - The `WA.v8.7.25` `Loco 5AC` automatically built `/tmp/uph.ko` (`MD5: 3f2e756225bf67947abcc5dd46bccd9d`), bind-mounted it, and associated hands-free to the OpenWrt `LAP-120` AP at **`526.5 MBit/s` (`VHT80`)**:
     - **Idle Ping RTT over RF**: **`1.085 / 1.359 / 1.802 ms`** (`0%` loss, `10/10` packets).
     - **4-Stream TCP Uplink (`WA.v8.7.25 Loco 5AC -> OpenWrt LAP-120`)**: **`134.0 Mbps` mean (`137.0 Mbps` peak, `1` retransmit)**.
     - **4-Stream TCP Downlink (`OpenWrt LAP-120 -> WA.v8.7.25 Loco 5AC`)**: **`78.8 Mbps` receiver / `79.4 Mbps` sender (`82.1 Mbps` peak)**.
     - **UDP Downlink (`OpenWrt LAP-120 -> WA.v8.7.25 Loco 5AC`)**: **`83.6 Mbps` (`0.393 ms` jitter, `2.4%` loss)**.


---

## 5. `WPA2-PSK (CCMP)` (`allow_80211=1`) Cold-Boot Verification & Canary Panel Hardware Audit (`CONFIRMED`)

1. **`WPA2-PSK (CCMP)` Discovery — Ubiquiti `/bin/wpa_supplicant` `allow_80211=1` Gate**:
   - All production sectors in UISP use `WPA2-PSK (CCMP)` (`wpasupplicant.status=enabled`, `wpasupplicant.profile.1.network.1.key_mgmt.1.name=WPA-PSK`, `pairwise=CCMP`, `proto=RSN`).
   - Static inspection of `/bin/wpa_supplicant` (`709,880` bytes on `WA.v8.7.25`) revealed that Ubiquiti patched `wpa_supplicant v2.1` (`-D wext`) to drop non-airMAX beacons from `SIOCGIWSCAN` results unless the global configuration directive **`allow_80211=1`** is present in `/etc/wpasupplicant_*.conf` (alongside `/var/run/fscan_status` = `1`).
   - Furthermore, on `WA.v8.7.25`, `/etc/sysinit/radio.conf` writes `echo wifi0 1 0 0 0 > /proc/sys/dev/uph/addradio` (4 numeric flags instead of 3 on `v8.5.12`) and `echo 1 > /proc/sys/dev/uph_wifi0/enable`.
   - Adding `sed -i '/allow_80211/d;s/ap_scan=1/ap_scan=1\nallow_80211=1/' /etc/wpasupplicant_*.conf` and `s|echo 1 > /proc/sys/dev/uph_wifi0/enable|echo 0 > /proc/sys/dev/uph_wifi0/enable|` into the bi-directional `cron.1.job.1.cmd` unlocked immediate `WPA2-PSK (CCMP)` 4-way handshake and hands-free cold-boot association on **`WA.v8.7.25`**:
     - **Cold-Boot Association & 4-Way Handshake (`WPA2-PSK CCMP`)**: Associated automatically on the first cron tick after cold reboot (`wpa_state=COMPLETED`, `pairwise_cipher=CCMP`, `group_cipher=CCMP`, `key_mgmt=WPA2-PSK`, `authorized: yes`, `authenticated: yes`).
     - **Idle Ping RTT over `WPA2-PSK (CCMP)`**: **`1.114 / 1.296 / 1.956 ms`** (`min/avg/max`, `0%` packet loss).
     - **4-Stream TCP Uplink over `WPA2-PSK (CCMP)`**: **`120.0 Mbps` mean (`132.0 Mbps` peak interval, `1` retransmit)**.
     - **4-Stream TCP Downlink over `WPA2-PSK (CCMP)`**: **`79.5 Mbps` receiver / `80.3 Mbps` sender (`80.6 Mbps` peak interval)**.
   - **Production Bi-Directional Auto-Sensing `cron.1.job.1.cmd` (Preserves Stock `airMAX` TDMA + `WPA2-PSK` & Auto-Switches to FuturaMAX OpenWrt)**:
```ini
cron.status=enabled
cron.1.status=enabled
cron.1.user=ubnt
cron.1.job.1.status=enabled
cron.1.job.1.schedule=* * * * *
cron.1.job.1.cmd=if iwconfig ath0 2>/dev/null | grep -q Not-Associated; then O=/lib/modules/2.6.32.68/ubnt_poll_host.ko; if [ ! -f /tmp/uph.ko ]; then SZ=$(wc -c < $O); if [ $SZ -eq 186528 ]; then S1=30040; S2=30044; S3=31076; C3=9808; S4=40888; elif [ $SZ -eq 186560 ]; then S1=30072; S2=30076; S3=31108; C3=9808; S4=40920; else S1=30784; S2=30788; S3=31820; C3=10156; S4=41980; fi; (dd if=$O bs=1 count=$S1; dd if=/dev/zero bs=1 count=4; dd if=$O bs=1 skip=$S2 count=1028; awk 'BEGIN{printf "%c",16}'; dd if=/dev/zero bs=1 count=2; awk 'BEGIN{printf "%c",6}'; dd if=$O bs=1 skip=$S3 count=$C3; awk 'BEGIN{printf "%c%c",36,2}'; dd if=/dev/zero bs=1 count=1; awk 'BEGIN{printf "%c",1}'; dd if=$O bs=1 skip=$S4) > /tmp/uph.ko 2>/dev/null; mount --bind /tmp/uph.ko $O; sed -i 's|echo 1 > /sys/module/umac/parameters/is_ubnt_ptp|echo 0 > /sys/module/umac/parameters/is_ubnt_ptp|;s|echo wifi0 1 0 0|echo wifi0 0 0 0|;s|echo 1 > /proc/sys/dev/uph_wifi0/enable|echo 0 > /proc/sys/dev/uph_wifi0/enable|' /etc/sysinit/radio.conf; sed -i 's|iwpriv "ath0" wds 1|iwpriv "ath0" wds 0|' /etc/sysinit/wireless.conf; sed -i '/allow_80211/d;s/ap_scan=1/ap_scan=1\nallow_80211=1/' /etc/wpasupplicant_*.conf 2>/dev/null; /usr/etc/init.d/plugin stop wpasupplicant; /usr/etc/init.d/plugin stop wireless; /usr/etc/init.d/plugin stop radio; /usr/etc/init.d/plugin start radio; /usr/etc/init.d/plugin start wireless; /usr/etc/init.d/plugin start wpasupplicant; /usr/etc/init.d/plugin start bridge; /usr/etc/init.d/plugin start net; /usr/etc/init.d/plugin start route; else umount $O 2>/dev/null; rm -f /tmp/uph.ko; /sbin/ubntconf -c /tmp/system.cfg; /usr/etc/init.d/plugin stop wpasupplicant; /usr/etc/init.d/plugin stop wireless; /usr/etc/init.d/plugin stop radio; /usr/etc/init.d/plugin start radio; /usr/etc/init.d/plugin start wireless; /usr/etc/init.d/plugin start wpasupplicant; /usr/etc/init.d/plugin start bridge; /usr/etc/init.d/plugin start net; /usr/etc/init.d/plugin start route; fi; fi
```

2. **Canary Sector `/etc/board.info` Hardware Audit (`CONFIRMED`)**:
   - Read-only SSH inspection of `/etc/board.info` and `/proc/mtd` across the candidate low-client sectors revealed a critical hardware distinction:
     - **`Edificio-Panel-Belgrano` (`10.10.100.5`, 2 CPEs)**: `board.sysid=0xe7e9`, `board.name=Rocket Prism 5AC` (`XC.v8.7.25`, `RP-5AC-Gen2`). Uses Ubiquiti's proprietary AirPrism active RF filter ASIC and is **not supported by OpenWrt 24.10.4**. Must NOT be flashed with `ubnt_lap-120`.
     - **`Panel3-Guarida` (`10.10.100.83`, 3 CPEs)**: `board.sysid=0xe8e5`, `board.name=LiteAP AC` (`WA.v8.7.25`, `LAP-120`) — **exact `0xe8e5` hardware match to the physical bench AP (`192.168.1.2`)**.
     - **`Panel1-Guarida` (`10.10.100.84`, 4 CPEs)**: `board.sysid=0xe8e5`, `board.name=LiteAP AC` (`WA.v8.7.25`, `LAP-120`) — **exact `0xe8e5` hardware match to the physical bench AP (`192.168.1.2`)**, and all 4 of its CPEs are already on `WA.v8.7.25` (3) or `WA.v8.7.22` (1) (`189,880`-byte `ubnt_poll_host.ko`).
     - **`FT-UOM-1` (`10.10.100.172`, 2 CPEs)**: `board.sysid=0xe7fd`, `board.name=LiteAP GPS` (`WA.v8.7.25`, `LAP-GPS`), with both CPEs already on `WA.v8.7.25`.

---

## 6. Phase 1 & Phase 2 Completed on Canary Sector `Panel1-Guarida` (`10.10.100.84` `LAP-120` + 4 Live CPEs) (`CONFIRMED`)

1. **Phase 1 — Full Partition Backups & Baseline Telemetry (`artifacts/canary_panel1_guarida/phase1_inventory_and_backups.json`, `phase1_baseline_snapshot_initial.json`)**:
   - Verified `mtd0` (`u-boot`, `262,144 B`), `mtd1` (`u-boot-env`, `65,536 B`), `mtd4` (`cfg`, `262,144 B`), `mtd5` (`EEPROM/ART`, `65,536 B`), `system.cfg.orig`, `board.info`, `proc_mtd.txt`, `wstalist.json`, and `status.json` across `Panel1-Guarida` (`10.10.100.84`, `LAP-120` `sysid=0xe8e5`, `WA.v8.7.25`) and all 4 of its associated CPEs (`100%` local/remote MD5 match across all 20 binary partition dumps):
     - **`AP_Panel1-Guarida` (`10.10.100.84`)**: `LiteAP AC` (`sysid=0xe8e5`), `WA.v8.7.25`, `SSID=FT-Guarida1`, `Freq=5240 MHz` (`Channel 48`, `VHT20`), `netmode=bridge` (`br0 = eth0 + ath0`, `IP=10.10.100.84/24`, `GW=10.10.100.1`), `mtd5 ART MD5: a21894fcf4c129ed94432dcdfd473f5d`.
     - **`CPE1` (`FARELA Juan Jose`, `10.10.200.91`, `24:5A:4C:C0:4C:F8`)**: `LiteBeam 5AC` (`sysid=0xe7f9`), `WA.v8.7.22` (`ubnt_poll_host.ko = 189,880 B`), `netmode=router` (`br0` WAN `10.10.200.91/24`, `eth0` LAN `192.168.1.20/24`), `sig=-54 dBm`, `TX/RX=156.0/117.0 Mbps`, `mtd5 ART MD5: bfe5710ada9e38a820af2aec49487fb9`.
     - **`CPE2` (`SCHECHTEL_Camila`, `10.10.210.188`, `0C:EA:14:94:A5:F0`)**: `NanoStation 5AC loco` (`sysid=0xe7fa`), `WA.v8.7.25` (`ubnt_poll_host.ko = 189,880 B`), `netmode=router`, `sig=-60 dBm`, `TX/RX=173.3/144.4 Mbps`, `mtd5 ART MD5: b18089280f44983459e4ed16467b29cd`.
     - **`CPE3` (`GAMBOA_Gabriela`, `10.10.200.223`, `24:5A:4C:44:77:7A`)**: `LiteBeam 5AC` (`sysid=0xe7f9`), `WA.v8.7.25` (`ubnt_poll_host.ko = 189,880 B`), `netmode=router`, `sig=-49 dBm`, `TX/RX=144.4/117.0 Mbps`, `mtd5 ART MD5: cc0986dc0907dcf2583a5c27448145ad`.
     - **`CPE4` (`MONZON Stella Maris`, `10.10.200.41`, `24:5A:4C:E0:05:40`)**: `NanoStation 5AC loco` (`sysid=0xe7fa`), `WA.v8.7.25` (`ubnt_poll_host.ko = 189,880 B`), `netmode=router`, `sig=-60 dBm`, `TX/RX=144.4/117.0 Mbps`, `mtd5 ART MD5: a190100440de894e640e60adc43155b9`.
2. **Phase 2 — Live Pre-Staging of Bi-Directional Auto-Sensing `cron` on All 4 CPEs (`artifacts/canary_panel1_guarida/phase2_cpe_prestage_receipt.json`)**:
   - Pre-staged the bi-directional `cron.1.job.1.cmd` into `/tmp/system.cfg`, regenerated `/etc/crontabs/ubnt` via `/sbin/ubntconf -c /tmp/system.cfg`, started `crond` (`/usr/etc/init.d/plugin start cron`), and flashed to `mtd4` (`CFGMTD_RC=0`) on all 4 CPEs (`10.10.200.91`, `10.10.210.188`, `10.10.200.223`, `10.10.200.41`).
   - Verified after `65` seconds (at least one full `crond` tick on every CPE) that all 4 CPEs remained in `UPH_DORMANT_STOCK_TDMA` state (`iwconfig ath0` = `Access Point: 78:45:58:A0:34:A2`) with **zero link drops** (`link_uptime` increased continuously from `1,217,574s -> 1,218,044s`, `669,647s`, `590,965s`, `60,551s`).
