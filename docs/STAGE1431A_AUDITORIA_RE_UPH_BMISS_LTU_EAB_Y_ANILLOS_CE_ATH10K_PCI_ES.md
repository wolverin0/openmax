<!-- doc-head: Wave 65; cierre de RE estática UPH, LTU, CE y DFS con relocaciones -->
Se verificaron binarios y fuentes archivadas; no se cargaron módulos ni se tocaron radios.
Los 123 nombres EAB definidos pertenecen a ame_core; no son 123 APIs exportadas.
La tabla CE recuperada tiene 24 bytes por entrada; relocaciones y llamadas se cuentan aparte.
<!-- /doc-head -->

# Stage 1431A — Auditoría binaria UPH, LTU, Copy Engine y DFS

## Alcance y procedencia

Wave 65 termina con mediciones `CONFIRMED_STATIC_BINARY`, hashes de entradas,
offsets de sección, relocaciones, controles negativos y reproducción determinista.
No hubo SSH, carga de módulos, modificación de binarios, flash ni medición RF.
Las lecturas nativas ejecutadas son herramientas del host que analizan archivos.

La ruta solicitada del productor 1428A no existía; había otro análisis cfg80211
con el mismo número y otro nombre, que se conservó. Se creó el productor solicitado.
El productor 1429A interrumpido y su recibo anterior se archivaron antes de sustituirlos.
Sus bloques incompletos y resultados iniciales permanecen como evidencia histórica.

Los módulos UPH proceden de WA/XC 8.7.25; los LTU son AF-LTU y LTU-Rocket 2.4.2.
Las imágenes OpenWrt 24.10.4 de PowerBeam, LiteBeam, LAP y Loco contienen módulos
ath10k idénticos entre las cuatro placas; el kernel embebido es 6.6.110.
Los recibos incluyen cada ruta y SHA-256; no se generalizan offsets entre compilaciones.

## Stage 1428A — Bmiss y objetos LTU

En UPH WA, `ubnt_poll_host_sta_bmiss_ind` ocupa ocho bytes en `.text+5756`.
Su relocación R_MIPS_26 apunta al símbolo externo `ieee80211_mlme_sta_bmiss_ind`.
La llamada entrante relevante está en `.text+30720`, offset de archivo 30784.
Se distinguen offset de sección y offset de archivo; no son direcciones RAM.
El thunk no demuestra por sí solo un temporizador ni su unidad temporal.

`ackAccuulateCnt` pertenece a `ame_core.ko`, no a UPH.
Es un byte con valor almacenado 25; no debe confundirse con `penaltyThreshold`.

| Binario LTU | ackAccuulateCnt en .data | table_ptpPwrRange en .data | Tamaño tabla |
|---|---:|---:|---:|
| AF-LTU CPE 2.4.2 | 0x12d1 | 0x1ec | 448 bytes |
| LTU-Rocket AP 2.4.2 | 0x12ed | 0x1f8 | 448 bytes |

Las referencias ARM indirectas a la tabla se resuelven por índice de símbolo,
sección y valor del ancla `.LANCHOR2`; hay nombres de ancla repetidos.
Resolver únicamente por nombre podría atribuir un puntero a otro objeto.
Los offsets no establecen por sí solos el significado físico de cada fila de potencia.

Cada `ame_core` tiene 123 nombres EAB definidos: 114 funciones y nueve objetos,
incluido un objeto de metadatos de exportación. Se excluyen los helpers ARM `__aeabi`.
`ame_dev` no define EAB, pero importa `AME_EAB_DumpAirInternal`, con dos relocaciones.
Sus otros tres nombres que contienen la subcadena eab son helpers ABI.
La definición en core y el consumidor en dev no convierten todos los símbolos en APIs públicas.

Se conservaron seis lecturas ELF y dos salidas `fullrea` del thunk con límites de ocho bytes.
Una expectativa inicial de pruebas confundía el import real con un helper ABI;
se corrigió la expectativa contra los mismos binarios y se conservaron los fallos iniciales.

## Stage 1429A — Tabla host CE recuperada

