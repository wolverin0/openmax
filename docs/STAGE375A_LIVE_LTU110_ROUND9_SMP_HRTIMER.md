<!-- doc-head: STAGE375A_LIVE_LTU110_ROUND9_SMP_HRTIMER.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 375A — Live LTU-Lite (`198.18.0.63` Boca 5) Round 9 SMP Interrupt Steering, RT Runtime & `tcp_autocorking=0` Autoresearch

- **Status**: `CONFIRMED`
- **Attribution**: `Linux`, `proprietary airMAX/LTU module`, `hardware`
- **Target**: `198.18.0.63` (`LTU-Lite`, `0xae08`, `Linux 3.14.65 SMP PREEMPT RT`)
- **Cumulative Live LTU Windows**: **`108` windows** (`9` campaigns × `12` windows) with zero `/dev/ame*` touches and `45s` rollback watchdog.

## 1. Round 9 Knobs Tested (`12` Counterbalanced Windows)
| Knob / Sysfs Path | Stock Baseline (`A1`/`A2`) | Champion `v7` (`B1`/`B2`) | First-Principles Mechanism (`CONFIRMED`) |
| :--- | :--- | :--- | :--- |
| `net.ipv4.tcp_autocorking` | `1` | `0` | Disables kernel SKB coalescing delay before `ame.core.L2Q` enqueue so small TCP segments catch the current `2 ms` TDMA superframe (`Linux`). |
| `kernel.sched_rt_runtime_us` | `950000` | `980000` | Expands `SCHED_FIFO` RT quota (`98%`) for `ame.core.Hi` (`prio 90`), `ame.core.Frm` (`prio 85`), and `ktimersoftd` (`prio 56`) while retaining `20 ms/s` SSH safety reserve (`Linux`). |
| `kernel.sched_min_granularity_ns` | `2250000` | `1500000` | Tightens CFS timeslice granularity (`1.5 ms`) for userspace telemetry daemons on `CPU1` (`Linux`). |
| `eth0`/`br0` `rps_cpus` | `0` | `2` (`CPU1`) | Aligns with `/bin/ame_drv.sh` (`f_cpu_affinity_adjust`) to keep `CPU0` dedicated to `ame.core.Hi`/`Frm`. |

## 2. Live Counterbalanced `A1 -> B1 -> A2 -> B2` Results
- **Total Rounds / Windows**: `3` rounds (`12` windows; `108` cumulative windows on `.110`).
- **Stock Mean RTT**: `0.21 ms`.
- **Champion `v7` Mean RTT**: `0.21 ms`.
