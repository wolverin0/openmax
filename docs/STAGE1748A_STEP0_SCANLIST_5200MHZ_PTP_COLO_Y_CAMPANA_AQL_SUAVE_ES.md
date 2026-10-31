<!-- doc-head: Wave118 staging RAM PtP-Colo y banco AQL suave -->
El staging prepara archivos privados; no activa Step-0, retune ni flash.
La imagen1668A permanece sin cambios y sin certificación de arranque o interop híbrida.
El rollback de candidatos RAM no constituye rollback del enlace RF.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage1748A: scan_list, propuesta5200MHz y AQL suave

## Alcance autorizado y resultado del staging

Se preparan propuestas en RAM para AP198.18.0.91 y STA198.18.0.92.
Step-0a propone conservar6035,5170,5200 y añadir5745,5825 al scan_list STA habilitado.
Step-0b propone5200MHz, allow_80211=1 y op_mode=0 en AP; no se activa ninguno de los pasos.
El controlador1698A solo implementa dry-run: --execute aborta antes de conectarse.
Su antiguo objetivo5755MHz no sustituye la propuesta5200MHz de esta wave.
La prosa1700A sobre ausencia de hashes AP quedó desactualizada: los recibos actuales contienen ambos hosts.
Las precondiciones de hashes requieren observación fresca; un hash histórico no demuestra estado actual.

CONFIRMED: ambos hosts completaron staging, lectura de vuelta y sintaxis nativa del helper y rollback preparado.
La STA conserva la copia RAM del factory con6947480 bytes y el SHA exacto de la tabla siguiente.
Las copias originales coinciden con sus snapshots; SHA256 y longitud del archivo activo permanecieron iguales en ambos hosts.
Los guards de staging quedaron en inspección, nunca armados; no hubo activación, retune ni flash.
No se atribuye a archivos preparados una modificación del canal o la asociación de PtP-Colo.

## Factory exacto y aceptación separada

La fuente privada es el contenedor1668A OpenWrt24.10.4 LiteBeam5ACGen2, sin nueva mutación.

| Identidad | Valor |
|---|---|
| Tamaño | 6947480 bytes |
| SHA256 | `4cb8949265c5836003a2ea25500087a70795ff0249c33c81ad49dd3f3e35402b` |
| Formato | OPEN/PARTkernel/PARTrootfs/ENDS |
| CRC encabezado/kernel/rootfs | `12d8e382` / `f3c3d840` / `5315d814` |
| Destino de staging STA | `/tmp/stage1746a_colo_factory.bin` |

Contiene el healer ban_time1200, el hook4addr, watchdog de callback y LEDv4 ya extraídos y verificados.
El contenedor es unsigned: los CRC correctos no son firma criptográfica ni aceptación del bootloader.
La copia RAM no flashea, no prueba cold boot y no certifica la interop airOS/OpenWrt.

## Helper de staging y frontera del rollback

El helper stage1746a_colo_ram_staging_only_v2.sh inspecciona por defecto y exige --stage explícito.
Cada radio conserva su copia privada de /tmp/system.cfg dentro de /tmp/fmx-stage1746a/62 o54.
La carpeta es0700; original y candidatos son0600. No se imprimieron configuraciones ni secretos.
Los archivos step0a_system.cfg y step0b_system.cfg contienen propuestas, separadas del archivo activo.
Una comparación AWK del archivo completo, incluidos los saltos finales, verifica que no cambió /tmp/system.cfg.
El comparador rechaza su delimitador SOH; el coordinador además debe comprobar SHA256 y longitudes reales.
Crear la carpeta por primera vez es obligatorio; no se sobreescribe silenciosamente un intento anterior.

rollback60_staging_only.sh queda preparado, no armado, e inspecciona por defecto.
Su modo explícito --arm-staging-only esperaría60s y restauraría solo los dos archivos de propuesta.
No restaura estado RF ni llama a un reload; no se presenta como guard operativo de enlace.
No se inventa un API airOS RAM de aplicación/restauración que1698A nunca implementó ni verificó.
cfgmtd y rc.softrestart save quedan fuera de esta operación de staging.
La activación sigue BLOCKED_UNVERIFIED_RF_RESTORE_API hasta validar el mecanismo y su readback.

