<!-- doc-head: Wave314, profundidad y distribuciones Before/After de 18 nodos -->
SQLite se leyó en una transacción de solo lectura, sin SSH ni cambios en equipos.
Los conteos son observaciones guardadas; no se confunden con paquetes ni con ensayos independientes.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Profundidad muestral de 18 nodos

## Unidad y criterios
Corte reproducible: secuencia SQL máxima **2414**; las filas posteriores no cambian este análisis.

## Estado observado en la última muestra elegible

CONFIRMED: 18/18 últimas muestras elegibles registran OpenWrt 24.10.4;
el roster contiene 0 nodos stock híbridos. MemFree nativo está presente en
18/18 últimas muestras After. Esto describe el corte guardado, sin consulta viva.

| Nodo | Secuencia After | MemFree KiB |
|---|---:|---:|
| cpe_200_169 | 2410 | 15784.0000 |
| cpe_200_183 | 2412 | 10692.0000 |
| cpe_200_213 | 2408 | 11308.0000 |
| cpe_200_223 | 2403 | 10776.0000 |
| cpe_200_41 | 2384 | 10952.0000 |
| cpe_200_80 | 2404 | 16276.0000 |
| cpe_210_166 | 2409 | 12308.0000 |
| cpe_210_21 | 2413 | 12416.0000 |
| cpe_210_235 | 2406 | 10392.0000 |
| cpe_210_238 | 2407 | 11160.0000 |
| cpe_210_239 | 2411 | 11696.0000 |
| cpe_210_83 | 2414 | 12264.0000 |
| cpe_210_9 | 2405 | 10660.0000 |
| panel1_ap | 2379 | 10264.0000 |
| panel2_ap | 2380 | 12708.0000 |
| panel3_ap | 2381 | 7408.0000 |
| ptp_colo_ap | 2382 | 6964.0000 |
| ptp_colo_sta | 2383 | 7684.0000 |

La cobertura actual de RAM no rellena filas históricas sin MemFree. Para cpe_200_80,
los registros airOS previos no cuentan como ventanas OpenWrt; el cambio de plataforma
puede reducir n After frente al informe anterior sin borrar ninguna fila SQLite.


Roster de 18 IDs/IP únicos fijado por el registro. Before exige referencia explícita y hash
en `fmx_airos_before_baselines`; After exige plataforma/estado elegible e identidad exacta.
Una secuencia Before no se cuenta otra vez en After. ERROR/BACKOFF y host no verificado se excluyen.
El historial stock previo de nodos ahora OpenWrt queda excluido de su fase After actual.

`n_with_rtt` cuenta ventanas E2E del recolector con respuestas nativas, conteos enteros,
destino exacto y p50 recomputado. Un ping peer/core/RF no sustituye E2E ni una referencia
histórica escalar sustituye paquetes ausentes. Se admiten pérdida parcial y RTT nativo de 0 ms.
Los p10/p50/p90 e IQR principales describen **p50 por ventana E2E**, en ms:
interpolación lineal (n−1)·p; IQR = p75−p25. No son percentiles del total de paquetes.

## Las 36 distribuciones de fase

