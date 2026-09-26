# FMX-0002 — LAP-120 boot/recovery qualification runbook

Summary: the exact, ordered procedure to install OpenWrt on the lab LiteAP AC (LAP-120, sysid
0xe8e5, airOS 8.5.12) using the bootloader's own `urescue` TFTP server — which is simultaneously
the install path AND the recovery path, and never writes u-boot. Install and rollback are the
same operation with a different image, so recovery is exercised rather than rehearsed.
Keywords: FMX-0002, urescue, TFTP recovery, u-boot 1.1.4-s1100, OPEN magic, return-to-stock,
no-serial, LAP-120, dd-unlock (WITHDRAWN).
Read when: about to flash the lab unit, or to recover a bricked WA-board unit.
Status: CURRENT (2026-08-08, rev 2). Physical steps require the operator.
**Never write u-boot / u-boot-env / EEPROM.**

> **rev 2 correction.** Rev 1 made the dd-unlock method the primary install route. That route
> requires letting airOS's `fwupdate` write `u-boot` to `mtd0` before interrupting it — which
> contradicts this document's own hard boundary and AGENTS.md §4. On a unit with **no serial and
> no case access** it is also the only operation here with no fallback: a failure or power loss
> during the u-boot write destroys the bootloader, and with it `urescue` itself, leaving only an
> SPI clip on the flash chip. **Route A is withdrawn for this unit.** Route C (urescue-only) is
> primary. Rev 1 also proposed rehearsing recovery by pushing stock airOS onto a healthy unit;
> that is ceremony — it spends a flash cycle and a site visit re-proving a mechanism that the
> install itself exercises. Replaced by a zero-write entry check (§2).

---

## 0. Evidence base (all from THIS unit, read-only — `inventory/board_probe/preflash_probe.py`)

- Bootloader: **U-Boot 1.1.4-s1100 (Sep 5 2018)**, pulled from `mtd0` of the live unit
  (`research/raw/hardware/lab-lap120-mtd0-u-boot-*.bin`, sha256 in that dir).
- **`urescue` IS present in the bootloader** — strings: `urescue - start TFTP server and wait
  for firmware`, `Starting TFTP server...`, with default env `ipaddr=192.168.1.20`,
  `serverip=192.168.1.254`. This is the recovery path and it is independent of airOS.
- Bootloader magic table contains **`OPEN`** and `ENDS` next to `UBNT`/`PART`/`END.` — i.e. the
  stock bootloader recognises the OpenWrt `OPEN` image magic. INFERRED-strong (string table,
  not disassembled dispatch); the `urescue` physical test in §3 is what turns it CONFIRMED.
- `/bin/ubntbox` (8.5.12, sha256 `6ea397e5…`) contains an OpenSSL RSA image check
  (`EVP_VerifyFinal`, `Signature check failed`). **None of the three published sed patch
  patterns (`14 40 fe ff`, `14 40 fe fe`, `14 40 fe 27`) exist in it** — so the wiki's
  version-specific fwupdate patch cannot be reused as-is. This is why Route A is primary.
- OpenWrt version-bug clearance: the 23.05<.3 / 24.10<.3 read-only-flash bug does NOT affect us —
  our image is **24.10.4** (Linux 6.6.110; fix landed in 24.10.3 / 6.6.103). VERIFIED.
- Images SHA-256-verified against OpenWrt `sha256sums`:
  - factory `943d812c…` (7,013,016 B, magic `OPENWA.ar934x.v8.7.4-42`)
  - sysupgrade `cc01cbb3…` (7,012,651 B, `MIPS OpenWrt Linux-6.6.110`)

Flash map on this unit (stock airOS):
`mtd0 u-boot 256K · mtd1 u-boot-env 64K · mtd2 kernel 1M · mtd3 rootfs 14.4M · mtd4 cfg 256K ·
mtd5 EEPROM 64K`. **Never write mtd0, mtd1, mtd5.**

---

