<!-- doc-head: SUPERSEDED (W435, 31/10): the PtP-Colo precheck (HOLD 9/9, airOS at 6035 MHz) is historical; production Colo runs OpenWrt 24.10.4 at ch153 / 5765 MHz, link 450 m (operator 30/10). Wave 144 warmup, AQL 18000 y precheck PtP-Colo -->
El warmup se mide aparte y solo precede a A1; no prueba estado térmico o de colas constante durante todo el ABAB.
El precheck es de solo lectura y conserva la separación entre integridad de imagen y aceptación operacional.
Una ventana coordinada no constituye una transacción atómica ni certifica rollback RF o arranque híbrido.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 1904A: reverificación AQL y precheck de Colo

## Diseño y límites del warmup

El banco usa PowerBeam .241 AP y .242 STA con tráfico real desde .186.
El diseño fija un solo A1/B1/A2/B2, con A 12000 y B 18000; los límites por AC y otros parámetros capturados permanecen iguales.
Antes de A1 se ejecuta una carga TCP de unos 5 s, guardada y excluida de las métricas de las cuatro ventanas puntuadas.
Cada fase posterior tiene su propio guard real de 60 s y restaura el perfil original.
Esas restauraciones introducen intervalos ociosos: el warmup inicial no demuestra que todas las ventanas estén igualmente calientes.
No se atribuye a este diseño una eliminación causal del cold start de campañas anteriores.
Se conservan las pérdidas observadas aunque una media de latencia o capacidad mejore.
El warmup recibió 12582912 bytes TCP durante 5.018568 s; las diferencias OTA fueron 13533315 bytes AP y 13303641 bytes STA.
Los timestamps del coordinador sitúan el lanzamiento de las primeras tareas de A1 unos 2.16 s después de completed_utc del warmup.
Ese intervalo acredita orden de registros, no continuidad de tráfico ni un estado físico estable.

| Fase | TCP recibido Mbps | ICMP p95 ms | ICMP p99 ms | ICMP recibidos/100 | IPTV perdidos/2850 | VoIP perdidos/500 |
|---|---:|---:|---:|---:|---:|---:|
| A1 | 13.289380 | 5.7830 | 8.0568 | 95 | 2 | 1 |
| B1 | 18.517091 | 3.5070 | 49.3940 | 99 | 0 | 0 |
| A2 | 19.378992 | 3.2315 | 3.9897 | 100 | 0 | 0 |
| B2 | 18.221352 | 3.9630 | 26.6280 | 98 | 0 | 0 |

La media TCP pasó de 16.334186 a 18.369222 Mbps y la media del p95 por ventana de 4.50725 a 3.73500 ms.
Los percentiles describen respuestas recibidas; no representan los probes perdidos ni son percentiles agrupados.
El fmx_loss medio empeoró de 0.3712155 a 0.5447600: B conserva colas p99 de 49.394/26.628 ms y pérdida ICMP de 1%/2%.
P95 y capacidad pasaron; mejora pareada y cero pérdida fallaron. Decisión discard, sin promoción.
Las ocho restauraciones autónomas y el readback final verificaron el perfil original y leases liberados, sin recuperación manual.

## Precheck de imagen y configuración

El único destino SSH del precheck es STA 198.18.0.92; AP 198.18.0.91 recibe únicamente seis probes ICMP acotados.
La identidad esperada de STA es MAC 245A4CC043D6 y sysid 0xe7f9.
Se lee la identidad y configuración seleccionada antes y después, junto al hash y longitud del archivo activo completo.
Los bytes de system.cfg solo se procesan en memoria para hash/longitud; no se guardan ni se imprimen secretos.
El filtro de configuración publica solo frecuencia, ancho, país, scan_list y flags allow_80211/op_mode cuando existen.

| Imagen RAM esperada | Valor |
|---|---|
| Ruta STA | /tmp/stage1746a_colo_factory.bin |
| Bytes | 6947480 |
| SHA256 | `4cb8949265c5836003a2ea25500087a70795ff0249c33c81ad49dd3f3e35402b` |
| Formato | OPEN/PARTkernel/PARTrootfs/ENDS, unsigned |
| CRC encabezado/kernel/rootfs | `12d8e382` / `f3c3d840` / `5315d814` |

