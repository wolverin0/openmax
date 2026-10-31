<!-- doc-head: SUPERSEDED (W435, 31/10): the 72 C / 68 C thermal guard was agent-invented and removed by the operator on 30/10; temperature is telemetry only (orchestration/thresholds.json). Wave 62; preflight térmico bloqueado y canales OpenWrt capturados en vivo -->
LTU110 quedó apagado; no se inició RF ni se fabricó una curva térmica.
El kernel de .241 expone 27 frecuencias de 5 GHz en phy2; no acredita toda la flota.
El gate separa pruebas locales, observación real y criterios físicos pendientes.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 1413A — Burst-and-Park y tabla real de canales

## Estado de LTU-Lite #1

Stage 1410A ejecutó el preflight real contra `198.18.0.63`, con identidad
`PUBLIC_DEVICE_0045`, LTU-Lite, clave de host fijada y binario RAM auditado.
El resultado fue `BLOCKED_SAFETY_PRECONDITION`, salida 1.
Antes y después: `air_fpga` ausente, flags del driver ausentes y `ath0` DOWN.
No hubo arranque RF, escritura de configuración, flash, reinicio ni acceso a `/dev/ame*`.

El host remoto no tiene `timeout`, tampoco el applet BusyBox equivalente.
No expone `/proc/PID/task/PID/children`; su `ps` tampoco admite el formato requerido.
Se conservan las respuestas nativas de esas comprobaciones.
El script nativo `ame_drv.sh` pone `.drv_starting` antes de iniciar `air_fpga`,
espera en `amecli waitrdy -r 20` y sólo después retira ese flag.
Su función `f_stop` retorna sin apagar cuando encuentra `.drv_starting`.
Por tanto, lanzar `sleep 45; ame_drv.sh stop` no garantiza apagar un arranque atascado.
La revisión independiente encontró también el riesgo de que un arranque pendiente
reactivara RF después de una comprobación de apagado.

No se sustituyó ese mecanismo por señales o eliminación de flags sin verificación.
El candidato de script remoto está marcado NOT RELEASED y el adaptador vivo bloqueado.
No hay temperatura inicial medida, trayectoria térmica ni asociación OTA en esta etapa.
Tampoco se ejecutaron los 180 s de observación de enfriamiento: el bloqueo ocurre antes.
El reposo histórico no se convierte en una temperatura confirmada.

## Protocolo solicitado y guardas implementadas

El punto de entrada existente admite `--live-45s`, que invoca el nuevo preflight.
Las interfaces de simulación de Wave 59 conservan su comportamiento.
Se archivó el controlador anterior; los recibos históricos no se repincharon.
Su PASS corresponde a aquella revisión, no certifica los archivos modificados actuales.

El plan exige 180 s continuos de estado PARKED antes de un único intento,
cuatro lecturas válidas dos segundos después de detectar IPC y máximo inicial de 68 °C.
Las lecturas posteriores tienen máximo de 71 °C; errores, valores inválidos o 255
no se convierten en mediciones ni autorizan continuar.
Perfil previsto: AP-PTMP, 5500 MHz, 20 MHz, FMX-LTU, powerout -4 y antennagain 26.

El presupuesto empieza antes de RF: iniciar apagado a los 45 s y confirmarlo antes
de 60 s, reservando 15 s para detener. La inicialización reduce el tiempo OTA útil.
No se promete una ventana de 45 s adicionales después del arranque.
Muestrear cada 5 s no demuestra que no existan picos entre muestras.
La cancelación verificable del arranque y el apagado independiente siguen pendientes;
por eso estas guardas no habilitan todavía una ráfaga física.

## Captura real de PowerBeam .241

Stage 1411A consultó `.241` en solo lectura, sin escaneo RF ni cambios de región.
Identidad nativa: PowerBeam Gen2, MAC Ethernet `PUBLIC_DEVICE_0064`.
Kernel `6.6.110`, `iw 6.9`; el PHY de 5 GHz actual es `phy2`, con driver `ath10k_pci`.
Se conservan las evidencias de driver; no se deduce una variante CT sólo por el nombre.
La versión CT y el chip específico QCA9882 quedan UNKNOWN: faltan versión del módulo e ID PCI.
`phy1` usa `ath9k`; sus 24 entradas de 5 GHz están deshabilitadas.
No se mezclaron ambos PHY ni se supuso que el radio principal fuera `phy0`.

