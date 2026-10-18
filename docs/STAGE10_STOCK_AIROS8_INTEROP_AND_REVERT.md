# Stage 10 (`FMX-0015`) — Stock `airOS 8` (`5AC`) Interoperability, OpenWrt $\to$ `airOS 8` Rollback Qualification & Software-Reboot Persistence Report

**Date**: 2026-10-18 (Updated with `gpt-6-astra` `xhigh` Adversarial Audit Remediations `F01–F03`, `F12`)  
**Experiment ID**: `FMX-0015` / `FMX-0002-REVERT`  
**Verdict**: **`KEEP` on Isolated Bench (`CONFIRMED` Bench Throughput & Association; Production Migration Gated on `F01–F03` Soak & L2 Matrix)**

---

## 1. Executive Summary

We have answered four core engineering questions on isolated bench hardware (`OpenWrt LAP-120 AP 192.168.1.2` $\leftrightarrow$ `NanoStation 5AC Loco 192.168.1.20` flashed back to stock `airOS 8` `WA.v8.5.12` and `WA.v8.7.25` + `LiteBeam M5` on stock `airOS 6.1.4`), and subsequently audited all recipes offline via an independent `gpt-6-astra` (`xhigh`) adversarial review ([`docs/ADVERSARIAL_REVIEW_STAGE10_11.md`](ADVERSARIAL_REVIEW_STAGE10_11.md)):

1. **Proven Fallback from OpenWrt to Stock `airOS 8` (`FMX-0002-REVERT` — `CONFIRMED`)**:
   - We flashed the bench `NanoStation 5AC Loco` (`board.sysid=0xe7fa`) directly from OpenWrt 24.10.4 back to official Ubiquiti **`airOS 8` (`WA.v8.5.12.40181.190213.1104.bin`)** via `/dev/mtd3` (`firmware`) without touching `u-boot`, `u-boot-env`, or `ART` (`mtd5`), and later upgraded it to official **`WA.v8.7.25`** (`WA-8.7.25.260730.bin`) via `/sbin/fwupdate.real -m`. Both booted cleanly on the first try.
2. **Why AP-Only Beacon Spoofing Alone Is Not Enough (`CONFIRMED`)**:
   - Even if an OpenWrt AP spoofs Ubiquiti's `airMAX AC` vendor IE in its beacons so an unpatched `airOS 8` CPE associates, the unpatched `airOS 8` CPE enters TDMA polling slave mode (`addradio` mode `1`), holds its TX queues waiting for proprietary TDMA polls, and triggers a kernel panic/disconnect path after **~30 seconds** (`sltu` + `bnez` before `panic` at `.text+0x7c08` on `8.7.25` / `.text+0x7920` on `8.5.12` in `ubnt_poll_host.ko`).
