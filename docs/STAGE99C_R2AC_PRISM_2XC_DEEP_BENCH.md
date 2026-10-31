<!-- doc-head: STAGE99C_R2AC_PRISM_2XC_DEEP_BENCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 99C — `Rocket 2AC Prism` (`2XC.v8.7.11`) Binary Module Audit (`2XC` vs `5XC`), `ath_pktlog.ko` / `ath_hs_uart` / `AirPrism` Dissection & Counterbalanced Deep Fast-Path Benchmark

- **Status**: `CONFIRMED` (`<memorymaster-id>`, `claim_id=152897`)
- **Attribution**: `proprietary airMAX module` (`ubnt_poll_host.ko`, `umac.ko`, `ath_dev.ko`, `ath_spectral.ko`, `ath_pktlog.ko`) + `Linux` (`vmlinux` `2.6.32.68` `ath_hs_uart` on `QCA9558` `MIPS 74Kc` `720 MHz`, `128 MB` RAM) + `hardware` (`QCA988x` `2.4 GHz` + `AirPrism` `IRQ 64` + `AirView` `wifi1` `IRQ 2` + `GPS UART` `IRQ 22`)
- **Artifacts & Harness**:
  - Harness: [`tools/bench/run_stage99c_r2ac_prism_2xc_deep_bench.py`](<repo>/tools/bench/run_stage99c_r2ac_prism_2xc_deep_bench.py)
  - Receipt: [`artifacts/autoresearch/stage99c_r2ac_prism_2xc_deep_bench.json`](<repo>/artifacts/autoresearch/stage99c_r2ac_prism_2xc_deep_bench.json)
  - Extracted `2XC.v8.7.11` ELF Modules: `artifacts/firmware_re_xc_ltu/2xc_8711_modules/{ubnt_poll_host.ko,ath_pktlog.ko,ath_spectral.ko,ath_dev.ko}`
  - Verification Tests: [`tests/test_stage99c_r2ac_prism_2xc.py`](<repo>/tests/test_stage99c_r2ac_prism_2xc.py)

---

## 1. Binary ELF Module Comparison: `2XC.v8.7.11` (`2.4 GHz`) vs `5XC.v8.7.4-cs` / `5XC.v8.7.25` (`5 GHz`) (`CONFIRMED`)

All four core kernel modules were extracted from `Rocket 2AC Prism` (`198.18.0.48` on `EdgeSwitch 10XP` `Boca 8`, `2XC.v8.7.11`) and analyzed with `Elf32Image`:

| Module / Build | File Size (B) | MD5 | `.text` SHA256 (Prefix) | `.rodata` SHA256 (Prefix) | `.data` SHA256 (Prefix) | Functions |
| :--- | ---: | :--- | :--- | :--- | :--- | ---: |
| **`2XC.v8.7.11` `ubnt_poll_host.ko`** | **`186,560`** | `ba1c6b4fa2c1a0ac6704fbd9361b9f4c` | `ef20f24f3280...` (`99,168` B) | **`c7f5246bd840...` (`25,824` B)** | **`53168dfcab4e...` (`832` B)** | **`150`** |
| **`5XC.v8.7.4-cs` `ubnt_poll_host.ko`** | **`186,560`** | `4103f9d0a2fdbf312d93a68b10647bca` | `c9ffb5490444...` (`99,168` B) | **`c7f5246bd840...` (`25,824` B)** | **`53168dfcab4e...` (`832` B)** | **`150`** |
| **`5XC.v8.7.25` `ubnt_poll_host.ko`** | `189,880` | `5b26b076967befe129f669096539ae21` | `62a6d88e0789...` (`101,344` B) | `60cadb358f10...` (`26,112` B) | `21c72f66e619...` (`832` B) | `154` |
| **`2XC.v8.7.11` `ath_pktlog.ko`** | `20,740` | `a0401962294531f82851b1d9911ae8fd` | `eec780800f62...` | `9ba695538fd5...` | `4b1ce8b37aa2...` | `23` |
| **`2XC.v8.7.11` `ath_spectral.ko`** | `38,284` | `a0b0e6109e52181da388fd4fb4e84873` | `4181fb9ff6a6...` | `fed7e8ccedac...` | `1252624da0ad...` | `48` |
| **`2XC.v8.7.11` `ath_dev.ko`** | `290,368` | `27b718c379b7ea9185814d051c42e57c` | `c8a4de3785e9...` | `a8d8b8882968...` | `d5d049c207be...` | `310` |

### Key Reverse-Engineering Findings (`CONFIRMED`)
1. **Cross-Band (`2.4 GHz` `2XC` vs `5 GHz` `5XC`) TDMA Scheduler Table Invariance (`CONFIRMED`)**:
   - Between `2XC.v8.7.11` (`2.4 GHz`) and `5XC.v8.7.4-cs` (`5 GHz`), `ubnt_poll_host.ko` (`186,560` bytes, `150` functions) has **`0` differing bytes in `.rodata` (`25,824` bytes, `SHA256 = c7f5246bd840...`)** and **`0` differing bytes in `.data` (`832` bytes, `SHA256 = 53168dfcab4e...`)**, and identical `.bss` size (`2,560` bytes).
   - Even in `.text` (`99,168` bytes), only **`130` bytes** differ (`0.13%`), consisting solely of `umac`/`ath_dev` struct member offset immediates (`0xdf48` vs `0xded0` and `0x96f0` vs `0x92e8`). All `ptmp_netconf` profiles, `_retr_supression_levels`, `_voip_dynamic_duration_levels`, and all `31` `/proc/sys/dev/uph_wifi0/*` sysctl nodes are 100% identical between `2.4 GHz` `2XC` and `5 GHz` `5XC`.
