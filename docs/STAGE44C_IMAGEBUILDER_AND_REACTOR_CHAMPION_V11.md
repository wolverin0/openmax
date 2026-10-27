<!-- doc-head: STAGE44C_IMAGEBUILDER_AND_REACTOR_CHAMPION_V11.md preserved document content -->
<!-- /doc-head -->

# Stage 44C: OpenWrt 24.10.4 ImageBuilder Champion v11 First-Boot AQM & Closed-Loop Research Reactor (`M22` / `M23`) Integration

## 1. Executive Summary (`CONFIRMED`)

- **Task ID**: `T-S44C-GEM2-IMAGEBUILDER-CHAMPION-V11-AND-CLOSED-LOOP-REACTOR-V11`
- **Modules Upgraded**:
  - [`firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py) (`render_uci_defaults_98_futuramax_champion_v11_aqm`, `generate_stage44c_imagebuilder_champion_v11_manifest`)
  - [`tools/research/closed_loop_research_reactor.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/research/closed_loop_research_reactor.py) (`ingest_stage37a_champion_v11_and_synthesize_m22_m23`)
- **Generated Artifacts**:
  - [`artifacts/autoresearch/stage44c_imagebuilder_champion_v11_manifest_20261025.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage44c_imagebuilder_champion_v11_manifest_20261025.json)
  - [`artifacts/autoresearch/stage44c_closed_loop_reactor_v11_ingestion_20261025.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage44c_closed_loop_reactor_v11_ingestion_20261025.json)

## 2. ImageBuilder First-Boot Champion v11 Integration (`files/etc/uci-defaults/98-futuramax-champion-v11-aqm`)

[`render_uci_defaults_98_futuramax_champion_v11_aqm()`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py#L469-L538) embeds `/etc/uci-defaults/98-futuramax-champion-v11-aqm` (`0755`) across all 4 Ubiquiti AC target images (`ubnt_lap-120`, `ubnt_nanostation-ac-loco`, `ubnt_litebeam-ac-gen2`, `ubnt_rocket-prism-5ac-gen2`) alongside `/etc/hotplug.d/net/99-futuramax-wds-dms` and Dual-NMS coexistence (`fmx_uisp_ws_reporter` + `fmx_netjson_watchdog`):
- **Direct `mac80211` `/sys/kernel/debug/ieee80211/phy0/aqm` programming**:
  - `fq_quantum 4542` (`3×MTU`) on AP targets (`ubnt_lap-120`, `ubnt_rocket-prism-5ac-gen2`) and `fq_quantum 1514` (`1×MTU`) on CPE targets (`ubnt_nanostation-ac-loco`, `ubnt_litebeam-ac-gen2`).
  - `fq_limit 2048` on AP targets and `fq_limit 1024` on CPE targets.
  - `fq_memory_limit 4194304` (`4 MiB`).
- **Per-AC `ath10k` AQL TXQ Limits (`/sys/kernel/debug/ieee80211/phy0/aql_txq_limit`)**:
  - `AC_VO` (`0`): `300 / 600 us`
  - `AC_VI` (`1`): `1200 / 2400 us`
  - `AC_BE` (`2`): `1500 / 3000 us`
  - `AC_BK` (`3`): `500 / 1000 us`
  - `aql_threshold`: `5000 us`
- **3-Tier WMM TXQ Classification (`nftables` `inet fmx_iptv_qos`)**:
  - `UDP 5202 -> DSCP CS4` (`tid4_ac1` Dual `1080p60` IPTV)
  - `UDP 5203 -> DSCP EF` (`tid6_ac0` `100 pps` VoIP)

## 3. Closed-Loop Research Reactor Ingestion of Stage 37A & Synthesis of `M22` / `M23`

[`ingest_stage37a_champion_v11_and_synthesize_m22_m23()`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/research/closed_loop_research_reactor.py#L935-L1020) ingests:
- **`S37A-R1` (`HW_REFUTED_OR_BOUNDED`)**: `M17_MAC80211_FQ_LIMIT_TRIPLE_PLAY` (`fq_quantum=3028`, `fq_limit=2048/1024`, `AC_VO=600/1200` $\rightarrow$ `-3.628%` goodput, `-3.028%` p95 RTT).
- **`S37A-R2` (`HW_CONFIRMED` Champion v11)**: `M17b_MAC80211_FQ_LIMIT_TRIPLE_PLAY_QUANTUM_VO_AQL` (`fq_quantum=4542/1514`, `fq_limit=2048/1024`, `AC_VO=300/600` $\rightarrow$ `+2.648%` goodput, `-3.778%` p95 RTT, `-22.452%` p50 RTT, `0/5,684` Dual IPTV loss, `0/1,198` VoIP loss).

### Synthesized Next-Wave Mechanisms (`M22` & `M23`)

| Mechanism ID | Title | Empirical Basis |
| :--- | :--- | :--- |
| **`M22`** | `PB-040` Dynamic Per-Active-Station `fq_quantum` Scaling on `mac80211` (`1514B` Idle $\rightarrow$ `3028B` Dual-Play IPTV $\rightarrow$ `4542B` `3×MTU` Under Active `tid6_ac0` VoIP + `tid4_ac1` IPTV Triple-Play Contention) | `S37A-R1` (`-3.628%` GP at `3028B`) vs `S37A-R2` (`+2.648%` GP, `-22.452%` p50 RTT at `4542B` `3×MTU`) |
| **`M23`** | `PB-041` VoIP-Aware `AC_VO` Burst Guard on `ath10k` (`0 300 600 us` AQL Tightening + `nftables` `DSCP EF` Rate-Bounded Guard Preventing Voice Preemption Starvation of `AC_BE` Bulk TCP) | `S37A-R2` proved tightening `AC_VO` AQL from `600/1200 us` to `300/600 us` maintains `0/1,198` (`0.00%`) VoIP loss while preventing voice TXOP monopolization |
