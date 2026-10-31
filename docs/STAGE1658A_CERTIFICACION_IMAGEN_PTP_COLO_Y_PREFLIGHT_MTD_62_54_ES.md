<!-- doc-head: Wave103 SquashFS real, banco RAM y preflight PtP-Colo -->
Imagen reconstruida y extraída independientemente en WSL; aceptación de arranque separada.
Campaña PARTIAL: A1 medido; B1 sin medición válida; no se ejecutaron A2/B2.
Colo fue inspeccionado sin escrituras; interop híbrida UNKNOWN y sin autorización de migración.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage1658A: imagen PtP-Colo y preflight MTD

## Alcance y estado

CONFIRMED: construcción nativa de SquashFS y verificación de sus archivos extraídos.
CONFIRMED: preflight de solo lectura en 198.18.0.91 AP y 198.18.0.92 STA.
PARTIAL: la campaña RAM en PowerBeam .241/.242 se detuvo al agotar las reparaciones autorizadas.
CONFIRMED: ambos radios quedaron restaurados mediante recuperación independiente con lectura posterior.
Los callbacks fallidos conservan sus errores; no existe certificación del payload bajo carga.
No se ejecutó flash, migración WAN, cambio de frecuencia ni despliegue en PtP-Colo.

## Imagen real y procedencia

Base: OpenWrt24.10.4 para LiteBeam5ACGen2, kernel6.6.110; no se sustituyó mac80211 ni ath10k.
El constructor usó unsquashfs/mksquashfs nativos en WSL como root, sobre almacenamiento Linux.
Después de construir, una segunda extracción independiente verificó contenido, UID/GID y modos Unix.
Se preservaron1384 entradas de la base y /dev/console, carácter5:1, modo0600.
Se verificaron15 miembros:11 archivos de código/configuración, firmware, módulo y dos enlaces de arranque.

| Artefacto privado | Resultado |
|---|---|
| SquashFS real, xz | 4276224 bytes |
| SHA256 | `44fa6850eb1a71e2493f13975ed592492fb3d789a7c0f5278421e0944ee6a2d9` |
| CRC32 del archivo SquashFS | `1a0aad05` |
| Firmware incorporado sin nueva mutación | `a49160ff008390a34e43145bc56f6b8d047f8e02433aff20f965b6f2874ef52f` |
| nft_meta_bridge.ko incorporado | `a54904b6e22261ab84be5eb9c901e6aceb0c8a1eee8ff519a06d135febacc26f` |

El firmware coincide con el baseline existente del banco; el firmware stock de origen398e4380… es distinto.
Se copió el baseline autorizado byte por byte, conservando PB050/PB040 y sus cambios históricos.
El módulo nuevo declara dependencia nf_tables, presente en la imagen, y vermagic6.6.110/MIPS32_R2.
Los binarios permanecen privados bajo .git/wave103; el recibo público contiene hashes y metadatos.
El CRC32 de SquashFS identifica el archivo; no es el CRC del buffer de firmware del driver.

Este archivo es un payload SquashFS independiente, no un contenedor factory/sysupgrade listo para flashear.
No se ejecutó el arranque de esta imagen, su persistencia en frío ni su inicialización procd en hardware.

## Política incorporada y admisión

SweetSpot configura VO300/600us, BE1200/2400us, umbral AQL3000us y BQL eth0 limit_max16384.
La clasificación nft usa EF/CS6 y prioridad262, con ICMP aCS6; no fija direcciones ni puertos del benchmark.
VI/BK y los demás parámetros se conservan; el controlador del banco mantiene constantes sus valores.
La aplicación exige un guard independiente vivo y guarda un snapshot RAM para rollback con lectura posterior.

Tres capas WDS: admisión wds=1/rekey86400/max_inactivity60; hook exacto de verificación; healer periódico60s.
Se preservaron los bytes del hook/healer existente y del daemon LEDv4 SHA17c60861…; sus límites internos no desaparecen por empaquetarlos.
El watchdog nuevo requiere arm explícito, owner, callback SHA y sesión setsid; vence por uptime real60/120s.
Un callback que devuelve0 no reemplaza la comprobación independiente del estado restaurado.

La plantilla de producción queda disabled, sin credenciales ni rol inferido.
El arranque exige provisión explícita, valores UCI correctos y guard vivo antes de aplicar el perfil.
Los enlaces S96fmx-ptp-production y S97fmx-rssi-leds fueron comprobados dentro de la extracción real.
La existencia de esos enlaces prueba el cableado de inicio, no que procd ya haya ejecutado esta imagen.

## Campaña física y evidencia conservada

