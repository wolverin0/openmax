<!-- doc-head -->
# STAGE 2228A — Los 31 knobs de `.rodata` y el cuerpo real de `0x2138`

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los objetos ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2226A — el censo completo: 31 knobs, 21 sin documentar

El campo `+0x00` de cada registro es una relocación cuyo añadido es un desplazamiento dentro de `.rodata.str1.4`, así que el nombre se lee sin adivinar. Salen **31** registros por familia:

| Clasificación | WA | XC |
| :--- | ---: | ---: |
| Registros | **31** | **31** |
| Documentados en `ubntbox` | **10** | **10** |
| Sin documentar | **21** | **21** |

- `CONFIRMED`: hay **21** knobs de kernel que ningún binario de usuario de los ya censados nombra.
- `CONFIRMED`: los 10 documentados son los esperados; los otros 21 no aparecen en `ubntbox`.

### Los 21 sin documentar

`set_host_diag`, `set_diag`, `get_diag`, `get_host_diag`, `enable`, `timing`, `gqparam`, `sqparam`, `status`, `hsr_diag`, `get_reg`, `set_reg`, `ro`, `swr_limit`, `netconf`, `set_remote_host_diag`, `set_remote_target_diag`, `debug_block_sta`, `evm_meas_config`, `debug_tid`, `voip_bias`.

### Distribución por handler y tamaño

| Handler | Registros | | `.maxlen` | Registros |
| :--- | ---: | :--- | :--- | ---: |
| `0x2138` | **24** | | `0x4` | 8 |
| `0x45F0` | **7** | | `0x40` | 16 |
| | | | `0x800` | 7 |

- `CONFIRMED`: `.maxlen` y `.data` están perfectamente correlacionados: `0x4` con `0x9A4`, `0x40` con `0x9A8`, `0x800` con `0x1A4`.
- `CONFIRMED`: sólo hay **tres** clases de tamaño para 31 registros.
- `CONFIRMED`: el catálogo del proyecto tiene **481** nombres; el censo se reconcilió contra él.

## 2. Stage 2227A — corrección: `0x2138` sí llama

La wave 197 informó «cero llamadas» para `0x2138`. Era **una ventana demasiado estrecha**: el cuerpo real tiene **256** instrucciones y **5** llamadas por familia, 512 y 10 en total.

| Medición | WA | XC |
| :--- | ---: | ---: |
| Instrucciones hasta `jr ra` | **512** | **512** |
| Llamadas | **5** | **5** |

Llamadas resueltas por `.rel.text`:

```
ubnt_poll_host_set_diag, ubnt_poll_host_get_diag, printk,
ubnt_poll_host_set_host_diag, printk
```

- `REFUTED`: que `0x2138` no haga ninguna llamada. Hace cinco por familia, y entre ellas están los ayudantes de diagnóstico.
- `CONFIRMED`: el handler **sí delega**: elige entre `set_diag`, `get_diag` y `set_host_diag`.
- `CONFIRMED`: hay dos `printk`, que es lo que aparece cuando una comparación falla y se informa.
- `INFERRED`: la discriminación entre knobs es **por nombre**, y ahora está respaldada: hay ayudantes a los que llamar y `printk` para el caso desconocido. La wave 197 había descartado esa vía por la ausencia de llamadas, y esa ausencia era un artefacto de la ventana.

### Offsets accedidos a través de `a0`

- `CONFIRMED`: se leen o escriben `+0x00`, `+0x04` y `+0x9A8` (2472) desde el puntero de tabla.
- `CONFIRMED`: `+0x00` y `+0x04` son `procname` y `data`.
- `UNKNOWN`: qué representa `+0x9A8`, que cae muy lejos del registro de 44 bytes.

## 3. Qué cambia
- El censo de knobs pasa de 12 a **31**, con **21** nombres nuevos y completos.
- La conclusión de la wave 197 sobre `0x2138` queda **corregida**: sí llama, y la discriminación por nombre vuelve a ser la hipótesis respaldada.
- La regla de tres clases de `.maxlen` explica por qué el puntero de datos no bastaba: sólo hay tres.

## 4. Lo que queda abierto
- `UNKNOWN`: el significado de los 21 knobs nuevos, más allá del nombre.
- `UNKNOWN`: el destino de los dos `printk`.
- `UNKNOWN`: qué es `+0x9A8` en el acceso a la tabla.
- `UNKNOWN`: `vtable[456]`.

## 5. Stage 2229A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`, con los identificadores que devolvió la herramienta.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2226A` | `tools/re/extract_stage2226a_uph_all_31_rodata_ctl_table_knobs_re.py` y su recibo |
| `2227A` | `tools/re/reconcile_stage2227a_uph_0x2138_rel_text_and_pointer_arith_re.py` y su recibo |
| `2229A` | `tools/verify/record_stage2229a_memorymaster_ingest.py` y su recibo |
| `2230A` | `tests/test_stage2226a_to_2231a_suite.py` |
| `2231A` | `tools/verify/verify_stage2231a_wave198_opencode_gate.py` y su recibo |
