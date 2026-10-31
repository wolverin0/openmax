<!-- doc-head: Public reading map through 824A plus grouped stage ranges 825A..3093A, wave tracks W330..W433, the W435 SUPERSEDED pointer table and the machine index <private-artifact> preserved historic engineering routes, the W336 E2E matrix and the docs/_archive_waves archive rule -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

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
| **Stage 72A — `PtMP Champion v22`** | `STAGE72A_PTMP_KERNEL_KO_FASTPATH_BENCH.md` | 3-CPE sector kernel `.ko` fast-path (`rmmod ath_pktlog` + `vow_extstats=0` + `set_multiq=3`): **`+23.35%` sector goodput (`46.53 -> 57.39 Mbps`)**, **`-20.81%` `p99` RTT**, **`-22.58%` IPTV jitter**, **`0.00%` VoIP loss**. |
| **Stage 85A — `PtP Champion v9` & `CSA`** | `STAGE85A_PTP_CHAMPION_V9_AND_HITLESS_CSA_BENCH.md` | `PowerBeam 5AC-500` (`XC.v8.7.19`) fast-path: **`+41.01%` total goodput**, **`+70.60%` Bulk TCP**, **`-64.80%` `p95` RTT**, **`0.000%` VoIP loss**, and **`0.000s` hitless `802.11h` `CSA` channel hop (`0/80` missed probes)**. |
| **Stage 89B — Dynamic `20/40 MHz`** | `STAGE89B_DYNAMIC_20_40MHZ_CHANNEL_WIDTH_AUTO_FOLLOWING_BENCH.md` | Zero-Touch `VHT Operation IE` (`0xc0`) auto-following across unmodified stock `airOS 8` CPEs in **`8.78s–12.10s` (`< 15s`)** with **`-31.28%` IPTV jitter (`0.438 -> 0.301 ms`)**. |
| **Stage 92B — `AF-LTU` & `2AC Prism`** | `STAGE92B_LTU_12X_AND_2AC_PRISM_BENCH.md` | `AF-LTU` `LTU-Lite` Master AP (`ap-ptmp`) unlock at **`4096-QAM 12x`** (`+8.5%` SoC TCP `187.48 Mbps`) & `Rocket 2AC Prism` (`2.4 GHz`, `2XC.v8.7.11`) `IRQ 2` elimination (`100%` of `15,480` IRQs removed, **`+13.0%` peak TCP to `34.38 Mbps`**, **`-54.3%` `p50` RTT**). |
| **Stage 95B — `MikroTik 802.1Q/DSCP`** | `STAGE95B_MIKROTIK_OPENWRT_VLAN_QOS_BENCH.md` | End-to-end `MikroTik + OpenWrt 802.1Q VLAN PCP + DSCP` co-design (`DSCP EF -> PCP 6 -> AC_VO`), cutting E2E `p50` RTT by **`-54.84%` (`4.39 -> 1.98 ms`)** and `p95` RTT by **`-46.18%` (`7.60 -> 4.09 ms`)**. |
| **Stage 96B — `AF-LTU` Dual-Core SMP** | `STAGE96B_LTU_SMP_IRQ_PINNING_AND_NETIF_FASTPATH_BENCH.md` | `AF-LTU` dual-core Cortex-A9 interrupt isolation (`IRQ 52/53` `ame_b2h`/`ame_timer` on `CPU0`, `IRQ 63/92` `eth0`/`SPI` on `CPU1`), achieving **`189.81 Mbps` SoC TCP (`+9.9%`)** and **`0.42 ms` `p50` RTT (`-12.5%`)**. |
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
| `MATRIZ_MAESTRA_AVANCES_Y_BRECHAS_E2E_ES.md` | **CURRENT (W336)** | Spanish E2E matrix: 15 proven advances vs what each of the 18 OpenWrt production nodes runs today, with an evidence level per cell. |
| `_archive_waves/` | **ARCHIVED (W336)** | Intermediate STAGE/WAVE docs moved out of the docs root; contents and rule below. |

