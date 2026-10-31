<!-- doc-head: STAGE44A_M26_M27_NAPI_COALESCING_AND_R5AC_TXQ_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 44A Physical Benchmark: `M26` (`Rocket Prism 5AC` `br0` `tx_queue_len=256` & `netdev_budget=600` vs OpenWrt `ag71xx` `eth0` BQL) & `M27` (`Linux 6.6.110` NAPI Hard-IRQ Deferral & Poll Weight/Budget Tuning)

- **Task ID**: `T-S44A-M26-M27-PER-STA-WDS-NAPI-WEIGHT-AND-UDP-GRO-IPTV-BENCH`
- **Timestamp**: `2026-10-25T22:07:20Z`
- **Starting Baseline (`Arm A`)**: **`Stage 42A Champion v14` (`S42A-R5`: `M24e_M25e_PURE_SYSFS_WDS_TXQ_256_AND_LBM5_BR0_TXQ_256`)**
  - Direct sysfs `/sys/class/net/br-lan/tx_queue_len=256` & `/sys/class/net/phy0-ap0*/tx_queue_len=256` on `LAP-120` (`198.18.0.43`), `/sys/class/net/br-lan/tx_queue_len=256` & `/sys/class/net/phy0-sta0/tx_queue_len=256` on `Loco 5AC` (`198.18.0.47`), while `eth0` `tx_queue_len=1000` (with hardware Byte Queue Limits `BQL limit=54250/1780` on `ag71xx`).
  - `LiteBeam M5` (`198.18.0.48` / `198.18.0.52`) `br0/ath0/eth0` `tx_queue_len=256` + `ubnt_ewma_delegate_on=1`.
  - `Rocket Prism 5AC Gen2` (`198.18.0.64` / `198.18.0.68`) `ath0/eth0` `tx_queue_len=256`, `br0` `tx_queue_len=1000`, `net.core.netdev_budget=300`.
  - `mac80211` `aqm` `fq_quantum=4542/1514`, `fq_limit=2048/1024`, `AQL VO=300/600, VI=1200/2400, BE=1500/3000` (`AP`) / `900/1500` (`CPE`), `aql_threshold=5000/4000`, dual-netdev airtime weights `768:512:128`, `net.core.netdev_max_backlog=1000`, `dev_weight=64/1/1`, `netdev_budget=600`, `netdev_budget_usecs=20000`, `napi_defer_hard_irqs=0`, `gro_flush_timeout=0`.
- **Safety & Execution Policy**:
  - `100%` RAM-only (`0` flash writes; `cfgmtd -w` and `uci commit` forbidden).
  - `0` production radios touched (`198.18.0.7` untouched).
  - Counterbalanced `A1 -> B1 -> A2 -> B2` physical bench order across `5` rounds (`20` windows).

---

## 1. Pre-Experiment Hardware & Kernel Sysfs/Procfs Inspection (`CONFIRMED`)

Before executing Stage 44A, we inspected all sysfs/procfs netdev queueing, BQL, and NAPI knobs across `LAP-120` (`.20`), `Loco 5AC` (`.250`), `Rocket Prism 5AC Gen2` (`.198`), and `LiteBeam M5` (`.251`/`198.18.0.52`):

1. **OpenWrt 24.10 (`Linux 6.6.110`) on `LAP-120` (`.20`) & `Loco 5AC` (`.250`) (`CONFIRMED`)**:
   - `/sys/class/net/*/napi_defer_hard_irqs = 0` and `/sys/class/net/*/gro_flush_timeout = 0` exist and are writable on `eth0`, `br-lan`, `phy0-ap0`, `phy0-ap0.sta1`, `phy0-ap0.sta2`, and `phy0-sta0`.
   - `/proc/sys/net/core/dev_weight = 64`, `dev_weight_rx_bias = 1`, `dev_weight_tx_bias = 1`, `netdev_budget = 600`, `netdev_budget_usecs = 20000`, `netdev_max_backlog = 1000`.
   - **Hardware Byte Queue Limits (`BQL`) on `eth0` (`ag71xx`) vs Virtual Interfaces**:
     - On `LAP-120` (`.20`), `/sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit = 54250` bytes (active dynamic BQL!).
     - On `Loco 5AC` (`.250`), `/sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit = 1780` bytes (active dynamic BQL!).
     - On `br-lan`, `phy0-ap0*`, and `phy0-sta0`, `byte_queue_limits/limit = 0` (no BQL; `tx_queue_len=256` from `Stage 42A Champion v14` bounds them directly).
