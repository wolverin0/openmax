<!-- doc-head: Campeon oficial v2 (W360): el PtP OpenWrt ahora sale de los recibos de los champions v4..v13 (Stages 214A..759A, 100..340 ventanas medidas), con valores por extremo (ap/sta) cuando difieren; mismo criterio (solo valores medidos, mas ventanas y luego stage mas nuevo); PtMP AP y CPE sin cambios respecto de v1; indice W354 corregido (phy del enlace); que reescribe el AQL de PtP-Colo (dos loops dentro de la imagen del 28/10 mas un script de arranque) y el diff instalado vs oficial por nodo -->
Que cubre: que cambio respecto de v1, el champion PtP v13 perilla por perilla, los valores heredados, los procesos que escriben colas en PtP-Colo y el diff por nodo.
Estado: offline. 0 SSH, 0 escrituras en radios. El diff es de lectura: aplicarlo exige banco primero y autorizacion del operador.
Datos maquina: artifacts/champion/official_champion_v2.json. Generador: tools/research/build_official_champion.py. Test: tests/test_official_champion.py.
Leer cuando: antes de tocar colas en PtP-Colo o en un panel, o antes de disenar el proximo A/B.
<!-- /doc-head -->
# Campeon oficial v2 (W360)

## 1. Que cambio respecto de v1

- **Fuente del PtP:** son los 10 recibos de champion, de `stage214a` (v4) a `stage759a` (v13), en `artifacts/autoresearch/`.
  - Cada recibo trae su set promovido y sus ventanas medidas: 100, 124, 148, 172, 200, 228, 256, 284, 312 y 340.
  - Ya no se usan las filas champion del ledger 1256A, que terminaban en v7 y tenian las ventanas como INFERRED.
- **Regla sin cambios:**
  - Entra solo un valor medido.
  - Gana el que tiene mas ventanas; si empatan, el stage mas nuevo.
  - Los juegos D4 nunca ganan.
  - Sin prueba queda fuera.
- **Por extremo:** si la AP y la STA tienen valores distintos, la perilla aparece dos veces (`fq_quantum[ap]` y `fq_quantum[sta]`).
- **Indice W354 corregido:** `production_readbacks` ahora lee el phy del enlace. En ptp_colo eso es phy0, que da 2000/4000 y threshold 4000. Antes leia phy1, que esta ocioso y muestra los defaults. Hay un test nuevo en `tests/test_build_knob_index.py`.
- **PtMP AP (22) y CPE (2):** quedan igual que en v1. Ver `docs/CAMPEON_OFICIAL_V1_ES.md`, secciones 3 a 5.

## 2. Champion PtP v13 (54 perillas oficiales)

**% medido:** +18,6 % de goodput E2E en S757A-E2E-R9 (perfil completo, ronda que promovio el brazo B).

| Perilla | Oficial | Respaldo | Pierde |
| :-- | :-- | :-- | :-- |
| AQL VO / VI / BE / BK | 300/600, 1000/2000, 1500/2500 (ambos extremos), 500/1000 | v13, 340 | v10 1500/2000 (256); v6 BE 1500/3000; 214A 5000/12000 |
| aql_threshold | 3000 | v13, 340 (lo puso v12) | v5/v6 4000 (148); 214A 24000 |
| fq_quantum | AP 4542, STA 3028 | v13, 340 | v5/v6 3028/1514; 214A 300 |
| fq_limit / fq_memory_limit | 512 / 3 MiB | v13, 340 / v6, 148 (heredado) | 139A 1024; 214A 4 MiB |
| BQL limit_max / limit_min / hold_time | 24192 / 4542 / 400 | v13, 340 / v6, 148 (heredado) / v13 | v6 36288/600; 214A 65536/0/1000 |
| netdev_max_backlog / budget / budget_usecs | 2048 / 600 / 8000 | v13, 340 | v6 1500/480/6000; 214A 1000/300/2000 |
| tcp_notsent_lowat / tcp_limit_output_bytes | 8192 / 262144 | v13, 340 | v12 16384; v6 65536 |
| nf_cal_period | 120 | v13, 340 | v11 180; v10 30 |
| tx_bias / dev_weight | 2 / 48 | v13 / v6 (heredado) | 214A 1 / 64 |
| rts / htt_max_amsdu / htt_max_ampdu | 2346 / 2 / 64 | v13, 340 | v11 off, 3 |

