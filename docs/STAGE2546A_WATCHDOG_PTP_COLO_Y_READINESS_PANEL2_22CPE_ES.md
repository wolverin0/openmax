<!-- doc-head: Wave251, watchdog PtP-Colo y auditoría sanitizada de Panel2 -->
Trabajo offline: payload preparado, pruebas desechables y evidencia histórica auditada.
PtP-Colo y los22CPE de Panel2 permanecen en HOLD para despliegue.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# Stage2546A — Watchdog PtP-Colo y preparación de Panel2

## Decisión ejecutiva

Wave251 no abrió sesiones SSH ni escribió en radios.
El cierre local valida los productos offline y conserva los bloqueos operativos.
No autoriza flashear las imágenes ni migrar Panel2.

## Stage2544A: imágenes y recetas

Se auditaron las dos imágenes guardadas de Stage2520, de6910340bytes cada una.
Sus SHA256 coinciden con los recibos originales; las cabeceras OPENW y SquashFS están presentes.
El CRC de cabecera uImage es válido, pero el CRC del payload no coincide.
CRC almacenado: `3bc59b1c`; calculado: `8ed8bc49`.
Una segunda implementación independiente confirmó el desajuste en la base guardada y ambas derivadas.
Los payloads afectados son idénticos; no se atribuye el fallo a un repack concreto.
No se modificaron ni repinaron los binarios para ocultar ese resultado.
Se desconoce cómo reaccionaría el bootloader de cada equipo; las imágenes no quedan aceptadas.

La extracción local confirmó por allowlist rol, psk2, WDS, VHT20, channel207 y las identidades esperadas.
No se exportaron claves ni identificadores físicos de las configuraciones.
El primer acceso SquashFS desde el montaje Windows agotó30s; el intento quedó conservado.
La extracción posterior usó copia temporal Linux, un descompresor y eliminación al terminar.

La evidencia2521 indicaba airOS8 y kernel2.6.32 en ambos equipos, no OpenWrt.
Es una captura histórica, no una lectura actual de esta wave.
Convertir ambos equipos requiere un proceso distinto de cargar un módulo en un OpenWrt existente.
Las imágenes auditadas todavía no incorporan el watchdog nuevo: falta reconstruirlas e inspeccionarlas.

## Payload de primer arranque

Se generan árboles separados para AP198.18.0.91 y STA198.18.0.92.
Gateways de gestión:198.18.0.120 y198.18.0.121, respectivamente.
Incluyen `/usr/sbin/fmx_ptp_colo_watchdog.sh`, servicio procd y hook UCI de primer arranque.
El hook habilita e inicia el servicio; `ENABLED=0` mantiene su ejecución inerte por defecto.
No hay recarga desde un evento hotplug de alta que pueda entrar en recursión.

Antes de habilitarlo se necesita un archivo privado con el peer esperado, fuera de este paquete.
La salud exige el perfil ptp_colo de netifd, phy0, el SSID configurado, psk2, WDS y el peer exacto.
También exige frecuencia6035, ancho20MHz, daemon activo y ping al gateway de gestión.
Ese ping de gestión no se presenta como tráfico medido por el enlace OTA.

Si no levanta el objetivo en120s, evalúa fallback5200MHz/canal40.
Sólo procede si phy0 anuncia esa frecuencia sin disabled/noIR.
La STA recibe scan_list5200/6035, que netifd convierte en freq_list del supplicant.
No se confunde esa lista con la numeración del canal AP.
La configuración se prepara aparte y se reemplaza mediante rename del archivo wireless.
Un guardia separado de45s queda armado antes del reemplazo.
Un enlace duro sobre una decisión única arbitra COMMIT frente a ROLLBACK.
Si falla el fallback, se restaura la preimagen exacta; no se implementa una vuelta a airOS por flash.
Red, identidad, SSID, clave, WDS, país y potencia se preservan.
La atomicidad es por archivo y nodo; no es una transacción distribuida simultánea entre las dos radios.

La aritmética5GHz asigna6035 al canal207.
El código base de wpad trata6035 mediante la numeración6GHz, canal17/opclass131.
Eso no demuestra aceptación del canal207 parcheado por wpad ni por el equipo.
5200/canal40 tiene correspondencia estándar; su uso aún requiere validación bilateral y regulatoria.

## Pruebas y límites

Se probaron ramas de salud, fallo de wpad, gateway, PHY, peer incorrecto, recarga y guardia.
El arnés usa sistema de archivos desechable y mocks de todos los comandos de equipo.
La recuperación tras matar al padre invoca manualmente la rama del guardia.
No demuestra supervivencia real de un proceso desacoplado, arranque frío ni aceptación física.
Se conserva la primera revisión y los fallos encontrados por revisión independiente.
La suite añade manipulación de imágenes, manifiestos, datos de inventario y recibos.

## Stage2545A: Panel2,22CPE históricos

| Dato observado | Resultado |
|---|---:|
| Registros RF reconciliados | 22 |
| LiteBeam5ACGen2 | 21 |
| LiteBeam5ACLR | 1 |
| Familia/versión de firmware explícita | 0 |
| Clasificación WA/XC/XW/XM desconocida | 22 |
| Deltas derivados de cadenas disponibles | 22 |
| Deltas mayores de4dB | 2 |
| Delta máximo observado | 5dB |
| Pares RSSI crudos y máscaras de cadenas conocidos | 0 |
| CPE autorizados para migrar | 0 |

Se usó la radiografía20261024 y se conservó su hash; no se dedujo firmware a partir del modelo.
Las filas nuevas tienen identificadores secuencialesP2-001..P2-022.
La exportación usa allowlist y no incluye apellidos ni direcciones físicas de clientes.
El contexto Panel1/Panel3 respalda verificar psk2/CCMP, WDS y reenvío de puente en ambos extremos.
AQL1200/2400 es un candidato solicitado: falta probar soporte por familia y leer valores reales.
No se atribuye ese ajuste a una medición histórica que no lo registra.

Antes de migrar faltan inventario actual, firmware exacto, RSSI por cadena y máscaras activas.
También faltan interoperabilidad AP con todas las clases stock, pruebas OTA, backups y recuperación validada.
Los desbalances de cadenas exigen diagnóstico; no se corrigen mediante una afirmación de firmware.

## Memoria, pilares y cierre

Stage2547 registra un claim consolidado en project:futuramax, con lectura posterior.
Los alias por etapa referencian ese único claim; no son múltiples ingestas inventadas.
A: auditoría binaria histórica y CRC. B: fuentes primarias y Scholar nativo cualificado.
Scholar no aportó verificaciones semánticas Jev en vivo; no se inventó una ejecución completa del reactor.
C: frontera offline y pruebas desechables. D: diseño de fallos y separación de niveles de evidencia.
E: ingesta y readback reales. El gate estricto comprueba la estructura y los archivos vinculados.
Su rc0 no convierte los HOLD de producción en autorización operativa.

- [Recibo2544](../artifacts/autoresearch/stage2544a_ptp_colo_atomic_cutover_and_watchdog_receipt.json)
- [Recibo2545](../artifacts/autoresearch/stage2545a_panel2_guarida_22cpe_cutover_readiness_receipt.json)
- [Memoria2547](../artifacts/autoresearch/stage2547a_memorymaster_ingest_receipt.json)
- [Gate2549](../artifacts/verification/stage2549a_wave251_codex1_gate.json)
