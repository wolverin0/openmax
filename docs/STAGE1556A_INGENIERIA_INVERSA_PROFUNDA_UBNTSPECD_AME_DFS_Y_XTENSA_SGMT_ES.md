<!-- doc-head -->
*STAGE1556A — ingenieria inversa profunda: ubntspecd (BPS/SCORE/RATING), ame_dfs (PW/PRI/LNA) y offsets exactos Xtensa SGMT (PB040 CCA/PLL y WMI 0x9044)*
# STAGE 1556A — Disección profunda: `ubntspecd`, `ame_dfs.ko` y SGMT AR9888v2

## 0. Método y límites
- **100% estático y offline**: se leen ELF y contenedores SGMT ya presentes en disco. No hay SSH, ni carga de módulos, ni parcheo en radio, ni escritura de contenedores.
- Etiquetas: `CONFIRMED` (bytes medidos), `INFERRED` (deducido), `UNKNOWN` (no medido), `REFUTED` (medido en contra).
- Los nombres se comparan por **límites de token**; las direcciones de código se buscan como **palabras de 32 bits alineadas**, no como subcadena. Dos falsos positivos de esta wave se documentan abajo precisamente por eso.

## 1. Stage 1554A — `ubntspecd` (airOS) y `amespecd` (LTU)
### 1.1 Forma de los binarios
- `CONFIRMED`: `ubntspecd` de WA 8.7.25, XC 8.7.25 y XC 8.7.4cs pesa **47.192 B** en las tres, con SHA-256 distinto cada una. Es `ELF32` MIPS big-endian, `ET_EXEC`, **sin tabla de secciones** (`e_shnum = 0`) y por tanto sin símbolos.
- `CONFIRMED`: `amespecd` de LTU 2.4.2 pesa **45.760 B**, es `ELF32` ARM little-endian `ET_EXEC` y también viene sin tabla de secciones.
- `CONFIRMED`: ambos tienen `PT_INTERP` y `PT_DYNAMIC`, es decir son ejecutables **enlazados dinámicamente y PIC**. Esto condiciona todo el resto del apartado.
- `REFUTED`: no existe ningún `libubnt*` en los árboles airOS auditados (**0 ficheros**). La atribución de la fórmula a una librería `libubnt` no se sostiene con estos datos.

### 1.2 El ancla exacta de BPS, SCORE y RATING
- `CONFIRMED`: `ubntspecd` contiene la cadena de formato exacta **`" %d [%d] BPS=%d SCORE=%d RATING=%d"`** en el fichero offset **44.276** = dirección virtual **`0x0040acf4`** (primer `PT_LOAD`: `vaddr 0x400000`, `offset 0`, `filesz 46800`).
- `CONFIRMED`: el bloque de cadenas vecino sitúa la función en la ruta de estadísticas AM: `/tmp/amg_stas` (`0x0040ac78`), `STA list` (`0x0040aca0`), `LOCAL entry` (`0x0040aca8`), `Sending AM stats:` (`0x0040ada0`), `LOCAL AM stats update:` (`0x0040adb4`).
- `CONFIRMED`: los tres valores se imprimen como enteros (`%d`), no como coma flotante.
- `REFUTED`: no existen etiquetas de rating textuales (`EXCELLENT`, `GOOD`, `FAIR`, `POOR`): **0 ocurrencias**. `RATING` es numérico.

### 1.3 Por qué la aritmética queda UNKNOWN (con causa medida)
- `CONFIRMED`: **0** referencias estáticas a `0x0040acf4` por par `lui`+`addiu/ori` y **0** palabras de 32 bits (big-endian o little-endian) con ese valor en todo el fichero.
- `CONFIRMED`: `$gp` no se materializa con una constante de enlace, sino como **base + `$t9`** en tres prólogos: `0x00400f2c`, `0x004026ac`, `0x004088e0`, con bases `0x00022904`, `0x00021184` y `0x0000af50` respectivamente.
- `INFERRED`: al ser PIC dinámico, la dirección efectiva de la cadena se forma con el GOT en tiempo de carga; sin volcar ese GOT no se puede anclar la instrucción que consume los tres valores.
- `UNKNOWN`: la fórmula, los pesos y la combinación de histograma que producen BPS, SCORE y RATING **no se reconstruyen en esta etapa**. Se entrega el ancla exacta, el contexto funcional y el motivo técnico verificable, en lugar de una fórmula inventada.

