<!-- doc-head: Wave128 scan_list Colo54 y banco AQL20000 -->
La aplicación selectiva y su inversa requieren prueba del estado runtime; editar system.cfg no basta.
rc.softrestart no se considera no disruptivo; los modos save/force/test tienen efectos fuera del alcance.
El banco AQL20000 es independiente de cualquier cambio de PtP-Colo o certificación de producción.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage1808A: apply/restore de scan_list y AQL20000

## Alcance y criterio de aceptación

La autorización se limita a STA198.18.0.92: añadir5745,5825 conservando6035,5170,5200.
Se exige operación RAM/runtime no disruptiva, guard independiente60s, supervisión de ping al peer y restauración exacta.
No incluye cfgmtd, flash, retune del AP, reinicio general de red ni desasociación deliberada.
Un archivo de configuración modificado y luego restaurado no demuestra apply/restore del driver.
Resultado1806A: BLOCKED_NONDISRUPTIVE_RUNTIME_INVERSE_UNVERIFIED; la prueba operacional no se ejecutó.
Se completó el diagnóstico de solo lectura: configuración sin cambios, cero escrituras activas, flash y retunes.
No se armó ni ejecutó rollback. La restauración original es NOT_APPLICABLE_NO_MUTATION, no una restauración ensayada.
Resultado1807A: adquisición ABAB completa y candidato discard; las dos conclusiones se mantienen separadas.

## Qué hace realmente rc.softrestart

La lectura nativa de rc.do.softrestart coincide con la fuente WA.v8.7.25 de2423 bytes:
`7912ef2489dddb38254a5644f08b1bad7ce547f4ade50ec609330eafbc8866f0`.
El wrapper lanza bgnd de forma asíncrona; su retorno no acredita finalización ni salud del enlace.

| Ruta | Efecto comprobado en el script | Implicación |
|---|---|---|
| force | rc_stop, wifi0 down, regeneración sysinit y rc_start | Puede interrumpir el enlace |
| test | ubntconf -p; diff.sh o fallback al reinicio general | No garantiza aplicación selectiva |
| save | compara configuración, reinicia y programa cfgmtd -w | Incluye escritura persistente |

También modifica parámetros VM/cache y puede actualizar archivos de board mediante halupdate.
El nombre soft o test no convierte estas rutas en una operación permitida por esta autorización.
No se ejecuta ninguna de ellas para sustituir una API selectiva sin validar.

## Interfaces runtime y límites de la evidencia

La tabla iwpriv nativa expone setchanlist8BEE y getchanlist8BED con un buffer de256 bytes.
También expone disable_chan019B y enable_chan019C; sus nombres no prueban atomicidad ni ausencia de efectos RF.
El getchanlist observado no proporciona una lista invertible: un resultado vacío no equivale a una lista válida restaurable.

El athchans vivo coincide byte/hash con el athbox WA.v8.7.25 analizado:202920 bytes y SHA:
`c1d37671cafe6c7651f03000fd7dae7755ed8717bde07df1aeffba3aaa9a99e0`.
La revisión estática de athchans distingue estas rutas:

| Ruta | Evidencia estática | Límite |
|---|---|---|
| -g | abre /proc/sys/net/INTERFAZ/chanlist en lectura y muestra sus bytes | Requiere identidad del binario vivo |
| frecuencias sin -g | invoca disable_chan0 y luego enable_chan por frecuencia | No demuestra adición atómica |

La opción -g se bifurca antes del setter: no se debe deducir que ejecutar el applet sin opciones sea de solo lectura.
El código getter está después de0x0040c9ac; el antiguo extent113A terminaba antes y no cubría esa rama completa.
La lectura proc nativa enumera237 frecuencias de4920 a6100MHz en pasos de5MHz, incluidos los tres canales actuales y los dos propuestos.
Esto no confirma que el scan_list configurado de tres canales se haya aplicado al driver.
Su significado como inventario soportado o máscara permitida permanece UNKNOWN hasta decodificarlo y validarlo.
El script generado radio.conf contiene athchans6035/5170/5200; su presencia no prueba ejecución ni estado runtime.
No se asume que la configuración textual y el conjunto habilitado del driver sean idénticos.
Sin lectura runtime verificable, inversa exacta y guard operativo, la prueba selectiva permanece bloqueada.

