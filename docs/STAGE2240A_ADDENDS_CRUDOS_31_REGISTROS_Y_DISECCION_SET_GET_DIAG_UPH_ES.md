<!-- doc-head -->
# STAGE 2240A — Addends crudos de los 31 registros y disección de `set_diag` / `get_diag`

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los objetos ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2238A — el slot del handler es literal y compartido

Se volcaron las once palabras de cada registro con la relocación que cubre cada una.

| Medición | WA | XC |
| :--- | ---: | ---: |
| Registros | **31** | **31** |
| Palabras distintas en `+0x18` | **2** | **2** |
| Reparto | `0x2138` ×24, `0x45F0` ×7 | igual |

- `CONFIRMED`: **todos** los registros almacenan literalmente `0x00002138` o `0x000045F0` en `+0x18`.
- `REFUTED`: que cada registro guarde un desplazamiento propio a `.text`. Guardan la **misma** palabra.
- `CONFIRMED`: por tanto el slot del handler **no selecciona el knob**. La selección ocurre dentro del handler compartido.

### El mapa de funciones del tramo

| Símbolo | Dirección | Tamaño |
| :--- | :--- | ---: |
| `ubnt_poll_host_init_proc_sysctl` | `0x1D50` | 40 |
| `ubnt_poll_host_uninit_proc_sysctl` | `0x1D78` | 12 |
| `ubnt_poll_host_init_char_dev` | `0x1D84` | 76 |
| `ubnt_poll_host_uninit_char_dev` | `0x1DD0` | 12 |
| `ubnt_poll_host_radio_list_init` | `0x50D0` | 12 |
| **`ubnt_poll_host_radio_add`** | **`0x50DC`** | **1188** |

- `CONFIRMED`: `0x1D50` es `ubnt_poll_host_init_proc_sysctl`, no un envoltorio anónimo. Registra la tabla global.
- **`REFUTED`**: que `0x50DC` sea «el bloque de registro». Es **`ubnt_poll_host_radio_add`**, de 1188 bytes: la función que **agrega una radio** y que, dentro, clona y registra la tabla por radio.
- `CONFIRMED`: los tres ayudantes de diagnóstico viven fuera del tramo: `set_diag` en `0xA314`, `get_diag` en `0x7CC8`, `set_host_diag` en `0x7D28`.

## 2. Stage 2239A — los tres ayudantes, con nombre y llamadas

| Ayudante | Entrada | Tamaño | Llamadas |
| :--- | :--- | ---: | :--- |
| `ubnt_poll_host_set_diag` | `0xA314` | 144 | `ubnt_poll_host_ht_comm_tx`, `ubnt_poll_host_set_dfs_backoff` |
| `ubnt_poll_host_get_diag` | `0x7CC8` | 96 | `ubnt_poll_host_ht_comm_tx` |
| `ubnt_poll_host_set_host_diag` | `0x7D28` | 36 | **ninguna** |

- `CONFIRMED`: `set_diag` y `get_diag` comparten `ubnt_poll_host_ht_comm_tx`: ambos hablan por el canal de comunicación con el host.
- `CONFIRMED`: `set_diag` además ajusta el respaldo DFS.
- `CONFIRMED`: `set_host_diag` no llama a nada: es el más pequeño y el más directo.
- `INFERRED`: el despacho por nombre dentro de `0x2138` termina en estos tres cuerpos, y por eso hay dos `printk`: uno por nombre no reconocido.

### El tramo `0x45F0..0x50DC`

- `CONFIRMED`: el único símbolo con tamaño declarado en ese tramo es `ubnt_poll_host_radio_list_init` en `0x50D0`.
- `CONFIRMED`: `0x45F0` no tiene símbolo propio; es el cuerpo que sirve los siete knobs con `maxlen` `0x800`.
- `UNKNOWN`: el tamaño real de `0x45F0`, porque no hay símbolo que lo acote.

## 3. Qué cambia
- La hipótesis de «un offset distinto por registro» queda **descartada**: sólo hay dos palabras.
- `0x50DC` deja de ser un bloque anónimo y pasa a ser **`ubnt_poll_host_radio_add`**, con 1188 bytes.
- `0x1D50` pasa a ser `ubnt_poll_host_init_proc_sysctl`.
- Los tres ayudantes de diagnóstico quedan con dirección, tamaño y llamadas.

## 4. Lo que queda abierto
- `UNKNOWN`: el tamaño real de `0x45F0`.
- `UNKNOWN`: cómo compara `0x2138` el nombre, dado que el slot no lo distingue.
- `UNKNOWN`: el destino de los dos `printk`.
- `UNKNOWN`: `vtable[456]`.

## 5. Stage 2241A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`, con los identificadores que devolvió la herramienta.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2238A` | `tools/re/extract_stage2238a_uph_31_records_raw_addends_and_symtab_map_re.py` y su recibo |
| `2239A` | `tools/re/reconcile_stage2239a_uph_set_diag_get_diag_and_0x45f0_re.py` y su recibo |
| `2241A` | `tools/verify/record_stage2241a_memorymaster_ingest.py` y su recibo |
| `2242A` | `tests/test_stage2238a_to_2243a_suite.py` |
| `2243A` | `tools/verify/verify_stage2243a_wave200_opencode_gate.py` y su recibo |
