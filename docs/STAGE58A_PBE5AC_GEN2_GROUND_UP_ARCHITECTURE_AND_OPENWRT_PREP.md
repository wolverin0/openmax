<!-- doc-head: STAGE58A_PBE5AC_GEN2_GROUND_UP_ARCHITECTURE_AND_OPENWRT_PREP.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 58A — PowerBeam 5AC Gen2 (`PBE-5AC-Gen2`, `0xe3d6`) Ground-Up Architecture Dissection, Caldata Backup & OpenWrt 24.10.4 Preparation (`T-S58A-PBE5AC-GEN2-GROUND-UP-ARCHITECTURE-CALDATA-BACKUP-AND-OPENWRT-BUILD`)

## 1. Ground-Truth Hardware Identity across `.241`, `.242`, and `.251` (`CONFIRMED`)

| Host IP | Physical Port / Path | Device Model | Board Family | `board.sysid` | Base MAC (`eth0` / `ath0`) | SoC / Clocks | Main Radio (`wifi0`) | Secondary Radio (`wifi1`) | Running Firmware |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :--- |
| **`198.18.0.45`** | `eth3` (Wired PtP AP) | **PowerBeam 5AC Gen2 (`PBE-5AC-Gen2`)** | `WA` | **`0xe3d6`** | `PUBLIC_DEVICE_0038` (`eth0` `PUBLIC_DEVICE_0064`) | `AR9342` rev 3 (`535/400/200 MHz`), `64 MiB` DDR2 | `QCA9882` PCIe (`0777:e3d6`), 5 GHz `25 dBi` (`400mm` dish) | `AR9342` AHB `wmac` 2.4 GHz mgmt (`PUBLIC_DEVICE_0093`) | `WA.v8.7.11` |
| **`198.18.0.46`** | Over-the-Air PtP STA | **PowerBeam 5AC Gen2 (`PBE-5AC-Gen2`)** | `WA` | **`0xe3d6`** | `PUBLIC_DEVICE_0037` (`eth0` `PUBLIC_DEVICE_0094`) | `AR9342` rev 3 (`535/400/200 MHz`), `64 MiB` DDR2 | `QCA9882` PCIe (`0777:e3d6`), 5 GHz `25 dBi` (`400mm` dish) | `AR9342` AHB `wmac` 2.4 GHz mgmt (`PUBLIC_DEVICE_0095`) | `WA.v8.7.11` |
| **`198.18.0.48`** | `gi8` (`SG350-28P`) | **Rocket 2AC Prism (`R2AC-PRISM`)** | `2XC` | **`0xe2f2`** | `PUBLIC_DEVICE_0042` | `QCA9558` (`720 MHz`), `128 MiB` DDR2 | `QCA988x` PCIe (`0777:e2f2`), **2.4 GHz** (`devdomain=2400`) + GPS | `QCA9558` AHB `wmac` 2.4/5 GHz mgmt/AirView | `2XC.v8.7.11` |

---

## 2. Mandatory Protected-Partition & `mtd5` Caldata Backups (`AGENTS.md` §4 — `0` Flash Writes)

All protected partitions (`mtd0` `u-boot`, `mtd1` `u-boot-env`, `mtd4` `cfg`, `mtd5` `EEPROM/ART`) from both **PowerBeam 5AC Gen2** units (`198.18.0.45` and `198.18.0.46`) are backed up bit-for-bit under [`inventory/calibration_hash/pbe5ac_gen2_20261026/`](../inventory/calibration_hash/pbe5ac_gen2_20261026/):

| Unit | Partition | Size (Bytes) | Flash Offset | SHA-256 Digest | Internal Verification |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **`.241` (`AC8BA9C28A01`)** | `mtd0` (`u-boot`) | `262,144` | `0x00000000` | `b3d54d2c7eb154361dad22dbf880dacbd77857d339f1ad065ea84e28d8b4bfc2` | Identical bootloader across `.241` and `.242` |
| **`.241` (`AC8BA9C28A01`)** | `mtd1` (`u-boot-env`) | `65,536` | `0x00040000` | `63213a0bb3ec161faa51abf53417dcab7325b529c12150073923c6ab42cf711f` | Identical `u-boot-env` across `.241` and `.242` |
| **`.241` (`AC8BA9C28A01`)** | `mtd4` (`cfg`) | `262,144` | `0x00fa0000` | `060ad4d7256e1b562e1fc3ccd7b921dd72e86a2b66dad440faf9c9d874b0c263` | Persistent `airOS 8` config partition |
| **`.241` (`AC8BA9C28A01`)** | **`mtd5` (`EEPROM/ART`)** | **`65,536`** | **`0x00ff0000`** | **`d780aed0db673b3b72f71325b52c6c777aed9a607a9c9db89348ea0d2108846d`** | **`0x000c`: `e3d6 0777` \| `0x1000` (`wmac` `1088B`): `1bbc155f...` \| `0x5000` (`QCA9882` `2116B` `0x0844`): `a803e7c4...`** |
| **`.242` (`AC8BA9C28773`)** | `mtd0` (`u-boot`) | `262,144` | `0x00000000` | `b3d54d2c7eb154361dad22dbf880dacbd77857d339f1ad065ea84e28d8b4bfc2` | Identical bootloader across `.241` and `.242` |
| **`.242` (`AC8BA9C28773`)** | `mtd1` (`u-boot-env`) | `65,536` | `0x00040000` | `63213a0bb3ec161faa51abf53417dcab7325b529c12150073923c6ab42cf711f` | Identical `u-boot-env` across `.241` and `.242` |
| **`.242` (`AC8BA9C28773`)** | `mtd4` (`cfg`) | `262,144` | `0x00fa0000` | `472f31f334a4429a6652b80d28f3565f85a692f66de25792548a40f9a8986add` | Persistent `airOS 8` config partition |
| **`.242` (`AC8BA9C28773`)** | **`mtd5` (`EEPROM/ART`)** | **`65,536`** | **`0x00ff0000`** | **`f88bc3d756e078c4f04b3ee7e1700ea091a7288e8edcc217b4cd7dbda9de3754`** | **`0x000c`: `e3d6 0777` \| `0x1000` (`wmac` `1088B`): `a95510a5...` \| `0x5000` (`QCA9882` `2116B` `0x0844`): `eb5c41a2...`** |

