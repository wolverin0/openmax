<!-- doc-head: Plan de rollout del campeon oficial v2 (W364, Stage 3024A; politica del operador del 30/10 aplicada en W397, Stage 3057A): alcance 1 PtP y los 3 paneles de menos de 15 clientes, a cualquier hora y lo mas rapido posible, precondicion un gate PASS de banco del cambio exacto, aborto contra la banda A/A del mismo equipo medida en la misma corrida (metodo W388), sin piso fijo de memoria (W379), monitoreo con el daemon y el sidecar_e2e (W393), diff exacto por nodo y rollback (tools/champion_kits/NODO/) -->
Que cubre: alcance, precondiciones, orden, diff exacto por nodo, que medir, cuando abortar, como volver atras y que firma el operador.
Estado: plan offline. Nada de esto se ejecuta sin la aprobacion del operador. Politica del operador del 30/10 aplicada el 30/10 (W397).
Fuentes: artifacts/champion/official_champion_v2.json (diff hasta seq 11404), docs/CAMPEON_OFICIAL_V2_ES.md, artifacts/autoresearch/wave388_aa_noise_bands.json, artifacts/autoresearch/wave379_memory_floor_bench.json.
Leer cuando: antes de tocar colas en produccion con el champion v2.
<!-- /doc-head -->
# Plan de rollout del campeon oficial v2

## 0. Alcance (politica del operador, 30/10)

- **Produccion:** 1 PtP (PtP-Colo .62/.54) y los 3 paneles de Guarida con menos de 15 clientes (Panel1, Panel2 y Panel3). Nada mas.
- **Ritmo:** a cualquier hora y lo mas rapido posible. Sin ventana valle y sin la regla de un nodo por noche.
- **Fuera:** `ether2-sw-poe200`, los switches .200/.201, txpower, regdomain y canal; subir a una torre.

## 1. Precondiciones (sin todas, no arranca un nodo)

1. **Gate PASS de banco del cambio exacto.** El mismo diff, con los mismos valores y el mismo kit, paso en banco con su gate en PASS. Un PASS de otro valor u otra combinacion no cuenta.
2. **Kits probados.** El kit de `tools/champion_kits/<nodo>/` pasa sus pruebas nativas: apply, readback, disparo del watchdog con restore y rollback.
3. **Loops de colo.** Los loops de la imagen del 28/10 reescriben el AQL cada 5 s (AP) y cada 10 s (STA). Se reemplazan por los que leen `/etc/fmx_champion.conf`; si no, el cambio se pierde en segundos.
4. **Diff fresco.** Se relee el nodo justo antes de tocarlo. Si un valor ya no es el `instalado` del diff, el kit se niega (exit 3) y el diff se recalcula.
5. **Monitoreo vivo:** daemon before/after con `fmx_before_after_sample_fresh` = 1 y sidecar con filas por minuto del nodo y sus CPE en `fmx_sidecar_e2e_minute` (`check_stale.py` en 0).

## 2. Orden

| Paso | Nodo | Por que en este lugar |
| :-- | :-- | :-- |
| 1 | PtP-Colo (.62 AP y .54 STA, juntos) | Tiene banco espejo con el mismo hardware. Un solo enlace, sin CPE de clientes. |
| 2 | Panel3 | Sector mas chico (3 CPE). Prueba por primera vez el fq del AP. |
| 3 | Panel2 | Diff mas grande (10 perillas), 7 CPE y el contador de drops fq mas alto. Entra con el fq ya probado en Panel3. |
| 4 | Panel1 | Casi en el oficial (4 perillas). Es la referencia del monitor de 72 h. |

Se pasa al siguiente en cuanto el anterior cierra su observacion sin aborto (seccion 5). No hay espera de 24 h.

## 3. Diff exacto por nodo (instalado -> oficial)

| Nodo | Perillas |
| :-- | :-- |
| ptp_colo_ap y ptp_colo_sta (iguales) | AQL VO 2000/4000 -> 300/600, VI 2000/4000 -> 1000/2000, BE 2000/4000 -> 1500/2500, BK 2000/4000 -> 500/1000; aql_threshold 4000 -> 3000; BQL limit_max 36288 -> 24192, hold_time 600 -> 400; netdev_max_backlog 1000 -> 2048; tcp_notsent_lowat 4294967295 -> 8192 |
| panel3_ap | aql_threshold 4000 -> 5000; AQL VI 1000/2000 -> 1200/2400; fq_quantum 3028 -> 4542, fq_limit 512 -> 2048, fq_memory_limit 3145728 -> 4194304; BQL hold_time 600 -> 800, limit_max 36288 -> 42392; tcp_notsent_lowat 4294967295 -> 8192 |
| panel2_ap | AQL VO 1200/2400 -> 300/600, BE 1200/2400 -> 1500/3000, BK 1200/2400 -> 500/1000; aql_threshold 4000 -> 5000; fq_quantum 302 -> 4542, fq_limit 512 -> 2048, fq_memory_limit 3145728 -> 4194304; BQL hold_time 600 -> 800, limit_max 36288 -> 42392; tcp_notsent_lowat 4294967295 -> 8192 |
| panel1_ap | AQL VI 1000/2000 -> 1200/2400; BQL hold_time 600 -> 800, limit_max 36288 -> 42392; netdev_max_backlog 2048 -> 1000 |