Se preservaron dos fallos de comprobación de RAM: /tmp se resuelve a /var/tmp y requirió verificar su ruta física.
La primera llamada al helper original terminó127 por ausencia de cmp, antes de crear sus archivos.
La reparación1 del helper eliminó esa dependencia; el original quedó archivado con su SHA y el v2 usa otro nombre.
Esos intentos no se convierten retrospectivamente en ejecuciones exitosas.

## Banco .241/.242: AQL suave

El banco es independiente de las dos radios PtP-Colo y no habilita su migración.
Se completó un ABAB real de10s por ventana con TCP, IPTV3Mbps/1316B, VoIP64kbps/160B y100 ICMP64B desde.186.
B cambió solo aql_threshold a18000; conservó límites por AC, WMM, BQL, slot, coverage y tx_queue_len.
No hubo reload de red, cambio de firmware, reinicio LED ni escritura nft en esta campaña.

| Fase | TCP recibido Mbps | ICMP p95 ms | ICMP recibidos/100 | IPTV perdidos/2850 | VoIP perdidos/500 | fmx_loss |
|---|---:|---:|---:|---:|---:|---:|
| A1 | 6.563508 | 6.8260 | 85 | 0 | 0 | 0.450499 |
| B1 | 18.427446 | 5.4220 | 98 | 0 | 0 | 0.375405 |
| A2 | 17.043562 | 4.8940 | 93 | 0 | 0 | 0.357668 |
| B2 | 18.581188 | 5.1235 | 100 | 0 | 2 | 0.358174 |

La media TCP pasó de11.803535 a18.504317Mbps; la media del p95 por ventana pasó de5.8600 a5.27275ms.
Esas medias no constituyen un percentil agrupado ni garantizan cero pérdida.
Decisión discard: B1 perdió2% ICMP, B2 perdió0.4% VoIP y el segundo par no mejoró fmx_loss en>=0.005.
El fmx_loss medio B fue0.3667895; su mejora media no invalida los vetos prerregistrados.
LEDv4 mostró4/4 AUTO en40 muestras; esto no prueba continuidad entre muestras ni CPU/Sirq causalmente nulo.
Se verificaron ocho restauraciones autónomas; el readback final confirmó baseline y liberación de leases sin recuperación manual.
La adquisición completa no implica promoción del candidato ni aceptación de Step-0 en PtP-Colo.
Un PASS de pytest verifica el contrato y sus recibos; no convierte un candidato descartado en ganador.
Sin A/A y holdout disjunto no se declara certificación de producción.

## Evidencia disponible

[Construcción factory1668A](../artifacts/autoresearch/stage1668a_repacked_squashfs_bantime1200_colo_image_receipt.json).
[Precondición local de cinco pilares](../artifacts/autoresearch/stage1746a/prerequisite_1668_fivepillar_check.json).
[Controlador1698A de solo planificación](../tools/rollout/fmx_ptp_colo_and_guarida_panel3_staged_controller.py).
[Helper1746A v2](../tools/deploy/stage1746a_colo_ram_staging_only_v2.sh).
[Recibo final1746A de staging y SHA256 RAM](../artifacts/autoresearch/stage1746a_ptp_colo_5200mhz_staging_and_ram_sha256_receipt.json).
[Recibo final1747A del banco AQL suave](../artifacts/autoresearch/stage1747a_live_241_242_gentle_aql_txq_ab_receipt.json).
[Staging completado y lecturas de vuelta](../artifacts/autoresearch/stage1746a/completion/staging_execution.json).
[Análisis real1747A y decisión discard](../artifacts/autoresearch/stage1747a/campaign_analysis.json).
[Restauración final del banco](../artifacts/autoresearch/stage1747a/final_readback.json).
