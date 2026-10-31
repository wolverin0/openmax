<!-- doc-head -->
# STAGE 2432A — Auditoría de accesos directos al puntero del ioctl y mapa unificado de `radio+0xE4`

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Medido sobre `artifacts/firmware_re_xc_ltu/`. WA y XC coinciden en todo lo reportado.
- Este documento no contiene apellidos.

## 1. Stage 2430A — la contradicción resuelta: son dos disciplinas

### 1.1 El tamaño declarado en el comando

| Comando | Dirección | Tamaño | Número |
| :--- | ---: | ---: | ---: |
| `0x40905501` | 1 | **144** | 1 |
| `0xC0015502` | 3 | **1** | 2 |
| `0xC6945503` | 3 | **1684** | 3 |
| `0xC2145504` | 3 | **532** | 4 |
| `0xC2145505` | 3 | **532** | 5 |

### 1.2 Lo que cada manejador toca de verdad

| Manejador | Declarado | Span plano | Copias `__copy_user` |
| :--- | ---: | ---: | ---: |
| `get_info` | 144 | **144** | 0 |
| `get_stalist` | 1 | **1** | 2 |
| `get_stainfo` | 1684 | **0** | 2 |
| `get_sta_spec_data` | 532 | **0** | 2 |
| `set_sta_spec_data` | 532 | **0** | 2 |

- `CONFIRMED`: **`get_info` escribe exactamente 144 bytes** con almacenes planos, y su comando declara **144**. Coincidencia exacta.
- `CONFIRMED`: **`get_stalist` lee exactamente 1 byte** con una carga plana en el offset 0, y su comando declara **1**. Coincidencia exacta.
- `CONFIRMED`: los otros tres **no tocan el puntero en absoluto** de forma plana; sólo copian **6 bytes** con `__copy_user`.
- `CONFIRMED`: sus tamaños declarados —1684 y 532— **no corresponden a nada que el manejador toque**. La ventana declarada no se usa por esta vía.

### 1.3 La respuesta

- **`CONFIRMED`**: el módulo **sí desreferencia el puntero del ioctl directamente**, en `get_info` (144 bytes de escritura) y en `get_stalist` (1 byte de lectura), **sin** `copy_from_user` ni `copy_to_user`.
- En MIPS eso funciona mientras el proceso actual tenga mapeada la dirección en KUSEG; con un puntero inválido produce un *oops*, no un `EFAULT`.
- **`CONFIRMED`**: la razón de que `__copy_user` se use para **6 bytes** es que esos tres caminos se escribieron a prueba de fallo y los otros dos no. **No es una inconsistencia del análisis: es una inconsistencia del propio archivo.**
- **`REFUTED`**: la lectura de la wave 230 que trataba la contradicción como una incógnita sin resolver. Sí se resuelve: **conviven dos disciplinas**, y los tamaños declarados confirman cuál usa cada comando.
- **`UNKNOWN`**: por qué los comandos 3, 4 y 5 declaran 1684 y 532 bytes que nadie consume.

## 2. Stage 2431A — el mapa de `radio+0xE4`

Siete funciones reciben el mismo primer argumento: los cinco manejadores y los dos formateadores de registro.

| Función | Offsets distintos | Offsets |
| :--- | ---: | :--- |
| `get_info` | **68** | `0,12,16,20,24,25,26,28,32,268,276,280` y el bloque `4332..4494` |
| `get_stalist` | 2 | `12, 280` |
| `get_stainfo` | 3 | `12, 280, 4332` |
| `get_sta_spec_data` | 2 | `12, 280` |
| `set_sta_spec_data` | 2 | `12, 280` |
| `log_info` | 3 | `12, 25, 28` |
| `log_noack_info` | 4 | `12, 280, 4332, 4336` |

- `CONFIRMED`: **offset 12** (`+0x0C`) lo leen **las siete**. Es el único campo en el que coincide toda la familia.
- `CONFIRMED`: **offset 280** (`+0x118`) lo leen **seis de siete**; sólo `log_info` lo omite.
- `CONFIRMED`: **4332 y 4336** (`0x10EC` y `0x10F0`) los leen tres cada uno.
- `CONFIRMED`: esto **cierra el hallazgo de la wave 216**: allí el formateador elegía entre los punteros de `4332` y `4336` probando la bandera de `280` contra uno. Aquí se ve que el selector y sus **dos** destinos están en el mismo cuerpo de código.
- `CONFIRMED`: `get_info` es el único que lee el bloque ancho `4332..4494` (`0x10EC`..`0x118E`): es la **ficha de estación**, no la cabecera.
- **`UNKNOWN`**: el papel de `+0x0C`, que es el más compartido y por eso el más relevante.

## 3. Qué cambia
- La contradicción de la wave 230 deja de ser una incógnita: **hay dos disciplinas**, y el tamaño declarado dice cuál usa cada comando.
- El mapa de `radio+0xE4` deja de estar disperso: **`+0x0C` es común a las siete funciones**, y `+0x118` selecciona entre `+0x10EC` y `+0x10F0`.

## 4. Lo que queda abierto
- `UNKNOWN`: el papel de `+0x0C`.
- `UNKNOWN`: por qué los comandos 3, 4 y 5 declaran tamaños que nadie usa.
- `UNKNOWN`: el nombre del hueco `radio+0xE4`.
- `UNKNOWN`: `set_rate_override`, `vtable[456]` y el nombre del directorio de `/proc`.

## 5. Stage 2433A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax` y se añadieron las filas con **CRLF**.

## 6. Artefactos
`build_stage2430a_uph_ku_comm_plain_stores_vs_copy_user_kuseg_audit_re.py`, `build_stage2431a_uph_radio_0xe4_poll_dev_struct_unified_map_re.py`, `record_stage2433a_memorymaster_ingest.py`, `test_stage2430a_to_2435a_suite.py` y `verify_stage2435a_wave232_opencode_gate.py`, cada uno con su recibo.
