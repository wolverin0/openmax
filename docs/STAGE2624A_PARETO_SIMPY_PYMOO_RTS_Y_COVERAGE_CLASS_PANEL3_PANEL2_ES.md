<!-- doc-head: Wave 266 (2622A-2627A), Pareto SimPy + pymoo NSGA-II de RTS, coverage class y fq_limit, 100 % offline -->
SIMULATED_MODEL_ONLY: DCF con nodos ocultos entre CPE, timeout de ACK/CTS por coverage class, interferencia en la CPE,
FQ de mac80211 (fq_limit, fq_memory_limit, CoDel). Panel3 (3 CPE, 450-2275 m) y Panel2 (22 CPE, 259-2674 m, 15 INFERRED).
2623A calibra contra el único ciclo RTS 512 de 2534A. Panel3: frente factible desde fq_limit 2048 y candidato validado
en holdout (RTS 1024 + fq_limit 2048). Panel2: ninguna configuración sin descartes FQ, manda el límite de memoria de 3 MB.
Contrato D3 vivo: TARGET_NOT_MET. Gate: artifacts/verification/stage2627a_wave266_opus1_gate.json.
<!-- /doc-head -->

# Stage 2624A: Pareto SimPy + pymoo de RTS, coverage class y fq_limit en Panel3 y Panel2

## 1. Resumen ejecutivo

- Todo es modelo (`SIMULATED_MODEL_ONLY`): ningún radio fue contactado. La única referencia viva es el
  ciclo RTS 512 revertido de 2534A ([2535A](STAGE2535A_DIAGNOSTICO_CADENAS_Y_PRUEBA_RTS512_PANEL3_CPE9_ES.md)).
- Calibración (2623A): de 12 escenarios, solo 2 reproducen el -75 % medido con RTS 512. Los dos
  suponen que el timeout de ACK/CTS por defecto ya cubre los 2275 m y que el 80 % de la interferencia
  cerca de .210.9 respeta el NAV del CTS. Con holgura de 16 µs, RTS empeora los fallos en los 6 casos.
- Panel3: 105 de 210 configuraciones no tienen descartes FQ, todas con fq_limit 2048 o más. NSGA-II
  encontró los 21 puntos del frente real (recall 1,0 contra la grilla completa).
- Candidato Panel3 validado en 4 semillas de holdout pareadas: RTS 1024, distance 450 m (coverage
  class 1), fq_limit 2048. Fallos de .210.9 entre -62,34 % y -86,32 % contra la línea base y 0
  descartes FQ; también cumple en el otro escenario consistente (peor semilla -57,89 %).
- Panel2: 0 de 210 configuraciones sin descartes. Con fq_limit 2048 o más el backlog topa en 1536
  paquetes (3 MB a 2048 B por paquete) y aparecen 1505 descartes por memoria. Hace falta mover
  fq_memory_limit, que no está en el espacio de decisión, o tráfico con realimentación TCP.
- Contrato D3 vivo: TARGET_NOT_MET. El modelo no puede cambiar ninguno de sus tres términos.

## 2. Qué se modeló

| elemento | valor |
|---|---|
| sectores | Panel3: .210.238 450 m, .210.235 1050 m, .210.9 2275 m (3 CONFIRMED). Panel2: 22 CPE, 259-2674 m (7 CONFIRMED, 15 INFERRED) |
| Panel2 | hoy corre airOS (TDMA); aquí es una celda CSMA/CA hipotética posterior a la migración |
| decisión | RTS 256/512/1024/1536/apagado x distance 0/450/900/1350/1800/2250/2275 m (coverage class 0/1/2/3/4/5/6) x fq_limit 256/512/1024/2048/4096/8192 = 210 por sector |
| línea base | RTS apagado, distance vacía, fq_limit 512 (lo que hoy tiene Panel3) |
| objetivos | mínimo de fallos de la CPE más lejana (MPDU descartadas tras agotar reintentos), mínimo p95 de sondas, máximo goodput |
| restricción | 0 descartes FQ en cada semilla de entrenamiento (todo descarte de fq_tin_enqueue) |
| .210.9 | 6,5 Mbit/s MCS0 NSS1 y sin agregación, como se leyó en vivo en 2532A |
| colas | fq_limit global, fq_memory_limit 3145728 B a 2048 B por paquete (medido en telemetry.db), descarte del flujo más gordo, CoDel 20/100 ms, DRR de airtime |
| semillas | entrenamiento 262201-262203, holdout 262211-262214, calibración 262231-262233; 15 s medidos por corrida |

