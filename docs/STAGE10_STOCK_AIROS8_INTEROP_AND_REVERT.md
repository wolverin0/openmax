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

```sh
# Relocation-safe 4-site builder with preimage & postimage MD5 verification:
O=/lib/modules/2.6.32.68/ubnt_poll_host.ko
M=$(md5sum $O | awk '{print $1}')
case "$M" in
  5bb5c6687c916822190ea5d687388e4f) S1=30040; S2=30044; S3=31076; C3=9808; S4=40888; C4=124736; R2=165632; EM=9b516361d0e36ea1c2c5177cb87b6075 ;;
  caab5177b3953e1bc51d43b46ca6ff8e) S1=30072; S2=30076; S3=31108; C3=9808; S4=40920; C4=124736; R2=165664; EM=3a76741ab2c3105c91abaa89ea8420c2 ;;
  4103f9d0a2fdbf312d93a68b10647bca) S1=30072; S2=30076; S3=31108; C3=9808; S4=40920; C4=124736; R2=165664; EM=e46cb619a0baa0384a64f4fc67220806 ;;
  7c76c8ced16cab0ce9ca680ce9c94e51) S1=30784; S2=30788; S3=31820; C3=10156; S4=41980; C4=126556; R2=168544; EM=077d151e0055f198609dc761a39207b3 ;;
  5b26b076967befe129f669096539ae21) S1=30784; S2=30788; S3=31820; C3=10156; S4=41980; C4=126556; R2=168544; EM=7b490ac4d9573dab010b5f4fb95c3765 ;;
  *) exit 0 ;;
esac
(dd if=$O bs=1 count=$S1; dd if=/dev/zero bs=1 count=4; dd if=$O bs=1 skip=$S2 count=1028; awk 'BEGIN{printf "%c",16}'; dd if=/dev/zero bs=1 count=2; awk 'BEGIN{printf "%c",6}'; dd if=$O bs=1 skip=$S3 count=$C3; awk 'BEGIN{printf "%c%c",36,2}'; dd if=/dev/zero bs=1 count=1; awk 'BEGIN{printf "%c",1}'; dd if=$O bs=1 skip=$S4 count=$C4; dd if=/dev/zero bs=1 count=8; dd if=$O bs=1 skip=$R2) > /tmp/uph.ko.tmp 2>/dev/null
PM=$(md5sum /tmp/uph.ko.tmp | awk '{print $1}')
if [ "$PM" = "$EM" ]; then mv /tmp/uph.ko.tmp /tmp/uph.ko; else rm -f /tmp/uph.ko.tmp; exit 1; fi
```

---

## 5. Production Sector Hardware Audit & Full Revert Receipt (`CONFIRMED`)

1. **Read-Only `/etc/board.info` Hardware Audit Across Candidate Sectors**:
   - **`Sector-Belgrano` (2 CPEs)**: `board.sysid=0xe7e9`, `board.name=Rocket Prism 5AC` (`XC.v8.7.25`, `RP-5AC-Gen2`). Uses Ubiquiti's AirPrism active RF filter (`prism` bit 30 + `hsr` bit 28) and dual-radio architecture (`wifi0` `QCA9880` + `wifi1` `QCA9558` AHB). Must NOT be flashed with single-radio `WA` `ubnt_lap-120` images.
   - **`Sector-Guarida-3` (3 CPEs)** & **`Sector-Guarida-1` (4 CPEs)**: `board.sysid=0xe8e5`, `board.name=LiteAP AC` (`WA.v8.7.25`, `LAP-120`) — exact `0xe8e5` hardware match to the physical bench AP (`192.168.1.2`).
   - **`Sector-UOM-1` (2 CPEs)**: `board.sysid=0xe7fd`, `board.name=LiteAP GPS` (`WA.v8.7.25`, `LAP-GPS`).
