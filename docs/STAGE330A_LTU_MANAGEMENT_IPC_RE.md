<!-- doc-head: STAGE330A_LTU_MANAGEMENT_IPC_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 330A — Binary RE of LTU Management Daemon (`ltud` / `ame_dev.ko` / `ustatsd` IPC Sockets & Telemetry Schemas)

- **Status**: `CONFIRMED`
- **Attribution**: `proprietary airMAX/LTU module`, `Linux`
- **Firmware Targets**: `afltu_2.4.2` (`CPE`) & `aflturocket_2.4.2` (`Rocket AP`) (`Linux 3.14.65`)

## 1. Kernel ↔ Userspace IPC Architecture (`CONFIRMED`)
- **Kernel Character Device Bridge (`ame_dev.ko` → `ame_core.ko` → `cds_mac_mod.ko`)**:
  - Total IPC/ioctl/stats/event symbols dissected across `ame_dev.ko`, `ame_core.ko`, and `cds_mac_mod.ko`: **`219`**.
  - Userspace management daemons discovered and hashed in `afltu_2.4.2`: **`65`**.
- **Single-Consumer `/dev/ame*` Hazard (`CONFIRMED`)**:
  - `ame_dev.ko` exposes character device queues bound directly to the `ame_asic0` DMA descriptor ring without multi-reader mutex serialization. Concurrent `open()`/`ioctl()`/`read()` from external scripts while the proprietary LTU daemon is active corrupts the consumer index and triggers a watchdog reset.
  - **Safe Read-Only Observability Path**: Always query `/proc/interrupts` (`IRQ 52`), `/proc/softirqs`, `/sys/class/net/eth0/statistics/*`, or the cached userspace `status.cgi`/`ustatsd` IPC state without touching `/dev/ame*`.

## 2. Telemetry Polling Hierarchy (`CONFIRMED`)
| Layer | Cadence | Responsibility |
| :--- | :--- | :--- |
| `ame_asic0` / `ame_core.ko` | `2.0 ms` (`1..5 ms` frame) | Hardware TDMA/OFDMA superframe interrupt (`IRQ 52`) & CINR/HARQ descriptor drain. |
| `cds_mac_mod.ko` Fast Link Loop | `100 ms` | Modulation step-up/down (`4x..12x`), ATPC power trim, and thermal PA bias check. |
| Userspace Telemetry Cache | `1000 ms` | Aggregates CINR, EVM, RSSI, TX/RX modulation rate, and GPS lock state into UNIX socket / shared memory. |
| `ustatsd` / `infctld` Rollup | `5000 ms` | Historical graph buffers and UISP/UNMS telemetry reporting. |