3. **2-Sided Hybrid Interoperability Solution & Adversarial Audit Remediation (`FMX-0015`)**:
   - **On the Stock `airOS 8` CPE (`ubnt_poll_host.ko`)**:
     - Our initial bench test applied a 3-instruction (6 changed bytes) splice in `/tmp/uph.ko` (`legacy_md5`: `994e82faac67b6d40632fac960ab1996` on `WA.v8.5.12`; `3f2e756225bf67947abcc5dd46bccd9d` on `WA.v8.7.25`):
       1. `.text+0xa3b8` (`file offset 41976` on `8.7.25`): `0002102b` (`sltu $v0, $zero, $v0`) $\to$ `24020001` (`addiu $v0, $zero, 1`) so `ubnt_poll_host_is_ap_valid` returns `1`.
       2. `.text+0x7c08` (`file offset 31816` on `8.7.25`): `14400006` (`bnez $v0, +6`) $\to$ `10000006` (`b +6`) to bypass the missing-poll `panic` branch.
       3. `.text+0x7800` (`file offset 30784` on `8.7.25`): `0c000000` (`jal ubnt_poll_host_sta_bmiss_ind`) $\to$ `00000000` (`nop`).
     - **Adversarial Audit Remediation (`F01` — `CRITICAL` Catch)**: Because `ubnt_poll_host.ko` is a relocatable MIPS ELF (`ET_REL`), zeroing the `jal` instruction word at `file offset 30784` (`0x00000000`) without clearing its 8-byte `.rel.text` entry (`R_MIPS_26` at `file offset 168536` on `8.7.22/8.7.25`, `165656` on `8.7.1/8.7.4`, `165624` on `8.5.12`) leaves the `R_MIPS_26` relocation active. During `insmod`, the MIPS kernel loader (`vmlinux` `0x8000c99c`) writes `(((symbol_addr >> 2) + addend) & 0x03ffffff)` into the low 26 bits of the zeroed word, turning it into a non-NOP instruction if the 2-second beacon-miss path is ever reached!
      - **Relocation-Safe 4-Site Fix (`CONFIRMED` in Kernel RAM via `/dev/mem`)**: Zeroing **both** the 4-byte instruction word at `S1` (`30784`) **and** the 8-byte `.rel.text` entry at `R1` (`168536`, turning `R_MIPS_26 = 0x04` into `R_MIPS_NONE = 0x00`) guarantees that the kernel loader skips `0x7800` (`apply_r_mips_none` returns `0`). On the bench `WA.v8.7.25` `Loco 5AC` (`192.168.1.20`), we also discovered why `rmmod ubnt_poll_host` previously failed during `plugin stop radio`: `/bin/ubntspecd` holds `/dev/uph_wifi0` (`fd 6`, major `190`) open (`refcnt = 2`). Adding `killall ubntspecd 2>/dev/null; rmmod ubnt_poll_host 2>/dev/null; insmod ubnt_poll_host` cleanly reloads `/tmp/uph.ko` (`MD5: 077d151e0055f198609dc761a39207b3`) at `0x81400000`, and `/dev/mem` readback at physical `0x01407800` confirmed **`0x00000000` (`nop`, `top6=0, low26=0`)** in live kernel RAM ([`f01_bench_verification.json`](../artifacts/adversarial_review_stage10_11/f01_bench_verification.json)).
   - **On the OpenWrt AP (`mac80211.ko`, `/rom` MD5 `334afdc47772220e5550db392f0e0beb` $\to$ `/overlay` MD5 `6c869e80d4748753727192be08b7bbe6`)**:
     - When a stock `airOS 8` CPE transmits with `radio.1.ptpmode=0` and `radio.1.wds.status=disabled` (`iwpriv ath0 wds 0`), its data frames carry a **14-byte outer header** with EtherType `0x6558` (`ETH_P_TEB`) ahead of the inner Ethernet frame.
     - On our bench OpenWrt `LAP-120` AP, we patched 21 instructions (71 changed bytes at ELF file offsets `0x33c88..0x33cdb`, corresponding to `.text + 0x120e4..0x12137` since `.text` starts at file offset `0x21ba4`; full byte diff archived in [`ap_mac80211_eth_p_teb_diff.json`](../artifacts/adversarial_review_stage10_11/ap_mac80211_eth_p_teb_diff.json)) to check `skb->len >= 28` and `*(u16 *)(skb->data + 12) == 0x6558`, strip those **14 bytes** (`skb->data += 14`, `skb->len -= 14`), and clear `skb->ip_summed`.
     - **Scope Boundary (`F03`)**: Because this decapsulation hook runs on the OpenWrt AP's `mac80211.ko`, compatibility with unpatched third-party APs (MikroTik/Cambium/Mimosa) is **not automatic** unless either (a) the AP strips the 14-byte `0x6558` header at the bridge/driver layer, or (b) standard 4-address WDS (`wds=1`) is used without `0x6558` encapsulation.
4. **Software-Reboot Persistence via `/sbin/ubntconf` `cron.1.job.1.cmd` (`CONFIRMED` Mechanism; Hardened per `F02`)**:
   - Standard (non-`-cs`) `airOS 8` builds ignore `/etc/persistent/rc.poststart` and run `/sbin/uav` before `/sbin/ubntconf`. However, `/sbin/ubntconf` natively generates `/etc/crontabs/ubnt` from `cron.1.job.1.cmd` in `/tmp/system.cfg` after `/sbin/uav` exits.
   - Note: writing `cron.1.job.1.cmd` to `/tmp/system.cfg` and persisting it with `cfgmtd -w -p /etc/` modifies the `mtd4` (`cfg`) configuration partition once during installation; the runtime `/tmp/uph.ko` module patch itself runs in `/tmp` RAM on each boot without touching `mtd2`/`mtd3` (`kernel`/`rootfs`) or `mtd5` (`ART`).

---

