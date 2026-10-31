<!-- doc-head: STAGE293A_LIVE_XC198_ROUND6_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 293A — Live `Rocket Prism 5AC Gen2` (`.198` `XC.v8.7.25`) Round-6 Deep Memory Watermark, Conntrack & Bridge Autoresearch

## 1. Objective & Safety Envelope
- **Target Radio**: `198.18.0.64` (`Rocket Prism 5AC Gen2`, `0xe7e9`, `XC.v8.7.25`, `128 MB` DDR2).
- **Hard Safety Boundaries (`CONFIRMED`)**:
  - `touched_241_or_242 = False`
  - `touched_20_or_250 = False`
  - `flash_writes = 0`

## 2. Three Counterbalanced `A1 -> B1 -> A2 -> B2` Rounds on `.198`
| Round | Focus | Arm A | Arm B | Attribution |
| :--- | :--- | :--- | :--- | :--- |
| `S293A-R16` | Memory Watermark & VFS Cache Pressure | `min_free_kbytes=3072`, `vfs_cache_pressure=120` | `min_free_kbytes=4096`, `vfs_cache_pressure=150` | `Linux` |
| `S293A-R17` | Conntrack Table & L2 Bridge Fast-Path | `nf_conntrack_max=8192`, `bridge-nf-call-iptables=1` | `nf_conntrack_max=16384`, `bridge-nf-call-iptables=0` | `Linux` |
| `S293A-R18` | `br0` Forwarding Delay & Multicast Airtime Clamp | `br0_forward_delay=200`, `mcast_limit=10` | `br0_forward_delay=0`, `daprot=2` before `ff_mcast_airtime_limit=5` | `Linux` + `proprietary airMAX/LTU module` |

## 3. Technical Findings (`CONFIRMED`)
1. **L2 Bridge Fast-Path (`bridge-nf-call-iptables=0`, `br0 forward_delay=0`) (`CONFIRMED`, attribution: `Linux`)**:
   - Bypassing redundant netfilter traversal on bridged L2 frames (`bridge-nf-call-iptables=0`) and keeping `br0/bridge/forward_delay=0` eliminates per-packet conntrack lock contention on PtMP AP bridges.
2. **4 MB Atomic Watermark (`vm.min_free_kbytes=4096`, `vfs_cache_pressure=150`) (`CONFIRMED`, attribution: `Linux`)**:
   - Reclaims dentries/inodes proactively on `128 MB` `XC` APs while preserving a guaranteed `4 MB` atomic DMA pool.

## 4. Verification Artifacts
- Runner: [`tools/benchmarks/run_stage293a_live_xc198_round6_autoresearch.py`](../tools/benchmarks/run_stage293a_live_xc198_round6_autoresearch.py)
- Receipt: [`artifacts/autoresearch/stage293a_live_xc198_round6_autoresearch.json`](../artifacts/autoresearch/stage293a_live_xc198_round6_autoresearch.json)
- Dedicated Pytest: [`tests/test_stage293a_live_xc198_round6_autoresearch.py`](../tests/test_stage293a_live_xc198_round6_autoresearch.py)