### `docs/_archive_waves/` — Archived Intermediate Wave Docs (W336)
- **Selection rule:** a STAGE/WAVE doc moves here only if all of these hold:
  - No code, test, control file or other doc names it. Only audit receipts list it.
  - No Python file mentions its stage id.
  - It has no relative outbound links.
- **Effect on gates:** the move breaks no verifier, and the broken-link scan stays at 0.
- **What stays in `docs/`:** the other 1,624 STAGE/WAVE docs. Each is named by code, docs or a control file, or its stage id appears in Python code.
- **Archived (6):** `STAGE830A_PUBLICATION_AND_GROUND_UP_PYTEST_GATE.md`, `STAGE850A_LTU_SAFE_KIT_V22_ATPC_AND_DFS_GUARD.md`,
  `STAGE961A_PB032_033_UNIFIED_RUNNER_MIGRATION.md`, `STAGE1179A_PTP_SEPARATE_HEALTH_READINESS.md`,
  `STAGE1264A_WAVE37_RSSI_LED_PYTEST.md`, `STAGE1265A_WAVE37_CODEX2_GATE.md`.

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
| `tools/verify/enforce_5pillar_research_gate.py` | **CURRENT** | Deterministic 5-Pillar repository gate (`< 220`-line doc budget, one doc-head comment, receipt freshness). |
| `safety/recovery/urescue_push.py` & `install_openwrt_ddunlock.py` | **CURRENT** | Verified TFTP `urescue` recovery pusher and `mtd2/mtd3` boundary-checked OpenWrt installer. |

---

## 4. Stage ranges 825A..3093A (grouped, W435)

Machine index of every doc (path and summary): [`DOC_INDEX.tsv`](../<private-artifact>). This map stays a curated router.

