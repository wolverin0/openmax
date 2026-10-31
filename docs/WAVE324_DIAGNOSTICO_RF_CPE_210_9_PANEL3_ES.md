<!-- doc-head: Wave 324 ES: diagnostico RF solo-lectura de cpe_210_9 frente a sus hermanos de Panel3 (cpe_210_235, cpe_210_238) y panel3_ap; la degradacion es exclusiva del enlace, no del sector; hipotesis principal ACK/coverage_class a 2275 m -->
Veredicto: degradacion EXCLUSIVA del enlace de cpe_210_9. Mismo AP, canal 149 (5745 MHz), 20 dBm y mismas ventanas: los dos hermanos andan en MCS 5-8 con 2 streams y menos de 7 tx_failed/min; cpe_210_9 esta en MCS 0-1 con 1 stream y 945-5076 tx_failed/min.
No es el sector: panel3_ap tiene E2E mediana 8 ms y AP->core normal. No es solo el desbalance de cadenas: cpe_210_238 tiene 17-20 dB y anda en MCS 7.
No lo origino PtP-Colo en 5765 MHz: cpe_210_9 ya estaba degradado desde las 14:23 UTC y PtP-Colo paso a ch153 a las 19:14 UTC, sin cambio medible en la ventana siguiente.
Hipotesis principal (sin probar): timing de ACK / coverage_class 0 en el enlace mas largo (2275 m, ~15.2 us ida y vuelta). Bajo airOS el mismo enlace estaba sano (CCQ 94.4%). Probarla requiere una escritura reversible aprobada por el operador.
<!-- /doc-head -->
# Wave 324 - Diagnostico RF de cpe_210_9 (Panel3-Guarida)

Modo 100% lectura: sin SSH ni red, 0 escrituras.
- Fuentes: `tools/observability/telemetry.db` (`mode=ro`, max seq 2378, sha256 de payload recalculado en cada fila),
  los recibos de cutover de Panel3 y de PtP-Colo, y la radiografia airOS del 24/10 (solo campos numericos, sin nombres).
- Tambien la auditoria viva solo-lectura previa 2532A/2534A (via stage2568a).
- Datos maquina: `artifacts/observability/wave324_cpe_210_9_rf_root_cause_20261028.json`.

## Plan de radio y config conocida

| Dato | Valor | Fuente |
| :-- | :-- | :-- |
| Panel3 | ch149, 5745 MHz, 20 MHz, txpower 20 dBm (AP y CPEs) | cutover Panel3 + telemetria |
| PtP-Colo | ch153, 5765 MHz, 20 MHz, desde 19:14 UTC (antes 6035 MHz en airOS) | cutover PtP-Colo + telemetria |
| Adyacencia | canales vecinos sin solape (5735-5755 / 5755-5775); co-ubicacion no establecida en artefactos | - |
| coverage_class | 0 en AP y en cpe_210_9; `distance` sin configurar en ambos | 2532A (vivo, solo lectura) |
| Reintentos | short 7 / long 4 | 2532A |
| Block-ack | 0 TIDs con BA en ambos lados de cpe_210_9: no hay agregacion A-MPDU | 2532A |

## Hermanos bajo airOS (radiografia 24/10, CONFIRMED)

| CPE | Distancia | Ida y vuelta | Senal | Delta cadenas | CCQ | Retry |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| cpe_210_9 | 2275 m | 15.2 us | -62 dBm | 0 dB | 94.4% | 5.6% |
| cpe_210_235 | 1050 m | 7.0 us | -60 dBm | 10 dB | 96.0% | 4.0% |
| cpe_210_238 | 450 m | 3.0 us | -56 dBm | 0 dB | 95.2% | 4.8% |

Con airOS los tres estaban sanos. cpe_210_9 era el mas lejano y estaba balanceado.

## Comparacion OpenWrt por ventana

Ventanas:
- **A** = 14:23-19:14 UTC, antes de que PtP-Colo pase a 5765 MHz;
- **B** = 19:14-20:00, con PtP-Colo ya en 5765;
- **C** = 22:xx, despues de que panel3_ap se reinicio cerca de las 21:05 (otra lane).

En las tablas, "fail/min" es el crecimiento de tx_failed por minuto, contado solo entre muestras del mismo arranque.

**Vista CPE (lo que mide cada CPE de su enlace al AP)**

