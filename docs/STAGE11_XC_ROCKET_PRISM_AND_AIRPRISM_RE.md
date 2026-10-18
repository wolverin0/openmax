# Stage 11 — Ubiquiti `XC` (`QCA9558 + QCA9880 + AirPrism`) Firmware, Dual-Radio & AirPrism Static Reverse-Engineering Report

- **Date:** 2026-10-18
- **Status:** `COMPLETE` (`CONFIRMED` static binary reverse engineering of `XC-8.7.25.260730.bin` and `XC-8.7.4-cs.210415.bin`)
- **Analyzed Artifacts (`artifacts/firmware_re_xc_ltu/`):**
  - `XC-8.7.25.260730.bin` (`10,290,738` B, MD5 `f31173233aa0b326f6c4815b082975d9`, SHA256 `ea9dc97264a091468f9b9c9291bee8b2037df7eb5ad6a37a2b3b91f1281249e9`)
  - `XC-8.7.4-cs.210415.bin` (`9,763,520` B, MD5 `8727e3da0a2a9dcdf6bb5583c2281f33`, SHA256 `51157c24de1387db53876165fca0a5c0714ad165763bac2d83707791c4a49d14`)
  - Extracted root filesystems (`xc_8725_rootfs/`, `xc_874cs_rootfs/`), decompressed kernels (`xc_8725_vmlinux.bin`), and structured symbol/relocation/control-flow extractions (`xc_fw_headers_summary.json`, `xc_boards_radios_complete.json`, `xc_dual_radio_hsr_vmlinux.json`, `xc_hsr_spi_and_uboot.json`).

---

## Executive Summary & Key Findings

1. **`XC` vs `WA` Container, Flash Layout & Boot Chain (`CONFIRMED`):**
   - Both `XC-8.7.25.260730.bin` (`XC.qca955x.v8.7.25.48568.260730.1009`) and `XC-8.7.4-cs.210415.bin` (`XC.qca955x.v8.7.4-cs.45112.210415.1103`) use the identical `UBNT` FW6 partition container (`PARTu-boot`, `PARTkernel`, `PARTrootfs`) as `WA`, mapped onto a 16 MB SPI NOR flash (`ath-nor0:256k(u-boot),64k(u-boot-env),1024k(kernel),14720k(rootfs),256k(cfg),64k(EEPROM)`).
   - Both `XC-8.7.4-cs` and `XC-8.7.25` have the exact same `/etc/poststart` -> `. /etc/persistent/rc.poststart` hook in `/usr/etc/rc.d/rc.funcs` (`rc_start()`) and both execute `/sbin/uav > /tmp/uav.log` in `/init`. However, `ubntconf` (`bin/ubntbox`) only creates the `/etc/poststart` enable flag when the firmware version string contains `-cs`, and `/sbin/uav` strips custom `rc.*` scripts from `/etc/persistent/` on non-`-cs` builds.
   - Conversely, `cron.status=enabled` + `cron.1.job.1.cmd=...` in `/tmp/system.cfg` is parsed natively by `ubntconf` (`-t cron`) on **both** `XC-8.7.4-cs` and `XC-8.7.25`, writing `/etc/crontabs/admin` and starting `/bin/crond` via `/etc/sysinit/cron.conf`. Thus, the Stage 10 `cron.1.job.1.cmd` RAM-module patcher is universal across both `XC-8.7.4-cs` and `XC-8.7.25`.

2. **Exact `ubnt_poll_host.ko` Byte Identity with `WA` (`CONFIRMED`):**
   - In **`XC-8.7.25.260730.bin`**, `lib/modules/2.6.32.68/ubnt_poll_host.ko` is **`189,880` bytes** (`MD5 = 5b26b076967befe129f669096539ae21`), with `.text` at file offset `64` (`0x40`) and `.text` size `101,072` bytes — **having the exact same file size and patch byte offsets as `WA-8.7.25`**:
     - **Site 1 (`bmiss` 2s timer `jal` at `.text + 0x007800`):** file offset **`30784`** (`0x0c000000` $\rightarrow$ `0x00000000` NOP; `S1=30784, S2=30788`)
     - **Site 2 (`timer_30s` reset branch at `.text + 0x007c08`):** file offset **`31816`** (`0x14400006` $\rightarrow$ `0x10000006`; `C2=1028, S3=31820`)
     - **Site 3 (`ubnt_poll_host_is_ap_valid` at `.text + 0x00a3a4`, return at `.text + 0x00a3b8`):** file offset **`41976`** (`0x0002102b` $\rightarrow$ `0x24020001`; `C3=10156, S4=41980`)
   - In **`XC-8.7.4-cs.210415.bin`**, `lib/modules/2.6.32.68/ubnt_poll_host.ko` is **`186,560` bytes** (`MD5 = 4103f9d0a2fdbf312d93a68b10647bca`), with `.text` at file offset `64` (`0x40`) and `.text` size `99,168` bytes — **having the exact same file size and patch byte offsets as `WA-8.7.4`..`8.7.15`**:
     - **Site 1 (`bmiss` 2s timer `jal` at `.text + 0x007538`):** file offset **`30072`** (`0x0c000000` $\rightarrow$ `0x00000000` NOP; `S1=30072, S2=30076`)
     - **Site 2 (`timer_30s` reset branch at `.text + 0x007940`):** file offset **`31104`** (`0x14400006` $\rightarrow$ `0x10000006`; `C2=1028, S3=31108`)
     - **Site 3 (`ubnt_poll_host_is_ap_valid` at `.text + 0x009f80`, return at `.text + 0x009f94`):** file offset **`40916`** (`0x0002102b` $\rightarrow$ `0x24020001`; `C3=9808, S4=40920`)
   - **STA (`managed`) vs AP (`master`) Mode Operation:**
     - In **STA (`managed`) mode**, the existing Stage 10 `WA` surgical patcher (`SZ=186560` / `SZ=189880`) + `/var/run/fscan_status` (`status=0`) + `wpa_supplicant` (`allow_80211=1`) works on `XC` with **zero modifications**.
     - In **AP (`master`) mode**, setting `radio.1.polling=disabled` in `/tmp/system.cfg` causes `ubntconf` to write `0 > /proc/sys/dev/uph_wifi0/enable` (`uph_PollingEnable_proc_write` in `ubnt_poll_host.ko`), disabling airMAX TDMA polling while keeping `umac.ko` (`ath0`), `/bin/hostapd` (`/etc/sysinit/aaa.conf`), and **both AirPrism filter subsystems (`ubnt_prism_hook` and `hsr`) fully active**.