La secuencia quedó incompleta: A1 del intento2 medido y B1 del intento3 fallido sin tráfico; A2/B2 no ejecutados.
El intento1 se interrumpió antes del tráfico por un fallo del colector al exigir timers UCI opcionales en A.
Se conservaron el fallo y las dos restauraciones reales; no se convirtió ese intento en una ventana válida.
La reparación1 permite campos opcionales ausentes en A y mantiene obligatorios los timers configurados en B.
El A1 medido del intento2 se conserva, con tráfico real y dos restauraciones autónomas correctas.
El primer B1 de ese intento falló antes de medir: network.wireless.reload no existe en el ubus disponible.
El callback retiró tres binds RAM pero terminó253 al usar el mismo método no soportado.
Lecturas independientes de archivos, mounts y kernel confirmaron la recuperación del baseline; no se falsifica ese exit como0.
La reparación2 cambió solamente el transporte a network.reload y conservó A1 para reanudar la secuencia.
El último B1 falló por drift real de AQL antes del tráfico; no se ejecutaron los casos restantes.
La interferencia de un escritor heredado es INFERRED, no una causa demostrada por esta campaña.
Los dos callbacks reales60s del último B1 devolvieron1: umount de /usr/sbin informó Resource busy.
Los binds de wireless/hotplug se retiraron; quedó el bind RAM de /usr/sbin, con holder UNKNOWN.
La recuperación independiente verificó inode/root propios, detuvo LED y liberó solamente el bind RAM propio mediante lazy-unmount.
Luego ejecutó la recarga de red original y restauró el kernel original tras un período de quietud.
Las lecturas finales comprobaron archivos, mounts, política kernel y limpieza de procesos, módulo nft y leases propios en ambos radios.
No se relabelan los callbacks fallidos como restauraciones verificadas ni se inicia otro experimento.
La recuperación manual necesaria no convierte los dos callbacks con exit1 en un rollback autónomo exitoso.

| Dato real | A1: baseline, intento2 |
|---|---:|
| TCP recibido | 20.635185 Mbps |
| ICMP recibidos/enviados | 100/100 |
| ICMP p50 / p95 / p99 | 2.39 / 4.543 / 7.2683 ms |
| IPTV, pérdida en receptor | 0/2850 paquetes |
| VoIP, pérdida en receptor | 0/500 paquetes |

Solo existe una ventana de datos válida y ninguna ventana candidata válida.
B1 no produjo métricas; A2/B2 no se ejecutaron. No hay comparación pareada ni efecto candidato medido.
El recibo final conserva fmx_loss=null y mission_complete=false; p95 de A1 por sí solo no certifica B.
La prueba RAM de componentes equivalentes se distingue del arranque completo de la imagen.
Resultado: PARTIAL_FAILED_FULL_STACK_BENCH, sin promoción ni autorización de rollout.

## Preflight PtP-Colo y hashes MTD

Ambos equipos reportan LiteBeam5AC, sysid0xe7f9 y airOS WA.v8.7.25.
AP.62: MAC602232B08685; STA.54: MAC245A4CC043D6.
AP informa6035MHz/20MHz y WDS habilitado; la STA conserva frecuencia/ancho0 en su configuración dinámica.
Esos ceros no son prueba de un canal físico0MHz ni de un ancho efectivo0MHz.
allow_80211 y op_mode permanecen UNKNOWN; no existe prueba de interop híbrida aceptada.

Los hashes se calcularon en el controlador sobre dos lecturas SSH de los bytes reales de cada partición.
No se imprimieron credenciales ni se publicaron binarios MTD.

| Equipo | Partición | Bytes | SHA256 |
|---|---|---:|---|
| .62 | mtd0 u-boot | 262144 | `988de5143235db3c0afc810b3bbad0b9177e96ec8493b4873486eb626d80ebfc` |
| .62 | mtd1 u-boot-env | 65536 | `63213a0bb3ec161faa51abf53417dcab7325b529c12150073923c6ab42cf711f` |
| .62 | mtd4 cfg | 262144 | `000271d481d9b8cd0a5bae65ee518be96baec26de192161da7eeb7faae6913aa` |
| .62 | mtd5 EEPROM | 65536 | `e68ff8a3f3267e71f25f9f3385cb3d59fb0aaab97c821c49771f391cb990d002` |
| .54 | mtd0 u-boot | 262144 | `988de5143235db3c0afc810b3bbad0b9177e96ec8493b4873486eb626d80ebfc` |
| .54 | mtd1 u-boot-env | 65536 | `63213a0bb3ec161faa51abf53417dcab7325b529c12150073923c6ab42cf711f` |
| .54 | mtd4 cfg | 262144 | `dd76989b6b4f76f2e927a21ad9a6ab095e58698f6fa9ddabc0e50728579161e9` |
| .54 | mtd5 EEPROM | 65536 | `f1443af7afd04f9788cc79906e59a1f4ab0e75e9e9d5454a03f62ee095e4fb34` |

Las lecturas/hash no equivalen a una restauración ensayada ni a un respaldo externo verificado.
La herramienta SHA nativa inicial no estaba disponible; se retuvo ese fallo y la reparación por doble lectura real.
No se modificaron mtd0/1/4/5, calibración, MAC, configuración del core ni reglas WAN.
El gate de interop y la aprobación de corte siguen pendientes: híbrido UNKNOWN implica no migrar.

## Recibos

[Construcción y extracción independiente](../artifacts/autoresearch/stage1656a_image_build/build_receipt.json).
[Preflight vivo y hashes MTD](../artifacts/autoresearch/stage1657a_live_ptp_colo_62_54_preflight_and_mtd_hashes_receipt.json).
[Campaña1656A final y fallos preservados](../artifacts/autoresearch/stage1656a_ptp_colo_image_and_bench_certification_receipt.json).
[Lectura final: baseline restaurado y leases liberados](../artifacts/autoresearch/stage1656a/final_readback.json).
[Recuperación independiente de B1](../artifacts/autoresearch/stage1656a/final_B1_independent_baseline_recovery.json).
La construcción y el preflight pueden aprobar independientemente; no reemplazan la campaña ABAB incompleta.
Este informe no atribuye una ejecución de pytest ni un PASS del gate1661A sin su recibo posterior.
