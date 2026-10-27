<!-- doc-head: Public reading map through824A and preserved historic engineering routes -->
<!-- /doc-head -->

# openMAX Master Documentation & Reading Map (`docs/DOCS-MAP.md`)

## Current milestones through Stage824A / Hitos hasta Stage824A

This Stage825A update reconciles saved evidence; it adds no radio measurements or publication.
Esta actualizacion documental separa resultados reportados, empaquetado, simulacion y aceptacion fisica.

| Milestone | Source-qualified result and limit |
| --- | --- |
| WA v13 | Stage773A reported 78.51 Mbps peak TCP in VHT20 and -86.37% loaded p50 RTT; imported claims, not remeasured here. |
| PtP v4/v5 | Stage741A/v5 reported 25.47 Mbps peak TCP in VHT40; PBE-5AC-Gen2 and LBE-5AC-Gen2 have distinct board-specific profiles. |
| PB040 + PB050 + PB060 | Stage817A composed seven triple-patch SGMT payloads offline; byte/layout verification is CONFIRMED, target activation UNKNOWN. |
| LTU v20 | Stage774A reported 264 windows. Stage818A packages guarded br1 DHCP filtering tested with local command stubs; zero-rogue-DHCP runtime UNKNOWN. |
| Guarida v10 | Stage819A is an uncalibrated sensitivity/Pareto model, not measured tower capacity. The imported 514.80 Mbps claim belongs to Stage775A/v9. |
| Stage823A | Static strings in ubntspecd expose per-bandwidth BPS / SCORE / RATING labels; the numeric formula, coefficients and CPE-histogram combination remain UNKNOWN. |
| Stage824A | Static symbols locate the DFS classifier surface in ame_dfs.ko; numeric PW/PRI tables, detector criteria and LNA-saturation immunity remain UNKNOWN. |

Both PBE-5AC-Gen2 and LBE-5AC-Gen2 have CONFIRMED profile metadata; every revision's runtime compatibility remains UNKNOWN.
No universal compatibility, safe OTA conversion, zero-FP rate or production acceptance follows from these artifacts.
Attribution: Linux/mac80211/ath10k and QCA firmware for WA/PtP; Linux and proprietary airMAX/LTU module for LTU;
external controller for simulation, packaging and documentation. Static names alone do not establish algorithm behavior.
Source links are local evidence pointers; a privacy-filtered public selection may omit historical targets.
Sources: [WA v13](STAGE773A_WA_CHAMPION_V13_344WINDOW_FIELD_ROLLOUT_KIT.md), [PtP v5](STAGE741A_PBE5AC_LBE5AC_VHT40_PB050_PRODUCTION_BUNDLE_V5.md),
[triple patch](STAGE817A_UNIVERSAL_PB060_TRIPLE_PATCH_OPENWRT_AIROS_KIT.md), [LTU kit](STAGE818A_LTU_4096QAM_12X_LDPC_AND_SUPER4096_SAFE_KIT.md),
[model](STAGE819A_GUARIDA_TOWER_V10_TRIPLE_PATCH_AND_XW_MIXED_TDMA_PARETO.md), [825A source ledger](STAGE825A_PUBLIC_MILESTONES_THROUGH_824A.md).

The directory below preserves earlier reading routes; historical report claims are not independently reaccepted by this update.

## 1. Recommended Reading Order for Engineers & Researchers

1. **[`README.md`](../README.md)** — Executive summary, physical testbed manifesto, and confirmed benchmark progression (`Stages 1–99D`).
2. **Local project rules (excluded from public selection)** — Project constitution, source-of-truth hierarchy (`CONFIRMED` / `INFERRED` / `UNKNOWN` / `REFUTED`), safety boundaries (`mtd0/1/5`), and the 5-Pillar research framework.
3. **[`docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md`](MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md)** — Master Research & Autoresearch Index (`v29.0`): hardware champions, `571`-knob catalog, and cross-platform tuning matrices (`WA`, `XC`, `2XC`, `XW`, `AF-LTU`, `MikroTik`).
4. **[`docs/CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md`](CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md)** — Complete ledger of `32` hardware discoveries (`FMX-DISC-01` through `FMX-DISC-32`).
5. **[`docs/CURRENT_STATE.md`](CURRENT_STATE.md)** — Living operational state log and active bench configurations.
6. **[`docs/DECISIONS.md`](DECISIONS.md)** & **[`docs/EXPERIMENTS.md`](EXPERIMENTS.md)** — Architectural Decision Records (`D-0001..D-0018`) and experiment register (`FMX-0001..0016`, Campaigns `C1–C8`).
7. **[`docs/QCA988X_CONTROL_BOUNDARY.md`](QCA988X_CONTROL_BOUNDARY.md)** & **[`docs/HARDWARE_MATRIX.md`](HARDWARE_MATRIX.md)** — Source-verified `ath10k-ct` control boundaries and Grade-A hardware identity matrix.
8. **[`safety/recovery/FMX-0002_recovery_runbook.md`](../safety/recovery/FMX-0002_recovery_runbook.md)** — Mandatory partition backup and TFTP `urescue` recovery runbook.

