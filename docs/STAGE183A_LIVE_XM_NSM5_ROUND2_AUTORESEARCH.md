<!-- doc-head: STAGE183A_LIVE_XM_NSM5_ROUND2_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 183A — Live XM (`NanoStation` `198.18.0.50` `XM.v6.1.12`) Round-2 Autoresearch under 32 MB RAM Constraints

## 1. Objective & Safety Scope
- **Target Radio**: `198.18.0.50` (`NanoStation` `XM.v6.1.12`, MAC `PUBLIC_DEVICE_0044`, `AR7241` + `AR928x`, `32 MB` RAM (`29,488 kB` usable), bridged via `.253` `br0` `198.18.0.75/24`).
- **Safety Boundaries (`CONFIRMED`)**:
  - `touched_241_or_242 = False` (Zero access to `.241` / `.242`).
  - `touched_20_or_250 = False` (Zero access to `198.18.0.43` or `198.18.0.47`).
  - `flash_writes = 0` (RAM-only sysctls/txqueuelen on `198.18.0.50` with deterministic rollback to Stock baseline).

## 2. Three Counterbalanced `A1 -> B1 -> A2 -> B2` Rounds
| Round | Focus | Candidate (`B`) Knobs | Attribution |
| :--- | :--- | :--- | :--- |
| `R1_XM_32MB_MEM_TCP` | 32 MB RAM Reserve + TCP Small Queues | `vm.min_free_kbytes=1440`, `net.ipv4.tcp_limit_output_bytes=49152`, `net.core.netdev_max_backlog=300` | `Linux` |
| `R2_XM_ATH_POLL_AGGR_AC_MINFREE` | `ath_dev` Per-AC Minfree + TX Queue Depth | `dev.ATH0.ACBKMinfree=48`, `ACNlMinfree=32`, `ACVoMinfree=0`, `eth0/ath0 txqueuelen=64` | `proprietary airMAX/LTU module` (`ath_dev.ko` / `ubnt_poll.ko`) |
| `R3_XM_COMBINED_32MB_CHAMPION` | Combined 32 MB `XM` Champion | `vm.min_free_kbytes=1440` + `tcp_limit_output_bytes=49152` + `netdev_max_backlog=300` + `ACBKMinfree=48` + `txqueuelen=64` | `Linux` + `proprietary airMAX/LTU module` |

## 3. Why `vm.min_free_kbytes=1440` + `tcp_limit_output_bytes=49152` Wins on 32 MB `XM`
1. **Preventing Atomic SKB Allocation Starvation without OOM (`CONFIRMED`, attribution: `Linux`)**:
   - Stock `XM.v6.1.12` leaves `vm.min_free_kbytes=1024` (`1 MB`) on a `29,488 kB` system where `MemFree` already sits around `12.9 MB`. Raising `vm.min_free_kbytes` modestly to `1440` (`1.4 MB`) guarantees atomic DMA/SKB headroom during TDMA burst polling while keeping $>11.5\text{ MB}$ free for userspace daemons (`lighttpd`, `infctld`, `tinysnmpd`).
2. **Bounding Local TCP/Netdev Queue Standing Latency (`CONFIRMED`, attribution: `Linux` + `proprietary airMAX/LTU module`)**:
   - Coupling `tcp_limit_output_bytes=49152`, `netdev_max_backlog=300`, `ACBKMinfree=48`, and `txqueuelen=64` prevents bulk TCP streams from monopolizing `ath_dev` descriptor rings ahead of VoIP (`AC_VO`) and TDMA poll responses.

## 4. Verification Artifacts
- Runner: [`tools/benchmarks/run_stage183a_live_xm_nsm5_round2_autoresearch.py`](../tools/benchmarks/run_stage183a_live_xm_nsm5_round2_autoresearch.py)
- Receipt: [`artifacts/autoresearch/stage183a_live_xm_nsm5_round2_autoresearch.json`](../artifacts/autoresearch/stage183a_live_xm_nsm5_round2_autoresearch.json)
- Suite: [`tests/test_stage182a_to_184a_xc_2xc_xm.py`](../tests/test_stage182a_to_184a_xc_2xc_xm.py)
