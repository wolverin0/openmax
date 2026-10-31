<!-- doc-head: Wave105 imagen factory real, banco A/B y plan de canal PtP-Colo -->
Contenedor factory reconstruido y extraído con herramientas nativas; aceptación de arranque separada.
PtP-Colo inspeccionado sin escrituras, scans ni retunes; los candidatos no pertenecen al scan_list STA actual.
ABAB real completo con decisión discard; ninguna medición sustituye la interop híbrida pendiente.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage1670A: imagen ban_time1200 y plan PtP-Colo

## Imagen construida y verificada

CONFIRMED: se reconstruyó un contenedor factory completo desde OpenWrt24.10.4 para LiteBeam5ACGen2.
Se reutilizó el constructor SquashFS1656A, con mksquashfs/unsquashfs nativos en WSL.
Una extracción independiente del factory final comprobó15 miembros y sus modos Unix, UID/GID y bytes.
Los scripts son0755, las configuraciones0644 y los enlaces de inicio conservan sus destinos.
El kernel y el encabezado anteriores a rootfs permanecen idénticos; se preservaron1384 entradas de la base.

| Identidad del factory privado | Valor |
|---|---|
| Tamaño | 6947480 bytes |
| SHA256 | `4cb8949265c5836003a2ea25500087a70795ff0249c33c81ad49dd3f3e35402b` |
| CRC32 del archivo completo | `f4393a37` |
| fw_magic / trailer | `OPEN` / `ENDS` |
| CRC encabezado / kernel / rootfs | `12d8e382` / `f3c3d840` / `5315d814` |

Los tres CRC almacenados coinciden con sus cálculos independientes sobre el archivo real.
El formato es OPEN/PARTkernel/PARTrootfs/ENDS sin firma criptográfica de fabricante verificada.
CRC correcto prueba integridad estructural; no prueba aceptación del bootloader ni autorización de flash.
La cadena WA heredada del encabezado no cambia la procedencia OpenWrt24.10.4 de la imagen.

## Contenido y límites del payload

El healer común actual se incorpora byte por byte con ban_time1200, junto al hook99-fmx-4addr-verify.
Se conserva el watchdog de callback explícito, owner y SHA, con expiración monotónica60/120s.
Se conserva LEDv4, la política SweetSpot y la plantilla deshabilitada sin credenciales.
SweetSpot establece VO300/600us, BE1200/2400us, umbral3000us y BQLmax16384.
La clasificación EF/CS6 usa prioridad262; la política de producción no fija hosts del benchmark.
Firmware y módulo nft se mantienen privados; no se generó otra mutación de firmware.
Los binarios están bajo.git; el recibo público registra identidades y extracción sin publicar rootfs propietario.

UNKNOWN: arranque, persistencia en frío, provisión completa e interoperabilidad híbrida airOS/OpenWrt.
No se flasheó ningún radio ni se desplegó esta imagen en PtP-Colo.
Los enlaces procd comprobados dentro de la imagen no equivalen a ejecución de arranque en hardware.
Se mantienen los límites best-effort del hook/healer existente; empaquetarlos no los convierte en fail-closed.

## PtP-Colo: lectura real y bloqueo de Step-0

Los dos radios son LiteBeam5AC, sysid0xe7f9, airOS WA.v8.7.25.
Las lecturas SSH de estado/configuración y opciones del driver no realizaron escrituras, scans ni retunes.

| Equipo | Configuración observada | scan_list exacto | RF actual |
|---|---|---|---|
| 198.18.0.91 AP | 6035MHz, 20MHz, country511 | disabled | 6035MHz |
| 198.18.0.92 STA | freq0/chanbw0, AUTO, country511 | enabled:6035,5170,5200 | 6035MHz |

Los ceros de la STA describen selección dinámica; no significan una portadora o ancho físico de0MHz.
Las frecuencias enumeradas por el driver bajo el perfil actual no son certificación regulatoria.
No se interpreta country511 como aceptación de un país estándar ni como autorización de operar otro canal.

| Candidato de planificación | Frecuencia | Presente en scan_list STA actual |
|---|---:|---|
| ch149 | 5745MHz | No |
| ch165 | 5825MHz | No |
| ch56 | 5280MHz | No |