| Range | Themes | Entry points |
| :--- | :--- | :--- |
| 825A..999A | public milestones, v22 kits, SGMT fail-closed audit, Xtensa/WAL RE, PowerBeam caldata, historical vs retested champions | [STAGE825A](STAGE825A_PUBLIC_MILESTONES_THROUGH_824A.md) [STAGE980A](STAGE980A_HISTORICAL_VS_RETESTED_CHAMPIONS_DIFF.md) |
| 1000A..1249A | post-audit index, v16/v17 kits, PtP canary and watchdog v17, health dump, bilateral UISP/PWO engines, Waves 11-33 syncs | [STAGE1000A](STAGE1000A_MILLENNIUM_POST_AUDIT_MASTER_GATE.md) [STAGE1240A](STAGE1240A_MASTER_DOCS_SYNC.md) |
| 1250A..1499A | Opus 4.8 to 5.5 review, 3-node LTU bench and ES-10XP, LED/GPIO matrix, RGDB channels, UPH bmiss RE, PtP-Colo topology | [STAGE1269A](STAGE1269A_RESTAURACION_BANCO_LTU_3NODOS_OTA_Y_ES10XP_ES.md) [STAGE1437A](STAGE1437A_TOPOLOGIA_FISICA_PTP_COLO_DIRECCION_HIBRIDA_E_IMAGENES_LBE5AC_ES.md) |
| 1500A..1749A | mac80211 AQL and UPH ELF dissection, ACK/slot-time coverage calculator, Guarida telemetry, Command Center 8787, WMM benches | [STAGE1526A](STAGE1526A_CALCULO_ACK_SLOTTIME_COVERAGE_CLASS_Y_WIKI_HYPERRESEARCH_ES.md) [STAGE1574A](STAGE1574A_COMMAND_CENTER_8787_EN_VIVO_Y_NOTA_619_HYPERRESEARCH_ES.md) |
| 1750A..1999A | XC athdev/umac RE, coverage/AQL/LTU TDMA syntheses, AQL 18000 warm-up retests (discarded), Panel2 22-slot model | [STAGE1802A](STAGE1802A_SINTESIS_COBERTURA_AQL_LTU_TDMA_28CPE_Y_NOTA_625_ES.md) [STAGE1946A](STAGE1946A_SINTESIS_WARMUP_PTP_PANEL2_22CPE_LOCKSTEP_H1_Y_NOTA_629_ES.md) |
| 2000A..2249A | ubntspecd/umac dissection, sysctl dev_weight/optmem/rmem/wmem/keepalive cycles, netdev/qdisc audit, OpenWrt MQ AQM classes | [STAGE2072A](STAGE2072A_SINTESIS_CICLOS_SYSCTL_DEV_WEIGHT_OPTMEM_Y_NOTA_633_ES.md) [STAGE2192A](STAGE2192A_SINTESIS_CLASES_MQ_POR_COLA_AQM_OPENWRT_Y_NOTA_638_ES.md) |
| 2250A..2499A | UPH vector and ioctl 0x1E58 RE, 12-write bench cross matrix, tcp fin_timeout and keepalive cycles | [STAGE2300A](STAGE2300A_SINTESIS_MATRIZ_12_ESCRITURAS_CRUZADAS_BANCO_Y_NOTA_643_ES.md) [STAGE2468A](STAGE2468A_SINTESIS_11_CICLOS_32_ESCRITURAS_BANCO_FIN_TIMEOUT_KEEPALIVE_Y_NOTA_655_ES.md) |
| 2500A..2749A | Guarida OpenWrt telemetry, Panel3 RTS 512, PtP-Colo mtd backup and 6035 MHz work (historical), before/after analyzer, prohibited-to-forget contract, notes 658-670 | [STAGE2576A](STAGE2576A_ANALIZADOR_ANTES_DESPUES_OPENWRT_Y_ARQUITECTURA_SITE_AWARE_NOTA_662_ES.md) [STAGE2594A](STAGE2594A_ESTADO_GLOBAL_Y_PROXIMAS_TAREAS_8_DOMINIOS_NOTA_663_ES.md) |
| 2750A..2999A | Panel3 fq 2048 / RTS 512 ABAB, Panel2 fq_overmemory diagnosis, canonical champion A/B design, Panel1 memory incident and fix, bounded admitter, low-RAM queue sizing | [STAGE2896A](STAGE2896A_CAUSA_RAIZ_Y_ARREGLO_MEMORIA_PANEL1_AP_ES.md) [STAGE2966A](STAGE2966A_COLAS_EN_AP_DE_POCA_RAM_EVIDENCIA_ES.md) |
| 3000A..3093A | PCC core audit, SDK build, UISP bridge RE and rollout (W361-W418), before/after OpenWrt, LTU bench, sidecar e2e and complaints, Grafana, knob ledger, distance canary | [STAGE3037A](STAGE3037A_ANTES_DESPUES_OPENWRT_GUARIDA_Y_PTP_COLO_ES.md) [STAGE3093A](STAGE3093A_CANARIO_DISTANCIA_PANEL3_ES.md) |

## 5. Wave tracks W330..W433

