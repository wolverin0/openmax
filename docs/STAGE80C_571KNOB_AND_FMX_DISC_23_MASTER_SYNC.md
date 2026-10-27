<!-- doc-head: STAGE80C_571KNOB_AND_FMX_DISC_23_MASTER_SYNC.md preserved document content -->
<!-- /doc-head -->



# Stage 80C — Updated 571-Knob Coverage Ledger & `FMX-DISC-21..23` Master Sync (`Stages 73A–79B`)

- **Status**: `CONFIRMED`
- **Task ID**: `T-S80C-UPDATED-571KNOB-COVERAGE-LEDGER-AND-FMX-DISC-21-22-CURATION`
- **Sync Implementation**: [`run_stage80c_571knob_and_discoveries_v23_sync.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/research/run_stage80c_571knob_and_discoveries_v23_sync.py)
- **Receipt Artifact**: [`stage80c_571knob_and_discoveries_v23_sync_20261026.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage80c_571knob_and_discoveries_v23_sync_20261026.json)
- **Unit Test Suite**: [`test_stage80c_571knob_and_discoveries_v23_sync.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_stage80c_571knob_and_discoveries_v23_sync.py)

---

## 1. Curated Discoveries `FMX-DISC-21` through `FMX-DISC-23` (`CONFIRMED`)

| Discovery ID | Stages | Layer Attribution | Core Physical Mechanism & Empirical Law |
| :--- | :---: | :--- | :--- |
| **`FMX-DISC-21`** | `74A`, `76B`, `77B`, `79A` | `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`), `Linux` | **1) `atpc` 5th-Integer `def_power=24` Contract (`0 0 0 0 24`) & `timing='0 0 0' -> 200/200/6000` (`200 200 5000`)**: `/proc/sys/dev/uph_wifi0/atpc` parses a 5-integer vector where the 5th integer is `def_power=24` (`0 0 0 0 24`); writing only 4 integers drops default TX power. `timing='0 0 0'` resolves internally to `200/200/6000` us while `'200 200 5000'` bounds max TXOP in PtP `v7`.<br>**2) Asymmetric CPU-Class NAPI Scaling Law (`Stage 76B`)**: `QCA9558 XC` (`720 MHz` `MIPS 74Kc`) sustains `netdev_budget=800`, whereas `AR9342 WA` (`535 MHz` `MIPS 74Kc`) saturates its softirq time slice above `netdev_budget=600`. |
| **`FMX-DISC-22`** | `76B` | `Linux`, `mac80211`, `proprietary airMAX/LTU module` | **OpenWrt BusyBox `ping -i <float>` Silent Rejection & `seq 1 25` `1200B` Per-Window Rate-Control Warmup Law**: OpenWrt 24.10 BusyBox `ping` rejects fractional sub-second intervals (`ping -i 0.05` exits without sending probes), requiring `for i in $(seq 1 25); do ping -c 1 -W 1 -s 1200 <ip> & done` before every counterbalanced window (`A1`, `B1`, `A2`, `B2`) so `802.11n XW` `ath_rate_atheros` stays warmed at `MCS3–MCS4` instead of decaying to `MCS0 (6.5 Mbps)`. |
| **`FMX-DISC-23`** | `75A`, `78B`, `79A`, `79B` | `proprietary airMAX/LTU module` (`umac.ko`, `ath_dev.ko`) | **`UMAC-BUG-01..05` & `ATHDEV-BUG-01..04` + `iwpriv ath0 set_multiq 3` (`0x1 | 0x2`) (`Stage 79A PtP Champion v7` `S79A-R1`)**: Static `/fullrea` dissection of `umac.ko` and `ath_dev.ko` proved `set_multiq` is a 2-bit bitmask (`0x1` = 5-subqueue per-AC XOFF backpressure; `0x2` = deep `802.1Q VLAN` + `PPPoE 0x8864` inner IPv4/IPv6 DSCP parser). Enabling `set_multiq=3` (`0x1 | 0x2`) in `Stage 79A` (`S79A-R1`) promoted **`PtP Champion v7`**: **`+5.33%` Aggregate Goodput**, **`+9.77%` Bulk TCP**, **`-29.76%` `p95` RTT**, **`-31.98%` `p99` RTT**, and **`-35.16%` VoIP loss**. |

---

## 2. Master 571-Knob Coverage Ledger Summary (`Stages 60A–79B`, `CONFIRMED`)

- **Immutable Catalog**: [`orchestration/autoresearch/firmware_knob_candidates.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/orchestration/autoresearch/firmware_knob_candidates.json) (`571` knobs, `SHA-256: 54cdcc8213bfdc8e909c0daae236c48a930a739bbe57153de619f6a7cd3a2f8a` verified byte-intact).
- **Evaluated Knob Groups (`Stages 60A–79B`)**: `14` distinct functional knob groups covering `41` direct catalog IDs across `WA`, `XC`, `XW`, and `AF-LTU`.
- **Synchronized Core Docs (`< 220` Lines Each, Single ``)**:
  - [`CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/docs/CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md) (`111` lines; `FMX-DISC-01..23` + `Champion v1..v20` + `PtP v4..v7`)
  - [`MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md) (`186` lines)
  - [`CURRENT_STATE.md`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/docs/CURRENT_STATE.md) (`191` lines)

---

## 3. Five-Pillar Compliance Summary (`5/5 PASS`)

- **Pillar A**: Reconciles all `571` knobs + `UMAC-BUG-01..05` + `ATHDEV-BUG-01..04` + `FMX-DISC-21..23`.
- **Pillar B**: Synced to `ClosedLoopResearchReactor` (`discovery_to_research_queue.json`).
- **Pillar C**: All empirical promotions (`Champion v20`, `PtP v6`, `PtP v7`) verified under `A1 -> B1 -> A2 -> B2` with `45s` rollback watchdog.
- **Pillar D**: Integrates `Stage 75B` NSGA-II Pareto, `Stage 76A` SimPy 32-CPE Guarida simulation, and `Stage 77A/78A` `aeon` regime classification.
- **Pillar E**: Durable MemoryMaster claim `mm-stage80c-571knob-and-discoveries-v23-sync-20261026` synced to `memorymaster.db`.
