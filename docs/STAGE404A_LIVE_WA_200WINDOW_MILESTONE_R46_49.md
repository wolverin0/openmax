<!-- doc-head: STAGE404A_LIVE_WA_200WINDOW_MILESTONE_R46_49.md preserved document content -->
<!-- /doc-head -->


# Stage 404A — Live `WA` **`200`-Window Milestone** (`R46..R49`): Per-TID AQL, TCP Compressed SACK, Multicast Querier & Champion `v8`

## 1. Executive Summary (`CONFIRMED`)
- **Stage ID**: `Stage 404A` (`S404A-R46..R49`)
- **Historic Milestone**: Reached **`200` cumulative live hardware windows (`49` counterbalanced RF rounds = `196` RF windows + `4` Stage 162A E2E windows; `212` including E2E-R2..R4)** on `OpenWrt 24.10.4` `WA` (`AR9342` + `QCA9882` `ath10k-ct`).
- **All 4 Rounds Promoted `Arm B` (`4/4` `PROMOTE_ARM_B`)**:
  - `S404A-R46`: Tight per-TID `aql_txq_limit` (`VO=300/600 us`, `BE=1500/2500 us`, `Pareto +6.80%`).
  - `S404A-R47`: Fast TCP Compressed SACK (`tcp_comp_sack_delay_ns=250000`, `tcp_comp_sack_nr=16`, `Pareto +7.97%`).
  - `S404A-R48`: Bridge `multicast_querier=1` + `multicast_snooping=1` + `multicast_to_unicast=1` (`FMX-DISC-36` safe sysfs path, `Pareto +11.08%`, **`-32.73%` `p50` RTT**).
  - `S404A-R49`: `49`-Round `200`-Window Universal `WA` Champion `v8` vs Stock `OpenWrt 24.10.4` (`Pareto +2.36%`, **`-43.03%` `p95` RTT**).
- **Primary Artifact**: [`artifacts/autoresearch/stage404a_live_wa_200window_milestone_r46_49.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage404a_live_wa_200window_milestone_r46_49.json)

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Results (`R46..R49`)

| Round | Knob Under Test (`Arm A` vs `Arm B`) | Arm A Goodput (`Mbps`) | Arm B Goodput (`Mbps`) | Arm A `p50` / `p95` (`ms`) | Arm B `p50` / `p95` (`ms`) | Arm A / B Jitter (`ms`) | Decision & Attribution |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`S404A-R46`** | Per-TID `aql_txq_limit`: `VO=600/1200, BE=3000/4000` vs `VO=300/600, BE=1500/2500` | `58.499` | `56.941` (`58.267` in `B2`) | `25.503` / `73.653` | **`22.246`** (`-12.77%`) / **`65.961`** (`-10.44%`) | `2.748` / **`1.990`** (`-27.58%`) | **`PROMOTE_ARM_B`** (`Pareto +6.80%`; `mac80211` per-AC airtime bounding) |
| **`S404A-R47`** | `tcp_comp_sack_delay_ns` / `nr`: `1 ms / 44` vs `250 us / 16` | `55.544` | **`57.992`** (`+4.41%`, `58.733` in `B2`) | `21.373` / `70.078` | `23.950` / **`69.419`** | `2.131` / `2.135` | **`PROMOTE_ARM_B`** (`Pareto +7.97%`; `Linux` TCP faster SACK loss recovery on A-MPDU) |
| **`S404A-R48`** | `br-lan` `multicast_querier`: `0` vs `1` (`FMX-DISC-36` Safe Sysfs Path) | `56.898` | **`57.857`** (`58.121` in `B1`) | `24.654` / `60.355` | **`16.585`** (**`-32.73%`**) / **`53.686`** (`-11.05%`) | `2.467` / **`1.938`** (`-21.44%`) | **`PROMOTE_ARM_B`** (`Pareto +11.08%`; `Linux` `bridge.ko` MDB group state maintenance) |
| **`S404A-R49`** | Stock `OpenWrt 24.10.4` (`Arm A`) vs **`200`-Window `WA` Champion `v8` (`Arm B`)** | `68.398` | `64.114` (`65.750` in `B2`) | `22.298` / `99.292` | **`18.183`** (`-18.45%`, `13.923` in `B2`) / **`56.570`** (**`-43.03%`**, `49.561` in `B1`) | `1.464` / `3.647` | **`PROMOTE_ARM_B`** (`Pareto +2.36%`; full-stack `v8` tail-latency suppression) |
