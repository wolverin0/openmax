<!-- doc-head: STAGE303A_LTU_6ROUND_CHAMPION_V4.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 303A: Consolidated 6-Round (`72`-Window) Live LTU-Lite (`.110`) Safe Linux Champion v4

## 1. Provenance & Safety (`CONFIRMED` — Attribution: `Linux` / `hardware`)
- **Script**: `firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh` (v4, SHA-256 `d2c9264407d0cc60a9d7a97d68473be08416d221b70d39d8e405446e96d543ab`).
- **Live Evidence**: Consolidates 6 live campaigns (`Stage 185A`, `Stage 188A`, `Stage 218A`, `Stage 247A`, `Stage 287A`, `Stage 299A` = `18` `A1 -> B1 -> A2 -> B2` rounds = `72` live measurement windows on `198.18.0.63`).
- **Safety Guarantee**: `0` touches on `/dev/ame*`; `0` touches on `.241`, `.242`, `.20`, or `.250`.

## 2. Consolidated v4 Parameter Summary
| Campaign | Validated Parameters in `rc.poststart_ltu_safe_champion.sh` v4 |
| :--- | :--- |
| **Round 1 (`S185A`)** | `IRQ 52 -> CPU1 (2)`, `IRQ 63 -> CPU0 (1)`, `eth0 RPS/XPS=1`, `ath0 RPS/XPS=2`, `BQL limit_max=36288` |
| **Round 2 (`S188A`)** | `netdev_budget=480`, `dev_weight=48`, `somaxconn=512`, `optmem_max=65536`, `tx_queue_len=256` |
| **Round 3 (`S218A`)** | `vm.min_free_kbytes=4096`, `tcp_limit_output_bytes=65536`, `tcp_notsent_lowat=16384` |
| **Round 4 (`S247A`)** | `tcp_pacing_ca_ratio=120`, `ss_ratio=200`, `multicast_snooping=0`, `nf_conntrack_max=16384` |
| **Round 5 (`S287A`)** | `rmem_default=262144`, `wmem_default=262144`, `netdev_max_backlog=3000`, `tcp_tw_reuse=1`, `rps_sock_flow_entries=4096` |
| **Round 6 (`S299A`)** | `udp_rmem_min=16384`, `udp_wmem_min=16384`, `ping_group_range="0 2147483647"`, `fq_codel target 2000us interval 40000us ecn` |