### 1.4 El daemon LTU no lleva esa superficie
- `CONFIRMED`: `amespecd` tiene **0** anclas `BPS=`/`SCORE=`/`RATING=` y **0** tokens `score`/`rating` en minúscula. Su único token de la familia es `hist` (1 ocurrencia).
- `INFERRED`: la puntuación de tres valores es una superficie del daemon airOS y no del daemon espectral LTU.

## 2. Stage 1554A — `ame_dfs.ko`: tablas de radar y criterios
- `CONFIRMED`: el módulo conserva nombres reales (149 funciones, 49 objetos). Las tablas se leen **por símbolo**, no por patrón.
- `CONFIRMED`: `dfs_threshold`, `dfs_work` y `dfs_work_special` miden **52 B** cada una, y las tres son **byte-idénticas** (SHA-256 `216fbaa203e2f859…`). Palabras little-endian:
  `0xFFFFFFE0, 4, 4, 0, 0, 0x74737461, 0, 2, 0, 0, 0xFFFFFFFF, 0, 0`
  Los bytes de esa quinta palabra son ASCII `atst`, lo que indica que la estructura mezcla enteros con un campo de texto.
- `CONFIRMED`: `spyke_acc_coef` mide **60 B**; su primera palabra interpretada como `f32` little-endian vale **0.012104**, y el resto decae monótonamente como enteros (`572729394, 505356321, 437984285, …`). La semántica de esos valores es `UNKNOWN`.
- `CONFIRMED`: `dfs_hit` mide **192 B**; `pulseTime` y `priTime` miden **4.092 B** cada uno y viven en `.bss` (cero en reposo), lo que da **1.023 bins de 32 bits** por histograma.
- `CONFIRMED`: existen los siete contadores `type0Cnt … type6Cnt`, más `type5log` (8.184 B). Siete clases de patrón en este driver.
- `CONFIRMED`: el detector se ancla en `ep_task` (**4.496 B**) y en `handle_func_startdfs` (**1.044 B**); la ruta de ganancia/LNA se ancla en `handle_func_fixrxgain` (**48 B**) y `gISR_noisefloor`.
- `REFUTED`: ningún símbolo usa los tokens `lna`, `sat` o `saturation`. La inmunidad de LNA no se nombra así en este binario; el portador medible es el camino `fixrxgain` + `gISR_noisefloor`.
- `UNKNOWN`: la semántica campo a campo de las tablas de umbral (¿µs?, ¿dB?, ¿conteos?) no se asigna sin una prueba de consumo; los valores exactos quedan entregados y hasheados.
- `CONFIRMED`: `ame_dfs.ko` **no** es el mismo fichero en CPE y AP: **141.472 B** frente a **170.108 B**, con SHA-256 distinto. Las tablas medidas arriba son las de la imagen **CPE** y toda afirmación debe declarar de cuál habla.

## 3. Stage 1555A — Offsets exactos en el contenedor SGMT AR9888v2
Se cargan los tres contenedores embebidos en `umac.ko` con el patcher del repositorio (`firmware/xtensa_sgmt_surgical_patcher.py`) y se valida la **preimagen** contra el contenedor real, de modo que una discrepancia lanza excepción en lugar de reportarse como acierto.

### 3.1 PB040-CCA-AGC-OVERRIDE (`cca_thresh62`, WHAL)
- `CONFIRMED`: **segmento 3**, dirección virtual **`0x009c7a78`**, offset relativo al segmento **`0x043e78`**, longitud **16 B**.
- Palabras originales: **`0x00029e00`, `0x137216a0`, `0x13721320`, `0x00029e10`** (`BB_timing_controls_1` / `cca_thresh62`, valor por defecto, valor sombra y `BB_timing_controls_5`).
- Palabras parcheadas: **`0x00029e00`, `0x137216a0`, `0x13761320`, `0x00029e10`**. Cambia **un solo byte**, el índice **10** (`0x72 → 0x76`).
- `CONFIRMED`: la preimagen coincide en los tres hermanos documentados (`ptmp_ap`, `ptmp_sta`, `ptp`) con `matches = 1` en los tres.

