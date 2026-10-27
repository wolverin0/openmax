<!-- doc-head: STAGE399A_LTU_DUALBANK_NAND_AMEIMG_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 399A — Ground-Up Binary RE of LTU Dual-Bank NAND Flash & `AMEIMG` Upgrade State Machine

- **Status**: `CONFIRMED`
- **Attribution**: `proprietary airMAX/LTU module`, `Linux`, `hardware`
- **Inspected Containers**: `afltu_2.4.2` (`7` extracted parts) & `aflturocket_2.4.2` (`12` extracted parts).

## 1. Dual-Bank NAND/SPI-NOR Partition & Failover Architecture (`CONFIRMED`)
| Partition | Name | Protected? | Role in Dual-Bank `AMEIMG` Boot & Upgrade State Machine |
| :--- | :--- | :--- | :--- |
| `mtd0` / `mtd1` | `spl` / `uboot` | **YES** | Preloader & U-Boot bootloader (NEVER modify). |
| `mtd2` / `mtd3` | `uboot_env0` / `uboot_env1` | **YES** | Redundant boot environment storing active bank pointer (`boot_bank=0|1`). |
| `mtd4` / `mtd5` | `dtb0` / `dtb1` | Banked | Dual Device Tree Blobs for `amesoc3` HPS + FPGA bridge. |
| `mtd6` / `mtd7` | `kernel0` / `kernel1` | Banked | Dual `Linux 3.14.65 SMP PREEMPT RT` `uImage` banks. |
| `mtd8` / `mtd9` | `rootfs0` / `rootfs1` | Banked | Dual SquashFS rootfs + `part05_fpga.bin` bitstream banks. |
| `mtd10` | `cfg` (`/etc/persistent`) | User Config | Stores `/etc/persistent/rc.poststart` (`cfgmtd -w -p /etc/`). |
| `mtd11` | `eeprom` | **YES** | Factory MAC, board ID (`0xae02..0xae0b`), and `AD9361`/PA calibration tables. |

## 2. Universal 5-Board CPE + Rocket AP Compatibility (`CONFIRMED`)
All 5 LTU CPE boards (`0xae02` `LTU-Pro`, `0xae07` `LTU-LR`, `0xae08` `LTU-Lite`, `0xae09` `LTU-XR`, `0xae0b` `LTU-Instant`) share the identical `afltu` `AMEIMG` rootfs and `Linux 3.14.65 SMP PREEMPT RT` kernel, while `0xae06` (`LTU-Rocket`) runs `aflturocket`. Deploying [`rc.poststart_ltu_safe_champion.sh`](../firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh) inside `/etc/persistent/` (`mtd10`) operates 100% in userspace/sysctl/qdisc without touching `mtd0..mtd9` or `mtd11`.
