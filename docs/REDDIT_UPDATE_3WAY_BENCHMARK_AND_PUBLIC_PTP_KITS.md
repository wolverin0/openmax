<!-- doc-head: Copyable bilingual Reddit update (EN/ES) for r/wisp and openMAX GitHub: 13 concise 1-to-3-line breakthroughs with exact improvements and repo doc links -->
<!-- /doc-head -->

# openMAX Reddit Update (`r/wisp` + GitHub `wolverin0/openmax`) — Complete 3-Day Synthesis

Format: **1 to 3 lines per item** stating **what was achieved**, **what improved (exact % / ms / Mbps)**, and **the exact document/script path in `https://github.com/wolverin0/openmax`**.

---

## 1. Ready-to-Paste Reddit Update (English — 13 Concise Breakthroughs + Repo Links)

```markdown
**Update (3 days later) — 13 Major Hardware & Field Breakthroughs, 3-Way Benchmark Table & Public PtP/PtMP Scripts (`openMAX`)**

Since our update 3 days ago (`https://github.com/wolverin0/openmax`), here is a concise summary (1–3 lines per milestone) of everything we proved on live hardware and tower sectors, what improved, and where to read the full data or grab the scripts in the repo:

1. **3-Way Hardware Benchmark (`Stock airOS 8` vs. `Tuned airOS 8` vs. `OpenWrt 24.10.4` Champion):**
   * **What improved:** Tuning Stock `airOS 8` in place (`rc.poststart`, zero flashing) cuts loaded `p95` latency by **`-50.3%` (`34.3 -> 17.0 ms`)** and VoIP jitter by **`-54.1%` (`1.55 -> 0.71 ms`)**; migrating to `OpenWrt 24.10.4` + our Champion profile cuts unloaded sector RTT **`~10x` (`22.58 -> 1.93 ms`)** and loaded saturation RTT by **`-86.4%` DL (`8.43 ms`) / `-88.9%` UL (`10.37 ms`)** with **`64.0–78.51 Mbps` peak TCP** in `20 MHz`.
   * **Repo doc & scripts:** `docs/BENCHMARK_3WAY_AIROS_STOCK_VS_TUNED_VS_OPENWRT_CHAMPION.md` | `firmware/public_field_kits/README.md`

2. **Standalone Drop-In PtP & PtMP Field Scripts for Both `Stock airOS 8` and `OpenWrt 24.10.4`:**
   * **What we shipped:** Dependency-free POSIX `sh` kits with `--dry-run`, `--apply-ram`, `--persist`, `--verify` (live read-back), and `--rollback` for both `airOS 8` (`tx_queue_len=192`, `netdev_budget=600`, `ampduFrames=24`, WMM `AC_VI`/`AC_VO`, `ath_pktlog` unload) and `OpenWrt 24.10.4` (`--role ptp | ptmp-ap | ptmp-cpe` with `FQ-CoDel` `4 MiB`, per-AC `AQL`, `BQL`, and `CoTSQ 64 KB`).
   * **Repo scripts:** `firmware/public_field_kits/airos8_ptp_ptmp_tuned_champion.sh` | `firmware/public_field_kits/openwrt24_ptp_ptmp_champion.sh`

3. **3 Live Tower Sectors + 1 PtP Backhaul Migrated 100% Remotely (`18/18` Radios on `OpenWrt 24.10.4` Linux `6.6.110`, Zero Tower Climbs):**
   * **What improved:** All 18 active radios (`LiteAP 120` APs + `LiteBeam 5AC Gen2` & `NanoStation 5AC Loco` CPEs + PtP backhaul) were converted over the air using a `75s` RAM rollback watchdog, preserving Router/NAT mode, `nftables` hardware flow-offloading, and a working LuCI WebUI.
   * **Repo docs:** `docs/STAGE12_FULL_OPENWRT_SECTOR_AND_UISP_BRIDGE.md` | `docs/CURRENT_STATE.md`

