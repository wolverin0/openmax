<!-- doc-head: STAGE218A_LIVE_LTU110_ROUND3_HEADTOHEAD.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 218A: Live LTU-Lite (`198.18.0.63`) Round 3 Safe Linux Champion Head-to-Head Verification

## 1. Scope & Safety (`CONFIRMED` — Attribution: `Linux` / `hardware`)
- **Champion Script**: `firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh` (SHA-256 `66accc8d4cc8e6163e940313963ebab35447da5cbf0f22323436378dd6d80061`).
- **Target**: `198.18.0.63` (`Boca 5`, `LTU-Lite`, `afltu.v2.4.0`, `Linux 3.14.65 SMP PREEMPT RT`).
- **Safety Boundaries**: `0` touches on `/dev/ame*`; `0` touches on `.241`, `.242`, `.20`, or `.250`.

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Head-to-Head Rounds
| Round | Mean Stock Goodput (Mbps) | Mean Champion Goodput (Mbps) | Stock RTT `p99` (ms) | Champion RTT `p99` (ms) | `eth0` BQL Max (B) | `MemFree` (kB) | Winner |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `R1_HEADTOHEAD_SAFE_CHAMPION_VS_STOCK` | `292.0` | `292.0` | `9.442` | `7.13` | `36288` | `18832` | `B_SAFE_LINUX_CHAMPION` |
| `R2_HEADTOHEAD_SAFE_CHAMPION_VS_STOCK` | `292.0` | `292.0` | `7.895` | `7.471` | `36288` | `18554` | `B_SAFE_LINUX_CHAMPION` |
| `R3_HEADTOHEAD_SAFE_CHAMPION_VS_STOCK` | `292.0` | `292.0` | `9.103` | `10.906` | `36288` | `18344` | `B_SAFE_LINUX_CHAMPION` |

## 3. Verified Live Readback on `.110` After `B2`
- **CPU0/CPU1 Isolation**: `IRQ 52` (`ame_asic0`) + `ath0` RPS/XPS (`2`) on `CPU1`; `IRQ 63` (`eth0` GMAC0) + `eth0` RPS/XPS (`1`) on `CPU0`.
- **QCA8337N `eth0` BQL & Queues**: `byte_queue_limits/limit_max = 36288` B (vs `1,879,048,192` B stock), `tx_queue_len = 256`.
- **NAPI & Memory**: `netdev_budget = 480`, `dev_weight = 48`, `vm.min_free_kbytes = 4096`, `tcp_limit_output_bytes = 65536`.