2. **`Rocket Prism 5AC Gen2` (`.198`, `XC.v8.7.25`, `Linux 2.6.32.68`) (`CONFIRMED`)**:
   - `/sys/class/net/ath0/tx_queue_len = 256` and `/sys/class/net/eth0/tx_queue_len = 256`, **but `/sys/class/net/br0/tx_queue_len = 1000`**, and `/proc/sys/net/core/netdev_budget = 300` (half of OpenWrt's `600`).

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Results Summary (`5` Rounds / `20` Windows)

| Round ID | Mechanism & Treatment (`Arm B` vs `Stage 42A Champion v14` `Arm A`) | 3-CPE Goodput (`A -> B`) | Loaded `p95` RTT (`A -> B`) | Loaded `p99` RTT (`A -> B`) | Dual IPTV Loss & Jitter (`tid4_ac1`) | VoIP Loss & Jitter (`tid6_ac0`) | Decision & Label |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`S44A-R1`** | `M26_R5AC_BR0_TXQ_256_AND_ETH0_256_UNIFORM_SECTOR_TXQ` (`R5AC` `br0=256, budget=600` + OpenWrt `eth0 tx_queue_len=256`) | `45.803 -> 44.894 Mbps` (`-1.985%`) | `97.380 -> 104.997 ms` (`+7.822%`) | `98.613 -> 104.997 ms` (`+6.474%`) | `6.8936% -> 6.3751%` loss, `1.978 -> 1.967 ms` (`-0.556%`) | `0.00% -> 0.00%` loss, `1.784 -> 2.615 ms` (`+46.581%`) | `RETAIN_CURRENT_CHAMPION` (`REFUTED`, Pareto `-4.7223%`) |
| **`S44A-R2`** | `M27a_NAPI_DEFER_HARD_IRQS_2_GRO_TIMEOUT_100US` (`napi_defer_hard_irqs=2`, `gro_flush_timeout=100000` ns across `eth0/br-lan/phy0-*`) | `46.040 -> 45.385 Mbps` (`-1.423%`) | `105.852 -> 96.483 ms` (`-8.851%`) | `105.852 -> 99.396 ms` (`-6.099%`) | `6.5607% -> 8.1571%` loss, `1.773 -> 1.937 ms` (`+9.250%`) | `0.00% -> 0.00%` loss, `1.743 -> 1.910 ms` (`+9.581%`) | `RETAIN_CURRENT_CHAMPION` (`REFUTED`, Pareto `+1.6752%`, GP `-1.423%`) |
| **`S44A-R3`** | `M27b_DEV_WEIGHT_TX_BIAS_2_BUDGET_USECS_8000` (`dev_weight=48, dev_weight_tx_bias=2, netdev_budget=300, netdev_budget_usecs=8000`) | `47.441 -> 46.769 Mbps` (`-1.416%`) | `107.637 -> 104.715 ms` (`-2.715%`) | `111.469 -> 105.560 ms` (`-5.301%`) | `5.6356% -> 5.8912%` loss, **`2.001 -> 1.155 ms` (`-42.279%`)** | `0.00% -> 0.00%` loss, `1.808 -> 1.970 ms` (`+8.960%`) | `RETAIN_CURRENT_CHAMPION` (`REFUTED`, Pareto `-0.4664%`) |
| **`S44A-R4`** | `M26_M27c_UNIFORM_TXQ_256_AND_TX_BIAS_2_BUDGET_12MS` (`eth0=256` + `R5AC br0=256` + `dev_weight=64, dev_weight_tx_bias=2, budget_usecs=12000`) | `43.493 -> 28.646 Mbps` (`-34.137%`) | `132.595 -> 88.442 ms` (`-33.299%`) | `132.595 -> 92.217 ms` (`-30.452%`) | `7.2260% -> 2.5554%` loss, **`1.611 -> 0.906 ms` (`-43.762%`)** | `0.0833% -> 0.00%` loss, **`2.537 -> 0.800 ms` (`-68.467%`)** | `RETAIN_CURRENT_CHAMPION` (`REFUTED`, Pareto `-22.4818%`) |
| **`S44A-R5`** | **`M26b_PURE_R5AC_BR0_TXQ_256_OPENWRT_ETH0_1000`** (`Rocket Prism 5AC` `br0/ath0/eth0` `tx_queue_len=256` & `netdev_budget=600`; OpenWrt `eth0=1000` with `ag71xx` BQL & NAPI stock) | **`32.998 -> 35.354 Mbps` (`+7.140%`, `B2=38.518 Mbps`)** | **`85.782 -> 82.678 ms` (`-3.618%`)** | **`97.689 -> 85.123 ms` (`-12.863%`)** | **`0.4738% -> 0.00%` loss (`0/5,690` lost in `B1+B2`, `4.965 Mbps`)** | **`0.2504% -> 0.00%` loss (`0/1,199` lost in `B1+B2`, `127.5 Kbps`)** | **`PROMOTE_NEW_CHAMPION` (`Stage 44A Champion v15`, `CONFIRMED`, Pareto `+8.4063%`)** |

---

## 3. Three Hardware & Kernel Boundary Discoveries (`CONFIRMED`)

1. **OpenWrt `ag71xx` Hardware Byte Queue Limits (`BQL`) vs `eth0 tx_queue_len=256` Starvation (`S44A-R1` & `S44A-R4`, `CONFIRMED`)**:
   - Unlike virtual interfaces (`br-lan`, `phy0-ap0*`, `phy0-sta0`) where `byte_queue_limits/limit = 0` and reducing `tx_queue_len` from `1000 -> 256` in `S42A-R5` boosted goodput (`+3.21%`) and cut `p95` RTT (`-7.92%`), the physical `eth0` (`ag71xx`) MAC on `LAP-120` (`.20`) and `Loco 5AC` (`.250`) already runs dynamic hardware Byte Queue Limits (`BQL limit = 54,250 B` on AP, `1,780 B` on CPE).
   - Shrinking `eth0` `tx_queue_len` from `1000` to `256` (`S44A-R1`, `S44A-R4`) caused wire-to-bridge ingress/egress tail-drop bursts during 3-CPE TCP + Dual IPTV saturation (`-1.99%` goodput and `+7.82%` `p95` RTT in `S44A-R1`). Keeping `eth0` at `tx_queue_len = 1000` while bounding virtual `br-lan` and `phy0-*` at `256` is mandatory.
2. **Linux 6.6.110 `napi_defer_hard_irqs=2` + `gro_flush_timeout=100us` (`M27a`) & `dev_weight_tx_bias=2` (`M27b`/`M27c`) Trade-Offs on Single-Core `MIPS 74Kc` (`S44A-R2` .. `S44A-R4`, `CONFIRMED`)**:
   - **`M27a` (`S44A-R2`)**: Enabling `napi_defer_hard_irqs=2` and `gro_flush_timeout=100000` ns (`100 us`) reduced 3-CPE loaded `p95` RTT by **`-8.851%` (`105.852 -> 96.483 ms`)** and `p99` RTT by **`-6.099%` (`105.852 -> 99.396 ms`)**, but holding UDP `1,316`-byte MPEG-TS datagrams in GRO flush timers for `100 us` increased Dual IPTV loss from `6.56% -> 8.16%` and trimmed bulk TCP goodput by `-1.423%` (`46.040 -> 45.385 Mbps`).
   - **`M27b` (`S44A-R3`)**: Setting `dev_weight=48, dev_weight_tx_bias=2, netdev_budget=300, netdev_budget_usecs=8000` slashed Dual `1080p60` IPTV jitter by **`-42.279%` (`2.001 -> 1.155 ms`)**, cut `p95` RTT by `-2.715%`, and cut `p99` RTT by `-5.301%`, but halving `netdev_budget` (`600 -> 300`) reduced bulk TCP goodput by `-1.416%` (`47.441 -> 46.769 Mbps`).
3. **Pure `Rocket Prism 5AC Gen2` (`.198`) `br0/ath0/eth0` `tx_queue_len=256` & `net.core.netdev_budget=600` Co-Design (`S44A-R5` -> `Stage 44A Champion v15`, `CONFIRMED`)**:
   - Isolating `M26b` on `Rocket Prism 5AC Gen2` (`ifconfig br0 txqueuelen 256; ifconfig ath0 txqueuelen 256; ifconfig eth0 txqueuelen 256; sysctl -w net.core.netdev_budget=600`) while keeping OpenWrt `eth0=1000` (`BQL` active), `br-lan/phy0-*=256`, and NAPI at `64/1/1` (`600` budget, `20000 us`) delivered simultaneous improvements across throughput, tail latency, and real-time UDP loss:
     - **Aggregate 3-CPE Goodput**: **`32.998 -> 35.354 Mbps` (`+7.140%`, peaking at `38.518 Mbps` in `B2`)**
     - **Loaded 3-CPE `p95` RTT**: **`85.782 -> 82.678 ms` (`-3.618%`)**
     - **Loaded 3-CPE `p50` RTT**: **`41.071 -> 38.897 ms` (`-5.293%`)**
     - **Loaded 3-CPE `p99` RTT**: **`97.689 -> 85.123 ms` (`-12.863%`)**
     - **Dual `1080p60` IPTV (`tid4_ac1`)**: Eliminated `Arm A`'s `0.4738%` loss (`27/5,699` lost datagrams) to **`0.00%` loss (`0/5,690` lost datagrams across `B1` + `B2`, `4.965 Mbps` delivered)**
     - **Real-Time VoIP (`tid6_ac0`)**: Eliminated `Arm A`'s `0.2504%` loss (`3/1,198` lost frames) to **`0.00%` loss (`0/1,199` lost frames across `B1` + `B2`, `127.5 Kbps` delivered)**
     - **Pareto Score Delta**: **`+8.4063%` -> `PROMOTE_NEW_CHAMPION` (`Stage 44A Champion v15`)**.
