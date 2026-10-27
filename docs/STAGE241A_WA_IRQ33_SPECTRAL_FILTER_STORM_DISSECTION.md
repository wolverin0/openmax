<!-- doc-head: STAGE241A_WA_IRQ33_SPECTRAL_FILTER_STORM_DISSECTION.md preserved document content -->
<!-- /doc-head -->


# Stage 241A — Binary Dissection of IRQ `33` (`ath-spectral-filter` `4.53 Billion` Interrupt Storm) in `WA.v8.7.25` `ath_dev.ko`

## 1. Binary Reverse Engineering of `ath-spectral-filter` in `ath_dev.ko` (`CONFIRMED`)

| ELF Symbol / Section | Offset in `ath_dev.ko` (`287,216` B) | Size | Dissected Call / String Target |
| :--- | :--- | :--- | :--- |
| **`.rodata` IRQ Name** | `0x032488` | `20` B | `"ath-spectral-filter"` |
| **`.rodata` Error Log** | `0x03249c` | `55` B | `"<3>unable to request IRQ for SPECTRAL-XMIT-FILTER GPIO"` |
| **`ath_spectral_filter_init`** | `.text+0x027c00` | `124` B | Calls `gpio_int_init` (`ubnthal.ko`) on `ATH GPIO` IRQ `33` |
| **`ath_spectral_filter_uninit`** | `.text+0x027c7c` | `48` B | Calls `gpio_int_uninit` (`ubnthal.ko`) |
| **`ath_spectral_filter_start`** | `.text+0x027cac` | `8` B | Tail-calls `gpio_int_enable` (`ubnthal.ko`) |
| **`ath_spectral_filter_stop`** | `.text+0x027cb4` | `8` B | Tail-calls `gpio_int_disable` (`ubnthal.ko`) |
| **`ath_dev_start_spectral_scan`** | `.text+0x007e9c` | `144` B | Invokes `ath_spectral_filter_start` when `ubntspecd` starts |
| **`ath_dev_stop_spectral_scan`** | `.text+0x0077a0` | `224` B | Invokes `ath_spectral_filter_stop` when `ubntspecd` stops |

## 2. Why `4.53 Billion` IRQ `33` Interrupts Fire Across `.60`, `.61`, `.82`, and `.83` (`CONFIRMED`)

- On `WA` dual-radio boards (`0xe3d6` `PBE-5AC-Gen2` and `0xe8e5` `LAP-120`), `radio.1` (`wifi0`, `QCA9882` PCIe 5 GHz data radio) has its TX-active line wired to an `AR9342` GPIO pin (`SPECTRAL-XMIT-FILTER GPIO`, **IRQ `33`**) so `radio.2` (`wifi1`, `AR9342` AHB AirView scanner driven by `/bin/ubntspecd -w -t -a -i wifi1 -j airview1 -m 4 -f 20 -s 200`) can blank self-transmissions during FFT sweeps.
- Because `airview.status=enabled` by default in `/tmp/system.cfg`, `ubntspecd` runs 24/7 even when no operator has the AirView UI open, causing the `AR9342` CPU to take a hardware interrupt on **every TX burst**:
  - **`Panel3 (.83)`**: **`2,142,307,805`** IRQ `33` interrupts (**`4,117.9 irq/s`**)
  - **`Guarida STA (.61)`**: **`1,059,786,236`** IRQ `33` interrupts (**`2,038.2 irq/s`**)
  - **`Panel2 (.82)`**: **`946,177,060`** IRQ `33` interrupts (**`1,818.7 irq/s`**)
  - **`Almafuerte AP (.60)`**: **`384,131,424`** IRQ `33` interrupts (**`2,064.3 irq/s`**)

## 3. Safe `Mode B` Mitigation (`airview.status=disabled`, `CONFIRMED`)

- Setting `airview.status=disabled` in `/tmp/system.cfg` stops `ubntspecd` on `wifi1`, triggering `ath_dev_stop_spectral_scan` (`.text+0x0077a0`) $
ightarrow$ `ath_spectral_filter_stop` (`.text+0x027cb4`) $
ightarrow$ `gpio_int_disable` on IRQ `33` with **zero impact** on `wifi0` (`hostapd` / `ubnt_poll_host.ko`), reclaiming `~1.85%` hard IRQ + `~3.40%` softirq CPU on the `AR9342`.
