<!-- doc-head: Copyable bilingual public milestones through824A; source qualifications retained; nothing posted -->
<!-- /doc-head -->

# openMAX Reddit drafts: milestones through824A

Local drafts only. No Reddit post, upload or external message was sent.

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

## EN copyable update

```text
openMAX researches existing Ubiquiti airMAX AC/M5/LTU hardware: https://github.com/wolverin0/openmax
Milestones through824A distinguish saved reported results from local software validation.
WA v13 sources report78.51Mbps VHT20 peak and86.37% less loaded p50 RTT; PtP v5 reports25.47Mbps VHT40.
PowerBeam5ACGen2 and LiteBeam5ACGen2 have their own exact profiles; this is metadata support, not universal runtime acceptance.
Seven PB040+PB050+PB060 target payloads were composed offline. LTUv20 sources report264windows;
the guarded br1 DHCP kit was tested with local command stubs, not a live radio.
Guarida v10 is an uncalibrated sensitivity model.514.80Mbps belongs to an earlier v9 source claim.
Static823A found ubntspecd scoring labels, not the scoring formula;824A found ame_dfs classifier symbols,
not numeric radar thresholds or proven LNA-saturation immunity. Dynamic acceptance remains UNKNOWN.
The legacy publicWA v4 tester starts wired with Wi-Fi/DHCP off, no shared key and no OTA migration watchdog.
Use exact model/revision, current checksums, your own credentials and a separately validated recovery path.
No production deployment, safe remote conversion or universal RF gain is promised.
```

## ES texto para copiar

```text
openMAX investiga el hardware Ubiquiti airMAX AC/M5/LTU existente: https://github.com/wolverin0/openmax
Hasta824A separamos resultados reportados, verificacion local, simulacion y aceptacion en radio.
WA v13 reporta78.51Mbps VHT20 y86.37% menos p50 cargado; PtP v5 reporta25.47Mbps VHT40.
PowerBeam5ACGen2 y LiteBeam5ACGen2 conservan perfiles propios; sus metadatos no prueban compatibilidad fisica universal.
Se compusieron siete payloads PB040+PB050+PB060 offline. LTUv20 reporta264ventanas;
el kit DHCP de br1 se probo con stubs locales, sin ejecutar el firewall de una radio.
Guarida v10 es un modelo sin calibrar;514.80Mbps corresponde a un reporte anterior v9.
823A encontro etiquetas de puntaje en ubntspecd, no su formula;824A encontro simbolos DFS,
no umbrales numericos de radar ni inmunidad LNA demostrada. La aceptacion dinamica sigue UNKNOWN.
El tester publico WA v4 inicia por cable, sin Wi-Fi/DHCP ni clave compartida y sin watchdog OTA remoto.
Identificar modelo/revision, verificar hashes vigentes, definir claves propias y validar recuperacion aparte.
No se promete deploy, conversion remota segura ni una ganancia RF universal.
```

## Earlier benchmark limitations retained

Legacy Stage161 R16 reported+13.68% goodput in a short contrast, with slightly worse p99.
The8-flow+68.3%..+90.6% contrast mixes runs; it does not isolate a VM-setting effect.
Stage162/163 reported-25.78%E2Ep95 remains UNPROVEN because of999/samples=1 records and unproved flowtable activation.
Configured fields are not getters; local image checks do not establish boot/recovery/stock-airOS interoperability.

## Full discovery catalogue (historical source index)

