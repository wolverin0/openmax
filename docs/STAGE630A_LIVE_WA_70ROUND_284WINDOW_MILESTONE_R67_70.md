<!-- doc-head: STAGE630A_LIVE_WA_70ROUND_284WINDOW_MILESTONE_R67_70.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 630A — Live WA `70`-Round / `284`-Window Milestone (`R67..R70`): UDP Floor, Bridge Ageing, TCP Churn & `WA Champion v11`

- **Claim Classification**: `CONFIRMED`
- **Subsystem Attribution**: `QCA firmware`, `ath10k`, `mac80211`, `Linux` (`net/ipv4/udp.c`, `net/bridge/br_fdb.c`, `net/ipv4/tcp_timer.c`), `hardware` (`AR9342` + `QCA9882`)
- **Safety Boundaries**: `198.18.0.45` and `198.18.0.46` untouched (`touched_241_or_242 = false`); `0` flash writes.

---

## 1. Executive Summary (`R67..R70` = `70` Rounds / `284` Cumulative Live Windows!)

`Stage 630A` completes rounds `R67..R70`, reaching **`70` counterbalanced rounds = `280` RF windows + `4` `Stage 162A` E2E windows = `284` cumulative live windows** (`308` including all 7 E2E rounds):

| Round | Hypothesis / Arm Comparison | Arm A Goodput / `p50` / `p95` | Arm B Goodput / `p50` / `p95` | Pareto $\Delta$ | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`S630A-R67`** | `udp_rmem_min=4096, udp_wmem_min=4096` vs `16384 / 16384` | `70.593 Mbps` / `18.142 ms` / `67.716 ms` | `67.770 Mbps` / `23.733 ms` / `70.644 ms` (VoIP jitter `2.461 -> 2.350 ms`) | `-6.89%` | `RETAIN_ARM_A` |
| **`S630A-R68`** | Bridge `snooping=0, querier=0` vs `ageing=30000, snooping=1, querier=1` | `67.957 Mbps` / `20.272 ms` / `48.844 ms` | **`70.399 Mbps`** (`+3.59%`) / `22.236 ms` / `58.745 ms` | `-5.09%` | `RETAIN_ARM_A` |
| **`S630A-R69`** | `tcp_max_orphans=2048, fin_timeout=60` vs `4096, fin_timeout=15, keepalive=300` | `66.391 Mbps` / `19.678 ms` / `57.556 ms` | **`67.637 Mbps`** (`+1.88%`) / `19.965 ms` / **`46.445 ms`** (`-19.30%`) | **`+14.77%`** | **`PROMOTE_ARM_B`** (VoIP jitter `2.966 -> 1.943 ms`) |
| **`S630A-R70`** | **Stock `OpenWrt 24.10.4` vs `70`-Round (`284`-Window) `WA Champion v11`** | `58.207 Mbps` / `93.068 ms` / `159.311 ms` | **`70.719 Mbps`** (**`+21.50%`**) / **`22.349 ms`** (**`-75.99%`**) / **`97.732 ms`** (**`-38.65%`**) | **`+325.42%`** | **`PROMOTE_ARM_B`** |

---

## 2. Key Findings (`S630A-R70` `284`-Window Head-to-Head)

1. **Goodput Surge**: `+21.50%` (`58.207 -> 70.719 Mbps`, peaking at **`72.333 Mbps`** in `B2`) under simultaneous bidirectional TCP + IPTV (`5 Mbps` `AF41`) + VoIP (`G.711` `EF`) + Gaming UDP.
2. **Latency Collapse**: Under-load `p50` RTT drops **`-75.99%`** (`93.068 -> 22.349 ms`, reaching `16.724 ms` in `B2`) and `p95` RTT drops **`-38.65%`** (`159.311 -> 97.732 ms`).
3. **VoIP Jitter Reduction**: VoIP jitter drops `-26.90%` (`3.622 -> 2.648 ms`, `0%` loss).

---

## 3. Artifacts & Verification

- JSON Receipt: [`stage630a_live_wa_70round_284window_milestone_r67_70.json`](../artifacts/autoresearch/stage630a_live_wa_70round_284window_milestone_r67_70.json)
- Runner: [`run_stage630a_live_wa_70round_284window_milestone_r67_70.py`](../tools/autoresearch/run_stage630a_live_wa_70round_284window_milestone_r67_70.py)
- Test Suite: [`test_stage630a.py`](../tests/test_stage630a.py)