La interfaz AP observada estaba en 5200 MHz, ancho 20 MHz, SSID FMX-PBE-PTP.
No se cambió a 5190 MHz/40 MHz ni se contactó `.242`.
El dominio observado fue US / DFS-FCC; esto describe el estado, no certifica
autorización regulatoria para otro país, instalación o ancho de canal.

| Frecuencias listadas en phy2 | Máximo informado | Restricción observada |
|---|---|---|
| 5180, 5200, 5220, 5240 MHz | 23 dBm | Sin radar/no-IR en esas filas |
| 5260, 5280, 5300, 5320 MHz | 24 dBm | Radar/DFS |
| 5500 a 5720 MHz, pasos de 20 | 24 dBm | Radar/DFS |
| 5745, 5765, 5785, 5805, 5825 MHz | 30 dBm | Sin radar/no-IR en esas filas |
| 5845, 5865 MHz | 27 dBm | no IR |

Son 27 frecuencias listadas y no marcadas disabled en phy2.
Los dBm son límites reportados por canal, no potencia medida ni EIRP.
La pertenencia a la lista no demuestra que el AP pueda iniciar transmisión,
que todo ancho sea viable ni que todas las placas o contrapartes sean compatibles.
`iw reg get` y las restricciones de ancho originales permanecen en el recibo.

El primer parser esperaba MHz enteros y produjo cero filas ante `5180.0 MHz`.
Se preservaron esa salida, el código ejecutado y la corrección offline para decimales.
No se presenta esa corrección como una segunda observación de hardware.

## Cruce UISP y límites de cobertura

Stage 1412A cruza las frecuencias reportadas por UISP con las filas del PHY de 5 GHz.
La consulta nueva GET `/devices` respondió: 604 equipos, 432 con estado active;
417 de esos activos reportaron frecuencia y 15 no. Diez carecen de identidad completa.
Sólo 173 activos aportaron lastSeen/updated de hasta 24 h; ese metadato no fecha
necesariamente la medición de frecuencia. El inventario antiguo de 606 equipos no se usó.
Dentro del intervalo explícito 5000 ≤ MHz < 5925 hay 350 activos y 39 frecuencias:
168 coinciden con canales listados, dos coinciden con no IR y 180 no coinciden exactamente.
Otros 67 reportan 5925 ≤ MHz < 7125; se separan del subconjunto estricto de 5 GHz.
Esos números extendidos no prueban que su hardware sea de 6 GHz ni su compatibilidad.
El recibo conserva fuente, antigüedad, identificadores, anchos y categorías de coincidencia.
Un centro de 40 MHz ausente como canal primario no demuestra incompatibilidad:
sin semántica centro/control y ancho confirmado, esa conclusión queda UNKNOWN.
No se equipara inventario histórico o accesibilidad Ethernet con RF actual.
El cruce sobre una sola PowerBeam no certifica el 100 % de los enlaces PtP/PtMP.

## Evidencia y ejecución local

- [1410A: preflight y bloqueo](../artifacts/verification/stage1410a_ltu110_live_45s_burst_and_park_receipt.json).
- [1411A: canales nativos](../artifacts/verification/stage1411a_openwrt_241_live_iw_phy_channel_list.json).
- [1412A: comparación UISP](../artifacts/verification/stage1412a_live_iw_phy_vs_uisp_frequencies.json).
- [Controlador y preflight](../tools/bench/run_stage1410a_ltu110_live_45s_burst.py).
- [Suite 1414A](../tests/test_stage1410a_to_1415a_suite.py).
- [Gate 1415A](../artifacts/verification/stage1415a_wave62_codex1_gate.json).

`python -m pytest tests/test_stage1410a_to_1415a_suite.py -q`

El gate debe mantener INCOMPLETE para el objetivo físico pendiente, aunque pytest pase.
Para habilitar RF hace falta un mecanismo revisado que quiesca el arranque y permita
el apagado independiente dentro del presupuesto; no basta con observar un temporizador.
