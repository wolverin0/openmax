<!-- doc-head: Wave98, control inverso PB050, ensayo físico incompleto y restauración exacta -->
Se preservan los intentos fallidos, los datos crudos y el veto de asociación.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Wave98: canario RAM PB050/PB040 en .241 y .242

Estado: **PARTIAL_FAILED_FIRMWARE_PROTOCOL**. La campaña causal no está completada.
El único intento adicional autorizado se detuvo después de A1. No hubo B1, A2 ni B2.
No se promueve firmware ni se certifica rendimiento de producción.

## Procedencia y contrato

La imagen activa a49160ff… ya contenía PB050 y PB040; se conservó el rechazo inicial
de volver a aplicar 72→76. La autorización posterior permitió construir el control A
con 76→72 en 0x009b758e, conservando PB050=0x0fa0 en 0x0040c140 y el resto de bytes decodificados.
B quedó definido como la imagen combinada a49160ff… sin modificaciones.
El control mide 208119 B; la imagen B original, 204796 B.

En A1 ambos drivers consumieron CRC whole baa98d4b e IE3 529b8db6,
verificados antes y después del tráfico junto al SHA del archivo seleccionado.
La política común fue VO=300/600, BE=1200/2400, umbral AQL=3000,
BQL máximo=16384 y clasificación WMM EF/CS6→priority262.

## Intentos y datos reales

Se preservaron tres prefijos anteriores sin tráfico medido: falta de stat,
tiempo insuficiente de arranque secuencial y escritura concurrente de hooks históricos.
La autorización <orca-id> permitió un único intento adicional con cuatro
hooks propios aislados por bind de archivo RAM a un noop, dentro del guardián independiente.
El intento adicional ejecutó TCP, IPTV CBR de 3 Mbps, VoIP equivalente G.711 y 100 pings desde .186.

| Dato diagnóstico A1 | Valor observado |
| --- | --- |
| TCP recibido | 17.9628 Mbps |
| ICMP enviados/recibidos | 100/100 |
| ICMP p50 / p95 / p99 | 2.100 / 3.321 / 4.059 ms |
| IPTV perdido/total | 2/2850 |
| VoIP perdido/total | 0/500 |

Estas cifras son diagnósticas. El agregador rechazó la ventana por ausencia de estación
en la quinta muestra STA; AP conservó estación en 5/5 y STA en 4/5.
La muestra STA fue a uptime96808.96; el guardián venció a96809.18.
La causa de la ausencia es UNKNOWN; esta cercanía temporal no prueba causalidad.
Sin una secuencia ABAB válida no existe estimación de efecto PB040 ni prueba de no inferioridad.
El efecto del consumidor físico del registro CCA también permanece UNKNOWN.

## Restauración comprobada

Ambos guardianes setsid transcurrieron al menos60s y restauraron autónomamente el firmware original.
Readback final: SHA a49160ff…, CRC whole92363606, IE3 12b29d01 y OTP4c4fd0bc.
Se restauraron las cuatro vinculaciones de hooks y sus hashes exactos.
Se verificó ausencia de nuevos binds de archivo y se conservó el montaje RAM padre preexistente.
La configuración original de colas y PHY quedó restaurada; se retiró el módulo nft propio
y se liberaron exclusivamente los locks de Wave98.
LED v4 conserva sus bytes y AUTO; se reinició el servicio tras renumerar PHY.
No se afirma ausencia de parpadeos durante las recargas deliberadas.
No hubo escrituras flash ni cambios en particiones protegidas o PtP-Colo.

## Evidencia y aceptación

- [Recibo 1626A](../artifacts/autoresearch/stage1626a_live_ptp_pb050_pb040_sgmt_canary_and_sweetspot_receipt.json).
- [Auditoría 1627A](../artifacts/autoresearch/stage1627a_live_ptp_fw_checksums_and_cca_telemetry_audit.json).
- [Pruebas](../tests/test_stage1626a_to_1631a_suite.py) y [gate](../artifacts/verification/stage1631a_wave98_codex2_gate.json).

Las pruebas verifican integridad de evidencia y restauración; un resultado local verde
no convierte el protocolo incompleto en éxito físico.
El ajuste histórico Wave84 conserva el bloque original de tres filas y sus hashes;
reconcilia únicamente la aserción del prefijo mutable, sin reescribir el ledger.
La literatura previa se reutiliza con su referencia; no se afirma una búsqueda externa nueva.
MemoryMaster se consultó en modo lectura; no se declara ingestión durable nueva.
