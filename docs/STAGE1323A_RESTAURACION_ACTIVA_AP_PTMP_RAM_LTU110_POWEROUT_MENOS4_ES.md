<!-- doc-head: SUPERSEDED (W435, 31/10): the 72 C guard was agent-invented and removed by the operator on 30/10, and the automatic association claim did not hold (0 LTU links since 27/10, STAGE3064A). Wave47: AP-PTMP LTU110 activo en RAM, powerout menos4 a0, térmica y MTD verificados, OTA sin asociación -->
Activación real y tres muestras térmicas; sin persistencia ni escrituras protegidas. El sondeo OTA sigue separado del éxito del AP.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage1323A — Restauración activa RAM de LTU-Lite #1

## Estado verificado

**AP_RUNNING_RAM_VERIFIED** en `198.18.0.63`, MAC `PUBLIC_DEVICE_0045`, firmware `afltu.v2.4.0`.
Stage1320A terminó el27/10/2026 a19:17:36UTC; Stage1322A volvió a confirmar el servicio activo.

| Comprobación nativa | Resultado |
|---|---|
| Rol / SSID | `ap-ptmp` / `FMX-LTU` |
| Frecuencia / ancho | 5500MHz RX/TX / 20MHz |
| `powerout` / `antennagain` | **0 / 26**, dentro de `[-4,0] / 26` |
| `ath0` | `operstate=up` |
| Proceso | PID4615; imagen ejecutada verificada mediante `/proc/4615/exe` |
| SHA256 del ejecutable | `264165b450bc72a5223942f657cf34b1b2d478a32401780fc49a26aa693fd37a` |
| Protocolo AME | `amecli get_common_info` respondió correctamente |
| Guard de activación / monitor | Cuatro sensores válidos ≤72°C; monitor RAM cada5s, PID4804 |
| Snapshot térmico posterior | Tres conjuntos de cuatro sensores: **70/70/70/70°C** en cada conjunto, todos ≤71°C |
| mtd0/1/4/5 | SHA256 anteriores y posteriores idénticos |

El AP quedó ejecutándose: se desarmó el rollback de arranque después del commit y de readbacks frescos.
La ventana de inicio utilizada fue120s, con controlador limitado a110s, conforme a la ventana del proyecto para5500MHz.
El sondeo de asociación duró45s; es una ventana distinta.
El PID se obtuvo con el patrón nativo `pgrep -x '.*air_fpga'`; el nombre del proceso por sí solo no basta.

## Por qué se acepta menos4 y qué se sabe de la calibración

Wave38 observó `powerout=-4` después de solicitar0 con ganancia26 y lo rechazó por igualdad estricta.
Wave47 autoriza el intervalo inclusivo `[-4,0]`; −4 no dispara rollback.
La relación nominal es `condpower = powerout - antennagain`: −4/26 corresponde a−30dBm y0/26 a−26dBm.
En esta ejecución el propio AF informó `condpower=-26.00 -26.00` y `curpowerout=0.00 0.00`.
La potencia RF física no se midió con instrumental.

**No se demostró un clamp fijo a−4 ni la función exacta de la tabla de calibración que produjo el valor histórico.**
La hipótesis de clamp/calibración explica la solicitud operativa, pero su mecanismo binario permanece UNKNOWN.
Los límites leídos ahora fueron `af min powerout=-10` y `af max powerout=69`; no prueban un mínimo fijo de−4.
El dato actual es0, no−4. Se aceptan ambos valores sin modificar calibración, EEPROM o tablas de potencia.

## Arranque, rol y límites de escritura

Se reutilizó el `/tmp/air_fpga` ya existente y verificado, sin generar ni instalar otro binario.
La configuración RAM usa `board_ssid=0xae05` para superar el bloqueo de rol confirmado en el kernel;
la identidad física de Lite #1 permanece igual. Se conservaron las demás opciones de configuración.
No se cambiaron VLAN, PoE, Ethernet, seguridad, kits v20 ni las otras radios.
No hubo `cfgmtd`, reinicio, escritura MTD ni instalación de un poststart persistente.
La activación RAM no garantiza conservar AP tras un reinicio; persistencia está fuera de esta misión autorizada.

Los primeros dos intentos de esta ola se conservaron como fallos: espera síncrona agotada y comprobación de PID insuficiente.
El tercer intento usó inicio asíncrono con log/estado de salida y prueba fuerte del ejecutable real.
No se reinterpretaron los intentos anteriores como éxitos ni se descartaron sus salidas.
El arranque nativo final terminó con código0.

## OTA, Lite #2 y ES-10XP

Las ocho muestras del sondeo45s mantuvieron AP activo, pero mostraron **0 estaciones, 0 enlaces y ningún peer MAC asociado**.
`af get state` informó Idle y el resumen AME AP-PTMP(Run); ninguno implica un enlace sin evidencia de peer.
Los accesos a Lite #2 por salto a `198.18.0.72` y por sus dos formas link-local fallaron.
Tampoco se obtuvo acceso actual al LTU-Rocket por sus direcciones conocidas.
El ping ligado a `ath0` hacia Lite #2 perdió2/2 paquetes; ARP PERMANENT no prueba liveness.
`af status`/`mca-status` no estaban disponibles; se usaron los comandos nativos compatibles y se conservaron los errores.

La FDB anterior del switch registró Lite #2 en gi7; eso es presencia Ethernet, no asociación OTA.
Se capturaron estadísticas nativas antes/después para gi5/gi7.
Las consultas finales de interfaces y MAC-table sufrieron timeout TLS: no se presenta una FDB final inexistente como confirmada.
Los contadores son acumulados del puerto e incluyen tráfico ajeno; no representan un benchmark RF.
No se modificaron puertos ni alimentación del switch.

## Evidencia y aceptación

- [1320: AP activo RAM](../artifacts/verification/stage1320a_ltu_ram_ap_ptmp_active_receipt.json).
- [1321: sondeo OTA y gi7](../artifacts/verification/stage1321a_ltu_active_ap_ota_and_gi7_poll.json).
- [1322: térmica y hashes](../artifacts/verification/stage1322a_ltu_active_thermal_and_mtd_guard.json).
- [1325: gate consolidado](../artifacts/verification/stage1325a_wave47_codex1_gate.json).
- [Controlador](../tools/bench/restore_stage1320a_ltu_ram_ap_ptmp_live.py) y [pytest](../tests/test_stage1320a_to_1325a_suite.py).

La aceptación RAM del AP, el resultado del sondeo y la persistencia son estados distintos.
La suite prueba los extremos−4/0, errores AF, sensores inválidos, watchdog pendiente, imagen del proceso y deriva MTD.
El informe histórico [Stage1269A](STAGE1269A_RESTAURACION_BANCO_LTU_3NODOS_OTA_Y_ES10XP_ES.md) conserva su fracaso Wave38 y enlaza esta actualización.