## 1. Operating constraint and host prep

**No serial console; the case will not be opened.** (Operator, 2026-08-08.) Everything below is
therefore button-and-LED driven. The consequence that matters: **any operation that writes
`u-boot` is unrecoverable on this unit**, because the SPI-clip rescue of last resort needs the
case open. That single constraint is what selects Route C and withdraws Route A.

### Host prep (operator PC on the flat 192.168.1.0/24 segment)
1. Host needs **any** address on `192.168.1.0/24` — this bench PC is already `192.168.1.21`
   (Ethernet 2). It does **not** need to be `192.168.1.254`: in urescue the *unit* is the TFTP
   **server** at `192.168.1.20` and the host is the client, so `serverip=192.168.1.254` in the
   unit's u-boot env is irrelevant here (it only matters if the unit pulls a file via `tftpboot`).
2. Disable any other interface that could route 192.168.1.0/24 (Wi-Fi especially), so the TFTP
   transfer cannot leave via the wrong NIC.
3. **Windows Firewall:** TFTP data returns from a *new ephemeral port*, which the firewall
   commonly drops silently. Symptom is a probe that succeeds followed by a push that stalls at
   block 1. Allow the Python process, or disable the firewall on that adapter for the transfer.
3. Both images are staged and verified:
   - `firmware/openwrt/openwrt-24.10.4-…-ubnt_lap-120-squashfs-factory.bin` — `OPEN` magic,
     7,013,016 B, sha256 `943d812c…` (install)
   - `firmware/WA.v8.5.12.40181.190213.1104.bin` — `UBNT` magic, 8,738,874 B,
     sha256 `4bda8ddf…`, identical build to what the unit runs now (rollback) ✅ present
4. Power the unit from a source you can cut and restore cleanly, ideally not a PoE switch port
   that renegotiates slowly. Do not cut power *during* a write.

---

## 2. Prove urescue ENTRY — zero writes

The uncertain step on a no-serial unit is not "does urescue work" (it is the standard Ubiquiti
recovery mechanism and works across the product line); it is **can the operator reach it blind,
by LED pattern alone, on this unit.** That is testable without writing anything.

1. Set the host NIC to **192.168.1.254/24**.
2. Power off the unit. Press and hold **RESET**, apply power while still holding.
3. Keep holding ~15–20 s until the LED pattern changes to the alternating/sequencing urescue
   pattern. Release.
4. On the host, confirm the unit is sitting in the bootloader's TFTP server — **no image sent**:
   ```
   python safety/recovery/urescue_push.py --probe-only
   ```
   This pings 192.168.1.20 and checks UDP/69 answers. Nothing is uploaded.
5. If it answers → **entry CONFIRMED**; power-cycle normally back into airOS and proceed to §4.
   If it does not answer → adjust hold time / retry; do **not** proceed to any flash until entry
   is reproducible. Getting this wrong later is what turns a failed flash into a dead unit.

Do this twice, so entry is known-repeatable rather than a one-off.

---

## 3. What the install itself proves (why there is no separate rehearsal)

`urescue` is one mechanism used two ways: push the OpenWrt factory image and it is an *install*;
push the stock `WA.v8.5.12` image and it is a *recovery*. Same entry, same tool, same transfer —
only the file differs. So exercising the install exercises the recovery path; rehearsing it first
on a healthy unit costs a flash cycle and a site visit and proves nothing the install will not.

**Rejection is cheap — this is what makes it safe to simply try.** This unit's bootloader runs the
update as two separate calls, `go ${ubntaddr} ucheck_fw …` then `go ${ubntaddr} uupdate_fw …`:
validate first, write second. TFTP lands the image in RAM at `ubntaddr=0x80200020`, and the
check runs against RAM. If the OpenWrt `OPEN`-magic image is refused (`Signature authentication
failed`), **nothing has been written and the unit is still on airOS 8.5.12.** CONFIRMED: the
two-call sequence, from the pulled u-boot. INFERRED: that no flash erase precedes the check.
Treat the first attempt as the experiment that settles it.