La tabla está en `ath10k_pci.ko`, `.rodata+628`: doce entradas de 24 bytes, 288 bytes.
Un consumidor `_28` referencia su base mediante HI16/LO16 y la copia con `kmemdup`.
La secuencia de argumentos confirma a0 apuntando a esa base y a1 con tamaño 288.
Las relocaciones de callbacks corroboran el layout; algunos nombres locales fueron eliminados.
Un puntero ejecutable relocado no se presenta como un nombre de función recuperado.

| CE | src_nentries | dest_nentries | src_sz_max |
|---|---:|---:|---:|
| CE0 | 16 | 0 | 256 |
| CE1 | 0 | 128 | 2048 |
| CE2 | 0 | 64 | 2048 |
| CE3 | 32 | 0 | 2048 |
| CE4 | 8192 | 0 | 256 |
| CE5 | 0 | 128 | 512 |
| CE6 | 0 | 0 | 0 |
| CE7 | 2 | 2 | 2048 |

Layout: flags, src_nentries, src_sz_max, dest_nentries y dos punteros de callback.
No existe un campo dest_sz_max en esa estructura.
CE6 inactivo y CE7 bidireccional son válidos; los flags 8 y 16 también lo son.
El detector anterior rechazaba esos casos y por eso su cero de coincidencias no probaba ausencia.
CE8 solicita 96 entradas; el redondeo del asignador a 128 es una proyección de fuente,
no una lectura de una asignación DMA en un radio.

Se verificaron fuentes ath10k-ct del commit `ac71b14dc93aef0af6f0f24808b0afb673eaa5f5`
y el parche smallbuffers de OpenWrt 24.10.4, con copias y hashes.
Las exportaciones de implementación CE están en core y los atributos host en PCI.
Se resuelven las relocaciones de `__ksymtab`; los nombres sueltos de strings no bastan.
Los tamaños seleccionados en ejecución y cualquier efecto de rendimiento siguen UNKNOWN.

## Stage 1430A — Parámetro de radar y referencias DFS

En el `umac.ko` auditado, `.modinfo` registra `ubnt_radar_mode` de tipo uint.
Su descripción es AP behaviour upon STA radar detection.
El objeto ocupa cuatro bytes de `.bss`; el registro `__param` tiene 20 bytes,
permiso 0644 y enlaces a `param_set_uint`, `param_get_uint` y al objeto.
El valor real en ejecución no fue leído.

Se midieron cuatro relocaciones nombradas al objeto de modo.
Para `ieee80211_mark_dfs` hay seis registros: dos R_MIPS_26 y dos pares HI16/LO16.
Los dos primeros son transferencias directas resueltas; los pares cargan direcciones.
La premisa de cinco registros no coincide con esa métrica en este binario.
No se descartan llamadas indirectas ni se convierte cada registro en una llamada.
La semántica REL se contrastó con el [cargador MIPS de Linux 2.6.32](https://raw.githubusercontent.com/torvalds/linux/v2.6.32/arch/mips/kernel/module.c).

`ath_dev.ko` tiene cero nombres de símbolo que contengan radar y once con dfs.
Esa ausencia nominal no demuestra ausencia de DFS, de detección física ni de otro módulo responsable.
Esta etapa no cambia parámetros ni establece aceptación regulatoria o funcionamiento RF.

## Evidencia y reproducción

- [1428A: UPH y LTU](../artifacts/verification/stage1428a_uph_bmiss_and_ltu_eab_relocation_audit.json).
- [1429A: tabla CE](../artifacts/verification/stage1429a_ath10k_pci_ce_ring_tables.json).
- [1430A: radar y DFS](../artifacts/verification/stage1430a_ubnt_radar_mode_and_dfs_relocation_audit.json).
- [Suite 1432A](../tests/test_stage1428a_to_1433a_suite.py).
- [Gate 1433A](../artifacts/verification/stage1433a_wave65_re_gate.json).

`python -m pytest tests/test_stage1428a_to_1433a_suite.py -q`

PASS significa integridad y corrección de esta auditoría estática, no verificación de radios en vivo.
