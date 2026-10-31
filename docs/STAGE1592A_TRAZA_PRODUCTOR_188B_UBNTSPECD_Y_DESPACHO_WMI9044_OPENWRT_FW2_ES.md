<!-- doc-head -->
*STAGE1592A — traza del productor de 188 B en ubntspecd y despacho del literal WMI 0x9044 en firmware-2.bin de OpenWrt*
# STAGE 1592A — Función `0x004073b0` y el literal WMI `0x9044`

## 0. Método y límites
- **100% estático y offline**: se leen ELF y contenedores SGMT ya presentes en el repo. Sin SSH y sin escribir nada bajo `firmware/`.
- Etiquetas: `CONFIRMED` (bytes medidos), `INFERRED`, `UNKNOWN`, `REFUTED`.
- Los desensambladores se validan antes de afirmar: el de MIPS por estructura de instrucción, el de Xtensa `l32r` por **tasa de localidad de destino** contra el azar.

## 1. Stage 1590A — función `0x004073b0` de `ubntspecd`
### 1.1 Extensión y alcanzabilidad
- `CONFIRMED`: la función empieza en **`0x004073b0`** y mide **363 instrucciones** tanto en WA 8.7.25 como en XC 8.7.25.
- `CONFIRMED`: **0 llamadores directos** en todo el `.text`. Ningún `jal 0x004073b0` existe, así que se alcanza por tabla de punteros o no se alcanza.
- `INFERRED`: su papel no se puede fijar por sitios de llamada; hay que buscarlo en las tablas que contienen su dirección.

### 1.2 Resolución de importaciones dinámicas
- `CONFIRMED`: `PT_DYNAMIC` expone **63** entradas `JUMP_SLOT` con nombre resoluble en `.dynstr`.
- `CONFIRMED`: en todo el binario solo hay **2** pares `lw $t9, off($gp)` + `jalr $t9`, en `0x004026e8` y `0x004088c0`.
- `CONFIRMED`: el voto de `$gp` es **ambiguo**: el mejor candidato `0x004236e0` obtiene **2 votos** y el segundo también **2**, porque hay dos sitios y 63 slots.
- `CONFIRMED`: bajo ese candidato los dos sitios resuelven a `pclose` y `strcpy`.
- `INFERRED`: son **candidatos**, no prueba. Con dos muestras el problema está subdeterminado y así se reporta.

### 1.3 Almacenes y campos por-STA
- `CONFIRMED`: la función ejecuta **38** almacenes (`sw`, `sh`, `sb`). **Ninguno** usa desplazamiento literal `0x971c`, `0x5f1c` o `0x271c`.
- `CONFIRMED`: en todo el `.text` hay **0** almacenes con esos tres desplazamientos.
- `CONFIRMED`: existen **35** constructores de base `lui 0x0005` / `lui 0x0006`, el mismo patrón que usa el bucle de lectura, porque `0x4971c` excede un desplazamiento con signo de 16 bits. Ninguno va seguido de un almacén a los tres campos.
- `UNKNOWN`: quién escribe BPS, SCORE y RATING. La etapa no lo encuentra y no lo inventa.

### 1.4 El sitio `0x00407a44` no es un stride de 188
- `CONFIRMED`: el intérprete afín sobre la ventana de `0x00407a44` produce los valores `{47, 48, 64, 1280}` y **ningún 188**.
- `REFUTED`: la afirmación de la Wave 90 de que `0x00407a44` fuera el segundo sitio de stride 188. Era un falso positivo del detector por cadena de registros: compartía el prefijo `sll 6` / `sll 4` / `subu` con el idioma real.
- `CONFIRMED`: el **único** sitio genuino de 188 B sigue siendo el bucle de impresión en **`0x00407f3c`**, donde además están las 7 lecturas de los tres campos.
- `INFERRED`: `0x004073b0` indexa otra estructura, con multiplicadores 320 y 1600 sobre el mismo registro semilla; no es el productor del registro de 188 B.

## 2. Stage 1591A — el literal WMI `0x9044` en `firmware-2.bin`
### 2.1 Identidad y geometría
- `CONFIRMED`: `firmware-2.bin` mide **204.796 B**, SHA-256 `398e4380e7e55105f3da0f78af29d1e437404ed3a82597aa4b6daaa7dce1a38e`.
- `CONFIRMED`: IE3 **197.537 B** e IE4 **7.140 B**; **4 + 4 segmentos**; **258.485 B** decodificados en total.
- `CONFIRMED`: el literal `0x00009044` aparece **una sola vez**, alineado a 4 B, en **IE3 segmento 0**, offset `0xf8c`, vaddr **`0x00980f8c`**.