## 2. Physical Benchmark Results on Isolated Lab Bench (`OpenWrt LAP-120 AP 192.168.1.2` $\leftrightarrow$ `Stock airOS 8 Loco 5AC 192.168.1.20`)

| Firmware & Security Mode | Channel / Width | Test / Metric | Measured Result | Notes / Status |
| :--- | :---: | :--- | :--- | :--- |
| **`WA.v8.5.12` (Open)** | `5180 MHz` / `80 MHz` (`VHT80`) | **Software-Reboot Auto-Association** | **`650.0 MBit/s` TX / `526.6–650.0 MBit/s` RX** (`VHT-MCS 7`, `NSS 2`) | SNR `51–54 dB`, zero disconnects past 30s+ |
| **`WA.v8.5.12` (Open)** | `5180 MHz` / `80 MHz` (`VHT80`) | **Idle Ping RTT (`LAP-120 <-> Loco 5AC`)** | **`1.115 / 1.231 / 1.343 ms`** (`min/avg/max`, `0%` loss) | `1.184 / 1.411 / 1.679 ms` on `20 MHz` (`0%` loss) |
| **`WA.v8.5.12` (Open)** | `5180 MHz` / `80 MHz` (`VHT80`) | **4-Stream TCP Uplink (`CPE -> AP`)** | **`147.0 Mbps` mean (`152.0 Mbps` peak)** | `4` TCP retransmits across `140 MBytes` |
| **`WA.v8.5.12` (Open)** | `80 MHz` / `20 MHz` | **1-Stream TCP Uplink (`CPE -> AP`)** | **`63.9 Mbps` (`80 MHz`) / `58.1 Mbps` (`20 MHz`)** | **`0` TCP retransmissions** in both widths |
| **`WA.v8.5.12` (Open)** | `5180 MHz` / `80 MHz` (`VHT80`) | **UDP / TCP Downlink (`AP -> CPE`)** | **`85.0 Mbps` UDP / `62.0 Mbps` TCP (`4S`)** | Terminated on `Loco 5AC` (`AR9342` 535 MHz CPU) |
| **`WA.v8.5.12` + `airOS 6.1.4 M5`** | `80 MHz` AP (`5AC VHT80 + M5 HT40`) | **Simultaneous Mixed-Gen PtMP UL / DL** | **`99.5 Mbps` UL (`87.7 + 11.8`) / `56.1 Mbps` DL (`42.2 + 13.9`)** | **`0%` packet loss**, `Loco 5AC` loaded RTT **`8.21 ms` avg** |
| **`WA.v8.7.25` (Open)** | `5180 MHz` / `80 MHz` (`VHT80`) | **4-Stream TCP Uplink / Downlink** | **`134.0 Mbps` UL (`137.0` peak) / `78.8 Mbps` DL (`82.1` peak)** | Idle RTT **`1.085 / 1.359 / 1.802 ms`** (`0%` loss) |
| **`WA.v8.7.25` (`WPA2-PSK CCMP`)** | `5180 MHz` / `80 MHz` (`VHT80`) | **4-Stream TCP Uplink / Downlink (`CCMP`)** | **`120.0 Mbps` UL (`132.0` peak) / `79.5 Mbps` DL (`80.6` peak)** | Idle RTT **`1.114 / 1.296 / 1.956 ms`** (`0%` loss) |
| **`WA.v8.7.25` (`WPA2-PSK CCMP`)** | `5240 MHz` / `20 MHz` (`VHT20`) | **4-Stream TCP Uplink / Downlink (`CCMP`)** | **`78.7 Mbps` UL (`93.2` peak, `0` retrans, `3.94 bit/s/Hz`) / `63.6 Mbps` DL (`74.2` peak, `3.18 bit/s/Hz`)** | `173.3 MBit/s` (`VHT-MCS 8 SGI NSS 2`), Idle RTT **`1.483 ms` avg** (`0%` loss) |

*(Note: In the bench trials above, `iperf3` was terminated directly on the CPE/AP CPUs and reboot persistence was verified across software `reboot` commands. Physical power-cut cold boot and multi-MAC Ethernet bridge testing Behind-the-CPE are tracked in the Stage 10B Acceptance Checklist below.)*

---

## 3. Exact `ubnt_poll_host.ko` Offset & MD5 Table (`WA` & `XC`, Including `F01` Relocation-Safe Fix)

