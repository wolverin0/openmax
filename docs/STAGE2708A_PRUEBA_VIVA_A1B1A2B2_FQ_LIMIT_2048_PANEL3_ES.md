<!-- doc-head: Wave279, guarda de memoria de Panel3 y captura pasiva sin ajuste fq_limit -->
La prueba A1/B1/A2/B2 quedó sin ejecutar: MemAvailable estaba por debajo de 14336 kB.
Se conservaron lecturas nativas, pings y una sola instancia del admitter; no hubo escrituras RF.
<!-- /doc-head -->
# Panel3: candidato fq_limit 2048 detenido por la guarda de memoria

## Alcance y decisión

Se autorizó comparar 512 contra 2048 en RAM, con cuatro ventanas de 30 s
y retorno autónomo de 60 s. La condición previa era MemAvailable ≥14336 kB.
El primer preflight leyó 7184 kB, fq_limit 512 y kernel 6.6.110.
La captura definitiva comenzó con 7576 kB y llegó a un mínimo de 6504 kB.
Por ello no se escribió fq_limit, no se armó el watchdog y no se ejecutó B.
No se liberó memoria, reinició WiFi ni modificó ningún servicio para forzar la prueba.

## Procedencia y límites del candidato

Stage2624A es un modelo SimPy/pymoo, no una promoción de hardware.
Su candidato combina RTS, distancia y fq_limit; la prueba pedida aquí
aislaba solamente fq_limit. Ese cambio aislado no fue aplicado.
La nota Stage2684A mantiene abierta W271-H3 y el significado causal
del rótulo fq_overmemory en este backport. Se conservan los nombres
nativos sin convertir el contador en prueba de una causa de descartes.
Las cifras históricas de Panel1 y la eliminación de duplicados de
Stage2496A son contexto; no constituyen un control pareado de esta prueba.

## Observación pasiva real

Se observaron 33,07 s sin cambios de parámetros, con siete muestras de
AQM, /proc/meminfo y el proceso exacto /usr/sbin/panel3_admitter.sh.
En todas las muestras y en una sesión SSH final independiente hubo una
sola instancia del admitter. Esto demuestra presencia en esos instantes,
sin afirmar supervisión continua entre muestras.

| Dato pasivo | Resultado |
| --- | --- |
| fq_limit antes/final | 512 / 512 |
| fq_overmemory: delta entre extremos pasivos | 0 |
| fq_overlimit: delta entre extremos pasivos | 0 |
| fq_memory_usage: cambio entre extremos | +10240 bytes |
| MemAvailable mínimo/final | 6504 / 6528 kB |
| CPE .210.9 | 20/30 respuestas, p95 104,928 ms |
| CPE .210.235 | 0/30 respuestas, p95 desconocido |
| CPE .210.238 | 0/30 respuestas, p95 desconocido |

No se observó DUP en estas salidas. El p95 usa el rango más cercano
superior sobre las respuestas recibidas; no imputa RTT a paquetes perdidos.
No se resolvió de forma inequívoca el enlace entre las IP objetivo y los
contadores por estación: tx_failed comparativo permanece UNKNOWN.
Las pérdidas corresponden a las sondas pasivas registradas y no demuestran
una causa RF, una regresión por el candidato ni indisponibilidad física.

El primer intento de captura pasiva encontró una carrera de lectura de
/proc cuando desapareció un proceso. Se preservaron su recibo y código;
la reparación tolera únicamente esa desaparición al censar procesos.
El segundo intento completó la observación. Ninguno aplicó el candidato.

## Persistencia y cierre

Stage2707 agrega una sola fila pasiva al esquema existente de telemetry.db,
con payload completo, hash y lectura SQL independiente. No crea cuatro
ventanas experimentales ni modifica filas anteriores.
MemoryMaster y el ledger CRLF registran el bloqueo sin promoción.

| Meta | Estado |
| --- | --- |
| panel3_admitter_running | confirmado en las muestras |
| cpe_210_9_tx_failed_delta_pct ≤ −50% | UNKNOWN: no existe comparación A/B |
| fq_overmemory_delta == 0 en candidato | no medido; el cero pasivo no lo sustituye |

El gate queda INCOMPLETE por memoria insuficiente y prueba sin ejecutar.
Los tests locales verifican trazabilidad y rechazo de afirmaciones falsas;
no son ventanas de tráfico ni validación de rendimiento del candidato.
Máximo autorizado: tres rondas y 30 minutos; rondas A/B ejecutadas: cero.

- [Captura nativa](../artifacts/autoresearch/stage2706a_panel3_fq_limit_2048_a1b1a2b2_receipt.json)
- [Persistencia SQLite](../artifacts/autoresearch/stage2707a_panel3_fq_limit_telemetry_db_receipt.json)
- [Gate](../artifacts/verification/stage2711a_wave279_codex1_gate.json)
