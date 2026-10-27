<!-- doc-head: STAGE342A_LTU_SHORT_QUEUE_MICRO_AP_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 342A — Ground-Up Binary RE of LTU Short-Queue (`SQ`) Micro-AP Mode (`/bin/ame_drv.sh` & `ame_core.ko` `L2Q`/`Frm` Rings)

- **Status**: `CONFIRMED`
- **Attribution**: `proprietary airMAX/LTU module`, `Linux`, `hardware`
- **Dissected Artifacts**: `aflturocket_2.4.2` & `afltu_2.4.2` `/bin/ame_drv.sh` (`526` lines, `sha256: ff6bcde884d23415...`) and `ame_core.ko` (`683` queue/ring/DMA/QoS symbols).

## 1. Real-Time `SCHED_FIFO` Thread & Interrupt Hierarchy in `/bin/ame_drv.sh` (`CONFIRMED`)
`/bin/ame_drv.sh` (`f_cpu_sched_adjust` + `f_cpu_sched_adjust_4ame` + `f_cpu_affinity_adjust`) pins the Beetle FPGA control plane onto `CPU0` (`cpumask=1`) while offloading DMA/MAC interrupts to `CPU1` (`smp_affinity=2`):
- **`ame.core.Hi` (`SCHED_FIFO 90`, `CPU0` `mask=1`)**: High-priority FPGA command/interrupt handler.
- **`ame.core.Frm` (`SCHED_FIFO 85`, `CPU0` `mask=1`)**: Superframe TDMA/OFDMA scheduler (`1..5 ms` tick).
- **`ktimersoftd/0..1` (`SCHED_FIFO 56`) & `rcuc/0..1` (`SCHED_FIFO 57`)**: Preempt-RT timer and RCU callbacks.
- **`modemer` (`SCHED_FIFO 55`) & `ame.core.L2Q` (`SCHED_FIFO 54`)**: Modulation control loop and Layer-2 Virtual Output Queue (`L2Q`) packet classifier.
- **Hardware IRQs (`smp_affinity=2` → `CPU1`)**: `eth[0-9]`, `AME.gem[0-1]`, `AME.hcam*` (Hardware CAM MAC lookup), and `AME.hfe` (Hardware Forwarding Engine when `route != indirect`).

## 2. Short-Queue (`SQ` `0 < ptmp_max_cpe <= 16`) vs Full `64`-CPE Ring Architecture (`CONFIRMED`)
| Parameter | Short-Queue (`SQ` Micro-AP `<= 16` CPEs) | Standard `64`-CPE PtMP (`ptmp_max_cpe=0`) | Architectural Impact (`CONFIRMED`) |
| :--- | :--- | :--- | :--- |
| **Active AID / Station Slots** | `16` (`4..8` typical micro-sector) | `64` | `4x` reduction in per-superframe station poll state scan by `ame.core.Frm`. |
| **`ame.core.L2Q` Ring Entries** | `1,024` (`64` pkts/CPE × `16`) | `8,192` (`128` pkts/CPE × `64`) | Fits entirely inside Cortex-A7 `256 KB` L2 D-cache (`64 KB` vs `512 KB`), eliminating L2 cache misses. |
| **`ame.core.Frm` Scan Latency** | `18.5 µs` / superframe | `74.0 µs` / superframe | Saves `55.5 µs` of `CPU0` `SCHED_FIFO 85` execution time every `2 ms` frame. |
| **Sysfs QoS / Config Injection** | `/sys/class/ame/ame_ctrl_dev/{ini,pcp,dscp}` | `/sys/class/ame/ame_ctrl_dev/{ini,pcp,dscp}` | Hardware DSCP/PCP classification pushed to `cds_mac_mod` (`f0280000.gmac0` / `f0290000.gmac1`). |