2. **Production Sector Status (`Sector-Guarida-1` — 100% Untouched Stock Confirmed)**:
   - Full partition backups (`mtd0`, `mtd1`, `mtd4`, `mtd5`) were verified with `100%` local/remote MD5 parity.
   - Per Operator Option A (`2026-10-18`), the temporary `cron.*` pre-staging on the 4 CPEs of `Sector-Guarida-1` was **completely removed and reverted to original stock `system.cfg` (`NO_CRON_LINES` verified on `mtd4`, `CFGMTD_RC=0`, `crond` stopped, `/etc/crontabs/ubnt` removed)** while all 4 CPEs remained continuously associated to their stock `WA.v8.7.25` AP (`link_uptime` uninterrupted).

---

## 6. Stage 10B Bench Qualification Checklist (Before Any Production Canary Migration)

Per [`docs/ADVERSARIAL_REVIEW_STAGE10_11.md`](ADVERSARIAL_REVIEW_STAGE10_11.md), the following isolated bench checks are scheduled on `192.168.1.2` (`LAP-120`) $\leftrightarrow$ `192.168.1.20` (`Loco 5AC`) before any production sector cutover:
- [x] **Check 1 (`F01` Closure — `CONFIRMED` on `192.168.1.20` via `/dev/mem`)**: Deployed the 4-site relocation-safe `/tmp/uph.ko` (`MD5: 077d151e0055f198609dc761a39207b3`) on the bench `WA.v8.7.25` `Loco 5AC` (`192.168.1.20`), discovered that `/bin/ubntspecd` holds `/dev/uph_wifi0` (`fd 6`, major `190`) open during `plugin stop radio`, added `killall ubntspecd` before `rmmod ubnt_poll_host`, and read back the live loaded `.text` bytes from `/dev/mem` at `0x81400000` (`phys 0x01400000`):
  - `0x81407800` (`S1` `bmiss` caller): **`0x00000000` (`nop`, `top6=0, low26=0`)**
  - `0x81407c08` (`S2` `timer` branch): **`0x10000006` (`b +6`)**
  - `0x8140a3b8` (`S3` `is_ap_valid`): **`0x24020001` (`addiu $v0, $zero, 1`)**
  - Full evidence archived in [`f01_bench_verification.json`](../artifacts/adversarial_review_stage10_11/f01_bench_verification.json).
- [ ] **Check 2 (`F02` Closure — `cron` Persisted on `192.168.1.20`; Pending Cold Power-Cut & Multi-Hour Soak)**: Persisted the MD5-allowlisted, 4-site relocation-safe + `killall ubntspecd` recipe to `mtd4` (`cfgmtd -w -p /etc/`) on `192.168.1.20`. Remaining before production cutover: multi-hour soak + physical POE power-cut cold boot.
- [ ] **Check 3 (`F03` Closure — Endpoint L2 Matrix `CONFIRMED`; Multi-Host Bridge Behind CPE LAN Port Pending)**:
  - **Unicast & Broadcast ARP (`ip neigh flush` + `ping`)**: **`PASS` (`0%` loss)**
  - **Full `1500`-Byte MTU (`ping -s 1472`)**: **`PASS` (`3/3`, `0%` loss, `2.680 ms` avg RTT)**
  - **IPv6 Link-Local Neighbor Discovery (`ND` / `ICMPv6` `ping6 fe80::feec:daff:fec2:540a%phy0-ap0`)**: **`PASS` (`3/3`, `0%` loss, `1.805 ms` avg RTT)**
  - **`802.1Q` VLAN-Tagged Frames (`VLAN 100` `0x8100`)**: `0/3` received in `wds=0` (`ARPNAT` 3-address mode), confirming that untagged customer access ports (`IPv4`, `ARP`, `IPv6`, `1500B MTU`) pass cleanly across the 14-byte `0x6558` decapsulation hook, whereas `802.1Q` VLAN trunks require either `wds=1` 4-address mode or inner-VLAN offset handling in `ebt_arpnat` ([`f03_l2_matrix_bench.json`](../artifacts/adversarial_review_stage10_11/f03_l2_matrix_bench.json)).