Con 2275 m, `iw` redondea hacia arriba: 2250 m da coverage class 5 y 2275 m da 6. Cada clase suma
3 µs al slot, al timeout de ACK y al de CTS.

## 3. Calibración contra 2534A (2623A)

Cambio de fallos de .210.9 con RTS 512 contra RTS apagado (coverage class 0, fq_limit 512). Banda
aceptada: -84,96 % a -50,6 %; medido: -74,96 % (B contra A), -69,39 % contra el promedio de A y A2.

| holgura ACK/CTS | interferencia lejana | NAV protege | cambio modelado | consistente |
|---|---|---|---|---|
| 25 µs | 450/s | 0,8 | -82,69 % | sí |
| 25 µs | 750/s | 0,8 | -75,19 % | sí (referencia) |
| 25 µs | 450/s y 750/s | 0,5 | +47,83 % y +42,74 % | no |
| 25 µs | 200/s | 0,5 y 0,8 | conteos de 1 a 7 fallos | no |
| 16 µs | 200/450/750/s | 0,5 y 0,8 | de +70,81 % a +1061,36 % | no |

- Si el timeout quedara corto a 2275 m, el CTS también llegaría tarde y RTS empeoraría: el ciclo
  medido no encaja con esa hipótesis dentro del modelo.
- En el escenario de referencia el p95 de las sondas de .210.9 pasa de 40,07 a 6,59 ms con RTS 512
  (medido: RTT 80 a 20 ms). La pérdida de ping de 16-21 % no se reproduce: las sondas chicas
  sobreviven la cadena de reintentos en todos los escenarios.
- Es una verificación sobre un solo ciclo sin duraciones: selecciona escenarios, no valida el modelo.

## 4. Panel3: frente de Pareto (escenario de referencia, media de 3 semillas)

| RTS | distance (coverage class) | fq_limit | fallos .210.9 | p95 sondas | goodput |
|---|---|---|---|---|---|
| apagado (línea base) | vacía (0) | 512 | 14,24 % | 45,58 ms | 3,39 Mbit/s |
| 512 o 1024 | 450 m (1) | 2048 o más | 1,42 % | 4,88 ms | 4,09 Mbit/s |
| 512 o 1024 | vacía (0) | 2048 o más | 1,55 % | 5,66 ms | 4,09 Mbit/s |
| 512 o 1024 | 1350 m (3) | 2048 o más | 1,34 % | 6,54 ms | 4,07 Mbit/s |
| 256 | 900 m (2) | 2048 o más | 1,38 % | 6,03 ms | 4,07 Mbit/s |

- La línea base tuvo hasta 1348 descartes FQ por semilla, todos por límite de paquetes y ninguno por
  memoria. Con fq_limit 1024 todavía quedan al menos 262; desde 2048 no hay ninguno.
- RTS 512 y 1024 dan resultados idénticos: las tramas de datos son de 1500 B (superan los dos
  umbrales) y las sondas de 100 B no llegan a ninguno. RTS 1536 deja sin RTS las tramas sueltas de
  .210.9, que es justo lo que las protege.
- Las diferencias entre coverage class 0, 1, 2 y 3 son chicas y dependen del modelo (un slot más
  largo acorta la ventana en que un nodo oculto termina su backoff); no son una recomendación.

### 4.1 Holdout del candidato RTS 1024, distance 450 m, fq_limit 2048

| semilla | fallos base | fallos candidato | cambio | descartes FQ base | candidato | p95 sondas base a candidato |
|---|---|---|---|---|---|---|
| 262211 | 140 | 38 | -72,86 % | 1303 | 0 | 27,68 a 6,59 ms |
| 262212 | 95 | 13 | -86,32 % | 663 | 0 | 29,15 a 5,27 ms |
| 262213 | 105 | 36 | -65,71 % | 1305 | 0 | 37,58 a 8,98 ms |
| 262214 | 77 | 29 | -62,34 % | 1512 | 0 | 271,47 a 50,10 ms |

Lo que sostiene el resultado es el par RTS 1024 (o 512) + fq_limit 2048; la distance de 450 m es
incidental (ver la nota sobre coverage class arriba) y no es una recomendación de escribir `distance`.

