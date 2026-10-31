<!-- doc-head -->
*STAGE1958A — Resolución GOT/lo16 de los offsets athstats y tabla completa WA/XC*
# STAGE 1958A — Offsets athstats resueltos

## 0. Frontera
- **Cero SSH y cero escrituras a radio**: `ssh_connections=0`, `radio_writes=0`, `executable=0` en los tres recibos.
- Análisis estático sobre `athbox` y los recibos de la Wave 150. No se ejecutó nada y no hubo red.
- Este documento no contiene apellidos.

## 1. Stage 1956A — la hipótesis GOT/lo16 era correcta
- `CONFIRMED`: el código PIC construye el puntero de formato como **página + mitad baja**. Los dos anclajes aparecen exactamente donde se predijo:
  - `addiu a1,a1,0x77dc` en **0x403ea4** → etiqueta `no tx buffer` en 0x4177dc.
  - `addiu a1,a1,0x78cc` en **0x403e2c** → etiqueta `xmit filtered` en 0x4178cc.
- `CONFIRMED`: la página es **0x410000** para el bloque heredado y **0x420000** para el bloque `ast_*`.
- `CONFIRMED`: la función arranca en **0x401890** con marco de **0x2640** bytes.
- `CONFIRMED`: el literal de tamaño del ioctl es **0x1210** (4624) en **0x402490**.
- `CONFIRMED`: la cadena de impresión condicional tiene **32** contadores: cada uno se carga con `lw a2,N(sp)`, se prueba con `bne a2,zero` y se imprime desde `página+mitad_baja`.
- `CONFIRMED`: se resolvieron **8 de 8** etiquetas sin ambigüedad.
- `CONFIRMED`: el prefijo de marco es **0x48**, probado dos veces: `0xfc - 0xb4 = 0x48` y `0x124 - 0xdc = 0x48`.

## 2. Stage 1956A — tabla resuelta
| Etiqueta | Offset de marco | Offset de buffer | Estado |
| :--- | ---: | ---: | :--- |
| `no_tx_buffer` | 0xfc | **0xb4** | `CONFIRMED` |
| `xmit_filtered` | 0x124 | **0xdc** | `CONFIRMED` |
| `ast_tx_nobuf` | 0x13a0 | 0x1358 | `INFERRED` |
| `ast_tx_xretries` | 0x13c0 | 0x1378 | `INFERRED` |
| `ast_be_nobuf` | 0x1468 | 0x1420 | `INFERRED` |
| `ast_tx_buf_count` | 0x146c | 0x1424 | `INFERRED` |
| `ast_tx_mgmt` | 0x1478 | 0x1430 | `INFERRED` |
| `ast_tx_packets` | 0x147c | 0x1434 | `INFERRED` |

- `INFERRED`: los seis `ast_*` comparten el prefijo 0x48 medido en las dos etiquetas heredadas. El prefijo está probado solo para el bloque heredado.

## 3. Stage 1957A — la consecuencia incómoda
- `CONFIRMED`: `no_tx_buffer` (**0xb4**) y `xmit_filtered` (**0xdc**) caen **dentro** de los 4624 bytes que copia el ioctl. Son offsets de bytes confirmados y coinciden con los que usó la telemetría en vivo.
- `REFUTED`: que las ocho etiquetas provengan de **una sola** respuesta de 4624 bytes. Los seis `ast_*` resuelven entre **0x1358** y **0x1434**, es decir **más allá** del final de la copia.
- `INFERRED`: si el prefijo 0x48 se mantiene en ese bloque, los seis necesitan un buffer mayor o un segundo ioctl.
- `UNKNOWN`: el nombre de miembro del kernel de cualquiera de las ocho filas. El cuerpo del caso no nombra ningún miembro y no se inventó ninguno.
- `CONFIRMED`: la actualización de la Stage 1939A es **PARTIAL**: dos offsets pasan a confirmados y seis quedan inferidos fuera de rango.

## 4. Lo que esto cambia en la práctica
- La lectura de 0xb4 y 0xdc como pérdidas de buffer **no** era un error de offset: el applet imprime exactamente esos bytes. El problema es qué contadores escribe el kernel allí, que sigue en `UNKNOWN`.
- Los contadores verdaderos (`ast_*`) **no** están donde se suponía: quedan fuera de la copia de 4624 bytes que se midió.
- Un decodificador correcto debe usar el número de ioctl y el tamaño real del buffer del que venga cada bloque, no un único tamaño global.

## 5. Stage 1959A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos con `scope=project:futuramax`.
- `CONFIRMED`: la lectura de ida y vuelta devolvió los **3** con estado `candidate`.

## 6. Lo que no se prueba
- `UNKNOWN`: el miembro del kernel en cada uno de los ocho offsets.
- `UNKNOWN`: qué ioctl o buffer sirve los seis `ast_*`.
- `UNKNOWN`: si el prefijo 0x48 vale también para el bloque `ast_*`.
- `UNKNOWN`: cualquier lectura en vivo.

## 7. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1956A` | `tools/re/extract_stage1956a_athbox_got_lo16_print_block_dissection_re.py` y su recibo |
| `1957A` | `tools/re/reconcile_stage1957a_complete_siocgathstats_offset_table.py` y su recibo |
| `1959A` | `tools/verify/record_stage1959a_memorymaster_ingest.py` y su recibo |
| `1960A` | `tests/test_stage1956a_to_1961a_suite.py` |
| `1961A` | `tools/verify/verify_stage1961a_wave153_opencode_gate.py` y la compuerta de la wave |
