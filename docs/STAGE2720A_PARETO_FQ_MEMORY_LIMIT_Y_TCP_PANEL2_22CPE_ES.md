<!-- doc-head: Wave 281 (2718A-2723A), fq_memory_limit, TCP de lazo cerrado y AQL en Panel2 y Panel3, 100 % offline -->
SIMULATED_MODEL_ONLY. Extiende el modelo 2622A (MAC sin cambios) con TCP de lazo cerrado, cola de driver con AQL por
estación y fq_memory_limit 3/4/6/8 MB. El piso de RAM libre de 14336 kB es inalcanzable: los AP ya tienen menos con la
cola vacía (ABANDON del frente con RAM). Panel2: ningún descarte por memoria, ni siquiera hoy; la mejora de RTT viene de
RTS y coverage class contra nodos ocultos en subida. Panel3: eliminar descartes FQ empeora el RTT. D4 vivo: TARGET_NOT_MET.
Gate: artifacts/verification/stage2723a_wave281_opus1_gate.json.
<!-- /doc-head -->

# Stage 2720A: fq_memory_limit, TCP de lazo cerrado y AQL en Panel2 (22 CPE) y Panel3

## 1. Resumen ejecutivo

- Todo es modelo (SIMULATED_MODEL_ONLY), sin SSH ni red. Recibos:
  [2718A](../artifacts/autoresearch/stage2718a_panel2_panel3_fq_memory_limit_tcp_aql_pareto_receipt.json) y
  [2719A](../artifacts/autoresearch/stage2719a_panel2_22cpe_holdout_validation_receipt.json).
- **ABANDON del frente con RAM >= 14336 kB.** La RAM libre modelada es la RAM idle menos el pico de colas,
  así que nunca supera la idle. Los dos AP medidos (2498A, cola vacía) tienen 11180 kB (Panel3) y 7848 kB
  (Panel1) disponibles: faltan 3156 kB antes de encolar un solo paquete. Ningún valor de fq_memory_limit,
  fq_limit o AQL puede cumplir el piso; habría que liberar RAM por otro lado.
- La búsqueda corrió entonces sobre el problema relajado (RAM como objetivo, no como restricción).
- Panel2, 2719A: OOM_FREE_FRONT_EXISTS_BASELINE_ALREADY_OOM_FREE. Con TCP de lazo cerrado la cola FQ no
  pasa de 150 paquetes, ni con la ráfaga apuntada a la CPE más lenta: 0 descartes por memoria en 12 de 12
  corridas de holdout, incluida la configuración de hoy.
- La única mejora de RTT validada en Panel2 (peor semilla -35,47 %, media 1825 a 424 ms) sale de RTS 512 +
  coverage class 6, que protegen la subida de 22 CPE ocultas entre sí; fq_memory_limit no influye.
- Panel3: los descartes FQ de hoy son por límite de paquetes (fq_limit 512, 0 por memoria). Sacarlos sube el
  RTT en holdout (al menos +55,79 %), porque esos descartes frenan a TCP. Ningún candidato validó en 4 rondas.
- Contrato D4 vivo: TARGET_NOT_MET.

## 2. Qué se modeló

| elemento | valor |
|---|---|
| decisión | RTS 512/1536/apagado x distance 0/450/2275 m x fq_limit 512..8192 x fq_memory_limit 3/4/6/8 MB x AQL BE 500/1000, 1500/3000, 1850/3700, 3000/6000, 5000/12000 µs = 900 por sector |
| línea base | RTS apagado, distance vacía, fq_limit 512, 3 MB, AQL 1500/3000 (lo leído en ambos AP, 2498A) |
| TCP | IW10, delayed ACK, mitad de ventana una vez por RTT, RTO con estimación de RTT; servidor a 15 ms |
| AQL | cola de driver por estación; toma de la FQ mientras su airtime pendiente < low, o < high si el total < 4000 µs |
| estrés | 2 ráfagas por corrida de 8 flujos TCP de 1 MB a una CPE por semilla (2719A agrega siempre la más lenta) |
| RAM | pico (FQ + driver) x 2048 B; idle medida una sola vez en 2498A; AP de Panel2 sin lectura: ASUMIDO LAP-120 |
| objetivos | RTT p95 de sondas bajo carga, goodput TCP, RAM pico |
| restricciones | 0 descartes por memoria y 0 por límite de paquetes en cada semilla de entrenamiento |

