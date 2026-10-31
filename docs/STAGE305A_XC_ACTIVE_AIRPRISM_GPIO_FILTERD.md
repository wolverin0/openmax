<!-- doc-head: Stage 305A Active-AirPrism 2-Bank GPIO 13..16 Filter Daemon (fmx_xc_airprism_filterd.sh) -->
Userspace 2-bank GPIO 13..16 filter daemon for Active-AirPrism XC radios implementing the 6-entry cascade truth table from umac.ko.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 305A — Active-`AirPrism` `XC` 2-Bank `GPIO 13..16` Filter Daemon (`fmx_xc_airprism_filterd.sh`)

- **Status**: `CONFIRMED` (`live_radios_241_242_20_250_touched = false`, `memory-master`: `<memorymaster-id>`)
- **Attribution**: `proprietary airMAX/LTU module` / `Linux` / `hardware` (`QCA9558` `GPIO 13..16` `0x1e000`)
- **Daemon Script**: [`fmx_xc_airprism_filterd.sh`](../firmware/openwrt/xc_family_universal_kit/fmx_xc_airprism_filterd.sh) (`SHA-256`: `91698b102cdb1256fce7ca2ab35afad4348f0a0e6a0f0273cfab1825e4d511a4`)
- **Receipt**: [`stage305a_xc_active_airprism_gpio_filterd.json`](../artifacts/autoresearch/stage305a_xc_active_airprism_gpio_filterd.json)

## 1. 6-Entry Cascade Truth Table (`XC.v8.7.25` `umac.ko` `ubnt_prism_filters` @ `.data+0x001510`)
| Entry | Bank | GPIO Pins (`mask`) | Frequency Range (`MHz`) | Max BW (`MHz`) | Pin State (`val`) |
| :---: | :---: | :--- | :--- | :---: | :--- |
| `0` | Bank 1 | `GPIO 15, 16` (`0x18000`) | `5150 .. 5250` | `<= 160` | `g15=1, g16=1` (`0x18000`) |
| `1` | Bank 1 | `GPIO 15, 16` (`0x18000`) | `5470 .. 5860` | `<= 50` | `g15=1, g16=0` (`0x08000`) |
| `2` | Bank 1 | `GPIO 15, 16` (`0x18000`) | `3000 .. 6200` (fallback) | `<= 160` | `g15=0, g16=1` (`0x10000`) |
| `3` | Bank 2 | `GPIO 13, 14` (`0x06000`) | `5200 .. 5300` | `<= 160` | `g13=1, g14=0` (`0x02000`) |
| `4` | Bank 2 | `GPIO 13, 14` (`0x06000`) | `5725 .. 5860` | `<= 160` | `g13=0, g14=1` (`0x04000`) |
| `5` | Bank 2 | `GPIO 13, 14` (`0x06000`) | `3000 .. 6200` (fallback) | `<= 160` | `g13=1, g14=1` (`0x06000`) |

## 2. Verified Self-Test Vectors on `198.18.0.62` `/bin/sh`
- `5180MHz_40MHz_UNII1`: `ACTIVE_AIRPRISM sysid=0xe7e9 freq=5180MHz bw=40MHz g13=1 g14=1 g15=1 g16=1 bank1=0x18000(e0) bank2=0x06000(e5) mask=0x1e000`
- `5220MHz_40MHz_UNII1_2A_OVERLAP`: `ACTIVE_AIRPRISM sysid=0xe7e9 freq=5220MHz bw=40MHz g13=1 g14=0 g15=1 g16=1 bank1=0x18000(e0) bank2=0x02000(e3) mask=0x1a000`
- `5500MHz_40MHz_UNII2C_NARROW`: `ACTIVE_AIRPRISM sysid=0xe7e9 freq=5500MHz bw=40MHz g13=1 g14=1 g15=1 g16=0 bank1=0x08000(e1) bank2=0x06000(e5) mask=0x0e000`
- `5500MHz_80MHz_UNII2C_WIDE`: `ACTIVE_AIRPRISM sysid=0xe7e9 freq=5500MHz bw=80MHz g13=1 g14=1 g15=0 g16=1 bank1=0x10000(e2) bank2=0x06000(e5) mask=0x16000`
- `5785MHz_40MHz_UNII3_NARROW`: `ACTIVE_AIRPRISM sysid=0xe7e9 freq=5785MHz bw=40MHz g13=0 g14=1 g15=1 g16=0 bank1=0x08000(e1) bank2=0x04000(e4) mask=0x0c000`
- `5785MHz_80MHz_UNII3_WIDE`: `ACTIVE_AIRPRISM sysid=0xe7e9 freq=5785MHz bw=80MHz g13=0 g14=1 g15=0 g16=1 bank1=0x10000(e2) bank2=0x04000(e4) mask=0x14000`
- `PASSIVE_XC_0XE1F5_NOOP`: `PASSIVE_NOOP sysid=0xe1f5`