**Resto con 340 ventanas:** enable_nft_wmm_qos 1, gro 16/20000 ns, tcp_early_retrans 3, tcp_comp_sack 250000 ns/16, tcp_autocorking 0, tcp_mtu_probing 1, tcp_slow_start_after_idle 0, tcp_thin_linear_timeouts 1, pacing 120/200, tcp_recovery 1, optmem_max 65536, ani_enable 1, active_fw_stats_poll 0, pktlog_filter 0x0, multicast_querier 1.

**Heredados (INFERRED):** v13 ya no los lista, asi que se toma el ultimo valor que si los listo. Entre parentesis, el champion que los saco de su set:
- tcp_rmem y tcp_wmem (los saco 279A);
- bql_limit_min, dev_weight, fq_memory_limit, fq_initial_quantum 3028, eth qdisc 1514/100 ms, flow_offloading 1, packet_steering 1 y min_free_kbytes 4096 (385A, cuando el set paso a listar solo cambios);
- multicast_to_unicast 1 (511A);
- dtim 2, beacon 100 y tx_queue_len 256 (569A);
- multicast_snooping 0 (679A).

## 3. Que reescribe el AQL en PtP-Colo

La fuente es la imagen OpenWrt del 28/10, que arma `tools/ptp/build_ptp_colo_openwrt_images_20261028.py`. W348 vio los dos loops corriendo, uno en cada extremo.

W348 anoto 5 s para los dos loops. Los periodos de esta tabla salen del codigo del builder, que para la STA dice 10 s.

| Proceso | Extremo | Cuando | Que escribe |
| :-- | :-- | :-- | :-- |
| `/usr/sbin/fmx_panel1_champion_persistence.sh` | ambos | una vez al arrancar (`/etc/rc.local`) | AQL VO 300/600, VI 1000/2000, BE 1500/3000, BK 500/1000; threshold 4000; fq 3028/512/3 MiB; BQL 36288/4542/600; nf_cal 120; sysctl (backlog 2048, notsent 8192, budget_usecs 6000, ...) |
| `/usr/sbin/fmx_ptp_ap_watchdog.sh` | AP | loop cada 5 s (lineas 216-232) | AQL `"$ac 2000 4000"` en las 4 AC; fq_limit 2048 en `aqm/fq_limit` (esa ruta no existe y la escritura falla); `multicast_to_unicast` 0 en los brport |
| `/usr/sbin/fmx_cpe_watchdog.sh` | STA | loop cada 10 s, mas hasta 4 s de ping (lineas 291-317) | el mismo AQL 2000/4000 y la misma escritura fallida de fq_limit; re-enlaza phy0-sta0 y hace `wifi reload` tras 8 pings fallidos |

**Que queda en el equipo** (telemetria, seq 11404):
- El AQL 2000/4000 de las 4 AC es el del loop: pisa al script de arranque a los 5 o 10 s.
- threshold 4000, BQL 36288/4542/600, nf_cal 120 y ani 1 son los del script de arranque.
- Los sysctl del script de arranque no quedaron: backlog 1000 en lugar de 2048, notsent 4294967295 en lugar de 8192. La causa es UNKNOWN y no se puede ver offline.
- El script de arranque no cambio desde el 26/10, antes del build del 28/10. Que la imagen tenga esta misma version es INFERRED, por la fecha del archivo.

**Choques con el oficial:**
- **El loop:** fuerza el AQL uniforme en las 4 AC, contra la jerarquia oficial, y pone multicast_to_unicast 0 contra el 1 oficial. Cualquier A/B o cambio de AQL en colo se pierde en 5 a 10 s si no se cambia el loop.
- **El script de arranque:**
  - threshold 4000 contra 3000;
  - BQL 36288/600 contra 24192/400;
  - en el AP, fq_quantum 3028 contra 4542;
  - budget_usecs 6000 contra 8000;
  - tcp_limit_output_bytes 65536 contra 262144;
  - pacing 110/150 contra 120/200;
  - early_retrans 4 contra 3;
  - optmem 20480 contra 65536.

