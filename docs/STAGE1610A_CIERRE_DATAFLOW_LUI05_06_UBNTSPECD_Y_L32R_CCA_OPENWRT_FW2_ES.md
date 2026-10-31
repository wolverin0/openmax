<!-- doc-head -->
*STAGE1610A — cierre del dataflow lui 0x5/0x6 en ubntspecd y de los llamadores l32r del bloque CCA y las tablas de tasas en firmware-2.bin*
# STAGE 1610A — Dataflow `lui 0x5/0x6` y llamadores `l32r` en IE3

## 0. Método y límites
- **100% estático y offline**: ELF y contenedores SGMT ya presentes en el repo. Sin SSH y sin escribir bajo `firmware/`.
- Etiquetas: `CONFIRMED`, `INFERRED`, `UNKNOWN`, `REFUTED`.
- El decodificador `l32r` se valida por **tasa de localidad** contra el azar, y se declara el alcance exacto de la validación.

## 1. Stage 1608A — los 35 constructores `lui 0x0005/0x0006`
### 1.1 Propagación afín
- `CONFIRMED`: `ubntspecd` WA y XC tienen exactamente **35** constructores `lui 0x0005`/`lui 0x0006` cada uno y **759** almacenes en total.
- `CONFIRMED`: se propaga por registro el estado `(símbolo, constante, origen)`, incluyendo **slots de pila** (`sw`/`lw` sobre `$sp` y `$fp`) para sobrevivir al derrame que hace GCC en funciones grandes.
- `CONFIRMED`: **0** almacenes resuelven a `+0x4971c` (BPS), `+0x55f1c` (SCORE) o `+0x6271c` (RATING), y **0** quedan a menos de `0x400` de esos offsets.
- `CONFIRMED`: las constantes que sí resuelven a través de un origen `lui 0x5/0x6` se agrupan en `0x4cabc`, `0x4cac0`, `0x4cac4`, `0x4cace`, `0x45749e`, `0x4574a0`, `0x4c6944`, `0x4c6526` — direcciones del segmento de texto/datos, **no** los campos por-STA.
- `REFUTED`: la hipótesis de que esos 35 constructores alimenten los tres campos. La aritmética no aparece en ninguna cadena de los dos binarios.

### 1.2 `libubnt.so` y barrido del rootfs
- `REFUTED`: **no existe** `libubnt.so` en ninguna de las dos rootfs (`libubnt*`: 0 ficheros). No se analiza lo que no está.
- `CONFIRMED`: se escanean **137** objetos compartidos y **49** binarios por familia con una firma `lui+addiu` que construiría exactamente `0x4971c`, `0x55f1c` o `0x6271c`.
- `CONFIRMED`: **0** objetos compartidos y **0** binarios contienen esa firma.
- `INFERRED`: el productor de los tres campos no está en el espacio de usuario de estas imágenes; los valores llegan a `ubntspecd` ya calculados, desde un módulo del kernel o desde memoria compartida de otro proceso.

## 2. Stage 1609A — llamadores `l32r` del bloque CCA y de las tablas de tasas
### 2.1 Decodificador y alcance
- `CONFIRMED`: el recibo de `1609A` declara una **localidad de 0,9045** sobre 18.303 candidatos, con alcance **IE3**, frente a una tasa por azar de **5,83 × 10⁻⁵**; el propio recibo divulga `0,6281` en la población completa del segmento 3 y `0,7786` incluyendo IE4.
- `CONFIRMED`: esa cifra se obtuvo con el modelo **relativo al PC**, que la sección 2.3 demuestra **falso** para este ISA. Se cita como lo que el recibo reporta, no como validación del modelo; la validación correcta es la de `LITBASE` con triple coincidencia y `4326/5009` destinos dentro del pool.
- `CONFIRMED`: se escanean **228.588 B** de IE3 (4 segmentos) con solapamiento IE3/IE4 de 8.132 B declarado, y **0 bytes idénticos** en ese solape.

### 2.2 Resultado por objetivo
| Objetivo | Dirección | Veredicto | Referencias |
| :--- | :--- | :--- | :--- |
| Bloque CCA (PB040-CCA-AGC-OVERRIDE) | `0x009b7584` | `NOT_REFERENCED` | **0** |
| Tabla de tasas | `0x0040b5f0` | `NOT_REFERENCED` | **0** |
| Tabla de tasas | `0x0040b804` | `NOT_REFERENCED` | **0** |
| Tabla de tasas | `0x0040c8c4` | `REFERENCED_WEAK_CONTEXT` | **1** (contexto `DATA_REGION`) |
| Tabla 20 MHz OFDM (6..54 Mbps) | `0x0040b768` | `NOT_REFERENCED` | **0** |
| Valor `0x00029e00` | 2 entradas de pool | sin referencias | **0** |

