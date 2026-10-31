<!-- doc-head -->
*STAGE1568A — RE profundo: resolucion del direccionamiento MIPS PIC de ubntspecd (BPS/SCORE/RATING) y mapeo SGMT de firmware-2.bin de OpenWrt frente a airOS 8*
# STAGE 1568A — `ubntspecd` (MIPS PIC) y `firmware-2.bin` (SGMT)

## 0. Método y límites
- **100% estático y offline**: se leen ELF y contenedores ya presentes en el repo. Sin SSH, sin carga de módulos, sin escritura de firmware.
- Etiquetas: `CONFIRMED` (bytes medidos), `INFERRED`, `UNKNOWN`, `REFUTED`.
- Regla de dirección MIPS aplicada: `%hi` lleva **acarreo** cuando la mitad baja tiene el bit 15 puesto. Para `0x0040acf4`, `hi = 0x0041` y `lo = 0xacf4` (con signo, `-21260`). Sin ese acarreo la búsqueda da cero y se concluye falsamente que no hay referencia.

## 1. Stage 1566A — resolución del PIC en `ubntspecd`
### 1.1 El mecanismo real no es `$gp`
- `CONFIRMED`: la cadena `" %d [%d] BPS=%d SCORE=%d RATING=%d"` en `0x0040acf4` se referencia con **`lui $fp, 0x0041`** en `0x00407f00` y **`addiu $a0, $fp, -21260`** en **`0x004080d4`**.
- `REFUTED`: la hipótesis de la Wave 86 de que la referencia era GP-relativa o vía GOT. No hay ni un `lw $rt, off($gp)` que apunte a la cadena, ni un slot de GOT con `0x0040acf4`, ni un par `lui/addiu` con `hi = 0x0040`.
- `CONFIRMED`: hay **1** sitio de referencia por binario (WA y XC), no 8: al exigir que el `lui` sea el **más cercano** al `addiu` con el mismo registro base, los emparejamientos espurios desaparecen.
- `CONFIRMED`: el binario es `ET_EXEC` PIC enlazado dinámicamente, pero el modelo de datos usado es **base constante en `$fp`**, no small-data `$gp`.

### 1.2 La función y el punto de impresión
- `CONFIRMED`: la función que contiene la referencia empieza en **`0x00407db8`**, mide **264 instrucciones** y la llamada de log es **`jal 0x0040b340`** en **`0x004080f8`**.
- `CONFIRMED`: el bucle **no calcula** el score. Lee tres campos **precalculados por STA** y los pasa como argumentos:
  - `BPS` = palabra en **`+0x4971c`** del registro de STA,
  - `SCORE` = palabra en **`+0x55f1c`**,
  - `RATING` = palabra en **`+0x6271c`**.
- `CONFIRMED`: el puntero de entrada se forma como `s1 + (s5*5 + s2)*4` y el paso entre STA es de **188 bytes**.
- `CONFIRMED`: el primer `%d` sale de `lhu a1, 28(...)`; el segundo `[%d]` es un registro heredado del bloque anterior.

### 1.3 Por qué la aritmética sigue UNKNOWN
- `CONFIRMED`: **0** almacenes con desplazamiento literal `0x4971c`, `0x55f1c` o `0x6271c` en todo el `.text`. Quien escribe esos campos usa **desplazamiento por registro**, no literal.
- `CONFIRMED`: **0** operaciones de memoria float (`lwc1`/`ldc1`/`swc1`) en todo el `.text`, pero **29** instrucciones `COP1`. `INFERRED`: hay aritmética float con constantes construidas en registros enteros (vía `mtc1`), no cargadas de literales.
- `UNKNOWN`: los pesos y la combinación de histograma. No se inventan: se entrega el punto exacto donde se leen los tres valores y se demuestra por qué la búsqueda literal no alcanza a quien los produce.

## 2. Stage 1566A — coeficientes de `ame_dfs.ko`
- `CONFIRMED`: `spyke_acc_coef` mide **60 B**, SHA-256 `8eabda21b8912952…`, y su primer `f32` little-endian vale **0.012104**.
- `CONFIRMED`: `handle_func_fixrxgain` mide **48 B** y sus constantes ARM (`movw`/`movt`/`cmp`) quedan extraídas en el recibo.
- `UNKNOWN`: la semántica de ambos; los valores son exactos y hasheados.

## 3. Stage 1567A — `firmware-2.bin` de OpenWrt (QCA988X hw2.0)
### 3.1 Identidad y estructura
- `CONFIRMED`: `firmware-2.bin` mide **204.796 B**, SHA-256 `398e4380e7e55105f3da0f78af29d1e437404ed3a82597aa4b6daaa7dce1a38e`, y es **idéntico en las 4 imágenes** WA (un solo hash distinto).
- `CONFIRMED`: cabecera `QCA-ATH10K`, versión **`10.1-ct-8x-__fW-022-ecad3248`**, tabla de IE en `0x0c` con **6 registros**: `0(28)`, `1(4)`, `2(8)`, `30(16)`, `4(7140 @0x6c)`, `3(197537 @0x1c58)`, con **3 bytes** de relleno final.
- `CONFIRMED`: **2 contenedores SGMT** (IE4 e IE3), **4 segmentos cada uno = 8 segmentos**, destinos `0x00980000`, `0x0040b000`, `0x0040b1a0`/`0x0040bd10`, `0x00983c00`, entry point `0x00983c00`, **258.485 B** decodificados en total.
- `CONFIRMED`: los 8 segmentos se decodifican con el descompresor BMI_LZ del repositorio y la relectura con `SgmtContainer` coincide.

