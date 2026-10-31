<!-- doc-head: STAGE336A_LIVE_2XC253_ROUND7_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 336A — Live `2XC` `Rocket 2AC Prism` (`198.18.0.65` Boca 6) Round 7 2.4 GHz High-Noise Floor & Co-Channel Contention Autoresearch

## 1. Objective & Safety Envelope (`CONFIRMED`)
Execute **Round 7** (`4` counterbalanced `A1 -> B1 -> A2 -> B2` windows) on the live bench `Rocket 2AC Prism` (`198.18.0.65`, `2XC.v8.7.11`, Linux `2.6.32.68`, Boca 6) evaluating:
- **2.4 GHz High-Noise Floor & Co-Channel Immunity** (`proprietary airMAX/LTU module`): `uph_wifi0/daprot=2` (Dynamic AirPrism CCA immunity), `uph_wifi0/ff_mcast_airtime_limit=4` (capping 2.4 GHz lowest-rate multicast airtime tax to `4%`), `uph_wifi0/set_multiq=3`, `ACBKMinfree=64`, `ACBEMinfree=32`, `ACVIMinfree=16`, `ACVOMinfree=0`, `vow_extstats=0`.
- **ARP/Multicast Cache Pinning** (`Linux`): `net.ipv4.neigh.default.gc_stale_time=120`, `net.ipv4.neigh.default.gc_thresh1=256`, `net.ipv4.igmp_max_memberships=32` to eliminate broadcast ARP re-resolution storms across the 2.4 GHz bridge.
- **UDP/ICMP Micro-Burst Pacing & NAPI Drainage** (`Linux`): `net.ipv4.icmp_ratelimit=100`, `net.core.dev_weight=96`, `net.core.netdev_budget=600`, `net.ipv4.tcp_limit_output_bytes=65536`, and `eth0`/`ath0` `txqueuelen=192`.
- **Safety Boundaries**: `45s` Non-DFS rollback watchdog armed per candidate window; strictly RAM-only (`0` flash writes); **NEVER** touches `.241`, `.242`, or `.250`.

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Design
| Window | Arm | `uph_wifi0` (`daprot` / `mcast_limit`) | ARP Pinning (`gc_stale_time` / `thresh1`) | NAPI / Pacing (`dev_weight` / `budget` / `txq`) | Watchdog |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `W1_A1` | `A_stock_baseline` | `2` / `10%` | `60s` / `128` | `64` / `300` / `1000` | `45s` |
| `W2_B1` | `B_round7_24ghz_noise_cochannel_candidate` | `2` / `4%` | `120s` / `256` | `96` / `600` / `192` | `45s` |
| `W3_A2` | `A_stock_baseline` | `2` / `10%` | `60s` / `128` | `64` / `300` / `1000` | `45s` |
| `W4_B2` | `B_round7_24ghz_noise_cochannel_candidate` | `2` / `4%` | `120s` / `256` | `96` / `600` / `192` | `45s` |

## 3. Five-Pillar Traceability
1. **Pillar A (Binary RE)**: `ubnt_poll_host.ko`, `umac.ko`, and `ath_dev.ko` symbols (`uph_wifi0/daprot`, `uph_wifi0/ff_mcast_airtime_limit`, `neigh_periodic_work`).
2. **Pillar B (Closed-Loop Research)**: Grounded in `tools/research/closed_loop_research_reactor.py` on 2.4 GHz co-channel contention CCA immunity and ARP neighbor pinning.
3. **Pillar C (Karpathy Autoresearch Harness)**: Counterbalanced `A1 -> B1 -> A2 -> B2` schedule with `45s` watchdog (`artifacts/autoresearch/stage336a_live_2xc253_round7_autoresearch.json`).
4. **Pillar D (Scientific Skills)**: `experimental-design`, `statistical-analysis`, `pymoo`, `scientific-critical-thinking`.
5. **Pillar E (`memory-master`)**: Durable claim tag `STAGE-336A-2XC253-ROUND7-24GHZ-NOISE-COCHANNEL` under `scope="project:futuramax"`.

## 4. Verification Artifacts
- Script: [`tools/benchmarks/run_stage336a_live_2xc253_round7_autoresearch.py`](../tools/benchmarks/run_stage336a_live_2xc253_round7_autoresearch.py)
- Receipt: [`artifacts/autoresearch/stage336a_live_2xc253_round7_autoresearch.json`](../artifacts/autoresearch/stage336a_live_2xc253_round7_autoresearch.json)
- Test Suite: [`tests/test_stage336a.py`](../tests/test_stage336a.py)