El otro candidato del frente (RTS 1024, 1350 m, fq_limit 8192) llegó a -67,62 % en la peor semilla
pero tuvo 65 descartes por memoria en la semilla 262213: con fq_limit por encima de 1536 paquetes el
límite que manda es fq_memory_limit, también en Panel3. El cero del candidato elegido depende de
que ninguna ráfaga de holdout llenara 3 MB.

## 5. Panel2: sin configuración factible

| fq_limit | configuraciones factibles | mínimo de descartes FQ | de ellos por memoria | backlog máximo |
|---|---|---|---|---|
| 256 | 0 de 35 | 6630 | 0 | 256 |
| 512 | 0 de 35 | 4499 | 0 | 512 |
| 1024 | 0 de 35 | 2581 | 0 | 1024 |
| 2048, 4096, 8192 | 0 de 35 cada uno | 1505 | 1505 | 1536 |

- Las tres rondas de NSGA-II (44, 50 y 49 configuraciones) y la grilla completa coinciden: 0 de 210.
- La menos mala: RTS 1536, distance vacía, fq_limit 2048 o más (1505 descartes por memoria, fallos de
  .210.21 a 2674 m 9,19 %, p95 10,45 ms, 34,21 Mbit/s). La línea base de Panel2 tiene 4499 descartes,
  todos por límite de paquetes.
- Las ráfagas son de lazo abierto, sin control de congestión TCP: sobrestiman el backlog simultáneo
  de 22 CPE. El resultado dice que con este tráfico 3 MB no alcanzan, no que Panel2 sea inviable.

## 6. fq_limit y los contadores exportados

En telemetry.db (solo lectura) el contador exportado `fq_overlimit` vale 0 en todas las muestras de
panel3_ap mientras `fq_overmemory` crece, y `fq_memory_usage / fq_backlog` da 2048 B por paquete.
Si el backport coincide con upstream, donde 2631A y 2632A documentan que las etiquetas de debugfs
están invertidas, el contador que crece cuenta todos los descartes y el de memoria es 0: los
descartes de Panel3 vienen de fq_limit 512 (512 x 2048 B = 1 MB, lejos de 3 MB). El modelo reporta
los dos contadores por separado y su restricción exige 0 en ambos. Estado: HIPÓTESIS condicionada a
que el backport siga a upstream.

## 7. Contratos Karpathy

| contrato | resultado |
|---|---|
| modelo (Panel3, holdout: peor semilla <= -50 % y 0 descartes FQ) | MODEL_TARGET_MET en la ronda 1 |
| modelo (Panel2) | no validado en 3 rondas; STOP_MAX_ROUNDS a los 221,6 s (límite 3 rondas y 30 min) |
| D3 vivo | TARGET_NOT_MET |

| término D3 vivo | valor | cumple |
|---|---|---|
| panel3_admitter_running | UNKNOWN_OFFLINE (sin SSH no se lee la tabla de procesos) | no |
| cpe_210_9_tx_failed_delta_pct | -74,96 % en un solo ciclo revertido | numéricamente sí, sin persistencia |
| fq_overmemory_delta | incrementos mayores que cero en telemetry.db | no |

El gate 2627A recalcula los tres términos desde el disco y vuelve a simular la línea base y el
candidato de Panel3 para comprobar que el recibo es reproducible.

## 8. Límites del modelo

Sin calibración más allá de un ciclo revertido; ráfagas sin realimentación TCP; sin adaptación de
tasa; A-MPDU todo o nada; sin acoplamiento entre celdas; interferencia externa solo en la CPE con
tasa supuesta proporcional a (d/2275)²; todos los pares de CPE ocultos entre sí. No es QoE de campo
y no se afirma inviabilidad global de nada.

## 9. Próximo paso (no ejecutado, requiere orden del operador)

1. Panel3: ciclos A/B alternados y cronometrados de fq_limit 512 contra 2048 mirando ambos contadores
   exportados, separados de los ciclos de RTS de 2535A.
2. Medir el trayecto real de .210.9 antes de escribir `distance`; el modelo no justifica tocarla.
3. Panel2: decidir fq_memory_limit antes de cualquier migración.

## 10. Verificación

```
python tools/sim/run_stage2622a_mixed_distance_rts_coverage_fq_pareto.py --force
python tools/verify/verify_stage2627a_wave266_opus1_gate.py --write
python -m pytest tests/test_stage2622a_to_2627a_suite.py -q
```
