<!-- doc-head: FuturaMAX Master Multi-Lane (Codex + AGY1 + AGY2) Reconciliation Ledger -->
Active authoritative curation document (<250 lines) establishing per-hardware champions,
Codex verifier findings (Stages 38B..47B), 571-knob catalog reconciliation, and unmerged deploy fixes.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Master Multi-Lane (Codex + AGY1 + AGY2) Reconciliation Ledger

Generated: `2026-10-26T04:18:00Z` | Authority: Flash Curator #2 (`3e19d6cd`) | Status: `RECONCILED`

## 1. Multi-Lane Task Board Census & Fleet Roster Audit
Audited `docs/MULTI_AGENT_TASK_BOARD.md` and `artifacts/orchestration/agent_task_board.json`:
- **Total Registered Tasks**: `136` tasks across all agents:
  - `codex:<orca-id>` (Offline Verifier & Autoresearch Matrix): `17` tasks (`T-CODEX-01`, `T-PB-CODEX-01..05`, `T-AUTO-CODEX-01`, `T-S37B`..`T-S47B`).
  - `subagent:bench-runner` / `subagent:multiradio-autoresearch` (`AGY1` Live Bench Runner): `78` tasks (`T-BENCH-01..12`, `T-S27..T-S65A`).
  - `orca:gemini-lane1` & `orca:gemini-lane2` (`AGY2` Controllers & Deploy Packager): `41` tasks (`T-ORCA-GEM*`, `T-PB-GEM*`, `T-S48B..T-S64A`).

---

## 2. Complete Per-Hardware Champion & Discovery Matrix

| Hardware & Topology | Previously in `deploy_packager.py` | Discovered Champion (Stages 1–64A) | Confirmed Real-World Gains | Refuted Knobs & Safety Invariants | Reconciliation Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **OpenWrt PtMP** (`LAP-120` AP + `Loco5AC` WA + `Rocket5AC` XC + `LiteBeamM5` XW) | **Champion v18** (`limit_min=4542`, `limit_max=42392`, `hold_time=1000` ms, `dev_weight_tx_bias=2`) | **Stage 55A Champion v19** (`M34b`: `hold_time=800` ms, `limit_min=4542` 3×MTU, `limit_max=42392` 28×MTU, `dev_weight_tx_bias=2`, `fq_quantum=4542`, `fq_memory_limit=4MB`, `hostapd oom_score_adj=-900`) | **`+6.539%` GP** (`40.56->43.21 Mbps`), **`p95` RTT `< 82 ms`** (`85.54->81.66 ms`, `-4.54%`), **`p99` RTT `-7.24%`** (`90.75->84.18 ms`), `0.00%` IPTV/VoIP loss | `hold_time=600` ms inflates `p95` (`+6.56%`); `AC_VI` AQL (`2000/3500`) > `AC_BE` causes `-21.17%` GP drop; `netdev_budget_usecs < 20000` returns `-EINVAL` on `HZ=100` | **MERGE INTO PACKAGER**: Upgrade `deploy_packager.py` from `v18` to `Champion v19` (`hold_time=800` ms + OOM/FQ memory guards) |
| **OpenWrt PtP** (`LAP-120` AP $\leftrightarrow$ `Loco5AC` STA / `PBE-5AC-Gen2`) | *Unseparated from PtMP* | **Stage 55A OpenWrt PtP Profile** (`M35`: `AC_BE=1500/3000` AP / `900/1500` CPE, `fq_quantum=4542`, `dev_weight_tx_bias=2`, `eth0` BQL `4542/42392/800ms`) | **`46.83–47.21 Mbps`** Triple-Play goodput, **`28.46 ms`** `p50` RTT, **`53.24 ms`** `p95` RTT, `0.0%` loss (`30.09 Mbps` on PBE dish, `+34.7%` vs `FF 5ms`) | PtP `BE=3000/6000` inflates `p95` (`+1.73%`); `fq_quantum=6056` (`4×MTU`) trims goodput (`-1.56%`) | **MERGE INTO PACKAGER**: Expose dedicated `STAGE55A_OPENWRT_PTP_PROFILE` |
| **airOS 8 WA PtP** (`PowerBeam 5AC Gen2` `.241` AP $\leftrightarrow$ `.242` STA OTA) | **Stage 54D** (`txq=192, ampdu=24, ack=25us, budget=600`) | **Stage 62A Champion v4** (`S62A-R2`: `set_multiq=1, aggr_swretry=6, nonaggr_swretry=8, enable_tx_tcp_cksum=1, netdev_budget=800, tcp_limit_output_bytes=98304` on top of `S60A-R3` `cwmin=3, cwmax=6, ampdu=32, RPS` + universal `cron` persistence) | **`+26.01%` Aggregate GP** (`20.33->25.62 Mbps`), **`+33.09%` Bulk TCP** (`12.68->16.88 Mbps`), Jain fairness `0.9986`, `0.00%` IPTV/VoIP loss | Pausing `ubntspecd` / bringing `wifi1` down (`S62A-R1`) drops TCP by `-21.28%` due to bridge flapping; `IRQ 33` is silicon-coupled to `wifi0` reception | **MERGE INTO PACKAGER**: Upgrade PtP profile in `deploy_packager.py` with `S60A-R3 + S62A-R2` (`+26.01%` GP) |
| **airOS 8 XC/WA PtMP** (`Rocket Prism 5AC Gen2` `.198` AP, Guarida Panel2/3) | Mode B (`cms_bias=6, voip_bias=6, daprot=2`), Panel3 `RTS=256B`/Soft-TDMA `K=3` | **Stage 44A Champion v15** + Stage 39A `voip_bias`/`ff_mcast` 16-int vector guard | `Rocket198` `br0/ath0/eth0 tx_queue_len=256` + `netdev_budget=600` unlocked **`+7.14%` GP**, `-3.62%` `p95`, `-12.86%` `p99` RTT | Setting `voip_bias` without `ff_mcast_airtime_limit` corrupts 16-int sysctl vector in `ubnt_poll_host.ko` | **VERIFIED**: Keep 16-int vector guard enforced |
| **airOS 6 XW/XM** (`PowerBeam M5 300` `.219/.220`, `LiteBeam M5` `.251`, `Loco M2`) | Stage 29B (`tx_chain=2, rx_chain=3, txop=15ms, ampdu=16f/16KB`) | **Stage 42A Champion v14** (`LiteBeam M5` `br0/ath0/eth0 txqueuelen 256`, `ewma_delegate=1`, `netdev_budget=600`) | Slashes loaded `p95` RTT by **`-7.92%`** (`104.43->96.16 ms`), IPTV jitter **`-12.36%`**, VoIP jitter **`-8.11%`** | `CONFIG_BRIDGE_IGMP_SNOOPING` absent on `XW`; unpolled `no_ack_rate=1` degrades GP by `-8.35%` | **VERIFIED** |
| **LTU PtP/PtMP** (`LTU-Lite` `198.18.0.61 <-> .2`, `LTU Rocket`) | Stage 48B/49B/50B (`ulpwrtune=-75`, `pb_boost=1`, `cpe_mcs 7..31`, `maxBD=0x5..0xa`, 3-tier HTB) | **Stage 63B + Stage 64A Ground-Up Champion** (SMP IRQ split, `gBDHandleOnce=84`, `autoMcsUpDown` fix, Level-6 `4096-QAM` scheduler unlock + `/fullrea` `ame_core_fmx.ko` & `ame_dev_fmx.ko` binary patches) | Slashes loaded `p95` RTT by **`-90.8%+`**, cuts BLER `37%->19%`, fixes `frame_len->duty_cycle` (`0x1236c`) & `adj_mcs=0x20` (`0x1919cc`) in binary | `echo 0 > maxBD` clobbers `gBDHandleOnce=0` (DMA stall); stock `autoMcsUpDown` collapses traffic to `QPSKl` via `90 1` bug | **MERGE INTO PACKAGER**: Upgrade LTU deploy package with Stage 63B + Stage 64A SHA-256 guarded binary patches |

