<!-- doc-head: Wave 438 corrige PtP-Colo a 450 m y separa BDP, propagación y BQL Ethernet -->
Derivación offline confirmada; 8.192 bytes sigue siendo candidato, no valor óptimo.
Sin RTT RF directo verificable ni caudal útil del cuello de botella: BDP RF UNKNOWN.
Comparación aislada 24.192 frente a 8.192 pendiente de banco y recorrido Ethernet válido.
<!-- /doc-head -->

# Stage 3098A: PtP-Colo a 450 m, BQL y A/B pendiente

## Dictamen

La distancia de **450 m** proviene de la corrección explícita del operador en Wave 438.
No se midió geodésicamente en esta etapa. Los recibos W337/W338 usaban 7 km.
No corresponde reducir BQL ni escalar otras colas sólo por esta corrección.
El resultado es **CONFIRMED offline** para cálculos, procedencia y plan; ningún valor obtiene GO productivo.
Cero SSH, tráfico generado, escrituras a radios o cambios del estado maestro.

## Qué estaba mal en la propuesta de 8.192 bytes

W338 calculó aproximadamente 863 B con 147,92 Mbps y 46,7 µs.
147,92 Mbps era el agregado de tres CPE de Panel1 en W334, no la tasa de PtP-Colo.
46,7 µs era aproximadamente `2 × 7000 / c`, no un RTT medido.
La afirmación de que el exceso de BQL sólo agrega latencia y nunca caudal no quedó demostrada.
Se preservan los recibos anteriores; no se reescriben para ocultar los supuestos.

Con `c=299792458 m/s`, la propagación de ida y vuelta a 450 m es **3,002077 µs**.
Multiplicada por PHY 144,4 / 173,3 Mbps da **54,187 / 65,032 B**.
Es únicamente el componente geométrico; faltan MAC, acceso al medio, procesamiento y demás recorrido.
No se convierte ese resultado sub-MTU en límite BQL.

## Evidencia guardada y BDP

El reporte del 28/10 registra PHY AP TX/RX 173,3/173,3 y STA 144,4/173,3 Mbps.
En ambos, `ptp_peer_p50_ms` y `ptp_peer_p95_ms` son null.
El snapshot SQLite STA **34702**, del 31/10 00:10:40 UTC, tiene RTT del colector 2/4/6 ms.
Sus percentiles son min=2, p50=4 y p95=5,8 ms; tres respuestas.
La ruta está marcada `ROUTED_E2E_PATH_UNCONTROLLED`, sin peer RF resuelto.
El AP 34701 muestra RTT 0 ms por resolución entera del colector; no es demora física cero.
Ambas filas se leyeron en transacción SQLite read-only y sus payload SHA256 se verificaron.

`BDP_bytes = 125 × capacidad_Mbps × RTT_ms`.
Para BDP de transporte hacen falta capacidad útil del cuello de botella y RTT del mismo recorrido.
La PHY no es goodput, y el RTT cargado incluye colas que no deben realimentar su propia dimensión.

| PHY registrada Mbps | RTT E2E 2 ms | RTT E2E 4 ms | RTT E2E p95 5,8 ms |
| ---: | ---: | ---: | ---: |
| 144,4 | 36.100 B | 72.200 B | 104.690 B |
| 173,3 | 43.325 B | 86.650 B | 125.642,5 B |