Por qué la ráfaga: en una primera corrida sin ella la cola FQ nunca se llenó (0 descartes incluso con
fq_limit 512), mientras panel3_ap descarta en vivo unos 0,55 por segundo. Un arranque lento de 8 flujos a
la vez (speedtest, gestor de descargas) sí la llena.

## 3. Calibración (re-chequeo de 2623A con TCP)

Siguen siendo consistentes con el -75 % medido de 2534A los mismos 2 de 12 escenarios (holgura ACK 25 µs,
NAV 0,8). La referencia pasó de 750 a 450 ráfagas externas por segundo (-68,24 % contra -62,32 %): la
selección no se arrastra sola, se rehizo. Con holgura de 16 µs, RTS empeora en los 6 casos, como antes.

## 4. Panel3

| métrica | línea base (media de 3 semillas) |
|---|---|
| RTT p95 de sondas | 239,68 ms |
| descartes FQ (máximo por semilla) | 978, todos por límite de paquetes, 0 por memoria |
| RAM pico de colas | 1066 kB |

- Grilla completa de 900: 894 sin descartes por memoria y 722 sin ningún descarte; frente real de 292
  puntos, del que NSGA-II encontró el 31,8 % en 4 rondas.
- En holdout, todo candidato sin descartes empeoró el RTT (+55,79 % el mejor; varios por encima de +400 %).
  Con fq_limit 512 los descartes actúan como la señal que frena a TCP en la CPE lenta; al quitarlos la
  cola de .210.9 crece. Cuál es el descarte "bueno" (fq_limit o CoDel) es la pregunta abierta.
- Meta relajada no cumplida: STOP_MAX_ROUNDS tras 4 rondas, 784,9 s (límites 4 rondas y 30 min).

## 5. Panel2 (2719A, 6 semillas de holdout x 2 modos de ráfaga)

| candidato | descartes por memoria | RAM pico | peor cambio de RTT p95 | meta relajada |
|---|---|---|---|---|
| línea base | 0 descartes por memoria | 286 kB (entrenamiento) | referencia | - |
| knee del frente (fq 1024, 4 MB, AQL 500/1000) | 0 | 404 kB | +33,97 % | no |
| menor RTT (RTS 512, 2275 m, fq 4096, 4 MB, AQL 500/1000) | 0 | 1786 kB | -35,47 % | sí |
| menor RAM (fq 4096, 3 MB, AQL 1500/3000) | 0 | 484 kB | 0 % | no |

- Las 100 combinaciones fq_limit x fq_memory_limit x AQL de la subgrilla no tienen descartes: la celda está
  limitada por colisiones de subida (RTT p95 de base cerca de 2 s, 15 % de pérdida de sondas), y el reloj de
  los ACK mantiene corta la cola de bajada del AP.
- El resultado "limitado por memoria" de 2622A venía de ráfagas sin realimentación TCP; con TCP desaparece.

## 6. Contrato Karpathy D4

| término | valor | cumple |
|---|---|---|
| fq_overmemory_delta | incrementos mayores que cero en panel3_ap (telemetry.db); 0 en panel1_ap | no |
| free_ram_kb | 11180 y 7848 kB, por debajo de 14336 (2498A) | no |
| loaded_rtt_p95_delta_pct | UNKNOWN_OFFLINE: no existe una ventana viva antes/después | no |

Meta completa del modelo: TARGET_NOT_MET por la RAM. Meta relajada: Panel2 sí, Panel3 no.

## 7. Límites

Una sola lectura de memoria por AP y ninguna del AP de Panel2; TCP tipo Reno sin SACK ni CUBIC; tráfico
supuesto; sin adaptación de tasa; Panel2 es una celda CSMA hipotética con 15 de 22 filas INFERRED; todas las
CPE ocultas entre sí. No es QoE de campo.

## 8. Próximo paso (no ejecutado, requiere orden del operador)

1. Medir MemAvailable en serie de tiempo en los AP y ver qué procesos ocupan RAM antes de discutir el piso.
2. Panel3: ciclos A/B de fq_limit 512 contra 1024 midiendo RTT y ambos contadores, no solo descartes.
3. Panel2: la evidencia del modelo apunta a la subida (nodos ocultos), no a la memoria de la FQ.

## 9. Verificación

```
python tools/sim/run_stage2718a_fq_memory_tcp_aql_pareto.py --force
python tools/sim/run_stage2719a_panel2_holdout_validation.py --force
python tools/verify/verify_stage2723a_wave281_opus1_gate.py --write
```