La validación local del parser usa ese factory real existente, sin reconstruirlo ni contactar radios.
La captura viva debe repetir lectura de los bytes completos y verificar sus hashes/longitudes antes y después.
El SHA se calcula en el coordinador sobre stdout binario nativo; no se confunde con una herramienta SHA ejecutada en airOS.
La comprobación de RAM resuelve /tmp a su ruta física y verifica el mount observado.
Dos lecturas coincidentes describen la observación; no bloquean el archivo ni garantizan estabilidad futura.
El precheck no sube archivos, modifica configuración, escanea, retunea, recarga red ni flashea.
La captura real terminó al primer intento: identidad STA exacta antes/después, imagen exacta y configuración activa sin cambios.
system.cfg tuvo 5436 bytes y SHA256 `5e0d7357782f3fb6458366cbb1f133944fceebce78fe5424cdf04e99b166536c` en ambas lecturas.
El filtro observó freq=0, chanbw=0, countrycode=511 y scan_list habilitado con 6035,5170,5200.
El RF observado fue 6035 MHz y el peer respondió 6/6 sin pérdida: los ceros de configuración representan selección automática, no RF de 0 MHz.
Solo se constató el país configurado; no se certifica aprobación regulatoria ni disponibilidad de otro canal.

## Una sola ventana coordinada: checklist, no ejecución atómica

La ventana reúne decisiones y checkpoints bajo un coordinador; dos hosts y un arranque de firmware no tienen semántica todo-o-nada.
Todos los pasos operativos quedan HOLD_NOT_EXECUTED. Validar esta lista puede pasar sin certificar el cutover.

| Orden | Requisito previo o checkpoint | Estado operacional |
|---|---|---|
| 0 | Congelar alcance, identidades y autorización de cada acción | Precheck únicamente |
| 1 | Backups/hash y recuperabilidad de mtd0/1/4/5 en ambos extremos | Requiere prueba fresca |
| 2 | Imagen exacta, rol STA y perfil de campo provisionado en privado | Hash no prueba arranque |
| 3 | Apply selectivo runtime de scan_list e inversa exacta | Bloqueado por 1806A |
| 4 | Guard independiente, deadline real y trigger por pérdida del peer | No armado en Colo |
| 5 | Step-0a: conservar canales actuales y añadir 5745/5825 | No ejecutado |
| 6 | Step-0b: AP 5200, allow_80211=1/op_mode=0 y lectura bilateral | No ejecutado |
| 7 | Step-1: conversión OTA de STA tras gates y autoridad explícita | No flash autorizado aquí |
| 8 | Tres capas WDS/4addr, tráfico bidireccional y recuperación independiente | Sin estado post-flash |

El bloqueo 1806A sigue vigente: el setter observado no es atómico y falta una inversa runtime no disruptiva validada.
Los modos test/force de softrestart pueden reiniciar servicios; save puede escribir configuración persistente.
Un timer RAM de 60 s muere al reiniciar. No protege flash ni arranque del nuevo SO por el solo hecho de estar preparado.
Step-1 requiere un mecanismo de recuperación que sobreviva al reinicio, probado independientemente, además de interop híbrida y backups.
La firma de fabricante, arranque, perfil provisionado, interop airOS/OpenWrt y rollback RF permanecen sin certificar.
No se sustituye esa prueba por restaurar únicamente un archivo staging.
PASS_READONLY_PRECHECK_OPERATIONAL_HOLD valida lectura y checklist; todos los estados de cutover siguen HOLD.
La ingestión 1905A aceptó el claim <memorymaster-id>, id 157707, como candidate; no es validación independiente.
No hay A/A ni holdout de esta reverificación; ningún PASS de pruebas locales elimina los vetos físicos.

## Evidencia disponible

[Parser contra el factory real local](../artifacts/autoresearch/stage1903a/local_factory_validation.json).
[Procedimiento de precheck y comandos de solo lectura](../tools/bench/run_stage1903a_ptp_colo_atomic_step0_step1_precheck.py).
[Bloqueo runtime e inversa 1806A](../artifacts/autoresearch/stage1806a_ptp_colo_54_live_scanlist_apply_restore_proof_receipt.json).
[Staging histórico 1746A](../artifacts/autoresearch/stage1746a_ptp_colo_5200mhz_staging_and_ram_sha256_receipt.json).
[Warmup real excluido del score](../artifacts/autoresearch/stage1902a/warmup.json).
[Análisis real del ABAB](../artifacts/autoresearch/stage1902a/campaign_analysis.json).
[Adquisición 1902A y decisión discard](../artifacts/autoresearch/stage1902a_live_241_242_warmup_isolated_aql18000_ab_receipt.json).
[Precheck 1903A de solo lectura](../artifacts/autoresearch/stage1903a_ptp_colo_atomic_step0_step1_precheck_receipt.json).
[Captura nativa antes/después](../artifacts/autoresearch/stage1903a/attempt1/capture_result.json).
[Ingestión real 1905A](../artifacts/autoresearch/stage1905a_wave144_memorymaster_ingest.json).