La tabla es **sensibilidad PHY × RTT E2E**, no BDP RF medido ni recomendación de memoria.
BDP RF, RTT directo RF y capacidad útil del cuello de botella permanecen **UNKNOWN**.
Marco de referencia: [RFC 6349](https://www.rfc-editor.org/rfc/rfc6349.html).

## BQL del kit frente a la propuesta

El kit v2 AP y STA declara limit_max=24.192, hold_time=400 ms y hereda limit_min=4.542 B.
Los snapshots 34701/34702 leen realmente **36.288 / 4.542 / 600 ms** en eth0 TX.
W339 también identificó ag71xx-legacy y enlace Ethernet de 1000 Mbps.
Declarado en el kit, instalado y óptimo medido son estados distintos.

| limit_max B | Equivalente tramas de 1514 B | Serialización ideal Ethernet 1 Gbps | Equivalente a PHY 173,3 Mbps |
| ---: | ---: | ---: | ---: |
| 8.192 | 5,411 | 0,065536 ms | 0,378165 ms |
| 24.192 | 15,979 | 0,193536 ms | 1,116769 ms |
| 36.288 | 23,968 | 0,290304 ms | 1,675153 ms |

24.192→8.192 reduce el máximo **66,14%**; la diferencia ideal Ethernet es **0,128 ms**.
No son tiempos de residencia observados ni una mejora RTT prometida.
BQL limita bytes pendientes por cola TX de Ethernet mediante feedback de completados.
El límite dinámico puede estar por debajo del máximo; registrar `limit` e `inflight`, no sólo `limit_max`.
Referencias: [DQL](https://raw.githubusercontent.com/torvalds/linux/v6.6/include/linux/dynamic_queue_limits.h),
[feedback y clamp](https://raw.githubusercontent.com/torvalds/linux/v6.6/lib/dynamic_queue_limits.c).
La distancia RF no es entrada de ese algoritmo.

`fq_limit` cuenta paquetes, `fq_memory_limit` memoria skb, `fq_quantum` servicio por turno.
AQL expresa airtime en microsegundos; no es BQL Ethernet ni reserva TCP.
Conservar esas colas capturadas: este cálculo no deriva nuevos valores FQ/AQL/backlog.

## Ensayos previos que limitan la conclusión

W353 ya ensayó BQL8192 en banco .241/.242; p95 A/B 9,9/10,1 y 9,26/10,0 ms.
Se perdieron goodput y drops; terminó por orden del Orchestrator y no obtuvo KEEP.
El nombre del recibo no convierte ese banco en producción .62/.54.
W363c obtuvo NO_GO del kit combinado: p95 pareado +24,00%, RX L2 −2,38%.
Cambió múltiples valores y bucles; no demuestra que BQL24192 aislado causara la regresión.
Reusar esos resultados, sin presentar el control 8192 como nunca ensayado.

## A/B necesario cuando el coordinador libere el banco

1. Identificar AP .241/STA .242, PHY, enlaces, ruta y receptor cableado detrás del TX Ethernet bajo prueba.
2. Probar carga atravesando ese TX: AP eth0 RX→RF no ejercita AP eth0 TX BQL para la bajada.
   Una STA RF-only con HTTP local puede omitir STA eth0 TX; ese recorrido invalida el ensayo BQL.
   Si falta terminación más allá del Ethernet lejano, esperar recorrido válido; no inferir efecto por un eco RF.
3. Medir RTT RF directo y capacidad útil por dirección; A/A fresco con carga y observador idénticos.
4. Capturar preimágenes reales, bucles activos, BQL/FQ/AQL/sysctl, boot, contadores y salud de memoria.
5. Comparar sólo **A=24192 frente a B=8192**, ambos min=4542 y hold=400 ms.
   No comparar 24192/400 con 8192/800 como si cambiara sólo el máximo.
6. Seis ventanas A/A; tres rondas A1-B1-A2-B2 con TCP bulk, IPTV UDP CBR y G.711/20 ms.
   Conservar FQ/AQL, radio, backlogs y bucles idénticos; medir caudal en receptor, no sólo bytes ofrecidos.
7. Recoger p50/p95/p99, pérdida/jitter por flujo, BQL limit/inflight, deltas FQ y MemAvailable/OOM.
   Vigilar deriva de PHY/carga, reset de contadores, DUP, asociaciones y cambios de bucles.
8. Watchdog compartido de 45 s en .242 antes de cada cambio, y AP si se modifica; renovar atómicamente.
   Comprobar generación/boot/deadline; restaurar y releer preimagen exacta, reachability RF y limpieza propia.
9. GO sólo como propuesta si QoE mejora repetidamente fuera del ruido pareado A/A sin dañar caudal/pérdida/p99.
   Recorrido no ejercitado o evidencia incompleta: INCONCLUSIVE; daño: NO_GO. No ajustar bandas tras mirar B.
10. No aplicar nada en .62/.54 en esta wave. Un canario posterior exige permiso específico y monitoreo Antes/Después.

El objetivo heredado 8192 + fq_overmemory=0 + p95≤−25% permanece sin probar; no se declara alcanzado.
Recibo con fuentes fijadas, filas, fórmulas, plan y 12 pruebas locales:
[wave438_colo_bql.json](../artifacts/autoresearch/wave438_colo_bql.json).
Gate: [wave438_lane1_colo_bql_gate.json](../artifacts/verification/wave438_lane1_colo_bql_gate.json).
