<!-- doc-head: STAGE398A_LTU_BLE_GATT_PROVISIONING_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 398A — Ground-Up Binary RE of LTU BLE Management Radio, Alignment Mode & UART/GPIO Interrupts

- **Status**: `CONFIRMED`
- **Attribution**: `proprietary airMAX/LTU module`, `Linux`, `hardware`
- **Symbols Dissected**: **`2298`** UART/GPIO/SPI/HAL/alignment symbols across `afltu_2.4.2` and `aflturocket_2.4.2`.

## 1. Provisioning & Antenna Alignment (`f_align` / `f_dealign`) Hazard (`CONFIRMED`)
In `/bin/ame_drv.sh` (lines `375..421`), Ubiquiti's UISP/BLE alignment mode (`ame_drv.sh align <sec>` / `ame_drv.sh dealign`) executes:
```sh
f_stop
f_start
sleep 2
amecli align 1 $1
```
- **Critical Production Hazard (`CONFIRMED`)**: Entering or exiting antenna alignment mode invokes `f_stop` followed by `f_start`, which kills `amespecd`, `air_fpga`, and `af_cal`, brings `ath0` down, and reloads the FPGA state machine—causing a **`6..8 second` full RF link blackout**.
- **Safe Alternative**: Read real-time `CINR`/`EVM`/`RSSI` from `status.cgi` / `ustatsd` UNIX cache without ever invoking `amecli align 1`.

## 2. UART / GPIO / SPI Interrupt Isolation (`CONFIRMED`)
- `IRQ 63` (`UART0` / management serial) and `spi32766.0` (`dbg_ame_debug_level=5`) share `CPU0` if left unpinned.
- In `rc.poststart_ltu_safe_champion.sh` (`v8`), `IRQ 52` (`ame_asic0`) and `IRQ 63` are explicitly separated across `CPU0`/`CPU1` (`smp_affinity=2` vs `1`), preventing management/provisioning polling from jittering the `2 ms` TDMA superframe interrupt.