4. **Zero-Downtime Hybrid Mode (Stock `airOS 8` Customer CPEs Connected to `OpenWrt 24.10.4` Sector APs):**
   * **What improved:** Solved all 4 interoperability locks (`ubnt_poll_host_is_ap_valid`, 30s TDMA watchdog, `allow_80211=1`, and `ETH_P_TEB 0x6558` 4-addr WDS bridge admitter) so unmodified `airOS 8` CPEs stay connected and pass **`78.7 Mbps` UL / `63.6 Mbps` DL in `20 MHz`** while migrating a sector one customer at a time.
   * **Repo doc:** `docs/STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md`

5. **64 MB RAM OOM Eradication + Linux 6.6 `sysctl` Partial-Apply Bug Fixed (`100%` Live Read-Back Match, `0 differs`):**
   * **What improved:** Capping `mac80211` `fq_memory_limit` from `16 MiB` (25% of RAM!) to `4 MiB` + `vm.min_free_kbytes=4096` + `oom_score_adj=-900` increased usable free RAM from `6.5 MB` to **`10.6–22.4 MB` (`0` OOM crashes)**. We also caught that multi-key `sysctl -w` aborts on absent kernel keys (`netdev_budget_usecs`), fixing it with a per-key loop so `tcp_limit_output_bytes=65536` applies `100%` (`38/38` AP & `25/25` CPE knobs verified live).
   * **Repo doc:** `docs/STAGE773A_WA_CHAMPION_V13_344WINDOW_FIELD_ROLLOUT_KIT.md`

6. **Ethernet `BQL` (`Byte Queue Limits`) Convex Sweet-Spot (`limit_min=4542` `3×MTU`, `hold_time=800 ms`, BDP-Calibrated PtP):**
   * **What improved:** Aligning `eth0` BQL `limit_min=4542` to match the AP's `4542B` DRR `fq_quantum` (`hold_time=800 ms`) prevented mid-window DQL decay from clipping aggregates, boosting 3-CPE Triple-Play goodput by **`+6.54%`** and cutting `p95`/`p99` RTT by **`-4.54%` / `-7.24%` (`0.00%` IPTV/VoIP loss)**.
   * **Repo doc:** `docs/STAGE55A_M34_M35_BQL_HOLDTIME_AND_OPENWRT_PTP_PROFILE_BENCHMARK.md`

7. **Kernel `.ko` Fast-Path Datapath Pruning (`PtMP Champion v22` & `PtP Champion v9` + Hitless `802.11h CSA`):**
   * **What improved:** Stripping unconsumed `ath_pktlog.ko` DMA overhead, `vow_extstats=0`, and `set_multiq=3` delivered **`+23.35%` 3-CPE sector goodput (`46.53 -> 57.39 Mbps`)**, **`+41.01%` PtP total goodput (`+70.60%` Bulk TCP, `-64.80%` `p95` RTT)** on `PowerBeam 5AC-500`, and **`0.000s` hitless channel hops (`0/80` missed probes)**.
   * **Repo docs:** `docs/STAGE72A_PTMP_KERNEL_KO_FASTPATH_BENCH.md` | `docs/STAGE85A_PTP_CHAMPION_V9_AND_HITLESS_CSA_BENCH.md`

8. **Zero-Touch Dynamic `20 MHz <-> 40 MHz` Auto-Following & `802.11v/ac OPMODE_NOTIF` (`fmx_omn`) MIPS Injector:**
   * **What improved:** Stock `airOS 8` CPEs follow OpenWrt AP `VHT Operation IE` bandwidth changes in **`8.78s–12.10s`** (`-31.28%` IPTV jitter), and we built a standalone `3.6 KB` static MIPS big-endian `OPMODE_NOTIF` action-frame injector (`96/96` byte-exact in QEMU `24Kc`) to negotiate dynamic NSS/width changes without dropping association.
   * **Repo doc:** `docs/STAGE89B_DYNAMIC_20_40MHZ_CHANNEL_WIDTH_AUTO_FOLLOWING_BENCH.md`

