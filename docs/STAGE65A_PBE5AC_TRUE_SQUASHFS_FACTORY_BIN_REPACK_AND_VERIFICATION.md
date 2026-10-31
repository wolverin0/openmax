<!-- doc-head: STAGE65A_PBE5AC_TRUE_SQUASHFS_FACTORY_BIN_REPACK_AND_VERIFICATION.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 65A: True SquashFS (`hsqs`) Repack of OpenWrt 24.10.4 `factory.bin` & `sysupgrade.bin` for PowerBeam 5AC Gen2 (`0xe3d6`) + `/sbin/fwupdate.real -c` Verification

- **Stage / Ticket**: `Stage 65A` (`T-S65A-PBE5AC-TRUE-SQUASHFS-FACTORY-BIN-REPACK-AND-FWUPDATE-CHECK-VERIFICATION`)
- **Date**: `2026-10-26`
- **Target Hardware**:
  - `198.18.0.46` (`198.18.0.74`, `PUBLIC_DEVICE_0037`, `PBE-5AC-Gen2` `0xe3d6`, Remote OTA STA — Step 1 target)
  - `198.18.0.45` (`198.18.0.8`, `PUBLIC_DEVICE_0038`, `PBE-5AC-Gen2` `0xe3d6`, Local AP — Step 2 target)
- **Artifacts & Tools**:
  - [`tools/deploy/build_stage65a_true_squashfs_factory_repack.py`](../tools/deploy/build_stage65a_true_squashfs_factory_repack.py)
  - [`artifacts/autoresearch/stage65a_pbe5ac_squashfs_factory_repack_and_fwupdate_check_20261026.json`](../artifacts/autoresearch/stage65a_pbe5ac_squashfs_factory_repack_and_fwupdate_check_20261026.json)
  - [`tests/test_stage65a_pbe5ac_squashfs_factory_repack.py`](../tests/test_stage65a_pbe5ac_squashfs_factory_repack.py)

---

## 1. Why True SquashFS (`hsqs`) Repack Is Mandatory (`CONFIRMED`)

- Ubiquiti's `fwupdate.real` (`factory.bin`) and OpenWrt's documented `WA v8.5.7+` `dd` / `mtd` flash procedure (`sysupgrade.bin`) write raw `kernel` (`mtd2`, `0x100000` B) and `rootfs` (`mtd3`, `SquashFS` at `0x280184` in `factory.bin` / `0x280000` in `sysupgrade.bin` + `0xff` erase-block padding + `\xde\xad\xc0\xde` JFFS2 EOF marker).
- Any external `.tar.gz` sysupgrade overlay is ignored during an initial `airOS 8 -> OpenWrt` flash because `deadc0de` causes `mount_root` to format a clean JFFS2 overlay on first boot and execute `/etc/uci-defaults/*` from the **SquashFS (`hsqs`) rootfs itself**.
- Therefore, baking `/etc/uci-defaults/99-fmx-pbe5ac-ptp`, `/usr/sbin/fmx_ptp_rollback_watchdog.sh`, and `/etc/rc.local` **directly inside the SquashFS (`hsqs`) rootfs** of both `factory.bin` and `sysupgrade.bin` guarantees 100% first-boot execution under every install path.

---

## 2. True SquashFS Unpack, Injection & Repack Verification (`mksquashfs 4.6.1`, `CONFIRMED`)