---

## 2. Highlighted Engineering & Hardware Breakthrough Reports (`Stages 7–99D`)

| Stage / Domain | Primary Report | Historical source-reported result; scope remains specific |
| :--- | :--- | :--- |
| **Stage 7 — Multi-Vendor PtMP** | [`STAGE7_MULTIVENDOR_PTMP_REPORT.md`](STAGE7_MULTIVENDOR_PTMP_REPORT.md) | 3-station (`802.11ac` + `MikroTik ath9k` + `airOS 6 M5`) `WMM AC_VO` Deficit Bypass (**`21.0x` RTT cut**) & `RTS/CTS 256B` (**`+18.5%` UL**). |
| **Stage 8 — Adaptive Controller** | [`STAGE8_ADAPTIVE_CONTROLLER_AND_SECTOR_SIM.md`](STAGE8_ADAPTIVE_CONTROLLER_AND_SECTOR_SIM.md) | Zero-fork `fmx_adaptive_controller.sh` (**`47.6x` `p95` tail-latency cut**), `VHT40` vs `VHT80` (**`2.26x` spectral efficiency**), and 6-flow BiDir stress (**`39.1x` RTT cut**). |
| **Stage 9 — `20 MHz` & `CoTSQ`** | [`STAGE9_20MHZ_RATEMASK_COTSQ_AND_PROCD.md`](STAGE9_20MHZ_RATEMASK_COTSQ_AND_PROCD.md) | `VHT20` (**`0.9531` Jain fairness**, **`3.342 bit/s/Hz` DL / `3.656 bit/s/Hz` UL**), `CoTSQ 128 KB` (**`181.90 Mbps` UL**), and `procd` supervision. |
| **Stage 10 — Stock `airOS 8` Interop** | [`STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md`](STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md) | Cracked all 4 stock `airOS 8` locks (`ubnt_poll_host_is_ap_valid`, 30s TDMA watchdog, `allow_80211=1`, `ETH_P_TEB` `0x6558`), achieving **`78.7 Mbps` UL / `63.6 Mbps` DL in `20 MHz`**. |
| **Stage 11A — `XC` AirPrism RE** | [`STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md`](STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md) | Decompiled 34 `XC` board structs (`ubnthal.ko`), 2-stage AirPrism (`GPIO 13..16` + SPI `hsr` at `0xbf000000`), and `SPECTRAL-XMIT-FILTER`. |
| **Stage 11B — `LTU` `4096-QAM` RE** | [`STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md`](STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md) | Mapped `amesoc3` Cortex-A9 + `AD9361` SDR + `Arria 10` FPGA, `4096-QAM` (`12X`, `0x1f`) rate tables, and `2/4/8`-subband `OFDMA`. |
| **Stage 12 — Live Sector Cutover** | [`STAGE12_FULL_OPENWRT_SECTOR_AND_UISP_BRIDGE.md`](STAGE12_FULL_OPENWRT_SECTOR_AND_UISP_BRIDGE.md) | Live outdoor `20 MHz` sector cutover (`Live-Sector-1` + `CPE-A` + `CPE-B`) to OpenWrt 24.10.4 (**~10x lower wireless RTT `1.93–2.42 ms`**, **`69.80 Mbps` TCP DL**) + native `udapi-bridge`. |
| **Stage 72A — `PtMP Champion v22`** | [`STAGE72A_PTMP_KERNEL_KO_FASTPATH_BENCH.md`](STAGE72A_PTMP_KERNEL_KO_FASTPATH_BENCH.md) | 3-CPE sector kernel `.ko` fast-path (`rmmod ath_pktlog` + `vow_extstats=0` + `set_multiq=3`): **`+23.35%` sector goodput (`46.53 -> 57.39 Mbps`)**, **`-20.81%` `p99` RTT**, **`-22.58%` IPTV jitter**, **`0.00%` VoIP loss**. |
| **Stage 85A — `PtP Champion v9` & `CSA`** | [`STAGE85A_PTP_CHAMPION_V9_AND_HITLESS_CSA_BENCH.md`](STAGE85A_PTP_CHAMPION_V9_AND_HITLESS_CSA_BENCH.md) | `PowerBeam 5AC-500` (`XC.v8.7.19`) fast-path: **`+41.01%` total goodput**, **`+70.60%` Bulk TCP**, **`-64.80%` `p95` RTT**, **`0.000%` VoIP loss**, and **`0.000s` hitless `802.11h` `CSA` channel hop (`0/80` missed probes)**. |
| **Stage 89B — Dynamic `20/40 MHz`** | [`STAGE89B_DYNAMIC_20_40MHZ_CHANNEL_WIDTH_AUTO_FOLLOWING_BENCH.md`](STAGE89B_DYNAMIC_20_40MHZ_CHANNEL_WIDTH_AUTO_FOLLOWING_BENCH.md) | Zero-Touch `VHT Operation IE` (`0xc0`) auto-following across unmodified stock `airOS 8` CPEs in **`8.78s–12.10s` (`< 15s`)** with **`-31.28%` IPTV jitter (`0.438 -> 0.301 ms`)**. |
| **Stage 92B — `AF-LTU` & `2AC Prism`** | [`STAGE92B_LTU_12X_AND_2AC_PRISM_BENCH.md`](STAGE92B_LTU_12X_AND_2AC_PRISM_BENCH.md) | `AF-LTU` `LTU-Lite` Master AP (`ap-ptmp`) unlock at **`4096-QAM 12x`** (`+8.5%` SoC TCP `187.48 Mbps`) & `Rocket 2AC Prism` (`2.4 GHz`, `2XC.v8.7.11`) `IRQ 2` elimination (`100%` of `15,480` IRQs removed, **`+13.0%` peak TCP to `34.38 Mbps`**, **`-54.3%` `p50` RTT**). |
| **Stage 95B — `MikroTik 802.1Q/DSCP`** | [`STAGE95B_MIKROTIK_OPENWRT_VLAN_QOS_BENCH.md`](STAGE95B_MIKROTIK_OPENWRT_VLAN_QOS_BENCH.md) | End-to-end `MikroTik + OpenWrt 802.1Q VLAN PCP + DSCP` co-design (`DSCP EF -> PCP 6 -> AC_VO`), cutting E2E `p50` RTT by **`-54.84%` (`4.39 -> 1.98 ms`)** and `p95` RTT by **`-46.18%` (`7.60 -> 4.09 ms`)**. |
| **Stage 96B — `AF-LTU` Dual-Core SMP** | [`STAGE96B_LTU_SMP_IRQ_PINNING_AND_NETIF_FASTPATH_BENCH.md`](STAGE96B_LTU_SMP_IRQ_PINNING_AND_NETIF_FASTPATH_BENCH.md) | `AF-LTU` dual-core Cortex-A9 interrupt isolation (`IRQ 52/53` `ame_b2h`/`ame_timer` on `CPU0`, `IRQ 63/92` `eth0`/`SPI` on `CPU1`), achieving **`189.81 Mbps` SoC TCP (`+9.9%`)** and **`0.42 ms` `p50` RTT (`-12.5%`)**. |
| **Stage 98A — `MikroTik BTest/MNDP`** | [`STAGE98A_MKT_BOCA7_BTEST_AND_MNDP_PROTOCOL_AUDIT.md`](STAGE98A_MKT_BOCA7_BTEST_AND_MNDP_PROTOCOL_AUDIT.md) | Clean-room wire-protocol decoders for MikroTik `MNDP` (`UDP/5678`), `CDP`, and Bandwidth Test (`TCP/2000`) with non-intrusive bench admission rules. |
| **Stage 99B — `LTU` `80`-Symbol SimPy** | [`STAGE99B_LTU_80SYMBOL_SUPERFRAME_SIMPY_PARETO.md`](STAGE99B_LTU_80SYMBOL_SUPERFRAME_SIMPY_PARETO.md) | `SimPy` + `pymoo` (`NSGA-II`) Pareto optimization (`13` non-dominated points) proving the `80`-symbol (`61 DL + 19 UL` at `22.4 MS/s`, `2.0 ms` / `500 Hz`) superframe + SMP pinning dominates legacy `4.0–8.0 ms` frames. |

