<!-- doc-head: Wave272, rechazo nativo sin flash e ingesta real con límite de Kuma -->
Los CRC lógicos y del contenedor pasan; ambos checks nativos rechazan la firma con rc99.
Prometheus recibió una cohorte fresca; no hubo cutover ni push Kuma sin monitor identificado.
<!-- /doc-head -->
# Validación viva de PtP-Colo y observabilidad

Alcance autorizado: comprobar imágenes y publicarlas temporalmente en RAM,
sin flashear, reiniciar WiFi ni escribir MTD. El contrato de rendimiento
posterior al cutover no puede demostrarse dentro de esa restricción.

## Imágenes y CRC

Las imágenes Stage2520/2634 se preservaron byte a byte. La inspección
SquashFS encontró ausente el watchdog solicitado y detectó problemas
en las longitudes/CRC PART y en el trailer del contenedor.

El uImage lógico está repartido entre PARTkernel y PARTrootfs. Calcular su
CRC directamente sobre bytes contiguos del factory incluye cabeceras PART
intermedias y da un resultado incorrecto. Se concatenaron los payloads,
se aplicó `fix_uimage_crc.repair` al stream lógico y se reconstruyó el
contenedor con longitudes y CRC correctos.

Las dos candidatas aisladas verifican OPEN, PARTkernel, PARTrootfs y CRC
de cabecera/datos uImage. La extracción SquashFS independiente confirmó
`option freq 6035`, canal207 y el script de watchdog con soporte45s.
El watchdog queda en inspección, sin armar: ni la configuración ni la
presencia del archivo demuestran arranque o recuperación de un radio.

## Comprobación nativa, STA primero

Se fijaron las claves SSH desde una radiografía histórica y se verificaron
modelo LiteBeam5AC, sysid0xe7f9, airOSWA8.7.25, frecuencia6035 y rol.
El primer intento falló al abrir SFTP, sin subir archivos. La revisión
posterior usó SSH con creación exclusiva, handshake y lectura independiente
del archivo completo para comprobar SHA256.

| Radio | Comando ejecutado | Resultado |
| --- | --- | --- |
| STA .54 | fwupdate.real -c /tmp/candidate_test.bin | 99, Signature check failed |
| AP .62 | fwupdate.real -c /tmp/candidate_test.bin | 99, Signature check failed |

Se preservó el rechazo sin modificar la verificación de firmas. Se eliminó
el archivo propio en ambos equipos y se confirmó su ausencia. Los ocho
MD5 protegidos mtd0/1/4/5 antes/después coinciden entre sí y con Stage2538.
No se ejecutó ningún comando de flash ni cutover.

Los CRC válidos no convierten estas candidatas en firmware autenticado.
Las imágenes permanecen en HOLD para producción.

## Ingesta real y frescura

El textfile original Wave269 estaba vencido y quedó intacto. Se tomó una
cohorte nueva de Panel1 .84 y Panel3 .83 y se verificaron íntegramente las
filas SQL504–509: dos rondas, seis peers RF y contexto buddy/hops completo.
Hubo87/90 respuestas RF; no se afirma cero pérdida.

Se extendió únicamente el exportador propio9297 conservando las series
anteriores. Se reinició esa unidad para cargar código; Prometheus mantuvo
su proceso, configuración y job. El input nuevo se publicó sin reinicio.

Las consultas nativas de Prometheus confirmaron época fuente exacta,
`fresh=1` y seis peers calificados dentro del TTL90s. No se cambió la fecha
de las observaciones para hacerlas frescas. Después se verificó frescura0
y UNKNOWN_STALE. Los relojes del controlador y del host se distinguen.
La publicación es una captura, sin un nuevo sondeo periódico de radios.

KumaNAS respondió a las comprobaciones de acceso, pero las búsquedas de
monitores existentes no encontraron uno vinculado al alcance Site-Aware.
No se reutilizó un monitor WAN/backup ni se crearon tokens o monitores.
El push quedó pendiente de ID y ruta documentada de token apropiados.

## Contrato y cierre

| Meta pedida | Evidencia |
| --- | --- |
| uimage_crc_valid | true en ambas candidatas, sobre stream lógico |
| fwupdate_check_rc == 0 | no:99 en ambos radios |
| post_cutover_link_6035mhz_up | no ejecutado por SIN FLASH |
| rtt_p95_delta_pct <= -25% | no medido; no hay par comparable post-cutover |

El gate queda INCOMPLETE. Las pruebas locales verifican CRC, trazabilidad,
limpieza, rechazo y controles de frescura; no sustituyen aceptación nativa,
cutover o un push real. Se preservaron intentos y reparaciones acotadas.
El ledger se amplió con CRLF conservando sus bytes previos y MemoryMaster
registra los resultados con estos límites, sin promoción de campeón.

- [Recibo firmware](../artifacts/autoresearch/stage2664a_ptp_colo_live_fwupdate_check_receipt.json)
- [Recibo observabilidad](../artifacts/autoresearch/stage2665a_live_prometheus_kuma_wave269_ingest_receipt.json)
- [Gate](../artifacts/verification/stage2669a_wave272_codex1_gate.json)
