<!-- doc-head: Campeon oficial v1 (W355): un valor oficial por perilla para PtP OpenWrt (LiteBeam/PowerBeam 5AC), PtMP OpenWrt AP (LAP-120/LiteAP AC) y CPE OpenWrt, elegido solo con rondas medidas del ledger 1256A (indice W354), regla de conflicto (mas ventanas, luego stage mas nuevo; sin prueba queda fuera), los tres juegos D4 (ledger v19, lectura en vivo, script 29/10) y el diff instalado vs oficial en ptp_colo_ap/sta y panel1/2/3_ap -->
Que cubre: la regla, el valor oficial de cada perilla y su respaldo (stage, ventanas, %), los conflictos, lo que queda afuera y el diff por nodo de produccion.
Estado: offline. 0 SSH, 0 escrituras en radios. El diff es de lectura: aplicarlo exige banco primero y autorizacion del operador.
Datos maquina: artifacts/champion/official_champion_v1.json. Generador: tools/research/build_official_champion.py. Test: tests/test_official_champion.py.
Leer cuando: antes de copiar valores champion a un panel, a PtP-Colo o a una CPE, o antes de disenar el proximo A/B.
<!-- /doc-head -->
# Campeon oficial v1 (W355)

## 1. Regla

- **Entra** solo un valor que una fila CHAMPION o KEPT del ledger 1256A probo con al menos 1 ventana medida.
- **Ventanas de los perfiles PtP:** las filas de perfil 214A (v4) y 385A (v7) no traen ventanas propias. Usan las del perfil (100 y 172), que el propio ledger marca como INFERRED.
- **Conflicto:** gana el valor con mas ventanas; si empatan, el stage mas nuevo. Todo es OpenWrt 24.10.4, asi que "firmware mas nuevo" es lo mismo que "stage mas nuevo".
- **Juegos D4** (ledger v19, lectura en vivo del 29/10, script del 29/10): no tienen ventanas propias. Nunca ganan, solo aparecen como conflicto.
- **Sin prueba queda fuera.** El test `tests/test_official_champion.py` lo verifica con datos sinteticos y con los reales.
- **Rondas PtMP:** el valor sale del texto del brazo probado.
  - `a/b` en `fq_quantum` y `fq_limit` es AP/CPE.
  - Un valor sin rol cuenta solo para el AP, que es el equipo bajo prueba.
  - Los tramos de airOS (XC, XW, Prism) se ignoran.
- **El % es de la ronda o del perfil completo**, no de la perilla sola.

## 2. PtP OpenWrt (42 perillas oficiales, ambos extremos)

| Perilla | Oficial | Respaldo | Pierde (ventanas) |
| :-- | :-- | :-- | :-- |
| AQL BE | 1500/3000 | perfil 214A, 100 | 275A KEPT 2000/4000 (4), **revisar** |
| AQL VI / VO / BK | 5000/12000 | perfil 214A, 100 | - |
| aql_threshold | 24000 | perfil 214A, 100 | 145A 4000, 139A 4500, 275A 3000 (4 c/u), **revisar** |
| fq_quantum / fq_memory_limit | 300 / 4 MiB | perfil 214A, 100 | 123A 3028 y 4542; 139A 3 MiB (4) |
| fq_limit | 512 | perfil 385A, 172, +24,2 % goodput E2E | 139A 1024 (4) |
| BQL limit_max / limit_min / hold_time | 65536 / 0 / 1000 | perfil 214A, 100 | 135A 36288/4542/600, 123A (4) |
| netdev_max_backlog / budget / budget_usecs | 1000 / 300 / 2000 | perfil 214A, 100 | 145A 1500, 139A 480, 135A 6000 (4) |
| tcp_notsent_lowat / tcp_limit_output_bytes | 4294967295 / 262144 | perfil 214A, 100 | 135A 8192, 145A 65536 (4) |
| tx_queue_len | 1000 | perfil 214A, 100 | 135A 256 (4) |

**Resto del perfil 214A:** dev_weight 64, tx_bias 1, eth qdisc 1514/100 ms, fq_initial_quantum 15140, flow_offloading 0, packet_steering 0, min_free_kbytes 4096, optmem_max 20480, tcp_pacing 120/200, tcp_recovery 1, tcp_rmem y tcp_wmem.

