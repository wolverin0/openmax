<!-- doc-head: STAGE291A_LTU_5ROUND_CHAMPION_V3.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 291A: Consolidated 5-Round Live LTU-Lite (`.110`) Safe Linux Champion v3

## 1. Provenance & Safety (`CONFIRMED` — Attribution: `Linux` / `hardware`)
- **Script**: `firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh` (v3, SHA-256 `8181d67ad0ef17674d4b03ced5b3c375f49f1828874fc3bfdf99c9636666b2e8`).
- **Live Validation**: Consolidates 5 full autoresearch campaigns (`Stage 185A`, `Stage 188A`, `Stage 218A`, `Stage 247A`, `Stage 287A` = `15` counterbalanced `A1 -> B1 -> A2 -> B2` rounds / `60` live measurement windows on `198.18.0.63`).
- **Safety Guarantee**: `0` touches on `/dev/ame*`; `0` touches on `.241`, `.242`, `.20`, or `.250`.

## 2. Consolidated v3 Parameter Table
| Campaign | Validated Parameters in `rc.poststart_ltu_safe_champion.sh` v3 |
| :--- | :--- |
| **Round 1 (`S185A`)** | `IRQ 52 -> CPU1 (2)`, `IRQ 63 -> CPU0 (1)`, `eth0 RPS/XPS=1`, `ath0 RPS/XPS=2`, `BQL limit_max=36288` |
| **Round 2 (`S188A`)** | `netdev_budget=480`, `dev_weight=48`, `somaxconn=512`, `optmem_max=65536`, `tx_queue_len=256` |
| **Round 3 (`S218A`)** | `vm.min_free_kbytes=4096`, `tcp_limit_output_bytes=65536`, `tcp_notsent_lowat=16384` |
| **Round 4 (`S247A`)** | `tcp_pacing_ca_ratio=120`, `ss_ratio=200`, `multicast_snooping=0`, `nf_conntrack_max=16384`, `fq_codel 1514B/2.5ms` |
| **Round 5 (`S287A`)** | `rmem_default=262144`, `wmem_default=262144`, `netdev_max_backlog=3000`, `tcp_tw_reuse=1`, `rps_sock_flow_entries=4096`, `rps_flow_cnt=2048` |
