<!-- doc-head: STAGE376A_LTU_ROCKET_ARRIA10_FPGA_MAILBOX_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 376A — Ground-Up Binary RE of LTU-Rocket Dual-SoC Architecture (`amesoc3` HPS + FPGA Mailbox, `HFE`/`HCAM`, & `100 MHz` Synthesis)

- **Status**: `CONFIRMED`
- **Attribution**: `proprietary airMAX/LTU module`, `hardware`, `Linux`
- **Module Size Delta**: `aflturocket_2.4.2` `cds_mac_mod.ko` (`145,332 B`) vs `afltu_2.4.2` `cds_mac_mod.ko` (`139,672 B`) = **`+5,660 B`** of AP-only multi-user OFDMA scheduler, GPS superframe phase-lock, and `100 MHz` synthesis code (`195` FPGA/mailbox/HFE/HCAM symbols extracted).

## 1. Hard Processor System (`HPS`) ↔ FPGA Baseband Architecture (`CONFIRMED`)
| Hardware Block | MMIO / Interrupt / Daemon | First-Principles Function (`CONFIRMED`) |
| :--- | :--- | :--- |
| **`amesoc3` ARMv7 HPS** | Dual-Core `Linux 3.14.65 SMP PREEMPT RT` | Runs `ame.core.Hi` (`FIFO 90`), `ame.core.Frm` (`FIFO 85`), `modemer` (`FIFO 55`), and `ame.core.L2Q` (`FIFO 54`). |
| **FPGA Baseband (`air_fpga`)** | `IRQ 52` (`ame_asic0`) + HPS Mailbox (`hps:$5`) | Executes 2048-point FFT/IFFT, LDPC FEC, `4096-QAM` demapper, and hardware TDMA/OFDMA slot timing. |
| **`AME.hcam` (Hardware CAM)** | `IRQ /proc/interrupts AME.hcam*` (`CPU1`) | Line-rate hardware station `AID` (`1..64`) + VLAN tag classification in FPGA fabric. |
| **`AME.hfe` (Hardware Forwarding)** | `IRQ /proc/interrupts AME.hfe` (`CPU1`) | Zero-copy L2 bridge forwarding between `f0280000.gmac0` / `f0290000.gmac1` and `AME.gem0..1` DMA rings. |

## 2. `100 MHz` Full-Band Synthesis (`CONFIRMED`)
- **Supported Channel Widths**: `10, 20, 30, 40, 50, 60, 80, 100 MHz`.
- **`100 MHz` Numerology**: `2048`-point FFT (`48.828 kHz` subcarrier spacing), delivering up to **`1,360 Mbps`** raw PHY rate (`> 950 Mbps` TCP/IP goodput) at `4096-QAM 12x` (`2x2` MIMO).