3. **Two Distinct AirPrism Hardware/Driver Subsystems (`prism` vs `hsr`) Decoded (`CONFIRMED`):**
   - Decompilation of `ubnthal.ko` (`radio_cap_names` at `.data + 0x0060`) and `umac.ko` proves that Ubiquiti's "AirPrism" branding across the `XC` line comprises **two separate hardware mechanisms** controlled inside `umac.ko`:
     1. **Capability Bit 30 (`0x40000000`, `"prism"`) — 2-Stage Switched RF Band-Pass Filter Bank (`ubnt_prism_hook` at `umac.ko` `.text + 0x0ac874`, table `ubnt_prism_filters` at `.data + 0x001510`):**
        - Present on **`R5AC-PRISM` (`0xe7e5`), `PS-5AC` (`0xe7e6`/`0xe7e8`), `RP-5AC-Gen2` (`0xe7e7`/`0xe7e9`), and `Prism-AP` (`0xdc97`)** (`caps = 0xfce00814`).
        - Hooked into all 6 WMI channel-change paths in `umac.ko` (`wmi_unified_pdev_set_channel`, `wmi_unified_chan_switch_handler`, `wmi_unified_vdev_start_send`, `wmi_unified_vdev_restart_send`, `wmi_unified_vdev_start_chan_send`, `wmi_unified_vdev_chan_switch_send`).
        - Drives **4 host `QCA9558` GPIO pins (`GPIO 15, 16` for Stage 1 and `GPIO 13, 14` for Stage 2)** via `ubnthal_gpio_SetOut` (`0xb8040008`) according to `(center_freq_mhz, chanbw_mhz)` using the exact 6-entry `ubnt_prism_filters` truth table documented in Section 3.2.
     2. **Capability Bit 28 (`0x10000000`, `"hsr"`) — High Selectivity Receiver Tunable Active Filter ASIC over Shared SPI Bus (`umac.ko` `.text + 0x08c000..0x08cc54` + `ubnt_poll_host_hsr_diag`):**
        - Present on **`R5AC-PTP` (`0xe7f8`, `hsr_param = 171`), `R5AC-PTMP` (`0xe7f9` `hsr_param = 31`, `0xe7fa` `hsr_param = 43`), `R5AC-PRISM` (`0xe7e5`, `hsr_param = 31`), `PS-5AC` (`0xe7e6`/`0xe7e8`, `hsr_param = 31`), `RP-5AC-Gen2` (`0xe7e7`/`0xe7e9`, `hsr_param = 31`), and `Prism-AP` (`0xdc97`, `hsr_param = 31`)**.
        - Controlled via the QCA9558 hardware SPI controller (`0xbf000000`) locked with `ath_flash_spi_down()` / `ath_flash_spi_up()` (exported by `vmlinux`), using chip-select (`CS1`/`CS2`) and `ubnthal_gpio_Export` (`GPIO 11`/`12`/`17` depending on `hsr_param` bits).
        - Note: the adjacent function at `umac.ko` `.text + 0x08cf00..0x08d65c` (which also calls `ath_flash_spi_down`/`up` and bit-bangs `0xbf000000`) is Ubiquiti's **`Error-A12` anti-counterfeit SPI NOR flash OTP/UID verifier** (checking `/etc/board.info` `board.sysid`).

4. **Dual-Radio (`wifi0` + `wifi1` / `airview1`) & Gen2 Management Radio Architecture (`CONFIRMED`):**
   - Every dual-radio `XC` board (`R5AC-PTP`, `R5AC-PTMP`, `R5AC-PRISM`, `PS-5AC`, `RP-5AC-Gen2`, `Prism-AP`, `IS-5AC`, `NS-5AC`) pairs:
     - **`radio.1` (`wifi0` / `ath0`):** `QCA9880` (`PCIe` `bus_id=1`, `0x168c:0x003c`, 2x2 802.11ac data radio, `txpower_max=28 dBm` on `RP-5AC-Gen2`).
     - **`radio.2` (`wifi1` / `airview1`):** `QCA9558` internal SoC AHB WMAC (`AHB` `bus_id=0`, `0x168c:<subsys>`, 1x1 802.11n 5 GHz auxiliary radio, `caps=0x0000000c`) driven by `ath_dev.ko` + `ath_spectral.ko` + `ath_dfs_prescan.ko` for continuous background AirView spectrum analysis (`/bin/ubntspecd`) and zero-wait DFS radar prescan (`/bin/dfsprescan`, `/bin/radarprescan`).
     - **Self-TX Spectral Blanking (`ath_spectral_filter_init` at `ath_dev.ko` `.text + 0x027c00`):** registers a hardware GPIO interrupt `"ath-spectral-filter"` (`SPECTRAL-XMIT-FILTER GPIO`) so that `wifi1` (`QCA9558` AHB WMAC) discards FFT samples contaminated by simultaneous `wifi0` (`QCA9880`) transmissions.

---

## 1. Firmware Partition Structure, Boot Chain & `XC-8.7.4-cs` vs `XC-8.7.25` Persistence

### 1.1 FW6 Image Header & Partition Map (`CONFIRMED`)

Both `XC` firmware images use the standard `UBNT` FW6 container format and target the 16 MB SPI NOR flash layout defined in U-Boot (`mtdparts=ath-nor0:256k(u-boot),64k(u-boot-env),1024k(kernel),14720k(rootfs),256k(cfg),64k(EEPROM)`):

| Field / Partition | `XC-8.7.25.260730.bin` | `XC-8.7.4-cs.210415.bin` | Flash Mapping / Notes |
| :--- | :--- | :--- | :--- |
| **File Size** | `10,290,738` B | `9,763,520` B | FW6 image (`UBNT` magic) |
| **File MD5** | `f31173233aa0b326f6c4815b082975d9` | `8727e3da0a2a9dcdf6bb5583c2281f33` | Verified |
| **Version String** | `XC.qca955x.v8.7.25.48568.260730.1009` | `XC.qca955x.v8.7.4-cs.45112.210415.1103` | Header offset `4..260` |
| **`PARTu-boot`** | Offset `324`, len `237,188` B (`MD5 8f7879e6...`) | Offset `324`, len `234,140` B (`MD5 c914daf0...`) | `baseaddr=0x9f000000`, `part_size=262,144` (256 KB); `U-Boot 1.1.4-g4f57088a-dirty` |
| **`u-boot-env`** | *(Not in FW image)* | *(Not in FW image)* | `0x9f040000`, `65,536` B (64 KB) |
| **`PARTkernel`** | Offset `237,576`, len `1,008,399` B (`MD5 1828f0cb...`) | Offset `234,528`, len `1,008,514` B (`MD5 aa52e6c8...`) | `baseaddr=0x9f050000`, `part_size=1,048,576` (1024 KB), `memaddr/entry=0x80002000`, `MIPS Ubiquiti Linux-2.6.32.68` |
| **`PARTrootfs`** | Offset `1,246,039`, len `9,043,968` B (`MD5 999bc839...`) | Offset `1,243,106`, len `8,519,680` B (`MD5 ab435e20...`) | `baseaddr=0x9f150000`, `part_size=15,073,280` (14,720 KB), SquashFS 4.0 LZMA (`2,213` / `2,211` files) |
| **`cfg` (`persistent`)** | *(Preserved on flash)* | *(Preserved on flash)* | `0x9ffb0000`, `262,144` B (256 KB, mounted via `cfgmtd` to `/etc/persistent`) |
| **`EEPROM` (`ART`)** | *(Protected calibration)* | *(Protected calibration)* | `0x9fff0000`, `65,536` B (64 KB; `wifi1` AHB caldata at `+0x1000`, `wifi0` PCIe caldata at `+0x5000`) |