---

## 4. Install — Route C: urescue only (PRIMARY)

Never writes u-boot. Same mechanism as recovery. Refusal costs nothing (§3).

1. Enter urescue exactly as in §2 (host 192.168.1.254/24, unit 192.168.1.20).
2. Push the OpenWrt **factory** image — it must be `factory`, not `sysupgrade`; urescue expects
   the `OPEN`/`PART` container, and `urescue_push.py` will warn if handed a bare uImage:
   ```
   python safety/recovery/urescue_push.py \
     --image firmware/openwrt/openwrt-24.10.4-ath79-generic-ubnt_lap-120-squashfs-factory.bin \
     --expect-sha256 943d812c40e8f1e6bfb71b32b12395fdd480b62318bc537c7687f8affa9378c0
   ```
3. The unit validates, writes the firmware region, and reboots itself. Do **not** cut power.
4. Health check: OpenWrt on `192.168.1.1`, SSH/LuCI reachable; `dmesg | grep ath10k` shows
   `qca988x hw2.0 … firmware ver 10.2.4-…` and a `wlan0`; `cat /proc/mtd` shows the OpenWrt
   8-partition layout (`mtd2 firmware`, `mtd5 rootfs_data`).
5. **Reboot once more and re-check config persistence** — this is the 23.05/24.10 read-only-flash
   symptom. 24.10.4 contains the fix, so settings must survive; if they do not, say so rather
   than working around it.

**If urescue refuses the OPEN image** (`Signature authentication failed`): nothing was written,
the unit is still airOS 8.5.12. Record it — that is a real FMX-0002 result and it means signed-
bootloader enforcement extends to urescue on this board. Fall back to Route B, not Route A.

### Route B — patched fwupdate + factory image (fallback)
Requires deriving a new patch offset by disassembling the `EVP_VerifyFinal` caller in the pulled
8.5.12 `ubntbox`; **no published pattern matches** (§0). Writes only kernel+rootfs via fwupdate,
not u-boot. Deferred unless Route C is refused.

### Route A — dd-unlock — **WITHDRAWN for this unit**
The wiki's "airOS 8.5.7 and newer" method requires letting stock `fwupdate` write **u-boot** to
`mtd0` before interrupting it. That violates AGENTS.md §4, and with no serial and no case access
a failed u-boot write is unrecoverable (it destroys `urescue` itself; only an SPI clip remains).
Do not use it on a unit that cannot be opened. Recorded here so it is not re-proposed.

### Post-install health check
- OpenWrt boots, `br-lan` at 192.168.1.1, SSH/LuCI reachable.
- `dmesg | grep ath10k` shows `qca988x hw2.0 … firmware ver 10.2.4-…` and a created `wlan0`.
- Flash map shows the OpenWrt 8-partition layout (mtd2 `firmware`, mtd5 `rootfs_data`).

---

## 5. Rollback / return-to-stock

Identical procedure to the install, different file — that is the point of Route C.

1. Enter `urescue` (§2).
2. Push the stock image (present and verified):
   ```
   python safety/recovery/urescue_push.py \
     --image firmware/WA.v8.5.12.40181.190213.1104.bin \
     --expect-sha256 4bda8ddf20a4b6f6ed3cc77f7616b283fe67e7604c61adcdd2f0342dd27f6270
   ```
   This is byte-identical to the build the unit shipped with here, so the rollback target is the
   exact baseline rather than an approximation of it.
3. Re-run `inventory/board_probe/preflash_probe.py` to confirm baseline (sysid 0xe8e5, 0 clients,
   chanbw 40, no `polling_ff` keys).

## 6. Hard boundaries (AGENTS.md §4)
Never write `mtd0` (u-boot), `mtd1` (u-boot-env), `mtd5` (EEPROM/calibration). No DFS disable, no
EIRP change. Lab unit only — production radios are read-only.