---

## 3. Repository Directory & Component Register

### `docs/` — Navigation, Architecture & Multi-Lane Audits
| File | Status | Purpose |
| :--- | :--- | :--- |
| `DOCS-MAP.md` | **CURRENT** | Master reading map and repository directory (this file). |
| `MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md` | **CURRENT (`v29.0`)** | Master index of all 5 research pillars, hardware champions, and `571` cataloged knobs. |
| `CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md` | **CURRENT** | Curated registry of `32` confirmed discoveries (`FMX-DISC-01..32`) and closed hardware gaps. |
| `CURATED_MULTILANE_CODEX_AGY_RECONCILIATION.md` | **CURRENT** | Multi-lane (`Codex` + `AGY`) reconciliation and `571`-knob taxonomy (`365` `CONFIRMED_LIVE_TESTED`). |
| `STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE.md` | **CURRENT** | Deep binary reverse engineering of `ubnt_poll_host.ko`, `umac.ko`, `ame_core.ko`, and `eab_driver.ko`. |
| `STAGE59A_ZERO_FALSE_POSITIVE_WISP_RF_OBSERVABILITY_AND_GUARIDA_PLAN.md` | **CURRENT** | Zero-false-positive RF observability architecture and 3-panel sector telemetry plan. |
| `TESTBED_ENVIRONMENT_GUIDE.md` | **CURRENT** | Physical 2-tier coaxial + rooftop testbed guide, Fraunhofer distance, and automated recovery. |
| `COMMUNITY_CALL_FOR_COLLABORATION.md` | **CURRENT** | Open call for WISP operators, kernel developers, and academic wireless researchers. |