9. **`QCA988x` Xtensa Firmware RAM Overlay (`PB-040/050/060` `SGMT` Patcher) & `VHT40` Peer-Phymode Fix:**
   * **What improved:** Zero-flash-touch `/tmp` bind-mount patching of `ath10k` `firmware-2.bin` (`TXOP`/`TID` scheduler/`CCA-AGC`) plus deterministic `wifi down; sleep 2; wifi up` (`WMI_PEER_ASSOC_CMDID` fix) eliminated `30% -> 0.0%` full-MTU loss and boosted `PowerBeam 5AC Gen2` PtP throughput by **`+115.35%` (`24.83–25.47 Mbps`)**.
   * **Repo docs:** `docs/STAGE491A_PBE5AC_PTP_COMPLETE_DOSSIER_AND_SCORECARD.md` | `docs/STAGE662A_PBE5AC_PTP_CHAMPION_V3_VHT40_ROLLOUT_KIT.md` | `docs/STAGE817A_UNIVERSAL_PB060_TRIPLE_PATCH_OPENWRT_AIROS_KIT.md`

10. **`XC` (`Rocket Prism 5AC Gen2`) Active AirPrism `GPIO 13..16` Filter Daemon & `Rocket 2AC Prism` `IRQ 2` Storm Elimination:**
    * **What improved:** Reconstructed the 6-entry 2-bank AirPrism hardware filter table (`ubnt_prism_hook`) for OpenWrt (`95`-board selector) and unbound the `ath_hsr` SPI bit-banging storm on `Rocket 2AC Prism` (`100%` elimination of `15,480` `IRQ 2` interrupts), boosting TCP goodput by **`+13.0%`** and cutting `p50` RTT by **`-54.3%` (`1.63 -> 0.745 ms`)**.
    * **Repo docs:** `docs/STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md` | `docs/STAGE92B_LTU_12X_AND_2AC_PRISM_BENCH.md`

11. **`AF-LTU` (`LTU-Lite` / `LTU-Rocket`) `4096-QAM 12x` Unlock, `80`-Symbol Superframe & Dual-Core Cortex-A9 SMP Pinning:**
    * **What improved:** Mapped `ame_core.ko` + `AD9361` SDR + `Arria 10` FPGA (`4096-QAM` `0x1f` + `2/4/8`-subband `OFDMA`), optimized the `80`-symbol (`61 DL + 19 UL`) superframe via `SimPy`/`pymoo` NSGA-II, and pinned `IRQ 52/53/63/92` across `CPU0/CPU1`, cutting CPU core imbalance by **`-75.31%`**, raising SoC TCP to **`189.81 Mbps` (`+9.86%`)**, and cutting loaded `p50` RTT by **`-12.5%` (`0.42 ms`)**.
    * **Repo docs:** `docs/STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md` | `docs/STAGE99B_LTU_80SYMBOL_SUPERFRAME_SIMPY_PARETO.md` | `docs/STAGE818A_LTU_4096QAM_12X_LDPC_AND_SUPER4096_SAFE_KIT.md`

12. **`MikroTik RouterOS + OpenWrt 802.1Q VLAN/DSCP` End-to-End Co-Design (`CAKE diffserv4 no-wash`):**
    * **What improved:** Preserving `DSCP EF (46) -> VLAN PCP 6 -> WMM AC_VO` and `DSCP AF41 (34) -> VLAN PCP 5 -> WMM AC_VI` across the router-to-AP trunk cut saturated Triple-Play E2E `p50` RTT by **`-54.84%` (`4.39 -> 1.98 ms`)** and `p95` RTT by **`-46.18%` (`7.60 -> 4.09 ms`)**.
    * **Repo docs:** `docs/STAGE7_MULTIVENDOR_PTMP_REPORT.md` | `docs/PUBLIC_OVERVIEW.md`

13. **Zero-False-Positive Bilateral Site-Aware Observability, 18-Node SQLite `Before/After` Daemon & `<1%` CPU RSSI LED Daemon:**
    * **What improved:** Built a 3-tier backbone blast-radius DAG + on-tower Peer-Buddy quorum engine + 18-node persistent SQLite collector (`txpower`, `BQL`, `sysctl`, per-PHY `AQL`/`FQ-CoDel` deltas) that distinguishes backhaul drops from RF contention (`0` false-positive channel changes), plus a zero-fork RSSI LED daemon (`<0.93%` CPU under load).
    * **Repo docs:** `docs/STAGE59A_ZERO_FALSE_POSITIVE_WISP_RF_OBSERVABILITY_AND_GUARIDA_PLAN.md` | `docs/STAGE1239A_GUIA_MAESTRA_INTEGRACION_PWO_Y_CONCIENCIA_BILATERAL_ES.md` | `docs/STAGE1485A_DAEMON_LED_V4_MENOS_05PCT_CPU_BAJO_CARGA_VIVA_ES.md`

