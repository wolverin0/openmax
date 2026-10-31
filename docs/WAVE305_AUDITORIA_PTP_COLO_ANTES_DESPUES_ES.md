<!-- doc-head: Wave305 actualizada por Wave322, fuentes fechadas y cohortes ampliadas -->
Auditoría offline con hashes SQLite; CONFIRMED describe registros, INFERRED hipótesis causales.
No se ejecutó SSH ni se modificó la base de telemetría.
<!-- /doc-head -->

# PtP-Colo: Before / After actualizado

Corte SQL reproducible: **2342**.
Reporte agregado fechado: `2026-10-28T22:46:53.181792+00:00`.
El corte histórico documentado abarca `2026-10-28T19:08:46.015478+00:00` a `2026-10-28T19:14:37.815918+00:00`.

## Cohortes y referencias fechadas

| Radio | Before n | After n | Fila del reporte | Última SQL | Nuevas observaciones |
|---|---:|---:|---:|---:|---:|
| ptp_colo_ap | 9 | 11 | 2364 | 2328 | 0 |
| ptp_colo_sta | 9 | 10 | 2365 | 2311 | 0 |

Las referencias del reporte conservan sus hashes originales. Un reporte retrasado es
una instantánea histórica válida, separada de la última fila SQL; no se confunde con corrupción.
Las filas ERROR/BACKOFF se conservan en los conteos de estado y no fabrican RF, RAM ni RTT.
Las últimas filas Before terminaron a las 19:10 UTC, durante el proceso de corte.
Ese tiempo es de cierre de la fila: no fecha cada lectura de RSSI o RAM, que pudo ser previa.

## Señal y frecuencia

| Radio | Before dBm | After SQL dBm | Diferencia reportada dB | Fecha After UTC |
|---|---:|---:|---:|---|
| ptp_colo_ap | -55.0000 | -36.0000 | 19.0000 | 2026-10-28T22:39:12.790890+00:00 |
| ptp_colo_sta | -57.0000 | -34.0000 | 23.0000 | 2026-10-28T22:38:22.300161+00:00 |

**CONFIRMED**: el Before nativo registra airOS 8 en 6035 MHz. El −57 dBm corresponde
al último STA y el AP tuvo −55 dBm; el JSON contiene todas las ventanas, no solo esa pareja.
Estado de la lectura −34 dBm en la cohorte After: `CONFIRMED_RECORDED_AFTER_COHORT`.
Los diagnósticos históricos del corte registran canal 153, **5765 MHz / 20 MHz en ambos radios**.
5805 MHz: `UNKNOWN_AS_OPERATING_FREQUENCY_MENTIONS_ARE_NOT_RUNTIME_PROOF`.
Cada frecuencia permanece ligada a su propia fuente; no se copia al SQL si allí está ausente.

**INFERRED, sin aislamiento causal**: atribuir toda diferencia a firmware, antena o frecuencia.
Cambian controlador, convenciones RSSI, instante, tráfico y ajustes RF no controlados.
La diferencia está expresada en dB; no se calculan porcentajes sobre dBm negativos.

## RTT E2E seleccionado y distribución de ventanas

| Radio | Before p50/p95 ms | After p50/p95 ms | Cambio p50/p95 % |
|---|---:|---:|---:|
| ptp_colo_ap | 0.0000 / 0.0000 | 0.0000 / 1.8000 | null / null |
| ptp_colo_sta | 3.0000 / 10.2000 | 2.0000 / 3.8000 | -33.3333 / -62.7451 |

La comparación es descriptiva entre ventanas del recolector hacia el mismo equipo.
Una disminución porcentual no acredita carga equivalente ni una mejora causal de QoE.
Un Before de 0 ms nativos conserva respuestas reales y hace indefinido el porcentaje.
Los RTT peer de veinte sondas no se mezclan con E2E o core de tres paquetes.

| Radio | Ventanas After E2E válidas | Mediana de p50 por ventana ms | Rango p95 de ventanas ms |
|---|---:|---:|---:|
| ptp_colo_ap | 11 | 0.0000 | 0.0000 / 75.1500 |
| ptp_colo_sta | 10 | 2.5000 | 2.0000 / 12.7000 |

La mediana y el rango de cuantiles de ventanas no son percentiles de paquetes agrupados.
El JSON conserva conteos nativos, muestras y pérdidas; los valores ausentes siguen null.

## MCS y MemFree por instantánea

| Radio | MCS TX/RX último After | MemFree Before KiB | MemFree corte KiB | MemFree último After KiB |
|---|---:|---:|---:|---:|
| ptp_colo_ap | 8.0000 / 8.0000 | 18020.0000 | 13964.0000 | null |
| ptp_colo_sta | 8.0000 / 8.0000 | 9172.0000 | 18364.0000 | null |

Antes no se exportó MCS; no se reconstruye desde una tasa PHY. El STA tenía MCS 8/8
en los diagnósticos iniciales; el índice de cada lectura posterior puede variar.
El reporte omite MemFree Before aunque SQLite lo conserva en `memory_kb.MemFree`.
La RAM inicial del corte y la telemetría SQL posterior permanecen separadas por fuente y fecha.
MemFree no equivale a MemAvailable; una lectura de arranque no diagnostica fugas ni capacidad sostenida.

## Documentación, límites y reproducción

`CURRENT_STATE.md` conserva una afirmación de radios todavía en airOS, superada
como estado actual por el corte registrado y las filas OpenWrt posteriores.
Las incidencias antiguas de CRC permanecen históricas; no se validan retrospectivamente
otras imágenes por el hecho de que estas hayan arrancado. No se editó el documento fuente.
El catálogo conserva hashes de los artefactos PtP-Colo; las menciones de modelos o planes
no se promocionan a medición física. El patrón literal `artifacts/ptp_colo*/` puede no
coincidir con los directorios reales `canary_ptp_colo` y respaldos `stage2538a_ptp_colo_mtd_backups`.

`python tools/observability/build_wave305_ptp_colo_before_after_audit.py --check`

El límite SQL permite reproducir el resultado aunque se anexen muestras nuevas.