---

## 3. Codex Offline Verifier Findings (`Stages 38B..47B`): Mandatory Harness Rules
1. **Stage 38B (`UPH 16-int vector`)**: Always write `voip_bias` and `ff_mcast_airtime_limit` together and verify full 16-int readback.
2. **Stage 39B / 43B / 45B / 47B (`Programmatic Report Tables`)**: Never hand-edit Markdown benchmark tables; generate all tables strictly from `fmx_objective.summary` and raw receiver JSON layers.
3. **Stage 40B (`Direct Sysfs Queue Writes`)**: Never use BusyBox `ip link set dev <if> txqueuelen` on OpenWrt 24.10; always write `/sys/class/net/*/tx_queue_len`.
4. **Stage 41B / 47B (`Kernel Boundaries & Dynamic BQL`)**: Keep OpenWrt `eth0 tx_queue_len=1000` (governed by dynamic BQL `limit_min=4542, limit_max=42392, hold_time=800` ms) and `netdev_budget_usecs=20000` (`CONFIG_HZ=100` minimum).
5. **Stage 45B (`Multi-CPE Zero-Starvation Gate`)**: Hard fail-stop any multi-CPE round if any associated station suffers `100%` packet loss.

---

## 4. 571-Knob Catalog Census (`42` Sources)
- **Tested / Mined in Live Benchmarks**: **`245` knobs (`42.9%`)**.
- **Untested Candidates Ready for Next Waves**: **`326` knobs (`57.1%`)**:
  - **OpenWrt `ath10k`**: `ct_special_7` (`RC_MAX_PER_THR`), `ct_special_10` (`RIFS_ENABLE`), `mac80211_wmm_txop_be_vi`, `wmi10_1_pdev_beacon_gen_mode`.
  - **airOS 8 `WA/XC`**: `fixed_frame`, `timing`, `sta_priority`, `swr_limit`, `ptp_xmit`.
  - **LTU `AME`**: `ofdma_en`, `ofdma_subbands`, `ldpc_iteration`, `adj_mix_mcs`.