Full repo, benchmarks, and field scripts: `https://github.com/wolverin0/openmax`
```

---

## 2. Versión Lista para Copiar en Español (13 Avances de 1 a 3 Líneas + Links al Repo)

```markdown
**Actualización (3 días después) — 13 Avances Probados en Hardware y Campo, Comparativa Triple y Scripts Públicos PtP/PtMP (`openMAX`)**

Resumen directo (1 a 3 líneas por ítem) de todo lo que logramos y medimos en estos 3 días (`https://github.com/wolverin0/openmax`), qué mejora concreta dio cada avance y en qué documento del repo está el detalle técnico:

1. **Comparativa Triple en Hardware (`airOS 8 Stock` vs. `airOS 8 Tuneado` vs. `OpenWrt 24.10.4 Champion`):**
   * **Qué mejoró:** Tunear `airOS 8` original sin flashear baja el ping cargado `p95` un **`-50.3%` (`34.3 -> 17.0 ms`)** y el jitter de VoIP un **`-54.1%` (`1.55 -> 0.71 ms`)**; pasar a `OpenWrt 24.10.4` + nuestro perfil Champion baja el ping en vacío **`~10x` (`22.58 -> 1.93 ms`)** y el ping saturado un **`-86.4%` en DL (`8.43 ms`) / `-88.9%` en UL (`10.37 ms`)**, llegando a **`64.0–78.51 Mbps` TCP en `20 MHz`**.
   * **Doc y scripts:** `docs/BENCHMARK_3WAY_AIROS_STOCK_VS_TUNED_VS_OPENWRT_CHAMPION.md` | `firmware/public_field_kits/README.md`

2. **Scripts Públicos PtP y PtMP Listos para Usar (para `airOS 8 Stock` y para `OpenWrt 24.10.4`):**
   * **Qué subimos:** Dos scripts POSIX `sh` sin dependencias externas con `--dry-run`, `--apply-ram`, `--persist`, `--verify` y `--rollback` para optimizar tanto radios con `airOS 8` original (`/etc/persistent/rc.poststart`) como radios con `OpenWrt 24.10.4` (`--role ptp | ptmp-ap | ptmp-cpe`).
   * **Scripts en el repo:** `firmware/public_field_kits/airos8_ptp_ptmp_tuned_champion.sh` | `firmware/public_field_kits/openwrt24_ptp_ptmp_champion.sh`

3. **3 Paneles Sectoriales + 1 Enlace Troncal PtP Migrados 100% por Aire (`18/18` Radios en `OpenWrt 24.10.4` Linux `6.6.110`, 0 Subidas a Torre):**
   * **Qué mejoró:** Migramos en remoto los 3 sectores (`LiteAP 120`) y todos sus CPEs (`LiteBeam 5AC Gen2` y `NanoStation 5AC Loco`) con watchdog en RAM de `75s`, manteniendo Router/NAT, `nftables flow_offloading` y la interfaz web **LuCI** operativa en los 18 equipos.
   * **Docs en el repo:** `docs/STAGE12_FULL_OPENWRT_SECTOR_AND_UISP_BRIDGE.md` | `docs/CURRENT_STATE.md`

4. **Modo Híbrido Sin Corte (Clientes `airOS 8` Originales Conectados a Paneles `OpenWrt 24.10.4`):**
   * **Qué mejoró:** Destrabamos los 4 candados de interoperabilidad (`ubnt_poll_host_is_ap_valid`, watchdog TDMA de 30s, `allow_80211=1` y admisor `ETH_P_TEB 0x6558` 4-addr WDS) permitiendo que clientes `airOS 8` trafiquen **`78.7 Mbps` UL / `63.6 Mbps` DL en `20 MHz`** contra un AP OpenWrt mientras se migra el panel cliente por cliente.
   * **Doc en el repo:** `docs/STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md`