## 4. Por nodo: instalado vs oficial (telemetria hasta seq 11404, 29/10 noche ART)

| Nodo | Igual | Distinto (instalado -> oficial) |
| :-- | --: | :-- |
| ptp_colo_ap y ptp_colo_sta | 3 | AQL VO/VI/BE/BK 2000/4000 -> 300/600, 1000/2000, 1500/2500, 500/1000; threshold 4000 -> 3000; BQL limit_max 36288 -> 24192, hold 600 -> 400; netdev_max_backlog 1000 -> 2048; notsent_lowat 4294967295 -> 8192 |
| panel1_ap | 9 | AQL VI 1000/2000 -> 1200/2400; BQL hold 600 -> 800, limit_max 36288 -> 42392; netdev_max_backlog 2048 -> 1000 |
| panel2_ap | 3 | AQL VO/BE/BK -> 300/600, 1500/3000, 500/1000; threshold 4000 -> 5000; fq 302/512/3 MiB -> 4542/2048/4 MiB; BQL; notsent_lowat |
| panel3_ap | 5 | threshold 4000 -> 5000; AQL VI -> 1200/2400; fq 3028/512/3 MiB -> 4542/2048/4 MiB; BQL; notsent_lowat |

**PtP-Colo:**
- **Iguales:** ani_enable 1, BQL limit_min 4542 y nf_cal_period 120.
- **fq:** sin dato instalado, porque el nodo tiene 2 phy y `observation.aqm` no dice cual lee.
- **Antes de aplicar** el diff de AQL hay que cambiar el loop, y eso es cambiar la imagen o el script: decision del operador.
- **Cambio respecto de v1:** el diff de colo ya no apunta al perfil v4 (24000 y 65536) sino a v13. 6 de los 9 valores distintos coinciden con champions o rondas medidas mas viejos: 214A, v5/v6, 145A, 135A y 275A.

## 5. Fuera del campeon (sin cambios de criterio)

- **PtMP:** igual que en v1.
  - nf_cal_period, dev_weight y dev_weight_rx_bias del AP: sin ronda medida.
  - CPE: AQL, BQL y sysctl sin rol CPE.
- **PtP, dependen del enlace:** distance_m, coverage_class, txpower_mbm, htmode_label.
- **PtP, parametros de la prueba:** profile_mode, traffic_mode, tcp_streams, gaming_udp_probe y las marcas DSCP voip/iptv/bulk/scavenger.
- **PtP, `bb_timing_29e00_hex`:** es un registro del firmware QCA y queda para el carril de RE binario.
- **PtP, `aql_txq_limit` sin AC:** no compite con el AQL por AC.
- **Kits `99-fmx-wa-universal-champion-v14..v20`:** existen en `firmware/openwrt/`, pero no tienen recibo de champion con ventanas, asi que no entran.

## 6. Limites

1. **Sets parciales desde v7:** a partir de 385A los sets promovidos listan solo lo que cambio. Lo que no aparece se toma como heredado; esta marcado con `heredado` en el JSON.
2. **% del perfil:** sale de la ronda E2E del recibo solo cuando promovio el brazo B; si no, queda sin dato.
3. **Rondas de titulo PtP:** solo pierden; ningun valor oficial sale de ellas.
4. **Diff:** es de lectura. El JSON trae, para cada valor instalado, que champion o ronda lo midio (`instalado_probado_en`).
5. **v1 congelado:** `official_champion_v1.json` queda como registro. El generador actual ya no lo reproduce, aunque el doc v1 diga lo contrario.

**Regenerar:**
- Este JSON: `python -m tools.research.build_official_champion --hasta-seq 11404`.
- El indice: `python -m tools.research.build_knob_index`. Embebe la telemetria actual, asi que su sha cambia con cada corrida.
