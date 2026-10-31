<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head -->
*STAGE1580A — auditoria COP1/stride-188 en ubntspecd y parcheador determinista SGMT para firmware-2.bin de OpenWrt ath10k-ct*
# STAGE 1580A — COP1 y stride 188 en `ubntspecd`, y parcheador SGMT de `firmware-2.bin`

## 0. Método y límites
- **100% estático y offline**: se leen ELF y contenedores ya presentes en el repo. Sin SSH, sin carga de módulos y sin escribir nada bajo `firmware/openwrt`.
- Etiquetas: `CONFIRMED` (bytes medidos), `INFERRED`, `UNKNOWN`, `REFUTED`.
- Toda cifra de este documento proviene de los recibos de las etapas; los hashes exactos del contenedor parcheado viven en el recibo de `1579A`, no se copian aquí a mano.

## 1. Stage 1578A — censo COP1 y auditoría del stride 188
### 1.1 Versiones pedidas
- `REFUTED`: **no existen** las builds `WA 8.7.19` ni `XC 8.7.15` en el repositorio: **0 rutas** coinciden con `8.7.19`, `8.7.15`, `8719` o `8715` tras excluir los directorios con nombre de hash de 64 caracteres.
- `CONFIRMED`: la auditoría corre sobre los tres daemons que sí existen — `ubntspecd` de **WA 8.7.25**, **XC 8.7.25** y **XC 8.7.4cs** — y cada entrada del recibo declara su versión real.

### 1.2 Las 29 palabras con opcode `0x11`
- `CONFIRMED`: los tres binarios tienen **29** palabras con opcode `0x11` en el segmento ejecutable, en las **mismas 29 direcciones virtuales**.
- `CONFIRMED`: de esas 29, solo **3** decodifican a un mnemónico COP1 definido por MIPS32: `cfc1` en `0x0040a9c0`, `cfc1` en `0x0040a9f4` y `add.s` en `0x0040ab70`.
- `CONFIRMED`: las otras **26** llevan formatos **fuera del conjunto definido** (`0x01, 0x03, 0x09, 0x0a, 0x0b, 0x12, 0x13, 0x19, 0x1a, 0x1b`) y forman **2 grupos adyacentes** (`0x00408938`–`0x0040893c` y `0x0040a9d8`–`0x0040a9dc`).
- `INFERRED`: esa combinación —formatos inválidos y pares contiguos— es la firma de **datos embebidos en `.text`** (pools o tablas), no de instrucciones.
- `REFUTED`: la afirmación de la Wave 88 de que había “29 instrucciones COP1 de punto flotante”. El número correcto es **3 instrucciones estándar** y 26 palabras no decodificables como instrucción.
- `CONFIRMED`: **0** de las 29 resulta ser un `mtc1` alimentado por una constante entera, así que no hay “constantes float” que extraer por esa vía.

### 1.3 Índice por stride 188 (`0xbc`)
- `CONFIRMED`: el idioma `((s<<6) - (s<<4) - s) << 2` aparece **2 veces** en WA y **2** en XC, en las mismas direcciones: `0x00407a44`–`0x00407a7c` dentro de la función `0x004073b0`, y `0x00407f3c`–`0x00407f64` dentro de la función `0x00407db8`.
- `CONFIRMED`: no hay ninguna multiplicación por `0xbc` (`mult` con constante 188): el compilador usa el idioma de desplazamientos y restas.
- `INFERRED`: la segunda ocurrencia es la que calcula el índice de STA del bucle de impresión; la primera pertenece a la función previa que prepara o recorre la misma lista.

### 1.4 Los tres campos por-STA
- `CONFIRMED`: en WA hay **7 lecturas** con desplazamiento literal a los tres campos — `BPS` `0x971c` (2), `SCORE` `0x5f1c` (2), `RATING` `0x271c` (3) — y **las 7 están dentro de la misma función `0x00407db8`**.
- `CONFIRMED`: **0 escrituras** con desplazamiento literal a esos tres offsets en los tres binarios.
- `INFERRED`: el bucle de impresión solo consume campos ya calculados; el cálculo ocurre en otro punto y se escribe mediante un puntero calculado o una copia en bloque, que un escaneo por desplazamiento literal no puede ver.
- `UNKNOWN`: los pesos y la combinación que producen los tres valores.

## 2. Stage 1579A — parcheador determinista de `firmware-2.bin`
### 2.1 Identidad y geometría
- `CONFIRMED`: `firmware-2.bin` mide **204.796 B**, SHA-256 `398e4380e7e55105f3da0f78af29d1e437404ed3a82597aa4b6daaa7dce1a38e`, idéntico en las 4 imágenes WA.
- `CONFIRMED`: tabla de IE en `0x0c` con 6 registros; **IE4** de 7.140 B en `0x6c` e **IE3** de **197.537 B** en `0x1c58`.
- `CONFIRMED`: cada IE contiene un contenedor SGMT con **4 segmentos**, entry point `0x00983c00`, destinos `0x00980000`, `0x0040b000`, `0x0040b1a0`/`0x0040bd10` y `0x00983c00`.