**Fuera del rollout:** las perillas sin dato instalado (fq en PtP-Colo, por sus 2 phy) y lo que el campeon v2 no tiene (nf_cal_period, AQL de CPE).

## 4. Que medir antes y despues

| Metrica | Fuente | Prometheus |
| :-- | :-- | :-- |
| RTT y perdida E2E por CPE | sidecar `fmx_sidecar_e2e_minute`: p50/p95/p99 y perdida por minuto desde el lado del core, 1 eco/s | `fmx_sidecar_e2e_rtt_ms`, `fmx_sidecar_e2e_loss_ratio` |
| Trafico y drops por abonado | sidecar `fmx_sidecar_queue_minute` (colas del core, solo lectura) | `fmx_sidecar_queue_bytes_per_second`, `fmx_sidecar_queue_dropped_per_second` |
| RTT por camino | daemon `probes.<camino>` (almafuerte, core, e2e, tower_guarida) | `fmx_before_after_rtt_seconds`, `fmx_before_after_loss_ratio` |
| Retries y MCS | daemon `stations[].tx_retries`, `tx_failed`, `tx.mcs`, `rx.mcs` | `fmx_before_after_extended_probe_value` |
| Drops fq | delta de `memory_aqm_by_phy.phy0.fq_overmemory` (total de drops) | `fmx_before_after_extended_probe_value` (fq_global) |
| Memoria y OOM | daemon `mem_available_kb`; eventos OOM y reinicios por `boot_id` | `fmx_before_after_mem_available_bytes` |
| Etiqueta del perfil | `fmx_profile_id` y `fmx_config_sha256` en cada fila del sidecar | etiquetas del sidecar |

La tabla `fmx_sidecar_before_after_delta` compara cada nodo entre su primer perfil y el ultimo (PRE_CHAMPION_V2 contra CHAMPION_V2).

## 5. Observacion y criterios de aborto

**Banda A/A por corrida.** En cada nodo, justo antes de aplicar, se miden ventanas A/A en ese mismo equipo y en esa misma corrida, con el metodo de W388: ventanas iguales, cuantiles tipo 7, q0,005 de goodput y q0,995 de p95, p99 y perdida.
- Las bandas de banco de W388 (30 ventanas: goodput q0,005 44,5 Mbit/s, p95 q0,995 20,8 ms, p99 q0,995 27,9 ms, perdida q0,995 5 %) son la referencia del metodo, no valores para produccion.
- No hay porcentajes fijos de aborto.

**Pasos de cada nodo:**
1. A/A del nodo (banda propia).
2. Canary: el kit corre con hold de 60 s y watchdog de 45 s, renovado cada 15 s.
3. Ventanas despues del cambio con la misma carga y duracion que el A/A.

**Abortar** (rollback inmediato) si pasa cualquiera de estas:
- **Fuera de banda:** el goodput cae debajo del q0,005 del A/A, o el p95, el p99 o la perdida superan el q0,995 del A/A del mismo equipo.
- **Enlace:** se cae el enlace o la interfaz phy0-ap0/sta0, o una CPE se desasocia y no vuelve en 60 s.
- **Memoria:** aparece un OOM nuevo o el equipo reinicia. **No hay piso fijo de MemAvailable:** W379 no califico ningun piso (en LAP-120 el cruce fue descriptivo, unos 5372 kB, y la Loco tuvo OOM en la linea de base), asi que el 5120 kB del contrato se elimino.
- **Drops fq:** el delta de `fq_overmemory` por minuto supera el q0,995 de su A/A.
- **Datos:** el daemon o el sidecar dejan de reportar el nodo o sus CPE. Sin datos no se sigue.
- **Reclamos:** un reclamo de cliente del sector durante la observacion. La tabla diaria del sidecar sigue bloqueada sin credencial; hasta entonces lo informa el operador.

## 6. Rollback

- **Durante el canary:** el watchdog compartido restaura solo el pre-image exacto si el kit no confirma, o si falla un readback o un chequeo de salud.
- **Despues de confirmar:** `sh /usr/share/fmx_champion/fmx_champion_kit.sh rollback`, el kit de `tools/champion_kits/<nodo>/`. Vuelve el pre-image guardado, el `/etc/rc.local` original y, en PtP-Colo, el loop original.
- **Verificacion:** cada perilla vuelve al `instalado` del diff y las ventanas vuelven a la banda A/A del nodo.

## 7. Que aprueba el operador

| Paso | Aprobacion |
| :-- | :-- |
| 0 | El gate PASS de banco del cambio exacto y los kits probados (precondiciones 1 y 2) |
| 1 | Reemplazar los loops de PtP-Colo e instalar `/etc/fmx_champion.conf` y el kit (escritura persistente en flash) |
| cada nodo | El nodo y el diff releido; el canary y la confirmacion (rc.local con el hook) |
| abort | El rollback no espera aprobacion: se ejecuta y despues se informa |

**Prohibido en todo el rollout:** tocar nodos fuera del alcance de la seccion 0, `ether2-sw-poe200` o los switches .200/.201, y subir a una torre.