Across all 9 extracted `WA` and `XC` firmware images (`lib/modules/2.6.32.68/ubnt_poll_host.ko`, `.text` at file offset `64`), the exact file offsets and MD5 hashes are:

| Firmware Build(s) | `.ko` Size (Bytes) | Stock `.ko` MD5 (Preimage Allowlist) | `S1` (`bmiss` `.text` file offset) | `S_panic` (`timer` `.text` file offset) | `S_ret` (`is_ap_valid` `.text` file offset) | `R1` (`R_MIPS_26` `.rel.text` file offset, 8 bytes) | Legacy 3-Site MD5 (Retains `R_MIPS_26`) | **Relocation-Safe 4-Site MD5 (`F01` Fixed)** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`WA.v8.5.12`** | `186,528` | `5bb5c6687c916822190ea5d687388e4f` | `30040` (`.text+0x7518`) | `31072` (`.text+0x7920`) | `40884` (`.text+0x9f74`) | `165624` (`idx 1170`) | `994e82faac67b6d40632fac960ab1996` | **`9b516361d0e36ea1c2c5177cb87b6075`** |
| **`WA.v8.7.1-cs` / `WA.v8.7.4-cs`** | `186,560` | `caab5177b3953e1bc51d43b46ca6ff8e` | `30072` (`.text+0x7538`) | `31104` (`.text+0x7940`) | `40916` (`.text+0x9f94`) | `165656` (`idx 1170`) | `ee022e8a86e46c67ac5516a8a4793b0d` | **`3a76741ab2c3105c91abaa89ea8420c2`** |
| **`XC.v8.7.1-cs` / `XC.v8.7.4-cs`** | `186,560` | `4103f9d0a2fdbf312d93a68b10647bca` | `30072` (`.text+0x7538`) | `31104` (`.text+0x7940`) | `40916` (`.text+0x9f94`) | `165656` (`idx 1170`) | `306fa8f5d0e67a5464af2cac929d1684` | **`e46cb619a0baa0384a64f4fc67220806`** |
| **`WA.v8.7.22` / `WA.v8.7.25`** | `189,880` | `7c76c8ced16cab0ce9ca680ce9c94e51` | `30784` (`.text+0x7800`) | `31816` (`.text+0x7c08`) | `41976` (`.text+0xa3b8`) | `168536` (`idx 1192`) | `3f2e756225bf67947abcc5dd46bccd9d` | **`077d151e0055f198609dc761a39207b3`** |
| **`XC.v8.7.22` / `XC.v8.7.25`** | `189,880` | `5b26b076967befe129f669096539ae21` | `30784` (`.text+0x7800`) | `31816` (`.text+0x7c08`) | `41976` (`.text+0xa3b8`) | `168536` (`idx 1192`) | `c36e694868da56bfec0c0fa3182ac748` | **`7b490ac4d9573dab010b5f4fb95c3765`** |

### Why Clearing `R1` (`R_MIPS_26` $\to$ `R_MIPS_NONE`) Fixes `F01`
At `S1` (`.text+0x7800` on `8.7.25`), the original instruction is `0c000000` (`jal 0`) with an ELF `.rel.text` entry at `R1 = 168536` (`r_offset = 0x00007800`, `r_info = 0x00014804`, type `4 = R_MIPS_26` targeting `ubnt_poll_host_sta_bmiss_ind` at `.text+0x167c`).
- If only `S1` is zeroed (`00000000`), the MIPS kernel module loader (`vmlinux` `0x8000c99c`) still processes `R1` and writes `(((symbol_addr >> 2) + addend) & 0x03ffffff)` into `.text+0x7800`.
- When the 8-byte `.rel.text` entry at `R1` (`168536..168543`) is also zeroed (`0000000000000000`), its relocation type becomes `0` (`R_MIPS_NONE`). In `vmlinux`, `apply_r_mips_none` is a pure no-op (`return 0;`), so `.text+0x7800` remains `0x00000000` (`nop`) in loaded kernel RAM.

---

## 4. Transactional, MD5-Allowlisted, Relocation-Safe Patch Recipe (`F01` & `F02` Remediated)