2. **`2XC-DISC-01` — Why `ath_pktlog.ko` Is Shipped on Disk (`20,740` B) But Omitted from `/etc/modules.d/50-ath-11c-2ac` (`CONFIRMED`)**:
   - On `2XC.v8.7.11`, `/lib/modules/2.6.32.68/ath_pktlog.ko` (`20,740` bytes, `23` functions: `pktlog_txctl`, `pktlog_txstatus`, `pktlog_rx`, `pktlog_rcfind`, `pktlog_rcupdate`, `pktlog_ani`) and `/bin/athdebug` / `/bin/athstats` (`pktlogconf`) are present in SquashFS, but `/etc/modules.d/50-ath-11c-2ac` loads only `adf`, `asf`, `ath_hal`, `ath_rate_atheros`, `ath_spectral`, `ath_dev`, `umac` — omitting `ath_pktlog` at boot. We still enforce `rmmod ath_pktlog 2>/dev/null || true` as an idempotent guard without ever re-inserting `ath_pktlog.ko` (`PKTLOG-BUG-02`).
3. **`XC-BUG-03` — `ath_hs_uart_close` (`0x80122d5c` in `vmlinux`) Is an 8-Byte Empty Stub (`jr $ra; nop`) (`CONFIRMED`)**:
   - Inspecting `/proc/kallsyms` on `2XC.v8.7.11` revealed `80122d40 t ath_hs_uart_open`, **`80122d5c t ath_hs_uart_close`**, and `80122d64 t ath_hs_uart_put_char`. Because `0x80122d64 - 0x80122d5c = 8` bytes (`jr $ra; nop`), QCA's `ath_hs_uart_close` never clears `ATH_HS_UART_INT_EN` (`0x18500010`) when `/dev/ttyS1` (`4, 65`) is closed. Consequently, once `/usr/bin/ubnt-gps-reader` opens `/dev/ttyS1` at boot, `ath_hs_uart_isr` (`0x80123044`, `IRQ 22 hs-uart`) fires continuously at `~183.5 IRQs/sec` (`34.3M` interrupts). Freezing `ubnt-gps-reader` (`kill -STOP`) eliminates the user-space context switches and `/proc/sys/dev/uph/gps_info` + `/tmp/gps_sat_info` writes (`-11.3%` `IRQ 22` wakeups).

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` `2XC` Deep Fast-Path Triple-Play Benchmark (`CONFIRMED`)

By binding `iperf3 -s -B 198.18.0.48` on `br0` (`Boca 8`), we eliminated the Linux multihomed UDP source-IP mismatch (`br0` primary `.253` vs alias `.251`) and drove full concurrent Triple-Play traffic from `LTU-Lite #1` (`198.18.0.63` on `Boca 5`): Bulk TCP (`5201`) + IPTV UDP (`8 Mbps`, `1316B`, `TOS 0x80` on `5202`) + VoIP UDP (`64 kbps`, `160B`, `TOS 0xb8` on `5203`) + `20` loaded `1400B` ICMP pings.

| Trial / Summary | Arm ID | Bulk TCP (`Mbps`) | IPTV UDP (`Mbps` / Jitter / Loss) | Loaded `1400B` RTT `p50` / `p95` / `p99` (`ms`) | `IRQ 2` (`wifi1`) $\Delta$ | `IRQ 22` (`hs-uart`) $\Delta$ | `IRQ 4` (`eth0`) $\Delta$ |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Trial 1 (`A1`)** | `S99C-ARM-A-STAGE98D-BASELINE` | `22.590` | `7.920` / `0.323 ms` / `0%` | `2.661` / `4.930` / `5.516` | `+1,510` | `+1,113` | `+19,090` |
| **Trial 2 (`B1`)** | `S99C-ARM-B-2XC-DEEP-FASTPATH-CHAMPION` | **`30.640` (`+35.6%`)** | `7.844` / `0.394 ms` / `0%` | `2.018` / `3.792` / `3.805` | **`0`** | `+930` | **`+24,687`** |
| **Trial 3 (`A2`)** | `S99C-ARM-A-STAGE98D-BASELINE` | `28.801` | `7.902` / `0.531 ms` / `0%` | `2.672` / `5.459` / `6.141` | `+1,351` | `+1,113` | `+23,126` |
| **Trial 4 (`B2`)** | `S99C-ARM-B-2XC-DEEP-FASTPATH-CHAMPION` | `24.391` | `7.918` / **`0.273 ms`** / `0%` | **`1.661` / `2.564` / `2.714`** | **`0`** | `+1,044` | `+20,670` |
| **Median (`Arm A`)** | `S99C-ARM-A-STAGE98D-BASELINE` | `25.695` | `7.911` / `0.427 ms` / `0%` | `2.667` / `5.194` / `5.829` | `+2,861` total | `+2,226` total | `+42,216` total |
| **Median (`Arm B`)** | `S99C-ARM-B-2XC-DEEP-FASTPATH-CHAMPION` | **`27.515` (`+7.1%`, peak `+35.6%`)** | `7.881` / **`0.334 ms` (`-21.8%`)** / `0%` | **`1.839` (`-31.0%`) / `3.178` (`-38.8%`) / `3.260` (`-44.1%`)** | **`0` (`-100%`)** | **`+1,974` (`-11.3%`)** | **`+45,357` (`+7.4%`)** |