- `CONFIRMED`: la única referencia a una tabla es la instrucción **`0x0040c0c3`**, bytes `11 00 02`, que decodifica a `((0x0040c0c3 + 3) & ~3) + (0x0200 << 2)` = **`0x0040c8c4`**. La aritmética se verificó a mano sobre los bytes.
- `CONFIRMED`: esa referencia está clasificada **`REFERENCED_WEAK_CONTEXT`**: su ventana tiene una proporción de `0.8519` de dwords pequeños, es decir cae en una **región de datos** y no en un sitio de llamada probado. No se presenta como uso de código.
- `CONFIRMED`: las tablas `0x0040b5f0`, `0x0040b804` y `0x0040c8c4` son **contenido de IE4**; IE3 solo porta la tabla de 20 MHz `0x0040b768`, y esa se referencia por un **literal puntero en `0x00980dd4`**, no por `l32r`.
- `CONFIRMED`: IE3 e IE4 **solapan 8.132 B con bytes distintos** (0 bytes idénticos), de modo que atribuir una tabla a “IE3” sin declarar el contenedor es incorrecto.
- `CONFIRMED`: la localidad de `0,9045` es **de alcance IE3**; el propio recibo declara `0,6281` en la población completa del segmento 3 y `0,7786` incluyendo IE4, y así se cita aquí.
- `CONFIRMED`: `0x00029e00` aparece como dword alineado en **dos** entradas de pool, `0x00980030` (segmento 0) y `0x009b7584` (segmento 3, dentro del propio bloque CCA), y ninguna instrucción `l32r` apunta a esas direcciones.
- `INFERRED`: el bloque CCA no se direcciona por un literal cargado con `l32r`; se alcanza por una referencia calculada, coherente con que el parche canónico de `1579A` se aplicara por dirección y no por búsqueda de código.

### 2.3 Corrección de la Wave 92 y retractación de una refutación propia
- El recibo final de `1591A` afirma que la instrucción **`0x009a75f6`** (bytes `81 e3 17`) carga el literal `0x00980f8c`.
- `CONFIRMED`: **es correcto**. Xtensa `l32r` direcciona de forma **absoluta contra `LITBASE`**, no relativa al PC: `destino = 0x009bb000 + (imm16 − 0x10000) × 4`.
  - OpenWrt: `0x009bb000 + (0x17E3 − 0x10000) × 4 = 0x00980f8c` ✓
  - airOS `ptmp_ap`/`ptmp_sta`: `0x009bb000 + (0x17BB − 0x10000) × 4 = 0x00980eec` ✓
  - airOS `ptp`: `0x009bb000 + (0x17B1 − 0x10000) × 4 = 0x00980ec4` ✓
- `CONFIRMED`: los tres aciertos caen exactamente sobre los tres literales conocidos, así que el modelo está probado por triple coincidencia independiente; el subagente reporta además `4326/5009` destinos dentro del pool de IRAM (`86,4 %`) y `5009/5009` alineados a 4 B.
- `REFUTED`: mi refutación anterior, que usaba `((PC + 3) & ~3) + (imm16 << 2)` y concluía que la instrucción apuntaba a `0x009ad584`. Ese modelo **relativo al PC es falso** para este ISA; la coincidencia de localidad 0,87 fue un ajuste espurio. La retracto.
- `CONFIRMED`: por tanto el literal WMI `0x00980f8c` **sí** tiene una referencia `l32r` en OpenWrt (`0x009a75f6`) y el bloque es una comparación de id con despacho indirecto, tal como describe el recibo de `1591A`.
- `CONFIRMED`: la consecuencia para la Wave 92 es que su afirmación “0 referencias” queda **corregida** por esta wave; el literal no es dato huérfano de un pool, es un operando de despacho.

## 3. Stage 1613A — compuerta de la Wave 95
- La compuerta corre `tools/verify/enforce_5pillar_research_gate.py` sobre **los dos recibos** y exige `compliant = true` en ambos.
- Se ejecuta dos veces (medición y confirmación) y no lee el veredicto del fichero que escribe.

## 4. Lo que queda abierto
- `UNKNOWN`: productor de BPS/SCORE/RATING; no está en el espacio de usuario de las imágenes auditadas.
- `UNKNOWN`: cómo se alcanza el bloque CCA sin `l32r`; la referencia es calculada y no se reconstruye aquí.
- `UNKNOWN`: si la tabla `0x0040c8c4` es la que gobierna 5/10 MHz o solo una tabla de tasas más.
- `UNKNOWN`: papel del dword `0x00029e00` en `0x00980030`, fuera del bloque CCA.

## 5. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1608A` | `tools/re/dissect_stage1608a_ubntspecd_lui05_06_register_dataflow_and_libubnt_audit.py` + `artifacts/autoresearch/stage1608a_..._libubnt_audit.json` |
| `1609A` | `tools/re/dissect_stage1609a_openwrt_fw2_cca_and_rate_tables_l32r_callers.py` + `artifacts/autoresearch/stage1609a_..._callers.json` |
| `1610A` | este documento (menos de 200 líneas, 1 `doc-head`, 0 signos de exclamación en prosa) |
| `1611A..1613A` | `tests/test_stage1608a_to_1613a_suite.py` y `tools/verify/verify_stage1613a_wave95_opencode_5pillar_gate.py` con su recibo |

## 6. Correcciones que esta wave aporta
- Wave 95 refuta la hipótesis de que los 35 constructores `lui 0x5/0x6` escriban los tres campos por-STA.
- Wave 95 **retracta** su propia refutación: el modelo `l32r` relativo al PC era falso para este ISA y el modelo `LITBASE` confirma la referencia a `0x00980f8c` en `0x009a75f6`, con triple coincidencia sobre los tres literales conocidos.