### 3.2 PB040-SUB20MHZ-PLL-DIV (5 / 10 MHz)
- `CONFIRMED`: **segmento 1**, dirección virtual **`0x0040bb40`**, offset **`0x000b40`**, longitud **8 B**.
- Original: `06 0c 12 18 24 30 36 00` → Parcheado: `06 0c 12 18 24 30 48 00`. El séptimo byte pasa de `0x36` (54 = 27 Mbps en unidades de 0,5 Mbps) a `0x48` (72 = 36 Mbps).
- `CONFIRMED`: preimagen verificada también en los tres hermanos (`matches = 1`).

### 3.3 WMI 0x9044 (`WMI_PEER_RATE_RETRY_SCHED_CMDID`)
- `CONFIRMED`: el literal **`0x00009044`** aparece **una sola vez**, **alineado a 4 bytes**, y **no** en `.data` sino en el **segmento 0 (IRAM)**:
  - `ptmp_ap` y `ptmp_sta`: **`0x00980eec`**, offset **`0x0eec`**;
  - `ptp`: **`0x00980ec4`**, offset **`0x0ec4`**.
- `CONFIRMED`: control positivo del método — el literal conocido `0x00009064` sí está en su dirección documentada (`0x0040fb54` en `ptmp_ap`, `0x0040fb44` en `ptmp_sta`, `0x0040f5d4` en `ptp`), con `literal_ok = 1` en las tres.
- `REFUTED` (falso positivo descartado): un escaneo por bytes encontraba `44 90 00 00` en **`0x0040d13f`**, que está **desalineado** y cae fuera de los datos del segmento. Se rechaza.
- `UNKNOWN`: el destino de salto del despacho de `0x9044`. El literal vive en IRAM y no en el array de opcodes de `.data` que indexa `0x9064`, así que la geometría de 3 bytes por entrada no se hereda. No se afirma ningún `target`.

### 3.4 Estado de activación
- `CONFIRMED`: no se ha escrito, recompreso, flasheado ni cargado ningún contenedor. `container_written = 0` y `activation = BLOCKED`.
- Las palabras parcheadas provienen de la especificación del repositorio; esta etapa demuestra que **aplican limpiamente sobre la preimagen**, no que la radio las acepte.

## 4. Lo que queda abierto
- `UNKNOWN`: fórmula BPS→SCORE→RATING (requiere GOT en tiempo de carga o un desensamblador PIC con resolución de `$gp`).
- `UNKNOWN`: semántica de campo de `dfs_threshold`, `dfs_work`, `dfs_work_special` y `spyke_acc_coef`.
- `UNKNOWN`: distribución en ejecución de los histogramas `pulseTime`/`priTime` (en `.bss`, cero en reposo).
- `UNKNOWN`: destino del despacho WMI `0x9044` y cuerpo del handler.

## 5. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1554A` | `tools/re/dissect_stage1554a_ubntspecd_score_and_ame_dfs_tables.py` + `artifacts/autoresearch/stage1554a_opencode_fullrea_ubntspecd_and_ame_dfs_dissection.json` |
| `1555A` | `tools/re/dissect_stage1555a_xtensa_sgmt_whal_pll_wmi9044_offsets.py` + `artifacts/autoresearch/stage1555a_opencode_fullrea_xtensa_sgmt_whal_pll_wmi9044_offsets.json` |
| `1556A` | este documento (menos de 175 líneas, 1 `doc-head`, 0 signos de exclamación) |
| `1557A..1559A` | `tests/test_stage1554a_to_1559a_suite.py` y `tools/verify/verify_stage1559a_wave86_opencode_gate.py` con su recibo |