### `knowledge/` & `debates/` — Foundational Theory, Firmware Internals & Literature
| File | Status | Purpose |
| :--- | :--- | :--- |
| `knowledge/ANALYTICAL_QUEUE_MODEL_AND_HOOKS.md` | **CURRENT** | Mathematical models for `CoTSQ 6ms` A-MPDU efficiency $\eta(K)$, Bianchi PtMP hidden-node Markov chains, and WMI/HTT hooks. |
| `knowledge/ATH10K_CT_FIRMWARE_DEEP_DIVE.md` | **CURRENT** | Deep dive into `QCA9880`/`QCA9882` `ath10k-ct` internals: HTT credit rings, peer stats, and retry amplification. |
| `knowledge/PACED_AGGREGATION_AND_COTSQ.md` | **CURRENT** | Empirical and analytical proof of why `TSQ=1ms` starves 802.11ac aggregation and `CoTSQ` restores throughput. |
| `knowledge/PTMP_OUTDOOR_TDMA_VS_CSMA.md` | **CURRENT** | Physics of outdoor PtMP contention vs hybrid `mac80211` `AQL` + `ATF` + `RTS/CTS NAV`. |
| `knowledge/AUTONOMOUS_WIRELESS_RESEARCH_ENGINE.md` | **CURRENT** | Karpathy/IteRate-style closed-loop optimization engine, reward function $J(\theta)$, and counterbalanced `A1 -> B1 -> A2 -> B2` gate. |
| `knowledge/SPECTRAL_AND_CSI_ANALYSIS.md` | **CURRENT** | Baseband FFT spectral scanning via RelayFS (`fft_sample_ath10k`) vs structural absence of CSI on `QCA988x`. |
| `knowledge/REAL_HARDWARE_LITERATURE.md` | **CURRENT** | Tiered catalogue of peer-reviewed real-hardware wireless systems papers (`IteRate`, `PNOFA`, `Ending the Anomaly`, `AirSlice`). |
| `debates/001-openmax-qca9880-ptmp-optimizat/synthesis.md` | **CURRENT** | Multi-LLM architectural consensus on MIPS 74Kc CPU ceilings, split-plane shaping, and uplink gates. |

### `orchestration/`, `controller/`, `telemetry/` & `tools/` — Executable Engines & Verification
| Path | Status | Purpose |
| :--- | :--- | :--- |
| `orchestration/autoresearch/fmx_autoresearch_harness.py` | **CURRENT** | Counterbalanced `A1 -> B1 -> A2 -> B2` hardware autoresearch harness with `45s` Non-DFS / `120s` DFS rollback watchdog. |
| `orchestration/autoresearch/firmware_knob_candidates.json` | **CURRENT** | Machine-readable `571`-knob catalog across `WA`, `XC`, `2XC`, `XW`, `AF-LTU`, `OpenWrt`, and `MikroTik` (`365` `CONFIRMED_LIVE_TESTED`). |
| `controller/fmx_adaptive_controller.sh` | **CURRENT** | Zero-fork POSIX closed-loop adaptive `AQL`/`ATF` sector daemon (`< 0.1%` MIPS CPU) supervised by `procd`. |
| `controller/optimizer/rate_bandit.py` | **CURRENT** | Adaptive Resetting Multi-Armed Bandit (`ADR-bandit`) rate-mask controller with Page-Hinkley drift detection. |
| `telemetry/spectral_fft/parser.py` | **CURRENT** | Binary RelayFS spectral FFT parser (`fft_sample_ath10k`, `23.4 µs/sample`) and interference classifier. |
| `tools/research/closed_loop_research_reactor.py` | **CURRENT** | Closed-loop `HYPERRESEARCH V8` + `scholar-mcp` research reactor and receipt synchronizer. |
| `tools/verify/enforce_5pillar_research_gate.py` | **CURRENT** | Deterministic 5-Pillar repository gate (`< 220`-line doc budget, `1` `<!-- doc-head -->`, receipt freshness). |
| `safety/recovery/urescue_push.py` & `install_openwrt_ddunlock.py` | **CURRENT** | Verified TFTP `urescue` recovery pusher and `mtd2/mtd3` boundary-checked OpenWrt installer. |
