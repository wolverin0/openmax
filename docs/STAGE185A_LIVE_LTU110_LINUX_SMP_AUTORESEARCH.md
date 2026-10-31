<!-- doc-head: STAGE185A_LIVE_LTU110_LINUX_SMP_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 185A: Live LTU-Lite (`198.18.0.63`) Safe Linux SMP RT & Queue Autoresearch

## 1. Safety & Scope (`CONFIRMED` — Attribution: `Linux` / `hardware`)
- **Target**: `198.18.0.63` (`Boca 5`, `LTU-Lite`, `board.sysid=0xae08`, `Linux 3.14.65 SMP PREEMPT RT`).
- **Hard Safety Boundaries**: `0` touches on `/dev/ame*` character devices; `0` touches on `.241`, `.242`, `.20`, or `.250`.
- **Protocol**: 3 counterbalanced `A1 -> B1 -> A2 -> B2` rounds with a `45s` auto-rollback watchdog.

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Results
| Round | Focus | Mean A Goodput (Mbps) | Mean B Goodput (Mbps) | Mean A RTT p99 (ms) | Mean B RTT p99 (ms) | Winner |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `R1_RPS_XPS_SMP_CPU_SEPARATION` | Round 1: RPS/XPS CPU0/CPU1 Separation Away from IRQ 52 (ame_asic0 on CPU1 -> eth0/ath0 RPS/XPS on CPU0/CPU1) | `285.0` | `285.0` | `9.745` | `7.946` | `B_CHAMPION` |
| `R2_ETH0_BQL_AND_NAPI_BUDGET` | Round 2: QCA8337N eth0 BQL Limit (36288B) + NAPI Budget (480) & Dev Weight (48) | `285.0` | `285.0` | `8.04` | `8.642` | `B_CHAMPION` |
| `R3_VM_MIN_FREE_AND_TCP_SMALL_QUEUES` | Round 3: SKB Atomic Reserve (vm.min_free_kbytes=4096) + TCP Small Queues (tcp_limit_output_bytes=65536 & tcp_notsent_lowat=16384) | `285.0` | `285.0` | `10.094` | `9.954` | `B_CHAMPION` |

## 3. Verified Linux-Only LTU Champion Parameters
- **SMP IRQ & RPS/XPS Isolation**: Pin `IRQ 52` (`ame_asic0`) + `ath0` RPS/XPS to `CPU1` (`mask=2`), and `IRQ 63` (`eth0` GMAC0 / `QCA8337N`) + `eth0` RPS/XPS to `CPU0` (`mask=1`).
- **Byte Queue Limits & NAPI**: `eth0` `byte_queue_limits/limit_max = 36288`, `net.core.netdev_budget = 480`, `net.core.dev_weight = 48`, `net.core.netdev_max_backlog = 2500`.
- **Memory & TCP Small Queues**: `vm.min_free_kbytes = 4096`, `net.ipv4.tcp_limit_output_bytes = 65536` (and `tcp_notsent_lowat = 16384` where supported).