5. **Fin de los Reinicios por Falta de RAM (64 MB OOM) + Fix del Bug de `sysctl` Multi-Clave en Linux 6.6 (`100% MATCH`, `0 differs`):**
   * **Qué mejoró:** Bajar `fq_memory_limit` de `16 MiB` (25% de la RAM) a `4 MiB` + `vm.min_free_kbytes=4096` + `oom_score_adj=-900` subió la RAM disponible de `6.5 MB` a **`10.6–22.4 MB` (`0` OOMs)**. Además corregimos el aborto silencioso de `sysctl -w` multi-clave ante claves ausentes (`netdev_budget_usecs`), logrando **`38/38` parámetros en AP y `25/25` en CPEs con `0 differs` en vivo**.
   * **Doc en el repo:** `docs/STAGE773A_WA_CHAMPION_V13_344WINDOW_FIELD_ROLLOUT_KIT.md`

6. **Óptimo Convexo de `BQL` (`Byte Queue Limits`) en Ethernet (`limit_min=4542` `3×MTU`, `hold_time=800 ms` y BDP en PtP):**
   * **Qué mejoró:** Alinear `limit_min=4542` al `fq_quantum=4542` del AP (`hold_time=800 ms`) evitó el recorte prematuro de ráfagas DRR, subiendo el goodput Triple-Play de 3 CPEs un **`+6.54%`** y bajando la latencia `p95`/`p99` un **`-4.54%` / `-7.24%` (`0.00%` pérdida en IPTV/VoIP)**.
   * **Doc en el repo:** `docs/STAGE55A_M34_M35_BQL_HOLDTIME_AND_OPENWRT_PTP_PROFILE_BENCHMARK.md`

7. **Poda de Ruta Rápida en Módulos `.ko` (`PtMP Champion v22` y `PtP Champion v9` + Cambio de Canal `802.11h CSA` en `0.000s`):**
   * **Qué mejoró:** Eliminar la telemetría DMA no consumida (`rmmod ath_pktlog`, `vow_extstats=0`) y activar `set_multiq=3` dio **`+23.35%` de goodput en sector PtMP (`46.53 -> 57.39 Mbps`)**, **`+41.01%` de goodput total en PtP (`+70.60%` Bulk TCP, `-64.80%` `p95` RTT)** y salto de canal sin perder un solo ping (**`0/80` probes perdidos**).
   * **Docs en el repo:** `docs/STAGE72A_PTMP_KERNEL_KO_FASTPATH_BENCH.md` | `docs/STAGE85A_PTP_CHAMPION_V9_AND_HITLESS_CSA_BENCH.md`

8. **Seguimiento Automático `20 MHz <-> 40 MHz` y Binario MIPS `fmx_omn` (`802.11v/ac OPMODE_NOTIF`):**
   * **Qué mejoró:** Los CPEs `airOS 8` siguen cambios de ancho de canal del AP OpenWrt en **`8.78s–12.10s`** (`-31.28%` jitter IPTV), y compilamos un inyector estático MIPS big-endian de `3.6 KB` (`fmx_omn`, `96/96` byte-exacto en QEMU `24Kc`) para renegociar NSS/ancho en caliente sin desasociar.
   * **Doc en el repo:** `docs/STAGE89B_DYNAMIC_20_40MHZ_CHANNEL_WIDTH_AUTO_FOLLOWING_BENCH.md`

9. **Parcheo Quirúrgico en RAM del Firmware `QCA988x` (`PB-040/050/060` `SGMT`) y Fix `VHT40` en `PowerBeam 5AC Gen2`:**
   * **Qué mejoró:** Montaje en RAM (`/tmp`) sin tocar flash sobre `firmware-2.bin` (`TXOP`/`TID` scheduler/`CCA-AGC`) más secuencia limpia `wifi down; sleep 2; wifi up` (`WMI_PEER_ASSOC_CMDID`), eliminando la pérdida de `30% -> 0.0%` en `1472B` y subiendo el throughput PtP un **`+115.35%` (`24.83–25.47 Mbps`)**.
   * **Docs en el repo:** `docs/STAGE491A_PBE5AC_PTP_COMPLETE_DOSSIER_AND_SCORECARD.md` | `docs/STAGE662A_PBE5AC_PTP_CHAMPION_V3_VHT40_ROLLOUT_KIT.md` | `docs/STAGE817A_UNIVERSAL_PB060_TRIPLE_PATCH_OPENWRT_AIROS_KIT.md`

