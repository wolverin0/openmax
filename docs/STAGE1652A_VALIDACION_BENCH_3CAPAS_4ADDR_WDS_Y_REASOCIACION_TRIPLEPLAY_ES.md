<!-- doc-head: Wave102; auditoría WDS real y reasociación bajo carga, objetivo de cero pérdidas incumplido -->
12 ventanas A1/B1/A2/B2, seis reasociaciones forzadas y recuperación comprobada.
Se distinguen configuración declarada, observación de actores y aceptación funcional.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stages1650A..1655A: tres capas WDS y estrés de reasociación

## Resultado y alcance

Se ejecutaron tres rondas reales `A1 → B1 → A2 → B2` en el banco exclusivo:
AP LAP-120 `198.18.0.43`, STA Loco `198.18.0.67`, MAC `PUBLIC_DEVICE_0036`.
OpenWrt24.10.4, kernel6.6.110, 5180 MHz y 20 MHz.
La potencia inicial y final fue 20 dBm en AP y 17 dBm en STA.
Se verificaron identidad, claves de host fijadas y acceso a la STA a través del AP.
No se accedió a PowerBeam, LTU ni Guarida.

CONFIRMED: doce ventanas de carga y seis reasociaciones tras solicitudes `del_client`.
CONFIRMED: recuperación posterior, configuración y firmware conservados.
REFUTED en esta campaña: cero pérdidas de ping6 durante las desconexiones forzadas.
UNKNOWN: prueba directa de dos binds ejecutados por ambos actores en cada reasociación.
La adquisición y las pruebas de software se separan de esa aceptación operativa.

## Stage1650A: estado real de las tres capas

| Capa | Evidencia observada | Límite de la conclusión |
| --- | --- | --- |
| 1, UCI | `wds=1`, `wpa_group_rekey=86400`, `max_inactivity=60` | `disassoc_low_ack` explícito ausente |
| 1, archivo hostapd activo | `disassoc_low_ack=1`, `wds_sta=1`, bridge `br-lan` | No aparecen rekey ni `ap_max_inactivity`; sus valores efectivos quedan sin confirmar |
| 2, hotplug | Archivo ejecutable `99-fmx-4addr-verify`, filtro `ACTION=add`, espera5s y llamada `--fast` | El contenido demuestra intención; no prueba una ejecución nueva cuando se reutiliza el puerto |
| 3, healer | Archivo ejecutable y `PATH=/usr/sbin:/usr/bin:/sbin:/bin` explícito | La captura no prueba activación periódica; consulta de cron/crond sin resultado positivo |

Solo se usa el archivo `hostapd-phy4.conf` correspondiente al PHY activo.
Los archivos antiguos phy0..3 no demuestran configuración vigente.
La ausencia de un parámetro en el archivo generado tampoco prueba por sí sola su valor efectivo.
La primera consulta UCI terminó en salida1 por la opción ausente; se conserva y se complementa.
No se modificaron UCI, cron, scripts instalados ni configuración persistente.
El script desplegado y la copia local congelada coincidían byte a byte con `ban_time=500`.
Después del ensayo, otro cambio en el archivo compartido local pasó ese valor a1200;
`reason=5` permaneció igual. Se conserva la versión auditada y no se afirma equivalencia
con la copia posterior del repositorio, que no se desplegó desde este carril.

## Actores y significado de los binds

La fuente oficial de hostapd llama `i802_set_wds_sta` a la función relevante.
Si el AP_VLAN ya existe, su camino puede reutilizarlo sin repetir creación y attach al bridge.
En las seis reasociaciones se observó esa reutilización: `phy4-ap0.sta1` siguió disponible,
con forwarding posterior, sin una secuencia nueva de dos attaches en dmesg.

El nombre solicitado `wireless_station_update` no aparece en la revisión oficial
de netifd fijada por el paquete. `station_update` es un callback de configuración UCI.
Existe una ruta distinta `wireless_device_hotplug_event` → `wireless_interface_handle_link`
→ `interface_handle_link`; su existencia en fuente no prueba que se ejecutara en estos eventos.
Esto no se presenta como prueba negativa sobre todas las compilaciones desplegadas.

Se suscribió exclusivamente `hostapd-auth` durante28s por ventana.
Se conservaron tipo, interfaz y MAC de los eventos `sta_auth`/`sta_connected`;
se descartó el resto del payload en memoria. No se capturó un monitor ubus global.
Los seis B contienen una notificación `sta_connected` del peer esperado.
Esa notificación, una línea de link-up o forwarding final no prueban dos llamadas exitosas.

La orden de kick guardó uptime antes y después de ubus. Su shell carecía de `set -e`:
la salida0 final del shell no certifica el código devuelto por ubus.
Las solicitudes exactas y las reasociaciones posteriores están capturadas por separado.

## Stage1651A: ensayo físico y resultados