Instead of dispatching by file size (`wc -c`) or writing directly to `/tmp/uph.ko` without lock/hash verification, the hardened `cron` script:
1. Uses an atomic single-flight lock directory (`mkdir /tmp/uph.lock`).
2. Checks the exact **stock MD5 preimage** (`md5sum $O`) against the known allowlist and **fails closed** on any unknown firmware build.
3. Applies the **4-site relocation-safe splice** (including zeroing the 8-byte `.rel.text` entry at `R1`) into a staging file `/tmp/uph.ko.tmp`.
4. Verifies the **exact post-patch `reloc_safe_md5`** (`EM`) before moving `/tmp/uph.ko.tmp` to `/tmp/uph.ko` and bind-mounting.

5. **Critical Bench Discovery (`ubntconf` `2,042`-Byte Crontab Buffer Limit)**:
   - On `airOS 8` (`WA.v8.7.25`), `/sbin/ubntconf -c /tmp/system.cfg` formats `/etc/crontabs/ubnt` into a fixed **`2,048`-byte buffer** (`2,042` bytes written, `2,030` bytes available for `cron.1.job.1.cmd` after `* * * * * `). Any `cron.1.job.1.cmd` exceeding `2,030` bytes is silently truncated in `/etc/crontabs/ubnt`, breaking shell syntax on boot.
   - Our production-ready `F01 + F02` `cron.1.job.1.cmd` below is **`1,994` bytes** (`2,005` bytes in `/etc/crontabs/ubnt`), preserving **all 10 full 32-char MD5 hashes** (`M` and `K`), the atomic lock (`/tmp/uph.l`), the 3-tick stability window (`/tmp/u_ok`), the 4-site relocation-safe patch, `killall ubntspecd`, and `allow_80211=1`:

```sh
cron.1.job.1.cmd=mkdir /tmp/uph.l 2>/dev/null||exit 0;trap 'rmdir /tmp/uph.l' EXIT;if iwconfig ath0 2>/dev/null|grep -qi 'Access Point: [0-9A-F]';then echo 0 >/tmp/u_ok;exit 0;fi;C=$(cat /tmp/u_ok 2>/dev/null||echo 3);if [ $C -lt 2 ];then echo $((C+1))>/tmp/u_ok;exit 0;fi;echo 0 >/tmp/u_ok;O=/lib/modules/2.6.32.68/ubnt_poll_host.ko;P=/usr/etc/init.d/plugin;D="dd if=$O bs=1";Z="dd if=/dev/zero bs=1";if [ ! -f /tmp/uph.ko ];then M=$(md5sum $O|awk '{print $1}');A=30784;B=30788;E=31820;F=10156;G=41980;H=126556;R=168544;case $M in 5bb5c6687c916822190ea5d687388e4f)A=30040;B=30044;E=31076;F=9808;G=40888;H=124736;R=165632;K=9b516361d0e36ea1c2c5177cb87b6075;;caab5177b3953e1bc51d43b46ca6ff8e)A=30072;B=30076;E=31108;F=9808;G=40920;H=124736;R=165664;K=3a76741ab2c3105c91abaa89ea8420c2;;4103f9d0a2fdbf312d93a68b10647bca)A=30072;B=30076;E=31108;F=9808;G=40920;H=124736;R=165664;K=e46cb619a0baa0384a64f4fc67220806;;7c76c8ced16cab0ce9ca680ce9c94e51)K=077d151e0055f198609dc761a39207b3;;5b26b076967befe129f669096539ae21)K=7b490ac4d9573dab010b5f4fb95c3765;;*)exit 0;;esac;($D count=$A;$Z count=4;$D skip=$B count=1028;awk 'BEGIN{printf "%c",16}';$Z count=2;awk 'BEGIN{printf "%c",6}';$D skip=$E count=$F;awk 'BEGIN{printf "%c%c",36,2}';$Z count=1;awk 'BEGIN{printf "%c",1}';$D skip=$G count=$H;$Z count=8;$D skip=$R)>/tmp/u.t 2>/dev/null;[ "$(md5sum /tmp/u.t|awk '{print $1}')" = "$K" ]||{ rm -f /tmp/u.t;exit 1;};mv /tmp/u.t /tmp/uph.ko;mount --bind /tmp/uph.ko $O;sed -i 's|1 > /sys|0 > /sys|;s|wifi0 1 0 0|wifi0 0 0 0|;s|1 > /proc|0 > /proc|;s|insmod ubnt_poll_host|killall ubntspecd;rmmod ubnt_poll_host;insmod ubnt_poll_host|' /etc/sysinit/radio.conf;sed -i 's|wds 1|wds 0|' /etc/sysinit/wireless.conf;sed -i '/allow_80211/d;s/ap_scan=1/ap_scan=1\nallow_80211=1/' /etc/wpasupplicant_*.conf 2>/dev/null;else umount $O 2>/dev/null;rm -f /tmp/uph.ko;/sbin/ubntconf -c /tmp/system.cfg;fi;for s in wpasupplicant wireless radio;do $P stop $s;done;for s in radio wireless wpasupplicant bridge net route;do $P start $s;done
```