10. **Daemon AirPrism Activo (`GPIO 13..16`) para `XC` (`Rocket Prism 5AC Gen2`) y Eliminación del `100%` de `IRQ 2` en `Rocket 2AC Prism`:**
    * **Qué mejoró:** Reconstruimos la tabla de filtros hardware AirPrism (`ubnt_prism_hook`, selector de `95` placas) y eliminamos las `15,480` interrupciones `IRQ 2` por SPI bit-banging en `2.4 GHz`, aumentando el TCP un **`+13.0%`** y bajando el ping `p50` un **`-54.3%` (`1.63 -> 0.745 ms`)**.
    * **Docs en el repo:** `docs/STAGE11_XC_ROCKET_PRISM_AND_AIRPRISM_RE.md` | `docs/STAGE92B_LTU_12X_AND_2AC_PRISM_BENCH.md`

11. **`AF-LTU` (`LTU-Lite` / `LTU-Rocket`) `4096-QAM 12x`, Supertrama de `80` Símbolos y Afinidad SMP Dual-Core Cortex-A9:**
    * **Qué mejoró:** Mapeamos `ame_core.ko` + `AD9361` + `Arria 10` (`4096-QAM` `0x1f` + `OFDMA`), optimizamos la supertrama de `80` símbolos (`61 DL + 19 UL`) con `SimPy`/`pymoo` y aislamos `IRQ 52/53/63/92` entre `CPU0/CPU1`, reduciendo el desbalance de CPU un **`-75.31%`**, subiendo el TCP a **`189.81 Mbps` (`+9.86%`)** y bajando el `p50` cargado un **`-12.5%` (`0.42 ms`)**.
    * **Docs en el repo:** `docs/STAGE11_LTU_MODULATION_4096QAM_AND_ARCH_RE.md` | `docs/STAGE99B_LTU_80SYMBOL_SUPERFRAME_SIMPY_PARETO.md` | `docs/STAGE818A_LTU_4096QAM_12X_LDPC_AND_SUPER4096_SAFE_KIT.md`

12. **Co-Diseño `MikroTik RouterOS + OpenWrt 802.1Q VLAN/DSCP` (`CAKE diffserv4 no-wash`):**
    * **Qué mejoró:** Preservar `DSCP EF -> VLAN PCP 6 -> WMM AC_VO` y `DSCP AF41 -> VLAN PCP 5 -> WMM AC_VI` de punta a punta redujo el ping `p50` bajo saturación Triple-Play un **`-54.84%` (`4.39 -> 1.98 ms`)** y el `p95` un **`-46.18%` (`7.60 -> 4.09 ms`)**.
    * **Docs en el repo:** `docs/STAGE7_MULTIVENDOR_PTMP_REPORT.md` | `docs/PUBLIC_OVERVIEW.md`

13. **Observabilidad Site-Aware Cero Falsos Positivos, Colector SQLite `Antes/Después` de 18 Nodos y Daemon LED RSSI `<1%` CPU:**
    * **Qué mejoró:** Motor bilateral con DAG de radio de explosión + quórum Peer-Buddy en torre + demonio SQLite persistente con sondas extendidas (`txpower`, `BQL`, `sysctl`, `AQL`/`FQ-CoDel`) que distingue caídas de troncal de problemas RF (`0` cambios de canal en falso), más daemon LED sin forks (`0.81%–0.92%` CPU).
    * **Docs en el repo:** `docs/STAGE59A_ZERO_FALSE_POSITIVE_WISP_RF_OBSERVABILITY_AND_GUARIDA_PLAN.md` | `docs/STAGE1239A_GUIA_MAESTRA_INTEGRACION_PWO_Y_CONCIENCIA_BILATERAL_ES.md` | `docs/STAGE1485A_DAEMON_LED_V4_MENOS_05PCT_CPU_BAJO_CARGA_VIVA_ES.md`

Repositorio completo y scripts: `https://github.com/wolverin0/openmax`
```
