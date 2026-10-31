<!-- doc-head -->
*STAGE1634A — callgraph LITBASE/wsr en firmware-2.bin y traza del array de 188 B en ubntspecd*
# STAGE 1634A — LITBASE, `wsr` y el productor de 188 B

## 0. Método
- **100% estático y offline**. Sin SSH y sin escribir bajo `firmware/`.
- Etiquetas: `CONFIRMED`, `INFERRED`, `UNKNOWN`, `REFUTED`.

## 1. Stage 1632A — callgraph absoluto con LITBASE
### 1.1 Modelo y validación
- `CONFIRMED`: `l32r` direcciona de forma absoluta: `destino = 0x009bb000 + (imm16 − 0x10000) × 4`.
- `CONFIRMED`: el modelo se valida por **triple coincidencia** independiente, no por convención:
  - OpenWrt `0x00980f8c`: **1** referencia,
  - airOS `ptmp` `0x00980eec`: **3** referencias,
  - airOS `ptp` `0x00980ec4`: **3** referencias.
- `CONFIRMED`: se evalúa además la alternativa relativa al PC sobre las mismas instrucciones y **no** reproduce esos destinos, lo que discrimina los dos modelos.

### 1.2 Cobertura
- `CONFIRMED`: 8 segmentos de OpenWrt (IE3+IE4) y 12 segmentos de los tres contenedores de airOS, con **86.523** candidatos `l32r` y **86.523** instrucciones evaluadas.
- `CONFIRMED`: `firmware-2.bin` = 204.796 B, SHA-256 `398e4380e7e55105…`.
- `REFUTED`: airOS **no** distribuye `firmware-2.bin`; sus contenedores viven dentro de `umac.ko`, que es lo que se escanea.

### 1.3 Resultado por objetivo
| Objetivo | OpenWrt | airOS |
| :--- | :--- | :--- |
| CCA `0x009b7584` | **0** | **0** |
| Dword IRAM `0x00980030` | **15** | **7** |
| PB050 RC `0x00980754` | **1** | **3** |
| PB050 dato `0x0040c140` | **0** | **0** |
| Slot de tasas `0x00980dd4` | **1** | **3** |
| Tabla 20 MHz `0x0040b768` | **0** | **0** |
| Tablas `0x0040b5f0`, `0x0040b804`, `0x0040c8c4` | **0** | **0** |

- `CONFIRMED`: 3 de 9 objetivos tienen referencia. El bloque CCA **no** se carga con `l32r`: se alcanza de otra forma.
- `CONFIRMED`: el slot `0x00980dd4` sí tiene una referencia (`1` en OpenWrt, `3` en airOS), así que la tabla de 20 MHz se alcanza **por puntero**, no directamente.

### 1.4 `wsr` y LITBASE dinámico
- `CONFIRMED`: **0** instrucciones candidatas con opcode `0x13` (familia `wsr`) en los 20 segmentos.
- `INFERRED`: LITBASE es **estático** en estas imágenes, así que las direcciones absolutas calculadas arriba son válidas para todo el binario.
- `UNKNOWN`: el mapeo campo `sr` → LITBASE exigiría la tabla del ISA, que no está en el repositorio.

## 2. Stage 1633A — el array de 188 B en `ubntspecd`
### 2.1 Forma real de acceso
- `CONFIRMED`: los tres campos **no** se direccionan con un desplazamiento de 16 bits (no caben). La forma medida es **base de 32 bits + desplazamiento con signo**:
  - `BPS`: base `0x00050000`, desplazamiento `−26852` → efectivo `0x4971c`,
  - `SCORE`: base `0x00050000`, desplazamiento `24348` → efectivo `0x55f1c`,
  - `RATING`: base `0x00060000`, desplazamiento `10012` → efectivo `0x6271c`.
- `REFUTED`: la hipótesis de una base en la banda `0x48000..0x4a000`. El escaneo de constructores en esa banda devuelve **0** en WA y **0** en XC.
- `CONFIRMED`: el detector estricto del idioma `((s<<6) − (s<<4) − s) << 2` devuelve **0** sitios y **0** multiplicaciones por `0xbc` en ambos binarios; el único sitio genuino conocido (`0x00407f3c`, medido en `1578A`) queda fuera de su ventana, lo que se declara como limitación del detector y no como ausencia.

### 2.2 Ingesta desde el kernel o desde la red
- `CONFIRMED`: la tabla de símbolos dinámicos expone importaciones de ingesta: **`fread`, `ioctl`, `memcpy`, `recvmsg`**.
- `CONFIRMED`: hay **5** llamadas indirectas por `$t9` en WA y **5** en XC.
- `INFERRED`: un buffer llenado por `ioctl` o `recvmsg` explica la ausencia total de almacenes por campo: los valores llegan ya calculados.
- `UNKNOWN`: qué llamada concreta llena la estructura, porque atribuir un `jalr $t9` a una importación exige el valor de `$gp`, que sigue subdeterminado.
- `UNKNOWN`: el productor del array de 188 B; no está en el espacio de usuario auditado.

## 3. Stage 1637A — compuerta
- Corre `tools/verify/enforce_5pillar_research_gate.py` sobre **los dos recibos** y exige `compliant = true`.
- Se ejecuta dos veces (medición y confirmación).

## 4. Lo que queda abierto
- `UNKNOWN`: cómo se alcanza el bloque CCA sin `l32r`.
- `UNKNOWN`: productor real de BPS/SCORE/RATING.
- `UNKNOWN`: mapeo `sr`→LITBASE y atribución de las llamadas `$t9`.

## 5. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1632A` | `tools/re/dissect_stage1632a_litbase_wsr_and_full_ie3_ie4_l32r_callgraph.py` + recibo |
| `1633A` | `tools/re/dissect_stage1633a_ubntspecd_188b_stride_and_kernel_ingest.py` + recibo |
| `1634A` | este documento (menos de 180 líneas, 1 `doc-head`, 0 signos de exclamación en prosa) |
| `1635A..1637A` | `tests/test_stage1632a_to_1637a_suite.py` y `tools/verify/verify_stage1637a_wave99_opencode_5pillar_gate.py` |