La RE acotada de umac identifica bits por canal, actualización de bitmap y callback indirecto posterior.
La lectura binaria nativa posterior confirma2356432 bytes y SHA660435ed… idéntico al módulo local analizado.
La secuencia reset-all seguida de habilitaciones no es atómica; el efecto RF del callback sigue UNKNOWN.
No se afirma que haya ocurrido una desasociación: el riesgo estático y un evento físico observado son evidencias distintas.

## Banco PowerBeam .241/.242

Se prerregistró un único A1/B1/A2/B2 real, con10s de TCP, IPTV3Mbps, VoIP64kbps y100 sondas ICMP por ventana.
B modifica solo aql_threshold a20000; conserva límites por AC, WMM, BQL, coverage, slot y tx_queue_len.
Se mantienen firmware y LEDv4, sin reload, reinicio LED, escritura nft ni flash.
El selector exige mejora fmx_loss>=0.005 en ambos pares, retención TCP>=95%, p95B<=8ms y cero pérdidas UDP/ICMP en B.
Las cuatro ventanas reales terminaron válidas, sin errores de adquisición y con restauración autónoma en ambos radios.

| Fase | TCP recibido Mbps | ICMP p95 ms | ICMP recibidos/100 | IPTV perdidos/2850 | VoIP perdidos/500 | fmx_loss |
|---|---:|---:|---:|---:|---:|---:|
| A1 | 5.651187 | 6.5835 | 58 | 0 | 0 | 0.452574 |
| B1 | 3.452051 | 6.2250 | 51 | 1 | 0 | 0.452822 |
| A2 | 6.151459 | 7.1050 | 51 | 9 | 2 | 0.461823 |
| B2 | 16.748069 | 4.1270 | 99 | 0 | 0 | 0.360546 |

La media TCP pasó de5.901323 a10.100060Mbps; la media del p95 por ventana pasó de6.84425 a5.17600ms.
Los percentiles usan respuestas recibidas: no representan los probes perdidos ni prueban cero pérdida.
El promedio no sustituye los pares: B1 empeoró fmx_loss y perdió49% ICMP y un paquete IPTV; B2 perdió1% ICMP.
La retención media y el objetivo p95 pasaron; mejora pareada y cero pérdida fallaron. Decisión discard, sin promoción.
El objetivo medio B fue0.406684 frente a0.4571985 en A; esa mejora media no elimina los vetos.
LEDv4 mostró4/4 AUTO en40 muestras; no se infiere continuidad entre muestras ni CPU/Sirq causalmente nulo.
Las ocho restauraciones del banco se verificaron; lectura final: baseline restaurado, leases liberados y sin recuperación manual.
Sin A/A y holdout independiente no se declara certificación de producción.

## Evidencia

[Script de reinicio nativo leído sin ejecutarlo](../artifacts/autoresearch/stage1806a/probe_do_softrestart.json).
[Tabla iwpriv nativa](../artifacts/autoresearch/stage1806a/probe_private_ioctl_list.json).
[Getter observado](../artifacts/autoresearch/stage1806a/probe_chanlist.json).
[Lectura proc real](../artifacts/autoresearch/stage1806a/probe_proc_chanlist.json).
[Auditoría acotada del mecanismo y sus identidades](../artifacts/autoresearch/stage1806a/source_mechanism_audit.json).
[Identidad nativa posterior de umac](../artifacts/autoresearch/stage1806a/final_umac_hash.json).
[Prerregistro del banco1807A](../artifacts/autoresearch/stage1807a/preregistration.json).
[Auditoría histórica113A de athbox](../artifacts/autoresearch/stage113a_athbox_15applets_plt_and_ioctl_audit.json).
[Recibo final1806A y bloqueo operativo](../artifacts/autoresearch/stage1806a_ptp_colo_54_live_scanlist_apply_restore_proof_receipt.json).
[Recibo final1807A y decisión discard](../artifacts/autoresearch/stage1807a_live_241_242_aql20000_zero_loss_abab_receipt.json).
[Análisis real de cuatro ventanas](../artifacts/autoresearch/stage1807a/campaign_analysis.json).
[Restauración final del banco](../artifacts/autoresearch/stage1807a/final_readback.json).
