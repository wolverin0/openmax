<!-- doc-head: Wave84 banco fisico PtP Triple-Play y preflight Colo -->
Tres iteraciones finitas con datos reales y decisiones keep/discard/crash trazables.
Sin subagentes, simulacion de rendimiento, escritura flash ni migracion de Colo.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage1544A: banco vivo PowerBeam y runbook PtP-Colo

Estado: CONFIRMED para adquisicion fisica; sin promocion ni certificacion de produccion.
Banco: 198.18.0.45 AP y .242 STA; origen Ubuntu .186; daemon LEDv4 activo.
La STA tiene eth0 sin carrier; la MAC del servidor se aprende por Wi-Fi y cada ventana conserva deltas OTA.
iperf3 se extrajo en /tmp desde paquetes oficiales con hashes; no se instalo en flash ni globalmente.

## Plan y resultados

Tres iteraciones, cada una A1/B1/A2/B2 de20s. Carga: TCP, IPTV UDP3Mbps/1316B y sondas G711 UDP64kbps/160B.
ICMP:200 sondas64B a100ms. Se guardaron RSSI/cadenas, reintentos, colas, BQL/AQL y /proc/stat.
Iteracion1: coverage0/4; lectura host-shadow, sin prueba directa de registros de temporizacion RF.
Iteracion2: AQL VO/VI/BE5000/12000 frente a600/1200,1500/3000,2500/5000us; BK intacto.
Iteracion3: BQLmin4542/hold800ms en ambos brazos; quantum1514 frente a4542.

| Iteracion | Decision | fmx_loss B | TCP A/B Mbps |
|---|---|---|---|
| 1 | crash | NA | NA |
| 2 | keep | 0.773805 | 19.660/19.279 |
| 3 | keep | 0.729014 | 20.922/20.718 |

A1 original tuvo timeout G711 y error de restauracion por printf con salto final en debugfs.
Se preservo el fallo y se restauro el estado inicial con lectura exacta. No se repitio A1.
La enmienda fija UDP antes del TCP con0.5s de diferencia; solapamiento cargado comun19.5s.
Los datos faltantes son NA, nunca cero. El umbral keep exige mejora emparejada0.005 y capacidad>=95%.
La comparacion incompleta conserva crash. Cada ventana usa guardia independiente60s y restauracion verificada.
LED: lecturas periodicas AUTO4/4 y SHA del daemon; no equivalen a observacion continua de ausencia de parpadeo.
No hay holdout disjunto ni aceptacion independiente: conservar o descartar no certifica un champion.

## Watchdog vivo y limites

En .242 se observaron expiraciones reales de60s noDFS y120s DFS; heartbeat desarmo en2s.
La falla de sonda fue inyectada explicitamente en dry-run-live, sin tocar el enlace.
El script v18 de esta etapa valida timers; no implementa ni autoriza una recuperacion de campo.

## Checklist de corte de campo

