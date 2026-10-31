<!-- doc-head: Wave288, línea base airOS BEFORE con metadatos de producción sin probar -->
Se conservan los conteos nativos y los valores ausentes; no se ejecutó un corte ni una comprobación de imagen.
La observación de Panel2 es independiente del inventario histórico de veintidós CPE.
<!-- /doc-head -->

# Línea base viva PtP-Colo y Panel2

## Contrato y alcance

La [prerregistración](../artifacts/autoresearch/stage2760a_wave288_preregistration.json)
fijó hasta tres rondas en cuarenta y cinco minutos. La línea base PtP requiere
dos ciclos consecutivos con airOS 8, frecuencia actual 6035 MHz, ancho 20 MHz,
intervalos nativos de CPU del mismo arranque y veinte sondeos enviados por dirección
con respuestas suficientes para calcular RTT. No se relajaron esos criterios después de medir.

Los extremos `.105.62` AP y `.105.54` STA conservaron su firmware stock.
No hubo escrituras RF, retunes, flash, ejecución de `fwupdate` ni corte a OpenWrt.
El ICMP nace en cada radio hacia la dirección de gestión opuesta; su recorrido
no se certifica como un segmento L2 puro.

## Tres rondas reales conservadas

El [recibo PtP](../artifacts/autoresearch/stage2760a_ptp_colo_before_airos8_telemetry_db_baseline_receipt.json)
retiene las tres rondas, sin una cuarta repetición para obtener verde.

| Ronda | AP enviados/recibidos | STA enviados/recibidos | p95 AP / STA, ms | Calificación |
|---|---:|---:|---:|---|
| 1 | 20 / 20 | 20 / 20 | 10,71345 / 4,55450 | CPU sin intervalo previo |
| 2 | 20 / 20 | **21 / 20** | 10,39045 / 4,61605 | Denominador fuera del contrato |
| 3 | 20 / 20 | 20 / 20 | 23,83015 / 19,26500 | Válida sin pareja anterior válida |

La orden del segundo STA solicitó veinte paquetes, pero el contador nativo
informó veintiuno enviados y veinte recibidos: pérdida 4,7619% sobre 21.
Se conserva esa diferencia, sin sustituir el contador por el argumento solicitado.
Los ciclos 2 y 3 se seleccionaron para **exportar registros**, no como una
pareja que cumpliera la calificación consecutiva.

En la tercera ronda, los p95 observados fueron 23,83015 ms desde AP y
19,265 ms desde STA. Son mediciones BEFORE stock; no prueban una mejora posterior.
La línea base PtP queda `PARTIAL_BASELINE` por el criterio de consecutividad.

## Métricas y persistencia

El adaptador preserva señal por cadena, ruido, tasas, contadores de interfaz,
CPU y RAM cuando sus fuentes nativas están disponibles. Un dato no soportado
permanece `null`; RSSI nativo sin unidad dBm verificada se mantiene separado.
Los porcentajes de CPU usan deltas del mismo arranque; no se convierten
contadores acumulados de toda la vida del equipo en carga instantánea.
En la tercera ronda se observaron cadenas AP −61/−55 dBm y STA −63/−56 dBm,
con ruido −98/−101 dBm. Las tasas AP TX/RX 173,3/173,3 y STA 156/173,3 Mb/s
son reportes PHY, no goodput TCP. Las cifras y la variación de RTT son BEFORE.

El exporte congelado contiene seis muestras reales y seis referencias propias
en `fmx_airos_before_baselines`. Cada referencia liga secuencia, nodo, run,
ciclo y hash al payload de `openwrt_before_after_samples` en la misma transacción.
La fase es `BEFORE`, sin registros AFTER inventados ni exporte de tablas ajenas.
Las ocho copias locales históricas de particiones protegidas conservaron sus hashes;
esto no constituye una validación CRC de una imagen nueva.

## Panel2

El [recibo Panel2](../artifacts/autoresearch/stage2761a_panel2_guarida_before_telemetry_db_receipt.json)
conserva el radio `.82` en airOS, 5805 MHz y ancho 20 MHz.
La lista nativa observada contiene **siete** estaciones frente al inventario
histórico esperado de veintidós. No se fuerza el conteo a 22 ni se atribuye una causa
a la diferencia. Esta muestra BEFORE sí completa su aceptación observacional.

## Meta de producción

El [gate](../artifacts/verification/stage2765a_wave288_codex2_gate.json)
separa observación de línea base y aceptación productiva. Quedan `UNKNOWN`:
CRC uImage, resultado de `fwupdate`, enlace 6035 MHz después de un corte y
reducción de p95 de al menos 25% después de migrar. No se autorizaron ni ejecutaron esas etapas.
El estado global es **PARTIAL**; la presencia actual de 6035 MHz no es un readback posterior al corte.

Las pruebas usan fixtures desechables para errores de parser y atomicidad SQLite;
la aceptación física usa exclusivamente los recibos nativos persistidos.
El [anexo CRLF](../artifacts/autoresearch/stage2764a_results_crlf_append_receipt.json)
preserva el prefijo del registro y las cuatro filas nuevas.
La [memoria aceptada](../artifacts/autoresearch/stage2763a_memorymaster_ingest_receipt.json)
permanece candidata y no sustituye una aprobación productiva independiente.