---

## 3. Ground-Up Architecture Comparison: `PBE-5AC-Gen2` (`0xe3d6`) vs `LBE-5AC-Gen2` (`0xe7f9`)

Both `PBE-5AC-Gen2` (`ubnt_powerbeam-5ac-gen2`) and `LBE-5AC-Gen2` (`ubnt_litebeam-ac-gen2`) inherit from `target/linux/ath79/dts/ar9342_ubnt_wa.dtsi`:
- **Identical SoC, Memory, Radio Silicon & Datapath**:
  - **Host CPU**: `Atheros AR9342` rev 3 (`MIPS 74Kc V4.12`, `cpu 535 MHz / ddr 400 MHz / ahb 200 MHz`, `266.24 BogoMIPS`).
  - **RAM & Flash**: `64 MiB` DDR2 (`61,960 kB` usable), `16 MiB` SPI NOR (`ath-nor0`, `64 KB` eraseblock).
  - **Main 5 GHz Radio (`wifi0` / `phy0`)**: PCIe `0000:00:00.0` (`QCA9882`, PCI ID `0777:11ac` in airOS / `168c:003c` in OpenWrt, subsystem `0777:e3d6` vs `0777:e7f9`), Legacy PCI IRQ `64`, calibration data at `mtd5 + 0x5000` (`0x0844 = 2,116` bytes), max TX power `24 dBm` (`-4..24 dBm`).
  - **Management 2.4 GHz Radio (`wifi1` / `phy1`)**: Integrated `AR9342` AHB `wmac` (IRQ `2`), calibration data at `mtd5 + 0x1000` (`1,088` bytes), `1x1` 2.4 GHz (`max 19 dBm`).
  - **Spectral Scan GPIO Filter**: Both feature `IRQ 33: ATH GPIO ath-spectral-filter` in `/proc/interrupts`.
  - **Ethernet PHY (`eth0`)**: `Qualcomm Atheros AR8035` Gigabit RGMII PHY (IRQ `4`), supporting Linux `ag71xx` Byte Queue Limits (`BQL`) and `gro_flush_timeout`.
- **Exact Board-Level Differences (`0xe3d6` vs `0xe7f9`)**:
  1. **Board Magic & PCIe Subsystem ID**: `PBE-5AC-Gen2` uses `board.sysid = 0xe3d6` (`0x000c` in `mtd5` = `e3d6 0777`, `board.bom = 13-00492-15`, `FCC ID = SWX-PBE5ACG2`), whereas `LBE-5AC-Gen2` uses `board.sysid = 0xe7f9`. Flashing an `LBE-5AC-Gen2` factory image onto a `PBE-5AC-Gen2` via airOS `fwupdate.real` is rejected unless the `ubnt-fw` header matches `0xe3d6`.
  2. **RF Dish & Feed Architecture**: `PBE-5AC-Gen2` has dual built-in antenna profiles (`antenna.1 = 400mm Cassegrain dish, 25 dBi`, `antenna.2 = Feed only, 3 dBi`), providing `+2 dB` TX and `+2 dB` RX (`+4 dB` two-way link budget gain and tighter front-to-back sidelobe rejection) over `LBE-5AC-Gen2` (`23 dBi` stamped 3-panel reflector).
  3. **GPIO LEDs**: `PBE-5AC-Gen2` populates `feature.rssi.leds = 4` (4-segment RSSI alignment bar graph + LAN + Power LEDs), whereas `LBE-5AC-Gen2` has only 3 status LEDs (`Power`, `LAN`, `WLAN`).

---

## 4. Official OpenWrt `24.10.4` `ubnt_powerbeam-5ac-gen2` Images Staged & Validated

Downloaded into [`firmware/openwrt/`](../firmware/openwrt/) and verified against [`firmware/openwrt/sha256sums`](../firmware/openwrt/sha256sums) and `FlashMapValidator`:
- **Factory Image**: `openwrt-24.10.4-ath79-generic-ubnt_powerbeam-5ac-gen2-squashfs-factory.bin` (`6,881,944` bytes, SHA-256 `52d25c7f17ffc69dedc66895af090630e913945ac34fcb87288a4c381021f174`, `OPEN` header `WA.ar934x.v8.7.4-42.OpenWrt-r28959-29397011cc`, `0xe3d6` verified, fits safely inside `0x00050000..0x00f50000` [`15,728,640` B window]).
- **Sysupgrade Image**: `openwrt-24.10.4-ath79-generic-ubnt_powerbeam-5ac-gen2-squashfs-sysupgrade.bin` (`6,881,601` bytes, SHA-256 `c3e17ac02259db08708dfa8250e1b06d7765487923bdd435dc5d52998da301a4`).
- **Initramfs Kernel (RAM-Boot Recovery/Canary)**: `openwrt-24.10.4-ath79-generic-ubnt_powerbeam-5ac-gen2-initramfs-kernel.bin` (`6,523,102` bytes, SHA-256 `d50f3b6c5e2eec303a339acd12b4f1bd91d04d313188f7604001f4409b6bc747`).