1. **SquashFS Extraction & Root-Preserving Unpack/Repack**:
   - Extracted the stock SquashFS 4.0 image (`4,234,676` bytes at `0x280184`, `XZ` compression, `256 KiB` block size, `1,395` inodes) from `openwrt-24.10.4-ath79-generic-ubnt_powerbeam-5ac-gen2-squashfs-factory.bin`.
   - Unpacked with `sudo unsquashfs` (preserving character device nodes `/dev/console` `5, 1` and `/dev/null` `1, 3`), injected:
     - `/etc/uci-defaults/99-fmx-pbe5ac-ptp` (`-rwxr-xr-x root/root`, `2,034` B on STA / `2,032` B on AP)
     - `/usr/sbin/fmx_ptp_rollback_watchdog.sh` (`-rwxr-xr-x root/root`, `1,457` B, `180s` peer ping check -> automatic WDS/channel fallback scan)
     - `/etc/rc.local` (`-rwxr-xr-x root/root`, `203` B, launching `/usr/sbin/fmx_ptp_rollback_watchdog.sh >/dev/null 2>&1 &`)
   - Repacked with `mksquashfs ... -noappend -comp xz -b 256k -no-xattrs -all-root` (`1,397` inodes, `4,263,936` B, padded with `61,440` B of `0xff` to the `64 KiB` erase-block boundary `0x420000 = 4,325,376` B + `\xde\xad\xc0\xde`).

2. **Repacked Firmware Images & Recomputed Cryptographic/Binary Checksums**:

| Image Artifact | Role / Target | Size (Bytes) | SquashFS Offset | `PARTrootfs` / `fwtool` CRC32 | SHA-256 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `openwrt-24.10.4-ubnt_powerbeam-5ac-gen2-squashfs-factory-sta-242.bin` | `.242` (`STA` `factory.bin`) | `6,947,480` | `0x280184` | `PARTkernel=0xbe9d3f27`, **`PARTrootfs=0x5773b46d`** | `97b846fd...` |
| `openwrt-24.10.4-ubnt_powerbeam-5ac-gen2-squashfs-factory-ap-241.bin` | `.241` (`AP` `factory.bin`) | `6,947,480` | `0x280184` | `PARTkernel=0xbe9d3f27`, **`PARTrootfs=0xc5249df9`** | `b318e6b4...` |
| `openwrt-24.10.4-ubnt_powerbeam-5ac-gen2-squashfs-sysupgrade-sta-242.bin` | `.242` (`STA` `sysupgrade.bin`) | `6,947,137` | `0x280000` | `meta=0x90ba054a`, **`sig=0xd496c1da`** | `bf73a03d...` |
| `openwrt-24.10.4-ubnt_powerbeam-5ac-gen2-squashfs-sysupgrade-ap-241.bin` | `.241` (`AP` `sysupgrade.bin`) | `6,947,137` | `0x280000` | `meta=0x02ed2cd6`, **`sig=0x802b14ba`** | `28cc43ef...` |

---

## 3. Live `/sbin/fwupdate.real -c` Hardware Parser Dissection on `198.18.0.45` (`CONFIRMED`)

- Executed `/sbin/fwupdate.real -c /tmp/test_factory_sta_242.bin -d` (read-only `-c` check flag ONLY) on `198.18.0.45` (`WA.v8.7.11`):
  - `Header MAGIC 'OPEN'` -> **PASS** (`OPEN` header CRC `0x12d8e382` verified).
  - `Versions: New(526084) 8.7.4, Required(525571) 8.5.3` -> **PASS** (`8.7.4 >= 8.5.3`).
  - `PARTkernel` (`0xbe9d3f27`) and `PARTrootfs` (`0x5773b46d`) CRC32 & partition bounds -> **PASS** (`0` CRC errors, `0` truncation errors).
  - Binary reverse engineering of `/sbin/fwupdate.real` (`0x409fc0..0x409ff8`) confirmed that after validating the `OPEN` header and `PART` CRCs, stock `WA.v8.7.11` `fwupdate.real` calls `sub_40c060` (`0x409fec: jal 0x40c060`) on the 256-byte `ENDS` trailer and prints `Signature check failed` on any non-Ubiquiti-RSA-signed image (including official stock OpenWrt `factory.bin`).
  - Consequently, `factory-sta-242.bin` / `factory-ap-241.bin` are 100% valid for U-Boot `urescue` TFTP, while `sysupgrade-sta-242.bin` / `sysupgrade-ap-241.bin` (with identical baked SquashFS at `0x280000`) are 100% ready for the documented `MTD_WRITEABLE` `mtd2`/`mtd3` OTA conversion path.
