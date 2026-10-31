<!-- doc-head: Wave48: estabilidad LED bajo carga y alcance de integración WA v7 -->
La corrección del indicador, la carga observada y el overhead causal son resultados diferentes.
Sin control LED OFF/ON contrabalanceado, zero-overhead permanece UNKNOWN.
<!-- /doc-head -->

# Stage 1329A — Indicadores bajo carga e integración WA v7

La campaña preregistrada ejecutó cinco ventanas consecutivas, conservando todos
los resultados. El daemon permaneció encendido en
ambos PowerBeam de banco: `.241` AP y `.242` STA. Se conserva el perfil bench65
(-80/-75/-70/-65 dBm) y la configuración PtP v17.

Cada ventana conserva el RAW y sus hashes, dos flujos HTTP TCP, UDP echo real
de 64/1316 bytes, ICMP, CPU/softirq y LED antes, durante y después. El gate recalcula
las métricas desde los datos originales y compara JSON con sysfs, RSSI,
asociación, perfil y servicio. Una barra sólo se exige encendida cuando el
RSSI medido alcanza su umbral. Hubo **30 observaciones LED con cuatro salidas
encendidas**, servicio activo y perfil bench65: cinco ventanas, dos radios, tres fases.

## Resultados vivos del banco

CONFIRMED_LIVE_HARDWARE. HTTP informa payload completado/tiempo de la ventana;
RTT corresponde a diez ICMP por ventana bajo TCP y UDP concurrentes.

| Ventana | HTTP Mbps | RTT ICMP p50/p95/p99 ms | UDP no emparejado % | Sirq AP/STA % | Ticks daemon AP/STA |
| --- | ---: | --- | ---: | --- | --- |
| 1 | 14.11 | 21.95/42.97/47.03 | 13.33 | 20.00/32.56 | 157/88 |
| 2 | 15.07 | 22.90/70.05/72.16 | 0.00 | 20.41/31.75 | 155/100 |
| 3 | 13.80 | 25.75/44.17/47.64 | 4.17 | 24.95/39.16 | 186/103 |
| 4 | 15.25 | 21.34/31.34/34.79 | 0.00 | 17.68/30.26 | 155/92 |
| 5 | 14.67 | 20.34/31.57/33.33 | 7.69 | 19.12/30.12 | 171/105 |

ICMP: **50/50 recibidos**, más diez guardas fuera de carga de 3/3 cada una.
UDP: **138 enviados, 131 echoes emparejados**, 134 recibidos y 134 enviados
por el servidor. Los siete no emparejados son observados (5.07%). Una revisión
independiente detectó división entera en `t[1]/1000000000`: el reloj ejecutado
quedó cuantizado en segundos. **QoE/deadline de 150 ms es UNKNOWN_INVALID_TIMER**;
no se puede llamar al 5.07% pérdida bajo un deadline válido. Los RTT UDP originales
se conservan como inválidos para esa interpretación. Cuatro datagramas no aparecen
recibidos por la aplicación servidora (2.90%); no equivalen a drops físicos RF.

Las colas/configuración v17, canal, identidad de arranque y contadores de
reinicio permanecieron iguales. Los locks se liberaron y el helper/módulo UDP
cargado en RAM se retiró con hashes y lectura posterior verificadas.
FDB/ARP posterior aprendió al par por `phy2-ap0.sta1` en AP y `phy2-sta0` en STA.
Es observación **POST_CAMPAIGN_FDB**; los deltas de bytes por interfaz en cada
ventana **no se registraron**.

## Alcance científico

El porcentaje CPU procede de deltas `/proc/stat`: se excluyen los campos guest
que ya están incluidos en user/nice. Los contadores deben ser enteros,
monótonos y tener un intervalo positivo. Datos vacíos o inválidos no son cero.
Softirq positivo es carga observada del sistema; no se atribuye automáticamente
al daemon ni demuestra por sí mismo el costo del indicador.

Los ticks del daemon más hijos esperados son positivos en las diez mediciones:
la afirmación literal de **cero CPU de ejecución es REFUTED**. Son contadores
de ejecución observados, sin convertirlos en una regresión causal de Sirq.
Las cinco ventanas LED ON no contienen un control LED OFF/ON contrabalanceado.
Por ello **overhead causal/regresión de Sirq es UNKNOWN**, incluso si una
muestra informara cero softirq. La implementación puede pasar sus checks
mientras CPU cero queda refutado y QoE UDP 150 ms queda sin medición válida.
No se detiene el daemon para inventar un control fuera del preregistro.

Los bytes ejecutados del helper y runner quedaron archivados con sus SHA256.
El helper futuro usa división flotante, verifica el deadline después de recibir
y conserva el RTT del instante aceptado; el parser futuro exige COVERAGE rc0.
Son reparaciones locales: **no se repitieron las cinco ventanas ni se desplegó
el helper corregido**. Sus pruebas de reloj usan un modelo aritmético acotado
de ucode, separado de una validación de runtime/ABI en los radios.

## Integración y simulación de cuatro placas

El compañero nuevo WA v7 es independiente de las fuentes canónicas Wave44.
Admite exclusivamente PowerBeam 5AC Gen2, LiteBeam AC Gen2, NanoStation AC loco
y LAP-120, identificados por su board ID. Las fuentes de identidad de placa
deben concordar; un modelo desconocido o contradictorio falla cerrado.
El overlay conserva empaquetado TAR con permisos objetivo explícitos y
validación de hashes. Los permisos del host Windows/DrvFS no sustituyen los
permisos de destino dentro del paquete.

El paquete mapea PBE a `blue:rssi0..3`, LBE/NS Loco a `blue:power` y LAP-120
a `white:dome`. En placas de un LED indica asociación; `bars_lit` es RSSI lógico
0..4 y `led_count=1` declara el número físico. No se inventan cuatro LEDs.

Pasaron ocho escenarios asociados/no asociados de las cuatro placas y cinco
adversarios, ejecutando el shell real con `iw`/sysfs descartables en Linux.
Su alcance es SIMULATED_FIXTURES_ONLY. No representan
asociaciones PtMP físicas, clientes vivos ni aceptación en las otras placas.
La aceptación PtMP viva y la confirmación visual humana permanecen UNKNOWN.
El overlay es un compañero explícito para un futuro empaquetado; las 16 imágenes
WA v7 existentes y canonical Wave44 se conservaron sin reconstrucción ni flasheo.

## Recibos y aceptación

- [Carga PtP 1326A](../artifacts/verification/stage1326a_ptp_loaded_led_stability_receipt.json)
- [Paquete WA 1327A](../artifacts/verification/stage1327a_wa_v7_universal_led_overlay_sync.json)
- [Fixtures 1328A](../artifacts/verification/stage1328a_four_wa_boards_led_simulation_receipt.json)
- [Gate 1331A](../artifacts/verification/stage1331a_wave48_codex2_gate.json)

La evidencia final se conserva en los recibos. El gate separa
`implementation_and_local_gate_passed` de `literal_all_requirements_passed`;
ningún PASS local autoriza afirmar overhead cero, rendimiento RF nuevo o
aceptación física de la matriz WA.
