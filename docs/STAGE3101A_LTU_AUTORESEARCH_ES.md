<!-- doc-head: W441 base RF medida con una estacion; alcance revisado por Master -->
Dos repeticiones A/A de TCP subida/bajada, 30 s por sentido y 30 RTT por carga.
Rocket AP y Lite1 .110 siguen enlazados; configuraciones verificadas contra W432.
Lite2/PtP pendientes; los nueve sysfs sin rango/rollback pasan a W442.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# W441: medicion Rocket ↔ LTU-Lite1

CONFIRMED, capa HARDWARE/RUNTIME, atribuida al par propietario LTU + Linux + generadores TCP.
Alcance revisado por `<orca-id>`: cerrar W441 con una estacion medida.
Recibo fuente: `artifacts/autoresearch/wave441_ltu_autoresearch.json`. Gate: `artifacts/verification/wave441_lane4_ltu_autoresearch_gate.json`.

Rocket PUBLIC_DEVICE_0050, stock 2.1.0, AP FMX-LTU/NONE, 20 MHz,
TX5500/RX6025. CPE PUBLIC_DEVICE_0045, stock2.4.0, RX5500/TX6025.
TCP y ping ligados a 198.18.0.63 → 198.18.0.138 por br0;
retorno br0, excepcion NAT y origen TCP110 observados. AP br0 contiene solo ath0.
No es un benchmark con generadores externos ni una prueba de capacidad/SLA de reenvio.

| Repeticion | Sentido TCP | Mbit/s recibidos | RTT p50 ms | p95 ms | p99 ms | Retrans TCP |
| :-- | :-- | --: | --: | --: | --: | --: |
| AA1 | Subida CPE→AP | 6.265 | 11.319 | 17.720 | 18.452 | 206 |
| AA1 | Bajada AP→CPE | 70.513 | 13.137 | 40.025 | 54.390 | 0 |
| AA2 | Subida CPE→AP | 4.465 | 12.495 | 17.484 | 19.756 | 228 |
| AA2 | Bajada AP→CPE | 69.432 | 13.462 | 17.843 | 18.748 | 0 |

Los 120 pings bajo carga fueron recibidos. Cuantiles por interpolacion lineal;
las muestras numericas quedan en el JSON. RTT siempre CPE→AP, tambien durante bajada TCP.
Cada carga dura 30 s, un flujo TCP; cada direccion tiene 30 pings.
No se suman subida y bajada secuenciales como agregado simultaneo.

Banda A/A observada: subida 4.465–6.265 Mbit/s (rango/media 33.55%);
bajada 69.432–70.513 Mbit/s (1.55%). p95 de bajada 17.843–40.025 ms (76.67%).
Es un rango de dos repeticiones, no un intervalo de confianza. No hay efecto de tuning ni campeon.
Los numeros historicos de Stage15 §4 no se reutilizan: esta tabla es una base nueva y limitada a una CPE.
La precision de p99 con 30 muestras es limitada; una mejora pequena podria quedar dentro de esta variacion.

MemAvailable minimo de ambos nodos: 60184 KiB. Cuatro sensores, tres cortes por corrida/nodo:
Lite1 79–80; Rocket 96–97, unidades nativas no verificadas aqui.
Relojes de equipos no sincronizados: UTC del host es la referencia temporal.

Ambas campanas CLEANED, con PID+starttime+boot y watchdog180s. Puerto5232 sin listener al finalizar.
Hashes System de ambos y RC de Lite1 iguales a W432; peer1 y roles verificados al cierre.
Sin escritura de configuracion, firmware, knobs RF, produccion ni PowerBeam.

## Pendientes y fallos preservados

- Lite2 no asociada, IP111/115 sin respuesta; no se reclama ROCKET LISTO PARA LLEVAR.
- Dos estaciones y PtP no medidos. ABAB pasa a W442 por decision del Master.
- Catalogo LTU20, indice78 y ledger125: nueve filas sin historial indexado son sysfs sin rango/rollback cualificado;
  seleccion valida0. Ausencia de historial no se rebautiza n_eff=0. Ver `STAGE3101A_knob_selection.json`.
- Lectura Loco solo lectura; permiso de cambio revocado por `<orca-id>`: lane2 posee el acceso persistente.
- RX Lite2 solicitado por `<orca-id>`, pendiente de acceso lane2. Getter de espectro en Lite1 respondio;
  no se deriva fallo de hardware de una curva plana sin validar unidades, frescura y control comparable.
- Primer arranque local encontro stdin cerrado antes de red; snapshot conservado. PTY posterior termino rc1
  despues de AA1 CLEANED y antes de AA2; se reabrio transporte y se recuperaron pings con boot fijado.
- Ping nativo rechazo -i; se uso su intervalo por defecto. sha256sum nativo no existe;
  primer verificador rechazo hash ausente; luego SHA256 del host sobre lectura privada verifico las identidades originales.
- Objetivo Karpathy completo NO cumplido: no tratamiento, fq_overmemory_delta UNKNOWN, no promocion.
