<!-- doc-head -->
*STAGE1646A — productor signed-16 en ubntspecd y llamadores Xtensa de PB050, tasa e IRAM*
# STAGE 1646A — Signed-16 y llamadores Xtensa

## 0. Método
- **100% estático y offline**. Sin SSH, sin escrituras bajo `firmware/`.
- Etiquetas: `CONFIRMED`, `INFERRED`, `UNKNOWN`, `REFUTED`.

## 1. Stage 1644A — buscador de almacenes signed-16
- `CONFIRMED`: se rastrean **35** constructores `lui 0x0005/0x0006` por binario con propagación afín y **slots de pila** (para sobrevivir al derrame de GCC), y **759** almacenes.
- `CONFIRMED`: con la forma `base 32 bits + imm16 con signo`, la banda `0x4971c..0x6eb1c` recibe **18** almacenes en WA y **18** en XC.
- `CONFIRMED`: esos 18 caen en `0x4cabc`, `0x4cac0`, `0x4cac4` y `0x4cace`, todos dentro de la función **`0x00400f80`**: son punteros de tabla, no los campos por-STA.
- `CONFIRMED`: **0** almacenes exactos a `0x4971c`, `0x55f1c` o `0x6271c` en ambos binarios.
- `REFUTED`: que exista un almacén por campo en la ventana; el productor **no** está en estos binarios.
- `INFERRED`: los tres valores llegan ya calculados, coherente con las importaciones de ingesta (`fread`, `ioctl`, `memcpy`, `recvmsg`) medidas en `1633A`.

## 2. Stage 1645A — llamadores Xtensa de los tres literales
- `CONFIRMED`: el modelo absoluto `LITBASE = 0x009bb000` con `destino = LITBASE + (imm16 − 0x10000) × 4` localiza exactamente los llamadores esperados, **3 de 3 objetivos**:

| Objetivo | OpenWrt | airOS | Instrucciones OpenWrt | Instrucciones airOS |
| :--- | :--- | :--- | :--- | :--- |
| PB050 RC `0x00980754` | **1** | **3** | `0x0098e3c7` | `0x0098b18b` ×3 |
| Slot de tasas `0x00980dd4` | **1** | **3** | `0x009a26de` | `0x009a2d01`, `0x009a2d2d`, `0x009a30f5` |
| Dword IRAM `0x00980030` | **15** | **7** | `0x00983cc5`, `0x00983c87`, `0x0098444c`, … | `0x00983c9b`, `0x009a3fe3`, … |

- `CONFIRMED`: cada llamador es una instrucción `l32r` cuya aritmética absoluta iguala el literal; la coincidencia es una identidad, no un patrón.
- `CONFIRMED`: el dword IRAM `0x00980030` es el literal **más referenciado** de los tres (15 en OpenWrt, 7 en airOS), lo que lo sitúa como punto caliente de configuración.
- `UNKNOWN`: el flujo de control alrededor de cada llamador. La ventana de bytes decodifica **solo** `l32r` y cuenta el resto; no se implementa un decodificador de longitud de instrucción ni de límites de función, así que no se nombran funciones Xtensa.
- `REFUTED`: atribuir a estos llamadores una función concreta sin ese decodificador; el recibo reporta instrucción + ventana, no una decompilación completa.

## 3. Stage 1649A — compuerta
- Corre `enforce_5pillar_research_gate.py` sobre los dos recibos y exige `compliant = true`.
- Se ejecuta dos veces (medición y confirmación).

## 4. Abierto
- `UNKNOWN`: productor real de `STA_DEMOD_BPS`, `STA_SPECTRAL_SCORE`, `STA_LINK_RATING`.
- `UNKNOWN`: semántica de los 15+7 llamadores del dword IRAM.
- `UNKNOWN`: relación entre el slot `0x00980dd4` y la tabla de 20 MHz `0x0040b768`, que sigue sin referencia `l32r` directa.

## 5. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1644A` | `tools/re/dissect_stage1644a_ubntspecd_signed16_0x50000_producer_stores.py` + recibo |
| `1645A` | `tools/re/dissect_stage1645a_xtensa_callers_of_980754_980dd4_980030.py` + recibo |
| `1646A` | este documento (menos de 180 líneas, 1 `doc-head`, 0 signos de exclamación en prosa) |
| `1647A..1649A` | `tests/test_stage1644a_to_1649a_suite.py` y `tools/verify/verify_stage1649a_wave101_opencode_5pillar_gate.py` |
