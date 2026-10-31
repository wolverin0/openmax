<!-- doc-head -->
*STAGE1970A — Mapa multi-ioctl del marco 0x2640 de athbox en WA y XC*
# STAGE 1970A — Dos buffers, no uno

## 0. Frontera
- **Cero SSH y cero escrituras a radio**: `ssh_connections=0`, `radio_writes=0`, `executable=0` en los tres recibos.
- Análisis estático sobre `athbox` y los recibos de las Waves 150 y 153. Sin dispositivo y sin red.
- Este documento no contiene apellidos.

## 1. Stage 1968A — el hallazgo
- `CONFIRMED`: la función athstats (0x401890..0x402640, marco 0x2640) emite **dos** ioctls, y ambos usan el mismo comando **0x89f0**: en **0x40194c** y **0x402494**.
- `CONFIRMED`: hay **dos buffers de 0x1210 bytes** en la pila:
  - buffer 1: **sp+0x48 … sp+0x1258**;
  - buffer 2: **sp+0x1258 … sp+0x2468**.
- `CONFIRMED`: los literales de tamaño **0x1210** aparecen en **0x402474** y **0x402490**, uno por buffer.
- `CONFIRMED`: las dos etiquetas heredadas están en el buffer 1: `no_tx_buffer` en **0xb4** y `xmit_filtered` en **0xdc**.
- `CONFIRMED`: los seis `ast_*` están en el buffer 2, entre **0x148** y **0x224**.
- `REFUTED`: la hipótesis de un buffer único más grande. No hace falta: son dos respuestas de 4624 bytes cada una.
- `UNKNOWN`: a qué dispositivo o VAP apunta cada una de las dos llamadas, porque comparten número de comando.

## 2. Stage 1968A — quién llena 0xb4 y 0xdc
- `CONFIRMED`: el caso del ioctl en `umac.ko` (**0x5cdc8** en WA, **0x5ccb0** en XC) **no escribe** 0xb4 ni 0xdc. Solo parchea **0x110c**, **0x1110**, **0x1114** y copia el bloque.
- `INFERRED`: por tanto el caso es un **copiador y parcheador**, no el productor de esos dos bytes.
- `UNKNOWN`: la función que llena 0xb4 y 0xdc. Está fuera del camino del ioctl y no se localizó.

## 3. Stage 1969A — mapa pila → kernel
| Etiqueta | Buffer | Offset en el buffer | Confianza |
| :--- | ---: | ---: | :--- |
| `no_tx_buffer` | 1 | 0xb4 | `CONFIRMED` |
| `xmit_filtered` | 1 | 0xdc | `CONFIRMED` |
| `ast_tx_nobuf` | 2 | 0x148 | `CONFIRMED_OFFSET` |
| `ast_tx_xretries` | 2 | 0x168 | `CONFIRMED_OFFSET` |
| `ast_be_nobuf` | 2 | 0x210 | `CONFIRMED_OFFSET` |
| `ast_tx_buf_count` | 2 | 0x214 | `CONFIRMED_OFFSET` |
| `ast_tx_mgmt` | 2 | 0x220 | `CONFIRMED_OFFSET` |
| `ast_tx_packets` | 2 | 0x224 | `CONFIRMED_OFFSET` |

- `CONFIRMED`: las ocho filas caen dentro de alguno de los dos buffers; **cero** quedan fuera.
- `CONFIRMED`: el ioctl copia la estructura tal cual, así que el offset en el buffer es el offset en la estructura del kernel.
- `UNKNOWN`: el nombre de miembro de cada fila. El módulo no lo registra y no se inventó.

## 4. Consecuencia
- La lectura de 0xb4 y 0xdc como pérdidas de buffer sigue siendo correcta **en cuanto a offset**: son los bytes que el applet imprime.
- La diferencia entre la primera y la segunda respuesta explica por qué los seis contadores verdaderos parecían estar fuera de rango en la Wave 153.
- Un decodificador correcto debe pedir **dos** respuestas de 0x1210 y tratar cada una con su propia base.

## 5. Stage 1971A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos con `scope=project:futuramax`.
- `CONFIRMED`: la lectura de ida y vuelta devolvió los **3** con estado `candidate`.

## 6. Lo que no se prueba
- `UNKNOWN`: qué dispositivo o VAP selecciona cada llamada.
- `UNKNOWN`: quién llena 0xb4 y 0xdc antes de la copia.
- `UNKNOWN`: el nombre de miembro de las ocho filas.
- `UNKNOWN`: cualquier lectura en vivo.

## 7. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `1968A` | `tools/re/extract_stage1968a_athbox_0x2640_frame_multi_ioctl_map.py` y su recibo |
| `1969A` | `tools/re/reconcile_stage1969a_multi_ioctl_stack_to_kernel_struct_map.py` y su recibo |
| `1971A` | `tools/verify/record_stage1971a_memorymaster_ingest.py` y su recibo |
| `1972A` | `tests/test_stage1968a_to_1973a_suite.py` |
| `1973A` | `tools/verify/verify_stage1973a_wave155_opencode_gate.py` y la compuerta de la wave |