0. `OPERATOR_REQUIRED`: Autorizar otra ventana de produccion PtP-Colo y el drenaje WAN a cargo de Infra. Wave84 no autoriza flash, retune, desactivar mangle ni maniobras PoE.
1. `FRESH_READ_ONLY_BASELINE`: Identificar AP198.18.0.91 y STA198.18.0.92 por sysid0xe7f9 y MAC. Leer mca-status, iwconfig, radio.1.chanbw/ieee_mode/freq/wds/allow_80211/chains, senal, ruido, tasas, uptime y ping repetido. Renovar estado y trafico MK2-RS ether10-colo; faltan RTT y referencia historica completa del router.
2. `RF_AND_REGULATORY`: Confirmar frecuencia, ancho, DFS/CAC y pais en ambos extremos y ancho de Abeni co-ubicado. Sin scans ni cambio de canal bajo esta autorizacion. Elegir timer60s noDFS o120s DFS tras clasificacion actual; el timer no reemplaza la aceptacion CAC reglamentaria.
3. `BACKUPS_AND_RESTORE_PATH`: Leer y calcular hashes mtd0/1/4/5, configuracion completa y calibracion. Conservar copias independientes verificadas. Nunca escribir mtd0, mtd1, mtd5, MAC ni calibracion. Verificar imagen conocida y recuperacion especifica del modelo antes de tocar firmware.
4. `IMAGE_AND_OVERLAY`: Fijar SHA256 de imagen factory revisada para LiteBeam5ACGen2. Inspeccionar SquashFS: IP exacta STA, SSID, puntero de credenciales, disabled=0, WDS y perfil RF permitido. Verificar 99-fmx-pbe5ac-ptp, rollback real, ajustes compatibles v17, telemetria LEDv4 sin GPIO y arranque. No usar imagen PowerBeam en LiteBeam.
5. `WAN_DRAIN_AND_CONFIRM`: Infra debe aportar comandos COLO mangle/routing reversibles con IDs actuales y ejecutarlos solo tras aprobacion del operador. Verificar drenaje de trafico cliente y capacidad WAN restante. Nunca desactivar ether2-sw-poe200 ni switches PoE compartidos.
6. `HYBRID_BENCH_PROOF`: Exigir aceptacion independiente airOS8 AP allow_80211=1/op_mode=0 CSMA-WDS con OpenWrt STA en placas equivalentes y requisitos de interop AP con CPE stock. El banco full-OpenWrt actual no prueba interop hibrida.
7. `ARM_REAL_ROLLBACK`: Antes del cambio de campo guardar estado original exacto y preparar rollback real independiente con observador heartbeat externo. Verificar accion y timer por lectura. El script v18 de Wave84 solo valida dry-run-live y no ejecuta rollback de produccion.
8. `REMOTE_STA_FIRST`: Con gate flash aprobado por separado migrar primero STA remota .105.54 OTA, dejando AP .105.62 en airOS. Sin subir a torre ni pedir cable local. Si falta gestion, asociacion, arranque o salud, no desarmar y ejecutar la recuperacion real revisada.
9. `HYBRID_ACCEPTANCE`: Capturar identidad de arranque, configuracion persistida exacta, asociacion, senal/ruido/tasa contra referencia fresca, gestion y conectividad cliente, perdida/latencia, Triple-Play real y salud WAN. Desarmar solo tras aceptar todos los controles; en caso contrario, rollback.
10. `LOCAL_AP_SECOND`: Solo tras aceptar modo hibrido y autorizar flash por separado migrar AP local .105.62 OTA. Mantener guardia independiente y repetir mediciones full-OpenWrt en campo. No inferir aceptacion a partir del banco.
11. `AA_DISCOVERY_HOLDOUT`: Antes de promover exigir control nulo A/A, discovery A/B preregistrado y holdout disjunto con SHA256 crudos, procedencia y RegressionGatekeeper de no inferioridad de capacidad. Dos pares exploratorios por hipotesis Wave84 no certifican un champion de produccion.
12. `RESTORE_SERVICE_AND_CLOSE`: Verificar persistencia tras arranque en frio solo en ventana aprobada, restaurar drenaje WAN por IDs exactos, confirmar flujos cliente y recuperacion aceptada, guardar recibos inmutables y liberar leases propios. Produccion sigue UNKNOWN hasta aceptacion independiente.

## Evidencia

[Recibo1542A](../artifacts/autoresearch/stage1542a_live_ptp_pbe5ac_triple_play_autoresearch_receipt.json).
[Watchdog y checklist1543A](../artifacts/autoresearch/stage1543a_live_ptp_colo_watchdog_and_cutover_receipt.json).
Cinco pilares: catalogo, sintesis de consultas y bibliografia1470A reutilizada, ABAB fisico, diseno experimental y recall MemoryMaster.
El identificador FMX del recibo vincula una afirmacion local; no se presenta como una nueva ingesta durable.
PtP-Colo conserva estado de produccion UNKNOWN: esta ola no modifica .105.62/.105.54 ni MK2-RS.
