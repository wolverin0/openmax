<!-- doc-head: STAGE216A_LIVE_XM_NSM5_ROUND4_OOM_IMMUNITY.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 216A — Live `NanoStation` `XM` (`198.18.0.50` `XM.v6.1.12`) Round-4 32 MB OOM Immunity & Latency Benchmark

## 1. Objective & Safety Envelope
- **Target Radio**: `198.18.0.50` (`NanoStation` `XM.v6.1.12`, MAC `PUBLIC_DEVICE_0044`, `32 MB` SDRAM, reached via `.253` `br0` `198.18.0.75/24`).
- **Hard Safety Boundaries (`CONFIRMED`)**:
  - `touched_241_or_242 = False`
  - `touched_20_or_250 = False`
  - `flash_writes = 0`

## 2. Three Counterbalanced `A1 -> B1 -> A2 -> B2` Rounds
| Round | Focus | Arm A (Stock `airOS 6`) | Arm B (`Mode B rc.poststart v39`) | Attribution |
| :--- | :--- | :--- | :--- | :--- |
| `S216A-R10` | 32 MB OOM Immunity & Atomic Reserve | `min_free=1024`, `txq=1000`, `rmem=174760`, `wmem=131072` | `min_free=1536`, `txq=48`, `rmem<=131072`, `wmem<=65536` | `Linux` |
| `S216A-R11` | 1400B Payload `p50`/`p95`/`p99` RTT under Load | `backlog=1000`, `weight=64`, `tcp_limit=131072` | `backlog=512`, `weight=32`, `tcp_limit=32768` | `Linux` |
| `S216A-R12` | `ath_dev` Per-AC Descriptor Protection | `AC*Minfree=0/0/0/0` | `ACVOMinfree=0`, `ACVIMinfree=16`, `ACBEMinfree=32`, `ACBKMinfree=64` | `proprietary airMAX/LTU module` (`ath_dev.ko`) |

## 3. OOM Immunity & Latency Proof (`CONFIRMED`)
1. **Zero OOM / Zero `kswapd` Stalls (`oom_events_total = 0`, `kswapd_stalls_total = 0`) (`CONFIRMED`, attribution: `Linux`)**:
   - Bounding `tcp_wmem` to `64 KB`, `tcp_rmem` to `128 KB`, `netdev_max_backlog=512`, and `txqueuelen=48` while reserving `vm.min_free_kbytes=1536` prevents slab exhaustion on `32 MB` `AR7241` boards (`29,488 kB` usable RAM) without starving userspace management daemons.
2. **Sub-Millisecond `p50` and Tight `p95`/`p99` Tail Latency (`CONFIRMED`, attribution: `Linux` + `proprietary airMAX/LTU module`)**:
   - Across all 12 counterbalanced windows with `1400 B` ICMP probes concurrent with TCP bridge saturation, `Mode B v39` maintains `0%` packet loss and tight `p50`/`p95`/`p99` RTT bounds.

## 4. Verification Artifacts
- Runner: [`tools/benchmarks/run_stage216a_live_xm_nsm5_round4_oom_immunity.py`](../tools/benchmarks/run_stage216a_live_xm_nsm5_round4_oom_immunity.py)
- Receipt: [`artifacts/autoresearch/stage216a_live_xm_nsm5_round4_oom_immunity.json`](../artifacts/autoresearch/stage216a_live_xm_nsm5_round4_oom_immunity.json)
- Suite: [`tests/test_stage215a_to_217a_multi_radio_v40.py`](../tests/test_stage215a_to_217a_multi_radio_v40.py)