### 3.2 CCA (`cca_thresh62`)
- `CONFIRMED`: el patrón de 16 B `009e0200a016721320137213109e0200` aparece **una vez**, en **IE3, segmento 3**, desplazamiento **`0x33984`**, dirección virtual **`0x009b7584`**.
- `CONFIRMED`: es el **mismo índice de segmento** que en airOS 8 (segmento 3) pero **otra dirección**: airOS `0x009c7a78` frente a OpenWrt `0x009b7584`.
- `INFERRED`: el payload es el mismo literal de `BB_timing_controls_1`; cambia el layout del build, no el contenido.

### 3.3 Divisores PLL sub-20 MHz
- `REFUTED`: el patrón `060c121824303600` **no aparece** en `firmware-2.bin`. 0 coincidencias sobre **258.485 B** escaneados, incluido el prefijo de 6 B.
- `INFERRED`: la tabla sub-20 MHz de airOS 8 no viaja en este build `ath10k-ct`; la ruta de 5/10 MHz debe resolverse por otra vía en OpenWrt.

### 3.4 WMI 0x9044
- `CONFIRMED`: `0x00009044` aparece **una vez alineado a 4 bytes**, en **IE3, segmento 0** (destino `0x00980000`), desplazamiento **`0x00000f8c`**, dirección virtual **`0x00980f8c`**.
- `CONFIRMED`: en airOS 8 el mismo literal vive en segmento 0 pero en `0x00980eec` (AP/STA) y `0x00980ec4` (PTP): mismo segmento, **dirección distinta**.
- `REFUTED`: el literal de control **`0x00009064`** de airOS **no existe** en este firmware (0 alineados y 0 desalineados). La tabla de despacho de airOS no se hereda.

## 4. Comparación directa airOS 8 frente a OpenWrt `firmware-2.bin`
| Payload | airOS 8 (1555A) | OpenWrt `firmware-2.bin` (1567A) | Veredicto |
| :--- | :--- | :--- | :--- |
| CCA 16 B | seg 3, `0x009c7a78`, off `0x043e78` | seg 3, `0x009b7584`, off `0x0033984` | presente, **vaddr distinta** |
| PLL 8 B | seg 1, `0x0040bb40`, off `0x000b40` | **no aparece** (0 de 258.485 B) | **ausente** |
| WMI `0x9044` | seg 0, `0x00980eec` / `0x00980ec4` | seg 0, `0x00980f8c`, off `0x0f8c` | presente, **vaddr distinta** |
| WMI `0x9064` (control) | `0x0040fb54` / `0x0040fb44` / `0x0040f5d4` | **no aparece** | **ausente** |

- `CONFIRMED`: **ningún** payload conserva la dirección virtual de airOS. Cualquier parche portado entre familias debe re-resolver el offset, nunca copiar el `vaddr`.
- `INFERRED`: la coincidencia de **índice de segmento** (CCA en 3, WMI en 0) con direcciones distintas es consistente con el mismo esqueleto de firmware reenlazado.

## 5. Lo que queda abierto
- `UNKNOWN`: aritmética y pesos de BPS/SCORE/RATING (requiere dataflow sobre los índices que escriben `+0x4971c`/`+0x55f1c`/`+0x6271c`).
- `UNKNOWN`: semántica de `spyke_acc_coef` y de `handle_func_fixrxgain`.
- `UNKNOWN`: ruta de 5/10 MHz en OpenWrt, dado que la tabla PLL de airOS no existe en `firmware-2.bin`.
- `UNKNOWN`: destino de salto del despacho WMI `0x9044` en ambas familias.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1566A` | `tools/re/dissect_stage1566a_ubntspecd_mips_got_and_ame_dfs_coefs.py` + `artifacts/autoresearch/stage1566a_opencode_fullrea_ubntspecd_got_and_ame_dfs_coefs.json` |
| `1567A` | `tools/re/dissect_stage1567a_openwrt_firmware2_sgmt_offsets.py` + `artifacts/autoresearch/stage1567a_opencode_fullrea_openwrt_firmware2_sgmt_offsets.json` |
| `1568A` | este documento (menos de 175 líneas, 1 `doc-head`, 0 signos de exclamación) |
| `1569A..1571A` | `tests/test_stage1566a_to_1571a_suite.py` y `tools/verify/verify_stage1571a_wave88_opencode_gate.py` con su recibo |

## 7. Nota de corrección
- Este documento corrige dos afirmaciones previas: el direccionamiento de la cadena de score **no** es `$gp`/GOT (es `$fp` constante), y el binario **sí** contiene aritmética float (29 `COP1`), aunque no cargue ni un literal float desde memoria.
