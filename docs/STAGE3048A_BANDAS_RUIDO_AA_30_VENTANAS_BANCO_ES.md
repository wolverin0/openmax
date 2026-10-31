<!-- doc-head: Wave 388, bandas A/A medidas y propuestas de guardas sin aplicar -->
30 ventanas TCP bidireccionales de 20 s, pérdida y RTT reales; límites de comparabilidad explícitos.
<!-- /doc-head -->

# Bandas A/A del banco WA — Wave 388

## Alcance y ruta confirmada

Se completaron 30 ventanas consecutivas, sin cambios de configuración, rutas, colas ni flash.
El receptor fue la Loco conocida por su clave SSH, asociada al LAP-120 .20, en VHT20 / 5180 MHz.
Antes del tráfico, .250 respondió con otra clave y otra MAC; se rechazó esa identidad.
La ruta IPv6 link-local existente permitió alcanzar la Loco correcta sin reparar ni alterar IPv4.
El host cableado generó TCP a través del bridge del AP; eth0 de la Loco permaneció sin carrier.
Los contadores del peer inalámbrico exacto aumentaron en ambos sentidos en todas las ventanas.
La evidencia del conflicto y el fallo pretráfico se conservan en el JSON, separados de las mediciones.

## Protocolo y datos

Cliente externo: iperf3 bidireccional, 4 flujos por sentido, ventana y bloque de 16 KiB.
El AP no alojó iperf3: originó 20 pings IPv6 de 64 B a intervalos de 1 s por ventana.
Goodput: receptor local del servidor para DL y receptor local del cliente para UL; sumas por stream verificadas.
Ping y TCP tienen distinto origen; no se presentan como la misma medición extremo a extremo.
Cada ventana guardó lecturas inicial, intermedia y final: memoria, asociación, arranque, OOM y contadores.
El receptor tuvo expiración autónoma de 60 s, con identidad PID/arranque y limpieza acotada.
No se aplicó una guarda de rendimiento durante A/A: se conservó la variabilidad, deteniendo sólo por integridad.

| Observable | Mínimo | Mediana | Máximo | q.005 | q.995 |
|---|---:|---:|---:|---:|---:|
| Goodput bidir Mbps | 43.6261 | 51.3981 | 53.6261 | 44.4655 | 53.5219 |
| p95 por ventana ms | 13.1783 | 16.0701 | 20.9860 | 13.2699 | 20.8227 |
| p99 por ventana ms | 13.7133 | 18.9945 | 28.4252 | 13.8687 | 27.9311 |
| Pérdida por ventana % | 0.0000 | 0.0000 | 5.0000 | 0.0000 | 5.0000 |

Pings: 595/600 recibidos; pérdida agregada 0.8333 %.
MemAvailable mínimo muestreado: AP 8360 KiB; Loco 6208 KiB.
Sin nuevo OOM observado; se mantuvieron las identidades de arranque. Los seis mensajes OOM previos de la Loco no se contaron como nuevos.
La campaña no demuestra capacidad máxima: utiliza buffers pequeños y no exige backlog RF sostenido.

## Derivación y límites

Cuantiles tipo 7: ordenar x; h=(n-1)*p; j=floor(h); Q(p)=x[j]+(h-j)*(x[j+1]-x[j]).
Con n=30, Q(.995)=0.145*x[28]+0.855*x[29]. Para goodput se propone describir la cola inferior q.005.
Para RTT y pérdida se describe q.995 de las 30 métricas de ventana, separado del cuantil de los pings agrupados.
Con 20 pings, la resolución de pérdida de una ventana es 5 puntos porcentuales.
Hubo una respuesta duplicada en la ventana 22: se conserva cruda y se usa la primera respuesta por secuencia para RTT.
Estos cuantiles empíricos no certifican una cola poblacional de 0,5 % ni independencia temporal.
No se convirtió ningún cuantil en una nueva guarda operativa. Un A/A sin cambios puede contener daño natural persistente.

## Comparación de guardas actuales auditadas

| ID | Valor auditado / resultado | Derivación permitida |
|---|---|---|
| L05 | pérdida >2 %: 5/30; p99 >40 ms: 0/30 | Excedencias del banco; transferencia a PtP UNKNOWN |
| L05 cadenas | diferencia >6 dB: 30/30 | Máximo de lecturas en ambos nodos; no prueba de falso positivo |
| L06 | pérdida >5 %: 0/30; fq_overmemory crece: 0/30 | Respetar el operador estricto > |
| L08 | retries 12/8 % y EVM −20 dB | UNKNOWN: faltan EVM y régimen multipeer |
| L09 | EVM −18 dB / bmiss 5 | UNKNOWN: no equiparar bmiss con beacon-loss acumulado |
| L10 | nf −84/−82, correlación 60/25 %, retry 120‰ | UNKNOWN: sin verdad de clasificación de campo |
| S02 | 4096/65536 permutaciones; cap histórico 14 | Cap actual16: 15 pares dan 32768 signos exactos, mismo resultado con ambos presupuestos; potencia UNKNOWN |
| W02 | hold/renovación/lease | No se probó temporización del watchdog en esta ola |
| W04 | deadlines de captura/comando | q.995 de las lecturas ejecutadas: 2.5452 s; no valida otros comandos |
| W05 | retries 3, presupuestos 30/50 s | UNKNOWN sin fallos controlados del colector |
| W03/W06 | valle, cadencia, rondas y reloj | Política operativa; no deriva del ruido RF |
| W07/W08 | polling, HTTP, TTL y métricas de ruta | Otros sistemas/observables; no calibrados |

“Demasiado laxo / daño omitido” permanece UNKNOWN para todas las guardas: faltan controles positivos.
Una excedencia A/A no se etiqueta automáticamente como falso aborto; cero excedencias tampoco demuestra sensibilidad.

## Cierre

Comprobaciones locales: 47/47; contadores y cuantiles recalculados desde datos crudos.
La limpieza final del receptor y la lectura fresca están en el recibo; no hubo cambios a restaurar.
Propuesta exclusivamente descriptiva. Aplicación y validación poblacional pendientes de controles de daño y holdout.

- Datos y fuente ejecutada: [JSON](../artifacts/autoresearch/wave388_aa_noise_bands.json).
- Gate: [evidencia](../artifacts/verification/wave388_lane1_aa_noise_gate.json).
