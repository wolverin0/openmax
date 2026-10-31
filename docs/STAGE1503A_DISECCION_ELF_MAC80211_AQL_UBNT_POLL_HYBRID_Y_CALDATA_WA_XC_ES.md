<!-- doc-head: Wave 77; disección ELF, procedencia híbrida y caldata estática -->
Auditoría exclusivamente local: ningún módulo cargado, SSH ni cambio de radio.
Las herramientas pasan sus verificaciones; la cobertura solicitada sigue incompleta.
<!-- /doc-head -->

# Wave 77 — Disección estática de AQL, híbrido y calibración

## Alcance y evidencia

Los scripts leen bytes de archivos locales, tablas ELF, rootfs SquashFS y FDT.
No ejecutan los módulos ni los scripts extraídos. No leen ni escriben particiones reales.
Los hashes SHA-256 identifican cada entrada; los informes extensos conservan símbolos,
relocaciones e instrucciones en archivos de evidencia, sin volcar ensamblador en consola.
La evidencia estática no demuestra asociación OTA, interoperabilidad ni rendimiento.

## Stage 1500A — mac80211 y ath10k

Se distinguen 21 rutas locales y ocho binarios únicos: siete mac80211 y un ath10k_core.
Cada variante tiene SHA-256, cabecera, tamaños de .text/.rodata/.data/.bss y censo
de símbolos y relocaciones REL/RELA. .bss es NOBITS: no contiene bytes de archivo.

En los siete mac80211, la inicialización compilada confirma:

| Campo | Valor compilado | Evidencia |
|---|---:|---|
| Límite AQL bajo | 5000 us | Cuatro stores, uno por AC |
| Límite AQL alto | 12000 us | Cuatro stores, uno por AC |
| Umbral AQL | 24000 us | Store asociado al campo leído por debugfs |

El store del umbral está en .text+2212; el campo relativo del objeto es +316.
La prueba vincula inicializador, flujo de registros y lectores debugfs: encontrar
un número aislado no basta. Las pruebas alteran constantes, campos y bucles en copias
en memoria para comprobar que una atribución incorrecta se rechaza.
La revisión independiente añadió casos de clobber en delay slot y de sobreescritura
del mismo campo. Se conservan los hallazgos y revisiones anteriores a su corrección.

`aql_txq_limit` y `aql_threshold` aparecen como nombres debugfs con referencias
relocalizadas; no se inventan símbolos globales con esos nombres.
`ieee80211_txq_may_transmit` también puede identificarse mediante su exportación
cuando el símbolo interno está renombrado. La identidad exacta de
`ieee80211_airtime_tx_txq` y `ath10k_mac_tx_push_txq` no queda establecida donde
faltan sus nombres. Ausencia de nombre no demuestra ausencia de funcionalidad.
Estos son valores compilados, no readbacks ni recomendaciones de ajuste operativo.

## Stage 1501A — Procedencia y parámetros híbridos

No se encontraron entradas WA y XC 8.7.11 autenticadas en el alcance local declarado.
El archivo llamado `stock_airos8_wa_8711_for_mtd_firmware.bin` contiene realmente
`WA.ar934x.v8.7.25.48568.260730.1010` en `lib/version`, extraído con salida nativa
exit 0 conservada. El nombre del archivo no autentica su versión.
El árbol 2XC no se sustituye por XC; otro rootfs sin versión queda sin autenticar.

Los ELF WA/XC 8.7.25 se auditan como referencias explícitas, no como 8.7.11:

| Propietario compilado | Registro __param | Sección | Valor en archivo |
|---|---|---|---|
| umac.ko | host_80211_enable, uint, 0644 | .data | 1 |
| umac.ko | ubnt_op_mode, uint, 0644 | .bss | Sin bytes almacenados |

El stride de __param es 20 bytes, recuperado de las relocaciones a nombre,
setter, getter y argumento. UPH no posee esos parámetros nombrados en las referencias.
Los literales `allow_80211`, `op_mode` y `wds` de una receta no son prueba de
parámetros ELF homónimos. El puente exacto entre configuración 8.7.11 y parámetros
compilados, los miembros sin símbolo de poll_state y la interoperabilidad Step 1
permanecen UNKNOWN. No se ensayó radio ni se propone cambiar el modo de una AP.

## Stage 1502A — Caldata y board.d

No apareció un checkout target/linux/ath79 en las raíces candidatas declaradas.
Se usaron las imágenes factory OpenWrt 24.10.4 locales de PowerBeam y LiteBeam,
extrayendo rootfs y FDT compilado. Esto no completa la cobertura de fuente ni de XC.

| Consumidor compilado, ambas placas WA | Celda ART | Longitud |
|---|---|---:|
| qcom,ath10k, PCIe 5 GHz | calibration@5000, offset 0x5000 | 2116 bytes |
| qca,ar9340-wmac, 2.4 GHz | calibration@1000, offset 0x1000 | 1088 bytes |

Las referencias phandle unen consumidor, celda y partición etiquetada `art`.
No se deduce el índice mtd5 de la numeración de airOS: el índice runtime OpenWrt
sigue UNKNOWN. Ningún acceso a mtd0/1/4/5 fue necesario.
`02_network` contiene los modelos y eth0; toma la MAC de `art`+0x5006.
El `11-ath10k-caldata` extraído no tiene casos PBE/LBE: el FDT aporta las celdas.
Su constante 0x2f20 (12064 bytes) corresponde a un caso D-Link, no a estas placas WA.
Por tanto no se sostiene una diferencia PBE=2116 frente a LBE=12064.

El catálogo local identifica PowerBeam con 0xe3d6, en conflicto con el 0xe7f8
solicitado. LiteBeam coincide con 0xe7f9. Son metadatos del catálogo, no lecturas
de identidad física: ningún ID de hardware queda verificado mediante esta auditoría.
El catálogo se interpreta por AST de literales, sin importarlo ni ejecutarlo.

## Reproducción y cierre

- [Auditor 1500A](../tools/re/extract_stage1500a_openmax_ath10k_mac80211_aql_elf_audit.py)
- [Auditor 1501A](../tools/re/extract_stage1501a_ubnt_poll_host_hybrid_allow80211_elf_audit.py)
- [Auditor 1502A](../tools/re/extract_stage1502a_wa_xc_caldata_and_board_d_static_audit.py)
- [Suite consolidada](../tests/test_stage1500a_to_1505a_suite.py)
- [Gate 1505A](../tools/verify/verify_stage1505a_wave77_re_gate.py)
- [Recibo del gate](../artifacts/Scrolls/stage1505a_wave77_re_gate.json)

El gate separa software_status de status global. Pytest limpio puede cerrar las
herramientas, pero no convierte fuentes faltantes en evidencia disponible.
El cierre integral permanece INCOMPLETE hasta aportar WA/XC 8.7.11 autenticados
y las entradas target/linux/ath79 y XC que faltan. Se conserva el primer error de
sintaxis del productor 1502A junto con el código corregido y su reproducción.