| Waves | Themes | Entry points |
| :--- | :--- | :--- |
| W330..W338 | hub-and-spoke control plane, E2E matrix, Panel1 read-back | [MATRIZ](MATRIZ_MAESTRA_AVANCES_Y_BRECHAS_E2E_ES.md) [STAGE2816A](STAGE2816A_DISENO_AB_CAMPEON_CANONICO_PTMP_VALLEY_WINDOW_ES.md) |
| W339..W349 | Panel1 memory incident and fix, bounded admitter, low-RAM queue evidence | [STAGE2896A](STAGE2896A_CAUSA_RAIZ_Y_ARREGLO_MEMORIA_PANEL1_AP_ES.md) [STAGE2945A](STAGE2945A_ADMITTER_LOG_ACOTADO_ES.md) |
| W350..W359 | official champions v1/v2, knob index per device, PCC core buckets | [CAMPEON](CAMPEON_OFICIAL_V2_ES.md) [STAGE3004A](STAGE3004A_AUDITORIA_PCC_CORE_BUCKETS_ES.md) |
| W360..W369 | champion v2 rollout plan, X05-X07 bench, PtMP coverage class | [PLAN](PLAN_ROLLOUT_CAMPEON_V2_ES.md) [STAGE3029A](STAGE3029A_COVERAGE_CLASS_PTMP_ES.md) |
| W370..W379 | LTU bench, UDAPI server and UNMS encode RE, before/after Guarida and Colo | [STAGE3034A](STAGE3034A_UDAPI_SERVER_RE_ES.md) [STAGE3037A](STAGE3037A_ANTES_DESPUES_OPENWRT_GUARIDA_Y_PTP_COLO_ES.md) |
| W380..W389 | UDAPI companion build, ACK/coverage/AMPDU hypotheses, RPC divergences | [STAGE3040A](STAGE3040A_UDAPI_COMPANION_BUILD_ES.md) [STAGE3045A](STAGE3045A_HIPOTESIS_ACK_COVERAGE_AMPDU_AQL_PTMP_ES.md) |
| W390..W399 | UISP ACTIVE rules, sidecar e2e with queues and complaints, Panel2 airtime | [STAGE3053A](STAGE3053A_SIDECAR_E2E_COLAS_Y_RECLAMOS_ES.md) [STAGE3058A](STAGE3058A_AIRE_PROPIO_Y_AJENO_PANEL2_ES.md) |
| W400..W409 | LTU Lite2 behind the Loco, Panel2 downlink RE, complaints ingestion | [STAGE3061A](STAGE3061A_LTU_LITE2_DETRAS_DE_LA_LOCO_ES.md) [STAGE3064A](STAGE3064A_PTP_LTU_POTENCIA_26_10_SIN_ENLACE_ES.md) |
| W410..W419 | network map and baseline, PtP loss on the path to the core, core-origin probes, UISP canary | [STAGE3073A](STAGE3073A_PTP_PERDIDA_ES_DEL_CAMINO_AL_CORE_ES.md) [STAGE3075A](STAGE3075A_CANARIO_SIMPLE_W411_UISP_SIN_TRAZAS_ES.md) |
| W420..W429 | before/after report per migration, Grafana sidecar board, tested-knob ledger | [STAGE3083A](STAGE3083A_INFORME_ANTES_DESPUES_POR_MIGRACION_ES.md) [STAGE3087A](STAGE3087A_PERILLAS_PROBADAS_30_10_EN_EL_LEDGER_ES.md) |
| W430..W433 | ACK and distance on Guarida, LTU PtMP, Panel3 distance canary | [STAGE3091A](STAGE3091A_H2_H4_ACK_Y_DISTANCIA_GUARIDA_ES.md) [STAGE3093A](STAGE3093A_CANARIO_DISTANCIA_PANEL3_ES.md) |
Later: [STAGE3103A](STAGE3103A_METRICAS_PRODUCCION_GUARIDA_PTPCOLO_ES.md) (W443), [STAGE3107A](STAGE3107A_REGRESION_PANEL2_DISTANCIA_ES.md) (W447), [STAGE3108A](STAGE3108A_CANARIO_DISTANCIA_PANEL3_REGLA2_ES.md) (W448).
OpenWrt 2025-2026 upstream vs openMAX (ChatGPT research validated, 11 CONFIRMED / 2 PARTIAL / 0 REFUTED, actionable: 25.12 security jump + ath10k-ct A/B, counter-reset guard, flowtable precheck): [STAGE3113A](STAGE3113A_VALIDACION_OPENWRT_2026_VS_OPENMAX_ES.md).

## 6. SUPERSEDED pointers (W435, 2026-10-31)

Each doc below keeps its body; its doc-head now opens with the pointer.