**Resto del perfil 385A:** enable_nft_wmm_qos 1, gro_flush_timeout_ns 20000, gro_normal_batch 16, htt_max_ampdu 64, htt_max_amsdu 2, rts off, tcp_autocorking 0, tcp_early_retrans 4, tcp_mtu_probing 1, tcp_slow_start_after_idle 0, tcp_thin_linear_timeouts 1.

**Revisar** quiere decir que una ronda KEPT posterior al perfil eligio otro valor. La regla le da el lugar al perfil por tener mas ventanas, pero esa ronda es la candidata natural al proximo A/B.

## 3. PtMP OpenWrt AP (22 perillas oficiales)

| Perilla | Oficial | Respaldo (ronda, ventanas, % goodput de la ronda) |
| :-- | :-- | :-- |
| fq_quantum / fq_limit | 4542 / 2048 | 37A M17b, 4, +2,65 % (le gana a 3028 de 36A por ser mas nuevo) |
| fq_memory_limit | 4 MiB | 36A M16b, 4, +2,51 % |
| AQL VO | 300/600 | 37A, 4 (le gana a 600/1200 de 36A y a 750/1500 de 24C) |
| AQL VI / BE / BK | 1200/2400 / 1500/3000 / 500/1000 | 36A, 4, +2,51 % |
| aql_threshold | 5000 | 36A, 4 (tambien 24C y 31A) |
| BQL limit_max / limit_min / hold_time | 42392 / 4542 / 800 | 55A M34b, 4, +6,54 % |
| netdev_budget_usecs | 6000 | 52A M33a, 4, +7,02 % (le gana a 20000 de 46A) |
| netdev_budget / dev_weight_tx_bias | 600 / 2 | 46A M29b, 4, +3,49 % |
| netdev_max_backlog / tcp_early_retrans | 1000 / 3 | 42A, 4, +3,21 % |
| tcp_notsent_lowat / tcp_limit_output_bytes | 8192 / 98304 | 41A, 4, +1,46 % |
| tcp_pacing ca / ss | 105 / 140 | 41A, 4 (le gana a 110/150 de 24C) |
| tcp_thin_linear_timeouts / tcp_autocorking | 1 / 0 | 25, 4, +3,66 % |

## 4. CPE OpenWrt (2 perillas oficiales)

- **Oficiales:** fq_quantum 1514 y fq_limit 1024, de 37A M17b (4 ventanas). Son el segundo valor de `a/b`.
- **Sin rol CPE:** ninguna otra ronda medida nombra un valor con rol CPE, asi que el resto queda fuera. Eso incluye AQL, aql_threshold, fq_memory_limit, BQL y los sysctl de v19.

## 5. Los tres juegos D4: conflictos y resolucion

| Perilla | Ledger v19 | En vivo 29/10 | Script 29/10 | Resolucion |
| :-- | :-- | :-- | :-- | :-- |
| AP fq quantum / limit / memoria | 4542/2048/4 MiB | 3028/512/3 MiB | 4542/2048/4 MiB | oficial = v19 = script (37A y 36A); el valor en vivo pierde |
| AP aql_threshold | 5000 | 4000, luego 5000 (W335) | 5000 | coinciden con el oficial (el valor final en vivo) |
| AP netdev_budget_usecs | 20000 (comando v19) | - | - | pierde: 52A midio 6000 |
| CPE fq quantum / limit | 1514/1024 | 300/8192 | 1514/1024 | oficial = v19 = script; el valor en vivo pierde |
| CPE AQL VI / BE / threshold | 1200/2400, 900/1500, 4000 | 5000 (thr) | 1000/2000, 1500/3000, 5000 | **sin oficial**: ninguno se probo (A/B STAGE2816A bloque 2) |
| nf_cal_period (AP y CPE) | 30 | - | 120 | **sin oficial**: ninguno se probo (bloque 3) |

## 6. Por nodo: instalado vs oficial

Las lecturas salen de telemetry.db (solo lectura, hasta seq 11189, 29/10 22:09 ART). fq es la ultima lectura con parametros: panel1 y panel3 a las 15:31 ART, panel2 a las 13:51 ART.

