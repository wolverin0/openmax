<!-- doc-head: Wave125, taxonomia estatica de 571 knobs y colas SAFE_RAM sin promocion fisica
CONFIRMED: 571 filas, 42 fuentes verificadas y 40 modulos ELF locales analizados.
La cola ejecutable queda vacia; las prioridades pertenecen a calificacion pendiente.
Alcance offline, cero SSH, sin cambios de radios ni firmware.
-->
<!-- /doc-head -->

# Stage1790A: taxonomía binaria y prioridades de calificación

## Resultado y límite de la evidencia

CONFIRMED: Stage1788A clasifica los 571 IDs únicos del catálogo inmutable.
Se verificaron los SHA-256 de sus 42 fuentes y se analizaron 40 archivos ELF.
423 knobs presentan al menos una coincidencia exacta de símbolo o cadena rodata.
UNKNOWN: los otros 148 no tienen presencia demostrada por este método.
Una coincidencia puede pertenecer a otra versión; cada match conserva ruta, hash,
sección, offset y vínculo con la identidad del catálogo. No prueba efecto ni propiedad.
Los símbolos importados se distinguen de los definidos y de las cadenas de exportación.
Las cadenas se comparan completas: un getter no demuestra su setter por subcadena.

| Módulo | Archivos analizados | Cobertura |
|---|---:|---|
| ubnt_poll_host.ko | 8 | ELF local |
| ath_dev.ko | 9 | ELF local |
| umac.ko | 9 | ELF local |
| ame_core.ko | 2 | ELF local |
| eab_driver.ko | 0 | UNKNOWN, no encontrado en los árboles locales |
| ath10k_core.ko | 5 | ELF local |
| mac80211.ko | 7 | ELF local |

No se sustituye eab_driver por ame_dev. Las copias no son replicaciones independientes.
El inventario incluye archivos extraídos bajo artifacts y firmware; no abre archivos
comprimidos ni obtiene binarios remotos. Los receipts adicionales se enumeran con hash.

## Propietario e interfaz

La atribución conserva la frontera del catálogo: Linux, mac80211, ath10k,
firmware QCA, hardware o módulo propietario airMAX/LTU según la fuente.
El propietario es referencia de módulo o inferencia por familia, nunca un import aislado.
Cada fila conserva la superficie, selector, acceso, readback y referencias originales.
procfs, sysfs e iwpriv proceden de rutas o descriptores retenidos.
debugfs y nl80211 se etiquetan INFERRED cuando falta enlace exacto de handler.
Los 87 controles WMI internos no se convierten en una API nl80211 utilizable.
Los tres controles policy_only son metadatos; su interfaz permanece UNKNOWN.
No se inventa un endpoint uci. No se resuelve un phy concreto sin evidencia del destino.
Stage1031A enlaza handlers y gramática de aql_txq_limit y fq_quantum al hash de mac80211.
Stage1105A conserva la incertidumbre del handler de aql_threshold.

## Seguridad y estado de pruebas

| Tier | Knobs | Interpretación |
|---|---:|---|
| SAFE_RAM | 0 | Ningún rango aprobado con rollback verificado |
| REQUIRES_RESTART | 28 | Semántica de carga o inicialización |
| RF_HAZARD | 20 | Riesgo conservador de RF o hardware |
| PROTECTED | 523 | Protección explícita o retención preventiva por incertidumbre |

INFERRED: la taxonomía de riesgo es conservadora y distingue el motivo por fila.
PROTECTED preventivo no afirma que el knob escriba almacenamiento protegido.
CONFIRMED: todos conservan qualification=UNQUALIFIED y ejecución deshabilitada.
Hay 6 intentos históricos en el catálogo, 37 referencias del ledger sin identidad
de prueba reconciliada y 528 sin prueba encontrada en las fuentes auditadas.
UNTESTED_IN_AUDITED_EVIDENCE no significa que jamás se haya probado el control.
No se traslada una prueba LTU de una versión a otra ni se acepta hardware actual.

## Cola Stage1789A

Los cuatro dominios tienen cola SAFE_RAM vacía y un backlog separado de calificación.
Los siguientes ejemplos son candidatos para obtener evidencia, no tratamientos aprobados.

| Dominio | Prioridades del backlog | Estado |
|---|---|---|
| OpenWrt PtMP | codel_interval, codel_target, ct_special_5 | UNKNOWN físico |
| OpenWrt PtP | codel_interval, codel_target, ct_special_5 | UNKNOWN físico |
| airMAX AC WA/XC | swr_limit WA/XC, ff_mcast_airtime_limit | UNKNOWN físico |
| AF-LTU | adj_mcs, adj_mix_mcs, autoMcs4096 | UNKNOWN físico |

El backlog incluye metadatos y controles de riesgo pendiente para no ocultar vacíos.
Su orden usa frentes no dominados de relevancia ordinal 0..3 y suma con pesos iguales,
con ID como desempate. Los cuatro ejes son Bulk TCP, VoIP p99, pérdida IPTV y Jain.
UNKNOWN: la ganancia física esperada de cada eje es null; no hay predicción cuantitativa.
Las hipótesis de colas, agregación, scheduling y adaptación pueden tener tradeoffs.
La pertenencia a ambos dominios OpenWrt no demuestra equivalencia PtMP/PtP.

## Cinco pilares y siguiente evidencia

A: catálogo, hashes, tablas retenidas y comparación exacta de símbolos/rodata.
B: cola de investigación local y preguntas pendientes; cero consultas scholar nuevas.
C: límite offline y protocolo futuro A1→B1→A2→B2; cero bloques ejecutados.
D: crítica científica, prioridad ordinal y ausencia explícita de inferencia causal.
E: ingestión real en MemoryMaster, scope project:futuramax, registrada en Stage1791A.
El gate de cinco pilares comprueba estructura; no acredita experimentos no ejecutados.
Antes de cualquier ensayo hacen falta identidad exacta, handler, rango tipado aprobado,
readback, rollback independiente y autorización específica del ensayo.
El plan futuro conserva watchdog de 45 s no DFS y 120 s DFS, sin activarlo en esta wave.

## Artefactos y verificación

- artifacts/autoresearch/stage1788a_571knob_binary_symbol_and_safety_taxonomy_receipt.json
- artifacts/autoresearch/stage1789a_untested_safe_knobs_prioritized_queue_receipt.json
- artifacts/autoresearch/stage1791a_wave125_memorymaster_ingest.json
- tests/test_stage1788a_to_1793a_suite.py
- artifacts/verification/stage1793a_wave125_astra7_gate.json

El gate registra pytest real, reproducción determinista y hashes de los archivos evaluados.
No hay identificadores de clientes, direcciones de dispositivos ni resultados de campo nuevos.
La regla de exclamaciones se aplica al texto; los comentarios HTML obligatorios contienen su sintaxis.