| ID | Finding | Layer | Evidence limit |
| :--- | :--- | :--- | :--- |
| FMX-DISC-01 | Protect authentication daemons from OOM on 64 MiB boards | Linux | Memory guard; not unlimited load capacity |
| FMX-DISC-02 | Bound mac80211 FQ memory | mac80211 | Use limits suitable for the exact RAM class |
| FMX-DISC-03 | ETH_P_TEB 0x6558 WDS decapsulation | mac80211 | Exact ABI and image required |
| FMX-DISC-04 | Two-stage vendor-IE withdrawal interoperability hypothesis | airMAX | Public kit does not prove stock-CPE zero-touch acceptance |
| FMX-DISC-05 | Big-endian MIPS iperf3 JSON crash | userspace | Use plain-text output; no iperf3 JSON mode |
| FMX-DISC-06 | Separate AirPrism GPIO filters, HSR and passive ISO hardware | hardware | Active-filter support needs exact hardware qualification |
| FMX-DISC-07 | airOS rc.poststart versus cron persistence | airOS | Saved configuration is not cold-boot proof |
| FMX-DISC-08 | LTU FPGA architecture and 4096-QAM rate-table analysis | LTU | Binary presence does not establish RF operation |
| FMX-DISC-09 | 32-CPE sector topology and backhaul fault isolation | network | Topology-specific evidence; no migration approval |
| FMX-DISC-10 | AP ACK pacing and relay/capacity crossover models | controller | Models are not measured subscriber capacity |
| FMX-DISC-11 | ubnt_poll_host 16-integer control vector | airMAX | Validate the exact handler and bounds |
| FMX-DISC-12 | ZeroClaw external-controller architecture | controller | Architecture proposal, not firmware feature acceptance |
| FMX-DISC-13 | Multi-VDEV cooperative CPE relay | controller | Feasibility depends on the control boundary |
| FMX-DISC-14 | PowerBeam M5 XW diversity behavior | ath9k | Board-specific, not an AC feature |
| FMX-DISC-15 | 2.4 GHz Rocket 2AC Prism and Loco M2 experiments | hardware | Separate band and driver populations |
| FMX-DISC-16 | OpenWrt BusyBox ip-link tool behavior | userspace | Tool capability must be checked on the installed build |
| FMX-DISC-17 | LTU driver audit inventory | LTU | Static/runtime evidence and memory impact remain distinct |
| FMX-DISC-18 | XW rate-control cold-start MCS0 airtime cost | ath9k | Warm-up changes must not hide failed windows |
| FMX-DISC-19 | AQL threshold/high-limit interaction and CoDel drops | mac80211 | A configured knob is not a measured actuator |
| FMX-DISC-20 | XC daprot symbol mapping and AirPrism stage-one bank | airMAX | Symbol identity is build-specific |
| FMX-DISC-21 | ATPC/timing vector layout and CPU-class budgets | Linux/airMAX | Do not transfer budgets between CPU classes |
| FMX-DISC-22 | BusyBox fractional ping timing and per-window warm-up | userspace | Retain sample counts and tool failures |
| FMX-DISC-23 | UMAC/ATHDEV defects, multiq and VLAN/PPPoE DSCP | airMAX | Saved benchmark and static security findings differ |
| FMX-DISC-24 | DFS-aware watchdog and migration safety gates | operations | Preserve CAC, recovery and zero-touch acceptance gates |
| FMX-DISC-25 | airOS scan whitelist and host_80211 behavior | airMAX | No regulatory or channel bypass in public kits |
| FMX-DISC-26 | Three-argument CSA channel-switch interface | airMAX | CSA success is not unrestricted channel support |
| FMX-DISC-27 | XC packet-log removal and dual-radio failure mode | airMAX | Do not apply module-removal recipes across boards |
| FMX-DISC-28 | Statistics-unsubscribe pointer handling | airMAX | Safe telemetry flags differ from unsafe unload paths |
| FMX-DISC-29 | LTU access-boundary review | LTU | Access prerequisites and disclosure impact are qualified |
| FMX-DISC-30 | LTU gain-table gate and early poststart exit | LTU | Persistence still requires independent cold-boot evidence |
| FMX-DISC-31 | Dynamic 20/40 MHz VHT width following | mac80211 | Peer/driver-specific interoperability |
| FMX-DISC-32 | BNG shaping, LTU frame geometry and 2XC interrupt load | network/LTU | Keep the independent experiments separate |
| FMX-DISC-33 | Module control-boundary audit and WDS churn healing | controller | Static defects and live healing require separate proof |
| FMX-DISC-34 | LTU superframe tail bounds and constrained Pareto ranking | LTU/controller | Offline ranking is not runtime authorization |
| FMX-DISC-35 | Flash-unlock and firmware-signature gate analysis | firmware | No signature bypass or flash instructions supplied |
| FMX-DISC-36 | Linux 6.6.110 module layout and skb data offsets | mac80211 | A matching version string alone is insufficient |
| FMX-DISC-37 | Dynamic AP-interface admitter rebinding | controller | Public helper has no fixed peer or captured vendor IE |
| FMX-DISC-38 | Four-address EAPOL delivery and AP_VLAN event ordering | mac80211 | Association alone does not prove bridged data |
| FMX-DISC-39 | Different mac80211 ABIs within the same kernel version | mac80211 | Use exact module hash, layout and original build |
| FMX-DISC-40 | Board-specific WA image packaging and control mapping | firmware | Shared WA family does not make DTBs interchangeable |
| FMX-DISC-41 | Authorized-gated four-address event patch, mac80211 v3 | mac80211 | Event gating is not general RX-security acceptance |
| FMX-DISC-42 | Stock PtP STA data gate and remote-first migration order | airMAX | Stage138 is offline static analysis/simulation; not a flash receipt |

Sources: [historical catalogue](CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md), [Stage138](../artifacts/autoresearch/stage138a_ptp_sta_data_gate_verdict.json), [Stage161](../artifacts/autoresearch/stage161a_live_wa_round16_18_autoresearch.json), [Stage162](../artifacts/autoresearch/stage162a_live_wa_e2e_forwarding_offload_benchmark.json), [Stage163](../artifacts/autoresearch/stage163a_cumulative_18round_wa_champion_v2.json).

[Tester guide](GUIA_UNIVERSAL_POWERBEAM_LITEBEAM_OPENMAX.md) and [public-v4 limits](OPENMAX_WA_PUBLIC_V4_TESTER_GUIDE.md). Local drafts only; no external posting.
See also: [3-Way Benchmark (Stock airOS 8 vs Tuned airOS 8 vs OpenWrt Champion)](BENCHMARK_3WAY_AIROS_STOCK_VS_TUNED_VS_OPENWRT_CHAMPION.md) and [Public PtP/PtMP Field Kits](../firmware/public_field_kits/README.md).