Step-0 permanece bloqueado: un cambio solo en AP podría dejar a la STA fuera de su lista permitida.
La evaluación futura requiere compatibilidad bilateral, interferencia medida, restricciones regulatorias y rollback admitido.
No se seleccionó un candidato, no se amplió scan_list y no se realizó retune.
La interoperabilidad híbrida sigue UNKNOWN; el plan de canal no concede autorización de migración.

## Banco físico .241/.242

El plan congelado limita la campaña a una secuencia A1/B1/A2/B2, con10s de tráfico por ventana.
El origen es198.18.0.62: TCP, IPTV3Mbps/1316B, VoIP64kbps/160B y100 sondas ICMP64B.
A usa la política kernel original fresca sin tabla WMM propia; B aplica directamente el SweetSpot descrito.
Se mantienen LEDv4 y firmware, sin recargar red, reiniciar LED ni modificar flash.
Cada fase exige guards reales60s y lectura de restauración independiente en ambos radios.
La selección exige mejora fmx_loss>=0.005 en ambos pares, retención TCP media>=95%, p95B<=8ms y cero pérdida.
La secuencia real terminó completa, sin reparaciones ni repetición de ventanas para obtener un resultado verde.

| Ventana | TCP recibido Mbps | ICMP p95 ms | ICMP recibidos/100 | IPTV perdidos/2850 | VoIP perdidos/500 | fmx_loss |
|---|---:|---:|---:|---:|---:|---:|
| A1 | 15.391826 | 9.910 | 100 | 0 | 0 | 0.913009 |
| B1 | 14.041184 | 11.955 | 92 | 0 | 2 | 0.578648 |
| A2 | 17.143088 | 9.070 | 96 | 0 | 0 | 0.443140 |
| B2 | 6.174881 | 8.939 | 63 | 2 | 1 | 0.706464 |

La media TCP pasó de16.267457 a10.108032Mbps: retención62.1365%, inferior al mínimo95%.
La media de p95 por ventana pasó de9.490 a10.447ms; no es un percentil agrupado de todas las sondas.
El fmx_loss medio de B fue0.642556, pero el segundo par empeoró y fallaron los cuatro criterios de selección.
Decisión discard: sin promoción; ni la media del objetivo ni los LEDs encendidos anulan las pérdidas de tráfico.

| Ventana | Sirq AP % | Sirq STA % |
|---|---:|---:|
| A1 | 8.969 | 22.470 |
| B1 | 12.135 | 32.465 |
| A2 | 15.778 | 29.545 |
| B2 | 10.811 | 17.745 |

LEDv4 permaneció AUTO con4/4 barras en las40 muestras observadas:5 por radio en cada ventana.
Esto confirma las muestras, no continuidad entre muestras ni un efecto causal aislado sobre CPU/Sirq.
La lectura final confirmó baseline restaurado y leases liberados, sin recuperación manual.
Se verificaron las ocho restauraciones autónomas, una por radio y fase; las cuatro ventanas quedaron sin errores de adquisición.
PASS_BOUNDED_LIVE_ACQUISITION acredita la adquisición completa; la decisión del candidato sigue siendo discard.
Solo se ejecutó un ABAB exploratorio: faltan A/A y holdout independiente para certificar rendimiento.
Esta campaña kernel/WMM no constituye una prueba del arranque de la imagen ni del efecto aislado de ban_time1200.

## Evidencia

[Factory y extracción nativa1668A](../artifacts/autoresearch/stage1668a_repacked_squashfs_bantime1200_colo_image_receipt.json).
[Recibo final1669A y límites de los cinco pilares](../artifacts/autoresearch/stage1669a_live_ptp_colo_step0_channel_plan_and_241_242_ab_receipt.json).
[Prerregistro del banco1669A](../artifacts/autoresearch/stage1669a/preregistration.json).
[Auditoría Colo de solo lectura](../artifacts/autoresearch/stage1669a/colo_readonly_audit.json).
[scan_list AP exacto](../artifacts/autoresearch/stage1669a/colo_62_scanlist_exact_readback.json).
[scan_list STA exacto](../artifacts/autoresearch/stage1669a/colo_54_scanlist_exact_readback.json).
[Análisis de las cuatro ventanas y decisión discard](../artifacts/autoresearch/stage1669a/campaign_analysis.json).
[Estado final restaurado](../artifacts/autoresearch/stage1669a/final_readback.json).