---

## 5. Production Sector Hardware, Telemetry & Layer-2 Audit (`CONFIRMED` — [`stage1_production_telemetry_audit.json`](../artifacts/stage1_production_telemetry_audit.json))

1. **Read-Only `/etc/board.info` & Live Stage 1 Telemetry Across All 4 Candidate Sectors (11 CPEs Total)**:
   - **`Edificio-Panel-Belgrano` (`XC.v8.7.25`, `board.sysid=0xe7e9`, `Rocket Prism 5AC Gen2`, `5700 MHz / 20 MHz`, NF `-86 dBm`, Airtime `32%`)**:
     - `BERON_Carlos` (`1950 m`): `-71 dBm`, CINR `20 dB`, MCS `4x/4x`, `netmode=router`, `NO_CRON`.
     - `ARIAS_Fernanda` (`2400 m`): `-59 dBm`, CINR `23 dB`, MCS `8x/5x`, `netmode=router`, `NO_CRON`.
     - Live read-only kernel audit confirmed `ubnt_poll_host_hsr_diag` (`0x85d07ebc`), `ubnt_prism_hook` (`0x864ac874`), `setup_shift_gpio` (`0x87b03fa0`), `set_shift_register` (`0x87b04058`), `gpio_shift_line_set` (`0x87b04108`), and `SPECTRAL-XMIT-FILTER` IRQ on `wifi1` (`ath_ahb`).
   - **`FT-UOM-1` (`WA.v8.7.25`, `board.sysid=0xe7fd`, `LiteAP GPS`, `5645 MHz / 20 MHz`, NF `-93 dBm`, Airtime `20%`)**:
     - `Yesica Liliana AMATULI` (`900 m`): `-57 dBm`, CINR `27 dB`, MCS `7x/8x`, `netmode=router`, `NO_CRON`.
     - `Aldana MUNOZ` (`300 m`): `-53 dBm`, CINR `25 dB`, MCS `7x/7x`, `netmode=router`, `NO_CRON`.
   - **`Panel3-Guarida` (`WA.v8.7.25`, `board.sysid=0xe8e5`, `LiteAP AC`, `5755 MHz / 20 MHz`, NF `-92 dBm`)**:
     - `TABORDA_Ada_Cristina_Ayelen` (`2700 m`): `-62 dBm`, CINR `24 dB`, MCS `7x/5x`, `netmode=router`, `NO_CRON`.
     - `GALEANO_Rocio_Del_Lujan` (`1050 m`): `-60 dBm`, CINR `29 dB`, MCS `8x/8x` (note: CPE RX chain difference `36 vs 46` = `10 dB` flagged by Stage 1 chain-imbalance detector), `netmode=router`, `NO_CRON`.
     - `SOSA_Joaquin_Alejandro` (`450 m`): `-56 dBm`, CINR `23 dB`, MCS `7x/7x`, `netmode=router`, `NO_CRON`.
   - **`Panel1-Guarida` (`WA.v8.7.25`, `board.sysid=0xe8e5`, `LiteAP AC`, `5240 MHz / 20 MHz`, NF `-94 dBm`, Airtime `27%`)**:
     - `FARELA Juan Jose` (`300 m`): `-53 dBm`, CINR `21 dB`, MCS `7x/5x`, `netmode=router`, `NO_CRON`.
     - `SCHECHTEL_Camila` (`900 m`): `-65 dBm`, CINR `22 dB`, MCS `7x/6x`, `netmode=router`, `NO_CRON`.
     - `GAMBOA_Gabriela` (`300 m`): `-45 dBm`, CINR `25 dB`, MCS `7x/6x`, `netmode=router`, `NO_CRON`.
     - `MONZON Stella Maris` (`300 m`): `-59 dBm`, CINR `23 dB`, MCS `8x/6x`, `netmode=router`, `NO_CRON`.