### 2.2 Validación del decodificador `l32r`
- `CONFIRMED`: se evalúan **200** candidatos `l32r` con tres fórmulas de dirección.
- `CONFIRMED`: la fórmula ganadora es `((PC + 3) & ~3) + (imm16 << 2)` con **174/200** destinos dentro de la imagen (**tasa de localidad 0,87**, todos alineados) frente a una tasa por azar de **6,0 × 10⁻⁵**.
- `INFERRED`: la fórmula es correcta con alta confianza; las otras dos quedan en 0,71.
- `UNKNOWN`: el flujo de instrucciones real. Un escaneo lineal por bytes no prueba límites de instrucción, así que cada acierto es un **candidato** que el contexto respalda.

### 2.3 Referencias al literal
- `CONFIRMED`: **0** instrucciones `l32r` apuntan a `0x00980f8c` en OpenWrt.
- `CONFIRMED`: **0** referencias también en los tres contenedores de airOS (`0x00980eec` en `ptmp_ap`/`ptmp_sta` y `0x00980ec4` en `ptp`).
- `CONFIRMED`: la ventana de 100 B alrededor del literal (`0x00980f5c`…) contiene **18 de 25** palabras que parecen punteros (`0x0040xxxx`/`0x0098xxxx`).
- `INFERRED`: el literal es **dato de un pool** en IRAM, no un operando de despacho. El rótulo “WMI opcode” para `0x9044` en este firmware queda **sin probar**.
- `REFUTED`: la hipótesis de que `0x9044` se consuma por un despacho `l32r`+salto en cualquiera de las dos familias.

### 2.4 Ancho de canal sin la tabla PLL de airOS
- `CONFIRMED`: la tabla de 20 MHz `0c1218243048606c` aparece **1 vez**, en **`0x0040b768`** (IE3 segmento 1).
- `CONFIRMED`: se enumeran **42** tablas candidatas de 8 bytes estrictamente ascendentes.
- `CONFIRMED`: **3** de ellas son referenciadas por una instrucción `l32r`:
  - `0x0040b5f0` ← instrucción `0x0040b1e3` (IE4 segmento 2),
  - `0x0040b804` ← instrucción `0x0040b67a` (IE4 segmento 2),
  - `0x0040c8c4` ← instrucción `0x0040c0c3` (IE3 segmento 2).
- `CONFIRMED`: se descarta **1** falso positivo autoresferencial en `0x0040c064`, donde la instrucción coincidía con la dirección de su propia tabla.
- `INFERRED`: el firmware usa tablas de tasas indexadas por código, de modo que el reloj se deriva de una tabla de tasas y no de la tabla de divisores sub-20 MHz de airOS.
- `UNKNOWN`: la ruta exacta de 5/10 MHz. Ninguna tabla se ata todavía a un conmutador de ancho, y la tabla PLL de airOS sigue ausente (`REFUTED` en `1567A` y re-medida aquí).

## 3. Stage 1595A — compuerta de la Wave 92
- La compuerta ejecuta, además de sus comprobaciones, `tools/verify/enforce_5pillar_research_gate.py` sobre **los dos recibos** y exige `compliant = true`.
- Se ejecuta dos veces (medición y confirmación) y no lee el veredicto del fichero que escribe.

## 4. Lo que queda abierto
- `UNKNOWN`: productor de BPS/SCORE/RATING; la función auditada no los toca.
- `UNKNOWN`: papel real del literal `0x9044`; está en un pool y ninguna `l32r` lo referencia.
- `UNKNOWN`: ruta de 5/10 MHz en OpenWrt, sin tabla de divisores y sin tabla atada al conmutador.
- `UNKNOWN`: `$gp` de `ubntspecd`, subdeterminado por dos únicos sitios indirectos.

## 5. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1590A` | `tools/re/dissect_stage1590a_ubntspecd_func_4073b0_and_188b_producer_trace.py` + `artifacts/autoresearch/stage1590a_..._producer_trace.json` |
| `1591A` | `tools/re/dissect_stage1591a_openwrt_fw2_wmi9044_target_and_chanbw.py` + `artifacts/autoresearch/stage1591a_..._dissection.json` |
| `1592A` | este documento (menos de 200 líneas, 1 `doc-head`, 0 signos de exclamación en prosa) |
| `1593A..1595A` | `tests/test_stage1590a_to_1595a_suite.py` y `tools/verify/verify_stage1595a_wave92_opencode_5pillar_gate.py` con su recibo |

## 6. Correcciones que esta wave aporta
- Wave 90 decía que `0x00407a44` era un segundo stride de 188: **era un falso positivo**.
- Wave 90 trataba el literal `0x9044` como opcode de despacho: en las dos familias **ninguna `l32r` lo referencia** y su ventana es un pool de punteros.
