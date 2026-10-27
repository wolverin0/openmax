<!-- doc-head: STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG.md continuation 1 of 3; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG.md) | Part 1/3
<a id="umac-xc8725"></a> [UMAC XC8.7.25](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_002.md#umac-xc8725) | <a id="uph-wa8725-y-xc8725"></a> [UPH WA8.7.25 y XC8.7.25](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_002.md#uph-wa8725-y-xc8725) | <a id="wextioctl-xc8725"></a> [WEXT/ioctl XC8.7.25](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_003.md#wextioctl-xc8725) | <a id="atributos-ltu-ap-y-cpe242"></a> [Atributos LTU AP y CPE2.4.2](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_003.md#atributos-ltu-ap-y-cpe242) | <a id="wavea-tablas-exactas-wa8725-resueltas"></a> [WaveA: tablas exactas WA8.7.25 resueltas](STAGE12_AUTORESEARCH_FIRMWARE_KNOB_CATALOG_CONTINUATION_440b29f9c1_003.md#wavea-tablas-exactas-wa8725-resueltas)

<!-- stage822a-payload-begin -->

Static local audit plus WaveA:571 disabled entries,42 sources and exact WA UMAC identity resolved.
Encoding ranges and dated attempts are not physically validated safe RAM ranges.
No SSH, network/device access, target execution or changes to the concurrent live loop.
CT3/4/6/9/11/13 and raw PHY/power/reset/regulatory controls remain excluded.


# Stage12 — catálogo offline de controles de firmware

Fecha: 2026-10-24. Resultado: **CONFIRMED** para las interfaces y semánticas de host indicadas; **UNKNOWN** para seguridad física, efecto aplicado y rollback no verificables. No se acepta ninguna mejora inalámbrica mediante esta auditoría.

El catálogo [firmware_knob_candidates.json](../orchestration/autoresearch/firmware_knob_candidates.json) contiene571 entradas informativas con42 fuentes SHA256 y localizador por símbolo/línea/offset, boundary, dominio de entrada, hipótesis física y condición de restauración. WaveA amplía las248 iniciales: resuelve su placeholder WA UMAC y añade15 parámetros y309 registros WEXT propios de WA (290 nombrados y19 dispatchers anónimos), sin colapsar aliases por nombre. Todas llevan `enabled=false`, `approved_range=null`, `qualification=UNQUALIFIED` y `rollback.verified=false`. La raíz impone `automatic_execution_allowed=false`, `actuation=none`, `mode=static_offline_disabled`. No contiene comandos ejecutables ni se conecta al loop activo.

El [esquema local](../orchestration/autoresearch/firmware_knob_candidates.schema.json) y los [tests offline](../tests/test_firmware_knob_candidates.py) comprueban estructura, referencias, hashes, finitud, unidades y cotas. Son validación de metadatos; no prueban que el firmware acepte o ejecute un valor.

## Alcance y procedencia

Esta tarea es el entregable estático de control-authority de Stage12, registrado en `BENCH_PLAN.md`. Otro agente posee el banco LAP120–Loco195. Aquí sólo se leyeron archivos locales y binarios como datos; no se ejecutaron scripts/binarios del firmware, helpers de banco, SSH, consultas web/MCP, cargas ni control de procesos del otro agente. El generador local de metadatos sólo usa `pathlib`, `json`, `hashlib` y `re`.

Los tres archivos solicitados se leyeron y se congelaron por bytes en [inputs](../artifacts/autoresearch/firmware_knob_audit_20261024/inputs/), junto con una copia textual del helper que explica sus métricas. El [manifiesto](../artifacts/autoresearch/firmware_knob_audit_20261024/input_snapshots.json) conserva ruta original, tamaño y hash. Los originales pueden cambiar legítimamente por trabajo concurrente; los tests ligan esta auditoría a las copias, sin imponerles una reversión.

| Fuente | Identidad y alcance | Límite |
| --- | --- | --- |
| ath10k-ct retenido | `tools/research/srccache/ath10k-ct/ath10k-7.2`; SHA/líneas por archivo en el JSON | `7.2` es la rama del host. No prueba identidad del módulo corriendo ni del handler firmware CT022. |
| WMI QCA10.1 | `wmi.c:10680..10688` selecciona `wmi_10_1_ops` y mapas `wmi_10x_{pdev,vdev}_param_map` | IDs no transferibles a 10.2.4, 10.4 o TLV. |
| mac80211 retenido | `tx.c`, `sta_info.c`, `mac80211.h`; estimador ath10k en `mac.c` | Parser debugfs exacto no retenido en ese subconjunto; dominio completo desconocido. |
| XC8.7.25 | `umac.ko` `ec1df9e6…`, `ubnt_poll_host.ko` `d327c4c8…`, `ath_dev.ko`; kernel2.6.32.68 | Tablas y disassembly estáticos, sin efecto físico ni estado actual. |
| WA8.7.25 | UPH `bfc3f499…`, reextraído del contenedor exacto; coincide con el recibo histórico de Loco195 |34 nodos confirmados de nuevo; semántica previa ligada por igualdad de bytes. No equivalencia global WA/XC. |
| WA UMAC | **CONFIRMED** `660435ed9c50f1390945535a975565d7234543e01933644bf99dd9deca1b2cd6`,2356432 B; header `WA.ar934x.v8.7.25.48568.260730.1010` | WaveA resuelve la identidad antes UNKNOWN.15 parámetros y309 WEXT en este módulo exacto; efecto/rollback físicos siguen UNKNOWN. La extracción antigua `46525d…` no se sustituye. |
| LTU2.4.2 AP/CPE | `aflturocket_2.4.2` y `afltu_2.4.2`, `ame_dev.ko`, `ame_core.ko`, `ame_adj.sh` | Hashes/offsets separados por build. LTU no utiliza aquí el boundary QCA10.1. |

Los informes de análisis [CT/mac80211](../artifacts/autoresearch/firmware_knob_audit_20261024/ct_mac80211_findings.json) y [WA/XC/LTU](../artifacts/autoresearch/firmware_knob_audit_20261024/wa_xc_ltu_findings.json) conservan los offsets, hashes completos, anotaciones de handlers y fallos locales del análisis. No es un inventario exhaustivo del firmware cerrado: lo no demostrado permanece `UNKNOWN`.

La ampliación actual usa [hechos WA WaveA](../artifacts/autoresearch/waves_abcd_20261024/wave_a_wa/facts_final.json), [receta de expansión](../artifacts/autoresearch/waves_abcd_20261024/expand_wave_a_catalog.py) y [WA/LTU RE](STAGE12_WA_UMAC_AND_LTU_STATE_MACHINE_RE.md). El generador de la auditoría inicial bajo `firmware_knob_audit_20261024` reproduce sólo su snapshot histórico248; para el catálogo571 se usa la receta WaveA sobre esa copia congelada. Los tests ahora verifican ambos bindings sin volver a marcar UNKNOWN la identidad resuelta.

## Cómo interpretar una cota

`encoding_domain` describe el parser, wire type, máscara, tabla de valores o un subconjunto de valores intentados, según su `note`. Un `u32` no implica que todos sus valores tengan semántica válida; un buffer de64 B no implica16 campos seguros. En AQL/FQ se enumeran puntos del recibo porque falta el parser exacto. No se interpolan.

`ram_safety.proposal` sólo contiene puntos de caracterización AQL ya presentes en la receta congelada. Tampoco autoriza aplicarlos. El resto es `null`. `observed_values` significa valores reportados/intentos del artefacto fechado, sin transformar una etiqueta `keep` en prueba física. **No hay ningún rango seguro validado en RAM**: aun un transporte volátil puede alterar RF, desasociar equipos o carecer de restauración verificable.

`research_candidate` significa hipótesis para una eventual caracterización separada; `characterization_only`, semántica o readback pendientes; `observation_only`, evidencia de consulta/caché; `excluded`, fuera de candidatos. Ninguna clasificación habilita ejecución. `confidence=CONFIRMED` califica presencia/código de host, nunca ganancia o seguridad.

## Lectura del autoresearch suministrado

La copia de `lap120_loco195_live_autoresearch_20261024.json` tiene timestamp `2026-10-24T05:16:59.566891+00:00`, SHA256 `46feb1adea27bf56557250d9d54eba3ea6243ffbdd663357bcc40278818eb016`, ocho iteraciones y dos repeticiones por iteración. Reporta un incumbent `iter6_ct_rc_per_28` con AQL1000/2000 µs, threshold4000, PER28, RIFS0 y pérdida objetivo0.268996; G66.15 Mbps, p95 9.588 ms y p99 9.727 ms. **Son resultados declarados en esa copia**, no una repetición ni aceptación de este trabajo.

Hay cuatro límites concretos en el helper textual congelado:

- `ct_special` suprime errores con `|| true`; su lectura sólo muestra ayuda. No demuestra valor aplicado ni restaurado por el firmware.
- `restoration_verified=True` se asigna en la construcción de la observación. El readback final muestra AQL/FQ/HTT, sin getter real para CT. No valida por sí mismo el contrato de restauración para CT.
- Sólo hay seis RTT por iteración en el artefacto. Un p99 calculado con esa muestra no caracteriza una cola de latencia estable.
- `retry_rate` es retransmisiones TCP divididas por500 y limitado a1; no es PER/reintentos MAC. Jain1.0 se fija en la observación de un enlace. No son evidencia de fairness PtMP ni PER físico.

La política congelada tiene campos AQL llamados `*_kb`, pero el helper asigna µs sin conversión. Además escribe las cuatro AC y la política representa sólo el límite alto/threshold: no incluye el bajo, FQ, HTT ni los campos CT7/10. Sus cotas512..65536 son validación de política, no aprobación física. Queda documentado el gap; `PROGRAM.md`, evaluador, helper, TSV, configuración y experimento vivo no se editaron ni ejecutaron por esta tarea.

## mac80211, ath10k y HTT

| Control | Boundary | Dominio documentado | Hipótesis y límite de rollback |
| --- | --- | --- | --- |
| AQL low/high | mac80211 | µs; pares intentados1000/2000,2000/4000,5000/12000 por AC | Limitar airtime pendiente puede bajar cola y también privar agregación. Capturar/restaurar las cuatro AC y threshold; getter host no revela cola firmware. |
| AQL threshold | mac80211 | µs; puntos4000,8000,24000 | Cambia la admisión de airtime agregado. No usar unidades KB ni extrapolar rango seguro. |
| FQ quantum | mac80211 | bytes; puntos300,1514 | Cambia servicio por turno, eficiencia/fairness. Restaurar valor original y estado de colas; parser exacto pendiente. |
| HTT aggr size | ath10k-ct → QCA FW | AMSDU1..31 y AMPDU1..64 tras conversión a `u8`; intentos2/48,3/32,3/64 | Tamaño/agregación puede cambiar airtime y latencia. Rechazar overflow antes de convertir: un `u32` grande puede truncarse a un `u8` válido. Getter sólo sombra host; no tamaño de agregado medido ni ACK firmware. |
| RTS threshold | QCA10.1 FW | Política64..2347 bytes; sentinela off depende de API | Colisiones frente a overhead. Preservar sentinela y estado original; un campo aceptado no prueba retry/RTS por trama. |
| Coverage class | ath10k-ct → hardware | Política0..31; incremento3 µs/unidad; `-1` es reutilización interna | Ajusta slot/ACK/CTS con reloj PHY y saturación. No equivale a `distance` propietario; restaurar registros/config exactos, sin acceso MMIO aquí. |
| VHT MCS mask | QCA10.1 FW | Índices0..9; requiere NSS/GI/width/peer completos | Tasa, margen y retries pueden cambiar en sentidos opuestos. Un MCS máximo escalar no representa máscara válida/restaurable. |
| `set_rates` | ath10k-ct | Broadcast/multicast/beacon | No es control de MCS unicast. Restauración requiere capturar todos los valores originales. |
| `set_rate_override` | ath10k-ct | Wave2 completo; Wave1 parcial | No atribuir capacidades Wave2 a QCA988x. Potencia/TPC excluidos; faltan efecto exacto y getter fiable. |
| CoDel target/interval, CAKE bandwidth | Linux qdisc, metadata de política |1..50 ms,10..500 ms,1..1000 Mbps en el validador congelado | Falta probar aplicador, qdisc y ubicación del path. No son perillas ocultas del firmware ni actuadores confirmados. |

El AQL de estas fuentes usa airtime **estimado**: ath10k se apoya en último bitrate y fallback6 Mbps salvo un servicio firmware compatible. Su getter no mide airtime real ni demuestra profundidad de colas inferiores.

## `ct_special` IDs3..16

La interfaz parsea un `u64` con selector en high32 y valor en low32. El host mantiene sombras, puede actualizarlas antes de enviar y, si el estado no es `ON`, puede devolver longitud sin enviar. `read_ct_special` imprime ayuda constante. La fuente advierte riesgo out-of-spec/daño: no se ofrecen recetas ni una whitelist de ejecución.

Para todo CT, la condición de rollback es rechazar al faltar estado previo exacto y restauración verificable, o ante error, caída de estación, reset, pérdida/p99 fuera del gate. En esta evidencia no existe getter real del firmware para restaurar ese preestado; reiniciar/recargar no se declara un rollback demostrado.

| ID | Nombre | Dominio de fuente, no rango seguro | Hipótesis / disposición |
| --- | --- | --- | --- |
|3|THRESH62_EXT|Campo PHY8bit; host acepta u32|Umbral CCA/PHY: **EXCLUDED**.|
|4|NOISE_FLR_THRESH|Band/type/value empaquetados; validaciones parciales|CCA/noise floor y out-of-spec: **EXCLUDED**.|
|5|IBSS_AMSDU_OK|Documentado0/1; host coerciona booleano|A-MSDU en IBSS; no habilita infraestructura. Caracterización pendiente.|
|6|MAX_TXPOWER|Ayuda0..65535 half-dBm; latch una vez|Potencia/estado no reversible: **EXCLUDED**.|
|7|RC_MAX_PER_THR|Ayuda0..256/default50; utilidad>100 incierta|Umbral de adaptación de tasa.28/50 son intentos reportados. No normalizar a porcentaje seguro; máscara `0xff` del helper convierte256→0.|
|8|STA_TXBW_MASK|Flags1/2/4 para20/40/80 MHz; default0|Restringir anchos por estación; OR/semántica exacta pendientes.|
|9|PDEV_XRETRY_TH|DocumentadoU16; default10.1=0x40|Umbral de retries que puede resetear PHY: **EXCLUDED**.|
|10|RIFS_ENABLE|Documentado0/1; default0|Interframe spacing/eficiencia frente a interoperabilidad. RIFS1 fue discard en la copia; efecto/restore FW sin verificar.|
|11|WMI_WD|0 en writer significa no-set; `0xffffffff` envía0/deshabilita|Watchdog; semántica de sentinela difiere de ayuda: **EXCLUDED**.|
|12|PSHACK|Bits0/1: ignorar PS y multicast buffered|Power-save/multicast; no prueba beneficio ni seguridad.|
|13|CSI|0/nonzero; header explícito10.4-only|**EXCLUDED** en QCA10.1. Presencia del selector no prueba CSI aquí.|
|14|BW_DISABLE_MASK|Bits0..3 deshabilitan20/40/80/160 MHz|Se aplica en próxima configuración de rates. Bit160 no crea capacidad PHY160 en QCA988x.|
|15|TXBF_CV_MSG|Documentado0/1/default0|Mensajes beamforming; soporte exacto depende de HW/FW.|
|16|RX_ALL_MGT|Documentado0/1/default0|Más management recibido puede mejorar observabilidad con coste CPU; efecto pendiente.|

## WMI pdev/vdev10.1

Se enumeraron **todos los miembros no `UNSUPPORTED` de los mapas10x seleccionados por10.1**:42 pdev y45 vdev. Esto cubre el mapa retenido, no todo mensaje privado de firmware ni todos sus handlers. El valor wire es `u32`; el rango semántico seguro es desconocido, sin propuesta de inyección numérica. Un ID mapeado puede carecer de aplicador soportado: fragmentation tiene ruta que devuelve `EOPNOTSUPP`.

Hipótesis: retry/kickout cambia entrega y estabilidad; agregación/burst cambia eficiencia frente a latencia/fairness; protección cambia overhead/colisiones; rate/SGI/LDPC/STBC/NSS cambia tasa y margen; stats cambia coste/cadencia de telemetría. El JSON particulariza estas hipótesis por entrada. Potencia, cadenas, calibración, resets, ANI/CCA, DCS y cambios de protección de seguridad quedan excluidos. Ningún raw WMI está autorizado; sin getter de firmware previo y ACK de aplicación no hay rollback calificado.

## WA/XC: sysctl, módulos e ioctls

El inventario conserva49 nodos XC:15 parámetros UMAC y34 UPH. En WA WaveA confirma15 parámetros UMAC,309 registros WEXT y34 UPH directamente en módulos extraídos del contenedor exacto. No se trasladan offsets XC: cada nuevo descriptor WA conserva su propio offset, selector, tipo y conteo; chwidth70 y122 siguen siendo identidades distintas. Las cotas int32/uint32 son de almacenamiento/parser, no autorización de toda configuración dentro de ellas.

Los UMAC son variables de módulo (`param_set_int` o `param_set_uint`), no control de firmware por trama demostrado. Incluso con modo0644, pueden consumirse sólo al cargar/inicializar. No se recargan módulos ni se propone rango. UPH usa buffers compartidos/caché y ramas de WRITE que despachan acciones. `get_reg`, `get_diag`, `get_host_diag` y `hsr_diag` leídos no hacen las consultas que su nombre podría sugerir. Una consulta real vía escritura no es una lectura pasiva. Ceros no demuestran AirPrism desactivado.

Excepción relevante: READ de `netconf` sí envía la consulta nativa0x22. No se identificó setter RF/config en su rama host, pero el consumidor firmware no está trazado; no se presume pasividad universal de `/proc`.

`radio.conf` aporta ejemplos, no cotas: ATPC tiene5campos, fixed_frame10; noack literal0 y scratch1 no establecen el modo real. Los29 descriptores WEXT seleccionados más `wifi0 distance` son interfaces host con conteos/tipos, sin prueba de aplicación por trama. El campo `ff` de `iwpriv` no equivale a UPH `fixed_frame`.

El rollback exige capturar el estado efectivo completo, incluidos campos acoplados y origen del getter. Una caché compartida no permite reconstruirlo; quedan sin propuesta. Registros/diagnósticos activos, reset GPS, alta de radio, ATPC/potencia y debug invasivo se excluyen.

## LTU2.4.2: sysfs AME

Se conservan diez atributos en **cada** build AP/CPE, bajo `/sys/class/ame/ame_ctrl_dev/`: `autoMcsCeiling`, `adj_mcs`, `autoMcs4096`, `cpe_mcs`, `adj_mix_mcs`, `adj_mimo`, `ofdma_en`, `ofdma_subbands`, `ofdma_subband0_hdrIdx`, `ldpc_iteration`. Sus hooks terminan en AME/BBP/FPGA, no en mac80211 o QCA10.1. Los offsets y hashes de funciones por build están en el informe y el catálogo.

- `autoMcsCeiling`, `ofdma_subbands` y `ldpc_iteration` truncan a8bits; `ofdma_en` además coerciona booleano. `11111111` decimal termina en0xc7, no0xff. No se acepta truncamiento como validación.
- `adj_mcs`, `adj_mimo` y `autoMcs4096` pasan valores base0/signed32; la unidad/semántica de `autoMcs4096` no se infiere de su nombre.
- `cpe_mcs` combina peer16bit, rate8bit y operación8bit; `adj_mix_mcs` tiene seis campos8bit. No son intercambiables con `mcs LEVEL` global.
- `ofdma_en_show` devuelve0bytes en estos binarios: vacío significa **UNKNOWN**, y no permite guardar/restaurar un booleano previo.
- El script mapea LDPC7/11/15/19/23/31 y RS25..30 a QPSK…4096QAM; auto32 y SISO QPSK34. Es una codificación estática, sin prueba de constelación o transmisión. Se preservan `NO_LDPC`, `NO_RS`, `NO_OFDMA` y guards de board/peer/FPGA/mode/training.

El D2 retenido usó **afltu.v2.4.0**, no2.4.2: `4096l` produjo0x1f inmediato y después0x20; retención **NOT_ACCEPTED**. `4096L` mayúscula imprime uso con rc0. Sólo se observó una escritura idempotente de máscara0xff; no OFDMA multiusuario. La restauración histórica exacta se conserva sin extrapolarla a2.4.2.

Rollback futuro requeriría restaurar juntos ceiling/adj_mcs/autoMcs4096, MIMO, peer/mode, scheduler fallback y backoff, con lectura inmediata y retención diferida. `mcs auto` puede conservar fallback; no acredita solo el retorno completo. Ningún atributo tiene rango RAM seguro ni propuesta aquí.

## Límite hardware y aceptación pendiente

GPIO13..16 del filtro AirPrism y GPIO7/LNA en wifi1 se catalogan sólo como **hardware/excluded**. El prototipo offline existente no prueba board mapping ni seguridad RF. No se proponen MMIO, GPIO, calibración/ART, factory, bootloader, flash, bypass regulatorio/DFS/firmas/licencias ni power overrides.

Antes de convertir alguna hipótesis en un experimento distinto harían falta identidad exacta HW/kernel/driver/FW, parser sin truncamiento, getter efectivo, preestado completo, watchdog y restauración verificables, receta fija y gates de carga/latencia/estabilidad. Son evidencias faltantes, no una orden de iniciar pruebas. Esta tarea termina con el catálogo y sus comprobaciones offline; el banco sigue bajo su propietario concurrente.

## Inventario individual

Las tablas siguientes son una vista compacta del JSON. Todas las cotas seguras son `null`; el locator detallado y la hipótesis/rollback por entrada están en `source_refs`, `physical_hypothesis` y `rollback`. En WA/XC se agrupan nombres UPH idénticos para lectura; el JSON mantiene ambas identidades separadas.

<!-- generated-catalog-inventory -->

### Parámetros WMI10.1 del mapa retenido

pdev: dominio wire `u32`, semántica y rango RAM seguro desconocidos; sin propuesta ni getter efectivo probado.

<!-- stage822a-payload-end -->