### 2.2 Qué parchea la herramienta
- **CCA (PB040-CCA-AGC-OVERRIDE)**: en **IE3, segmento 3**, offset **`0x33984`** (vaddr **`0x009b7584`**), preimagen de 16 B `009e0200a016721320137213109e0200` y reemplazo `009e0200a016721320137613109e0200`: cambia **un solo byte**, el índice **10** (`0x72 → 0x76`). La preimagen se verifica y el proceso falla cerrado si no coincide.
- **Canario seguro en `.rodata` de IE3**: se elige una cadena de depuración imprimible de al menos 8 caracteres y se cambia **una sola letra** de caja. El canario prueba que el firmware acepta un stream SGMT modificado sin tocar instrucciones, tablas numéricas ni nodos de dispositivo.
- **WMI 0x9044**: se **verifica y se reporta sin parchear**. El literal de 32 bits vive en **IE3, segmento 0**, offset **`0xf8c`** (vaddr **`0x00980f8c`**). No se parchea porque no hay un alias canónico demostrado para este build; inventar uno violaría la regla de no fabricar.

### 2.3 Invariantes que la herramienta demuestra
- `CONFIRMED`: recomprime con `bmi_lz_compress` y valida `bmi_lz_decompress(recompressed, tamaño) == bytes_mutados`, **bit a bit**.
- `CONFIRMED`: tras reconstruir el contenedor y reparsearlo, el entry point, el número de segmentos, los destinos y los tamaños decodificados se conservan, **todos los segmentos no mutados son byte-idénticos** y el segmento mutado difiere **solo** en los bytes documentados.
- `CONFIRMED`: el `firmware-2.bin` reconstruido se escribe **solo** bajo `artifacts/autoresearch/stage1579a/`; nunca sobre la imagen. `firmware_written_to_repo = 0`.
- `UNKNOWN`: si la radio acepta el contenedor parcheado. Eso es exactamente lo que el Carril 1 debe probar en vivo sobre `.20` ↔ `198.18.0.67`.

### 2.4 Auditoría de tablas de canal/PLL en IE3
- `CONFIRMED`: se escanean los 4 segmentos de IE3 completos y se cuenta, por segmento, el patrón de divisores sub-20 MHz `060c121824303600`, el payload CCA de 16 B y el dword little-endian `0x00029e00`.
- `REFUTED` (heredado de `1567A` y re-medido aquí): el patrón PLL de airOS **no aparece** en `firmware-2.bin`; la ruta de 5/10 MHz de OpenWrt no se resuelve copiando esa tabla.
- `CONFIRMED`: el recibo declara los bytes escaneados por segmento, de modo que un cero es un cero medido y no un escaneo vacío.

## 3. Stage 1583A — compuerta de la Wave 90
- La compuerta corre, además de sus propias verificaciones, la compuerta de 5 pilares del proyecto (`tools/verify/enforce_5pillar_research_gate.py`) **sobre los dos recibos** y exige `compliant = true` en ambos.
- Un recibo que no cumpla los 5 pilares hace fallar la wave aunque el resto pase. El veredicto y el detalle por pilar quedan en `artifacts/verification/stage1583a_wave90_opencode_5pillar_gate.json`.
- La compuerta se ejecuta dos veces (medición y confirmación) para probar que es repetible, y no lee el veredicto del fichero que está escribiendo.

## 4. Lo que queda abierto
- `UNKNOWN`: la aritmética y los pesos de BPS/SCORE/RATING; el cálculo no usa desplazamiento literal y no se alcanza con este método.
- `UNKNOWN`: si el contenedor parcheado es aceptado por la radio, y con qué efecto en CCA/AGC.
- `UNKNOWN`: la ruta de 5/10 MHz en OpenWrt, sin tabla PLL en `firmware-2.bin`.
- `UNKNOWN`: destino de salto del despacho WMI `0x9044` en ambas familias.
- `REFUTED`: las builds 8.7.19 y 8.7.15 no están disponibles localmente, así que no hay delta por versión.

## 5. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1578A` | `tools/re/dissect_stage1578a_ubntspecd_cop1_float_and_188b_stride.py` + `artifacts/autoresearch/stage1578a_opencode_fullrea_ubntspecd_cop1_float_and_188b_stride_audit.json` |
| `1579A` | `tools/re/patch_openwrt_ath10k_ct_firmware2_sgmt.py` + `artifacts/autoresearch/stage1579a_opencode_fullrea_openwrt_firmware2_patcher_and_ie3_audit.json` + contenedor parcheado bajo `artifacts/autoresearch/stage1579a/` |
| `1580A` | este documento (menos de 200 líneas, 1 `doc-head`, 0 signos de exclamación) |
| `1581A..1583A` | `tests/test_stage1578a_to_1583a_suite.py` y `tools/verify/verify_stage1583a_wave90_opencode_5pillar_gate.py` con su recibo |

## 6. Nota de corrección
- Este documento corrige la Wave 88 en dos puntos: no hay 29 instrucciones COP1 (hay 3 estándar y 26 palabras que son datos), y las constantes float no se obtienen por `mtc1` porque no existe ninguna.