| CPE | Ventana | E2E p50 mediana | Perdida media | Senal | Cadenas (mediana) | Desbalance | MCS dominante rx/tx | fail/min |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| cpe_210_9 | A | 22 ms | 19.9% | -53 | -55.5/-56 | 2 dB | 0/0, 0/1 | 1006 |
| cpe_210_9 | B | 20 ms | 19.7% | -52 | -54/-59 | 5 dB | 0/0 | n/d |
| cpe_210_9 | C | **61 ms** | **36.4%** | -53 | -62/-54 | 8 dB | 0/0 | **3690** |
| cpe_210_235 | A | 15 ms | 3.5% | -38 | -44/-41 | 3 dB | 7/8, 8/8 | 6.3 |
| cpe_210_235 | C | 22.5 ms | 0% | -39 | -44/-42 | 2 dB | 8/4 | 6.9 |
| cpe_210_238 | A | 14 ms | 1.5% | -44 | -46/-64 | **18 dB** | 7/5, 7/6 | 0.3 |
| cpe_210_238 | C | 23 ms | 2.8% | -43.5 | -46/-63 | 17 dB | 7/4, 7/3 | 2.7 |

**Vista AP (tabla de estaciones de panel3_ap, mapeada por station_id de la prueba de asociacion)**

| Estacion | Ventana | Senal | Desbalance | MCS dominante rx/tx | fail/min (AP->CPE) |
| :-- | :-- | :-- | :-- | :-- | :-- |
| cpe_210_9 | A | -49 | 9 dB | 1/0, 0/0 | 1796 |
| cpe_210_9 | B | -49 | 10 dB | 1/0 | 945 |
| cpe_210_9 | C | -50 | 2 dB | 0/0, 0/1 | **5076** |
| cpe_210_235 | A | -35 | 9 dB | 8/7, 8/8 | 4.3 |
| cpe_210_238 | A | -45 | 1 dB | 5/7, 6/7 | 1.7 |

- Para cpe_210_9, tx_retries casi no se mueve mientras tx_failed sube. Por eso el cociente failed/retries no sirve
  en este enlace; se compara fail/min entre estaciones.
- **AQM de panel3_ap:** fq_overmemory crece despacio (7020 -> 17488 en el arranque anterior). AQL BE pendiente mediana
  0 us en A/B y 104 us en C. E2E del AP: 8 ms en las tres ventanas. Sin congestion del sector.

## Hallazgos

1. **Exclusivo del enlace.** Con el mismo AP, canal, potencia y horario, cpe_210_9 falla 250 a 1000 veces mas por minuto
   que sus hermanos, en ambos sentidos.
2. **No es el sector.** panel3_ap esta sano y los hermanos no pierden paquetes.
3. **El desbalance de cadenas no alcanza.** El -62/-54 solo aparece en la ventana C. En A, cpe_210_9 estaba balanceado
   (2 dB) y ya en MCS 0-1. cpe_210_238 tiene 17-20 dB y anda en MCS 7. El AP ve ~9 dB tanto en cpe_210_9 como
   en el sano cpe_210_235.
4. **PtP-Colo en 5765 MHz no es el origen.** La degradacion existe desde las 14:23 UTC y la ventana B (con PtP en 5765)
   no empeora. Como contribuyente no se puede separar con estos datos.
5. **La ventana C empeoro tras el reinicio de panel3_ap** (61 ms, 36% de perdida). Los hermanos subieron a ~23 ms sin
   perdida. El reinicio vino de otra lane y queda como confusor, sin atribuir.
6. **Hipotesis principal, sin probar: timing de ACK.** cpe_210_9 es el enlace mas largo (2275 m, ~15.2 us ida y vuelta
   contra 7.0 y 3.0 us de los hermanos). OpenWrt corre con coverage_class 0 y distance sin configurar en ambos
   extremos, mientras airOS ajusta el ACK solo y ahi el enlace estaba sano. Un ACK que llega tarde explica:
   - fallos en ambos sentidos con senal suficiente;
   - ninguna sesion de block-ack;
   - que RTS 512 haya ayudado una vez (2534A: tx_failed 4202 -> 1052, RTT 80 -> 20 ms, perdida 16.7%; sin volver
     a la base en A2).
7. **Abiertos:** nodo oculto y reflexion/multitrayecto no se pueden descartar en solo lectura. RTS 512 ayudando es
   compatible tanto con nodo oculto como con ACK tardio.

## Siguiente paso (requiere aprobacion del operador)

- Prueba reversible A1-B1-A2-B2 con watchdog: `distance` cerca de 2300 m (o el coverage_class equivalente) en
  panel3_ap y cpe_210_9, leyendo fail/min, MCS y perdida por ventana.
- El valor del AP aplica a las 3 estaciones, asi que hay que vigilar a cpe_210_235 y cpe_210_238 durante la prueba.
- Si no mejora: inspeccion fisica (alineacion, conectores, linea de vista) y repetir RTS 512 en ciclos completos.

## Limites

- La distancia de 2275 m es la de la radiografia; 2534A advierte que la longitud real del camino es desconocida.
- Los contadores de estacion son acumulativos y se reinician con el arranque; las tasas solo usan pares del mismo arranque.
- No se verifico si PtP-Colo comparte torre con Panel3. Sin afirmacion causal sobre la hipotesis de ACK.