A mantuvo la asociación; B solicitó una desconexión con razón5 y veto500ms.
Las tres cargas estaban activas al solicitar el kick; el desplazamiento temporal real
se obtiene de uptime, sin afirmar un disparo exacto en el segundo5.
Cada ventana corrió20s de TCP bidireccional, IPTV UDP4Mbps/1316B y VoIP64Kbps/160B.
Los procesos independientes tuvieron guardas de45s y comprobación de PID/cmdline.
El tráfico fue directo entre radios; las CPU de los radios también ejecutaron la medición.

| Ronda | Goodput receptor A/B, Mbps | p95 ping6 A/B, ms | Pérdida ping6 A/B |
| --- | --- | --- | --- |
| I1 | 60.687 / 52.517 | 20.934 / 36.154 | 0% / 17.5% |
| I2 | 75.897 / 63.832 | 24.806 / 38.992 | 0% / 15% |
| I3 | 76.673 / 52.337 | 25.051 / 32.597 | 0% / 15% |

Son medias de dos ventanas por brazo, no una prueba de significación estadística.
Las seis ventanas B perdieron15%,20%,15%,15%,15%,15% de sus20 probes continuos.
IPTV y VoIP también perdieron aproximadamente17% durante esas ventanas.

| Conjunto de probes | Transmitidos | Recibidos | Pérdida |
| --- | --- | --- | --- |
| Continuos bajo carga, incluidos cortes | 240 | 221 | 7.9167% |
| Posteriores a las ventanas | 36 | 36 | 0% |
| Ambos conjuntos de campaña | 276 | 257 | 6.8841% |

El probe inicial de auditoría dio3/3 y se registra por separado.
No se quitaron pérdidas de desconexión para construir un resultado de cero pérdidas.
No hubo promoción de candidato: las tres rondas se registran como `discard`,
con parada por máximo de iteraciones, sin afirmar una meseta de rendimiento.

## Muestreo y reconciliación

Se conservaron24 muestras por ventana, con un `sleep1` más el coste de las consultas.
Los timestamps reales son la referencia; no se afirma una frecuencia exacta de1Hz.
Algunas primeras lecturas contenían23 muestras. La lectura final del archivo completado
contiene24 y coincide exactamente con el prefijo original, que también se conserva.

El criterio preregistrado de wedge usa tres muestras consecutivas de TXMCS0 o≤6.5Mbps,
RX≥24Mbps y contexto de bridge no-forwarding o ping6 perdido, después del asentamiento.
La evaluación se limita a los primeros24s y conserva los datos posteriores aparte.
No se observaron muestras de TXMCS0 en los archivos completos; esto no prueba ausencia universal.

En iperf3.17, `server.end.sum` devolvió bytes/bps cero con paquetes positivos.
La reconciliación usa `server.end.sum_received`, con bytes y tasa positivos,
y conserva los cálculos iniciales erróneos. No se repitió la medición física.
`fmx_loss` es una descripción posterior de las fracciones de pérdida de ping6/IPTV/VoIP,
sin selección de parámetros ni decisión causal basada en ese escalar.

La primera comparación final incluyó el contador de solo lectura `fq_collisions`.
Su cambio0→179 no era una modificación de configuración. Se conserva ese fallo;
la comprobación correcta compara los valores configurables, BQL, RF, firmware y mounts.
Se confirmó su conservación, la ausencia de las cargas propias y la liberación de leases.

## Investigación, memoria y verificación

Se reutiliza RE histórico cualificado y se distinguen fuentes oficiales de ejecución desplegada.
Pillar B incluye14 comprobaciones primarias y un reactor real en cola propia.
Scholar devolvió tres resultados heurísticos parciales y cero verificaciones Jev en vivo;
la búsqueda arXiv agotó su timeout y no se afirma que tuviera éxito.
MemoryMaster:1650A→157649 y1651A→157650, con readback exacto y estado `candidate`.
Confirmar registro y persistencia no promueve una afirmación científica.

- [Auditoría1650A](../artifacts/autoresearch/stage1650a_live_4addr_wds_3layer_best_practice_audit_receipt.json)
- [Estrés1651A](../artifacts/autoresearch/stage1651a_live_4addr_reassoc_triple_play_stress_receipt.json)
- [Datos físicos congelados](../artifacts/autoresearch/wave102/physical/runtime_frozen_manifest.json)
- [Reconciliación de receptores](../artifacts/autoresearch/wave102/physical/measurement_reconciliation.json)
- [Gate1655A](../artifacts/verification/stage1655a_wave102_codex1_gate.json)

`python -m pytest tests/test_stage1650a_to_1655a_suite.py -q`

`python tools/verify/enforce_5pillar_research_gate.py <recibo> --require-live-hardware`

El gate de esquema y las pruebas de software no sustituyen los criterios de aceptación física.
El gate Wave102 conserva como incumplidos cero pérdidas globales y la prueba de ambos binds.
La primera corrida pytest,124PASS/4FAIL, queda archivada. Las reparaciones del verificador
usan la versión histórica exacta y los formatos nativos de salida; no cambian los datos RF.