| Nodo | Fase | n total | n RTT | n señal | n MemFree | p10 ms | p50 ms | p90 ms | IQR ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| cpe_200_169 | before | 1 | 0 | 1 | 1 | null | null | null | null |
| cpe_200_169 | after | 14 | 14 | 14 | 3 | 17.5500 | 27.5000 | 45.8000 | 13.5000 |
| cpe_200_183 | before | 1 | 0 | 1 | 1 | null | null | null | null |
| cpe_200_183 | after | 15 | 15 | 15 | 4 | 8.0000 | 17.0000 | 35.8000 | 10.0000 |
| cpe_200_213 | before | 1 | 0 | 1 | 1 | null | null | null | null |
| cpe_200_213 | after | 14 | 14 | 14 | 4 | 6.0000 | 18.0000 | 43.4000 | 29.2500 |
| cpe_200_223 | before | 1 | 0 | 1 | 1 | null | null | null | null |
| cpe_200_223 | after | 264 | 261 | 264 | 4 | 5.0000 | 9.0000 | 20.0000 | 8.0000 |
| cpe_200_41 | before | 1 | 0 | 1 | 1 | null | null | null | null |
| cpe_200_41 | after | 266 | 262 | 266 | 3 | 5.0000 | 9.0000 | 24.0000 | 8.0000 |
| cpe_200_80 | before | 1 | 0 | 1 | 0 | null | null | null | null |
| cpe_200_80 | after | 2 | 2 | 2 | 2 | 19.1000 | 19.5000 | 19.9000 | 0.5000 |
| cpe_210_166 | before | 1 | 0 | 1 | 1 | null | null | null | null |
| cpe_210_166 | after | 15 | 15 | 15 | 4 | 7.4000 | 16.0000 | 23.6000 | 11.5000 |
| cpe_210_21 | before | 1 | 0 | 1 | 1 | null | null | null | null |
| cpe_210_21 | after | 12 | 12 | 12 | 2 | 20.5500 | 27.0000 | 58.6000 | 11.5000 |
| cpe_210_235 | before | 1 | 0 | 0 | 1 | null | null | null | null |
| cpe_210_235 | after | 262 | 262 | 262 | 4 | 7.0000 | 15.0000 | 34.9000 | 12.0000 |
| cpe_210_238 | before | 1 | 0 | 0 | 1 | null | null | null | null |
| cpe_210_238 | after | 231 | 230 | 231 | 4 | 5.9000 | 14.0000 | 33.2000 | 14.0000 |
| cpe_210_239 | before | 1 | 0 | 1 | 1 | null | null | null | null |
| cpe_210_239 | after | 15 | 14 | 15 | 4 | 8.3000 | 19.5000 | 31.8000 | 13.5000 |
| cpe_210_83 | before | 1 | 0 | 1 | 1 | null | null | null | null |
| cpe_210_83 | after | 15 | 14 | 15 | 4 | 8.6000 | 19.0000 | 28.8000 | 13.2500 |
| cpe_210_9 | before | 1 | 0 | 0 | 1 | null | null | null | null |
| cpe_210_9 | after | 145 | 140 | 145 | 4 | 9.9000 | 23.7500 | 116.9500 | 44.2500 |
| panel1_ap | before | 1 | 0 | 1 | 1 | null | null | null | null |
| panel1_ap | after | 270 | 263 | 270 | 3 | 4.0000 | 8.0000 | 16.8000 | 7.2500 |
| panel2_ap | before | 21 | 21 | 21 | 21 | 3.0000 | 8.0000 | 12.0000 | 6.0000 |
| panel2_ap | after | 14 | 14 | 14 | 3 | 6.3000 | 12.5000 | 18.0000 | 6.3750 |
| panel3_ap | before | 1 | 0 | 0 | 1 | null | null | null | null |
| panel3_ap | after | 270 | 268 | 270 | 3 | 4.0000 | 8.0000 | 18.0000 | 8.0000 |
| ptp_colo_ap | before | 9 | 9 | 9 | 9 | 0.0000 | 0.0000 | 3.0000 | 0.0000 |
| ptp_colo_ap | after | 14 | 14 | 14 | 3 | 0.0000 | 0.0000 | 2.4000 | 1.0000 |
| ptp_colo_sta | before | 9 | 9 | 9 | 9 | 1.8000 | 3.0000 | 15.6000 | 5.0000 |
| ptp_colo_sta | after | 13 | 13 | 13 | 3 | 2.0000 | 3.0000 | 12.4000 | 7.0000 |

## Nodos con menos de cinco ventanas RTT After válidas

| Nodo | IP | n RTT After | Ventanas adicionales para n=5 |
|---|---|---:|---:|
| cpe_200_80 | 198.18.0.16 | 2 | 3 |

Se necesitan observaciones adicionales, no solo más paquetes dentro de la misma ventana.
El umbral n=5 es el criterio de profundidad pedido; no acredita potencia estadística ni QoE.
Un IQR de cero con n=1 tampoco demuestra estabilidad.

## Señal, memoria y procedencia

El JSON añade p10/p50/p90/IQR para señal y MemFree. Señal por ventana es la mediana
de los peers válidos cuando no hay escalar nativo; conserva origen AP, CPE o vista de asociación.
También se publica la distribución de lecturas peer: tiene otro denominador y dependencia
por AP, estación y tiempo. No se interpreta como un RSSI físico único ni se mezcla con RTT.
Se descartan valores sin unidad dBm verificable; un registro modelado permanece identificado.

MemFree se normaliza desde `memory_kb.MemFree`, `memory.mem_free_kib` y alias explícitos
KiB. MemAvailable no es MemFree; dos alias contradictorios se excluyen y se contabilizan.
Una ausencia permanece null y nunca se rellena con cero.
Las importaciones históricas aparecen separadas de las observaciones nativas: n total no
equivale a ventanas experimentales independientes. El JSON conserva clases, exclusiones,
orígenes, pérdida parcial, paquetes recibidos y secuencias de las ventanas RTT válidas.

## Reproducción

El manifiesto contiene secuencia, fase y hash de cada payload dentro del roster y del
límite SQL congelado. La comprobación permite filas nuevas posteriores a ese límite.

`python tools/observability/build_wave314_sample_depth_audit.py --check`

No se certifica salud actual, causalidad ni capacidad de producción con estos conteos.

El alias nativo `mem_free_kb` conserva la unidad KiB de `/proc/meminfo`; valores
duplicados coincidentes cuentan una vez. MemAvailable conserva su significado distinto.