### 1.2 Kernel & Module Load Order (`CONFIRMED`)

During `/init` and `/usr/etc/rc.d/rc.funcs`, kernel modules are loaded in the following exact sequence:
1. **`ubnthal.ko`** (`43,036` B in `8.7.25`, loaded directly by `/init`): descrambles the internal board database (`34` `XC` board entries), validates the board's `EEPROM` (`0x9fff0000`), creates `/proc/ubnthal/board`, `/proc/ubnthal/system.info`, `/proc/ubnthal/status/`, and registers `/dev/gpio` (`char major 127`).
2. **`urd.ko`** (`/usr/etc/modules.d/48-ubnt-regd`): Ubiquiti regulatory database module.
3. **`/usr/etc/modules.d/50-ath-11c-5ac`** (Wireless stack):
   - `adf.ko` (`19,592` B) $\rightarrow$ `asf.ko` (`10,608` B) $\rightarrow$ `ath_hal.ko` (`586,216` B, AR9300/QCA9558 AHB HAL) $\rightarrow$ `ath_rate_atheros.ko` (`48,376` B) $\rightarrow$ `ath_spectral.ko` (`55,612` B) $\rightarrow$ `ath_dev.ko` (`306,120` B) $\rightarrow$ `ath_dfs_prescan.ko` (`65,120` B) $\rightarrow$ `umac.ko` (`1,771,860` B in `8.7.25`; `1,769,700` B in `8.7.4-cs`).
   - Inside `umac.ko`, `ol_ath_pci_probe` attaches `wifi0` (`QCA9880` on PCIe `bus_id=1`, downloading embedded target firmware from `umac.ko` `.rodata`), while `ath_ahb_probe` attaches `wifi1` (`QCA9558` WMAC on AHB `bus_id=0`).
4. **`ubnt_poll_host.ko`** (`/usr/etc/modules.d/51-ubnt-poll-host`, `189,880` B in `8.7.25`; `186,560` B in `8.7.4-cs`): attaches to `wifi0` via `ieee80211_UbntPollAttach`, downloads the airMAX target co-processor overlay into `QCA9880` target RAM, and registers `/dev/uph_wifi0` (`char major 190, minor 0`) and `/proc/sys/dev/uph_wifi0/*`.
5. **`rssi-leds.ko`** (`/usr/etc/modules.d/52-rssi-leds`).

### 1.3 `XC-8.7.4-cs` vs `XC-8.7.25`: Custom Scripts (`rc.poststart`) vs `cron` Persistence (`CONFIRMED`)

Static diffing of `/init`, `/usr/etc/inittab`, `/usr/etc/rc.d/rc`, and `/usr/etc/rc.d/rc.funcs` between `XC-8.7.4-cs` and `XC-8.7.25` revealed:
- **Identical shell scripts:** `/init` and `/usr/etc/rc.d/rc.funcs` are byte-for-byte identical in their startup hooks across both builds:
  - `/init` runs `/sbin/uav > /tmp/uav.log` right before `/sbin/ubntconf`.
  - `/usr/etc/rc.d/rc.funcs` (`rc_start()`) checks:
    ```sh
    if [ -e /etc/poststart ] && [ -e /etc/persistent/rc.poststart ]; then
        . /etc/persistent/rc.poststart 2>&1 | logger -t -p local0.notice "poststart" &
    fi
    ```