2. **Decisive Layer-2 Finding Across All 11 Production CPEs (`F03` Production Scope Closed)**:
   - Every single CPE across all 4 candidate sectors runs **`netmode=router`** with **`bridge.1.port.1.devname=ath0` only** (`eth0` is the customer LAN behind the CPE's NAT router, `vlan.status` is disabled on all 11 CPEs, and `ebtables` has `0` rules).
   - Consequently, **zero customer MACs are bridged onto the wireless link and zero `802.1Q` VLAN tags traverse `ath0`**: 100% of wireless data frames emitted by all 11 production CPEs are untagged IPv4/ARP frames originated by the CPE's own `br0` (`ath0`) interface — the exact packet profile verified on the bench!

---

## 6. Stage 10B Bench Qualification Checklist (`F01`, `F02`, `F03` — `CONFIRMED` on Physical Bench)

Per [`docs/ADVERSARIAL_REVIEW_STAGE10_11.md`](ADVERSARIAL_REVIEW_STAGE10_11.md), we executed and verified all three qualification checks on `192.168.1.2` (`LAP-120` OpenWrt 24.10.4) $\leftrightarrow$ `192.168.1.20` (`Loco 5AC` `WA.v8.7.25`):
- [x] **Check 1 (`F01` Closure — `CONFIRMED` via `/dev/mem` & 35s AP Outage Survival)**:
  - Deployed the 4-site relocation-safe `/tmp/uph.ko` (`MD5: 077d151e0055f198609dc761a39207b3`) with `killall ubntspecd` before `rmmod ubnt_poll_host`, and verified in `/dev/mem` (`base 0x82300000`, `refcnt = 0`):
    - `0x82307800` (`S1` `bmiss` caller): **`0x00000000` (`nop`)**
    - `0x82307c08` (`S2` `timer` branch): **`0x10000006` (`b +6`)**
    - `0x8230a3b8` (`S3` `is_ap_valid`): **`0x24020001` (`addiu $v0, $zero, 1`)**
  - Brought the AP radio down for **35 seconds** (triggering both the 2s beacon-miss path and the 30s missing-poll timer): the CPE survived with **zero panic and zero reboot** (`uptime` advanced continuously from `11434.89s` to `11520.65s`) and automatically reassociated (`47.54s`).
- [x] **Check 2 (`F02` Closure — `CONFIRMED` Fault Injection + Hands-Free Cold Reboot)**:
  - Verified unknown-hash fail-closed behavior (`UNKNOWN_HASH_TEST=FAIL_CLOSED_OK`), discovered the `2,042`-byte `/sbin/ubntconf` crontab buffer limit, persisted the `1,994`-byte hardened recipe (`2,005` bytes in `/etc/crontabs/ubnt`, `cfgmtd rc=0`), and executed a full cold reboot of `192.168.1.20`.
  - The CPE automatically patched `/tmp/uph.ko` (`077d151e0055f198609dc761a39207b3`), associated hands-free over **`VHT20` (`20 MHz`) + `WPA2-PSK CCMP`** at **`173.3 MBit/s` RX / `144.4 MBit/s` TX**, and delivered **`89.5 Mbps` 4-stream TCP Uplink (`95.6 Mbps` peak, `0` retransmits, `4.48 bit/s/Hz`)** and **`70.2 Mbps` 4-stream TCP Downlink (`72.2 Mbps` peak)** ([`f01_bench_verification.json`](../artifacts/adversarial_review_stage10_11/f01_bench_verification.json)).
- [x] **Check 3 (`F03` Closure — `CONFIRMED` L2 Matrix + Production `netmode=router` Audit)**:
  - Bench L2 matrix confirmed `0%` loss across Unicast/Broadcast ARP, `1500`-byte MTU (`ping -s 1472`, `2.680 ms` avg RTT), and IPv6 Link-Local ND (`1.805 ms` avg RTT) ([`f03_l2_matrix_bench.json`](../artifacts/adversarial_review_stage10_11/f03_l2_matrix_bench.json)), and the production audit confirmed all 11 CPEs across all 4 candidate sectors operate in `netmode=router` (`bridge.1.port.1.devname=ath0` only, untagged IPv4).