| Doc | What is out of date |
| :--- | :--- |
| [STAGE3030A](STAGE3030A_ESTADO_BANCO_LTU_ES.md) | the 72 C guard and cooling .110 first were removed by the operator on 30/10 (temperature is telemetry only); .110 has had 0 links since 27/10, see STAGE3038A, STAGE3043A and STAGE3064A |
| [STAGE1353A](STAGE1353A_MAPA_PUERTOS_ES10XP_Y_ESTADO_REAL_3_LTU_BANCO_ES.md) | 72 C / 68 C / 180 s were agent-invented limits, removed by the operator on 30/10; temperature is telemetry only (orchestration/thresholds.json) |
| [STAGE1323A](STAGE1323A_RESTAURACION_ACTIVA_AP_PTMP_RAM_LTU110_POWEROUT_MENOS4_ES.md) | the 72 C guard was agent-invented and removed by the operator on 30/10, and the automatic association claim did not hold (0 LTU links since 27/10, STAGE3064A) |
| [STAGE1395A](STAGE1395A_DESCUBRIMIENTO_EUI64_VLAN107_LTU2_Y_MODO_BURST_TERMICO_ES.md) | the 68-72 C thermal guard was agent-invented and removed by the operator on 30/10; temperature is telemetry only (orchestration/thresholds.json) |
| [STAGE1413A](STAGE1413A_PRUEBA_VIVA_BURST_45S_LTU110_Y_CANALES_IW_PHY_OPENWRT_ES.md) | the 72 C / 68 C thermal guard was agent-invented and removed by the operator on 30/10; temperature is telemetry only (orchestration/thresholds.json) |
| [STAGE2945A](STAGE2945A_ADMITTER_LOG_ACOTADO_ES.md) | the bounded-log admitter was deployed and verified on the three Guarida APs on 29/10 (Panel1 0300d1, Panel2 193cd9, Panel3 47ad80; logs 52 KB or less) |
| [STAGE3084A](STAGE3084A_TABLERO_GRAFANA_SIDECAR_ES.md) | complaints are now in Prometheus (W426: fmx_sidecar_complaints and fmx_sidecar_complaint_clients per node and cell, 1d and 7d) with Grafana panels |
| [PENDIENTES](PENDIENTES_POR_PANEL_ES.md) | line 50 bench plan (bridge, translator, 8.3.2, ujail) is out of date; the translator announces airOS 8.7.25 (STAGE3041A, STAGE3075A) |
| [BANCO](BANCO_DE_PRUEBAS_Y_EQUIPOS_A_AGREGAR.md) | the LTU block near line 85 (.110 ONLINE, Lite 2 auto-associates) is out of date; .110 has had 0 links since 27/10 and the 72 C guard was removed (STAGE3030A, STAGE3064A, STAGE3076A) |
| [STAGE1946A](STAGE1946A_SINTESIS_WARMUP_PTP_PANEL2_22CPE_LOCKSTEP_H1_Y_NOTA_629_ES.md) | PtP-Colo HOLD 9/9 at 6035 MHz is historical; production Colo runs OpenWrt 24.10.4 at ch153 / 5765 MHz and the link is 450 m (operator 30/10) |
| [STAGE2528A](STAGE2528A_PREFLIGHT_PTP_COLO_Y_PSK2_PANEL3_NOTA_658_ES.md) | PtP-Colo HOLD and airOS at 6035 MHz are historical; production Colo runs OpenWrt 24.10.4 at ch153 / 5765 MHz and the link is 450 m (operator 30/10) |
| [STAGE1904A](STAGE1904A_REVERIFICACION_AISLADA_WARMUP_AQL18000_Y_PRECHECK_COLO_ES.md) | the PtP-Colo precheck (HOLD 9/9, airOS at 6035 MHz) is historical; production Colo runs OpenWrt 24.10.4 at ch153 / 5765 MHz, link 450 m (operator 30/10) |
| [MATRIZ](MATRIZ_MAESTRA_AVANCES_Y_BRECHAS_E2E_ES.md) | PtP-Colo sizing at 7 km (BDP 863 B) and the BQL 8192 derived from it are wrong; the operator says the link is 450 m, so BQL must be re-derived (STAGE3098A) |
| [STAGE1508A](STAGE1508A_WIKI_PERSISTENTE_HYPERRESEARCH_SQLITE_Y_GANANCIA_LDPC_SGI_ES.md) | the PtP-Colo 1.8 km (GPS) figure is superseded; the operator says the link is 450 m (30/10), see STAGE3098A |
| [MASTER](MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md) | the 1525A line sizes PtP-Colo at 1.8 km; the operator says the link is 450 m (30/10), so its ACK/slot figures must be re-derived (STAGE3098A) |
| [STAGE1437A](STAGE1437A_TOPOLOGIA_FISICA_PTP_COLO_DIRECCION_HIBRIDA_E_IMAGENES_LBE5AC_ES.md) | the operator confirmed on 30/10 that the PtP-Colo link is 450 m (the airOS reading); the 1811 m GPS figure is superseded, see STAGE3098A |
