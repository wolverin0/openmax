<!-- doc-head -->
# STAGE 2210A — Handlers de `ctl_table` a 44 bytes y los dos registros sysctl

## 0. Frontera
- Cero SSH, cero escrituras a radio, cero ejecución: `ssh_connections=0`, `radio_writes=0`, `executable=0`.
- Todo se midió sobre los objetos ya extraídos en `artifacts/firmware_re_xc_ltu/`.
- Este documento no contiene apellidos.

## 1. Stage 2208A — el campo estaba en `+0x18`, no en `+0x14`

La wave 193 leyó cero en el `proc_handler` porque buscaba en `+0x14`. El mapa real, tomado de las relocaciones y no de una suposición, es:

| Desplazamiento | Campo | Evidencia |
| :--- | :--- | :--- |
| `+0x00` | `.procname` | relocación con añadido a una cadena de `.rodata.str1.4` |
| `+0x04` | `.data` | relocación |
| `+0x08` | `.maxlen` | valor literal |
| `+0x0C` | `.mode` | valor literal `0x1A4` |
| `+0x10` | `.child` | cero |
| `+0x14` | reservado | cero en todos |
| `+0x18` | **`.proc_handler`** | relocación a `.text` |
| `+0x1C`..`+0x28` | cola | cero |

- `CONFIRMED`: el paso entre registros es **`0x2C`** (44 bytes), medido como `0x17C - 0x150`.
- `CONFIRMED`: el `proc_handler` está en **`+0x18`** y su valor es un puntero a `.text`.
- `REFUTED`: que el campo estuviera en `+0x14`. Por eso la lectura anterior daba cero.
- `CONFIRMED`: sólo **dos** registros de esta tabla se resuelven por nombre de knob: `gpsreset` en `0x150` y `gps_info` en `0x17C`, iguales en WA y XC.

| Knob | Registro | `.maxlen` | `.mode` | `.proc_handler` |
| :--- | :--- | ---: | :--- | :--- |
| `gpsreset` | `0x150` | 4 | `0x1A4` | `0x1B00` |
| `gps_info` | `0x17C` | 256 | `0x1A4` | `0x1BFC` |

- `CONFIRMED`: son dos handlers **distintos**, no uno compartido.
- `UNKNOWN`: el nombre de cada handler. El más cercano hacia atrás es `ubnt_poll_host_set_tid5_rate_war`, pero su tamaño no cubre `0x1BFC`, así que es un **envolvente**, no el destino.
- `UNKNOWN`: dónde viven los otros diez knobs. En este bloque de `.data` no están.

## 2. Stage 2209A — dos registros y un directorio

| Símbolo | Sitio | Función envolvente |
| :--- | :--- | :--- |
| `register_sysctl_table` | `0x1D5C` | `0x1D50` |
| `register_sysctl_table` | `0x5400` | `0x50DC` |
| `proc_mkdir` | `0x5414` | `0x50DC` |

- `CONFIRMED`: el sitio de `0x1D5C` vive en una función de 12 bytes (`0x1D50`), es decir un envoltorio mínimo.
- `CONFIRMED`: los sitios de `0x5400` y `0x5414` comparten función (`0x50DC`), así que el registro de la tabla por radio y la creación del directorio ocurren en el mismo bloque.
- `UNKNOWN`: el argumento raíz de cada llamada. No se pudo plegar el par `lui`/`addiu` porque el valor llega en un registro copiado, no como constante inmediata.
- `UNKNOWN`: si la plantilla por radio se clona o se registra tal cual.

## 3. Qué cambia
- El `proc_handler` deja de ser «no medido»: está en `+0x18` y tiene valor.
- Los dos knobs medidos tienen handlers **distintos**.
- Los dos registros quedan atribuidos a funciones envolventes diferentes: uno mínimo y uno compartido con el directorio.

## 4. Lo que queda abierto
- `UNKNOWN`: los nombres de los handlers `0x1B00` y `0x1BFC`.
- `UNKNOWN`: la ubicación de los otros diez registros de knob.
- `UNKNOWN`: la raíz de cada `register_sysctl_table`.
- `UNKNOWN`: `vtable[456]`.

## 5. Stage 2211A — memoria durable
- `CONFIRMED`: se ingirieron **3** reclamos en `project:futuramax`, con los identificadores que devolvió la herramienta.

## 6. Artefactos
| Etapa | Artefacto |
| :--- | :--- |
| `2208A` | `tools/re/extract_stage2208a_uph_44byte_ctl_table_rel_data_handlers_re.py` y su recibo |
| `2209A` | `tools/re/reconcile_stage2209a_uph_0x1d5c_vs_0x5400_sysctl_init_re.py` y su recibo |
| `2211A` | `tools/verify/record_stage2211a_memorymaster_ingest.py` y su recibo |
| `2212A` | `tests/test_stage2208a_to_2213a_suite.py` |
| `2213A` | `tools/verify/verify_stage2213a_wave195_opencode_gate.py` y su recibo |
