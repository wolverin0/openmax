<!-- doc-head: W442 cierre parcial por orden del operador; potencia nativa y re-medicion -->
.110 solicitud28/ganancia13 restaurada y guardada con CRC; mediciones de20s por sentido.
Lite2 RC heredado retirado, solicitud28 guardada y arranque nativo verificado.
Rocket y pais4097 intactos; ABAB/top5 pendientes por corte explicito.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# W442: recuperacion de potencia y medicion

Estado CONFIRMED con alcance parcial. Fuente `artifacts/autoresearch/wave442_ground_up_discovery.json`.
Corte `<orca-id>`; decision final `<orca-id>`. No se acepta todo el contrato original.

Antes: .110 System15/AME2, salida calculada -8/2; Lite2 System15/AME15,
salida calculada -30/-30 y RC S24F; Rocket System56/AME30, salida23/23.
Los archivos default.cfg exactos de ambos firmwares indican solicitud28.
Board Lite: ganancia13. El getter de salida calculada no es la solicitud configurable.

.110: solicitud nativa28 produjo15/15. Se ensayaron pasos hasta20 y dos capturas20s,
pero el control de señal era incorrecto: signal(a/b,c/d) intercala campos distintos.
max(a,b) NO es un maximo validado de dos cadenas; no se acepta aquel umbral ni sus conclusiones.
Se detuvo ese control y se restauro solicitud oficial28/AME15/ganancia13, guardada
por cfgmtd oficial con Active/BackupCRC validos y RC intacto. No se reinicio .110.
El guarda inicial revirtio15 al vencer antes del guardado; resultado0 preservado.
Se reaplico entonces el ensayo20 por gestion Ethernet y se guardo; no fue un reintento ambiguo del escritor.
Ese control quedo invalidado y sus actuadores de umbral ahora rechazan ejecucion antes de acceder al equipo.

Lite2: se retiro el RC S24F completo y se dejo solo gestion LAN55 y retorno
al peer Loco realmente observado198.18.0.139. No se modifico la Loco.
Primero se guardaron solicitud28 y RC limpio; ese Backup conservaba el System/RC heredado.
Al bajar potencia bajo la interpretacion incorrecta la asociacion se perdio.
Se conservaron los intentos24/26 y sus fallos; tras la correccion semantica se restauro
solicitud oficial28 y RC limpio. El Backup actual conserva el perfil nativo previo, no el viejo S24F.
El unico cambio inicial del archivo persistente fue persistent/rc.poststart, intencional y verificado.
Las solicitudes posteriores solo cambiaron el campo de potencia y conservaron el RC limpio.
El objetivo fisico -45..-55 NO se acepta: nombres/unidades de los campos intercalados aun UNKNOWN.
Prueba exacta: STAGE3102A_signal_fields_re.json, offsets84/7c y86/7e en Rocket y CPE.
Arranque nativo: `<uuid>`.
Dos estaciones enlazadas al cierre: **True**.
La tabla de estado completa queda en final_live del JSON; no se inventa enlace por una IP accesible.
Si Lite2 sigue en Scan, la salida calculada -30 no se confunde con su solicitud persistente28/AME15.

| Corrida | TCP sentido | Mbit/s recibidos | RTT p50 ms | p95 ms | p99 ms | Retrans TCP |
| :-- | :-- | --: | --: | --: | --: | --: |
| AA1 | up | 4.559 | 11.982 | 17.921 | 19.591 | 233 |
| AA1 | down | 73.936 | 13.369 | 24.425 | 26.868 | 0 |
| NATIVE28_AFTER | up | 16.096 | 11.662 | 16.902 | 17.732 | 15 |
| NATIVE28_AFTER | down | 74.126 | 13.960 | 17.446 | 17.986 | 0 |
| FINAL20_AA1 | up | 22.168 | 12.477 | 20.202 | 24.824 | 102 |
| FINAL20_AA1 | down | 77.347 | 14.598 | 17.548 | 17.564 | 0 |
| FINAL20_AA2 | up | 11.664 | 14.090 | 19.547 | 23.241 | 33 |
| FINAL20_AA2 | down | 70.665 | 12.939 | 18.092 | 18.234 | 0 |

up es CPE→AP; down AP→CPE. RTT siempre .110→Rocket. Un flujo TCP20s y20pings por sentido,
muestras numericas y cuatro sensores/memoria conservados. Las dos FINAL20 son nombres historicos
del ensayo temporal20, NO la configuracion final. Su rango A/A no es intervalo de confianza.
NATIVE28_AFTER es una captura a la solicitud oficial; no se completo un A/A final contemporaneo a28.
Antes/despues y correccion de potencia, sin ABAB: no se declara un ganador causal ni campeon universal.
El agregado de dos CPEs y el PtP no se midieron. El p99 con20muestras tiene precision limitada.

RX Lite2: recepcion y asociacion CONFIRMED durante el arranque nativo, no ambas cadenas sanas;
la comparacion inicial de espectro solo daba actividad INFERRED. Espectro raw no plano
alrededor5500 y RSSI variable. Espectro type1 cacheado, escala/frescura sin validar,
modos de scan distintos: no prueba ambas antenas sanas ni identifica al Rocket como origen de toda energia.
`docs/STAGE3102A_rx_test.json` conserva el detalle y la comparacion con .110.

RE exacto2.4.0: frame_len_store usa el callback de duty_cycle; no se escribio ese control.
txpwr_store modifica solicitud, txpwr_show expone salida calculada; no se usaron como inversa de restauracion.
Ver STAGE3102A_cpe_power_re.json y STAGE3102A_ltu_asymmetry_re.json.
Scholarmcp no disponible en la herramienta descubierta; consulta primaria externa acotada:
[RFC3449](https://www.rfc-editor.org/info/rfc3449/) y
[TDD/TCP Bell Labs](https://www.nokia.com/bell-labs/publications-and-media/publications/flexible-uldl-in-small-cell-tdd-systems-a-performance-study-with-tcp-traffic/)
respaldan hipotesis generales de asimetria/ACK; no prueban el mecanismo LTU de este par.

Rocket, antena y pais4097 intactos por decision expresa. Sin firmware, particiones protegidas,
produccion ni PowerBeam. Solo se guardo configuracion mediante el escritor nativo validado.
Todos los procesos de medicion quedaron CLEANED. Duracion total 50.5 min;
se supero el presupuesto30 durante el cierre, la correccion del control erroneo y recuperacion del enlace,
sin iniciar nuevos benchmarks ni ABAB despues del corte.
Pendientes: top5 nuevo/no documentado, dos tratamientos ABAB, causa completa de Lite2,
medicion dos estaciones/PtP y objetivo Karpathy (fq_overmemory UNKNOWN).