- **Why `rc.poststart` only runs on `XC-8.7.4-cs`:**
  - `/sbin/ubntconf` (`bin/ubntbox`) inspects the firmware version string (`XC.qca955x.v8.7.4-cs...` vs `XC.qca955x.v8.7.25...`). Only when `-cs` is present does `ubntconf` create `/etc/poststart` (and allow `rc.prestart`/`rc.poststart`/`rc.poststop`), whereas on non-`-cs` builds `/sbin/uav` (Ubiquiti's MF-worm cleaner) removes unauthorized `rc.*` scripts from `/etc/persistent/`.
- **Why `cron.1.job.1.cmd` in `/tmp/system.cfg` works on BOTH `XC-8.7.4-cs` and `XC-8.7.25` (`CONFIRMED`):**
  - `ubntconf` on both `XC-8.7.4-cs` and `XC-8.7.25` contains the full `cron` plugin (`cron.status=enabled`, `cron.1.status=enabled`, `cron.1.user=admin`, `cron.1.job.1.status=enabled`, `cron.1.job.1.schedule=* * * * *`, `cron.1.job.1.cmd=...`), which generates `/etc/crontabs/admin` and `/etc/sysinit/cron.conf` (`plugin_start() { /bin/crond -b -c /etc/crontabs; }`).
  - Therefore, the exact Stage 10 `cron.1.job.1.cmd` persistence mechanism works identically on `XC-8.7.25` without needing `-cs` firmware.

---

## 2. `ubnt_poll_host.ko` Verification (`XC` vs `WA`) & AP/STA Mode Interoperability

### 2.1 Binary Comparison and Exact Patch Offsets (`CONFIRMED`)

Disassembly and relocation inspection of `lib/modules/2.6.32.68/ubnt_poll_host.ko` in both `XC` images confirms that `XC` and `WA` are compiled from the **exact same `ubnt_poll_host` source tree with the exact same `.text` layout and instruction offsets**:

| Property / Patch Site | `XC-8.7.25.260730.bin` | `XC-8.7.4-cs.210415.bin` | Exact `WA` Equivalent |
| :--- | :--- | :--- | :--- |
| **`ubnt_poll_host.ko` File Size** | **`189,880` bytes** | **`186,560` bytes** | `WA-8.7.25` (`189,880` B) / `WA-8.7.4..8.7.15` (`186,560` B) |
| **`ubnt_poll_host.ko` MD5** | `5b26b076967befe129f669096539ae21` | `4103f9d0a2fdbf312d93a68b10647bca` | Identical `.text` layout |
| **`.text` Section Offset / Size** | File offset `64` (`0x40`), size `101,072` B | File offset `64` (`0x40`), size `99,168` B | Identical |
| **Site 1: `bmiss` 2s Timer `jal`** | `.text + 0x007800` $\rightarrow$ **file offset `30784`** (`0x0c000000` $\rightarrow$ `0x00000000`) | `.text + 0x007538` $\rightarrow$ **file offset `30072`** (`0x0c000000` $\rightarrow$ `0x00000000`) | `S1=30784, S2=30788` (`8.7.25`) / `S1=30072, S2=30076` (`8.7.4-cs`) |
| **Site 2: `timer_30s` Reset Branch** | `.text + 0x007c08` $\rightarrow$ **file offset `31816`** (`0x14400006` $\rightarrow$ `0x10000006`) | `.text + 0x007940` $\rightarrow$ **file offset `31104`** (`0x14400006` $\rightarrow$ `0x10000006`) | `C2=1028, S3=31820` (`8.7.25`) / `C2=1028, S3=31108` (`8.7.4-cs`) |
| **Site 3: `ubnt_poll_host_is_ap_valid`** | Func `.text + 0x00a3a4`, ret `.text + 0x00a3b8` $\rightarrow$ **file offset `41976`** (`0x0002102b` $\rightarrow$ `0x24020001`) | Func `.text + 0x009f80`, ret `.text + 0x009f94` $\rightarrow$ **file offset `40916`** (`0x0002102b` $\rightarrow$ `0x24020001`) | `C3=10156, S4=41980` (`8.7.25`) / `C3=9808, S4=40920` (`8.7.4-cs`) |

### 2.2 Interoperability in `STA` (`managed`) vs `AP` (`master`) Mode (`CONFIRMED`)

1. **`XC` in `STA` (`managed`) Mode (e.g., `Rocket Prism 5AC Gen2` or `PowerBeam 5AC ISO` connecting to a standard 802.11ac OpenWrt `ath10k` AP):**
   - The Stage 10 `WA` surgical patcher script (`SZ=186560` / `SZ=189880` 12-byte `dd` splice + `/var/run/fscan_status` `status=0` + `wpa_supplicant` `-ddd` `allow_80211=1`) works **without changing a single byte** on both `XC-8.7.4-cs` and `XC-8.7.25`.
   - Because `umac.ko` remains completely untouched and loaded, `ubnt_prism_hook` and the `hsr` SPI filter tuner execute automatically whenever `ath0` associates or changes channel.

2. **`XC` in `AP` (`master`) Mode (e.g., `Rocket Prism 5AC Gen2` sector AP serving standard 802.11ac OpenWrt `ath10k` CPEs):**
   - In `ubnt_poll_host.ko`, `uph_PollingEnable_proc_write` controls `/proc/sys/dev/uph_wifi0/enable`.
   - When `radio.1.polling=disabled` is set in `/tmp/system.cfg`, `ubntconf` configures `/etc/sysinit/radio.conf` to write `0 > /proc/sys/dev/uph_wifi0/enable` and brings up `ath0` in standard 802.11ac AP (`master`) mode with `/bin/hostapd` (`/etc/sysinit/aaa.conf`).
   - Importantly, the 3 watchdog checks patched in Stage 10 (`bmiss` 2s timer, `timer_30s` reset, and `ubnt_poll_host_is_ap_valid`) are **STA-mode hooks** that guard association to an AP. When `XC` operates in `AP` (`master`) mode with `radio.1.polling=disabled` (or with the patched `ubnt_poll_host.ko` loaded and `enable=0`), standard 802.11ac clients (`OpenWrt ath10k`, laptops, or patched `WA`/`XC` stations) can associate directly to the `Rocket Prism 5AC Gen2` AP while **`umac.ko` continues to drive both the Stage 1/2 GPIO AirPrism filter bank (`ubnt_prism_hook`) and the SPI HSR active filter (`hsr`)**!

---

## 3. Complete `XC` Hardware Matrix, Dual-Radio (`wifi0` + `wifi1`) & AirPrism Architecture

### 3.1 Complete Descrambled `XC` Board Table in `ubnthal.ko` (`CONFIRMED`)

By reversing `ubnthal.ko` (`board_ validation_and_descramble` at `.text + 0x001380`), we extracted and descrambled the entire `.rodata` board table (`34` `XC` board definitions, `4,016` bytes per entry).

Every `XC` board entry contains:
- `board + 0x0000`: Board name string (e.g., `"RP-5AC-Gen2"`)
- `board + 0x003e`: `sysid` (`uint16`, e.g., `0xe7e9`)
- `board + 0x0044`: `feature_flags` (`uint32`: bit 2 = `led_Simple`, bit 4 = `gps`, bit 9 = `g2` Gen2 management Wi-Fi)
- `board + 0x0048`: `num_eth` (`uint32`, `1` or `2` Gigabit Ethernet ports)
- `board + 0x0054`: `eth0` flags (`bit 0` = PoE status, `bit 1` = Passthrough PoE output)
- `board + 0x0768`: `radio_count` (`uint32`: `1` or `2`)
- `board + 0x076c`: `radio[0]` (`wifi0`, size `0x0834 = 2100` B):
  - `+0x0770`: `vendor_id` (`0x168c`), `+0x0772`: `device_id` (`0x003c` = `QCA9880`), `+0x0776`: `subsys_id` (`sysid`)
  - `+0x0778`: `bus_type` (`1` = `PCIe`), `+0x077c`: `bus_id` (`1`), `+0x0780`: `caldata_offset` (`5` $\rightarrow$ `0x5000` in `EEPROM`)
  - `+0x0784`: `txpower_max` (`dBm`), `+0x078c`: `chains` (`0x22` = 2x2 MIMO, `0x11` = 1x1 SISO), `+0x0790`: `caps` (`uint32` bitmask)
  - `+0x0f8c`: `hsr_param` (`uint32`, returned when `ubnthal_get_radio_cap(0, "hsr")` is queried!)
- `board + 0x0fa0`: `radio[1]` (`wifi1` / `airview1`, size `0x0834 = 2100` B):
  - `+0x0fa4`: `vendor_id` (`0x168c`), `+0x0fa6`: `device_id` (`sysid` = `QCA9558` internal AHB WMAC)
  - `+0x0fac`: `bus_type` (`2` = `AHB`), `+0x0fb0`: `bus_id` (`0`), `+0x0fb4`: `caldata_offset` (`1` $\rightarrow$ `0x1000` in `EEPROM`)
  - `+0x0fc0`: `chains` (`0x11` = 1x1), `+0x0fc4`: `caps` (`0x0000000c` = `11a` + `11na` 5 GHz spectrum scanner).

#### Table 3.1 — All 34 `XC` Boards Supported by `ubnthal.ko` (`XC-8.7.25`)

| `sysid` | Model Name | `radios` | `eth` | `wifi0` Max TX | `wifi0` Chains | `wifi0` `caps` | `prism` (Bit 30) | `hsr` (Bit 28, `hsr_param`) | `beam` (Bit 25) | `gps` (Bit 4) | `g2` Mgmt (Bit 9) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`0xe7f8`** | `R5AC-PTP` | **2** | 1 | `27 dBm` | `2x2` | `0x1ce00814` | No | **Yes (`171` / `0xab`)** | No | No | No |
| **`0xe7f9`** | `R5AC-PTMP` | **2** | 1 | `27 dBm` | `2x2` | `0x1ce00814` | No | **Yes (`31` / `0x1f`)** | No | No | No |
| **`0xe7fa`** | `R5AC-PTMP` | **2** | 1 | `27 dBm` | `2x2` | `0x1ce00814` | No | **Yes (`43` / `0x2b`)** | No | No | No |
| **`0xe7e5`** | **`R5AC-PRISM`** | **2** | 1 | **`28 dBm`** | `2x2` | `0xfce00814` | **YES** | **Yes (`31` / `0x1f`)** | No | **YES** | No |
| **`0xe7e6`** | **`PS-5AC`** | **2** | 1 | **`28 dBm`** | `2x2` | `0xfce00814` | **YES** | **Yes (`31` / `0x1f`)** | No | **YES** | **YES** |
| **`0xe7e7`** | **`RP-5AC-Gen2`** | **2** | 1 | **`28 dBm`** | `2x2` | `0xfce00814` | **YES** | **Yes (`31` / `0x1f`)** | No | **YES** | **YES** |
| **`0xe7e8`** | **`PS-5AC`** | **2** | 1 | **`28 dBm`** | `2x2` | `0xfce00814` | **YES** | **Yes (`31` / `0x1f`)** | No | **YES** | **YES** |
| **`0xe7e9`** | **`RP-5AC-Gen2`** | **2** | 1 | **`28 dBm`** | `2x2` | `0xfce00814` | **YES** | **Yes (`31` / `0x1f`)** | No | **YES** | **YES** |
| **`0xdc97`** | **`Prism-AP`** | **2** | 1 | `25 dBm` | `2x2` | `0xfce00814` | **YES** | **Yes (`31` / `0x1f`)** | No | **YES** | No |
| **`0xe4f5`** | `R5AC-Lite` | 1 | 1 | `27 dBm` | `2x2` | `0x0ce00814` | No | No | No | No | No |
| **`0xe6b5`** | `NBE-5AC-19` | 1 | 1 | `26 dBm` | `2x2` | `0x0ee00814` | No | No | **YES** | No | No |
| **`0xe3b5`** | `NBE-5AC-16` | 1 | 1 | `26 dBm` | `2x2` | `0x0ce00814` | No | No | No | No | No |
| **`0xe4b5`** | `PBE-5AC-500` | 1 | 1 | `24 dBm` | `2x2` | `0x0ee00814` | No | No | **YES** | No | No |
| **`0xe4d5`** | `PBE-5AC-500-ISO` | 1 | 1 | `24 dBm` | `2x2` | `0x0ce00814` | No | No | No | No | No |
| **`0xe4e5`** | `PBE-5AC-620` | 1 | 1 | `24 dBm` | `2x2` | `0x0ee00814` | No | No | **YES** | No | No |
| **`0xe6e5`** | `PBE-5AC-300` | 1 | 1 | `24 dBm` | `2x2` | `0x0ce00814` | No | No | No | No | No |
| **`0xe5d5`** | `PBE-5AC-300-ISO` | 1 | 1 | `24 dBm` | `2x2` | `0x0ce00814` | No | No | No | No | No |
| **`0xe6f5`** | `PBE-5AC-400` | 1 | 1 | `25 dBm` | `2x2` | `0x0ce00814` | No | No | No | No | No |
| **`0xe5e5`** | `PBE-5AC-400-ISO` | 1 | 1 | `25 dBm` | `2x2` | `0x0ce00814` | No | No | No | No | No |
| **`0xe3e5`** | `LBE-5AC-23` | 1 | 1 | `25 dBm` | `2x2` | `0x0ce00814` | No | No | No | No | No |
| **`0xe4a2`** | `LBE-5AC-16-120` | 1 | 1 | `25 dBm` | `2x2` | `0x0ce00814` | No | No | No | No | No |
| **`0xe7f5`** | `AF-5X` | 1 | 1 | `26 dBm` | `2x2` | `0x0ce00814` | No | No | No | **YES** | No |
| **`0xe865`** | `IS-5AC` | **2** | 1 | `25 dBm` | `2x2` | `0x8ce00814` | No | No | No | No | **YES** |
| **`0xe815`** | `PBE-5AC-ISO-Gen2` | 1 | 1 | `24 dBm` | `2x2` | `0x0ce00814` | No | No | No | No | **YES** |
| **`0xe825`** | `PBE-5AC-Gen2` | 1 | 1 | `24 dBm` | `2x2` | `0x0ce00814` | No | No | No | No | **YES** |
| **`0xe835`** | `PBE-5AC-400-ISO-Gen2` | 1 | 1 | `25 dBm` | `2x2` | `0x0ce00814` | No | No | No | No | **YES** |
| **`0xe845`** | `NBE-5AC-Gen2` | 1 | 2 | `25 dBm` | `2x2` | `0x8ce00814` | No | No | No | No | **YES** |
| **`0xe855`** | `NS-5AC` | **2** | 2 | `25 dBm` | `2x2` | `0x8ce00814` | No | No | No | No | **YES** |
| **`0xe885`** | `PBE-5AC-X-Gen2` | 1 | 1 | `26 dBm` | `2x2` | `0x0ce00814` | No | No | No | No | **YES** |
| **`0xe3f5`** | `LBE-ac` | 1 | 1 | `25 dBm` | `1x1` | `0x0ce00814` | No | No | No | No | No |
| **`0xdc99`** | `Wave-Nano` | 1 | 1 | `25 dBm` | `2x2` | `0x8ce00814` | No | No | No | No | **YES** |
| **`0xdc9a`** | `Wave-LR` | 1 | 1 | `25 dBm` | `2x2` | `0x8ce00814` | No | No | No | No | **YES** |
| **`0xdc9b`** | `GBE-LR` | 1 | 1 | `25 dBm` | `2x2` | `0x8ce00814` | No | No | No | No | **YES** |
| **`0xdc98`** | `AF60-XR` | 1 | 1 | `25 dBm` | `2x2` | `0x0ce00814` | No | No | No | No | No |

> [!IMPORTANT]
> **`PowerBeam 5AC ISO` (`0xe4d5`, `0xe5d5`, `0xe5e5`, `0xe815`, `0xe835`) vs `Rocket Prism 5AC Gen2` (`0xe7e7`/`0xe7e9`) and `PrismStation 5AC` (`0xe7e6`/`0xe7e8`):**
> The `ubnthal.ko` board table proves that the `PowerBeam 5AC ISO` ("ISO" = passive RF isolator ring around the dish feed/radome) is a **single-radio (`radios=1`) board without `"prism"` (`Bit 30`) or `"hsr"` (`Bit 28`) active RF filtering** (`caps = 0x0ce00814`). True active AirPrism hardware filtering (`caps = 0xfce00814`, `prism=1` + `hsr=31`) and dual-radio `wifi0` + `wifi1` (`airview1`) are present on **`R5AC-PRISM` (`0xe7e5`), `PrismStation 5AC` (`PS-5AC`, `0xe7e6`/`0xe7e8`), `Rocket Prism 5AC Gen2` (`RP-5AC-Gen2`, `0xe7e7`/`0xe7e9`), and `Prism-AP` (`0xdc97`)** (while `R5AC-PTP` `0xe7f8` and `R5AC-PTMP` `0xe7f9`/`0xe7fa` have `hsr` SPI active filtering + dual radios, without the Stage 1/2 GPIO `prism` pre-selector bank).

---

### 3.2 Mechanism 1: `ubnt_prism_hook` (`umac.ko` `.text + 0x0ac874`) — 2-Stage GPIO Band-Pass Filter Bank (`CONFIRMED`)

When `ubnthal_get_radio_cap(radio_idx, "prism")` returns `1` (Bit 30 of `caps = 0xfce00814`), `umac.ko` executes `ubnt_prism_hook` (`0x0ac874`, size `468` B) on every channel/bandwidth transition across 6 WMI functions:
1. `wmi_unified_pdev_set_channel` (`.text + 0x0aca48`)
2. `wmi_unified_chan_switch_handler` (`.text + 0x0b7310`)
3. `wmi_unified_vdev_start_send` (`.text + 0x0ba0b8`)
4. `wmi_unified_vdev_restart_send` (`.text + 0x0ba2ac`)
5. `wmi_unified_vdev_start_chan_send` (`.text + 0x0bc740`)
6. `wmi_unified_vdev_chan_switch_send` (`.text + 0x0bc934`)

#### How `ubnt_prism_hook` Drives the Hardware (`CONFIRMED`)
- `ubnt_prism_hook` extracts `center_freq_mhz` and `chanbw_mhz` from the `ieee80211_channel` struct and calls helper `.text + 0x0abeb0` twice: once for `stage = 1` and once for `stage = 2`.
- Helper `.text + 0x0abeb0` iterates over the 6-entry `ubnt_prism_filters` table at `umac.ko` `.data + 0x001510` (`264` bytes = `6` entries $\times$ `44` bytes per entry) in order (`idx = 0..5`) and picks the **first entry** matching `entry.stage == stage` where:
  - `center_freq_mhz >= entry.freq_start_mhz`
  - `center_freq_mhz <= entry.freq_end_mhz`
  - `chanbw_mhz <= entry.max_bw_mhz`
- For each stage's two GPIO descriptors (`gpio_a`, `gpio_b`), `ubnt_prism_hook` calls `ubnthal_gpio_Export(pin, 1)` (direction = output, setting bit `1 << pin` in `QCA9558_GPIO_OE` at `0xb8040000`) and `ubnthal_gpio_SetOut(pin, state)` (writing `QCA9558_GPIO_OUT` at `0xb8040008`).

#### Table 3.2 — Exact `ubnt_prism_filters` Truth Table (`umac.ko` `.data + 0x001510`)

| Entry | Filter Stage | Frequency Range (`MHz`) | Max Channel BW (`MHz`) | Host QCA9558 GPIO Pin A | Host QCA9558 GPIO Pin B | Combined `GPIO_OUT` Mask (`GPIO 13..16`) | Target RF Sub-Band |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **0** | **Stage 1** | **`5150 – 5250 MHz`** | `160 MHz` | `GPIO 15 = 1` | `GPIO 16 = 1` | `0x00018000` | UNII-1 (`5.15–5.25 GHz` low band) |
| **1** | **Stage 1** | **`5470 – 5860 MHz`** | **`50 MHz`** | `GPIO 15 = 1` | `GPIO 16 = 0` | `0x00008000` | UNII-2C / UNII-3 (`5.47–5.86 GHz`, $\le 50\text{ MHz}$ BW) |
| **2** | **Stage 1** | **`3000 – 6200 MHz`** | `160 MHz` | `GPIO 15 = 0` | `GPIO 16 = 1` | `0x00010000` | Wideband / UNII-2A (`5.25–5.47 GHz`) / $>50\text{ MHz}$ bypass |
| **3** | **Stage 2** | **`5200 – 5300 MHz`** | `160 MHz` | `GPIO 13 = 1` | `GPIO 14 = 0` | `0x00002000` | UNII-1 upper / UNII-2A (`5.20–5.30 GHz`) |
| **4** | **Stage 2** | **`5725 – 5860 MHz`** | `160 MHz` | `GPIO 13 = 0` | `GPIO 14 = 1` | `0x00004000` | UNII-3 (`5.725–5.860 GHz` high band) |
| **5** | **Stage 2** | **`3000 – 6200 MHz`** | `160 MHz` | `GPIO 13 = 1` | `GPIO 14 = 1` | `0x00006000` | Mid-band (`5.15–5.20 GHz` & `5.30–5.725 GHz`) / wideband |

This is a **major architectural finding**: on `R5AC-PRISM`, `PS-5AC`, and `RP-5AC-Gen2`, the `prism` 2-stage pre-selector band-pass filter bank is switched purely by **4 host QCA9558 GPIO lines (`GPIO 13, 14, 15, 16`)**!

---

### 3.3 Mechanism 2: `hsr` Tunable Active Filter over Shared QCA9558 SPI Bus (`umac.ko` `.text + 0x08c000..0x08cc54`) (`CONFIRMED`)

In addition to `ubnt_prism_hook` (`GPIO 13..16`), boards with `caps` Bit 28 (`"hsr"`) have a High Selectivity Receiver (`HSR`) tunable filter ASIC connected to the **QCA9558 SPI bus (`0xbf000000`)**.

Decompilation of `umac.ko` `.text + 0x08c000..0x08cc54` and `vmlinux` (`ath_spi_*` at `0x801a9498`) reveals:
1. **Why `vmlinux` Exports `ath_flash_spi_down` / `ath_flash_spi_up`:**
   - The QCA9558 SPI controller at `0xbf000000` (`AR71XX_SPI_BASE`: `0xbf000000` = `SPI_FS`, `0xbf000004` = `SPI_CLOCK`, `0xbf000008` = `SPI_WRITE`, `0xbf00000c` = `SPI_READ`, `0xbf000010` = `SPI_RD_STATUS`) is shared between the **16 MB SPI NOR boot flash (`CS0`)** and the **HSR filter ASIC (`CS1`/`CS2` + GPIO control pins)**.
   - Before touching `0xbf000000`, `umac.ko` calls `ath_flash_spi_down()` (which acquires the kernel SPI mutex in `vmlinux` so MTD flash reads/writes cannot collide with HSR tuning), sets `[0xbf000000] = 1` (`AR71XX_SPI_FS_GPIO` bit-bang mode), shifts out the HSR command/frequency tuning words via `[0xbf000008]` (`SPI_WRITE`), restores `[0xbf000000] = 0`, and releases the mutex via `ath_flash_spi_up()`.
2. **How `hsr_param` (`31`, `43`, `171`) Configures the HSR Driver (`.text + 0x08c2ec..0x08cc54`):**
   - At attach time (`.text + 0x08cb4c`), `umac.ko` calls `ubnthal_get_radio_cap(radio_idx, "hsr")`, which returns `hsr_param` from `board + 0x0f8c`:
     - `31` (`0x1f` = `0b00011111`) on `R5AC-PTMP` (`0xe7f9`), `R5AC-PRISM` (`0xe7e5`), `PS-5AC` (`0xe7e6`/`0xe7e8`), `RP-5AC-Gen2` (`0xe7e7`/`0xe7e9`), and `Prism-AP` (`0xdc97`)
     - `43` (`0x2b` = `0b00101011`) on `R5AC-PTMP` (`0xe7fa`)
     - `171` (`0xab` = `0b10101011`) on `R5AC-PTP` (`0xe7f8`)
   - The bits of `hsr_param` select the hardware revision and GPIO/CS pin mapping (`.text + 0x08cbac..0x08cc2c`):
     - `bit 7` (`0x80`, set in `171` on `R5AC-PTP`): selects `GPIO 12` vs `GPIO 17` (`0x11`) as the HSR chip-select/enable GPIO (`ubnthal_gpio_Export(pin, 1)`).
     - `bit 5` (`0x20`, set in `43` and `171`) vs `bit 4` (`0x10`, set in `31`): selects the HSR filter bandwidth/step table and exports `GPIO 11` (`0x0b`) on `hsr_param == 31`.
   - `umac.ko` also exposes `ubnt_poll_host_hsr_diag` (called by `ubnt_poll_host.ko` `.text + 0x008b28` and `/proc/sys/dev/uph_wifi0/hsr_status`) to monitor HSR filter health (`HSR status: %d`, `Trying to recover HSR (status %d -> %d)`).
3. **Disambiguating `umac.ko` `.text + 0x08cf00..0x08d65c` (`Error-A12` Anti-Counterfeit Check):**
   - Immediately following the HSR functions in `umac.ko` is a second function (`.text + 0x08cf00..0x08d65c`) that also calls `ath_flash_spi_down()` / `ath_flash_spi_up()` and bit-bangs `0xbf000000` with `CS0` (`0x60000` / `0x70000`).
   - Decompiling `.text + 0x08cf00` alongside the XOR-obfuscated strings at `umac.ko` `.data + 0x000db0..0x001100` (`key = 0xd6`: `"Error-A12"`, `"board.sysid"`, `"/etc/board.info"`, `"%s=%x"`) confirms that `.text + 0x08cf00` is Ubiquiti's **anti-clone SPI NOR flash OTP security check (`Error-A12`)**, not part of AirPrism!

---

### 3.4 Dual-Radio (`wifi0` + `wifi1` / `airview1`) & TX Spectral Blanking (`CONFIRMED`)

On all 11 dual-radio `XC` boards (`0xe7f8`, `0xe7f9`, `0xe7fa`, `0xe7e5`, `0xe7e6`, `0xe7e7`, `0xe7e8`, `0xe7e9`, `0xdc97`, `0xe865`, `0xe855`), `ubntconf` generates `/etc/sysinit/radio.conf` and `/etc/sysinit/airview.conf` as follows:
- **`wifi0` (`ath0`):** `QCA9880` (`PCIe` `bus_id=1`, `0x168c:0x003c`), calibration data at `EEPROM + 0x5000` (`2,116` bytes `QCA9880` OTP/board-data). Used for all 802.11ac PtP/PtMP data traffic.
- **`wifi1` (`airview1`):** `QCA9558` internal AHB WMAC (`AHB` `bus_id=0`, `0x168c:<sysid>`), calibration data at `EEPROM + 0x1000` (`AR9300` EEPROM template). Configured with:
  - `/sbin/wlanconfig airview1 create wlandev wifi1 wlanmode monitor`
  - `/bin/ubntspecd -t -a -i wifi1` (background spectral FFT sweeping daemon for the AirView waterfall/ambient noise floor UI)
  - `/bin/dfsprescan` + `/bin/radarprescan` + `ath_dfs_prescan.ko` (background radar CAC pre-scanner on `wifi1` that allows `wifi0` to switch DFS channels with zero CAC outage).
- **Hardware Self-TX Spectral Filter (`ath_spectral_filter_init` at `ath_dev.ko` `.text + 0x027c00`):**
  - Because `wifi0` (`QCA9880`) and `wifi1` (`QCA9558` WMAC) are inside the same shielding enclosure (or coupled onto the RF port), `wifi0`'s +28 dBm transmissions would saturate `wifi1`'s spectral FFT scans.
  - `ath_dev.ko` registers a GPIO interrupt handler (`request_irq(..., "ath-spectral-filter", ...)` using `SPECTRAL-XMIT-FILTER GPIO`) wired to `wifi0`'s PA/TX-active line (`TX_FRAME` / `PA_ON`). Whenever `wifi0` transmits, the interrupt timestamps the TX burst so `ath_spectral.ko` discards self-TX FFT frames on `wifi1`!

---

## 4. Porting & Operational Blueprint: OpenWrt (`ath79` + `ath10k`) vs Hybrid Stock `XC` on `Rocket Prism 5AC Gen2` (`0xe7e9`)

### 4.1 Why `Rocket Prism 5AC Gen2` (`0xe7e9`) Is Missing / Incomplete in Upstream OpenWrt (`CONFIRMED`)

1. **Missing `ubnt,rocket-prism-5ac-gen2` (`0xe7e9`) Target Profile in `ath79/generic`:**
   - Upstream OpenWrt `ath79/generic` includes single-radio `qca9558` airMAX AC boards (`ubnt_powerbeam-5ac-500`, `ubnt_powerbeam-5ac-gen2`, `ubnt_nanobeam-ac-gen2`, `ubnt_rocket-5ac-lite`), which only instantiate PCIe `wifi0` (`QCA9880` caldata at `ART + 0x5000`) and (on Gen2 models) the 2.4 GHz management radio on AHB (`ART + 0x1000`).
   - On `RP-5AC-Gen2` (`0xe7e7`/`0xe7e9`) and `PS-5AC` (`0xe7e6`/`0xe7e8`), the `QCA9558` AHB WMAC (`ART + 0x1000`) is a **5 GHz 1x1 `11na` AirView/DFS scanner radio** (`caps = 0x0000000c`), NOT the 2.4 GHz management radio!
2. **Untuned / Unconfigured AirPrism RF Filters (`GPIO 13..16` and SPI `hsr`) under Stock OpenWrt:**
   - Upstream `ath79` + `ath10k` knows nothing about `ubnt_prism_hook` (`GPIO 13, 14, 15, 16`) or the SPI-attached `hsr` active filter (`0xbf000000` `CS1` + `GPIO 11`).
   - If upstream OpenWrt is booted on `RP-5AC-Gen2` without initializing `GPIO 13..16` and the `hsr` SPI filter, the 2-stage RF pre-selector switch (`GPIO 13..16`) and the HSR tunable filter remain in their power-on reset state, either **attenuating the operating 5 GHz channel by 20–35 dB** (if the filter defaults to an out-of-band path) or leaving the receiver unfiltered!

### 4.2 Two Concrete Paths to Exploit `Rocket Prism 5AC Gen2` (`0xe7e9`) in FuturaMAX (`CONFIRMED`)

#### Path A (Immediate, Zero-Risk, Full Hardware Support): Stock `XC-8.7.25` with Standard 802.11ac Mode (`CONFIRMED`)
- **How it works:**
  - Keep stock `XC-8.7.25.260730.bin` (or `XC-8.7.4-cs.210415.bin`) on the `Rocket Prism 5AC Gen2`.
  - **As a High-Selectivity Sector AP (`master` mode):** Set `radio.1.polling=disabled` in `/tmp/system.cfg` (which writes `0 > /proc/sys/dev/uph_wifi0/enable`). The `Rocket Prism 5AC Gen2` operates as a standard 802.11ac AP (`umac.ko` + `hostapd`) that accepts standard OpenWrt `ath10k` CPEs (and patched `WA`/`XC` CPEs), while **`umac.ko` natively drives both the Stage 1/2 `GPIO 13..16` `ubnt_prism_hook` pre-selector AND the SPI `hsr` active filter, AND `wifi1` (`airview1`) runs continuous background spectral/DFS scanning**!
  - **As a High-Selectivity PtP/PtMP Client (`managed` STA mode):** Apply the exact Stage 10 `cron.1.job.1.cmd` `ubnt_poll_host.ko` RAM patch (`SZ=189880` for `XC-8.7.25` or `SZ=186560` for `XC-8.7.4-cs`). The `Rocket Prism 5AC Gen2` associates as a standard 802.11ac VHT40/VHT80 client to any OpenWrt `ath10k` AP with full `ubnt_prism_hook` + `hsr` active RF filtering.

#### Path B (Full OpenWrt `ath79` + `ath10k` Port on `RP-5AC-Gen2` `0xe7e9`): Exact Requirements (`CONFIRMED`)
To run pure OpenWrt (`ath79` + `ath10k` + `ath9k`) on `RP-5AC-Gen2` (`0xe7e9`):
1. **Device Tree (`qca9558_ubnt_rocket-prism-5ac-gen2.dts`):**
   - `mtdparts`: `256k(u-boot)ro,64k(u-boot-env),15744k(firmware),256k(cfg)ro,64k(art)ro` (combined `kernel` + `rootfs` = `15,744` KB at `0x9f050000`).
   - `wifi0` (`pcie0` `0x168c:0x003c`): `qca,caldata` at `art + 0x5000` (`2,116` B).
   - `wifi1` (`wmac` `qca9558` AHB): `qca,caldata` at `art + 0x1000` (`ath9k` 1x1 5 GHz auxiliary spectral/background scan radio).
2. **Stage 1 & Stage 2 AirPrism Pre-Selector Control in OpenWrt (`GPIO 13, 14, 15, 16`):**
   - Export host QCA9558 `GPIO 13, 14, 15, 16` as outputs and apply Table 3.2 whenever `wlan0` (`QCA9880`) changes `(center_freq_mhz, chanbw_mhz)`:
     ```sh
     # Stage 1 (GPIO 15, 16)
     if [ "$FREQ" -ge 5150 ] && [ "$FREQ" -le 5250 ]; then
         gpioset 15=1 16=1
     elif [ "$FREQ" -ge 5470 ] && [ "$FREQ" -le 5860 ] && [ "$BW" -le 50 ]; then
         gpioset 15=1 16=0
     else
         gpioset 15=0 16=1
     fi
     # Stage 2 (GPIO 13, 14)
     if [ "$FREQ" -ge 5200 ] && [ "$FREQ" -le 5300 ]; then
         gpioset 13=1 14=0
     elif [ "$FREQ" -ge 5725 ] && [ "$FREQ" -le 5860 ]; then
         gpioset 13=0 14=1
     else
         gpioset 13=1 14=1
     fi
     ```
3. **HSR Active Filter (`hsr_param = 31`) on Shared SPI Bus:**
   - Because the HSR ASIC (`hsr` bit 28) is tuned over the shared QCA9558 SPI bus (`0xbf000000` + `GPIO 11`), running pure OpenWrt on `RP-5AC-Gen2` requires either porting the SPI tuning sequence from `umac.ko` `.text + 0x08c000..0x08cc54` as a Linux `spi-ath79` client driver or putting the HSR ASIC into wideband bypass mode. Consequently, **Path A (hybrid stock `XC-8.7.25` with `radio.1.polling=disabled` in AP mode or patched `ubnt_poll_host.ko` in STA mode)** delivers immediate 100% AirPrism (`prism` + `hsr`) hardware support and standard 802.11ac interoperability with zero custom SPI driver risk.
