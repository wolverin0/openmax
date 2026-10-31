<!-- doc-head: Wave91 Triple-Play vivo DSCP WMM AQL BQL ronda2 -->
Tres iteraciones finitas con trafico fisico .186 hacia PowerBeam .241/.242.
Objetivo de latencia y Sirq separado de la integridad de la campana exploratoria.
<!-- /doc-head -->

# Stage1586A: banco vivo PtP, ronda2

Evidencia CONFIRMED_LIVE_HARDWARE. Sin flash ni cambios de produccion o PtP-Colo.
El controlador raiz serializo todas las sesiones SSH a las radios; auxiliares solo revisaron fuentes y evidencias.
LEDv4 se mantuvo activo con su SHA original. No hubo reinicio de radio ni del daemon.

## Diseno congelado

Cada iteracion: A1/B1/A2/B2,20s de TCP iperf3 + IPTV UDP3Mbps/1316B + sondas G711 equivalentes64kbps/160B desde .186.
Se enviaron200 ICMP64B a100ms. UDP inicio antes de TCP, con19.5s de solapamiento cargado comun.
Iteracion1: clasificador bridge postrouting_wmm EF/CS6 hacia prioridad262/UP6 y AQL VO300/600, BE600/1200us.
Iteracion2: mejor politica elegible previa, cambiando BE500/1000us, BQLmax12288 y quantum300.
Iteracion3: refinamiento preregistrado del mejor elegible: BE800/1600, VO300/600, quantum1514 si era300, de otro modo750.
BQLmax del refinamiento:16384 si antes era12288, de otro modo12288. Reglas WMM solo si pertenecian al mejor elegible.
Keep exige dos mejoras emparejadas fmx_loss>=0.005, capacidad TCP>=95% del control y perdida UDP<=2%.
En la tercera iteracion tambien exige pico Sirq observado B<=A en ambos equipos. Sin nuevo umbral posterior a los datos.
Objetivo final: p95<=8ms en ambas B, IPTV0%, capacidad>=95% y ausencia de regresion del pico Sirq observado.

## Resultados reales

| Iteracion | Decision | fmx_loss B | p95 B ms | TCP A/B Mbps |
|---|---|---|---|---|
| 1 | discard | 0.377622 | 4.245 | 20.587/18.332 |
| 2 | discard | 0.437063 | 9.536 | 20.927/19.706 |
| 3 | discard | 0.477602 | 10.617 | 18.923/21.122 |
Iteracion1: capacidad B/A=89.04%; criterios fallidos: capacity.
Iteracion2: capacidad B/A=94.16%; criterios fallidos: capacity.
Iteracion3: capacidad B/A=111.62%; criterios fallidos: strict_sirq_no_spike.

Objetivo final completo alcanzado: `False`. Fin: `STOP_MAX_ITERATIONS`.
Una mejora de latencia con perdida de capacidad no se promueve. Cada politica se compara con A contemporaneo, no con cifras historicas de otra hipotesis.
Las tres decisiones quedaron anexadas sin reescribir filas anteriores de results.tsv.

## WMM, cadenas y errores

El mapa DSCP predeterminado depende de cfg80211/backports. No se deduce solo de uname.
La prioridad262 fuerza UP6; se comprobaron reglas exactas, contadores nft y paquetes TID6/AC0 reales.
Las reglas solo abarcaron .186/.242, puerto15842 y sondas ICMP; no se altero el firewall general.
El chequeo inicial fallo por faltar nft_meta_bridge. Se cargo el paquete oficial con ABI/hash coincidentes solo desde /tmp.
Se conservaron el fallo inicial y el intento con nombre de modulo incorrecto. Al cerrar se retiro el modulo propio.
Se guardaron RSSI por antena, identidad de estacion, reintentos, fallos TX y duracion TX/airtime.
dot11FCSErrorCount devolvio Not supported: UNKNOWN, no cero. fw_stats entrego FCS/CRC acumulativo del dispositivo/canal.
Los incrementos FCS del firmware no son CRC exclusivos del peer ni una tasa de perdida sin denominador valido.

## Sirq, LED y restauracion

Se tomaron24 muestras /proc/stat por radio, aproximadamente a1s, y cinco lecturas de LED/colas/estacion por ventana.
Los picos son maximos observados a1s. No prueban ausencia de transitorios mas cortos ni causalidad del daemon sin control LED-OFF.
Las consultas fw_stats generan WMI de lectura al inicio/final; esa instrumentacion estuvo presente en ambos brazos.
Guardia independiente60s antes de cada cambio, snapshot original y lectura exacta tras restaurar.
Al cerrar: politica RAM inicial, tabla nft propia ausente, modulo temporal retirado y leases propios liberados.
Sin A/A y holdout disjunto no hay certificacion ni promocion de produccion; el kit distribuido no se modifico.

## Evidencia

[Campana1584A](../artifacts/autoresearch/stage1584a_live_ptp_pbe5ac_dscp_wmm_aql_bql_round2_receipt.json).
[Auditoria1585A](../artifacts/autoresearch/stage1585a_live_ptp_pbe5ac_per_chain_fcs_airtime_audit.json).
Cinco pilares: catalogo y fuentes, consultas del reactor con literatura reutilizada identificada, ABAB fisico, diseno experimental y recall MemoryMaster.
El identificador FMX del recibo vincula evidencia local; no se presenta como nueva ingesta durable.