| Nodo | Igual | Distinto (instalado -> oficial) |
| :-- | --: | :-- |
| panel1_ap | 9 | AQL VI 1000/2000 -> 1200/2400; BQL hold 600 -> 800, limit_max 36288 -> 42392; netdev_max_backlog 2048 -> 1000 |
| panel2_ap | 3 | AQL VO/BE/BK (todas 1200/2400) -> 300/600, 1500/3000, 500/1000; threshold 4000 -> 5000; fq 302/512/3 MiB -> 4542/2048/4 MiB; BQL hold 600 -> 800, limit_max 36288 -> 42392; notsent_lowat 4294967295 -> 8192 |
| panel3_ap | 5 | threshold 4000 -> 5000; AQL VI 1000/2000 -> 1200/2400; fq 3028/512/3 MiB -> 4542/2048/4 MiB; BQL hold 600 -> 800, limit_max 36288 -> 42392; notsent_lowat 4294967295 -> 8192 |
| ptp_colo_ap y ptp_colo_sta | 2 | AQL BE 2000/4000 -> 1500/3000; VI/VO/BK 2000/4000 -> 5000/12000; threshold 4000 -> 24000; BQL 36288/4542/600 -> 65536/0/1000 |

**Lectura del diff:**
- **Panel2** es el mas alejado: tiene 10 diferencias y AQL uniforme.
- **Panel1** ya tiene el fq y el AQL del oficial, salvo VI.
- **PtP-Colo:** varios valores instalados coinciden con rondas KEPT medidas: BE 2000/4000 con 275A, threshold 4000 con 145A y BQL con 135A.
  - El oficial los reemplaza por el perfil 214A solo porque tiene mas ventanas, y BE y threshold estan marcados **revisar**.
  - W348 vio que el watchdog de colo reescribe AQL cada 5 s.
  - No conviene aplicar este diff sin un A/B en banco.
- **Sin oficial:** nf_cal_period 120 esta instalado en los 5 nodos y no tiene valor oficial.
- **Sin dato instalado:** 9 perillas por panel y 32 por PtP-Colo no tienen sonda, asi que dicen `sin dato`.

## 7. Fuera del campeon

| Motivo | Perillas |
| :-- | :-- |
| sin prueba (solo D4 o v19) | nf_cal_period (AP y CPE); dev_weight y dev_weight_rx_bias del AP; todo el AQL, BQL y sysctl de CPE salvo fq_quantum y fq_limit |
| depende del enlace | distance_m, coverage_class, txpower_mbm, htmode_label: el valor de banco no sirve en 7 km |
| parametro de la prueba | profile_mode, traffic_mode, tcp_streams, gaming_udp_probe |
| sin AC en el titulo | aql_txq_limit de rondas PtP 123A/140A: no compite con AQL por AC |
| sin valor legible | htt_max_amsdu_ampdu (381A) |

## 8. Limites y defectos encontrados

1. **Defecto del indice W354:** en ptp_colo toma el phy1, que no tiene interfaz y muestra los defaults 5000/12000/24000. Aca se usa el phy del enlace (phy0). Hay que corregir `production_readbacks` en `tools/research/build_knob_index.py`; esta fuera del alcance de W355.
2. **fq en PtP-Colo:** `observation.aqm` no dice de que phy lee, y el nodo tiene 2. Por eso fq queda sin dato instalado.
3. **Lado probado en las filas de titulo PtP:** lo decidio la regla de lado de control de W354. Esas filas solo pierden: ningun valor oficial PtP sale de ellas.
4. **Champions PtP v8 a v13 (407A a 759A):** existen, pero el ledger no trae sus valores. Por eso el oficial PtP es v7 sobre v4.
5. **Fuera de v1:** W349 (fq de poca RAM en banco) y W353 (AQL en PtP-Colo, parcial) no estan en el ledger, asi que no entran.
6. **Fuente de los juegos D4:** la tabla de `docs/STAGE2816A_DISENO_AB_CAMPEON_CANONICO_PTMP_VALLEY_WINDOW_ES.md` y los comandos v19 de `artifacts/autoresearch/champion_state_ledger.json`. Esos comandos se leen en solo lectura y se saltean las lineas por estacion, que traen MACs.

**Regenerar:** `python -m tools.research.build_official_champion --hasta-seq 11189` reproduce este JSON byte a byte. Sin `--hasta-seq` usa la telemetria actual.
