<!-- doc-head: SUPERSEDED (W435, 31/10): the 68-72 C thermal guard was agent-invented and removed by the operator on 30/10; temperature is telemetry only (orchestration/thresholds.json). Wave 59; descubrimiento LTU2 en solo lectura y controlador térmico desechable -->
Lite #2 figura en gi7, pero su configuración sigue sin capturarse.
Lite #1 quedó estacionado; el arranque está bloqueado por temperatura desconocida.
El ciclo de ráfaga está probado con simulación; su límite físico sigue sin verificarse.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 1395A — LTU2, VLAN 107 y Burst-and-Park

## Resultado observado

CONFIRMED: se consultaron el host, LTU-Lite #1 `198.18.0.63`,
PowerBeam `198.18.0.45` y la API del ES-10XP en solo lectura.
La radio de `.110` permaneció apagada antes y después de la captura.
No se contactó `.242`, ni se crearon VLAN, interfaces o direcciones.
No hubo cambios de PoE, particiones protegidas ni configuración del switch.

La MAC `PUBLIC_DEVICE_0043` apareció en la tabla del switch en gi7/VLAN 1.
Esto acredita una entrada observada, no disponibilidad actual, modelo ni asociación OTA.
Las sondas disponibles no permitieron confirmar identidad y sesión del segundo LTU.
Su `/tmp/system.cfg`, rol, frecuencia y SSID quedan UNKNOWN:
Stage 1394A registra `NOT_CAPTURED_CONDITION_UNMET`.

## EUI-64 y alcance de las sondas

El primer octeto `e0 XOR 02 = e2`; insertar `ff:fe` produce
`PUBLIC_DEVICE_0063`. La variante histórica con `e063` no es el EUI-64 calculado.
El sufijo `%29` identifica la interfaz del host; no significa puerto gi7.
Desde cada radio se usaron los nombres de interfaz observados en ese equipo.

Se conservaron las salidas de ping, conexiones SSH/HTTPS y descubrimiento UDP 10001.
UDP utilizó la consulta de lectura unicast de cuatro bytes; no hubo broadcast ni barrido de subred.
No se recibió una respuesta que verificara la identidad exacta de Lite #2.
Una dirección por defecto con MAC ambigua no autorizó lectura de configuración.

El intento inicial de contraseña en `.241` falló y se conserva.
Un suplemento separado con el mecanismo documentado `auth_none(root)` permitió
verificar PowerBeam Gen2 y su IP local; no se modificó su autenticación.
La MAC local observada fue `PUBLIC_DEVICE_0064`.
La corrección posterior del análisis de stderr está declarada y ligada por SHA-256;
no se presenta como una repetición de la captura principal.

## Mapa ES-10XP observado

API efectiva: `/api/v1.0/interfaces`, `/api/v1.0/vlans` y `/api/v1.0/tools/mac-table`.

| Puerto | VLAN sin etiqueta | VLAN con etiqueta | Enlace |
|---|---|---|---|
| gi1 | 1 | ninguna | 1000 full |
| gi2 | 1 | 99 | 100 full |
| gi3 | 1 | 99, 107 | 1000 full |
| gi4 | 1 | 107 | 1000 full |
| gi5 | 1 | ninguna | 100 full |
| gi6 | 1 | ninguna | 1000 full |
| gi7 | 107 | ninguna | 1000 full |
| gi8 | 1 | ninguna | 1000 full |

gi5 contiene la MAC conocida de Lite #1 `PUBLIC_DEVICE_0045`.
gi7 contiene la entrada de Lite #2 en VLAN 1 pese a su membresía sin etiqueta 107.
El PVID no fue expuesto de forma verificable: su valor queda UNKNOWN.
La discrepancia no demuestra por sí sola una causa de aislamiento ni autoriza corregirla.
Los contadores nativos no quedaron disponibles en esta captura.
Las MAC candidatas exactas del Rocket no aparecieron; no se identificó por prefijo.

No existe una interfaz VLAN 107 en `.110` ni `.241` en las capturas.
Por tanto, el recorrido etiquetado 107 queda sin probar; no se creó una interfaz para forzarlo.
Las salidas y todas las MAC por puerto quedan en el recibo, sin abreviar su evidencia nativa.

## Protocolo térmico de ráfaga

Wave 52 dejó evidencia de 73 °C después de funcionamiento continuo y detuvo la radio.
En Wave 59, `air_fpga` estuvo ausente y `ath0` administrativamente DOWN antes y después.
Los cuatro comandos AF de temperatura terminaron con código 255: es error, no 255 °C.
La temperatura actual es UNKNOWN; no se infieren 50–65 °C por tiempo de reposo.

El controlador host exige identidad exacta y estado PARKED, cuatro sensores válidos
y frescos de hasta 65 °C, y reloj monotónico válido antes de considerar un arranque.
Arma primero un watchdog independiente, vuelve a comprobar enfriamiento y sólo entonces
permite la transición del backend desechable a STARTING.
Durante ACTIVE exige AP-PTMP, 5500 MHz, 20 MHz, FMX-LTU, antennagain 26,
powerout en [-4, 0] y todos los sensores hasta 72 °C.

El presupuesto total de 60 s empieza antes del armado y comprende inicio, prueba y
confirmación de apagado. El apagado debe comenzar como máximo a los 45 s;
se reservan al menos 15 s para estacionar. Un inicio lento reduce el tiempo útil OTA.
Un apagado confirmado después de 60 s es fallo, aunque finalmente se enfríe.
No hay bucle de reinicio automático ni permiso para calentar el ASIC para leer sensores.

La implementación actual sólo admite `DISPOSABLE_VIRTUAL_BACKEND`.
No incorpora un adaptador que arranque RF real: esta etapa verifica máquina de estados,
fallos inyectados y evidencia pasiva. El límite físico de 60 s y cero disparos térmicos
en ráfagas reales siguen UNVERIFIED. Habilitar ejecución física requiere verificar
el watchdog independiente y una fuente válida de temperatura con el equipo estacionado.

## Evidencia y reproducción local

- [Descubrimiento 1392A](../artifacts/verification/stage1392a_ltu_lite2_eui64_and_vlan107_discovery.json).
- [Controlador y escenarios 1393A](../artifacts/verification/stage1393a_ltu110_cooled_burst_mode_receipt.json).
- [Lectura condicional 1394A](../artifacts/verification/stage1394a_ltu_lite2_readonly_config_probe.json).
- [Controlador Python](../tools/bench/run_ltu110_60s_cooled_burst_mode.py).
- [Suite 1396A](../tests/test_stage1392a_to_1397a_suite.py).
- [Gate 1397A](../artifacts/verification/stage1397a_wave59_codex1_gate.json).

`python -m pytest tests/test_stage1392a_to_1397a_suite.py -q`

El gate valida hashes, salidas nativas, escenarios y resultados pytest;
un PASS local no convierte las condiciones pendientes en aceptación física.
