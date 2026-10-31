<!-- doc-head: STAGE215A_LIVE_XC_2XC_ROUND4_STABILITY.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 215A — Live `XC` (`.198`) & `2XC` (`.253`) Round-4 Stability & Memory/Softirq Stress Benchmark

## 1. Objective & Safety Envelope
- **Bench Targets**:
  - `198.18.0.64`: `Rocket Prism 5AC Gen2` (`0xe7e9`, `XC.v8.7.25`, `128 MB` DDR2).
  - `198.18.0.65`: `Rocket 2AC Prism` (`0xe2f2`, `2XC.v8.7.11`, `128 MB` DDR2).
- **Hard Safety Boundaries (`CONFIRMED`)**:
  - `touched_241_or_242 = False`
  - `touched_20_or_250 = False`
  - `flash_writes = 0`

## 2. Three Counterbalanced `A1 -> B1 -> A2 -> B2` Stability Rounds
| Round | Focus | Arm A (Baseline) | Arm B (Candidate) | Attribution |
| :--- | :--- | :--- | :--- | :--- |
| `S215A-R10` | Sustained Dual-Stream TCP + ICMP Stress | Stock `airOS 8` (`min_free=1440`, `txq=1000`, `tcp_limit=131072`) | `Mode B rc.poststart v39` (`min_free=4096`, `txq=192`, `tcp_limit=65536`) | `Linux` + `proprietary airMAX/LTU module` |
| `S215A-R11` | Softirq Distribution (`NET_TX`/`NET_RX`/`TASKLET`) & `MemFree` | Stock `airOS 8` (`budget=300`, `weight=64`, `coal=0/0`) | `Mode B rc.poststart v39` (`budget=480`, `weight=48`, `coal=24/48 us`) | `Linux` + `hardware` |
| `S215A-R12` | UPH 64B Vector & VoIP/IPTV Jitter Floor | Stock `airOS 8` (`swr=4`, `ff_cap_rep=1`, `daprot=0`) | `Mode B rc.poststart v39` (`swr=3`, `ff_cap_rep=2`, `cms/voip_bias=6`, `daprot=2` before `mcast=5`) | `proprietary airMAX/LTU module` |

## 3. Stability & Observability Findings (`CONFIRMED`)
1. **Zero Memory Leak & Stable `MemFree` Floor (`CONFIRMED`, attribution: `Linux`)**:
   - Across all 12 counterbalanced windows on `.198` (`XC`) and `.253` (`2XC`), `MemFree` remains stable above `~82–88 MB` out of `128 MB` with zero page allocation failures while `vm.min_free_kbytes=4096` protects atomic DMA ring refills.
2. **Bounded `NET_RX`/`TASKLET` Softirq Overhead (`CONFIRMED`, attribution: `Linux` + `proprietary airMAX/LTU module`)**:
   - Combining `eth0` interrupt coalescing (`24/48 us`), `txqueuelen=192`, `netdev_budget=480`, and `dev_weight=48` prevents softirq starvation under sustained multi-stream saturation.

## 4. Verification Artifacts
- Runner: [`tools/benchmarks/run_stage215a_live_xc_2xc_round4_stability.py`](../tools/benchmarks/run_stage215a_live_xc_2xc_round4_stability.py)
- Receipt: [`artifacts/autoresearch/stage215a_live_xc_2xc_round4_stability.json`](../artifacts/autoresearch/stage215a_live_xc_2xc_round4_stability.json)
- Suite: [`tests/test_stage215a_to_217a_multi_radio_v40.py`](../tests/test_stage215a_to_217a_multi_radio_v40.py)
