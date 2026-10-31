<!-- doc-head: Stage 1293A - extraccion fallida de 01_leds desde SquashFS con causa medida y cierre 30 de 30 de los recibos de Waves 32..36, con 1252A sin evidencia previa declarada -->
# Stage 1293A — Extracción de `01_leds` y auditoría 30 de 30

- **Recibo de extracción**: [`artifacts/verification/stage1290a_squashfs_board_d_01_leds_extraction.json`](../artifacts/verification/stage1290a_squashfs_board_d_01_leds_extraction.json)
- **Recibo de cierre**: [`artifacts/verification/stage1291a_waves32_to_36_30of30_receipts_complete.json`](../artifacts/verification/stage1291a_waves32_to_36_30of30_receipts_complete.json)
- **Índice**: [`artifacts/verification/stage1292a_stages1169a_to_1259a_master_receipt_index.json`](../artifacts/verification/stage1292a_stages1169a_to_1259a_master_receipt_index.json)
- **Alcance**: offline estático. Sin radio, sin SSH.

## 1. Qué se intentó y qué se consiguió

El objetivo era leer `/etc/board.d/01_leds` de las cuatro imágenes factory 24.10.4. El entorno **no tiene
`unsquashfs`, ni `7z`, ni `xz`**, y en el repositorio **no existe ningún fichero `01_leds`**. Así que se
escribió un lector **SquashFS v4 en Python puro** usando sólo `lzma` de la biblioteca estándar.

| Capa | Estado |
| :--- | :-: |
| superbloque (magic `hsqs`, versión 4) | **funciona** en 4/4 imágenes |
| bloques de metadatos (cabecera de 2 bytes) | **funciona** |
| recorrido de directorios (`etc/board.d/01_leds`) | **resuelve la ruta** |
| inodo del fichero | **inconsistente** (`file_size` 23.616) |
| bloques de fragmento (48 por imagen) | **fallan los 48** con `LZMAError` |
| contenido de `01_leds` | **NO EXTRAÍDO** |

**`REFUTED`**: la matriz LED sigue sin recuperarse del binario. `led_matrix_recoverable = 0`.

## 2. La causa, dicha con precisión

El lector llega hasta el walk: encuentra `/etc/board.d/01_leds` y devuelve un inodo de tipo fichero. Pero
ese inodo declara `blocks_start = 0`, `fragment = 1`, `frag_offset = 66.447` y `file_size = 23.616`, que
no corresponden a un script de board (del orden de cientos de bytes).

Al resolver la tabla de fragmentos —que en SquashFS v4 es un **array de punteros `u64` a bloques de
metadatos**, con 512 entradas por bloque— las entradas se leen con valores plausibles (primer
`start = 0x2c500`, `size = 0xd844`), pero el bloque de datos en ese offset **no es un flujo XZ válido**.
Los 48 fragmentos fallan igual, lo que descarta un caso aislado.

Conclusión honesta: **hay un error de offset en mi cadena tabla→bloque**, no una ausencia en la imagen.

## 3. Lo que NO se hace

- No se inventa el contenido de `01_leds`.
- No se deduce el número de LEDs por board a partir del nombre del modelo.
- No se promociona el `0` de `shift_register_tokens` de la Wave 41 a «no hay registro de
  desplazamiento».
- No se marca `1252A` como verificado: **no tiene doc ni gate previos**.

## 4. Cierre 30 de 30 en Waves 32..36

Diez etapas no tenían recibo JSON propio. Se generaron **10 recibos de enlace**:

| Etapa | Evidencia enlazada |
| :--- | :--- |
| 1230A, 1239A, 1243A, 1245A, 1249A, 1251A, 1255A, 1257A, 1258A | doc o wave gate existente |
| **1252A** | **ninguna** (`no_evidence_found`) |

`present_before = 20`, `backfilled = 10`, `present_after = 30`, `complete_30_of_30 = 1`.

**Advertencia que viaja con el número**: un recibo de enlace **afirma que la evidencia existe en otro
sitio**, no que se haya re-medido. Presentar «30/30» como treinta verificaciones independientes sería
falso: son veinte verificaciones y diez punteros.

## 5. Índice 1169A..1259A

**73 recibos** indexados con tamaño y prefijo SHA-256, cubriendo el rango completo. Un índice prueba
presencia e integridad del recibo, **no** la corrección de su contenido.

## 6. Huecos

- **`UNKNOWN`** — el contenido exacto de `01_leds` para las cuatro boards.
- **`UNKNOWN`** — si `1252A` tuvo evidencia en otra ruta no indexada.
- **Bloqueado** — la extracción requiere corregir el offset de la cadena de fragmentos o instalar
  `unsquashfs`.
- **Límite conocido** — un `ucidef_set_led` es un default declarativo, no prueba de LED poblado.
- **No intentado** — arrancar ninguna board, leer `/sys/class/leds/` en vivo.
